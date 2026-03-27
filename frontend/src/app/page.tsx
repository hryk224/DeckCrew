"use client";

import { useState } from "react";
import { useSessionStream } from "@/lib/useSessionStream";

export default function Home() {
  const { session, proposals, decision, connected } = useSessionStream();
  const [requestText, setRequestText] = useState("");
  const isRunning = session !== null && session.status === "running";

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">DeckCrew</h1>
        <span className={`connection-status ${connected ? "connected" : ""}`}>
          {connected ? "Connected" : "Disconnected"}
        </span>
      </header>

      {/* Now Playing */}
      <section className="section">
        <h2 className="section-label">
          Now Playing
          {session && (
            <span className="turn-count">Turn {session.turn_count}</span>
          )}
        </h2>
        <div className="now-playing-params">
          <div className="param">
            <span className="param-key">Mood</span>
            <span className="param-value">
              {session?.current_params.mood ?? "—"}
            </span>
          </div>
          <div className="param">
            <span className="param-key">BPM</span>
            <span className="param-value">
              {session?.current_params.bpm ?? "—"}
            </span>
          </div>
          <div className="param">
            <span className="param-key">Energy</span>
            <span className="param-value">
              {session
                ? (session.current_params.energy * 100).toFixed(0) + "%"
                : "—"}
            </span>
          </div>
          <div className="param">
            <span className="param-key">Texture</span>
            <span className="param-value">
              {session?.current_params.texture ?? "—"}
            </span>
          </div>
          <div className="param">
            <span className="param-key">Focus</span>
            <span className="param-value">
              {session?.current_params.focus ?? "—"}
            </span>
          </div>
        </div>
      </section>

      {/* DJ Proposals */}
      <section className="section">
        <h2 className="section-label">DJ Proposals</h2>
        <div className="proposals-grid">
          {(proposals.length > 0
            ? proposals
            : [
                { agent_name: "groove", summary: "Waiting for session..." },
                { agent_name: "harmony", summary: "Waiting for session..." },
                { agent_name: "crowd", summary: "Waiting for session..." },
              ]
          ).map((p) => (
            <div
              key={p.agent_name}
              className="proposal-card"
              data-agent={p.agent_name}
            >
              <div className="proposal-agent">
                {p.agent_name.charAt(0).toUpperCase() + p.agent_name.slice(1)}
              </div>
              <p className="proposal-text">{p.summary}</p>
              {"perspective" in p && (
                <p className="proposal-perspective">{p.perspective}</p>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Decision */}
      <section className="section">
        <h2 className="section-label">Decision</h2>
        <div className="decision-content">
          {decision ? (
            <>
              <p className="decision-adopted">
                Adopted: {decision.adopted}
              </p>
              <p className="decision-reason">{decision.reason}</p>
            </>
          ) : (
            <>
              <p className="decision-adopted">No decision yet</p>
              <p className="decision-reason">
                {session ? "Waiting for turn..." : "Session has not started"}
              </p>
            </>
          )}
        </div>
      </section>

      {/* Request */}
      <section className="section">
        <h2 className="section-label">Request</h2>
        <div className="request-form">
          <textarea
            className="request-input"
            placeholder="Send a request to the DJs..."
            rows={2}
            disabled={!isRunning}
            value={requestText}
            onChange={(e) => setRequestText(e.target.value)}
          />
          <button
            className="request-button"
            type="button"
            disabled={!isRunning || requestText.trim() === ""}
          >
            Send
          </button>
        </div>
      </section>
    </div>
  );
}
