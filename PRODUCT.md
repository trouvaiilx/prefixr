# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Tauri v2 + Rust + React 19 + TypeScript + Tailwind CSS (managed with pnpm)

## Users

Writers, developers, puzzle/word-game players, and command-line power users who need instant, zero-latency word lookups while working in other desktop applications (editors, games, writing tools).

## Product Purpose

Affixr is an ultra-fast, keyboard-driven desktop dictionary and affix discovery utility. It provides instant filtering across 470,000+ words by prefix, suffix, and substring containment with persistent always-on-top visibility and out-of-focus background typing feedback.

## Positioning

Unlike web-based dictionaries or heavy launcher plugins, Affixr operates as a zero-latency, floating Spotlight-style micro-utility with sub-millisecond Rust binary search, out-of-focus keystroke tracking, and instant keyboard cycle between prefix, suffix, and contains search modes.

## Operating Context

Runs as an always-on-top floating window alongside writing environments, code editors, or full-screen games. Interacted with via rapid keyboard strokes (`Tab`, arrows, `Enter`, `Escape`) or passive background observation while typing in external applications.

## Capabilities and Constraints

- **Search Modes**: Prefix (`ChevronRight`), Suffix (`ChevronLeft`), and Contains (`ChevronDown`), cycled via `Tab`.
- **Performance**: Instant binary search for prefix and reversed suffix ($O(\log N + K)$) and parallel substring search for contains on 472,000+ words in Rust.
- **Background Typing**: Passive out-of-focus keyboard observer tracking matching candidates with real-time green/red character highlights and automatic used-word retirement on Enter.
- **Window Mechanics**: Floating Spotlight-style panel (`alwaysOnTop: true`), custom drag handle, auto-focus retention.
- **Sort Control**: Mouse-click sort toggle (Shortest, Random, Longest) with padlock lock/unlock.
- **Custom Wordlists**: On-the-fly dictionary switching (`F1` or UI picker).

## Brand Commitments

- **Name**: Affixr (formerly Prefixr).
- **Typography**: Cascadia Mono across all UI text, search inputs, and tabular counters.
- **Iconography**: Lucide icons (`ChevronRight`, `ChevronLeft`, `ChevronDown`, `Lock`, `Unlock`, `Sun`, `Moon`, `HelpCircle`, `Settings`).
- **Logo**: Modern brand mark at `assets/logo.png`.

## Accessibility & Inclusion

- Light and Dark modes with clean contrast ratios.
- Scalable typography presets (Compact, Standard, Relaxed, Large).
- High-contrast mode for enhanced visual delineation.
- Reduced motion toggle honoring user preferences.
- Accessible ARIA semantics (`role="combobox"`, `role="listbox"`, `aria-activedescendant`).
