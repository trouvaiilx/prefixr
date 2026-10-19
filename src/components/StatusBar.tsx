import React from "react";
import { RotateCcw } from "lucide-react";

interface StatusBarProps {
  hasQuery: boolean;
  shownCount: number;
  totalMatches: number;
  elapsedUs: number;
  wordCount: number;
  usedCount: number;
  onResetUsed: () => void;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  hasQuery,
  shownCount,
  totalMatches,
  elapsedUs,
  wordCount,
  usedCount,
  onResetUsed,
}) => {
  const getMatchSummary = () => {
    if (!hasQuery) return "Start typing to search";
    if (totalMatches === 0) return "No matches";
    if (shownCount < totalMatches) {
      return `Top ${shownCount.toLocaleString()} of ${totalMatches.toLocaleString()}`;
    }
    return `${totalMatches.toLocaleString()} ${
      totalMatches === 1 ? "match" : "matches"
    }`;
  };

  const formatLatency = (us: number) => {
    if (us < 1000) return "<1ms";
    return `${(us / 1000).toFixed(1)}ms`;
  };

  return (
    <footer className="flex items-center justify-between h-8 px-3 bg-surface border-t border-border-subtle text-[11px] tabular-nums select-none shrink-0">
      <div
        aria-live="polite"
        aria-atomic="true"
        className="flex items-center gap-2 text-ink-secondary truncate"
      >
        <span className="font-medium text-ink-primary">
          {getMatchSummary()}
        </span>
        {hasQuery && totalMatches > 0 && (
          <span className="text-ink-muted">({formatLatency(elapsedUs)})</span>
        )}
      </div>

      <div className="flex items-center gap-2.5 shrink-0">
        {usedCount > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="text-accent font-medium">
              {usedCount.toLocaleString()} used
            </span>
            <button
              type="button"
              tabIndex={-1}
              onMouseDown={(e) => e.preventDefault()}
              onClick={onResetUsed}
              title="Reset used words so they appear in searches again"
              aria-label="Reset used words"
              className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-elevated hover:bg-hover text-ink-primary border border-border-subtle transition-colors"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          </div>
        )}

        <span className="text-ink-secondary">
          {wordCount > 0
            ? `${wordCount.toLocaleString()} words`
            : "No words loaded"}
        </span>
      </div>
    </footer>
  );
};
