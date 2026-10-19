import React, { useEffect, useRef } from "react";
import { ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import {
  FontSizeScale,
  LetterSpacingMode,
  MatchItem,
  SEARCH_MODE_META,
  SearchMode,
} from "../types/affixr";
import { ResultRow } from "./ResultRow";

interface ResultsListProps {
  query: string;
  mode: SearchMode;
  matches: MatchItem[];
  typedOverlay: string;
  highlightIndex: number;
  fontSize: FontSizeScale;
  letterSpacing: LetterSpacingMode;
  onSelectWord: (word: string) => void;
  onHoverIndex: (index: number) => void;
}

export const ResultsList: React.FC<ResultsListProps> = ({
  query,
  mode,
  matches,
  typedOverlay,
  highlightIndex,
  fontSize,
  letterSpacing,
  onSelectWord,
  onHoverIndex,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const trimmedQuery = query.trim();

  // Keep highlighted row visible when navigating with Up/Down arrows
  useEffect(() => {
    if (highlightIndex < 0 || !containerRef.current) return;
    const rowEl = document.getElementById(`affixr-row-${highlightIndex}`);
    if (rowEl) {
      rowEl.scrollIntoView({ block: "nearest" });
    }
  }, [highlightIndex]);

  const renderModeIcon = () => {
    switch (mode) {
      case "prefix":
        return <ChevronRight className="w-5 h-5 text-accent" />;
      case "suffix":
        return <ChevronLeft className="w-5 h-5 text-accent" />;
      case "contains":
        return <ChevronDown className="w-5 h-5 text-accent" />;
    }
  };

  if (!trimmedQuery) {
    const meta = SEARCH_MODE_META[mode];
    return (
      <main className="flex-1 flex flex-col items-center justify-center px-6 text-center select-none">
        <div className="flex items-center justify-center w-11 h-11 rounded-xl bg-surface border border-border-subtle mb-3">
          {renderModeIcon()}
        </div>
        <p className="text-sm font-medium text-ink-primary mb-1">
          {meta.label} Search Ready
        </p>
        <p className="text-xs text-ink-secondary max-w-[250px] leading-relaxed mb-4">
          Start typing to filter words instantly, or press{" "}
          <kbd className="px-1.5 py-0.5 text-[11px] bg-surface rounded border border-border-subtle text-ink-primary">
            Tab
          </kbd>{" "}
          to cycle between Prefix, Suffix, and Contains.
        </p>
        <div className="grid grid-cols-3 gap-2 w-full max-w-[290px] text-[11px]">
          <div
            className={`flex items-center justify-center gap-1 py-1.5 px-2 rounded border ${
              mode === "prefix"
                ? "bg-accent-soft border-accent/40 text-accent font-semibold"
                : "bg-surface border-border-subtle text-ink-secondary"
            }`}
          >
            <ChevronRight className="w-3.5 h-3.5 shrink-0" />
            <span>Prefix</span>
          </div>
          <div
            className={`flex items-center justify-center gap-1 py-1.5 px-2 rounded border ${
              mode === "suffix"
                ? "bg-accent-soft border-accent/40 text-accent font-semibold"
                : "bg-surface border-border-subtle text-ink-secondary"
            }`}
          >
            <ChevronLeft className="w-3.5 h-3.5 shrink-0" />
            <span>Suffix</span>
          </div>
          <div
            className={`flex items-center justify-center gap-1 py-1.5 px-2 rounded border ${
              mode === "contains"
                ? "bg-accent-soft border-accent/40 text-accent font-semibold"
                : "bg-surface border-border-subtle text-ink-secondary"
            }`}
          >
            <ChevronDown className="w-3.5 h-3.5 shrink-0" />
            <span>Contains</span>
          </div>
        </div>
      </main>
    );
  }

  if (matches.length === 0) {
    return (
      <main className="flex-1 flex flex-col items-center justify-center px-6 text-center select-none">
        <p className="text-sm font-medium text-ink-primary mb-1">
          No matching words
        </p>
        <p className="text-xs text-ink-secondary max-w-[240px] leading-relaxed">
          No unused words match{" "}
          <span className="text-accent font-semibold">"{trimmedQuery}"</span> in{" "}
          <span className="font-semibold">{SEARCH_MODE_META[mode].label}</span>{" "}
          mode. Press{" "}
          <kbd className="px-1.5 py-0.5 text-[11px] bg-surface rounded border border-border-subtle text-ink-primary">
            Tab
          </kbd>{" "}
          to switch mode or{" "}
          <kbd className="px-1.5 py-0.5 text-[11px] bg-surface rounded border border-border-subtle text-ink-primary">
            Esc
          </kbd>{" "}
          to clear.
        </p>
      </main>
    );
  }

  return (
    <main
      ref={containerRef}
      id="affixr-results-listbox"
      role="listbox"
      aria-label="Matching dictionary words"
      className="flex-1 overflow-y-auto px-2 py-1.5 space-y-0.5"
    >
      {typedOverlay.length > 0 && (
        <div className="flex items-center justify-between px-3 py-1.5 mb-1 rounded-md bg-surface border border-border-subtle text-xs">
          <span className="text-ink-secondary">Background tracking:</span>
          <span className="font-semibold text-accent tracking-wider">
            {mode === "prefix" ? trimmedQuery.toLowerCase() : ""}
            <span className="text-ink-primary underline decoration-accent underline-offset-4">
              {typedOverlay}
            </span>
          </span>
        </div>
      )}

      {matches.map((item, idx) => (
        <ResultRow
          key={item.word}
          id={`affixr-row-${idx}`}
          item={item}
          mode={mode}
          typedOverlay={typedOverlay}
          isHighlighted={idx === highlightIndex}
          fontSize={fontSize}
          letterSpacing={letterSpacing}
          onSelect={onSelectWord}
          onMouseEnter={() => onHoverIndex(idx)}
        />
      ))}
    </main>
  );
};
