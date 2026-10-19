import React from "react";
import {
  FolderOpen,
  HelpCircle,
  Minus,
  Moon,
  Pin,
  PinOff,
  Settings,
  Sun,
  X,
} from "lucide-react";
import {
  invokeCloseWindow,
  invokeMinimizeWindow,
  invokeStartDragging,
} from "../lib/tauri";

interface TitleBarProps {
  wordlistName: string;
  isCustomWordlist: boolean;
  resolvedTheme: "dark" | "light";
  alwaysOnTop: boolean;
  onToggleTheme: () => void;
  onToggleAlwaysOnTop: () => void;
  onOpenSettings: () => void;
  onOpenHelp: () => void;
  onSwitchWordlist: () => void;
}

export const TitleBar: React.FC<TitleBarProps> = ({
  wordlistName,
  isCustomWordlist,
  resolvedTheme,
  alwaysOnTop,
  onToggleTheme,
  onToggleAlwaysOnTop,
  onOpenSettings,
  onOpenHelp,
  onSwitchWordlist,
}) => {
  const handleDragStart = (e: React.MouseEvent<HTMLDivElement>) => {
    if ((e.target as HTMLElement).closest("button")) return;
    if (e.button === 0) {
      invokeStartDragging();
    }
  };

  const preventFocusSteal = (e: React.MouseEvent) => {
    e.preventDefault();
  };

  return (
    <header
      onMouseDown={handleDragStart}
      data-tauri-drag-region
      className="flex items-center justify-between h-10 px-3 bg-surface border-b border-border-subtle select-none shrink-0"
    >
      {/* Brand + Active Dictionary Trigger */}
      <div className="flex items-center gap-2 min-w-0">
        <div className="flex items-center gap-2 pointer-events-none">
          <img
            src="/logo.png"
            alt="Affixr Logo"
            className="w-5 h-5 rounded-sm object-contain"
            draggable={false}
          />
          <span className="text-sm font-semibold tracking-tight text-ink-primary">
            affixr
          </span>
        </div>

        <button
          type="button"
          tabIndex={-1}
          onMouseDown={preventFocusSteal}
          onClick={onSwitchWordlist}
          title={`Current dictionary: ${wordlistName} — Click or press F1 to switch`}
          className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] border transition-colors truncate max-w-[140px] ${
            isCustomWordlist
              ? "bg-accent-soft border-accent/40 text-accent"
              : "bg-elevated border-border-subtle text-ink-secondary hover:text-ink-primary hover:border-border-strong"
          }`}
        >
          <FolderOpen className="w-3 h-3 shrink-0" />
          <span className="truncate">{wordlistName}</span>
        </button>
      </div>

      {/* Action Controls */}
      <div className="flex items-center gap-0.5">
        <button
          type="button"
          tabIndex={-1}
          onMouseDown={preventFocusSteal}
          onClick={onToggleAlwaysOnTop}
          aria-label={
            alwaysOnTop ? "Disable always on top" : "Enable always on top"
          }
          title={
            alwaysOnTop
              ? "Always on top: ON (click to unpin)"
              : "Always on top: OFF (click to pin)"
          }
          className={`p-1.5 rounded transition-colors ${
            alwaysOnTop
              ? "text-accent bg-accent-soft"
              : "text-ink-secondary hover:text-ink-primary hover:bg-hover"
          }`}
        >
          {alwaysOnTop ? (
            <Pin className="w-3.5 h-3.5" />
          ) : (
            <PinOff className="w-3.5 h-3.5" />
          )}
        </button>

        <button
          type="button"
          tabIndex={-1}
          onMouseDown={preventFocusSteal}
          onClick={onToggleTheme}
          aria-label={
            resolvedTheme === "dark"
              ? "Switch to light mode"
              : "Switch to dark mode"
          }
          title={
            resolvedTheme === "dark"
              ? "Switch to Light Mode"
              : "Switch to Dark Mode"
          }
          className="p-1.5 rounded text-ink-secondary hover:text-ink-primary hover:bg-hover transition-colors"
        >
          {resolvedTheme === "dark" ? (
            <Sun className="w-3.5 h-3.5" />
          ) : (
            <Moon className="w-3.5 h-3.5" />
          )}
        </button>

        <button
          type="button"
          tabIndex={-1}
          onMouseDown={preventFocusSteal}
          onClick={onOpenSettings}
          aria-label="Accessibility and appearance settings"
          title="Accessibility & Settings"
          className="p-1.5 rounded text-ink-secondary hover:text-ink-primary hover:bg-hover transition-colors"
        >
          <Settings className="w-3.5 h-3.5" />
        </button>

        <button
          type="button"
          tabIndex={-1}
          onMouseDown={preventFocusSteal}
          onClick={onOpenHelp}
          aria-label="Help and keyboard shortcuts"
          title="Help & Keyboard Reference"
          className="p-1.5 rounded text-ink-secondary hover:text-ink-primary hover:bg-hover transition-colors"
        >
          <HelpCircle className="w-3.5 h-3.5" />
        </button>

        <div className="w-px h-4 bg-border-subtle mx-1" />

        <button
          type="button"
          tabIndex={-1}
          onMouseDown={preventFocusSteal}
          onClick={() => invokeMinimizeWindow()}
          aria-label="Minimize window"
          title="Minimize"
          className="p-1.5 rounded text-ink-secondary hover:text-ink-primary hover:bg-hover transition-colors"
        >
          <Minus className="w-3.5 h-3.5" />
        </button>

        <button
          type="button"
          tabIndex={-1}
          onMouseDown={preventFocusSteal}
          onClick={() => invokeCloseWindow()}
          aria-label="Close window"
          title="Close"
          className="p-1.5 rounded text-ink-secondary hover:text-status-incorrect hover:bg-status-incorrect/15 transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
};
