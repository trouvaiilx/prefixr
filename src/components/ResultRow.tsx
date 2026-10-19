import React from "react";
import { Check, CornerDownLeft } from "lucide-react";
import { FONT_SIZE_STYLES } from "../hooks/useAccessibility";
import {
  FontSizeScale,
  LetterSpacingMode,
  MatchItem,
  SearchMode,
} from "../types/affixr";

interface ResultRowProps {
  id: string;
  item: MatchItem;
  mode: SearchMode;
  typedOverlay: string;
  isHighlighted: boolean;
  fontSize: FontSizeScale;
  letterSpacing: LetterSpacingMode;
  onSelect: (word: string) => void;
  onMouseEnter: () => void;
}

export const ResultRow: React.FC<ResultRowProps> = React.memo(
  ({
    id,
    item,
    mode,
    typedOverlay,
    isHighlighted,
    fontSize,
    letterSpacing,
    onSelect,
    onMouseEnter,
  }) => {
    const { word, matchStart, matchLen } = item;
    const chars = Array.from(word);
    const overlayChars = Array.from(typedOverlay.toLowerCase());
    const sizeStyles = FONT_SIZE_STYLES[fontSize];

    // In prefix mode, background typing continues after the prefix (from matchLen).
    // In suffix or contains mode, background typing starts from the beginning of the word (index 0).
    const overlayStartIdx = mode === "prefix" ? matchLen : 0;
    const overlayEndIdx = overlayStartIdx + overlayChars.length;

    const isExactOverlayMatch =
      overlayChars.length > 0 &&
      overlayEndIdx === chars.length &&
      overlayChars.every(
        (ch, idx) =>
          chars[overlayStartIdx + idx]?.toLowerCase() === ch
      );

    return (
      <div
        id={id}
        role="option"
        aria-selected={isHighlighted}
        onMouseDown={(e) => e.preventDefault()}
        onMouseEnter={onMouseEnter}
        onClick={() => onSelect(word)}
        className={`group flex items-center justify-between px-3.5 rounded-md cursor-pointer border transition-colors ${
          sizeStyles.rowClass
        } ${
          isHighlighted
            ? "bg-selected border-border-focus/50 text-ink-primary"
            : isExactOverlayMatch
              ? "bg-status-correct/10 border-status-correct/40 text-ink-primary"
              : "bg-transparent border-transparent hover:bg-hover text-ink-primary"
        }`}
      >
        <span
          className={`truncate ${
            letterSpacing === "wide" ? "tracking-wider" : "tracking-normal"
          }`}
        >
          {chars.map((ch, idx) => {
            const isQueryMatch =
              idx >= matchStart && idx < matchStart + matchLen;
            const isOverlayRange =
              overlayChars.length > 0 &&
              idx >= overlayStartIdx &&
              idx < overlayEndIdx;

            if (isOverlayRange) {
              const typedChar = overlayChars[idx - overlayStartIdx];
              const isCorrect = typedChar === ch.toLowerCase();
              return (
                <span
                  key={idx}
                  className={
                    isCorrect
                      ? "text-status-correct font-semibold underline decoration-status-correct/70 underline-offset-4"
                      : "text-status-incorrect font-semibold line-through decoration-status-incorrect/80"
                  }
                >
                  {ch}
                </span>
              );
            }

            if (isQueryMatch) {
              return (
                <span key={idx} className="text-accent font-semibold">
                  {ch}
                </span>
              );
            }

            return (
              <span key={idx} className="text-ink-primary">
                {ch}
              </span>
            );
          })}
        </span>

        <div className="flex items-center gap-2 ml-2 shrink-0">
          {isExactOverlayMatch && (
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-status-correct/20 text-status-correct">
              <Check className="w-3 h-3" />
              Match
            </span>
          )}

          <span className="text-[11px] tabular-nums text-ink-muted">
            {chars.length}
          </span>

          {isHighlighted && (
            <span
              className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium bg-elevated text-ink-secondary border border-border-subtle"
              title="Press Enter to mark word as used"
            >
              <CornerDownLeft className="w-3 h-3 text-accent" />
            </span>
          )}
        </div>
      </div>
    );
  }
);

ResultRow.displayName = "ResultRow";
