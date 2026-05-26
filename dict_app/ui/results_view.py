"""
results_view.py
───────────────
Display-only list of matched words.

Performance notes
─────────────────
• setUpdatesEnabled(False/True) brackets every bulk refresh, preventing
  per-item repaints and reducing GPU draw calls to a single composite flush.
• FocusPolicy.NoFocus ensures Tab/keyboard events are never stolen from
  SearchBar even if the user accidentally clicks a result row.
• SelectionMode.NoSelection removes the blue highlight bar so the list reads
  as pure text rather than an interactive chooser.
• ScrollPerPixel gives smooth inertial scrolling on trackpads / hi-DPI.

Extension points
────────────────
• To add inline definitions: store a dict[str, str] reference here and
  override the item creation to append a QLabel sub-row or use a delegate.
• To highlight the matched prefix: use a QStyledItemDelegate with
  QTextDocument to render rich text per item.
• To add keyboard navigation (↑ ↓ Enter to copy): override keyPressEvent
  and emit a word_selected signal upward.
"""

from __future__ import annotations

from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QListWidget,
    QListWidgetItem,
)


class ResultsView(QListWidget):
    """
    Render-only list of matched words.
    Refreshed on every keystroke; optimised to minimise repaint cost.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("results_list")

        # Never steal keyboard focus from the search bar
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # No row selection — this is a passive visual reference
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        # Cosmetic
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSpacing(0)
        self.setUniformItemSizes(True)   # faster layout for uniform-height items

    # ── Public API ────────────────────────────────────────────────────────────

    def display(self, words: Sequence[str]) -> None:
        """
        Replace the current list contents with *words*.

        Batches all item additions inside a setUpdatesEnabled(False) guard
        so the widget repaints exactly once after the full list is built.
        """
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            for word in words:
                item = QListWidgetItem(word)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                self.addItem(item)
        finally:
            self.setUpdatesEnabled(True)

    def clear_display(self) -> None:
        """Remove all items (alias for readability at call sites)."""
        self.clear()
