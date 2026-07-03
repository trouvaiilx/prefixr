"""
results_view.py
───────────────
Display list of matched words with keyboard-driven highlight navigation.

Performance notes
─────────────────
• setUpdatesEnabled(False/True) brackets every bulk refresh, preventing
  per-item repaints and reducing GPU draw calls to a single composite flush.
• FocusPolicy.NoFocus ensures Tab/keyboard events are never stolen from
  SearchBar even if the user accidentally clicks a result row.
• ScrollPerPixel gives smooth inertial scrolling on trackpads / hi-DPI.

Keyboard navigation
───────────────────
Arrow Up/Down (forwarded from SearchBar) move a visual highlight through the
results.  Enter on a highlighted row emits ``word_selected(str)`` so the
main window can mark the word as used and clear the input.
"""

from __future__ import annotations

from typing import Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListWidget,
    QListWidgetItem,
)


class ResultsView(QListWidget):
    """
    List of matched words with an optional keyboard highlight.
    Refreshed on every keystroke; optimised to minimise repaint cost.

    Signals
    ───────
    word_selected(str) — emitted when Enter is pressed on a highlighted word.
    """

    word_selected: Signal = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
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

    # ── Public API ────────────────────────────────────────────────────────────

    def display(self, words: Sequence[str]) -> None:
        """
        Replace the current list contents with *words*.

        Batches all item additions inside a setUpdatesEnabled(False) guard
        so the widget repaints exactly once after the full list is built.
        Resets the keyboard highlight.
        """
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            for word in words:
                item = QListWidgetItem(word)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                # Prevent mouse clicks from selecting items
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.addItem(item)
        finally:
            self.setUpdatesEnabled(True)

        # Reset highlight — new results start with no selection
        self._highlight_index = -1
        self.clearSelection()
        self.setCurrentItem(None)

    def clear_display(self) -> None:
        """Remove all items and reset highlight (alias for readability)."""
        self.clear()
        self._highlight_index = -1

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
        if self._highlight_index < 0 or self._highlight_index >= self.count():
            return
        item = self.item(self._highlight_index)
        if item is not None:
            self.word_selected.emit(item.text())

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
        # Temporarily make the item selectable so we can highlight it
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable)
        self.setCurrentItem(item)
        self.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)
