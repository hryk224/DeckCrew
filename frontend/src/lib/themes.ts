/**
 * Theme definitions for design comparison.
 *
 * CSS variable overrides live in globals.css under [data-theme="..."].
 * This file only defines theme names and display labels.
 */

export interface ThemeDef {
  id: string;
  label: string;
}

export const THEMES: ThemeDef[] = [
  { id: "tokyo-night", label: "Tokyo Night" },
  { id: "cyberpunk", label: "Cyberpunk" },
  { id: "velvet-lounge", label: "Velvet Lounge" },
  { id: "afterhours-mist", label: "Afterhours Mist" },
  { id: "warehouse", label: "Warehouse" },
];

export const DEFAULT_THEME = "tokyo-night";
