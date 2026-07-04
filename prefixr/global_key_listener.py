"""
global_key_listener.py
───────────────────────
OS-level keyboard observer.  Lets MainWindow react to a-z / Backspace / Enter
even while another application holds keyboard focus (e.g. the user Alt-Tabbed
into a game or a text field to actually type the word Prefixr found for them).

Design decisions
────────────────
• Built on pynput.keyboard.Listener, which installs a passive, non-blocking
  OS hook (Xlib on Linux, Quartz on macOS, WinAPI on Windows). "Passive" is
  the key property here: we only *observe* keystrokes, we never swallow or
  suppress them (Listener is constructed without suppress=True), so the
  application the user is actually typing into keeps receiving every key
  exactly as before. Prefixr never interferes with anything outside itself.
• Only three signals are exposed — letter_typed(str), backspace_pressed(),
  enter_pressed() — and every other key (arrows, modifiers, digits, symbols,
  function keys, Tab, Esc, …) is silently ignored at the source. This keeps
  the "only a-z, Backspace, Enter" contract in one place instead of scattered
  across callers.
• The listener runs on its own OS thread (managed internally by pynput). All
  three signals are emitted from that thread; Qt's signal/slot machinery
  automatically marshals the call onto the GUI thread for any slot connected
  with the default AutoConnection, so callers never need to worry about
  thread-safety themselves.
• start()/stop() are idempotent and cheap, so callers can freely start the
  listener only while it's actually useful (i.e. while a prefix is present)
  and stop it the instant the search field is cleared — no keystrokes are
  observed at all outside of that window.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Signal

try:
    from pynput import keyboard
except ImportError:  # pragma: no cover - environment without pynput installed
    keyboard = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class GlobalKeyListener(QObject):
    """
    Thin Qt wrapper around a background pynput keyboard hook.

    Signals
    ───────
    letter_typed(str)   — emitted with a single lowercase a-z character.
    backspace_pressed() — emitted when Backspace is pressed.
    enter_pressed()     — emitted when Enter/Return (main or numpad) is pressed.

    Every other key is ignored before any signal is emitted.
    """

    letter_typed: Signal = Signal(str)
    backspace_pressed: Signal = Signal()
    enter_pressed: Signal = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._listener: "keyboard.Listener | None" = None

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Install the OS hook if it isn't already running."""
        if keyboard is None:
            logger.warning("pynput is not installed; global key capture disabled")
            return
        if self._listener is not None:
            return  # already running

        self._listener = keyboard.Listener(on_press=self._on_press)
        # daemon=True (pynput's default) so the hook thread never blocks exit
        self._listener.start()

    def stop(self) -> None:
        """Remove the OS hook if it's running. Safe to call repeatedly."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    @property
    def is_active(self) -> bool:
        return self._listener is not None

    # ── Internal ──────────────────────────────────────────────────────────────

    def _on_press(self, key) -> None:
        """
        Runs on the pynput hook thread. Filters to exactly: a-z, Backspace,
        Enter. Everything else (arrows, Ctrl/Alt/Shift, digits, punctuation,
        function keys, Tab, Esc, media keys, …) is dropped here so no other
        part of the app ever sees a stray key.
        """
        try:
            if isinstance(key, keyboard.KeyCode) and key.char:
                ch = key.char
                if len(ch) == 1 and ch.isalpha() and ch.isascii():
                    self.letter_typed.emit(ch.lower())
                return

            if key == keyboard.Key.backspace:
                self.backspace_pressed.emit()
                return

            if key in (keyboard.Key.enter,):
                self.enter_pressed.emit()
                return
        except Exception:  # pragma: no cover - defensive; never crash the hook
            logger.exception("Error handling global key event")