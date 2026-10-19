---
name: Affixr
description: Ultra-fast, keyboard-driven desktop affix & substring search utility set in Cascadia Mono
colors:
  ground-dark: "#0a0e17"
  surface-dark: "#111827"
  elevated-dark: "#1a2336"
  hover-dark: "#1e293e"
  selected-dark: "#1e3158"
  ink-primary-dark: "#f1f5f9"
  ink-secondary-dark: "#a3b3cc"
  accent-dark: "#38bdf8"
  ground-light: "#f4f7fb"
  surface-light: "#ffffff"
  elevated-light: "#eaf0f8"
  ink-primary-light: "#0f172a"
  ink-secondary-light: "#3b4d6b"
  accent-light: "#0284c7"
  status-correct: "#34d399"
  status-incorrect: "#fb7185"
typography:
  search-input:
    fontFamily: '"Cascadia Mono", "Cascadia Code", monospace'
    fontSize: "20px"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "normal"
  result-row:
    fontFamily: '"Cascadia Mono", "Cascadia Code", monospace'
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.35
    letterSpacing: "normal"
  status-counter:
    fontFamily: '"Cascadia Mono", "Cascadia Code", monospace'
    fontSize: "11px"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "normal"
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
---

# Affixr Design System

## Overview

Affixr is a Spotlight-style floating desktop micro-utility designed around rapid visual scanning of hundreds of thousands of words. Every typographic, spatial, and color decision serves uninterrupted keyboard velocity and immediate character recognition.

## Colors

Affixr provides three coordinated palette modes governed via CSS custom properties on `:root` (`[data-theme="dark" | "light"]` and `[data-contrast="normal" | "high"]`):

- **Dark Mode (Default)**: Deep slate ground (`#0a0e17`) paired with elevated navy surfaces (`#111827`, `#1a2336`), crisp alabaster ink (`#f1f5f9`), hue-tinted secondary ink (`#a3b3cc`), and electric sky accent (`#38bdf8`).
- **Light Mode**: Porcelain paper ground (`#f4f7fb`) with pure white surfaces (`#ffffff`), deep slate ink (`#0f172a`), and cobalt accent (`#0284c7`).
- **High-Contrast Mode (WCAG AAA)**: Enforces ≥7:1 contrast ratios across all text and borders for effortless legibility.
- **Semantic Background-Typing Tokens**:
  - Correct letter: `#34d399` (dark) / `#059669` (light), paired with a bottom underline for colorblind accessibility.
  - Incorrect letter: `#fb7185` (dark) / `#e11d48` (light), paired with a strikethrough line.

## Typography

- **Primary Typeface**: **Cascadia Mono** (`@fontsource/cascadia-mono` weights 400, 600, 700) across all search inputs, result items, keyboard hints, and status counters.
- **Numeric Discipline**: `font-variant-numeric: tabular-nums` and `font-feature-settings: "tnum" 1, "zero" 1` ensure character lengths, match counts, and latency metrics never jitter during rapid typing.
- **Accessibility Scaling**: 4 user-selectable scale presets (`Compact`, `Normal`, `Relaxed`, `Large`) plus an optional `Wide Character Tracking` mode (`tracking-wider`) for effortless character-by-character reading.

## Layout

- **Spotlight Floating Window**: 390×680px default frameless window (`minWidth: 350`, `minHeight: 320`, `alwaysOnTop: true`).
- **Four-Zone Vertical Topology**:
  1. `TitleBar` (40px fixed): Custom draggable region, brand logo (`assets/logo.png`), active wordlist switcher pill, and quick utility actions (Pin, Theme, Settings, Help, Minimize, Close).
  2. `SearchBar` (56px fixed): Integrated `SearchModePill` (`Tab` cycle), auto-focused input field, and mouse-only Sort Order + Padlock controls.
  3. `ResultsList` (flexible `1fr` scrollable): Keyboard-navigable `listbox` with sub-character affix highlighting and background-typing overlays.
  4. `StatusBar` (32px fixed): Live match summary (`aria-live="polite"`), microsecond latency indicator, used-word counter with reset trigger, and total vocabulary count.

## Components

- **SearchModePill**: Displays the active search mode with Lucide directional chevrons:
  - **Prefix**: `ChevronRight` (`>`)
  - **Suffix**: `ChevronLeft` (`<`)
  - **Contains**: `ChevronDown` (`v`)
- **ResultRow**: Highlights matching prefix, suffix, or substring spans in `--accent-primary` (`font-weight: 600`) and overlays out-of-focus background-typed characters in semantic green/red with non-color cues (underline / strikethrough).

## Do's and Don'ts

- **Do** use `tabIndex={-1}` and `onMouseDown={(e) => e.preventDefault()}` on all toolbar buttons so clicking controls never steals keyboard focus from the search input.
- **Do** use Lucide vector icons consistently across all interactive controls.
- **Don't** bind `Tab` to anything other than cycling the search mode (`Prefix` → `Suffix` → `Contains`).
- **Don't** rely on color alone for background-typing correctness; always pair green/red with underline/strikethrough.
