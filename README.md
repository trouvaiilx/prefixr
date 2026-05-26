# Desktop Dictionary

A minimalist, ultra-fast desktop dictionary lookup tool built with Python + PySide6.
Inspired by **Spotlight** and **Flow Launcher** — dark-mode, keyboard-driven, zero latency.

---

## Features

| Feature | Detail |
|---|---|
| **Prefix search** | `bisect_left` binary search — O(log n + k) on 466 k words |
| **Always-focused input** | Caret returns automatically on Alt-Tab / window activation |
| **Sort toggle** | `Tab` or the button flips between shortest-first ↔ longest-first |
| **Escape to clear** | Clears the search field; window stays open |
| **No console** | `.pyw` entry-point suppresses the Windows console window |
| **Dark mode** | Blue-tinted near-black palette, Spotlight-inspired |

---

## Setup

### 1 — Install dependencies

```bash
pip install PySide6
```

### 2 — Add your word list

Place a `words.txt` file **next to `main.pyw`**.  
The file must contain one word per line (UTF-8).  
A 466 k-word English list is available from several open sources, e.g.:

```
https://github.com/dwyl/english-words  →  words_alpha.txt
```

Rename / symlink it to `words.txt`.

### 3 — Run

```bash
# Windows (no console)
pythonw main.pyw

# macOS / Linux
python main.pyw
```

Or double-click `main.pyw` on Windows if `.pyw` is associated with `pythonw.exe`.

---

## Project structure

```
main.pyw                   Entry point (no console on Windows)
words.txt                  Your word list — one word per line
dict_app/
├── __init__.py
├── config.py              All tuneable constants (frozen dataclass)
├── dictionary.py          Word loading, normalisation, bisect search
└── ui/
    ├── __init__.py
    ├── styles.py          Full dark-mode QSS stylesheet
    ├── search_bar.py      Always-focused QLineEdit + focus recovery
    ├── results_view.py    Optimised QListWidget for rapid refresh
    └── main_window.py     Mediator — wires all components together
```

### Dependency graph

```
main.pyw
  └─ MainWindow  ←  Config
       ├─ SearchBar      (no domain knowledge)
       ├─ ResultsView    (no domain knowledge)
       └─ Dictionary     (no Qt imports)
```

Each layer depends only downward; the domain layer (`dictionary.py`) is
completely decoupled from Qt and can be unit-tested with plain `pytest`.

---

## Keyboard reference

| Key | Action |
|---|---|
| Any letter | Instant prefix search |
| `Backspace` | Narrow/widen search |
| `Tab` | Toggle result sort order |
| `Escape` | Clear search field |

---

## Extending

### Fuzzy matching
Add a `fuzzy_search(query, …)` method to `Dictionary` using `rapidfuzz` or
`difflib`.  Wire a second mode in `MainWindow` without touching `SearchBar`
or `ResultsView`.

### Inline definitions
Attach a `dict[str, str]` to `Dictionary` loaded from a secondary file.
Create a `DefinitionDelegate(QStyledItemDelegate)` in `ui/` and set it on
`ResultsView` — zero changes to the search or focus logic.

### Frequency-based ranking
Store per-word frequency scores alongside `_words`.  Pass an optional
`weight_key` callable to `prefix_search()` and sort by `(len, -freq)`.

### Configuration file
Replace `Config`'s `field(default_factory=…)` defaults with values read
from a `~/.dict_app/config.toml` at import time — one change, propagates
everywhere.
