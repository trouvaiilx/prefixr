"""
search_bar.py
─────────────
The single text-input widget the user types into.

Design decisions
────────────────
• Tab is intercepted and re-emitted as a custom signal so MainWindow can
  wire it to the sort-toggle without SearchBar needing to know what toggling
  means (low coupling).
• Escape clears the field rather than dismissing the window, keeping the
  user in a continuous lookup flow.
• focusOutEvent schedules a delayed self-refocus via QTimer so the caret
  returns automatically whenever the window becomes active again.  The delay
  (cfg.focus_recovery_delay_ms) lets OS-level dialogs (e.g., Open File)
  complete their own focus handshake before we compete.
• WA_InputMethodEnabled is set explicitly so Input Method Editors (CJK, etc.)
  remain functional if the word list is extended in future.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QLineEdit

from ..config import Config


class SearchBar(QLineEdit):
    """
    Always-focused single-line input.

    Signals
    ───────
    tab_pressed        — emitted when Tab is pressed; consumed so focus never leaves.
    arrow_up_pressed   — emitted when ↑ is pressed (for result highlight navigation).
    arrow_down_pressed — emitted when ↓ is pressed (for result highlight navigation).
    enter_pressed      — emitted when Enter/Return is pressed.
    """

    tab_pressed: Signal = Signal()
    arrow_up_pressed: Signal = Signal()
    arrow_down_pressed: Signal = Signal()
    enter_pressed: Signal = Signal()

    def __init__(self, cfg: Config, parent=None) -> None:
        super().__init__(parent)
        self._cfg = cfg

        self.setObjectName("search_input")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setClearButtonEnabled(False)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)

        # Pre-allocate the recovery timer (avoids repeated construction)
        self._recovery_timer = QTimer(self)
        self._recovery_timer.setSingleShot(True)
        self._recovery_timer.setInterval(cfg.focus_recovery_delay_ms)
        self._recovery_timer.timeout.connect(self._try_refocus)

    # ── Event overrides ───────────────────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()

        if key == Qt.Key.Key_Tab:
            self.tab_pressed.emit()
            event.accept()
            return

        if key == Qt.Key.Key_Escape:
            if self.text():
                self.clear()
            event.accept()
            return

        if key == Qt.Key.Key_Up:
            self.arrow_up_pressed.emit()
            event.accept()
            return

        if key == Qt.Key.Key_Down:
            self.arrow_down_pressed.emit()
            event.accept()
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.enter_pressed.emit()
            event.accept()
            return

        super().keyPressEvent(event)

    def focusOutEvent(self, event) -> None:
        """
        When focus leaves the search bar, schedule a recovery attempt.
        We do not refocus immediately here because the OS may be in the
        middle of routing focus to a legitimate target (e.g., an alert).
        """
        super().focusOutEvent(event)
        self._recovery_timer.start()

    # ── Focus recovery ────────────────────────────────────────────────────────

    def _try_refocus(self) -> None:
        """
        Reclaim focus only if our parent window is still the active window
        and no other widget has legitimately taken focus.
        """
        window = self.window()
        if window and window.isActiveWindow() and not self.hasFocus():
            self.setFocus(Qt.FocusReason.OtherFocusReason)
