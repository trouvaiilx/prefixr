"""
dictionary.py
─────────────
Pure data layer.  Zero Qt imports; fully unit-testable in isolation.

Responsibilities
────────────────
• Load & normalize a flat word-list file into a sorted list held in RAM.
• Expose a fast prefix_search() backed by bisect for O(log n) range lookup.
• Provide a SortOrder enum used by both the search engine and the UI layer.

Extension points
────────────────
• Fuzzy / phonetic matching:  add a new search method; existing code unchanged.
• Inline definitions:         attach a parallel dict[str, str] populated from
                              a secondary file and exposed through a separate
                              method.
• Ranking / frequency data:   store per-word weights alongside the word list
                              and accept an optional sort key in prefix_search().
"""

from __future__ import annotations

import bisect
import logging
from enum import Enum, auto
from pathlib import Path
from typing import Sequence

logger = logging.getLogger(__name__)


# ── Sort strategy ─────────────────────────────────────────────────────────────

class SortOrder(Enum):
    """Result ordering applied *after* the prefix range is sliced."""

    SHORTEST_FIRST = auto()
    LONGEST_FIRST  = auto()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def toggled(self) -> "SortOrder":
        """Return the other order — used by the Tab toggle."""
        return (
            SortOrder.LONGEST_FIRST
            if self is SortOrder.SHORTEST_FIRST
            else SortOrder.SHORTEST_FIRST
        )

    def button_label(self) -> str:
        return "↑ Short" if self is SortOrder.SHORTEST_FIRST else "↓ Long"

    def tooltip(self) -> str:
        return (
            "Shortest matches first  [Tab to toggle]"
            if self is SortOrder.SHORTEST_FIRST
            else "Longest matches first  [Tab to toggle]"
        )


# ── Dictionary engine ─────────────────────────────────────────────────────────

class Dictionary:
    """
    Immutable after construction.  Thread-safe to read; never written to after
    __init__ completes, so no locking is needed for concurrent reads.

    Internal representation
    ───────────────────────
    A single sorted list[str] of lowercased, deduplicated words.
    bisect_left gives us the lower bound of any prefix in O(log n).
    The upper bound is derived by incrementing the last character, which is
    valid for all printable Unicode letters (A-Z, accented characters, etc.).
    """

    def __init__(self, words_file: Path) -> None:
        self._words: list[str] = []
        self._load(words_file)

    # ── Construction ──────────────────────────────────────────────────────────

    def _load(self, path: Path) -> None:
        """
        Read words_file, normalise each line to lowercase, deduplicate,
        sort lexicographically, and store the result in self._words.

        Any line that is empty after stripping is silently ignored so the
        engine tolerates trailing newlines, blank lines, and Windows CRLF.
        """
        try:
            raw_text = path.read_text(encoding="utf-8", errors="ignore")
        except FileNotFoundError:
            logger.error("words.txt not found at %s", path)
            return
        except OSError as exc:
            logger.error("Could not read %s: %s", path, exc)
            return

        seen: set[str] = set()
        words: list[str] = []

        for line in raw_text.splitlines():
            word = line.strip().lower()
            if word and word not in seen:
                seen.add(word)
                words.append(word)

        words.sort()
        self._words = words
        logger.info("Loaded %d words from %s", len(self._words), path)

    # ── Public API ────────────────────────────────────────────────────────────

    def prefix_search(
        self,
        prefix: str,
        sort_order: SortOrder,
        max_results: int,
    ) -> list[str]:
        """
        Return up to *max_results* words that start with *prefix*.

        Algorithm
        ─────────
        1. Normalise the prefix to lowercase.
        2. bisect_left → lower index (first word ≥ prefix).
        3. Build an exclusive upper bound string by incrementing the last
           Unicode code point, then bisect_left again → upper index.
        4. Slice self._words[lo:hi] — this is a O(k) copy where k is the
           number of matching words, bounded by the words list size.
        5. Sort the slice by length; return the first max_results items.

        The overall complexity is O(log n + k·log k) where n = vocabulary
        size and k = number of prefix matches.  In practice k << n for any
        non-trivial prefix, making this imperceptibly fast even for 466k words.

        Returns an empty list for an empty prefix (no "show everything" mode).
        """
        if not prefix or not self._words:
            return []

        p = prefix.strip().lower()
        if not p:
            return []

        # Lower bound — first index where a word could begin with p
        lo = bisect.bisect_left(self._words, p)

        # Upper bound — exclusive end of the prefix range.
        # Incrementing the last code point by 1 gives the lexicographic
        # successor of all strings starting with p.
        last_cp = ord(p[-1])
        if last_cp < 0x10FFFF:
            upper = p[:-1] + chr(last_cp + 1)
            hi = bisect.bisect_left(self._words, upper, lo)
        else:
            # Edge case: last char is the max Unicode code point
            hi = len(self._words)

        # Slice — all words in the prefix range
        matches: Sequence[str] = self._words[lo:hi]

        if not matches:
            return []

        # Sort by length; ties broken by lexicographic order (stable sort)
        reverse = sort_order is SortOrder.LONGEST_FIRST
        sorted_matches = sorted(matches, key=len, reverse=reverse)

        return sorted_matches[:max_results]

    # ── Introspection ─────────────────────────────────────────────────────────

    @property
    def word_count(self) -> int:
        """Total number of words in the loaded vocabulary."""
        return len(self._words)

    @property
    def is_loaded(self) -> bool:
        """False if words.txt was missing or empty."""
        return bool(self._words)
