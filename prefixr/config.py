"""
config.py
─────────
Single source of truth for every tuneable constant in the application.
Changing a value here propagates everywhere without touching business logic or UI.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path


def _words_path() -> Path:
    # When frozen by PyInstaller, bundled files are extracted to sys._MEIPASS.
    # In normal development, fall back to the project root beside main.pyw.
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent.parent))
    return base / "words.txt"

def _icon_path() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent.parent))
    return base / "icon.ico"


@dataclass(frozen=True)
class Config:
    # ── Paths ────────────────────────────────────────────────────────────────
    words_file: Path = field(default_factory=_words_path)
    icon_file: Path = field(default_factory=_icon_path)

    # ── Search behaviour ─────────────────────────────────────────────────────
    # Maximum number of results rendered at once.  Raise freely; bisect keeps
    # the search O(log n + k) regardless, and rendering 20-50 QListWidgetItems
    # is negligible on any modern GPU.
    max_results: int = 50

    # ── Window geometry ──────────────────────────────────────────────────────
    window_title: str = "Prefixr"
    window_width: int = 360
    window_height: int = 700
    window_min_width: int = 360
    window_min_height: int = 260

    # ── Typography ───────────────────────────────────────────────────────────
    # CSS font-family fallback chain used in the stylesheet.
    # "Segoe UI" (Windows) → "SF Pro Text" (macOS) → "Inter" → generic sans.
    font_family: str = (
        "'Segoe UI', 'SF Pro Text', 'Inter', 'Helvetica Neue', sans-serif"
    )
    font_size_input: int = 22    # px — the main search field
    font_size_results: int = 20  # px — result list items
    font_size_status: int = 12   # px — footer status text

    # ── Focus recovery ───────────────────────────────────────────────────────
    # Milliseconds after a focusOut event before the search bar attempts to
    # reclaim focus.  Small enough to be imperceptible; large enough to allow
    # legitimate inter-widget focus transitions (e.g., OS dialogs) to settle.
    focus_recovery_delay_ms: int = 60
