/**
 * Fixed preview scenarios for design review.
 *
 * Each scenario provides the same state shape as the real SSE stream:
 * session, proposals, feedback, decision. This allows the preview
 * to use the exact same rendering path as the live UI.
 *
 * Locale support: EN and JA variants are provided for each scenario.
 * Use getPreviewScenario(name, locale) / getTimelineScenario(name, locale).
 */

import type {
  Decision,
  FeedbackItem,
  Proposal,
  SessionState,
} from "@/types/session";

export type Locale = "en" | "ja";

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

/* ================================================================== */
/*  Single-shot Scenarios – EN                                        */
/* ================================================================== */

const SCENARIOS_EN: Record<string, PreviewScenario> = {
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
        name: "chiller",
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
        name: "clubber",
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
        name: "explorer",
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

/* ================================================================== */
/*  Single-shot Scenarios – JA                                        */
/* ================================================================== */

const SCENARIOS_JA: Record<string, PreviewScenario> = {
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
          { turn: 2, kind: "major", summary: "groove: キックをもっと強めにプッシュ" },
          {
            turn: 3,
            kind: "major",
            summary: "harmony: コードのボイシングを広げた",
          },
        ],
      },
      last_change: "harmony: コードのボイシングを広げて、浮遊感のあるパッドを追加",
      last_turn_kind: "major",
      last_user_request: null,
      turn_count: 3,
    },
    proposals: [
      {
        agent_name: "groove",
        summary: "キックをもっと強めに、テンポも少し上げてドライブ感出そう",
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
        summary: "コードのボイシングを広げて、浮遊感のあるパッドを重ねよう",
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
        summary: "今の方向性いい感じ、このままキープしよう",
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
          issue: "セットの流れはいい感じ",
          severity: "low",
          suggestion: "今はまだ変える必要なし",
        },
      },
      {
        source: "audience",
        name: "chiller",
        content: {
          reaction: "いい雰囲気に乗ってる",
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
          summary: "キックをもっと強めに、テンポもちょい上げ",
          reason: "Score 0.42 was lower than adopted (0.50)",
        },
        {
          agent_name: "crowd",
          summary: "今の方向性いい感じ、このままキープしよう",
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
            summary: "groove: テンポを一気に上げてピークへ",
          },
          {
            turn: 6,
            kind: "minor",
            summary: "harmony: コードをさりげなく広げた",
          },
        ],
      },
      last_change: "harmony: コードをさりげなく広げた",
      last_turn_kind: "minor",
      last_user_request: null,
      turn_count: 6,
    },
    proposals: [
      {
        agent_name: "groove",
        summary: "キックは攻めたまま、シンコペーションのハイハットを入れよう",
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
        summary: "パッドの上にキラキラしたアルペジオを重ねよう",
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
        summary: "ピークに乗れてる、このエネルギー最高",
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
          issue: "ハイエナジーが何ターンも続いてる",
          severity: "medium",
          suggestion: "そろそろリリースに向けて動いた方がいいかも",
        },
      },
      {
        source: "audience",
        name: "clubber",
        content: {
          reaction: "めっちゃアガる！",
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
          summary: "パッドの上にキラキラしたアルペジオを重ねよう",
          reason: "Score 0.10 was lower than adopted (0.32)",
        },
        {
          agent_name: "crowd",
          summary: "ピークに乗れてる、このエネルギー最高",
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
            summary: "harmony: ダークなトーンにシフト",
          },
          {
            turn: 4,
            kind: "major",
            summary: "crowd: フロアがもっとダークでヘヴィなのを求めてる",
          },
        ],
      },
      last_change: "crowd: フロアがもっとダークでヘヴィなのを求めてる",
      last_turn_kind: "major",
      last_user_request: null,
      turn_count: 4,
    },
    proposals: [
      {
        agent_name: "groove",
        summary: "キックをもっと強めに、テンポ上げてドライブかけよう",
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
        summary: "ベースをもっと深く、マイナーキーでテンション加えよう",
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
        summary: "フロアの声: もっとダークに、もっとヘヴィに",
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
          issue: "セットの流れはいい感じ",
          severity: "low",
          suggestion: "今はまだ変える必要なし",
        },
      },
      {
        source: "audience",
        name: "explorer",
        content: {
          reaction: "ちょっと飽きてきた…",
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
          summary: "キックをもっと強めに、テンポ上げてドライブかけよう",
          reason: "User request prioritized Crowd's proposal",
        },
        {
          agent_name: "harmony",
          summary: "ベースをもっと深く、マイナーキーでテンション加えよう",
          reason: "User request prioritized Crowd's proposal",
        },
      ],
    },
  },
};

/* ================================================================== */
/*  Scenario name list & getter                                       */
/* ================================================================== */

export const SCENARIO_NAMES = Object.keys(SCENARIOS_EN);

export function getPreviewScenario(
  name: string,
  locale: Locale = "en",
): PreviewScenario | null {
  const map = locale === "ja" ? SCENARIOS_JA : SCENARIOS_EN;
  return map[name] ?? null;
}

/* ================================================================== */
/*  Timeline Scenarios – EN                                           */
/* ================================================================== */

const TIMELINES_EN: Record<string, TimelineScenario> = {
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
        decision: { kind: "major", adopted: "groove", reason: "Adopting groove's breakbeat — crowd-first speaker order prioritized energy", applied_params: { mood: "energetic", bpm: 120, energy: 0.55, texture: "layered", focus: "drums" }, dialogue: { mode: "semi_free", total_messages: 8, rounds_executed: 1, early_stop: false, speaker_orders: [["crowd", "groove", "harmony"]] } },
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
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's compromise — semi_free debate resolved groove vs crowd clash", applied_params: { mood: "bright", bpm: 128, energy: 0.7, texture: "dense", focus: "synth" }, rejections: [{ agent_name: "groove", summary: "Push harder into DnB", reason: "Too aggressive a jump for mixed crowd" }, { agent_name: "crowd", summary: "Pull it back", reason: "Valid concern but audience engagement is high" }], dialogue: { mode: "semi_free", total_messages: 14, rounds_executed: 2, early_stop: false, speaker_orders: [["crowd", "groove", "harmony"], ["groove", "harmony", "crowd"]] } },
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
        decision: { kind: "minor", adopted: "harmony", reason: "Adopting harmony's vocal layer — DJs converged after semi_free debate", applied_params: { mood: "euphoric", bpm: 130, energy: 0.9, texture: "dense", focus: "vocal" }, dialogue: { mode: "semi_free", total_messages: 18, rounds_executed: 2, early_stop: true, speaker_orders: [["harmony", "groove", "crowd"], ["groove", "crowd", "harmony"]], vote_result: "adopt:harmony (3/3)" } },
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
        decision: { kind: "major", adopted: "groove", reason: "Adopting groove's half-time breakbeat — crowd spoke first in semi_free order", applied_params: { mood: "dark", bpm: 125, energy: 0.6, texture: "layered", focus: "drums" }, dialogue: { mode: "semi_free", total_messages: 22, rounds_executed: 2, early_stop: false, speaker_orders: [["crowd", "harmony", "groove"], ["crowd", "groove", "harmony"]] } },
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
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's final resolution — consensus after an eclectic journey", applied_params: { mood: "warm", bpm: 118, energy: 0.35, texture: "wide", focus: "pad" }, dialogue: { mode: "semi_free", total_messages: 26, rounds_executed: 2, early_stop: true, speaker_orders: [["harmony", "crowd", "groove"], ["harmony", "groove", "crowd"]], vote_result: "adopt:harmony (2/3)" } },
      },
    ],
  },
};

/* ================================================================== */
/*  Timeline Scenarios – JA                                           */
/* ================================================================== */

const TIMELINES_JA: Record<string, TimelineScenario> = {
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
          { agent_name: "groove", summary: "やわらかい四つ打ちキックを敷こう", perspective: "rhythmic foundation", suggested_params: { mood: "warm", bpm: 122, energy: 0.4, texture: "smooth", focus: "drums" } },
          { agent_name: "harmony", summary: "キックの上にローズのコードベッドを浮かせよう", perspective: "harmonic warmth", suggested_params: { mood: "warm", bpm: 120, energy: 0.35, texture: "smooth", focus: "pad" } },
          { agent_name: "crowd", summary: "ゆるめに行こう、みんなまだ落ち着いてる", perspective: "audience comfort", suggested_params: { mood: "warm", bpm: 120, energy: 0.35, texture: "smooth", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "オープニングのエネルギー感は良い", severity: "low", suggestion: "まだ変える必要なし" } },
          { source: "audience", name: "raver", content: { reaction: "今着いた、まずは一杯", energy_delta: 0.0, reason: "Warming up to the vibe" } },
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
          section: { current_section: "build", transition_intent: "lift", last_major_turn: 2, recent_changes: [{ turn: 2, kind: "major", summary: "groove: ドライブするベースラインを追加" }] },
          venue: { room_size: "intimate", crowd_density: 0.7, time_of_night: "late", event_vibe: "underground" },
          last_change: "groove: ドライブするベースラインを追加",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 2,
        },
        proposals: [
          { agent_name: "groove", summary: "ベースをもっと攻めて、ハイハットのシャッフルも入れよう", perspective: "rhythmic drive", suggested_params: { mood: "groovy", bpm: 126, energy: 0.65, texture: "wide", focus: "drums" } },
          { agent_name: "harmony", summary: "グルーヴの上にディスコ風スタブを重ねよう", perspective: "harmonic lift", suggested_params: { mood: "groovy", bpm: 124, energy: 0.55, texture: "wide", focus: "synth" } },
          { agent_name: "crowd", summary: "ベースでみんな動き出した、このまま上げていこう", perspective: "crowd momentum", suggested_params: { mood: "groovy", bpm: 124, energy: 0.6, texture: "wide", focus: "bass" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "いい感じにエネルギーが上がってる", severity: "low", suggestion: "この調子で続けて" } },
          { source: "audience", name: "raver", content: { reaction: "首振り始めた", energy_delta: 0.1, reason: "The bass line pulled me in" } },
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
          section: { current_section: "peak", transition_intent: "intensify", last_major_turn: 3, recent_changes: [{ turn: 2, kind: "major", summary: "groove: ドライブするベースラインを追加" }, { turn: 3, kind: "major", summary: "groove: パーカッションを重ねてピークドロップ" }] },
          venue: { room_size: "intimate", crowd_density: 0.85, time_of_night: "late", event_vibe: "underground" },
          last_change: "groove: パーカッションを重ねてピークドロップ",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 3,
        },
        proposals: [
          { agent_name: "groove", summary: "ピークに乗って、シンコペーションのクラップを追加", perspective: "rhythmic peak energy", suggested_params: { mood: "euphoric", bpm: 128, energy: 0.9, texture: "dense", focus: "drums" } },
          { agent_name: "harmony", summary: "ユーフォリアに明るいボーカルチョップを重ねよう", perspective: "harmonic peak", suggested_params: { mood: "euphoric", bpm: 128, energy: 0.88, texture: "dense", focus: "vocal" } },
          { agent_name: "crowd", summary: "今がその瞬間、このエネルギーをキープ！", perspective: "peak excitement", suggested_params: { mood: "euphoric", bpm: 128, energy: 0.9, texture: "dense", focus: "drums" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "ピークエネルギーに到達", severity: "medium", suggestion: "長居しすぎないで、リリースの準備を" } },
          { source: "audience", name: "raver", content: { reaction: "手が上がってる！", energy_delta: 0.15, reason: "Full engagement on the dance floor" } },
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
          section: { current_section: "release", transition_intent: "cool_down", last_major_turn: 4, recent_changes: [{ turn: 3, kind: "major", summary: "groove: ピークドロップ" }, { turn: 4, kind: "major", summary: "harmony: パッドとサブベースだけに引き戻した" }] },
          venue: { room_size: "intimate", crowd_density: 0.75, time_of_night: "late", event_vibe: "underground" },
          last_change: "harmony: パッドとサブベースだけに引き戻した",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 4,
        },
        proposals: [
          { agent_name: "groove", summary: "キックを柔らかく、サブに余韻を持たせよう", perspective: "rhythmic release", suggested_params: { mood: "deep", bpm: 124, energy: 0.5, texture: "smooth", focus: "bass" } },
          { agent_name: "harmony", summary: "コードにウォームなリバーブテイルを入れよう", perspective: "harmonic resolution", suggested_params: { mood: "deep", bpm: 126, energy: 0.55, texture: "wide", focus: "pad" } },
          { agent_name: "crowd", summary: "いいクールダウン、ちょっと息つこう", perspective: "audience relief", suggested_params: { mood: "deep", bpm: 126, energy: 0.6, texture: "wide", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "リリースのタイミングがいい", severity: "low", suggestion: "ピークからの良いトランジション" } },
          { source: "audience", name: "raver", content: { reaction: "息ついてる、最高だった", energy_delta: -0.1, reason: "Grateful for the cooldown" } },
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
          section: { current_section: "release", transition_intent: "hold", last_major_turn: 5, recent_changes: [{ turn: 4, kind: "major", summary: "harmony: パッドだけに引き戻した" }, { turn: 5, kind: "major", summary: "harmony: アンビエントテクスチャーで穏やかにフェード" }] },
          venue: { room_size: "intimate", crowd_density: 0.5, time_of_night: "late", event_vibe: "underground" },
          last_change: "harmony: アンビエントテクスチャーで穏やかにフェード",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 5,
        },
        proposals: [
          { agent_name: "groove", summary: "キックをフェードさせて、ハイハットの刻みだけ残そう", perspective: "rhythmic closure", suggested_params: { mood: "mellow", bpm: 120, energy: 0.2, texture: "minimal", focus: "drums" } },
          { agent_name: "harmony", summary: "最後のコードスウェルから静寂へ", perspective: "harmonic closure", suggested_params: { mood: "mellow", bpm: 122, energy: 0.25, texture: "smooth", focus: "pad" } },
          { agent_name: "crowd", summary: "完璧なエンディング、余韻を味わおう", perspective: "audience satisfaction", suggested_params: { mood: "mellow", bpm: 122, energy: 0.3, texture: "smooth", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "イントロからアウトロまできれいなアーク", severity: "low", suggestion: "よく構成されたセット" } },
          { source: "audience", name: "raver", content: { reaction: "最高のセット、この旅が好き", energy_delta: -0.05, reason: "Satisfied with the full arc" } },
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
          { agent_name: "groove", summary: "ブラシスネアのジェントルなダウンテンポビート", perspective: "rhythmic warmth", suggested_params: { mood: "ambient", bpm: 92, energy: 0.3, texture: "minimal", focus: "drums" } },
          { agent_name: "harmony", summary: "アンビエントパッドで空気感を作ろう", perspective: "harmonic atmosphere", suggested_params: { mood: "ambient", bpm: 90, energy: 0.25, texture: "minimal", focus: "pad" } },
          { agent_name: "crowd", summary: "ゆっくり始めよう、まだみんな来てるとこ", perspective: "audience awareness", suggested_params: { mood: "ambient", bpm: 90, energy: 0.25, texture: "minimal", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "良いオープニング", severity: "low", suggestion: "序盤のお客さんに合ってる" } },
          { source: "audience", name: "regular", content: { reaction: "いいBGMだね", energy_delta: 0.0, reason: "Chatting with friends, music is pleasant" } },
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
          section: { current_section: "build", transition_intent: "lift", last_major_turn: 2, recent_changes: [{ turn: 2, kind: "major", summary: "groove: ローファイヒップホップのグルーヴを投入" }] },
          venue: { room_size: "club", crowd_density: 0.5, time_of_night: "early", event_vibe: "mainstream" },
          last_change: "groove: ローファイヒップホップのグルーヴを投入",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 2,
        },
        proposals: [
          { agent_name: "groove", summary: "ウォーキングベースでグルーヴをもっと深く", perspective: "rhythmic depth", suggested_params: { mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "bass" } },
          { agent_name: "harmony", summary: "ジャジーなエレピのスタブを加えよう", perspective: "harmonic color", suggested_params: { mood: "smooth", bpm: 95, energy: 0.4, texture: "smooth", focus: "synth" } },
          { agent_name: "crowd", summary: "グルーヴが効いてる、ゆっくり上げていこう", perspective: "crowd patience", suggested_params: { mood: "smooth", bpm: 95, energy: 0.4, texture: "smooth", focus: "bass" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "流れは心地いいけど予測しやすい", severity: "low", suggestion: "そろそろ何かさりげない変化が欲しい" } },
          { source: "audience", name: "regular", content: { reaction: "首が動いてる", energy_delta: 0.05, reason: "The groove caught my attention" } },
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
          section: { current_section: "build", transition_intent: "hold", last_major_turn: 2, recent_changes: [{ turn: 2, kind: "major", summary: "groove: ウォーキングベース" }, { turn: 3, kind: "minor", summary: "harmony: ピアノスタブを少しだけ変化" }] },
          venue: { room_size: "club", crowd_density: 0.5, time_of_night: "early", event_vibe: "mainstream" },
          last_change: "harmony: ピアノスタブを少しだけ変化",
          last_turn_kind: "minor",
          last_user_request: null,
          turn_count: 3,
        },
        proposals: [
          { agent_name: "groove", summary: "今のグルーヴで続けよう、いい感じだから", perspective: "rhythmic consistency", suggested_params: { mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "bass" } },
          { agent_name: "harmony", summary: "ピアノのテーマをこのまま維持", perspective: "harmonic stability", suggested_params: { mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "synth" } },
          { agent_name: "crowd", summary: "ちょっとマンネリかも、何か新しいのが欲しい", perspective: "crowd fatigue", suggested_params: { mood: "warm", bpm: 98, energy: 0.5, texture: "wide", focus: "vocal" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "セットが単調になってきてる", severity: "medium", suggestion: "テクスチャーかテンポを変えてフロアを引き戻そう" } },
          { source: "audience", name: "regular", content: { reaction: "ちょっと退屈になってきた", energy_delta: -0.05, reason: "Nothing new has happened for a while" } },
        ],
        decision: { kind: "minor", adopted: "groove", reason: "Holding current groove — but critic flags incoming stagnation", applied_params: { mood: "smooth", bpm: 95, energy: 0.45, texture: "smooth", focus: "bass" }, rejections: [{ agent_name: "crowd", summary: "何か新しいのが欲しい", reason: "Score 0.15 — valid concern but change too abrupt" }] },
      },
      {
        name: "timeline-chill-lounge",
        label: "pivot",
        session: {
          session_id: "tl-chill-001",
          status: "running",
          current_params: { genre_group: "Chill & Downtempo", mood: "dreamy", bpm: 100, energy: 0.55, texture: "wide", focus: "synth" },
          section: { current_section: "build", transition_intent: "intensify", last_major_turn: 4, recent_changes: [{ turn: 3, kind: "minor", summary: "harmony: 少しだけ変化" }, { turn: 4, kind: "major", summary: "harmony: ドリーミーなシンセレイヤーにシフト" }] },
          venue: { room_size: "club", crowd_density: 0.55, time_of_night: "early", event_vibe: "mainstream" },
          last_change: "harmony: ドリーミーなシンセレイヤーにシフト",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 4,
        },
        proposals: [
          { agent_name: "groove", summary: "新しいバイブに合わせてシャッフルビートに切り替え", perspective: "rhythmic adaptation", suggested_params: { mood: "dreamy", bpm: 102, energy: 0.6, texture: "wide", focus: "drums" } },
          { agent_name: "harmony", summary: "シンセをさらに発展させてメロディックなフックを加えよう", perspective: "harmonic progression", suggested_params: { mood: "dreamy", bpm: 100, energy: 0.55, texture: "wide", focus: "synth" } },
          { agent_name: "crowd", summary: "お、きた！この変化で目が覚めた", perspective: "re-engagement", suggested_params: { mood: "dreamy", bpm: 100, energy: 0.55, texture: "wide", focus: "synth" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "停滞への対応がいい", severity: "low", suggestion: "テクスチャーの変化でフロアが戻ってきた" } },
          { source: "audience", name: "regular", content: { reaction: "おっ、いいね", energy_delta: 0.1, reason: "The new texture caught everyone's attention" } },
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
          section: { current_section: "release", transition_intent: "cool_down", last_major_turn: 5, recent_changes: [{ turn: 4, kind: "major", summary: "harmony: ドリーミーなシンセレイヤー" }, { turn: 5, kind: "major", summary: "crowd: ウォームなパッドへとクールダウンを誘導" }] },
          venue: { room_size: "club", crowd_density: 0.45, time_of_night: "early", event_vibe: "mainstream" },
          last_change: "crowd: ウォームなパッドへとクールダウンを誘導",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 5,
        },
        proposals: [
          { agent_name: "groove", summary: "ビートをフェードさせて、やわらかいパルスだけ残そう", perspective: "rhythmic resolution", suggested_params: { mood: "warm", bpm: 96, energy: 0.35, texture: "minimal", focus: "bass" } },
          { agent_name: "harmony", summary: "メジャーコードのベッドに解決しよう", perspective: "harmonic closure", suggested_params: { mood: "warm", bpm: 98, energy: 0.4, texture: "smooth", focus: "pad" } },
          { agent_name: "crowd", summary: "いいアークだった、ソフトに着地させよう", perspective: "audience satisfaction", suggested_params: { mood: "warm", bpm: 98, energy: 0.45, texture: "smooth", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "バランスの取れたセット", severity: "low", suggestion: "あのピボットがセットを単調さから救った" } },
          { source: "audience", name: "regular", content: { reaction: "いい旅だったね", energy_delta: -0.05, reason: "Content with the overall flow" } },
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
          { agent_name: "groove", summary: "ブレイクビートでエクレクティックなトーンを切り開こう", perspective: "rhythmic surprise", suggested_params: { mood: "energetic", bpm: 120, energy: 0.55, texture: "layered", focus: "drums" } },
          { agent_name: "harmony", summary: "シンセアルペジオでフロアを引き込もう", perspective: "harmonic intrigue", suggested_params: { mood: "energetic", bpm: 118, energy: 0.5, texture: "layered", focus: "synth" } },
          { agent_name: "crowd", summary: "ビッグステージのエネルギー、強く始めよう", perspective: "festival expectation", suggested_params: { mood: "energetic", bpm: 122, energy: 0.6, texture: "wide", focus: "drums" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "オープンフォーマットは強いオープニングが大事", severity: "low", suggestion: "早めに方向性を決めよう" } },
          { source: "audience", name: "explorer", content: { reaction: "何が来るのか楽しみ", energy_delta: 0.05, reason: "Festival crowd is ready for anything" } },
        ],
        decision: { kind: "major", adopted: "groove", reason: "Adopting groove's breakbeat — crowd-first speaker order prioritized energy", applied_params: { mood: "energetic", bpm: 120, energy: 0.55, texture: "layered", focus: "drums" }, dialogue: { mode: "semi_free", total_messages: 8, rounds_executed: 1, early_stop: false, speaker_orders: [["crowd", "groove", "harmony"]] } },
      },
      {
        name: "timeline-open-format-debate",
        label: "clash",
        session: {
          session_id: "tl-open-001",
          status: "running",
          current_params: { genre_group: "Open Format", mood: "intense", bpm: 128, energy: 0.75, texture: "dense", focus: "drums" },
          section: { current_section: "build", transition_intent: "intensify", last_major_turn: 2, recent_changes: [{ turn: 2, kind: "major", summary: "groove: ハイエナジーなドラムンベースパターンにシフト" }] },
          venue: { room_size: "festival", crowd_density: 0.8, time_of_night: "peak_hours", event_vibe: "experimental" },
          last_change: "groove: ハイエナジーなドラムンベースパターンにシフト",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 2,
        },
        proposals: [
          { agent_name: "crowd", summary: "エネルギーの上げ方が急すぎる、少し抑えて", perspective: "crowd overwhelm", suggested_params: { mood: "groovy", bpm: 122, energy: 0.6, texture: "wide", focus: "bass" } },
          { agent_name: "groove", summary: "ノッてきた、もっとDnBに振り切ろう", perspective: "rhythmic intensity", suggested_params: { mood: "intense", bpm: 132, energy: 0.85, texture: "dense", focus: "drums" } },
          { agent_name: "harmony", summary: "間を取ろう、テンポはキープしてメロディックなフックを追加", perspective: "harmonic bridge", suggested_params: { mood: "bright", bpm: 128, energy: 0.7, texture: "dense", focus: "synth" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "DJたちの方向性が割れてる", severity: "medium", suggestion: "harmonyの折衷案が両方を満足させるかも" } },
          { source: "audience", name: "explorer", content: { reaction: "ちょっと攻めてるけど、ハマってる", energy_delta: 0.1, reason: "The experimental crowd can handle it" } },
        ],
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's compromise — semi_free debate resolved groove vs crowd clash", applied_params: { mood: "bright", bpm: 128, energy: 0.7, texture: "dense", focus: "synth" }, rejections: [{ agent_name: "groove", summary: "もっとDnBに振り切ろう", reason: "Too aggressive a jump for mixed crowd" }, { agent_name: "crowd", summary: "少し抑えて", reason: "Valid concern but audience engagement is high" }], dialogue: { mode: "semi_free", total_messages: 14, rounds_executed: 2, early_stop: false, speaker_orders: [["crowd", "groove", "harmony"], ["groove", "harmony", "crowd"]] } },
      },
      {
        name: "timeline-open-format-debate",
        label: "peak",
        session: {
          session_id: "tl-open-001",
          status: "running",
          current_params: { genre_group: "Open Format", mood: "euphoric", bpm: 130, energy: 0.9, texture: "dense", focus: "synth" },
          section: { current_section: "peak", transition_intent: "intensify", last_major_turn: 3, recent_changes: [{ turn: 2, kind: "major", summary: "groove: DnBパターン" }, { turn: 3, kind: "major", summary: "harmony: シンセレイヤーでユーフォリックなピークへ" }] },
          venue: { room_size: "festival", crowd_density: 0.9, time_of_night: "peak_hours", event_vibe: "experimental" },
          last_change: "harmony: シンセレイヤーでユーフォリックなピークへ",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 3,
        },
        proposals: [
          { agent_name: "harmony", summary: "ユーフォリアをキープ、ボーカルサンプルを追加", perspective: "harmonic peak sustain", suggested_params: { mood: "euphoric", bpm: 130, energy: 0.9, texture: "dense", focus: "vocal" } },
          { agent_name: "groove", summary: "OK、折衷案が効いた、このまま乗ろう", perspective: "rhythmic agreement", suggested_params: { mood: "euphoric", bpm: 130, energy: 0.9, texture: "dense", focus: "drums" } },
          { agent_name: "crowd", summary: "フェスがピーク、今がその瞬間！", perspective: "peak crowd energy", suggested_params: { mood: "euphoric", bpm: 130, energy: 0.92, texture: "dense", focus: "synth" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "議論の後で全DJが揃った", severity: "low", suggestion: "珍しいコンセンサス、ピークを楽しもう" } },
          { source: "audience", name: "explorer", content: { reaction: "やばい、最高！", energy_delta: 0.15, reason: "The whole field is dancing" } },
        ],
        decision: { kind: "minor", adopted: "harmony", reason: "Adopting harmony's vocal layer — DJs converged after semi_free debate", applied_params: { mood: "euphoric", bpm: 130, energy: 0.9, texture: "dense", focus: "vocal" }, dialogue: { mode: "semi_free", total_messages: 18, rounds_executed: 2, early_stop: true, speaker_orders: [["harmony", "groove", "crowd"], ["groove", "crowd", "harmony"]], vote_result: "adopt:harmony (3/3)" } },
      },
      {
        name: "timeline-open-format-debate",
        label: "genre-shift",
        session: {
          session_id: "tl-open-001",
          status: "running",
          current_params: { genre_group: "Open Format", mood: "dark", bpm: 125, energy: 0.65, texture: "layered", focus: "bass" },
          section: { current_section: "release", transition_intent: "cool_down", last_major_turn: 4, recent_changes: [{ turn: 3, kind: "major", summary: "harmony: ユーフォリックなピーク" }, { turn: 4, kind: "major", summary: "crowd: ディープベースミュージックにジャンル転換" }] },
          venue: { room_size: "festival", crowd_density: 0.85, time_of_night: "peak_hours", event_vibe: "experimental" },
          last_change: "crowd: ディープベースミュージックにジャンル転換",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 4,
        },
        proposals: [
          { agent_name: "crowd", summary: "ジャンルチェンジにみんな驚いてる、攻めよう", perspective: "crowd intrigue", suggested_params: { mood: "dark", bpm: 125, energy: 0.65, texture: "layered", focus: "bass" } },
          { agent_name: "groove", summary: "ベースの下にハーフタイムのブレイクビートを敷こう", perspective: "rhythmic contrast", suggested_params: { mood: "dark", bpm: 125, energy: 0.6, texture: "layered", focus: "drums" } },
          { agent_name: "harmony", summary: "ベースの重さを支えるダークなパッドを", perspective: "harmonic darkness", suggested_params: { mood: "dark", bpm: 125, energy: 0.65, texture: "layered", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "ピーク後の大胆なジャンルスイッチ", severity: "low", suggestion: "オープンフォーマットの強み、予測不能さを維持しよう" } },
          { source: "audience", name: "explorer", content: { reaction: "おお、読めなかった", energy_delta: 0.05, reason: "The surprise factor is keeping people engaged" } },
        ],
        decision: { kind: "major", adopted: "groove", reason: "Adopting groove's half-time breakbeat — crowd spoke first in semi_free order", applied_params: { mood: "dark", bpm: 125, energy: 0.6, texture: "layered", focus: "drums" }, dialogue: { mode: "semi_free", total_messages: 22, rounds_executed: 2, early_stop: false, speaker_orders: [["crowd", "harmony", "groove"], ["crowd", "groove", "harmony"]] } },
      },
      {
        name: "timeline-open-format-debate",
        label: "resolve",
        session: {
          session_id: "tl-open-001",
          status: "running",
          current_params: { genre_group: "Open Format", mood: "warm", bpm: 120, energy: 0.45, texture: "wide", focus: "pad" },
          section: { current_section: "release", transition_intent: "hold", last_major_turn: 5, recent_changes: [{ turn: 4, kind: "major", summary: "crowd: ジャンル転換" }, { turn: 5, kind: "major", summary: "harmony: ウォームでワイドなパッドに解決" }] },
          venue: { room_size: "festival", crowd_density: 0.7, time_of_night: "peak_hours", event_vibe: "experimental" },
          last_change: "harmony: ウォームでワイドなパッドに解決",
          last_turn_kind: "major",
          last_user_request: null,
          turn_count: 5,
        },
        proposals: [
          { agent_name: "harmony", summary: "最後の解決、パッドの余韻を残そう", perspective: "harmonic finality", suggested_params: { mood: "warm", bpm: 118, energy: 0.35, texture: "wide", focus: "pad" } },
          { agent_name: "groove", summary: "最小限のビートで締め、パルスだけ", perspective: "rhythmic closure", suggested_params: { mood: "warm", bpm: 120, energy: 0.4, texture: "minimal", focus: "drums" } },
          { agent_name: "crowd", summary: "すごい旅だった、いい終わり方にしよう", perspective: "crowd gratitude", suggested_params: { mood: "warm", bpm: 120, energy: 0.45, texture: "wide", focus: "pad" } },
        ],
        feedback: [
          { source: "critic", name: "critic", content: { issue: "エクレクティックだけどまとまりのある旅", severity: "low", suggestion: "議論がセットをもっと面白くした" } },
          { source: "audience", name: "explorer", content: { reaction: "フェスのベストセット", energy_delta: -0.05, reason: "Full experience, felt every twist" } },
        ],
        decision: { kind: "major", adopted: "harmony", reason: "Adopting harmony's final resolution — consensus after an eclectic journey", applied_params: { mood: "warm", bpm: 118, energy: 0.35, texture: "wide", focus: "pad" }, dialogue: { mode: "semi_free", total_messages: 26, rounds_executed: 2, early_stop: true, speaker_orders: [["harmony", "crowd", "groove"], ["harmony", "groove", "crowd"]], vote_result: "adopt:harmony (2/3)" } },
      },
    ],
  },
};

/* ================================================================== */
/*  Timeline name list & getter                                       */
/* ================================================================== */

export const TIMELINE_NAMES = Object.keys(TIMELINES_EN);

export function getTimelineScenario(
  name: string,
  locale: Locale = "en",
): TimelineScenario | null {
  const map = locale === "ja" ? TIMELINES_JA : TIMELINES_EN;
  return map[name] ?? null;
}
