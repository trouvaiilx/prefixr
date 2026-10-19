export type SearchMode = "prefix" | "suffix" | "contains";

export type SortOrder = "shortest" | "random" | "longest";

export interface MatchItem {
  word: string;
  matchStart: number;
  matchLen: number;
}

export interface SearchResponse {
  matches: MatchItem[];
  totalMatches: number;
  elapsedUs: number;
}

export interface EngineStats {
  wordCount: number;
  usedCount: number;
  wordlistName: string;
  isCustomWordlist: boolean;
}

export type GlobalKeyPayload =
  | { kind: "char"; value: string }
  | { kind: "backspace" }
  | { kind: "enter" };

export type ThemePreference = "dark" | "light" | "system";

export type FontSizeScale = "compact" | "normal" | "relaxed" | "large";

export type LetterSpacingMode = "normal" | "wide";

export interface AccessibilitySettings {
  theme: ThemePreference;
  fontSize: FontSizeScale;
  highContrast: boolean;
  reducedMotion: boolean;
  letterSpacing: LetterSpacingMode;
  alwaysOnTop: boolean;
  backgroundTracking: boolean;
  maxResults: number;
}

export const NEXT_SEARCH_MODE: Record<SearchMode, SearchMode> = {
  prefix: "suffix",
  suffix: "contains",
  contains: "prefix",
};

export const SEARCH_MODE_META: Record<
  SearchMode,
  {
    label: string;
    shortLabel: string;
    placeholder: string;
    description: string;
  }
> = {
  prefix: {
    label: "Prefix",
    shortLabel: "PRE",
    placeholder: "Type prefix…",
    description: "Matches words starting with query [Tab to cycle]",
  },
  suffix: {
    label: "Suffix",
    shortLabel: "SUF",
    placeholder: "Type suffix…",
    description: "Matches words ending with query [Tab to cycle]",
  },
  contains: {
    label: "Contains",
    shortLabel: "CON",
    placeholder: "Type substring…",
    description: "Matches words containing query anywhere [Tab to cycle]",
  },
};

export const NEXT_SORT_ORDER: Record<SortOrder, SortOrder> = {
  shortest: "random",
  random: "longest",
  longest: "shortest",
};

export const SORT_ORDER_META: Record<
  SortOrder,
  {
    label: string;
    tooltip: string;
  }
> = {
  shortest: {
    label: "Short",
    tooltip: "Shortest matches first (click to cycle)",
  },
  random: {
    label: "Random",
    tooltip: "Random match order (click to cycle)",
  },
  longest: {
    label: "Long",
    tooltip: "Longest matches first (click to cycle)",
  },
};
