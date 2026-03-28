"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type {
  Decision,
  Feedback,
  FeedbackItem,
  Proposal,
  SessionState,
} from "@/types/session";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const AGENT_ORDER = ["groove", "harmony", "crowd"] as const;

function sortProposals(proposals: Proposal[]): Proposal[] {
  return [...proposals].sort(
    (a, b) =>
      AGENT_ORDER.indexOf(a.agent_name as (typeof AGENT_ORDER)[number]) -
      AGENT_ORDER.indexOf(b.agent_name as (typeof AGENT_ORDER)[number]),
  );
}

export interface SessionStreamState {
  session: SessionState | null;
  proposals: Proposal[];
  feedback: FeedbackItem[];
  decision: Decision | null;
  connected: boolean;
  reset: () => void;
}

interface UseSessionStreamOptions {
  /** Set to false to skip SSE connection (e.g. in preview mode). */
  enabled?: boolean;
}

export function useSessionStream(
  options: UseSessionStreamOptions = {},
): SessionStreamState {
  const { enabled = true } = options;

  const [session, setSession] = useState<SessionState | null>(null);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [decision, setDecision] = useState<Decision | null>(null);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!enabled) return;

    const es = new EventSource(`${API_URL}/session/stream`);
    esRef.current = es;

    es.onopen = () => {
      setConnected(true);
    };

    es.onerror = () => {
      setConnected(false);
    };

    es.addEventListener("session.state", (e: MessageEvent) => {
      const data = JSON.parse(e.data) as SessionState;
      if (data.status === "stopped") {
        // Clear UI on stop — treat as no active session
        setSession(null);
        setProposals([]);
        setFeedback([]);
        setDecision(null);
      } else {
        setSession(data);
      }
      setConnected(true);
    });

    es.addEventListener("session.proposals", (e: MessageEvent) => {
      const data = JSON.parse(e.data) as { proposals: Proposal[] };
      setProposals(sortProposals(data.proposals));
    });

    es.addEventListener("session.feedback", (e: MessageEvent) => {
      const data = JSON.parse(e.data) as Feedback;
      setFeedback(data.items);
    });

    es.addEventListener("session.decision", (e: MessageEvent) => {
      const data = JSON.parse(e.data) as Decision;
      setDecision(data);
    });

    es.addEventListener("session.heartbeat", () => {
      setConnected(true);
    });

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [enabled]);

  const reset = useCallback(() => {
    setSession(null);
    setProposals([]);
    setFeedback([]);
    setDecision(null);
  }, []);

  return { session, proposals, feedback, decision, connected, reset };
}
