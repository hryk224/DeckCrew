"use client";

import { useSearchParams } from "next/navigation";
import {
  getPreviewScenario,
  type PreviewScenario,
} from "@/lib/previewData";

/**
 * Read the `preview` query parameter and return the matching scenario.
 *
 * - `?preview=build-major` → returns the build-major fixture
 * - No `preview` param → returns null (normal SSE mode)
 * - Unknown scenario name → returns null (falls back to normal mode)
 */
export function usePreview(): PreviewScenario | null {
  const params = useSearchParams();
  const name = params.get("preview");
  if (!name) return null;
  return getPreviewScenario(name);
}
