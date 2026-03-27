export interface MusicParams {
  mood: string;
  bpm: number;
  energy: number;
  texture: string;
  focus: string;
}

// --- Section state (M3) ---

export type Section = "intro" | "build" | "peak" | "release";
export type TransitionIntent =
  | "hold"
  | "lift"
  | "intensify"
  | "cool_down"
  | "reset";
export type ChangeKind = "minor" | "major";

export interface ChangeRecord {
  turn: number;
  kind: ChangeKind;
  summary: string;
}

export interface SectionState {
  current_section: Section;
  transition_intent: TransitionIntent;
  last_major_turn: number;
  recent_changes: ChangeRecord[];
}

// --- Venue context (M5) ---

export type RoomSize = "intimate" | "club" | "festival";
export type TimeOfNight = "early" | "peak_hours" | "late";
export type EventVibe = "underground" | "mainstream" | "experimental";

export interface VenueContext {
  room_size: RoomSize;
  crowd_density: number;
  time_of_night: TimeOfNight;
  event_vibe: EventVibe;
}

// --- Session state ---

export interface SessionState {
  session_id: string;
  status: "idle" | "running" | "stopped";
  current_params: MusicParams;
  section?: SectionState;
  venue?: VenueContext | null;
  last_change: string | null;
  last_turn_kind?: ChangeKind | null;
  last_user_request: string | null;
  turn_count: number;
}

export interface Proposal {
  agent_name: string;
  summary: string;
  perspective: string;
  suggested_params: MusicParams;
}

// --- Room Feedback ---

export interface CriticFeedbackContent {
  issue: string;
  severity: "low" | "medium" | "high";
  suggestion: string;
}

export interface AudienceFeedbackContent {
  reaction: string;
  energy_delta: number;
  reason: string;
}

/**
 * Discriminated union for feedback items.
 * - `source`: "critic" or "audience" — determines the shape of `content`
 * - `name`: instance identifier (distinguishes multiple audiences in future)
 */
export type FeedbackItem =
  | {
      source: "critic";
      name: string;
      content: CriticFeedbackContent;
    }
  | {
      source: "audience";
      name: string;
      content: AudienceFeedbackContent;
    };

export interface Feedback {
  items: FeedbackItem[];
}

// --- Decision ---

export interface Rejection {
  agent_name: string;
  summary: string;
  reason: string;
}

export interface Decision {
  kind?: ChangeKind;
  adopted: string;
  reason: string;
  applied_params: MusicParams;
  rejections?: Rejection[];
}
