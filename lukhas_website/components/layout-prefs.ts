export type BarPlacement = "left-right" | "right-left" | "top-bottom" | "bottom-top";
export type BarDepth = "full" | "half";
export type WidgetId = "conversations" | "delivery" | "trading" | "terminal";
export type Prefs = {
  placement: BarPlacement;
  depth: BarDepth;
  orderLeft?: WidgetId[];
  orderRight?: WidgetId[];
  orderTop?: WidgetId[];
  orderBottom?: WidgetId[];
  metaAdaptive: boolean;
};

const DEF: Prefs = { placement: "left-right", depth: "full", metaAdaptive: true };

export function getTier(): 1|2|3|4|5 {
  if (typeof window === 'undefined') return 1; // SSR fallback
  return Number(localStorage?.getItem("lukhas:tier") || 1) as any;
}

export function loadPrefs(): Prefs {
  if (typeof window === 'undefined') return DEF; // SSR fallback
  try {
    return { ...DEF, ...(JSON.parse(localStorage?.getItem("lukhas:prefs")||"{}")) };
  } catch {
    return DEF;
  }
}

export function savePrefs(p: Prefs) {
  if (typeof window === 'undefined') return; // SSR guard
  try {
    localStorage?.setItem("lukhas:prefs", JSON.stringify(p));
  } catch {}
}

export function widgetOrderKey(side:"left"|"right"|"top"|"bottom"){
  return `lukhas:widgets:${side}`;
}
