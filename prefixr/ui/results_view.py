"""
results_view.py
───────────────
Display list of matched words with keyboard-driven highlight navigation,
prefix highlighting, and a "background typing" overlay.

Performance notes
─────────────────
• setUpdatesEnabled(False/True) brackets every bulk refresh, preventing
  per-item repaints and reducing GPU draw calls to a single composite flush.
• FocusPolicy.NoFocus ensures Tab/keyboard events are never stolen from
  SearchBar even if the user accidentally clicks a result row.
• ScrollPerPixel gives smooth inertial scrolling on trackpads / hi-DPI.
• Re-coloring the overlay (set_typed_overlay) only rewrites each row's rich
  text — it never touches the underlying item/word list — so it stays cheap
  even while the user is typing quickly in another application.

Keyboard navigation
───────────────────
Arrow Up/Down (forwarded from SearchBar) move a visual highlight through the
results.  Enter on a highlighted row emits ``word_selected(str)`` so the
main window can mark the word as used and clear the input.

Prefix highlighting & background typing overlay
─────────────────────────────────────────────────
Every row renders its word as rich text with three possible colorings,
applied left to right:

1. The typed *prefix* — always shown in the accent color, regardless of
   focus, so the user can see at a glance which part of every match they've
   already typed.
2. The *typed overlay* — extra characters captured by the global key
   listener while the app is out of focus (see MainWindow / GlobalKeyListener).
   Each such character is colored green if it matches the word at that
   position, or red if it doesn't. This lets the user glance at the always-
   on-top window while typing a word into another application and instantly
   see which candidate(s) they're still on track for.
3. Anything left over renders in the normal result color.

MainWindow owns *when* the overlay updates (only while the window is not
the active window, and only while a prefix is present); ResultsView just
renders whatever prefix/overlay it's given.
"""

from __future__ import annotations

import html as html_lib
from typing import Sequence

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QListWidget,
    QListWidgetItem,
)

from ..config import Config

# ── Highlight colors (kept in sync with the dark palette in styles.py) ────────
_COLOR_PREFIX    = "#4f7ef8"  # accent blue  — matches selection/accent color
_COLOR_CORRECT   = "#4ade80"  # green        — correct background-typed letter
_COLOR_INCORRECT = "#ff6b6b"  # red          — incorrect background-typed letter
_COLOR_NORMAL    = "#c8c8e0"  # default result text color

_ROW_PADDING_V = 5   # px — top and bottom padding for each row

_ROW_STYLE_NORMAL = """
    QLabel {
        background-color: transparent;
        border-left: 2px solid transparent;
        padding: 5px 16px 5px 14px;
    }
"""

_ROW_STYLE_SELECTED = """
    QLabel {
        background-color: #1e2a4a;
        border-left: 2px solid #4f7ef8;
        padding: 5px 16px 5px 14px;
    }
"""


class ResultsView(QListWidget):
    """
    List of matched words with an optional keyboard highlight, prefix
    highlighting, and a background-typing correctness overlay.

    Signals
    ───────
    word_selected(str) — emitted when Enter is pressed on a highlighted word.
    """

    word_selected: Signal = Signal(str)

    def __init__(self, cfg: Config, parent=None) -> None:
        super().__init__(parent)

        # Build a QFont from Config so sizeHint() works immediately on
        # labels that haven't entered the widget tree yet.
        self._row_font = QFont()
        self._row_font.setFamilies(
            [f.strip().strip("'") for f in cfg.font_family.split(",")]
        )
        self._row_font.setPixelSize(cfg.font_size_results)

        # Pre-compute a fixed row height so we never depend on stylesheet
        # resolution timing — font metrics + vertical padding.
        fm = QFontMetrics(self._row_font)
        self._row_height = fm.height() + _ROW_PADDING_V * 2

        self.setObjectName("results_list")

        # Never steal keyboard focus from the search bar
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Single-selection to display the keyboard highlight row
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Cosmetic
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSpacing(0)
        self.setUniformItemSizes(True)   # faster layout for uniform-height items

        # Track highlight index (-1 = nothing highlighted)
        self._highlight_index: int = -1

        # Current data backing the rendered rows
        self._words: list[str] = []
        self._prefix: str = ""
        self._typed: str = ""  # background-typed overlay, beyond the prefix

        # Row 1:1 with self._words; kept for cheap overlay-only repaints
        self._labels: list[QLabel] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def display(self, words: Sequence[str], prefix: str = "") -> None:
        """
        Replace the current list contents with *words*, highlighting *prefix*
        in every row. Resets the keyboard highlight and the background-typing
        overlay — a fresh search invalidates any in-progress overlay.
        """
        self._words = list(words)
        self._prefix = prefix.strip().lower()
        self._typed = ""

        self.setUpdatesEnabled(False)
        try:
            self.clear()
            self._labels = []
            for word in self._words:
                item = QListWidgetItem()
                # Prevent mouse clicks from selecting items
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

                label = QLabel(self._row_html(word))
                label.setTextFormat(Qt.TextFormat.RichText)
                label.setFont(self._row_font)
                label.setStyleSheet(_ROW_STYLE_NORMAL)

                self.addItem(item)
                item.setSizeHint(QSize(0, self._row_height))
                self.setItemWidget(item, label)
                self._labels.append(label)
        finally:
            self.setUpdatesEnabled(True)

        # Reset highlight — new results start with no selection
        self._highlight_index = -1
        self.clearSelection()
        self.setCurrentItem(None)

    def clear_display(self) -> None:
        """Remove all items and reset all state (alias for readability)."""
        self.clear()
        self._highlight_index = -1
        self._words = []
        self._prefix = ""
        self._typed = ""
        self._labels = []

    def set_typed_overlay(self, typed: str) -> None:
        """
        Update the background-typing overlay (characters typed beyond the
        prefix while the app is out of focus) and re-color every row in
        place, without rebuilding the item list.
        """
        self._typed = typed.lower()
        for word, label in zip(self._words, self._labels):
            label.setText(self._row_html(word))

    def matched_word(self) -> str | None:
        """
        Return the word among the current results whose text exactly equals
        prefix + typed-overlay (case-insensitive), or None if there is no
        such exact match yet. Used by MainWindow when Enter is pressed while
        the app is out of focus, to decide which word to mark as used.
        """
        if not self._prefix:
            return None
        target = self._prefix + self._typed
        for word in self._words:
            if word.lower() == target:
                return word
        return None

    @property
    def typed_overlay(self) -> str:
        return self._typed

    # ── Keyboard highlight navigation ─────────────────────────────────────────

    def move_highlight_down(self) -> None:
        """Move the highlight one row down, wrapping at the bottom."""
        count = self.count()
        if count == 0:
            return
        self._highlight_index = (self._highlight_index + 1) % count
        self._apply_highlight()

    def move_highlight_up(self) -> None:
        """Move the highlight one row up, wrapping at the top."""
        count = self.count()
        if count == 0:
            return
        if self._highlight_index <= 0:
            # Wrap to the bottom, or enter from -1
            self._highlight_index = count - 1
        else:
            self._highlight_index -= 1
        self._apply_highlight()

    def confirm_highlight(self) -> None:
        """
        If a word is currently highlighted, emit ``word_selected`` with its
        text.  Does nothing if no highlight is active.
        """
        if self._highlight_index < 0 or self._highlight_index >= len(self._words):
            return
        self.word_selected.emit(self._words[self._highlight_index])

    @property
    def has_highlight(self) -> bool:
        """True if a row is currently highlighted."""
        return 0 <= self._highlight_index < self.count()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _apply_highlight(self) -> None:
        """Visually select the row at ``_highlight_index`` and scroll to it."""
        item = self.item(self._highlight_index)
        if item is None:
            return

        # Reset every row's style to normal, then style just the current one.
        for label in self._labels:
            label.setStyleSheet(_ROW_STYLE_NORMAL)

        # Temporarily make the item selectable so we can highlight it
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable)
        self.setCurrentItem(item)
        self.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)

        label = self.itemWidget(item)
        if isinstance(label, QLabel):
            label.setStyleSheet(_ROW_STYLE_SELECTED)

    def _row_html(self, word: str) -> str:
        """
        Build the rich-text markup for one row: prefix in accent color,
        background-typed overlay in green/red per-character, remainder in
        the normal result color.
        """
        prefix_len = len(self._prefix)
        typed_len = len(self._typed)

        parts: list[str] = []
        for i, ch in enumerate(word):
            esc = html_lib.escape(ch)
            if i < prefix_len:
                parts.append(f'<span style="color:{_COLOR_PREFIX};font-weight:600;">{esc}</span>')
            elif i < prefix_len + typed_len:
                typed_ch = self._typed[i - prefix_len]
                color = _COLOR_CORRECT if typed_ch == ch.lower() else _COLOR_INCORRECT
                parts.append(f'<span style="color:{color};font-weight:600;">{esc}</span>')
            else:
                parts.append(f'<span style="color:{_COLOR_NORMAL};">{esc}</span>')

        return "".join(parts)