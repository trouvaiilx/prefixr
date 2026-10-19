import React, { useEffect, useState } from "react";
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type HelpTab = "about" | "usage" | "shortcuts" | "background";

export const HelpModal: React.FC<HelpModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<HelpTab>("about");

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

  const tabs: { id: HelpTab; label: string }[] = [
    { id: "about", label: "About" },
    { id: "usage", label: "How to Use" },
    { id: "shortcuts", label: "Shortcuts" },
    { id: "background", label: "Background" },
  ];

  const shortcuts = [
    { key: "Any letter", action: "Instant search in active mode" },
    { key: "Backspace", action: "Edit query and refresh results" },
    { key: "Tab", action: "Cycle search mode: Prefix → Suffix → Contains" },
    { key: "↑ / ↓", action: "Move keyboard highlight through results" },
    { key: "Enter", action: "Mark highlighted word as used & clear input" },
    { key: "Escape", action: "Clear search field (or close open dialog)" },
    { key: "F1", action: "Open file picker to load a custom .txt word list" },
  ];

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="help-modal-title"
      className="fixed inset-0 z-50 flex flex-col bg-ground/95 backdrop-blur-sm"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-surface border-b border-border-subtle shrink-0">
        <h2
          id="help-modal-title"
          className="text-sm font-semibold text-ink-primary"
        >
          Affixr Reference & Guide
        </h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close help"
          className="p-1 rounded text-ink-secondary hover:text-ink-primary hover:bg-hover transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Tab Navigation */}
      <div
        role="tablist"
        aria-label="Help sections"
        className="grid grid-cols-4 gap-1 px-3 py-2 bg-surface border-b border-border-subtle text-xs shrink-0"
      >
        {tabs.map((tab) => {
          const isSelected = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={isSelected}
              onClick={() => setActiveTab(tab.id)}
              className={`py-1.5 px-2 rounded font-medium transition-colors ${
                isSelected
                  ? "bg-accent-soft text-accent border border-accent/40"
                  : "text-ink-secondary hover:text-ink-primary hover:bg-hover border border-transparent"
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-4 text-xs leading-relaxed text-ink-secondary space-y-4">
        {activeTab === "about" && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-surface border border-border-subtle">
              <img
                src="/logo.png"
                alt="Affixr Logo"
                className="w-11 h-11 rounded-lg object-contain shrink-0"
              />
              <div>
                <h3 className="text-sm font-semibold text-ink-primary">
                  Affixr v1.0.0
                </h3>
                <p className="text-[11px] text-ink-secondary">
                  Ultra-fast desktop affix &amp; substring dictionary utility
                </p>
              </div>
            </div>

            <p>
              <strong className="text-ink-primary">Affixr</strong> (evolved from
              Prefixr) is a zero-latency, keyboard-first desktop word lookup
              utility engineered with <strong className="text-ink-primary">Rust</strong>{" "}
              and <strong className="text-ink-primary">Tauri v2</strong>.
            </p>

            <div className="space-y-2 bg-surface p-3 rounded-lg border border-border-subtle">
              <h4 className="font-semibold text-ink-primary">
                Engine Highlights
              </h4>
              <ul className="space-y-1.5 list-disc list-inside">
                <li>
                  <strong className="text-ink-primary">Prefix &amp; Suffix:</strong>{" "}
                  Sub-millisecond binary search on forward and reversed index tables.
                </li>
                <li>
                  <strong className="text-ink-primary">Contains:</strong>{" "}
                  Multi-threaded Rayon substring matching across 472,000+ words.
                </li>
                <li>
                  <strong className="text-ink-primary">Typography:</strong>{" "}
                  Set in <strong className="text-ink-primary">Cascadia Mono</strong>{" "}
                  with customizable scale, high-contrast tokens, and light/dark themes.
                </li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === "usage" && (
          <div className="space-y-3.5">
            <div className="p-3 rounded-lg bg-surface border border-border-subtle space-y-2">
              <h3 className="font-semibold text-ink-primary">
                1. Three Search Modes (Tab)
              </h3>
              <p>
                Press{" "}
                <kbd className="px-1.5 py-0.5 bg-elevated rounded border border-border-subtle text-ink-primary">
                  Tab
                </kbd>{" "}
                at any time to cycle through the three search modes:
              </p>
              <div className="space-y-1.5 pt-1">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-elevated text-ink-primary font-semibold border border-border-subtle">
                    <ChevronRight className="w-3.5 h-3.5 text-accent" />
                    Prefix
                  </span>
                  <span>Words starting with your query (e.g. "pre…")</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-elevated text-ink-primary font-semibold border border-border-subtle">
                    <ChevronLeft className="w-3.5 h-3.5 text-accent" />
                    Suffix
                  </span>
                  <span>Words ending with your query (e.g. "…ing")</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-elevated text-ink-primary font-semibold border border-border-subtle">
                    <ChevronDown className="w-3.5 h-3.5 text-accent" />
                    Contains
                  </span>
                  <span>Words containing your query anywhere</span>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-surface border border-border-subtle space-y-1.5">
              <h3 className="font-semibold text-ink-primary">
                2. Sort Order &amp; Lock (Mouse Click)
              </h3>
              <p>
                Click the sort button next to the search field to cycle between{" "}
                <strong className="text-ink-primary">Short</strong> (shortest
                first), <strong className="text-ink-primary">Random</strong>{" "}
                (default), and <strong className="text-ink-primary">Long</strong>{" "}
                (longest first). Click the padlock button to freeze your chosen
                sort order.
              </p>
            </div>

            <div className="p-3 rounded-lg bg-surface border border-border-subtle space-y-1.5">
              <h3 className="font-semibold text-ink-primary">
                3. Marking Words as Used
              </h3>
              <p>
                Use <strong className="text-ink-primary">↑ / ↓</strong> and{" "}
                <strong className="text-ink-primary">Enter</strong> (or click
                any result row) to mark a word as{" "}
                <strong className="text-ink-primary">used</strong>. Used words
                are hidden from subsequent searches until you click{" "}
                <strong className="text-ink-primary">Reset</strong> in the
                footer.
              </p>
            </div>
          </div>
        )}

        {activeTab === "shortcuts" && (
          <div className="bg-surface rounded-lg border border-border-subtle overflow-hidden">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border-subtle bg-elevated text-ink-primary">
                  <th className="py-2 px-3 font-semibold">Key / Input</th>
                  <th className="py-2 px-3 font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle">
                {shortcuts.map((s) => (
                  <tr key={s.key}>
                    <td className="py-2 px-3 whitespace-nowrap">
                      <kbd className="px-1.5 py-0.5 rounded bg-elevated border border-border-subtle text-ink-primary font-semibold">
                        {s.key}
                      </kbd>
                    </td>
                    <td className="py-2 px-3 text-ink-secondary">{s.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "background" && (
          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-surface border border-border-subtle space-y-2">
              <h3 className="font-semibold text-ink-primary">
                Out-of-Focus Word Tracking
              </h3>
              <p>
                Affixr floats on top of other windows so you can type a query,{" "}
                <strong className="text-ink-primary">Alt-Tab</strong> into
                another application (a game, editor, or browser), and type out
                a candidate word there while Affixr tracks your progress live:
              </p>
              <ul className="space-y-1.5 list-disc list-inside pt-1">
                <li>
                  <span className="text-status-correct font-semibold underline">
                    Green underlined letters
                  </span>{" "}
                  indicate characters matching the candidate at that position.
                </li>
                <li>
                  <span className="text-status-incorrect font-semibold line-through">
                    Red strikethrough letters
                  </span>{" "}
                  alert you immediately if you make a typo.
                </li>
                <li>
                  <strong className="text-ink-primary">Backspace</strong> undoes
                  the last tracked character.
                </li>
                <li>
                  <strong className="text-ink-primary">Enter</strong>{" "}
                  automatically marks the matching word as{" "}
                  <strong className="text-ink-primary">used</strong> and
                  refreshes the list for your next turn.
                </li>
              </ul>
            </div>

            <div className="p-3 rounded-lg bg-surface border border-border-subtle space-y-1">
              <h4 className="font-semibold text-ink-primary">
                Privacy &amp; Passive Design
              </h4>
              <p>
                The listener only observes <code className="text-ink-primary">a–z</code>,{" "}
                <code className="text-ink-primary">Backspace</code>, and{" "}
                <code className="text-ink-primary">Enter</code> while a search
                query is active and Affixr is unfocused. It never blocks or
                modifies your keystrokes, and can be toggled off anytime in
                Settings.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-end px-4 py-2.5 bg-surface border-t border-border-subtle text-xs shrink-0">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-1.5 rounded-md bg-accent text-accent-ink font-semibold hover:opacity-90 transition-opacity"
        >
          Close
        </button>
      </div>
    </div>
  );
};
