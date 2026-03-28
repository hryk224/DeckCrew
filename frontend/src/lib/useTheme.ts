"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { DEFAULT_THEME, THEMES } from "@/lib/themes";

/**
 * Read the `theme` query parameter and apply it to <html> via data-theme.
 *
 * - No `theme` param or `theme=tokyo-night` → no data-theme attribute (default)
 * - `theme=cyberpunk` → data-theme="cyberpunk"
 * - `theme=velvet-lounge` → data-theme="velvet-lounge"
 * - `theme=afterhours-mist` → data-theme="afterhours-mist"
 * - `theme=warehouse` → data-theme="warehouse"
 * - Unknown value → ignored, falls back to default
 *
 * Returns the active theme id.
 */
export function useTheme(): string {
  const params = useSearchParams();
  const raw = params.get("theme");
  const themeId =
    raw && THEMES.some((t) => t.id === raw) ? raw : DEFAULT_THEME;

  useEffect(() => {
    const html = document.documentElement;
    if (themeId === DEFAULT_THEME) {
      html.removeAttribute("data-theme");
    } else {
      html.setAttribute("data-theme", themeId);
    }
    return () => {
      html.removeAttribute("data-theme");
    };
  }, [themeId]);

  return themeId;
}
