"""
main.pyw
────────
Application entry point.  Named .pyw so Windows suppresses the console window.
On Linux/macOS the .pyw extension is treated identically to .py.

Start-up sequence
─────────────────
1. Create QApplication and opt into crisp high-DPI rendering.
2. Construct Dictionary — loads and normalises words.txt into RAM once.
3. Build MainWindow, which wires all child widgets together.
4. Enter the Qt event loop.

The Dictionary is constructed before any window is shown, so the user sees
the UI only after the word list is fully ready.  For a 466k-word file this
takes roughly 100-300 ms on typical hardware — imperceptible in practice.
If startup latency ever becomes a concern, load asynchronously in a QThread
and show a brief spinner in MainWindow while waiting.
"""

import sys
import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from dict_app.config import Config
from dict_app.dictionary import Dictionary
from dict_app.ui.main_window import MainWindow


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s  %(name)s  %(message)s",
    )


def main() -> None:
    _configure_logging()

    # ── High-DPI: let Qt scale fractional factors without rounding ────────
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Dictionary")
    app.setOrganizationName("dict_app")
    # "Fusion" renders consistently across platforms and supports full
    # stylesheet customisation without OS theme interference.
    app.setStyle("Fusion")

    cfg = Config()
    dictionary = Dictionary(cfg.words_file)

    window = MainWindow(dictionary, cfg)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
