"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Decision, Proposal, SessionState } from "@/types/session";

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
  decision: Decision | null;
  connected: boolean;
}

export function useSessionStream(): SessionStreamState {
  const [session, setSession] = useState<SessionState | null>(null);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [decision, setDecision] = useState<Decision | null>(null);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
    }

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
      setSession(data);
      setConnected(true);
    });

    es.addEventListener("session.proposals", (e: MessageEvent) => {
      const data = JSON.parse(e.data) as { proposals: Proposal[] };
      setProposals(sortProposals(data.proposals));
    });

    es.addEventListener("session.decision", (e: MessageEvent) => {
      const data = JSON.parse(e.data) as Decision;
      setDecision(data);
    });

    es.addEventListener("session.heartbeat", () => {
      setConnected(true);
    });
  }, []);

  useEffect(() => {
    connect();
    return () => {
      esRef.current?.close();
    };
  }, [connect]);

  return { session, proposals, decision, connected };
}
