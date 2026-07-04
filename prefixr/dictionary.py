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
import random
from enum import Enum, auto
from pathlib import Path
from typing import Sequence

logger = logging.getLogger(__name__)


# ── Sort strategy ─────────────────────────────────────────────────────────────

class SortOrder(Enum):
    """Result ordering applied *after* the prefix range is sliced."""

    SHORTEST_FIRST = auto()
    RANDOM         = auto()
    LONGEST_FIRST  = auto()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def toggled(self) -> "SortOrder":
        """
        Return the next order in the cycle — used by the Tab toggle.

        Cycle: SHORTEST_FIRST → RANDOM → LONGEST_FIRST → SHORTEST_FIRST …
        Random sits between the two length-based extremes.
        """
        _NEXT = {
            SortOrder.SHORTEST_FIRST: SortOrder.RANDOM,
            SortOrder.RANDOM: SortOrder.LONGEST_FIRST,
            SortOrder.LONGEST_FIRST: SortOrder.SHORTEST_FIRST,
        }
        return _NEXT[self]

    def button_label(self) -> str:
        return {
            SortOrder.SHORTEST_FIRST: "↑ Short",
            SortOrder.RANDOM: "Random",
            SortOrder.LONGEST_FIRST: "↓ Long",
        }[self]

    def tooltip(self) -> str:
        return {
            SortOrder.SHORTEST_FIRST: "Shortest matches first  [Tab to toggle]",
            SortOrder.RANDOM: "Random match order  [Tab to toggle]",
            SortOrder.LONGEST_FIRST: "Longest matches first  [Tab to toggle]",
        }[self]


# ── Dictionary engine ─────────────────────────────────────────────────────────

class Dictionary:
    """
    Word-list engine.  The vocabulary is immutable after construction;
    however a mutable ``_used`` set tracks words that the user has marked
    as "used" so they can be hidden from future results until reset.

    Internal representation
    ───────────────────────
    A single sorted list[str] of lowercased, deduplicated words.
    bisect_left gives us the lower bound of any prefix in O(log n).
    The upper bound is derived by incrementing the last character, which is
    valid for all printable Unicode letters (A-Z, accented characters, etc.).
    """

    def __init__(self, words_file: Path) -> None:
        self._words: list[str] = []
        self._used: set[str] = set()
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

    def reload(self, words_file: Path) -> None:
        """
        Replace the current vocabulary with a new word file.
        Clears the used-word set since it refers to the old vocabulary.
        """
        self._used.clear()
        self._load(words_file)

    # ── Public API ────────────────────────────────────────────────────────────

    def prefix_search(
        self,
        prefix: str,
        sort_order: SortOrder,
        max_results: int,
    ) -> list[str]:
        """
        Return up to *max_results* words that start with *prefix*,
        excluding any words in the used set.

        Algorithm
        ─────────
        1. Normalise the prefix to lowercase.
        2. bisect_left → lower index (first word ≥ prefix).
        3. Build an exclusive upper bound string by incrementing the last
           Unicode code point, then bisect_left again → upper index.
        4. Slice self._words[lo:hi] — this is a O(k) copy where k is the
           number of matching words, bounded by the words list size.
        5. Filter out used words.
        6. Order the slice per *sort_order* — by length (ascending/descending)
           for SHORTEST_FIRST/LONGEST_FIRST, or shuffled for RANDOM — then
           return the first max_results items.

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

        # Exclude used words
        if self._used:
            matches = [w for w in matches if w not in self._used]
            if not matches:
                return []

        if sort_order is SortOrder.RANDOM:
            # Shuffle a copy — matches may be a list slice or a filtered list,
            # either way we must not mutate self._words in place.
            shuffled = list(matches)
            random.shuffle(shuffled)
            return shuffled[:max_results]

        # Sort by length; ties broken by lexicographic order (stable sort)
        reverse = sort_order is SortOrder.LONGEST_FIRST
        sorted_matches = sorted(matches, key=len, reverse=reverse)

        return sorted_matches[:max_results]

    # ── Used-word management ──────────────────────────────────────────────────

    def mark_used(self, word: str) -> None:
        """Add *word* to the used set so it is hidden from future searches."""
        self._used.add(word.lower())

    def reset_used(self) -> None:
        """Clear all used words, making every word searchable again."""
        self._used.clear()

    @property
    def used_count(self) -> int:
        """Number of words currently marked as used."""
        return len(self._used)

    # ── Introspection ─────────────────────────────────────────────────────────

    @property
    def word_count(self) -> int:
        """Total number of words in the loaded vocabulary."""
        return len(self._words)

    @property
    def is_loaded(self) -> bool:
        """False if words.txt was missing or empty."""
        return bool(self._words)
