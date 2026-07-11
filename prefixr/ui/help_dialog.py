"""
help_dialog.py
──────────────
A small tabbed "?" help window: About / How to Use / Shortcuts / Background
Typing, each on its own tab so the information never feels cluttered.

Design decisions
────────────────
• QTabWidget keeps each topic isolated — the user only sees one panel of
  text at a time instead of one long scrolling wall.
• Every panel is a plain QLabel with rich text + word wrap inside a
  QScrollArea, so the dialog stays usable even at the app's minimum size
  or with a larger system font.
• The dialog is modal (exec()) and NoFocus on all its internal widgets
  isn't needed since it doesn't compete with SearchBar — MainWindow simply
  restores focus to the search bar after it closes.
• Styling reuses the same dark, blue-tinted palette as the rest of the
  app (see styles.py) so it never looks like a bolted-on system dialog.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..config import Config
from .styles import build_stylesheet

_ABOUT_HTML = """
<h2 style="margin-bottom:4px;">Prefixr</h2>
<p style="color:#8888aa;">A minimalist, ultra-fast desktop prefix-search tool.</p>
<p>
Prefixr keeps a word list in memory and instantly shows every word that
starts with whatever you type — no Enter required, no lag, even across
hundreds of thousands of words.
</p>
<p>
It's built to float above every other window, so you can look up a word
here while writing anywhere else — a crossword, a game, a document — without
ever switching focus away from what you're typing into.
</p>
<p style="color:#666688;">Built with Python + PySide6.</p>
"""

_USAGE_HTML = """
<h3 style="margin-bottom:4px;">How to use</h3>
<p>
1. Just start typing. Every keystroke narrows the result list to words
   that begin with what you've typed so far — <b>Backspace</b> widens it
   again.
</p>
<p>
2. Use <b>&uarr;</b> / <b>&darr;</b> to move a highlight through the
   results, then <b>Enter</b> to confirm the highlighted word and mark it
   used (it's hidden from future searches until you reset).
</p>
<p>
3. Click the sort button (or press <b>Tab</b>) to cycle how results are
   ordered: shortest first &rarr; random &rarr; longest first. Click the
   padlock next to it to lock the current order so Tab and the button stop
   changing it.
</p>
<p>
4. Press <b>F1</b> to load a different word list at any time — your choice
   is remembered the next time you open Prefixr.
</p>
<p>
5. Prefixr always stays on top and the search field re-claims keyboard
   focus automatically, so you can Alt-Tab away and back without ever
   clicking back into it.
</p>
"""

_SHORTCUTS_HTML = """
<h3 style="margin-bottom:4px;">Keyboard shortcuts</h3>
<table cellspacing="6" style="color:#d0d0e8;">
<tr><td style="color:#4f7ef8;font-weight:600;">Any letter</td><td>Instant prefix search</td></tr>
<tr><td style="color:#4f7ef8;font-weight:600;">Backspace</td><td>Narrow / widen search</td></tr>
<tr><td style="color:#4f7ef8;font-weight:600;">Tab</td><td>Cycle sort order (shortest &rarr; random &rarr; longest), unless locked</td></tr>
<tr><td style="color:#4f7ef8;font-weight:600;">Escape</td><td>Clear the search field</td></tr>
<tr><td style="color:#4f7ef8;font-weight:600;">&uarr; / &darr;</td><td>Move the keyboard highlight through results</td></tr>
<tr><td style="color:#4f7ef8;font-weight:600;">Enter</td><td>Confirm the highlighted result / mark it used</td></tr>
<tr><td style="color:#4f7ef8;font-weight:600;">F1</td><td>Open file picker to switch word list</td></tr>
</table>
<p style="color:#666688;margin-top:10px;">
The sort-order lock (padlock button) and the "?" help button are mouse-only
— they don't have dedicated key shortcuts.
</p>
"""

_BACKGROUND_HTML = """
<h3 style="margin-bottom:4px;">Background typing</h3>
<p>
Prefixr always stays on top, so a common flow is: type a prefix here, then
Alt-Tab into whatever you're actually writing in — a game, a document, a
terminal — and type the full word there. Prefixr keeps watching:
</p>
<p>
&bull; Every letter you type, in any app, is compared against each visible
result at the matching position: <span style="color:#4ade80;">green</span>
if it's correct, <span style="color:#ff6b6b;">red</span> if it isn't.
</p>
<p>
&bull; <b>Backspace</b> undoes the last letter, so a typo doesn't throw off
the highlighting.
</p>
<p>
&bull; The moment you press <b>Enter</b>, if what you've typed exactly
matches one of the visible results, that word is marked used automatically
— exactly as if you'd selected it by hand here.
</p>
<p style="color:#666688;">
This only activates while the search field has a prefix in it, and it never
blocks or consumes a keystroke — the app you're typing into always receives
every key normally.
</p>
"""


def _make_panel(html: str) -> QScrollArea:
    """Wrap a rich-text QLabel in a scroll area so long content never
    forces the dialog itself to grow past a reasonable size."""
    label = QLabel(html)
    label.setObjectName("help_panel_label")
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    label.setContentsMargins(4, 4, 4, 4)

    container = QWidget()
    container.setObjectName("help_panel")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.addWidget(label)
    layout.addStretch()

    scroll = QScrollArea()
    scroll.setObjectName("help_scroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setWidget(container)
    return scroll


class HelpDialog(QDialog):
    """
    Modal '?' help window with one tab per topic:
    About · How to Use · Shortcuts · Background Typing.
    """

    def __init__(self, cfg: Config, parent=None) -> None:
        super().__init__(parent)
        self._cfg = cfg

        self.setObjectName("help_dialog")
        self.setWindowTitle("Prefixr — Help")
        self.setModal(True)
        self.resize(380, 420)
        self.setMinimumSize(320, 320)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        tabs = QTabWidget()
        tabs.setObjectName("help_tabs")
        tabs.addTab(_make_panel(_ABOUT_HTML), "About")
        tabs.addTab(_make_panel(_USAGE_HTML), "How to Use")
        tabs.addTab(_make_panel(_SHORTCUTS_HTML), "Shortcuts")
        tabs.addTab(_make_panel(_BACKGROUND_HTML), "Background Typing")
        root.addWidget(tabs)

        # Top-level windows (dialogs included) don't reliably inherit a
        # parent's style sheet, so apply it directly here too.
        self.setStyleSheet(build_stylesheet(cfg))