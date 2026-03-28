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

export interface TimelineStep extends PreviewScenario {
  label: string;
}

export interface TimelineScenario {
  name: string;
  description: string;
  steps: TimelineStep[];
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

/* ------------------------------------------------------------------ */
/*  Timeline Scenarios – multi-turn experience previews               */
/* ------------------------------------------------------------------ */

const TIMELINES: Record<string, TimelineScenario> = {
  "timeline-house-party": {
    name: "timeline-house-party",
    description: "House Party: energy ramp → peak → release",
    steps: [
      {
        name: "timeline-house-party",
        label: "warmup",
        session: {
          session_id: "tl-house-001",
          status: "running",
          current_params: { genre_group: "House Party", mood: "warm", bpm: 120, energy: 0.35, texture: "smooth", focus: "pad" },
          section: { current_section: "intro", transition_intent: "hold", last_major_turn: 0, recent_changes: [] },
          venue: { room_size: "intimate", crowd_density: 0.6, time_of_night: "late", event_vibe: "underground" },
          last_change: null,
          last_turn_kind: null,
          last_user_request: null,
          turn_count: 1,
        },
        proposals: [
          { agent_name: "groove", summary: "Lay a soft four-on-the-floor kick", perspective: "rhythmic foundation", suggested_params: { mood: "warm", bpm: 122, energy: 0.4, texture: "smooth", focus: "drums" } },
          { agent_name: "harmony", summary: "Float a Rhodes chord bed over the kick", perspective: "harmonic warmth", suggested_params: { mood: "warm", bpm: 120, energy: 0.35, texture: "smooth", focus: "pad" } },
          { agent_name: "crowd", summary: "Keep it low-key, let people settle in", perspective: "audience comfort", suggested_params: { mood: "warm", bpm: 120, energy: 0.35, texture: "smooth", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Good opening energy", severity: "low", suggestion: "No changes needed yet" } },
          { source: "audience", name: "raver", content: { reaction: "Just arrived, getting a drink", energy_delta: 0.0, reason: "Warming up to the vibe" } },
        ],
        decision: { kind: "minor", adopted: "harmony", reason: "Adopting harmony's warm pad layer for the opening", applied_params: { mood: "warm", bpm: 120, energy: 0.35, texture: "smooth", focus: "pad" } },
      },
      {
        name: "timeline-house-party",
        label: "lift",
        session: {
          session_id: "tl-house-001",
          status: "running",
          current_params: { genre_group: "House Party", mood: "groovy", bpm: 124, energy: 0.55, texture: "wide", focus: "bass" },
          section: { current_section: "build", transition_intent: "lift", last_major_turn: 2, recent_changes: [{ turn: 2, kind: "major", summary: "groove: Added driving bass line" }] },
          venue: { room_size: "intimate", crowd_density: 0.7, time_of_night: "late", event_vibe: "underground" },
          last_change: "groove: Added driving bass line",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 2,
        },
        proposals: [
          { agent_name: "groove", summary: "Push the bass harder, add hi-hat shuffle", perspective: "rhythmic drive", suggested_params: { mood: "groovy", bpm: 126, energy: 0.65, texture: "wide", focus: "drums" } },
          { agent_name: "harmony", summary: "Layer a disco-style stab over the groove", perspective: "harmonic lift", suggested_params: { mood: "groovy", bpm: 124, energy: 0.55, texture: "wide", focus: "synth" } },
          { agent_name: "crowd", summary: "The bass got people moving, keep building", perspective: "crowd momentum", suggested_params: { mood: "groovy", bpm: 124, energy: 0.6, texture: "wide", focus: "bass" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Energy is building nicely", severity: "low", suggestion: "Continue the trajectory" } },
          { source: "audience", name: "raver", content: { reaction: "Nodding along now", energy_delta: 0.1, reason: "The bass line pulled me in" } },
        ],
        decision: { kind: "major", adopted: "groove", reason: "Adopting groove's proposal to accelerate the build", applied_params: { mood: "groovy", bpm: 126, energy: 0.65, texture: "wide", focus: "drums" } },
      },
      {
        name: "timeline-house-party",
        label: "peak",
        session: {
          session_id: "tl-house-001",
          status: "running",
          current_params: { genre_group: "House Party", mood: "euphoric", bpm: 128, energy: 0.88, texture: "dense", focus: "drums" },
          section: { current_section: "peak", transition_intent: "intensify", last_major_turn: 3, recent_changes: [{ turn: 2, kind: "major", summary: "groove: Added driving bass line" }, { turn: 3, kind: "major", summary: "groove: Full peak drop with layered percussion" }] },
          venue: { room_size: "intimate", crowd_density: 0.85, time_of_night: "late", event_vibe: "underground" },
          last_change: "groove: Full peak drop with layered percussion",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 3,
        },
        proposals: [
          { agent_name: "groove", summary: "Ride the peak, add syncopated claps", perspective: "rhythmic peak energy", suggested_params: { mood: "euphoric", bpm: 128, energy: 0.9, texture: "dense", focus: "drums" } },
          { agent_name: "harmony", summary: "Layer a bright vocal chop for euphoria", perspective: "harmonic peak", suggested_params: { mood: "euphoric", bpm: 128, energy: 0.88, texture: "dense", focus: "vocal" } },
          { agent_name: "crowd", summary: "This is the moment, hold the energy!", perspective: "peak excitement", suggested_params: { mood: "euphoric", bpm: 128, energy: 0.9, texture: "dense", focus: "drums" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Peak energy reached", severity: "medium", suggestion: "Don't stay here too long — plan the release" } },
          { source: "audience", name: "raver", content: { reaction: "Hands up!", energy_delta: 0.15, reason: "Full engagement on the dance floor" } },
        ],
        decision: { kind: "minor", adopted: "groove", reason: "Adopting groove's proposal — riding the peak moment", applied_params: { mood: "euphoric", bpm: 128, energy: 0.9, texture: "dense", focus: "drums" } },
      },
      {
        name: "timeline-house-party",
        label: "cool-down",
        session: {
          session_id: "tl-house-001",
          status: "running",
          current_params: { genre_group: "House Party", mood: "deep", bpm: 126, energy: 0.6, texture: "wide", focus: "pad" },
          section: { current_section: "release", transition_intent: "cool_down", last_major_turn: 4, recent_changes: [{ turn: 3, kind: "major", summary: "groove: Full peak drop" }, { turn: 4, kind: "major", summary: "harmony: Stripped back to pads and sub bass" }] },
          venue: { room_size: "intimate", crowd_density: 0.75, time_of_night: "late", event_vibe: "underground" },
          last_change: "harmony: Stripped back to pads and sub bass",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 4,
        },
        proposals: [
          { agent_name: "groove", summary: "Soften the kick, let the sub breathe", perspective: "rhythmic release", suggested_params: { mood: "deep", bpm: 124, energy: 0.5, texture: "smooth", focus: "bass" } },
          { agent_name: "harmony", summary: "Bring in a warm reverb tail on the chords", perspective: "harmonic resolution", suggested_params: { mood: "deep", bpm: 126, energy: 0.55, texture: "wide", focus: "pad" } },
          { agent_name: "crowd", summary: "Nice wind-down, catch our breath", perspective: "audience relief", suggested_params: { mood: "deep", bpm: 126, energy: 0.6, texture: "wide", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Release is well-timed", severity: "low", suggestion: "Good transition out of the peak" } },
          { source: "audience", name: "raver", content: { reaction: "Catching my breath, that was amazing", energy_delta: -0.1, reason: "Grateful for the cooldown" } },
        ],
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's warm release to guide the wind-down", applied_params: { mood: "deep", bpm: 126, energy: 0.55, texture: "wide", focus: "pad" } },
      },
      {
        name: "timeline-house-party",
        label: "outro",
        session: {
          session_id: "tl-house-001",
          status: "running",
          current_params: { genre_group: "House Party", mood: "mellow", bpm: 122, energy: 0.3, texture: "smooth", focus: "pad" },
          section: { current_section: "release", transition_intent: "hold", last_major_turn: 5, recent_changes: [{ turn: 4, kind: "major", summary: "harmony: Stripped back to pads" }, { turn: 5, kind: "major", summary: "harmony: Gentle fade with ambient textures" }] },
          venue: { room_size: "intimate", crowd_density: 0.5, time_of_night: "late", event_vibe: "underground" },
          last_change: "harmony: Gentle fade with ambient textures",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 5,
        },
        proposals: [
          { agent_name: "groove", summary: "Let the kick fade, just the hi-hat ticking", perspective: "rhythmic closure", suggested_params: { mood: "mellow", bpm: 120, energy: 0.2, texture: "minimal", focus: "drums" } },
          { agent_name: "harmony", summary: "Final chord swell into silence", perspective: "harmonic closure", suggested_params: { mood: "mellow", bpm: 122, energy: 0.25, texture: "smooth", focus: "pad" } },
          { agent_name: "crowd", summary: "Perfect ending, let it breathe out", perspective: "audience satisfaction", suggested_params: { mood: "mellow", bpm: 122, energy: 0.3, texture: "smooth", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Clean arc from intro to outro", severity: "low", suggestion: "Well-structured set" } },
          { source: "audience", name: "raver", content: { reaction: "Great set, love the journey", energy_delta: -0.05, reason: "Satisfied with the full arc" } },
        ],
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's final swell for a graceful close", applied_params: { mood: "mellow", bpm: 122, energy: 0.25, texture: "smooth", focus: "pad" } },
      },
    ],
  },

  "timeline-chill-lounge": {
    name: "timeline-chill-lounge",
    description: "Chill Lounge: smooth flow with critic-driven direction change",
    steps: [
      {
        name: "timeline-chill-lounge",
        label: "opening",
        session: {
          session_id: "tl-chill-001",
          status: "running",
          current_params: { genre_group: "Chill & Downtempo", mood: "ambient", bpm: 90, energy: 0.25, texture: "minimal", focus: "pad" },
          section: { current_section: "intro", transition_intent: "hold", last_major_turn: 0, recent_changes: [] },
          venue: { room_size: "club", crowd_density: 0.4, time_of_night: "early", event_vibe: "mainstream" },
          last_change: null,
          last_turn_kind: null,
          last_user_request: null,
          turn_count: 1,
        },
        proposals: [
          { agent_name: "groove", summary: "Gentle downtempo beat with brushed snare", perspective: "rhythmic warmth", suggested_params: { mood: "ambient", bpm: 92, energy: 0.3, texture: "minimal", focus: "drums" } },
          { agent_name: "harmony", summary: "Ambient pad wash to set the tone", perspective: "harmonic atmosphere", suggested_params: { mood: "ambient", bpm: 90, energy: 0.25, texture: "minimal", focus: "pad" } },
          { agent_name: "crowd", summary: "Easy start, people are still arriving", perspective: "audience awareness", suggested_params: { mood: "ambient", bpm: 90, energy: 0.25, texture: "minimal", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Appropriate opening", severity: "low", suggestion: "Good match for early crowd" } },
          { source: "audience", name: "regular", content: { reaction: "Nice background music", energy_delta: 0.0, reason: "Chatting with friends, music is pleasant" } },
        ],
        decision: { kind: "minor", adopted: "harmony", reason: "Adopting harmony's ambient pad for a gentle start", applied_params: { mood: "ambient", bpm: 90, energy: 0.25, texture: "minimal", focus: "pad" } },
      },
      {
        name: "timeline-chill-lounge",
        label: "groove-in",
        session: {
          session_id: "tl-chill-001",
          status: "running",
          current_params: { genre_group: "Chill & Downtempo", mood: "smooth", bpm: 95, energy: 0.4, texture: "smooth", focus: "bass" },
          section: { current_section: "build", transition_intent: "lift", last_major_turn: 2, recent_changes: [{ turn: 2, kind: "major", summary: "groove: Introduced a lo-fi hip-hop groove" }] },
          venue: { room_size: "club", crowd_density: 0.5, time_of_night: "early", event_vibe: "mainstream" },
          last_change: "groove: Introduced a lo-fi hip-hop groove",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 2,
        },
        proposals: [
          { agent_name: "groove", summary: "Deepen the groove with a walking bass", perspective: "rhythmic depth", suggested_params: { mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "bass" } },
          { agent_name: "harmony", summary: "Add jazzy electric piano stabs", perspective: "harmonic color", suggested_params: { mood: "smooth", bpm: 95, energy: 0.4, texture: "smooth", focus: "synth" } },
          { agent_name: "crowd", summary: "The groove is landing, keep building slowly", perspective: "crowd patience", suggested_params: { mood: "smooth", bpm: 95, energy: 0.4, texture: "smooth", focus: "bass" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Flow is pleasant but predictable", severity: "low", suggestion: "Could use a subtle shift soon" } },
          { source: "audience", name: "regular", content: { reaction: "Head-nodding", energy_delta: 0.05, reason: "The groove caught my attention" } },
        ],
        decision: { kind: "major", adopted: "groove", reason: "Adopting groove's walking bass to deepen the feel", applied_params: { mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "bass" } },
      },
      {
        name: "timeline-chill-lounge",
        label: "stagnation",
        session: {
          session_id: "tl-chill-001",
          status: "running",
          current_params: { genre_group: "Chill & Downtempo", mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "bass" },
          section: { current_section: "build", transition_intent: "hold", last_major_turn: 2, recent_changes: [{ turn: 2, kind: "major", summary: "groove: Walking bass" }, { turn: 3, kind: "minor", summary: "harmony: Slight variation on piano stabs" }] },
          venue: { room_size: "club", crowd_density: 0.5, time_of_night: "early", event_vibe: "mainstream" },
          last_change: "harmony: Slight variation on piano stabs",
          last_turn_kind: "minor",
          last_user_request: null,
          turn_count: 3,
        },
        proposals: [
          { agent_name: "groove", summary: "Continue the current groove, it's working", perspective: "rhythmic consistency", suggested_params: { mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "bass" } },
          { agent_name: "harmony", summary: "Stay with the piano theme", perspective: "harmonic stability", suggested_params: { mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "synth" } },
          { agent_name: "crowd", summary: "Feeling repetitive, wants something new", perspective: "crowd fatigue", suggested_params: { mood: "warm", bpm: 98, energy: 0.5, texture: "wide", focus: "vocal" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Set is becoming monotonous", severity: "medium", suggestion: "Introduce a textural shift or tempo change to re-engage the crowd" } },
          { source: "audience", name: "regular", content: { reaction: "Getting a bit bored", energy_delta: -0.05, reason: "Nothing new has happened for a while" } },
        ],
        decision: { kind: "minor", adopted: "groove", reason: "Holding current groove — but critic flags incoming stagnation", applied_params: { mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "bass" }, rejections: [{ agent_name: "crowd", summary: "Wants something new", reason: "Score 0.15 — valid concern but change too abrupt" }] },
      },
      {
        name: "timeline-chill-lounge",
        label: "pivot",
        session: {
          session_id: "tl-chill-001",
          status: "running",
          current_params: { genre_group: "Chill & Downtempo", mood: "dreamy", bpm: 100, energy: 0.55, texture: "wide", focus: "synth" },
          section: { current_section: "build", transition_intent: "intensify", last_major_turn: 4, recent_changes: [{ turn: 3, kind: "minor", summary: "harmony: Slight variation" }, { turn: 4, kind: "major", summary: "harmony: Shifted to dreamy synth layers" }] },
          venue: { room_size: "club", crowd_density: 0.55, time_of_night: "early", event_vibe: "mainstream" },
          last_change: "harmony: Shifted to dreamy synth layers",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 4,
        },
        proposals: [
          { agent_name: "groove", summary: "Match the new vibe with a shuffled beat", perspective: "rhythmic adaptation", suggested_params: { mood: "dreamy", bpm: 102, energy: 0.6, texture: "wide", focus: "drums" } },
          { agent_name: "harmony", summary: "Build on the synths, add a melodic hook", perspective: "harmonic progression", suggested_params: { mood: "dreamy", bpm: 100, energy: 0.55, texture: "wide", focus: "synth" } },
          { agent_name: "crowd", summary: "Now we're talking! The shift woke me up", perspective: "re-engagement", suggested_params: { mood: "dreamy", bpm: 100, energy: 0.55, texture: "wide", focus: "synth" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Good response to stagnation warning", severity: "low", suggestion: "The textural shift re-engaged the room" } },
          { source: "audience", name: "regular", content: { reaction: "Ooh, that's nice", energy_delta: 0.1, reason: "The new texture caught everyone's attention" } },
        ],
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's melodic hook — critic-driven pivot resolved stagnation", applied_params: { mood: "dreamy", bpm: 100, energy: 0.55, texture: "wide", focus: "synth" } },
      },
      {
        name: "timeline-chill-lounge",
        label: "settle",
        session: {
          session_id: "tl-chill-001",
          status: "running",
          current_params: { genre_group: "Chill & Downtempo", mood: "warm", bpm: 98, energy: 0.45, texture: "smooth", focus: "pad" },
          section: { current_section: "release", transition_intent: "cool_down", last_major_turn: 5, recent_changes: [{ turn: 4, kind: "major", summary: "harmony: Dreamy synth layers" }, { turn: 5, kind: "major", summary: "crowd: Guided wind-down to warm pads" }] },
          venue: { room_size: "club", crowd_density: 0.45, time_of_night: "early", event_vibe: "mainstream" },
          last_change: "crowd: Guided wind-down to warm pads",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 5,
        },
        proposals: [
          { agent_name: "groove", summary: "Fade the beat, leave just a gentle pulse", perspective: "rhythmic resolution", suggested_params: { mood: "warm", bpm: 96, energy: 0.35, texture: "minimal", focus: "bass" } },
          { agent_name: "harmony", summary: "Resolve to a major chord bed", perspective: "harmonic closure", suggested_params: { mood: "warm", bpm: 98, energy: 0.4, texture: "smooth", focus: "pad" } },
          { agent_name: "crowd", summary: "Lovely arc, let it land softly", perspective: "audience satisfaction", suggested_params: { mood: "warm", bpm: 98, energy: 0.45, texture: "smooth", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Well-rounded set", severity: "low", suggestion: "The pivot saved the set from monotony" } },
          { source: "audience", name: "regular", content: { reaction: "That was a nice journey", energy_delta: -0.05, reason: "Content with the overall flow" } },
        ],
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's major chord resolution for a satisfying close", applied_params: { mood: "warm", bpm: 98, energy: 0.4, texture: "smooth", focus: "pad" } },
      },
    ],
  },

  "timeline-open-format-debate": {
    name: "timeline-open-format-debate",
    description: "Open Format (semi_free): DJ debate with dynamic speaker order",
    steps: [
      {
        name: "timeline-open-format-debate",
        label: "opening",
        session: {
          session_id: "tl-open-001",
          status: "running",
          current_params: { genre_group: "Open Format", mood: "energetic", bpm: 118, energy: 0.5, texture: "layered", focus: "synth" },
          section: { current_section: "intro", transition_intent: "lift", last_major_turn: 0, recent_changes: [] },
          venue: { room_size: "festival", crowd_density: 0.7, time_of_night: "peak_hours", event_vibe: "experimental" },
          last_change: null,
          last_turn_kind: null,
          last_user_request: null,
          turn_count: 1,
        },
        proposals: [
          { agent_name: "groove", summary: "Open with a breakbeat to set the eclectic tone", perspective: "rhythmic surprise", suggested_params: { mood: "energetic", bpm: 120, energy: 0.55, texture: "layered", focus: "drums" } },
          { agent_name: "harmony", summary: "Start with a synth arpeggio to hook the crowd", perspective: "harmonic intrigue", suggested_params: { mood: "energetic", bpm: 118, energy: 0.5, texture: "layered", focus: "synth" } },
          { agent_name: "crowd", summary: "Big stage energy — open strong", perspective: "festival expectation", suggested_params: { mood: "energetic", bpm: 122, energy: 0.6, texture: "wide", focus: "drums" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Open format needs a strong opening statement", severity: "low", suggestion: "Commit to a direction early" } },
          { source: "audience", name: "explorer", content: { reaction: "Curious what's coming", energy_delta: 0.05, reason: "Festival crowd is ready for anything" } },
        ],
        decision: { kind: "major", adopted: "groove", reason: "Adopting groove's breakbeat — crowd-first speaker order prioritized energy", applied_params: { mood: "energetic", bpm: 120, energy: 0.55, texture: "layered", focus: "drums" } },
      },
      {
        name: "timeline-open-format-debate",
        label: "clash",
        session: {
          session_id: "tl-open-001",
          status: "running",
          current_params: { genre_group: "Open Format", mood: "intense", bpm: 128, energy: 0.75, texture: "dense", focus: "drums" },
          section: { current_section: "build", transition_intent: "intensify", last_major_turn: 2, recent_changes: [{ turn: 2, kind: "major", summary: "groove: Shifted to high-energy drum & bass pattern" }] },
          venue: { room_size: "festival", crowd_density: 0.8, time_of_night: "peak_hours", event_vibe: "experimental" },
          last_change: "groove: Shifted to high-energy drum & bass pattern",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 2,
        },
        proposals: [
          { agent_name: "crowd", summary: "The energy jump is too aggressive — pull it back", perspective: "crowd overwhelm", suggested_params: { mood: "groovy", bpm: 122, energy: 0.6, texture: "wide", focus: "bass" } },
          { agent_name: "groove", summary: "We're on fire, push harder into DnB territory", perspective: "rhythmic intensity", suggested_params: { mood: "intense", bpm: 132, energy: 0.85, texture: "dense", focus: "drums" } },
          { agent_name: "harmony", summary: "Split the difference — keep tempo but add melodic hooks", perspective: "harmonic bridge", suggested_params: { mood: "bright", bpm: 128, energy: 0.7, texture: "dense", focus: "synth" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "DJs disagree on direction", severity: "medium", suggestion: "Harmony's compromise could satisfy both camps" } },
          { source: "audience", name: "explorer", content: { reaction: "Bit intense but I'm into it", energy_delta: 0.1, reason: "The experimental crowd can handle it" } },
        ],
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's compromise — semi_free debate resolved groove vs crowd clash", applied_params: { mood: "bright", bpm: 128, energy: 0.7, texture: "dense", focus: "synth" }, rejections: [{ agent_name: "groove", summary: "Push harder into DnB", reason: "Too aggressive a jump for mixed crowd" }, { agent_name: "crowd", summary: "Pull it back", reason: "Valid concern but audience engagement is high" }] },
      },
      {
        name: "timeline-open-format-debate",
        label: "peak",
        session: {
          session_id: "tl-open-001",
          status: "running",
          current_params: { genre_group: "Open Format", mood: "euphoric", bpm: 130, energy: 0.9, texture: "dense", focus: "synth" },
          section: { current_section: "peak", transition_intent: "intensify", last_major_turn: 3, recent_changes: [{ turn: 2, kind: "major", summary: "groove: DnB pattern" }, { turn: 3, kind: "major", summary: "harmony: Built to euphoric peak with synth layers" }] },
          venue: { room_size: "festival", crowd_density: 0.9, time_of_night: "peak_hours", event_vibe: "experimental" },
          last_change: "harmony: Built to euphoric peak with synth layers",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 3,
        },
        proposals: [
          { agent_name: "harmony", summary: "Hold the euphoria, add a vocal sample", perspective: "harmonic peak sustain", suggested_params: { mood: "euphoric", bpm: 130, energy: 0.9, texture: "dense", focus: "vocal" } },
          { agent_name: "groove", summary: "OK, the compromise worked — ride it", perspective: "rhythmic agreement", suggested_params: { mood: "euphoric", bpm: 130, energy: 0.9, texture: "dense", focus: "drums" } },
          { agent_name: "crowd", summary: "Festival is peaking, this is the moment!", perspective: "peak crowd energy", suggested_params: { mood: "euphoric", bpm: 130, energy: 0.92, texture: "dense", focus: "synth" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "All DJs aligned after the debate", severity: "low", suggestion: "Rare consensus — enjoy the peak" } },
          { source: "audience", name: "explorer", content: { reaction: "This is incredible!", energy_delta: 0.15, reason: "The whole field is dancing" } },
        ],
        decision: { kind: "minor", adopted: "harmony", reason: "Adopting harmony's vocal layer — DJs converged after semi_free debate", applied_params: { mood: "euphoric", bpm: 130, energy: 0.9, texture: "dense", focus: "vocal" } },
      },
      {
        name: "timeline-open-format-debate",
        label: "genre-shift",
        session: {
          session_id: "tl-open-001",
          status: "running",
          current_params: { genre_group: "Open Format", mood: "dark", bpm: 125, energy: 0.65, texture: "layered", focus: "bass" },
          section: { current_section: "release", transition_intent: "cool_down", last_major_turn: 4, recent_changes: [{ turn: 3, kind: "major", summary: "harmony: Euphoric peak" }, { turn: 4, kind: "major", summary: "crowd: Genre pivot to deep bass music" }] },
          venue: { room_size: "festival", crowd_density: 0.85, time_of_night: "peak_hours", event_vibe: "experimental" },
          last_change: "crowd: Genre pivot to deep bass music",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 4,
        },
        proposals: [
          { agent_name: "crowd", summary: "The genre shift surprised people — lean into it", perspective: "crowd intrigue", suggested_params: { mood: "dark", bpm: 125, energy: 0.65, texture: "layered", focus: "bass" } },
          { agent_name: "groove", summary: "Add a half-time breakbeat under the bass", perspective: "rhythmic contrast", suggested_params: { mood: "dark", bpm: 125, energy: 0.6, texture: "layered", focus: "drums" } },
          { agent_name: "harmony", summary: "Dark pads to support the bass weight", perspective: "harmonic darkness", suggested_params: { mood: "dark", bpm: 125, energy: 0.65, texture: "layered", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Bold genre switch after peak", severity: "low", suggestion: "Open format strength — keep the unpredictability" } },
          { source: "audience", name: "explorer", content: { reaction: "Whoa, didn't see that coming", energy_delta: 0.05, reason: "The surprise factor is keeping people engaged" } },
        ],
        decision: { kind: "major", adopted: "groove", reason: "Adopting groove's half-time breakbeat — crowd spoke first in semi_free order", applied_params: { mood: "dark", bpm: 125, energy: 0.6, texture: "layered", focus: "drums" } },
      },
      {
        name: "timeline-open-format-debate",
        label: "resolve",
        session: {
          session_id: "tl-open-001",
          status: "running",
          current_params: { genre_group: "Open Format", mood: "warm", bpm: 120, energy: 0.45, texture: "wide", focus: "pad" },
          section: { current_section: "release", transition_intent: "hold", last_major_turn: 5, recent_changes: [{ turn: 4, kind: "major", summary: "crowd: Genre pivot" }, { turn: 5, kind: "major", summary: "harmony: Resolved to warm, wide pads" }] },
          venue: { room_size: "festival", crowd_density: 0.7, time_of_night: "peak_hours", event_vibe: "experimental" },
          last_change: "harmony: Resolved to warm, wide pads",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 5,
        },
        proposals: [
          { agent_name: "harmony", summary: "Final resolution — let the pads ring out", perspective: "harmonic finality", suggested_params: { mood: "warm", bpm: 118, energy: 0.35, texture: "wide", focus: "pad" } },
          { agent_name: "groove", summary: "Minimal beat to close, just a pulse", perspective: "rhythmic closure", suggested_params: { mood: "warm", bpm: 120, energy: 0.4, texture: "minimal", focus: "drums" } },
          { agent_name: "crowd", summary: "What a ride — end on a high note", perspective: "crowd gratitude", suggested_params: { mood: "warm", bpm: 120, energy: 0.45, texture: "wide", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "Eclectic but coherent journey", severity: "low", suggestion: "The debates made the set more interesting" } },
          { source: "audience", name: "explorer", content: { reaction: "Best set of the festival", energy_delta: -0.05, reason: "Full experience, felt every twist" } },
        ],
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's final resolution — consensus after an eclectic journey", applied_params: { mood: "warm", bpm: 118, energy: 0.35, texture: "wide", focus: "pad" } },
      },
    ],
  },
};

export const TIMELINE_NAMES = Object.keys(TIMELINES);

export function getTimelineScenario(name: string): TimelineScenario | null {
  return TIMELINES[name] ?? null;
}
