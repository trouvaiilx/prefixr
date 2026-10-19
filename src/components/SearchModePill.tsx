import React from "react";
import { ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import { SEARCH_MODE_META, SearchMode } from "../types/affixr";

interface SearchModePillProps {
  mode: SearchMode;
  onCycleMode: () => void;
}

export const SearchModePill: React.FC<SearchModePillProps> = ({
  mode,
  onCycleMode,
}) => {
  const meta = SEARCH_MODE_META[mode];

  const renderIcon = () => {
    switch (mode) {
      case "prefix":
        return <ChevronRight className="w-4 h-4 text-accent shrink-0" />;
      case "suffix":
        return <ChevronLeft className="w-4 h-4 text-accent shrink-0" />;
      case "contains":
        return <ChevronDown className="w-4 h-4 text-accent shrink-0" />;
    }
  };

  return (
    <button
      type="button"
      tabIndex={-1}
      onMouseDown={(e) => e.preventDefault()}
      onClick={onCycleMode}
      title={meta.description}
      aria-label={`Search mode: ${meta.label}. Press Tab or click to cycle between Prefix, Suffix, and Contains`}
      className="group flex items-center gap-1.5 h-8 px-2.5 rounded-md bg-elevated hover:bg-hover border border-border-subtle hover:border-accent/60 transition-colors shrink-0"
    >
      {renderIcon()}
      <span className="text-xs font-semibold tracking-tight text-ink-primary">
        {meta.label}
      </span>
      <kbd className="hidden sm:inline-block ml-0.5 px-1 py-0.5 text-[10px] leading-none font-medium text-ink-secondary bg-ground rounded border border-border-subtle">
        Tab
      </kbd>
    </button>
  );
};
