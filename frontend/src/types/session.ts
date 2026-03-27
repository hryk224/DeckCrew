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

export interface Decision {
  adopted: string;
  reason: string;
  applied_params: MusicParams;
}
