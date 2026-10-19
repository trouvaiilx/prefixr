import React from "react";
import {
  ArrowDownWideNarrow,
  ArrowUpNarrowWide,
  Lock,
  Shuffle,
  Unlock,
  X,
} from "lucide-react";
import { FONT_SIZE_STYLES } from "../hooks/useAccessibility";
import {
  FontSizeScale,
  SEARCH_MODE_META,
  SearchMode,
  SORT_ORDER_META,
  SortOrder,
} from "../types/affixr";
import { SearchModePill } from "./SearchModePill";

interface SearchBarProps {
  inputRef: React.RefObject<HTMLInputElement | null>;
  query: string;
  mode: SearchMode;
  sortOrder: SortOrder;
  sortLocked: boolean;
  fontSize: FontSizeScale;
  activeDescendantId?: string;
  onQueryChange: (value: string) => void;
  onCycleMode: () => void;
  onCycleSort: () => void;
  onToggleSortLock: () => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  onBlur: (e: React.FocusEvent<HTMLInputElement>) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  inputRef,
  query,
  mode,
  sortOrder,
  sortLocked,
  fontSize,
  activeDescendantId,
  onQueryChange,
  onCycleMode,
  onCycleSort,
  onToggleSortLock,
  onKeyDown,
  onBlur,
}) => {
  const modeMeta = SEARCH_MODE_META[mode];
  const sortMeta = SORT_ORDER_META[sortOrder];
  const sizeStyles = FONT_SIZE_STYLES[fontSize];

  const renderSortIcon = () => {
    switch (sortOrder) {
      case "shortest":
        return <ArrowUpNarrowWide className="w-3.5 h-3.5 shrink-0" />;
      case "random":
        return <Shuffle className="w-3.5 h-3.5 shrink-0" />;
      case "longest":
        return <ArrowDownWideNarrow className="w-3.5 h-3.5 shrink-0" />;
    }
  };

  return (
    <div className="px-3 pt-3 pb-2.5 bg-surface border-b border-border-subtle shrink-0">
      <div className="flex items-center gap-2">
        {/* Search Input Container with integrated Mode Pill */}
        <div className="flex items-center flex-1 min-w-0 h-11 px-2 rounded-lg bg-ground border border-border-strong focus-within:border-border-focus transition-colors">
          <SearchModePill mode={mode} onCycleMode={onCycleMode} />

          <input
            ref={inputRef}
            type="text"
            role="combobox"
            aria-expanded={true}
            aria-controls="affixr-results-listbox"
            aria-activedescendant={activeDescendantId}
            aria-autocomplete="list"
            aria-label={`Search dictionary by ${modeMeta.label}`}
            autoFocus
            spellCheck={false}
            autoCapitalize="off"
            autoComplete="off"
            autoCorrect="off"
            value={query}
            placeholder={modeMeta.placeholder}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={onKeyDown}
            onBlur={onBlur}
            className={`w-full min-w-0 bg-transparent px-2.5 text-ink-primary placeholder:text-ink-muted focus:outline-none ${sizeStyles.inputClass}`}
          />

          {query.length > 0 && (
            <button
              type="button"
              tabIndex={-1}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => onQueryChange("")}
              title="Clear search [Esc]"
              aria-label="Clear search query"
              className="p-1 rounded text-ink-secondary hover:text-ink-primary hover:bg-elevated transition-colors shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Mouse-only Sort Order Button + Lock Button */}
        <div className="flex items-center h-11 rounded-lg bg-ground border border-border-subtle p-1 gap-1 shrink-0">
          <button
            type="button"
            tabIndex={-1}
            disabled={sortLocked}
            onMouseDown={(e) => e.preventDefault()}
            onClick={onCycleSort}
            title={
              sortLocked
                ? `Sort order locked (${sortMeta.label})`
                : sortMeta.tooltip
            }
            aria-label={`Sort order: ${sortMeta.label}${
              sortLocked ? " (Locked)" : ""
            }`}
            className={`flex items-center gap-1.5 h-full px-2.5 rounded-md text-xs font-medium transition-colors ${
              sortLocked
                ? "text-ink-muted cursor-not-allowed opacity-60"
                : "text-ink-primary bg-elevated hover:bg-hover"
            }`}
          >
            {renderSortIcon()}
            <span>{sortMeta.label}</span>
          </button>

          <button
            type="button"
            tabIndex={-1}
            onMouseDown={(e) => e.preventDefault()}
            onClick={onToggleSortLock}
            title={sortLocked ? "Unlock sort order" : "Lock sort order"}
            aria-label={sortLocked ? "Unlock sort order" : "Lock sort order"}
            aria-pressed={sortLocked}
            className={`flex items-center justify-center w-8 h-full rounded-md transition-colors ${
              sortLocked
                ? "bg-accent-soft text-accent border border-accent/40"
                : "text-ink-secondary hover:text-ink-primary hover:bg-hover"
            }`}
          >
            {sortLocked ? (
              <Lock className="w-3.5 h-3.5" />
            ) : (
              <Unlock className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
