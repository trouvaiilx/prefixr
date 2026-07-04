"""
main_window.py
──────────────
Top-level QMainWindow.  Wires SearchBar ↔ Dictionary ↔ ResultsView together
while keeping each module ignorant of the others (Mediator pattern).

Responsibilities
────────────────
• Build and lay out all child widgets.
• Connect signals to slots (textChanged → search, tab_pressed → toggle sort).
• Forward arrow-key / Enter events from SearchBar to ResultsView for keyboard
  navigation of results and used-word marking.
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

Background typing (out-of-focus word tracking)
────────────────────────────────────────────────
While a prefix is present, a GlobalKeyListener hook observes a-z / Backspace
/ Enter system-wide — including while the user has Alt-Tabbed into a
different application to actually type the word Prefixr found for them.

• Every observed letter is appended to ``self._typed_buffer`` and forwarded
  to ResultsView, which colors each result green/red per-character.
• Backspace pops the last buffered character (correcting a typo).
• Enter looks for a result that exactly equals prefix + buffer and, if
  found, marks it used — exactly as if the user had selected it by hand —
  then clears the buffer so the next word starts fresh.
• The hook is only *installed* while the search field is non-empty (no
  background listening happens at all otherwise), and its events are only
  *applied* while this window is not the active window — when the window
  is focused, normal typing already goes through SearchBar/keyPressEvent,
  so global events are ignored to avoid double-handling.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QSettings, Qt
from PySide6.QtWidgets import (
    QFileDialog,
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
from ..global_key_listener import GlobalKeyListener
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

        # Background-typing state (see module docstring)
        self._typed_buffer: str = ""
        self._global_listener = GlobalKeyListener(self)

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
        self._results_view = ResultsView(self._cfg)
        root.addWidget(self._results_view, stretch=1)

        # ── Status footer ─────────────────────────────────────────────────
        footer = QHBoxLayout()
        footer.setContentsMargins(2, 2, 2, 0)
        footer.setSpacing(8)

        self._lbl_matches = QLabel(self._matches_text(0, empty=True))
        self._lbl_matches.setObjectName("status_matches")
        footer.addWidget(self._lbl_matches)

        footer.addStretch()

        self._lbl_used = QLabel("")
        self._lbl_used.setObjectName("status_used")
        footer.addWidget(self._lbl_used)

        self._reset_btn = QPushButton("Reset")
        self._reset_btn.setObjectName("reset_button")
        self._reset_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._reset_btn.setFixedHeight(22)
        self._reset_btn.setVisible(False)
        footer.addWidget(self._reset_btn)

        count_text = (
            f"{self._dictionary.word_count:,} words"
            if self._dictionary.is_loaded
            else "no words loaded"
        )
        self._lbl_wordcount = QLabel(count_text)
        self._lbl_wordcount.setObjectName("status_wordcount")
        footer.addWidget(self._lbl_wordcount)

        root.addLayout(footer)

    # ── Signal wiring ─────────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._search_bar.textChanged.connect(self._on_text_changed)
        self._search_bar.tab_pressed.connect(self._toggle_sort)
        self._sort_btn.clicked.connect(self._toggle_sort)

        # Keyboard navigation of results
        self._search_bar.arrow_down_pressed.connect(self._results_view.move_highlight_down)
        self._search_bar.arrow_up_pressed.connect(self._results_view.move_highlight_up)
        self._search_bar.enter_pressed.connect(self._on_enter_pressed)

        # Word selection from results
        self._results_view.word_selected.connect(self._on_word_selected)

        # Reset used words
        self._reset_btn.clicked.connect(self._on_reset_used)

        # Background typing (out-of-focus word tracking)
        self._global_listener.letter_typed.connect(self._on_global_letter)
        self._global_listener.backspace_pressed.connect(self._on_global_backspace)
        self._global_listener.enter_pressed.connect(self._on_global_enter)

        # Wordlist switching
        self._search_bar.f1_pressed.connect(self._on_switch_wordlist)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_text_changed(self, text: str) -> None:
        """Called on every keystroke — must complete in < 16 ms for 60 fps."""
        prefix = text.strip()

        # Any change to the prefix invalidates whatever the user was
        # background-typing against the previous result set.
        self._typed_buffer = ""

        if not prefix:
            self._results_view.clear_display()
            self._lbl_matches.setText(self._matches_text(0, empty=True))
            # No prefix → no background keystroke detection at all.
            self._global_listener.stop()
            return

        matches = self._dictionary.prefix_search(
            prefix,
            self._sort_order,
            self._cfg.max_results,
        )
        self._results_view.display(matches, prefix)
        self._lbl_matches.setText(self._matches_text(len(matches), empty=False))

        # A prefix is present — start (or keep running) the background hook.
        self._global_listener.start()

    def _toggle_sort(self) -> None:
        """Flip between shortest-first and longest-first, then re-run search."""
        self._sort_order = self._sort_order.toggled()
        self._sort_btn.setText(self._sort_order.button_label())
        self._sort_btn.setToolTip(self._sort_order.tooltip())
        # Re-search with the same prefix under the new order
        self._on_text_changed(self._search_bar.text())
        # Ensure keyboard focus stays on the input field
        self._search_bar.setFocus(Qt.FocusReason.OtherFocusReason)

    def _on_enter_pressed(self) -> None:
        """Forward Enter to the results view if a highlight exists, then clear input."""
        if self._results_view.has_highlight:
            self._results_view.confirm_highlight()
        # Always clear the input field on Enter
        self._search_bar.clear()

    def _on_word_selected(self, word: str) -> None:
        """Mark the selected word as used and refresh the UI."""
        self._dictionary.mark_used(word)
        self._update_used_status()
        # Re-run the search to immediately hide the used word
        self._on_text_changed(self._search_bar.text())

    def _on_reset_used(self) -> None:
        """Clear all used words and refresh."""
        self._dictionary.reset_used()
        self._update_used_status()
        self._on_text_changed(self._search_bar.text())
        self._search_bar.setFocus(Qt.FocusReason.OtherFocusReason)

    # ── Background typing (out-of-focus word tracking) ──────────────────────────

    def _on_global_letter(self, ch: str) -> None:
        """
        A single a-z key was observed system-wide. Ignored while this window
        is focused (normal typing already handles that via SearchBar), and
        ignored if there's no prefix (shouldn't normally fire — the listener
        is stopped in that case — but this is a cheap, harmless guard).
        """
        if self.isActiveWindow() or not self._search_bar.text().strip():
            return
        self._typed_buffer += ch
        self._results_view.set_typed_overlay(self._typed_buffer)

    def _on_global_backspace(self) -> None:
        """Undo the last background-typed character, if any."""
        if self.isActiveWindow() or not self._search_bar.text().strip():
            return
        if self._typed_buffer:
            self._typed_buffer = self._typed_buffer[:-1]
            self._results_view.set_typed_overlay(self._typed_buffer)

    def _on_global_enter(self) -> None:
        """
        The user finished typing a word elsewhere and pressed Enter. If the
        prefix + background-typed buffer exactly matches one of the current
        results, mark that word as used — the same effect as selecting it
        by hand — then reset the buffer for the next word.
        """
        if self.isActiveWindow() or not self._search_bar.text().strip():
            return

        matched = self._results_view.matched_word()
        if matched is not None:
            self._dictionary.mark_used(matched)
            self._update_used_status()

        self._typed_buffer = ""
        # Re-run the search: refreshes the list (hiding the now-used word)
        # and resets the overlay via ResultsView.display().
        self._on_text_changed(self._search_bar.text())

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        """Tear down the background OS hook so no thread outlives the window."""
        self._global_listener.stop()
        super().closeEvent(event)

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

    def _update_used_status(self) -> None:
        """Update the used-word counter in the footer and toggle reset button."""
        used = self._dictionary.used_count
        if used > 0:
            self._lbl_used.setText(f"{used} used")
            self._reset_btn.setVisible(True)
        else:
            self._lbl_used.setText("")
            self._reset_btn.setVisible(False)

    def _on_switch_wordlist(self) -> None:
        """
        Open a file picker so the user can load a different word list.
        Temporarily drops the always-on-top flag so the OS file dialog
        isn't hidden behind the window.
        """
        # Let the file dialog appear above us
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.show()  # re-apply flags

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a word list",
            "",
            "Text files (*.txt);;All files (*)",
        )

        # Restore always-on-top
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.show()

        if not path:
            self._search_bar.setFocus(Qt.FocusReason.OtherFocusReason)
            return

        self._dictionary.reload(Path(path))
        QSettings().setValue("wordlist_path", path)

        # Refresh all UI state
        self._error_banner.setVisible(not self._dictionary.is_loaded)
        count_text = (
            f"{self._dictionary.word_count:,} words"
            if self._dictionary.is_loaded
            else "no words loaded"
        )
        self._lbl_wordcount.setText(count_text)
        self._update_used_status()
        self._search_bar.clear()
        self._results_view.clear_display()
        self._lbl_matches.setText(self._matches_text(0, empty=True))
        self._search_bar.setFocus(Qt.FocusReason.OtherFocusReason)
