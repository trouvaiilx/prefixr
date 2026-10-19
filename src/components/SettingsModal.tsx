import React, { useEffect } from "react";
import {
  FolderOpen,
  Monitor,
  Moon,
  RotateCcw,
  Sun,
  X,
} from "lucide-react";
import {
  AccessibilitySettings,
  EngineStats,
  FontSizeScale,
  LetterSpacingMode,
  ThemePreference,
} from "../types/affixr";

interface SettingsModalProps {
  isOpen: boolean;
  settings: AccessibilitySettings;
  stats: EngineStats;
  onUpdateSetting: <K extends keyof AccessibilitySettings>(
    key: K,
    value: AccessibilitySettings[K]
  ) => void;
  onResetSettings: () => void;
  onSwitchWordlist: () => void;
  onRestoreDefaultWordlist: () => void;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  settings,
  stats,
  onUpdateSetting,
  onResetSettings,
  onSwitchWordlist,
  onRestoreDefaultWordlist,
  onClose,
}) => {
  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const themes: { id: ThemePreference; label: string; icon: React.ReactNode }[] =
    [
      { id: "dark", label: "Dark", icon: <Moon className="w-3.5 h-3.5" /> },
      { id: "light", label: "Light", icon: <Sun className="w-3.5 h-3.5" /> },
      {
        id: "system",
        label: "System",
        icon: <Monitor className="w-3.5 h-3.5" />,
      },
    ];

  const fontScales: { id: FontSizeScale; label: string }[] = [
    { id: "compact", label: "Compact" },
    { id: "normal", label: "Normal" },
    { id: "relaxed", label: "Relaxed" },
    { id: "large", label: "Large" },
  ];

  const maxResultOptions = [25, 50, 100, 200];

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-modal-title"
      className="fixed inset-0 z-50 flex flex-col bg-ground/95 backdrop-blur-sm"
    >
      {/* Modal Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-surface border-b border-border-subtle shrink-0">
        <h2
          id="settings-modal-title"
          className="text-sm font-semibold text-ink-primary"
        >
          Appearance & Accessibility
        </h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close settings"
          className="p-1 rounded text-ink-secondary hover:text-ink-primary hover:bg-hover transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Modal Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 text-xs">
        {/* Theme Selection */}
        <section className="space-y-2">
          <h3 className="font-semibold text-ink-primary">Color Theme</h3>
          <div className="grid grid-cols-3 gap-2">
            {themes.map((t) => {
              const active = settings.theme === t.id;
              return (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => onUpdateSetting("theme", t.id)}
                  aria-pressed={active}
                  className={`flex items-center justify-center gap-1.5 py-2 px-2.5 rounded-md border font-medium transition-colors ${
                    active
                      ? "bg-accent-soft border-accent text-accent"
                      : "bg-surface border-border-subtle text-ink-secondary hover:text-ink-primary hover:bg-hover"
                  }`}
                >
                  {t.icon}
                  <span>{t.label}</span>
                </button>
              );
            })}
          </div>
        </section>

        {/* Text Size Scale */}
        <section className="space-y-2">
          <h3 className="font-semibold text-ink-primary">
            Cascadia Mono Text Scale
          </h3>
          <div className="grid grid-cols-4 gap-1.5">
            {fontScales.map((s) => {
              const active = settings.fontSize === s.id;
              return (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => onUpdateSetting("fontSize", s.id)}
                  aria-pressed={active}
                  className={`py-2 px-2 rounded-md border font-medium transition-colors ${
                    active
                      ? "bg-accent-soft border-accent text-accent"
                      : "bg-surface border-border-subtle text-ink-secondary hover:text-ink-primary hover:bg-hover"
                  }`}
                >
                  {s.label}
                </button>
              );
            })}
          </div>
        </section>

        {/* Accessibility Toggles */}
        <section className="space-y-2">
          <h3 className="font-semibold text-ink-primary">
            Readability & Visual Comfort
          </h3>
          <div className="space-y-2 bg-surface p-3 rounded-lg border border-border-subtle">
            <label className="flex items-center justify-between gap-3 cursor-pointer">
              <div>
                <div className="font-medium text-ink-primary">
                  High Contrast Mode
                </div>
                <div className="text-[11px] text-ink-secondary">
                  Increases text contrast (WCAG AAA) and sharpens borders
                </div>
              </div>
              <input
                type="checkbox"
                checked={settings.highContrast}
                onChange={(e) =>
                  onUpdateSetting("highContrast", e.target.checked)
                }
                className="w-4 h-4 accent-[var(--accent-primary)] rounded cursor-pointer"
              />
            </label>

            <div className="h-px bg-border-subtle" />

            <label className="flex items-center justify-between gap-3 cursor-pointer">
              <div>
                <div className="font-medium text-ink-primary">
                  Wide Character Tracking
                </div>
                <div className="text-[11px] text-ink-secondary">
                  Expands letter spacing in results for easier letter scanning
                </div>
              </div>
              <input
                type="checkbox"
                checked={settings.letterSpacing === "wide"}
                onChange={(e) =>
                  onUpdateSetting(
                    "letterSpacing",
                    (e.target.checked ? "wide" : "normal") as LetterSpacingMode
                  )
                }
                className="w-4 h-4 accent-[var(--accent-primary)] rounded cursor-pointer"
              />
            </label>

            <div className="h-px bg-border-subtle" />

            <label className="flex items-center justify-between gap-3 cursor-pointer">
              <div>
                <div className="font-medium text-ink-primary">
                  Reduced Motion
                </div>
                <div className="text-[11px] text-ink-secondary">
                  Minimizes UI transitions and animations
                </div>
              </div>
              <input
                type="checkbox"
                checked={settings.reducedMotion}
                onChange={(e) =>
                  onUpdateSetting("reducedMotion", e.target.checked)
                }
                className="w-4 h-4 accent-[var(--accent-primary)] rounded cursor-pointer"
              />
            </label>
          </div>
        </section>

        {/* Behavior & Engine Settings */}
        <section className="space-y-2">
          <h3 className="font-semibold text-ink-primary">
            Behavior & Search Engine
          </h3>
          <div className="space-y-2 bg-surface p-3 rounded-lg border border-border-subtle">
            <label className="flex items-center justify-between gap-3 cursor-pointer">
              <div>
                <div className="font-medium text-ink-primary">
                  Always on Top
                </div>
                <div className="text-[11px] text-ink-secondary">
                  Keep Affixr floating above other desktop windows
                </div>
              </div>
              <input
                type="checkbox"
                checked={settings.alwaysOnTop}
                onChange={(e) =>
                  onUpdateSetting("alwaysOnTop", e.target.checked)
                }
                className="w-4 h-4 accent-[var(--accent-primary)] rounded cursor-pointer"
              />
            </label>

            <div className="h-px bg-border-subtle" />

            <label className="flex items-center justify-between gap-3 cursor-pointer">
              <div>
                <div className="font-medium text-ink-primary">
                  Background Typing Tracker
                </div>
                <div className="text-[11px] text-ink-secondary">
                  Highlight candidate letters green/red while typing in another
                  app
                </div>
              </div>
              <input
                type="checkbox"
                checked={settings.backgroundTracking}
                onChange={(e) =>
                  onUpdateSetting("backgroundTracking", e.target.checked)
                }
                className="w-4 h-4 accent-[var(--accent-primary)] rounded cursor-pointer"
              />
            </label>

            <div className="h-px bg-border-subtle" />

            <div className="flex items-center justify-between gap-3 pt-0.5">
              <div>
                <div className="font-medium text-ink-primary">
                  Result Limit
                </div>
                <div className="text-[11px] text-ink-secondary">
                  Maximum matches displayed per query
                </div>
              </div>
              <div className="flex items-center gap-1">
                {maxResultOptions.map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => onUpdateSetting("maxResults", n)}
                    className={`px-2 py-1 rounded border text-[11px] tabular-nums font-medium transition-colors ${
                      settings.maxResults === n
                        ? "bg-accent-soft border-accent text-accent"
                        : "bg-elevated border-border-subtle text-ink-secondary hover:text-ink-primary"
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Wordlist Management */}
        <section className="space-y-2">
          <h3 className="font-semibold text-ink-primary">Dictionary Source</h3>
          <div className="bg-surface p-3 rounded-lg border border-border-subtle space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-ink-secondary">Active file:</span>
              <span className="font-semibold text-ink-primary truncate max-w-[180px]">
                {stats.wordlistName}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-ink-secondary">Vocabulary size:</span>
              <span className="font-semibold tabular-nums text-ink-primary">
                {stats.wordCount.toLocaleString()} words
              </span>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <button
                type="button"
                onClick={onSwitchWordlist}
                className="flex-1 inline-flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-md bg-elevated hover:bg-hover text-ink-primary border border-border-subtle font-medium transition-colors"
              >
                <FolderOpen className="w-3.5 h-3.5 text-accent" />
                <span>Load Custom .txt (F1)</span>
              </button>

              {stats.isCustomWordlist && (
                <button
                  type="button"
                  onClick={onRestoreDefaultWordlist}
                  className="inline-flex items-center justify-center gap-1.5 py-1.5 px-2.5 rounded-md bg-elevated hover:bg-hover text-ink-secondary hover:text-ink-primary border border-border-subtle font-medium transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Default</span>
                </button>
              )}
            </div>
          </div>
        </section>
      </div>

      {/* Modal Footer */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-surface border-t border-border-subtle text-xs shrink-0">
        <button
          type="button"
          onClick={onResetSettings}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded text-ink-secondary hover:text-ink-primary hover:bg-hover transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Defaults</span>
        </button>

        <button
          type="button"
          onClick={onClose}
          className="px-4 py-1.5 rounded-md bg-accent text-accent-ink font-semibold hover:opacity-90 transition-opacity"
        >
          Done
        </button>
      </div>
    </div>
  );
};
