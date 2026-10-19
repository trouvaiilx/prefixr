import { invoke } from "@tauri-apps/api/core";
import { listen, UnlistenFn } from "@tauri-apps/api/event";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { open } from "@tauri-apps/plugin-dialog";
import {
  EngineStats,
  GlobalKeyPayload,
  MatchItem,
  SearchMode,
  SearchResponse,
  SortOrder,
} from "../types/affixr";

export function isTauriEnv(): boolean {
  return typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;
}

// Lightweight fallback vocabulary when running in browser-only Vite dev preview
const BROWSER_FALLBACK_WORDS = [
  "affix",
  "affixation",
  "affixes",
  "affixing",
  "prefix",
  "prefixes",
  "prefixing",
  "suffix",
  "suffixation",
  "suffixes",
  "preach",
  "precise",
  "precisely",
  "precision",
  "preclude",
  "predict",
  "prediction",
  "prefer",
  "preference",
  "prelude",
  "premier",
  "prepare",
  "presence",
  "preserve",
  "prevail",
  "prevent",
  "archipelago",
  "architecture",
  "archive",
  "monarch",
  "patriarch",
  "researching",
  "searching",
  "cascadia",
  "lexicon",
  "dictionary",
  "typography",
  "accessibility",
  "keyboard",
  "spotlight",
  "velocity",
];
const browserUsed = new Set<string>();

export async function invokeSearch(
  query: string,
  mode: SearchMode,
  sortOrder: SortOrder,
  maxResults: number,
  bgTrackingEnabled: boolean
): Promise<SearchResponse> {
  if (!isTauriEnv()) {
    const q = query.trim().toLowerCase();
    if (!q) return { matches: [], totalMatches: 0, elapsedUs: 12 };
    let filtered = BROWSER_FALLBACK_WORDS.filter((w) => !browserUsed.has(w));
    if (mode === "prefix") {
      filtered = filtered.filter((w) => w.startsWith(q));
    } else if (mode === "suffix") {
      filtered = filtered.filter((w) => w.endsWith(q));
    } else {
      filtered = filtered.filter((w) => w.includes(q));
    }
    const totalMatches = filtered.length;
    if (sortOrder === "shortest") {
      filtered.sort((a, b) => a.length - b.length || a.localeCompare(b));
    } else if (sortOrder === "longest") {
      filtered.sort((a, b) => b.length - a.length || a.localeCompare(b));
    }
    const matches: MatchItem[] = filtered.slice(0, maxResults).map((word) => ({
      word,
      matchStart:
        mode === "prefix"
          ? 0
          : mode === "suffix"
            ? Math.max(0, word.length - q.length)
            : Math.max(0, word.indexOf(q)),
      matchLen: q.length,
    }));
    return { matches, totalMatches, elapsedUs: 45 };
  }

  return invoke<SearchResponse>("search", {
    query,
    mode,
    sortOrder,
    maxResults,
    bgTrackingEnabled,
  });
}

export async function invokeMarkUsed(word: string): Promise<EngineStats> {
  if (!isTauriEnv()) {
    browserUsed.add(word.toLowerCase());
    return {
      wordCount: BROWSER_FALLBACK_WORDS.length,
      usedCount: browserUsed.size,
      wordlistName: "merged_english.txt",
      isCustomWordlist: false,
    };
  }
  return invoke<EngineStats>("mark_used", { word });
}

export async function invokeResetUsed(): Promise<EngineStats> {
  if (!isTauriEnv()) {
    browserUsed.clear();
    return {
      wordCount: BROWSER_FALLBACK_WORDS.length,
      usedCount: 0,
      wordlistName: "merged_english.txt",
      isCustomWordlist: false,
    };
  }
  return invoke<EngineStats>("reset_used");
}

export async function invokeGetStats(): Promise<EngineStats> {
  if (!isTauriEnv()) {
    return {
      wordCount: 472677,
      usedCount: browserUsed.size,
      wordlistName: "merged_english.txt",
      isCustomWordlist: false,
    };
  }
  return invoke<EngineStats>("get_engine_stats");
}

export async function invokePickAndLoadWordlist(): Promise<EngineStats | null> {
  if (!isTauriEnv()) return null;

  const win = getCurrentWindow();
  // Temporarily allow dialog above window
  await win.setAlwaysOnTop(false).catch(() => {});

  let selectedPath: string | null = null;
  try {
    const selected = await open({
      title: "Select a word list (.txt)",
      multiple: false,
      directory: false,
      filters: [
        { name: "Text Dictionary", extensions: ["txt"] },
        { name: "All Files", extensions: ["*"] },
      ],
    });
    if (typeof selected === "string") {
      selectedPath = selected;
    }
  } finally {
    await win.setAlwaysOnTop(true).catch(() => {});
  }

  if (!selectedPath) return null;

  const stats = await invoke<EngineStats>("load_custom_wordlist", {
    path: selectedPath,
  });
  try {
    localStorage.setItem("affixr.customWordlistPath", selectedPath);
  } catch {
    // ignore storage errors
  }
  return stats;
}

export async function invokeLoadSavedWordlist(
  path: string
): Promise<EngineStats | null> {
  if (!isTauriEnv()) return null;
  try {
    return await invoke<EngineStats>("load_custom_wordlist", { path });
  } catch {
    return null;
  }
}

export async function invokeRestoreDefaultWordlist(): Promise<EngineStats> {
  try {
    localStorage.removeItem("affixr.customWordlistPath");
  } catch {
    // ignore
  }
  if (!isTauriEnv()) {
    return {
      wordCount: 472677,
      usedCount: 0,
      wordlistName: "merged_english.txt",
      isCustomWordlist: false,
    };
  }
  return invoke<EngineStats>("restore_default_wordlist");
}

export async function invokeSetAlwaysOnTop(alwaysOnTop: boolean): Promise<void> {
  if (!isTauriEnv()) return;
  await getCurrentWindow().setAlwaysOnTop(alwaysOnTop).catch(() => {});
}

export async function invokeMinimizeWindow(): Promise<void> {
  if (!isTauriEnv()) return;
  await getCurrentWindow().minimize().catch(() => {});
}

export async function invokeCloseWindow(): Promise<void> {
  if (!isTauriEnv()) return;
  await getCurrentWindow().close().catch(() => {});
}

export async function invokeStartDragging(): Promise<void> {
  if (!isTauriEnv()) return;
  await getCurrentWindow().startDragging().catch(() => {});
}

export async function listenGlobalKey(
  handler: (payload: GlobalKeyPayload) => void
): Promise<UnlistenFn> {
  if (!isTauriEnv()) {
    return () => {};
  }
  return listen<GlobalKeyPayload>("affixr://global-key", (event) => {
    handler(event.payload);
  });
}
