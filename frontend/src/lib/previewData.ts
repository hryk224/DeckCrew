/**
 * Fixed preview scenarios for design review.
 *
 * Each scenario provides the same state shape as the real SSE stream:
 * session, proposals, feedback, decision. This allows the preview
 * to use the exact same rendering path as the live UI.
 */

import type {
  Decision,
  FeedbackItem,
  Proposal,
  SessionState,
} from "@/types/session";

export interface PreviewScenario {
  name: string;
  session: SessionState | null;
  proposals: Proposal[];
  feedback: FeedbackItem[];
  decision: Decision | null;
}

const SCENARIOS: Record<string, PreviewScenario> = {
  idle: {
    name: "idle",
    session: null,
    proposals: [],
    feedback: [],
    decision: null,
  },

  "build-major": {
    name: "build-major",
    session: {
      session_id: "preview-001",
      status: "running",
      current_params: {
        mood: "deep",
        bpm: 124,
        energy: 0.6,
        texture: "wide",
        focus: "pad",
      },
      section: {
        current_section: "build",
        transition_intent: "intensify",
        last_major_turn: 3,
        recent_changes: [
          { turn: 2, kind: "major", summary: "groove: Pushed the kick harder" },
          {
            turn: 3,
            kind: "major",
            summary: "harmony: Widened the chord voicing",
          },
        ],
      },
      last_change: "harmony: Widened the chord voicing, added floating pads",
      last_turn_kind: "major",
      last_user_request: null,
      turn_count: 3,
    },
    proposals: [
      {
        agent_name: "groove",
        summary: "Push the kick harder, raise tempo slightly for drive",
        perspective: "rhythmic momentum",
        suggested_params: {
          mood: "deep",
          bpm: 128,
          energy: 0.7,
          texture: "wide",
          focus: "drums",
        },
      },
      {
        agent_name: "harmony",
        summary: "Widen the chord voicing, add floating pad layers",
        perspective: "harmonic depth",
        suggested_params: {
          mood: "deep",
          bpm: 124,
          energy: 0.6,
          texture: "wide",
          focus: "pad",
        },
      },
      {
        agent_name: "crowd",
        summary: "Current direction feels right, maintain the vibe",
        perspective: "audience reception",
        suggested_params: {
          mood: "deep",
          bpm: 124,
          energy: 0.6,
          texture: "wide",
          focus: "pad",
        },
      },
    ],
    feedback: [
      {
        source: "critic",
        name: "critic",
        content: {
          issue: "Flow is progressing well",
          severity: "low",
          suggestion: "No immediate changes needed",
        },
      },
      {
        source: "audience",
        name: "audience",
        content: {
          reaction: "Vibing along",
          energy_delta: 0.0,
          reason: "The mood is comfortable, no strong push either way",
        },
      },
    ],
    decision: {
      kind: "major",
      adopted: "harmony",
      reason: "Adopting harmony's proposal (score: 0.50)",
      applied_params: {
        mood: "deep",
        bpm: 124,
        energy: 0.6,
        texture: "wide",
        focus: "pad",
      },
      rejections: [
        {
          agent_name: "groove",
          summary: "Push the kick harder, raise tempo slightly",
          reason: "Score 0.42 was lower than adopted (0.50)",
        },
        {
          agent_name: "crowd",
          summary: "Current direction feels right, maintain the vibe",
          reason: "Score 0.00 was lower than adopted (0.50)",
        },
      ],
    },
  },

  "peak-with-feedback": {
    name: "peak-with-feedback",
    session: {
      session_id: "preview-002",
      status: "running",
      current_params: {
        mood: "bright",
        bpm: 138,
        energy: 0.85,
        texture: "dense",
        focus: "drums",
      },
      section: {
        current_section: "peak",
        transition_intent: "intensify",
        last_major_turn: 5,
        recent_changes: [
          {
            turn: 5,
            kind: "major",
            summary: "groove: Big tempo push to peak energy",
          },
          {
            turn: 6,
            kind: "minor",
            summary: "harmony: Subtle chord widening",
          },
        ],
      },
      last_change: "harmony: Subtle chord widening",
      last_turn_kind: "minor",
      last_user_request: null,
      turn_count: 6,
    },
    proposals: [
      {
        agent_name: "groove",
        summary: "Keep the kick driving, add syncopated hi-hats",
        perspective: "rhythmic momentum",
        suggested_params: {
          mood: "bright",
          bpm: 140,
          energy: 0.9,
          texture: "dense",
          focus: "drums",
        },
      },
      {
        agent_name: "harmony",
        summary: "Layer a bright arpeggio over the pads",
        perspective: "harmonic texture",
        suggested_params: {
          mood: "bright",
          bpm: 138,
          energy: 0.85,
          texture: "dense",
          focus: "synth",
        },
      },
      {
        agent_name: "crowd",
        summary: "Ride the peak, the energy is perfect",
        perspective: "audience reception",
        suggested_params: {
          mood: "bright",
          bpm: 138,
          energy: 0.85,
          texture: "dense",
          focus: "drums",
        },
      },
    ],
    feedback: [
      {
        source: "critic",
        name: "critic",
        content: {
          issue: "Energy has been high for several turns",
          severity: "medium",
          suggestion: "Consider easing into a release soon",
        },
      },
      {
        source: "audience",
        name: "audience",
        content: {
          reaction: "Feeling the energy!",
          energy_delta: 0.1,
          reason: "The crowd is responding well to the intensity",
        },
      },
    ],
    decision: {
      kind: "minor",
      adopted: "groove",
      reason:
        "Adopting groove's proposal (score: 0.32) — influenced by audience wanted more energy",
      applied_params: {
        mood: "bright",
        bpm: 138,
        energy: 0.85,
        texture: "dense",
        focus: "drums",
      },
      rejections: [
        {
          agent_name: "harmony",
          summary: "Layer a bright arpeggio over the pads",
          reason: "Score 0.10 was lower than adopted (0.32)",
        },
        {
          agent_name: "crowd",
          summary: "Ride the peak, the energy is perfect",
          reason: "Score -0.45 was lower than adopted (0.32)",
        },
      ],
    },
  },

  "crowd-requested-shift": {
    name: "crowd-requested-shift",
    session: {
      session_id: "preview-003",
      status: "running",
      current_params: {
        mood: "dark",
        bpm: 122,
        energy: 0.65,
        texture: "layered",
        focus: "synth",
      },
      section: {
        current_section: "build",
        transition_intent: "lift",
        last_major_turn: 4,
        recent_changes: [
          {
            turn: 3,
            kind: "major",
            summary: "harmony: Shifted to darker tonality",
          },
          {
            turn: 4,
            kind: "major",
            summary: "crowd: Audience wants darker and heavier",
          },
        ],
      },
      last_change: "crowd: Audience wants darker and heavier",
      last_turn_kind: "major",
      last_user_request: null,
      turn_count: 4,
    },
    proposals: [
      {
        agent_name: "groove",
        summary: "Push the kick harder, raise tempo for drive",
        perspective: "rhythmic momentum",
        suggested_params: {
          mood: "dark",
          bpm: 126,
          energy: 0.75,
          texture: "layered",
          focus: "drums",
        },
      },
      {
        agent_name: "harmony",
        summary: "Deepen the bass, add minor key tension",
        perspective: "harmonic depth",
        suggested_params: {
          mood: "dark",
          bpm: 122,
          energy: 0.6,
          texture: "dense",
          focus: "bass",
        },
      },
      {
        agent_name: "crowd",
        summary: "Audience wants: make it darker and heavier",
        perspective: "user request",
        suggested_params: {
          mood: "dark",
          bpm: 122,
          energy: 0.65,
          texture: "layered",
          focus: "synth",
        },
      },
    ],
    feedback: [
      {
        source: "critic",
        name: "critic",
        content: {
          issue: "Flow is progressing well",
          severity: "low",
          suggestion: "No immediate changes needed",
        },
      },
      {
        source: "audience",
        name: "audience",
        content: {
          reaction: "Losing interest...",
          energy_delta: 0.3,
          reason: "Energy is too low, the crowd needs more excitement",
        },
      },
    ],
    decision: {
      kind: "major",
      adopted: "crowd",
      reason:
        "User request present — adopting crowd's proposal to reflect audience input",
      applied_params: {
        mood: "dark",
        bpm: 122,
        energy: 0.65,
        texture: "layered",
        focus: "synth",
      },
      rejections: [
        {
          agent_name: "groove",
          summary: "Push the kick harder, raise tempo for drive",
          reason: "User request prioritized Crowd's proposal",
        },
        {
          agent_name: "harmony",
          summary: "Deepen the bass, add minor key tension",
          reason: "User request prioritized Crowd's proposal",
        },
      ],
    },
  },
};

export const SCENARIO_NAMES = Object.keys(SCENARIOS);

export function getPreviewScenario(name: string): PreviewScenario | null {
  return SCENARIOS[name] ?? null;
}
