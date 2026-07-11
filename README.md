# Prefixr

A minimalist, ultra-fast desktop prefix-search tool built with Python + PySide6.
Inspired by **Spotlight** and **Flow Launcher** — dark-mode, keyboard-driven, zero latency.

```
┌────────────────────────────────────────────────────┐
│  pre█                                 [Random] [🔓]     
│  ────────────────────────────────────────────────  │
│  precise                                           │
│  prepare                                           │
│  preach                                            │
│  prefer                                            │
│  precede                                           │
│  premier                                           │
│  …                                                 │
│  3 matches                                    (?)  │
└────────────────────────────────────────────────────┘
```

---

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Project structure](#project-structure)
- [Packaging into a single executable](#packaging-into-a-single-executable)
- [Keyboard reference](#keyboard-reference)
- [Sort order & the lock](#sort-order--the-lock)
- [Background typing (out-of-focus word tracking)](#background-typing-out-of-focus-word-tracking)
- [In-app help](#in-app-help)
- [Extending](#extending)

---

## Features

| Feature | Detail |
|---|---|
| **Prefix search** | `bisect_left` binary search — O(log n + k) on 466 k words |
| **Always-focused input** | Caret returns automatically on Alt-Tab / window activation |
| **Sort toggle** | `Tab` or the button cycles shortest-first → random → longest-first (launches on **random**) |
| **Sort lock** | Click the padlock next to the sort button to freeze the current order — `Tab` and the button both stop cycling until you unlock it |
| **Prefix highlighting** | The typed prefix is highlighted in every result, at a glance |
| **Background typing** | While Alt-Tabbed into another app, keeps tracking what you type and highlights each result green/red per letter — see below |
| **Escape to clear** | Clears the search field; window stays open |
| **No console** | `.pyw` entry-point suppresses the Windows console window |
| **Dark mode** | Blue-tinted near-black palette, Spotlight-inspired |
| **Wordlist switching** | Press `F1` to load a different `.txt` word list on the fly (persists across restarts via native OS settings) |
| **In-app help** | Click the `?` button (bottom-right) for a tabbed reference: About / How to Use / Shortcuts / Background Typing |

---

## Setup

### 1 — Install dependencies

```bash
pip install PySide6 pynput
```

`pynput` powers the background-typing feature (a system-wide keyboard hook
that keeps working while another app is focused). Two platform notes:

- **macOS**: the first time it runs, grant the terminal / app **Input
  Monitoring** (and possibly **Accessibility**) permission under
  *System Settings → Privacy & Security*, or the hook silently sees nothing.
- **Linux**: works under X11. Under native **Wayland**, most compositors
  block global key hooks for security reasons — background typing may not
  function there, though the rest of the app is unaffected.

If `pynput` isn't installed at all, Prefixr still runs fine — it just logs
a warning and background typing is disabled; normal in-window search is
unaffected either way.

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
icon.ico                   Application icon
requirements.txt           Project dependencies
prefixr/
├── __init__.py
├── config.py                All tuneable constants (frozen dataclass)
├── dictionary.py            Word loading, normalisation, bisect search, sort orders
├── global_key_listener.py   OS-level a-z/Backspace/Enter hook (pynput), Qt signals
└── ui/
    ├── __init__.py
    ├── styles.py          Full dark-mode QSS stylesheet
    ├── search_bar.py      Always-focused QLineEdit + focus recovery
    ├── results_view.py    Rich-text result rows: prefix highlight + typing overlay
    ├── help_dialog.py     Tabbed '?' help window (About / Usage / Shortcuts / Background Typing)
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

## Packaging into a single executable

### 1 — Install PyInstaller

```bash
pip install pyinstaller
```

### 2 — Build

```bash
pyinstaller main.pyw \
  --onefile \
  --windowed \
  --name "Prefixr" \
  --icon "icon.ico" \
  --add-data "words.txt:." \
  --add-data "icon.ico:." \
  --add-data "prefixr:prefixr"
```

On **Windows** use `;` instead of `:` as the separator:

```bash
pyinstaller main.pyw --onefile --windowed --name "Prefixr" --icon "icon.ico" --add-data "words.txt;." --add-data "icon.ico;." --add-data "prefixr;prefixr"
```

### 3 — Find your executable

```bash
dist/Prefixr.exe    # Windows
dist/Prefixr        # macOS / Linux
```

The `words.txt` word list is bundled inside the executable — no external files needed.

---

## Keyboard reference

| Key | Action |
|---|---|
| Any letter | Instant prefix search |
| `Backspace` | Narrow/widen search |
| `Tab` | Cycle result sort order (shortest → random → longest) — no-op while locked |
| `Escape` | Clear search field |
| `↑` / `↓` | Move the keyboard highlight through results |
| `Enter` (focused) | Confirm the highlighted result / mark it used |
| `F1` | Open file picker to switch word list |

The padlock button and `?` help button are mouse-only; they don't have
dedicated key shortcuts.

---

## Sort order & the lock

Prefixr now **launches with random order by default** rather than
shortest-first — the idea being that with a large word list, a fixed
"shortest first" order tends to surface the same handful of short words
over and over, while random keeps every search feeling fresh.

Next to the sort button is a padlock (🔓 / 🔒):

- **Unlocked (🔓, default)** — `Tab` and the sort button both cycle
  shortest → random → longest as before.
- **Locked (🔒)** — click the padlock to freeze whatever order is currently
  active. The sort button becomes visibly disabled and both `Tab` and
  clicking it stop changing the order, until you click the padlock again
  to unlock it.

This is useful once you've found the ordering you like for a session and
want to make sure a stray `Tab` press doesn't shuffle it.

---

## Background typing (out-of-focus word tracking)

Prefixr always stays on top, so a common flow is: type a prefix, Alt-Tab
into whatever you're actually writing in (a game, a document, a terminal),
and type out the full word there. Prefixr keeps watching:

- Every letter you type — anywhere, in any app — is compared against each
  visible result at the matching position: **green** if it's correct,
  **red** if it isn't.
- `Backspace` undoes the last letter, so a typo doesn't throw off the
  highlighting.
- The moment you press `Enter`, if what you've typed (prefix + everything
  since) exactly matches one of the visible results, that word is marked
  **used** automatically — exactly as if you'd clicked it.

This only activates while the search field actually has a prefix in it —
with an empty search field, no keystrokes are observed anywhere, focused or
not. It's also a passive observer: it never blocks or consumes a keystroke,
so the app you're typing into always receives every key normally.

---

## In-app help

Click the small `?` button in the bottom-right corner of the window to open
a help dialog. To keep things readable, it's split into four tabs instead
of one long page:

| Tab | Contents |
|---|---|
| **About** | What Prefixr is and how it's built |
| **How to Use** | A short walkthrough of the core search/select flow |
| **Shortcuts** | The full keyboard reference, in one table |
| **Background Typing** | How the out-of-focus tracking feature works |

The dialog is modal and mouse-driven — closing it returns keyboard focus
straight back to the search bar.

---

## Extending

### Fuzzy matching
Add a `fuzzy_search(query, …)` method to `Dictionary` using `rapidfuzz` or
`difflib`. Wire a second mode in `MainWindow` without touching `SearchBar`
or `ResultsView`.

### Inline definitions
Attach a `dict[str, str]` to `Dictionary` loaded from a secondary file.
Create a `DefinitionDelegate(QStyledItemDelegate)` in `ui/` and set it on
`ResultsView` — zero changes to the search or focus logic.

### Frequency-based ranking
Store per-word frequency scores alongside `_words`. Pass an optional
`weight_key` callable to `prefix_search()` and sort by `(len, -freq)`.

### Configuration file
Replace `Config`'s `field(default_factory=…)` defaults with values read
from a `~/.prefixr/config.toml` at import time — one change, propagates
everywhere.