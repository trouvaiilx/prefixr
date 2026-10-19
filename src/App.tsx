import React, { useCallback, useEffect, useRef, useState } from "react";
import { HelpModal } from "./components/HelpModal";
import { ResultsList } from "./components/ResultsList";
import { SearchBar } from "./components/SearchBar";
import { SettingsModal } from "./components/SettingsModal";
import { StatusBar } from "./components/StatusBar";
import { TitleBar } from "./components/TitleBar";
import { useAccessibility } from "./hooks/useAccessibility";
import {
  invokeGetStats,
  invokeLoadSavedWordlist,
  invokeMarkUsed,
  invokePickAndLoadWordlist,
  invokeResetUsed,
  invokeRestoreDefaultWordlist,
  invokeSearch,
  listenGlobalKey,
} from "./lib/tauri";
import {
  EngineStats,
  MatchItem,
  NEXT_SEARCH_MODE,
  NEXT_SORT_ORDER,
  SearchMode,
  SortOrder,
} from "./types/affixr";

export const App: React.FC = () => {
  const {
    settings,
    resolvedTheme,
    updateSetting,
    toggleLightDark,
    resetAccessibility,
  } = useAccessibility();

  const inputRef = useRef<HTMLInputElement | null>(null);

  const [query, setQuery] = useState<string>("");
  const [mode, setMode] = useState<SearchMode>("prefix");
  const [sortOrder, setSortOrder] = useState<SortOrder>("random");
  const [sortLocked, setSortLocked] = useState<boolean>(false);

  const [matches, setMatches] = useState<MatchItem[]>([]);
  const [totalMatches, setTotalMatches] = useState<number>(0);
  const [elapsedUs, setElapsedUs] = useState<number>(0);
  const [highlightIndex, setHighlightIndex] = useState<number>(-1);
  const [typedOverlay, setTypedOverlay] = useState<string>("");

  const [stats, setStats] = useState<EngineStats>({
    wordCount: 472677,
    usedCount: 0,
    wordlistName: "merged_english.txt",
    isCustomWordlist: false,
  });

  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [isHelpOpen, setIsHelpOpen] = useState<boolean>(false);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  // Refs for latest state inside global event listener
  const latestRef = useRef({
    query,
    mode,
    sortOrder,
    matches,
    typedOverlay,
    maxResults: settings.maxResults,
    bgTracking: settings.backgroundTracking,
  });
  useEffect(() => {
    latestRef.current = {
      query,
      mode,
      sortOrder,
      matches,
      typedOverlay,
      maxResults: settings.maxResults,
      bgTracking: settings.backgroundTracking,
    };
  }, [
    query,
    mode,
    sortOrder,
    matches,
    typedOverlay,
    settings.maxResults,
    settings.backgroundTracking,
  ]);

  const focusInput = useCallback(() => {
    if (!isSettingsOpen && !isHelpOpen) {
      inputRef.current?.focus();
    }
  }, [isSettingsOpen, isHelpOpen]);

  // Initial load: restore saved custom wordlist if any, then fetch stats
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const savedPath = localStorage.getItem("affixr.customWordlistPath");
        if (savedPath) {
          const customStats = await invokeLoadSavedWordlist(savedPath);
          if (customStats && mounted) {
            setStats(customStats);
            return;
          }
        }
        const initialStats = await invokeGetStats();
        if (mounted) {
          setStats(initialStats);
        }
      } catch (err) {
        if (mounted) {
          setErrorBanner(String(err));
        }
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  // Run search whenever query, mode, sortOrder, or maxResults changes
  const runSearch = useCallback(
    async (
      q: string,
      m: SearchMode,
      s: SortOrder,
      max: number,
      bgEnabled: boolean
    ) => {
      const trimmed = q.trim();
      setTypedOverlay("");
      setHighlightIndex(-1);

      if (!trimmed) {
        setMatches([]);
        setTotalMatches(0);
        setElapsedUs(0);
        // Ensure background hook stops when query is empty
        await invokeSearch("", m, s, max, false).catch(() => {});
        return;
      }

      try {
        const res = await invokeSearch(trimmed, m, s, max, bgEnabled);
        setMatches(res.matches);
        setTotalMatches(res.totalMatches);
        setElapsedUs(res.elapsedUs);
      } catch (err) {
        setErrorBanner(String(err));
      }
    },
    []
  );

  useEffect(() => {
    runSearch(
      query,
      mode,
      sortOrder,
      settings.maxResults,
      settings.backgroundTracking
    );
  }, [
    query,
    mode,
    sortOrder,
    settings.maxResults,
    settings.backgroundTracking,
    runSearch,
  ]);

  // Focus recovery on window activation
  useEffect(() => {
    const onWinFocus = () => {
      focusInput();
    };
    window.addEventListener("focus", onWinFocus);
    return () => window.removeEventListener("focus", onWinFocus);
  }, [focusInput]);

  // Out-of-focus background typing listener
  useEffect(() => {
    let unlisten: (() => void) | null = null;
    let active = true;

    listenGlobalKey(async (payload) => {
      if (!active) return;
      const {
        query: curQuery,
        mode: curMode,
        sortOrder: curSort,
        matches: curMatches,
        typedOverlay: curOverlay,
        maxResults,
        bgTracking,
      } = latestRef.current;

      const trimmed = curQuery.trim().toLowerCase();
      if (!bgTracking || !trimmed) return;

      if (payload.kind === "char") {
        setTypedOverlay((prev) => prev + payload.value.toLowerCase());
      } else if (payload.kind === "backspace") {
        setTypedOverlay((prev) => prev.slice(0, -1));
      } else if (payload.kind === "enter") {
        const targetWithPrefix =
          curMode === "prefix" ? trimmed + curOverlay : curOverlay;
        const matchedItem = curMatches.find((item) => {
          const w = item.word.toLowerCase();
          return (
            w === targetWithPrefix ||
            (curOverlay.length > 0 && w === curOverlay)
          );
        });

        if (matchedItem) {
          const updatedStats = await invokeMarkUsed(matchedItem.word);
          setStats(updatedStats);
        }

        setTypedOverlay("");
        await runSearch(curQuery, curMode, curSort, maxResults, bgTracking);
      }
    }).then((fn) => {
      if (active) {
        unlisten = fn;
      } else {
        fn();
      }
    });

    return () => {
      active = false;
      if (unlisten) unlisten();
    };
  }, [runSearch]);

  // Actions
  const handleCycleMode = useCallback(() => {
    setMode((prev) => NEXT_SEARCH_MODE[prev]);
    focusInput();
  }, [focusInput]);

  const handleCycleSort = useCallback(() => {
    if (sortLocked) {
      focusInput();
      return;
    }
    setSortOrder((prev) => NEXT_SORT_ORDER[prev]);
    focusInput();
  }, [sortLocked, focusInput]);

  const handleToggleSortLock = useCallback(() => {
    setSortLocked((prev) => !prev);
    focusInput();
  }, [focusInput]);

  const handleSelectWord = useCallback(
    async (word: string) => {
      try {
        const updatedStats = await invokeMarkUsed(word);
        setStats(updatedStats);
        setQuery("");
        focusInput();
      } catch (err) {
        setErrorBanner(String(err));
      }
    },
    [focusInput]
  );

  const handleResetUsed = useCallback(async () => {
    try {
      const updatedStats = await invokeResetUsed();
      setStats(updatedStats);
      await runSearch(
        query,
        mode,
        sortOrder,
        settings.maxResults,
        settings.backgroundTracking
      );
      focusInput();
    } catch (err) {
      setErrorBanner(String(err));
    }
  }, [
    query,
    mode,
    sortOrder,
    settings.maxResults,
    settings.backgroundTracking,
    runSearch,
    focusInput,
  ]);

  const handleSwitchWordlist = useCallback(async () => {
    try {
      const newStats = await invokePickAndLoadWordlist();
      if (newStats) {
        setStats(newStats);
        setErrorBanner(null);
        setQuery("");
      }
    } catch (err) {
      setErrorBanner(String(err));
    } finally {
      focusInput();
    }
  }, [focusInput]);

  const handleRestoreDefaultWordlist = useCallback(async () => {
    try {
      const defaultStats = await invokeRestoreDefaultWordlist();
      setStats(defaultStats);
      setErrorBanner(null);
      setQuery("");
    } catch (err) {
      setErrorBanner(String(err));
    }
  }, []);

  // Global F1 handler & Search input key handler
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === "F1") {
        e.preventDefault();
        handleSwitchWordlist();
      }
    };
    window.addEventListener("keydown", handleGlobalKeyDown);
    return () => window.removeEventListener("keydown", handleGlobalKeyDown);
  }, [handleSwitchWordlist]);

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      handleCycleMode();
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (matches.length > 0) {
        setHighlightIndex((prev) => (prev + 1) % matches.length);
      }
      return;
    }

    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (matches.length > 0) {
        setHighlightIndex((prev) =>
          prev <= 0 ? matches.length - 1 : prev - 1
        );
      }
      return;
    }

    if (e.key === "Enter") {
      e.preventDefault();
      if (highlightIndex >= 0 && highlightIndex < matches.length) {
        handleSelectWord(matches[highlightIndex].word);
      } else {
        setQuery("");
      }
      return;
    }

    if (e.key === "Escape") {
      e.preventDefault();
      setQuery("");
      setTypedOverlay("");
      setHighlightIndex(-1);
    }
  };

  const handleInputBlur = () => {
    if (!isSettingsOpen && !isHelpOpen) {
      window.setTimeout(() => {
        if (!isSettingsOpen && !isHelpOpen) {
          inputRef.current?.focus();
        }
      }, 60);
    }
  };

  return (
    <div className="flex flex-col w-screen h-screen bg-ground text-ink-primary border border-border-strong overflow-hidden">
      <TitleBar
        wordlistName={stats.wordlistName}
        isCustomWordlist={stats.isCustomWordlist}
        resolvedTheme={resolvedTheme}
        alwaysOnTop={settings.alwaysOnTop}
        onToggleTheme={toggleLightDark}
        onToggleAlwaysOnTop={() =>
          updateSetting("alwaysOnTop", !settings.alwaysOnTop)
        }
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenHelp={() => setIsHelpOpen(true)}
        onSwitchWordlist={handleSwitchWordlist}
      />

      <SearchBar
        inputRef={inputRef}
        query={query}
        mode={mode}
        sortOrder={sortOrder}
        sortLocked={sortLocked}
        fontSize={settings.fontSize}
        activeDescendantId={
          highlightIndex >= 0 ? `affixr-row-${highlightIndex}` : undefined
        }
        onQueryChange={setQuery}
        onCycleMode={handleCycleMode}
        onCycleSort={handleCycleSort}
        onToggleSortLock={handleToggleSortLock}
        onKeyDown={handleInputKeyDown}
        onBlur={handleInputBlur}
      />

      {errorBanner && (
        <div
          role="alert"
          className="flex items-center justify-between px-3 py-2 bg-status-incorrect/15 border-b border-status-incorrect/40 text-status-incorrect text-xs shrink-0"
        >
          <span className="truncate">{errorBanner}</span>
          <button
            type="button"
            tabIndex={-1}
            onClick={() => setErrorBanner(null)}
            className="ml-2 underline font-medium shrink-0"
          >
            Dismiss
          </button>
        </div>
      )}

      <ResultsList
        query={query}
        mode={mode}
        matches={matches}
        typedOverlay={typedOverlay}
        highlightIndex={highlightIndex}
        fontSize={settings.fontSize}
        letterSpacing={settings.letterSpacing}
        onSelectWord={handleSelectWord}
        onHoverIndex={setHighlightIndex}
      />

      <StatusBar
        hasQuery={query.trim().length > 0}
        shownCount={matches.length}
        totalMatches={totalMatches}
        elapsedUs={elapsedUs}
        wordCount={stats.wordCount}
        usedCount={stats.usedCount}
        onResetUsed={handleResetUsed}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        settings={settings}
        stats={stats}
        onUpdateSetting={updateSetting}
        onResetSettings={resetAccessibility}
        onSwitchWordlist={handleSwitchWordlist}
        onRestoreDefaultWordlist={handleRestoreDefaultWordlist}
        onClose={() => {
          setIsSettingsOpen(false);
          window.setTimeout(() => inputRef.current?.focus(), 30);
        }}
      />

      <HelpModal
        isOpen={isHelpOpen}
        onClose={() => {
          setIsHelpOpen(false);
          window.setTimeout(() => inputRef.current?.focus(), 30);
        }}
      />
    </div>
  );
};
