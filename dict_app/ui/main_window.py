"""
main_window.py
──────────────
Top-level QMainWindow.  Wires SearchBar ↔ Dictionary ↔ ResultsView together
while keeping each module ignorant of the others (Mediator pattern).

Responsibilities
────────────────
• Build and lay out all child widgets.
• Connect signals to slots (textChanged → search, tab_pressed → toggle sort).
• Enforce focus ownership: search bar always holds the keyboard caret when
  the application window is active.
• Display match count and vocabulary size in the status footer.
• Show a prominent warning banner if words.txt could not be loaded.

Focus management strategy
─────────────────────────
Three complementary mechanisms ensure uninterrupted typing flow:

1. SearchBar.focusOutEvent() → schedules a delayed self-refocus via QTimer.
   Handles the common case where another widget briefly claims focus.

2. MainWindow.changeEvent(ActivationChange) → refocuses the bar whenever
   the OS brings our window to the foreground (Alt-Tab, taskbar click, etc.).

3. MainWindow.showEvent() → ensures the bar is focused on first display,
   overriding any default focus the OS might assign to another widget.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..config import Config
from ..dictionary import Dictionary, SortOrder
from .results_view import ResultsView
from .search_bar import SearchBar
from .styles import SEARCH_PLACEHOLDER, build_stylesheet


class MainWindow(QMainWindow):
    """
    Application shell.  Owns no domain logic — delegates all searching to
    Dictionary and all rendering to ResultsView.
    """

    def __init__(self, dictionary: Dictionary, cfg: Config) -> None:
        super().__init__()
        self._dictionary = dictionary
        self._cfg = cfg
        self._sort_order: SortOrder = SortOrder.SHORTEST_FIRST

        self._setup_window()
        self._build_ui()
        self._connect_signals()
        self.setStyleSheet(build_stylesheet(cfg))

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup_window(self) -> None:
        self.setWindowTitle(self._cfg.window_title)
        self.resize(self._cfg.window_width, self._cfg.window_height)
        self.setMinimumSize(self._cfg.window_min_width, self._cfg.window_min_height)
        # Always float above every other application window
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        # Remove the default menu bar chrome
        self.menuBar().setVisible(False)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 10)
        root.setSpacing(10)

        # ── Top row: search field + sort toggle ───────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self._search_bar = SearchBar(self._cfg)
        self._search_bar.setPlaceholderText(SEARCH_PLACEHOLDER)
        top_row.addWidget(self._search_bar, stretch=1)

        self._sort_btn = QPushButton(self._sort_order.button_label())
        self._sort_btn.setObjectName("sort_button")
        self._sort_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._sort_btn.setToolTip(self._sort_order.tooltip())
        self._sort_btn.setFixedHeight(44)
        self._sort_btn.setMinimumWidth(70)
        top_row.addWidget(self._sort_btn)

        root.addLayout(top_row)

        # ── Error banner (hidden by default) ──────────────────────────────
        self._error_banner = QLabel(
            "⚠  words.txt not found — place it next to main.pyw and restart."
        )
        self._error_banner.setObjectName("error_banner")
        self._error_banner.setWordWrap(True)
        self._error_banner.setVisible(not self._dictionary.is_loaded)
        root.addWidget(self._error_banner)

        # ── Thin separator ────────────────────────────────────────────────
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        root.addWidget(sep)

        # ── Results list ──────────────────────────────────────────────────
        self._results_view = ResultsView()
        root.addWidget(self._results_view, stretch=1)

        # ── Status footer ─────────────────────────────────────────────────
        footer = QHBoxLayout()
        footer.setContentsMargins(2, 2, 2, 0)
        footer.setSpacing(8)

        self._lbl_matches = QLabel(self._matches_text(0, empty=True))
        self._lbl_matches.setObjectName("status_matches")
        footer.addWidget(self._lbl_matches)

        footer.addStretch()

        count_text = (
            f"{self._dictionary.word_count:,} words"
            if self._dictionary.is_loaded
            else "no words loaded"
        )
        lbl_count = QLabel(count_text)
        lbl_count.setObjectName("status_wordcount")
        footer.addWidget(lbl_count)

        root.addLayout(footer)

    # ── Signal wiring ─────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._search_bar.textChanged.connect(self._on_text_changed)
        self._search_bar.tab_pressed.connect(self._toggle_sort)
        self._sort_btn.clicked.connect(self._toggle_sort)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_text_changed(self, text: str) -> None:
        """Called on every keystroke — must complete in < 16 ms for 60 fps."""
        prefix = text.strip()

        if not prefix:
            self._results_view.clear_display()
            self._lbl_matches.setText(self._matches_text(0, empty=True))
            return

        matches = self._dictionary.prefix_search(
            prefix,
            self._sort_order,
            self._cfg.max_results,
        )
        self._results_view.display(matches)
        self._lbl_matches.setText(self._matches_text(len(matches), empty=False))

    def _toggle_sort(self) -> None:
        """Flip between shortest-first and longest-first, then re-run search."""
        self._sort_order = self._sort_order.toggled()
        self._sort_btn.setText(self._sort_order.button_label())
        self._sort_btn.setToolTip(self._sort_order.tooltip())
        # Re-search with the same prefix under the new order
        self._on_text_changed(self._search_bar.text())
        # Ensure keyboard focus stays on the input field
        self._search_bar.setFocus(Qt.FocusReason.OtherFocusReason)

    # ── Focus management ──────────────────────────────────────────────────────

    def showEvent(self, event) -> None:
        """Give the search bar the initial keyboard focus on first paint."""
        super().showEvent(event)
        self._search_bar.setFocus(Qt.FocusReason.OtherFocusReason)

    def changeEvent(self, event: QEvent) -> None:
        """
        Whenever the OS activates our window (Alt-Tab, taskbar click, etc.),
        immediately return focus to the search bar so typing can resume
        without the user needing to click the field.
        """
        if (
            event.type() is QEvent.Type.ActivationChange
            and self.isActiveWindow()
        ):
            self._search_bar.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        super().changeEvent(event)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _matches_text(self, count: int, *, empty: bool) -> str:
        if empty:
            return "Start typing to search"
        if count == 0:
            return "No matches"
        if count >= self._cfg.max_results:
            return f"Top {count} shown"
        return f"{count} match{'es' if count != 1 else ''}"
