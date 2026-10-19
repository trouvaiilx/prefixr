import { useCallback, useEffect, useState } from "react";
import { invokeSetAlwaysOnTop } from "../lib/tauri";
import { AccessibilitySettings, FontSizeScale } from "../types/affixr";

const STORAGE_KEY = "affixr.settings.v1";

const DEFAULT_SETTINGS: AccessibilitySettings = {
  theme: "dark",
  fontSize: "normal",
  highContrast: false,
  reducedMotion: false,
  letterSpacing: "normal",
  alwaysOnTop: true,
  backgroundTracking: true,
  maxResults: 50,
};

export const FONT_SIZE_STYLES: Record<
  FontSizeScale,
  {
    inputClass: string;
    rowClass: string;
    rowHeightPx: number;
  }
> = {
  compact: {
    inputClass: "text-[17px]",
    rowClass: "text-[15px] py-1.5",
    rowHeightPx: 32,
  },
  normal: {
    inputClass: "text-[20px]",
    rowClass: "text-[18px] py-2",
    rowHeightPx: 38,
  },
  relaxed: {
    inputClass: "text-[22px]",
    rowClass: "text-[20px] py-2.5",
    rowHeightPx: 44,
  },
  large: {
    inputClass: "text-[25px]",
    rowClass: "text-[23px] py-3",
    rowHeightPx: 50,
  },
};

function loadInitialSettings(): AccessibilitySettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      const prefersReducedMotion =
        typeof window !== "undefined" &&
        window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
      return {
        ...DEFAULT_SETTINGS,
        reducedMotion: Boolean(prefersReducedMotion),
      };
    }
    const parsed = JSON.parse(raw);
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function useAccessibility() {
  const [settings, setSettings] =
    useState<AccessibilitySettings>(loadInitialSettings);
  const [resolvedTheme, setResolvedTheme] = useState<"dark" | "light">("dark");

  // Resolve theme ("system" -> media query) and apply DOM attributes
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const updateTheme = () => {
      const effective: "dark" | "light" =
        settings.theme === "system"
          ? mediaQuery.matches
            ? "dark"
            : "light"
          : settings.theme;

      setResolvedTheme(effective);
      document.documentElement.setAttribute("data-theme", effective);
      document.documentElement.setAttribute(
        "data-contrast",
        settings.highContrast ? "high" : "normal"
      );
      document.documentElement.setAttribute(
        "data-motion",
        settings.reducedMotion ? "reduced" : "normal"
      );
    };

    updateTheme();
    mediaQuery.addEventListener("change", updateTheme);
    return () => mediaQuery.removeEventListener("change", updateTheme);
  }, [settings.theme, settings.highContrast, settings.reducedMotion]);

  // Sync alwaysOnTop with Tauri window
  useEffect(() => {
    invokeSetAlwaysOnTop(settings.alwaysOnTop);
  }, [settings.alwaysOnTop]);

  // Persist to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch {
      // ignore storage errors
    }
  }, [settings]);

  const updateSetting = useCallback(
    <K extends keyof AccessibilitySettings>(
      key: K,
      value: AccessibilitySettings[K]
    ) => {
      setSettings((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  const toggleLightDark = useCallback(() => {
    setSettings((prev) => ({
      ...prev,
      theme: resolvedTheme === "dark" ? "light" : "dark",
    }));
  }, [resolvedTheme]);

  const resetAccessibility = useCallback(() => {
    setSettings(DEFAULT_SETTINGS);
  }, []);

  return {
    settings,
    resolvedTheme,
    updateSetting,
    toggleLightDark,
    resetAccessibility,
  };
}
