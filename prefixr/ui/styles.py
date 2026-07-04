"""
styles.py
─────────
All visual styling lives here.  Business logic, search code, and window
management are completely decoupled from presentation rules.

Color palette (dark, blue-tinted, inspired by Spotlight / Flow Launcher)
─────────────────────────────────────────────────────────────────────────
  Background base   #13131b    near-black with a blue undertone
  Surface 1         #1c1c26    search bar, cards
  Surface 2         #22222e    hover states
  Surface 3         #2a2a3a    active / selected
  Border subtle     #2e2e40
  Accent blue       #4f7ef8    selection highlight
  Text primary      #e8e8f5    main readable text
  Text secondary    #8888aa    muted / status text
  Text placeholder  #44445a    hint text inside input
  Danger            #ff6b6b    error messages
"""

from __future__ import annotations


def build_stylesheet(cfg) -> str:
    """
    Build the full application stylesheet from the Config object so that
    font sizes and font families defined in config.py are respected here.
    """
    ff = cfg.font_family
    fi = cfg.font_size_input
    fr = cfg.font_size_results
    fs = cfg.font_size_status

    return f"""

/* ── Root ──────────────────────────────────────────────────────────── */
QMainWindow {{
    background-color: #13131b;
}}

QWidget#central_widget {{
    background-color: #13131b;
}}

/* ── Search input ───────────────────────────────────────────────────── */
QLineEdit#search_input {{
    background-color: #1c1c26;
    color: #e8e8f5;
    border: 1.5px solid #2e2e40;
    border-radius: 10px;
    padding: 10px 18px;
    font-size: {fi}px;
    font-family: {ff};
    selection-background-color: #2e4a9e;
    selection-color: #ffffff;
}}

QLineEdit#search_input:focus {{
    background-color: #1e1e2a;
    border-color: #4a4a7a;
}}

QLineEdit#search_input[placeholder] {{
    color: #44445a;
}}

/* ── Results list ───────────────────────────────────────────────────── */
QListWidget#results_list {{
    background-color: transparent;
    border: none;
    outline: none;
    color: #d0d0e8;
    font-size: {fr}px;
    font-family: {ff};
    padding: 2px 0px;
}}

QListWidget#results_list::item {{
    padding: 0px;
    border: none;
    background-color: transparent;
}}

QListWidget#results_list::item:selected,
QListWidget#results_list::item:focus {{
    background-color: transparent;
    outline: none;
    border: none;
}}

QListWidget#results_list::item:hover {{
    background-color: transparent;
}}

/* ── Scroll bar ─────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 4px 0;
}}

QScrollBar::handle:vertical {{
    background: #3a3a55;
    border-radius: 2px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: #505077;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    height: 0;
    background: transparent;
}}

/* ── Separator line ─────────────────────────────────────────────────── */
QFrame#separator {{
    color: #22222e;
    background-color: #22222e;
    border: none;
    max-height: 1px;
}}

/* ── Sort toggle button ─────────────────────────────────────────────── */
QPushButton#sort_button {{
    background-color: #1e1e2c;
    color: #8888aa;
    border: 1px solid #2a2a3e;
    border-radius: 7px;
    padding: 5px 13px;
    font-size: 12px;
    font-family: {ff};
    font-weight: 500;
    letter-spacing: 0.2px;
}}

QPushButton#sort_button:hover {{
    background-color: #26263a;
    color: #aaaacc;
    border-color: #3a3a5a;
}}

QPushButton#sort_button:pressed {{
    background-color: #2e2e48;
    color: #ccccee;
}}

/* ── Reset button ──────────────────────────────────────────────────── */
QPushButton#reset_button {{
    background-color: transparent;
    color: #666688;
    border: 1px solid #2a2a3e;
    border-radius: 4px;
    padding: 2px 10px;
    font-size: 11px;
    font-family: {ff};
    font-weight: 500;
}}

QPushButton#reset_button:hover {{
    background-color: #26263a;
    color: #aaaacc;
    border-color: #3a3a5a;
}}

QPushButton#reset_button:pressed {{
    background-color: #2e2e48;
    color: #ccccee;
}}

/* ── Status / footer labels ─────────────────────────────────────────── */
QLabel#status_matches {{
    color: #555570;
    font-size: {fs}px;
    font-family: {ff};
    padding: 0 2px;
}}

QLabel#status_used {{
    color: #4f7ef8;
    font-size: {fs}px;
    font-family: {ff};
    padding: 0 2px;
}}

QLabel#status_wordcount {{
    color: #3e3e55;
    font-size: {fs}px;
    font-family: {ff};
    padding: 0 2px;
}}

/* ── Error / warning banner ─────────────────────────────────────────── */
QLabel#error_banner {{
    color: #ff6b6b;
    background-color: #2a1a1a;
    border: 1px solid #5a2a2a;
    border-radius: 7px;
    padding: 8px 14px;
    font-size: {fs}px;
    font-family: {ff};
}}

"""


# ── Placeholder text ──────────────────────────────────────────────────────────
SEARCH_PLACEHOLDER = "Type to search…"
