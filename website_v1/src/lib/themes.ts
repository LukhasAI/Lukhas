// src/lib/themes.ts
export type Theme = "dark" | "light";
export type GlassOverlay = boolean;

const DARK_VARS: Record<string, string> = {
  "--background": "#0B0B0F",
  "--surface": "#111216",
  "--surface-alt": "rgba(18,18,24,0.6)",
  "--text-primary": "#FFFFFF",
  "--text-secondary": "#C9CDD6",
  "--border": "rgba(255,255,255,0.08)",
  "--accent": "#4F8BFF",
};

const LIGHT_VARS: Record<string, string> = {
  "--background": "#FFFFFF",
  "--surface": "#F5F7FB",
  "--surface-alt": "rgba(255,255,255,0.55)",
  "--text-primary": "#0A0A0A",
  "--text-secondary": "#4B5563",
  "--border": "rgba(10,10,10,0.08)",
  "--accent": "#4F8BFF",
};

const STORAGE_THEME_KEY = "lucas:theme";
const STORAGE_GLASS_KEY = "lucas:glass";

export function applyTheme(theme: Theme, glassOverlay: GlassOverlay) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  const vars = theme === "light" ? LIGHT_VARS : DARK_VARS;
  Object.entries(vars).forEach(([k, v]) => root.style.setProperty(k, v));
  root.classList.toggle("glass-on", !!glassOverlay);
  try {
    localStorage.setItem(STORAGE_THEME_KEY, theme);
    localStorage.setItem(STORAGE_GLASS_KEY, glassOverlay ? "1" : "0");
  } catch {}
}

export function getStoredTheme(): {
  theme: Theme | null;
  glassOverlay: GlassOverlay;
} {
  if (typeof window === "undefined")
    return { theme: null, glassOverlay: false };
  try {
    const t = (localStorage.getItem(STORAGE_THEME_KEY) as Theme | null) ?? null;
    const g = localStorage.getItem(STORAGE_GLASS_KEY) === "1";
    return { theme: t, glassOverlay: g };
  } catch {
    return { theme: null, glassOverlay: false };
  }
}

export function getSystemTheme(): Theme {
  if (typeof window === "undefined") return "dark";
  return window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: light)").matches
    ? "light"
    : "dark";
}
