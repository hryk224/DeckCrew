"use client";

import { useCallback, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  getPreviewScenario,
  getTimelineScenario,
  type PreviewScenario,
  type TimelineScenario,
} from "@/lib/previewData";

/**
 * Timeline preview state with step navigation.
 */
export interface TimelinePreview {
  kind: "timeline";
  timeline: TimelineScenario;
  stepIndex: number;
  current: PreviewScenario;
  label: string;
  totalSteps: number;
  hasPrev: boolean;
  hasNext: boolean;
  goToPrev: () => void;
  goToNext: () => void;
}

/**
 * Single-shot preview state.
 */
export interface SnapshotPreview {
  kind: "snapshot";
  scenario: PreviewScenario;
}

export type PreviewState = SnapshotPreview | TimelinePreview | null;

/**
 * Read the `preview` query parameter and return the matching preview state.
 *
 * - `?preview=build-major` → snapshot preview
 * - `?preview=timeline-house-party` → timeline preview with step nav
 * - No `preview` param → null (normal SSE mode)
 */
export function usePreview(): PreviewState {
  const params = useSearchParams();
  const name = params.get("preview");
  const [stepIndex, setStepIndex] = useState(0);
  const prevNameRef = useRef(name);

  // Reset step index when switching to a different timeline
  if (name !== prevNameRef.current) {
    prevNameRef.current = name;
    setStepIndex(0);
  }

  const goToPrev = useCallback(
    () => setStepIndex((i) => Math.max(0, i - 1)),
    [],
  );
  const goToNext = useCallback(
    (max: number) => setStepIndex((i) => Math.min(max - 1, i + 1)),
    [],
  );

  if (!name) return null;

  // Check timeline first (timeline-* prefix)
  const timeline = getTimelineScenario(name);
  if (timeline) {
    const totalSteps = timeline.steps.length;
    const safeIndex = Math.min(stepIndex, totalSteps - 1);
    const step = timeline.steps[safeIndex];
    return {
      kind: "timeline",
      timeline,
      stepIndex: safeIndex,
      current: step,
      label: step.label,
      totalSteps,
      hasPrev: safeIndex > 0,
      hasNext: safeIndex < totalSteps - 1,
      goToPrev,
      goToNext: () => goToNext(totalSteps),
    };
  }

  // Fall back to single-shot scenario
  const scenario = getPreviewScenario(name);
  if (!scenario) return null;

  return { kind: "snapshot", scenario };
}
