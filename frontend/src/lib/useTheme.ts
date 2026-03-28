"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { DEFAULT_THEME, THEMES } from "@/lib/themes";

/**
 * Manage theme state with data-theme attribute and URL sync.
 *
 * Returns the active theme id and a setter. The setter:
 * - Updates local state (source of truth)
 * - Applies data-theme to <html>
 * - Syncs ?theme= query parameter via replaceState (no scroll jump)
 */
export function useTheme(): [string, (themeId: string) => void] {
  const params = useSearchParams();
  const raw = params.get("theme");
  const initial =
    raw && THEMES.some((t) => t.id === raw) ? raw : DEFAULT_THEME;

  const [themeId, setThemeId] = useState(initial);

  // Apply data-theme attribute when state changes
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

  const setTheme = useCallback((id: string) => {
    if (!THEMES.some((t) => t.id === id)) return;
    setThemeId(id);
    // Sync URL without navigation (preserves scroll position)
    const url = new URL(window.location.href);
    if (id === DEFAULT_THEME) {
      url.searchParams.delete("theme");
    } else {
      url.searchParams.set("theme", id);
    }
    window.history.replaceState(null, "", url.toString());
  }, []);

  return [themeId, setTheme];
}
