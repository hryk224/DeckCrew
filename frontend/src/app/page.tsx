"use client";

import { Suspense, useState } from "react";
import { startSession, submitRequest, runTurn } from "@/lib/api";
import { SCENARIO_NAMES } from "@/lib/previewData";
import { THEMES } from "@/lib/themes";
import { usePreview } from "@/lib/usePreview";
import { useSessionStream } from "@/lib/useSessionStream";
import { useTheme } from "@/lib/useTheme";
import type {
  AudienceFeedbackContent,
  CriticFeedbackContent,
  FeedbackItem,
} from "@/types/session";

type LoadingState = null | "starting" | "sending" | "turning";

const SECTION_SYMBOLS: Record<string, string> = {
  intro: "◇",
  build: "△",
  peak: "◆",
  release: "▽",
};


function extractCritic(
  items: FeedbackItem[],
): (FeedbackItem & { source: "critic" }) | null {
  const found = items.find((i) => i.source === "critic");
  return found ? (found as FeedbackItem & { source: "critic" }) : null;
}

function extractAudiences(
  items: FeedbackItem[],
): (FeedbackItem & { source: "audience" })[] {
  return items.filter(
    (i): i is FeedbackItem & { source: "audience" } => i.source === "audience",
  );
}

function severityClass(severity: string): string {
  if (severity === "high") return "severity-badge severity-high";
  if (severity === "medium") return "severity-badge severity-medium";
  return "severity-badge severity-low";
}

function energyLabel(delta: number): string {
  if (delta > 0.2) return "Wants much more energy";
  if (delta > 0) return "Wants more energy";
  if (delta < -0.2) return "Wants much less energy";
  if (delta < 0) return "Wants less energy";
  return "Satisfied";
}

export default function Home() {
  return (
    <Suspense>
      <HomeContent />
    </Suspense>
  );
}

function HomeContent() {
  const preview = usePreview();
  const currentTheme = useTheme();
  const stream = useSessionStream({ enabled: !preview });

  // In preview mode, use fixture data; otherwise use SSE stream
  const session = preview ? preview.session : stream.session;
  const proposals = preview ? preview.proposals : stream.proposals;
  const feedback = preview ? preview.feedback : stream.feedback;
  const decision = preview ? preview.decision : stream.decision;
  const connected = preview ? true : stream.connected;
  const reset = stream.reset;

  const [requestText, setRequestText] = useState("");
  const [loading, setLoading] = useState<LoadingState>(null);
  const [error, setError] = useState<string | null>(null);

  const isRunning = session !== null && session.status === "running";
  const isBusy = loading !== null;

  const critic = extractCritic(feedback);
  const audiences = extractAudiences(feedback);

  async function handleStartSession() {
    setLoading("starting");
    setError(null);
    try {
      reset();
      await startSession();
    } catch (e) {
      setError(
        `Failed to start session: ${e instanceof Error ? e.message : String(e)}`,
      );
    } finally {
      setLoading(null);
    }
  }

  async function handleRunTurn() {
    setLoading("turning");
    setError(null);
    try {
      await runTurn();
    } catch (e) {
      setError(
        `Failed to run turn: ${e instanceof Error ? e.message : String(e)}`,
      );
    } finally {
      setLoading(null);
    }
  }

  async function handleSendRequest() {
    const text = requestText.trim();
    if (!text) return;

    setLoading("sending");
    setError(null);
    try {
      await submitRequest(text);
      setRequestText("");
    } catch (e) {
      setError(
        `Failed to send request: ${e instanceof Error ? e.message : String(e)}`,
      );
      setLoading(null);
      return;
    }

    setLoading("turning");
    try {
      await runTurn();
    } catch (e) {
      setError(
        `Request sent, but turn failed: ${e instanceof Error ? e.message : String(e)}`,
      );
    } finally {
      setLoading(null);
    }
  }

  const loadingLabel =
    loading === "starting"
      ? "Starting..."
      : loading === "sending"
        ? "Sending..."
        : loading === "turning"
          ? "Running turn..."
          : null;

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="app-title-row">
          <span className={`record-dot ${isRunning ? "spinning" : ""}`} />
          <h1 className="app-title">DeckCrew</h1>
          <span className={`record-dot ${isRunning ? "spinning" : ""}`} />
        </div>

        {preview ? (
          <div className="preview-banner">
            <span className="preview-label">Preview</span>
            <span className="preview-scenario">{preview.name}</span>
            <div className="preview-nav">
              {SCENARIO_NAMES.map((s) => (
                <a
                  key={s}
                  href={`?preview=${s}${currentTheme !== "tokyo-night" ? `&theme=${currentTheme}` : ""}`}
                  className={`preview-link ${s === preview.name ? "active" : ""}`}
                >
                  {s}
                </a>
              ))}
            </div>
            <div className="preview-nav">
              {THEMES.map((t) => (
                <a
                  key={t.id}
                  href={`?preview=${preview.name}${t.id !== "tokyo-night" ? `&theme=${t.id}` : ""}`}
                  className={`preview-link ${t.id === currentTheme ? "active" : ""}`}
                >
                  {t.label}
                </a>
              ))}
            </div>
          </div>
        ) : (
          <div className="header-controls">
            <span
              className={`connection-status ${connected ? "connected" : ""}`}
            >
              {connected ? "Connected" : "Disconnected"}
            </span>
            {!isRunning ? (
              <button
                className="header-button"
                type="button"
                disabled={!connected || isBusy}
                onClick={handleStartSession}
              >
                {loading === "starting" ? "Starting..." : "Start Session"}
              </button>
            ) : (
              <button
                className="header-button"
                type="button"
                disabled={isBusy}
                onClick={handleRunTurn}
            >
              {loading === "turning" && !requestText
                ? "Running..."
                : "Run Turn"}
            </button>
            )}
          </div>
        )}
        {error && <p className="error-message">{error}</p>}
        {loadingLabel && !error && (
          <p className="loading-message">{loadingLabel}</p>
        )}
      </header>

      {/* Now Playing */}
      <section className="section">
        <h2 className="section-label">
          Now Playing
          {session && (
            <span className="turn-count">Turn {session.turn_count}</span>
          )}
          {isRunning && (
            <span className="equalizer">
              <span className="eq-bar" />
              <span className="eq-bar" />
              <span className="eq-bar" />
              <span className="eq-bar" />
              <span className="eq-bar" />
            </span>
          )}
        </h2>

        {session?.section && (
          <div className="section-bar">
            <span
              className="section-badge"
              data-section={session.section.current_section}
            >
              {SECTION_SYMBOLS[session.section.current_section] ?? ""}{" "}
              {session.section.current_section.toUpperCase()}
            </span>
            <span className="section-intent">
              → {session.section.transition_intent.replace("_", " ")}
            </span>
            {isRunning && (
              <span className="live-indicator">
                <span className="live-dot" />
                Live
              </span>
            )}
          </div>
        )}

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

      {/* Room Feedback */}
      <section className="section">
        <h2 className="section-label">Room Feedback</h2>
        {feedback.length === 0 ? (
          <p className="feedback-placeholder">
            {session ? "Waiting for feedback..." : "Waiting for session..."}
          </p>
        ) : (
          <div className="feedback-grid">
            {/* Critic */}
            <div className="feedback-card" data-source="critic">
              <div className="feedback-header">
                <span className="feedback-source-label">Critic</span>
                {critic && (
                  <span
                    className={severityClass(
                      (critic.content as CriticFeedbackContent).severity,
                    )}
                  >
                    {(critic.content as CriticFeedbackContent).severity}
                  </span>
                )}
              </div>
              {critic ? (
                <>
                  <p className="feedback-main">
                    {(critic.content as CriticFeedbackContent).issue}
                  </p>
                  <p className="feedback-detail">
                    {(critic.content as CriticFeedbackContent).suggestion}
                  </p>
                </>
              ) : (
                <p className="feedback-main">No critique available</p>
              )}
            </div>

            {/* Audience (list, supports future multi-audience) */}
            <div className="feedback-audience-list">
              {audiences.map((a) => (
                <div
                  key={a.name}
                  className="feedback-card"
                  data-source="audience"
                >
                  <div className="feedback-header">
                    <span className="feedback-source-label">
                      {a.name.charAt(0).toUpperCase() + a.name.slice(1)}
                    </span>
                    <span className="feedback-energy-label">
                      {energyLabel(
                        (a.content as AudienceFeedbackContent).energy_delta,
                      )}
                    </span>
                  </div>
                  <p className="feedback-main">
                    {(a.content as AudienceFeedbackContent).reaction}
                  </p>
                  <p className="feedback-detail">
                    {(a.content as AudienceFeedbackContent).reason}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Decision */}
      <section className="section">
        <h2 className="section-label">Decision</h2>
        <div className="decision-content">
          {decision ? (
            <>
              <div className="decision-adopted-block">
                <p className="decision-adopted-agent" data-agent={decision.adopted}>
                  Adopted: {decision.adopted.charAt(0).toUpperCase() + decision.adopted.slice(1)}
                </p>
                <p className="decision-reason">{decision.reason}</p>
                <p className="decision-applied">
                  bpm={decision.applied_params.bpm}{" "}
                  energy={(decision.applied_params.energy * 100).toFixed(0)}%{" "}
                  focus={decision.applied_params.focus}
                </p>
              </div>

              {decision.rejections && decision.rejections.length > 0 && (
                <div className="decision-rejections">
                  <p className="decision-rejections-label">Rejected</p>
                  {decision.rejections.map((r) => (
                    <div
                      key={r.agent_name}
                      className="decision-rejection-item"
                      data-agent={r.agent_name}
                    >
                      <p className="rejection-agent">
                        {r.agent_name.charAt(0).toUpperCase() + r.agent_name.slice(1)}
                      </p>
                      <p className="rejection-summary">{r.summary}</p>
                      <p className="rejection-reason">{r.reason}</p>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <>
              <p className="decision-adopted-agent">No decision yet</p>
              <p className="decision-reason">
                {session ? "Waiting for turn..." : "Session has not started"}
              </p>
            </>
          )}
        </div>
      </section>

      {/* Request (hidden in preview mode) */}
      {!preview && (
        <section className="section">
          <h2 className="section-label">Request</h2>
          <div className="request-form">
            <textarea
              className="request-input"
              placeholder="Send a request to the DJs..."
              rows={2}
              disabled={!isRunning || isBusy}
              value={requestText}
              onChange={(e) => setRequestText(e.target.value)}
            />
            <button
              className="request-button"
              type="button"
              disabled={!isRunning || requestText.trim() === "" || isBusy}
              onClick={handleSendRequest}
            >
              {loading === "sending" || loading === "turning"
                ? loadingLabel
                : "Send"}
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
