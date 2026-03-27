export interface MusicParams {
  mood: string;
  bpm: number;
  energy: number;
  texture: string;
  focus: string;
}

export interface SessionState {
  session_id: string;
  status: "idle" | "running" | "stopped";
  current_params: MusicParams;
  last_change: string | null;
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
  adopted: string;
  reason: string;
  applied_params: MusicParams;
  rejections?: Rejection[];
}
