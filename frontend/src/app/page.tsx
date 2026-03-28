"use client";

import { Suspense, useCallback, useRef, useState } from "react";
import {
  startSession,
  submitRequest,
  runTurn,
  updateGenreGroup,
  fetchInterventions,
  fetchProfile,
  clearMemory,
  type MemoryIntervention,
  type MemoryProfile,
} from "@/lib/api";
import { SCENARIO_NAMES, TIMELINE_NAMES } from "@/lib/previewData";
import { THEMES } from "@/lib/themes";
import { usePreview, type PreviewState } from "@/lib/usePreview";
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

const SECTION_ORDER = ["intro", "build", "peak", "release"] as const;

const THEME_SHORT: Record<string, string> = {
  "tokyo-night": "TKY",
  cyberpunk: "CYB",
  "velvet-lounge": "VLV",
  "afterhours-mist": "AFT",
  warehouse: "WRH",
};

const GENRE_GROUPS = [
  { id: "house_party", label: "House Party" },
  { id: "techno_night", label: "Techno Night" },
  { id: "edm_festival", label: "EDM Festival" },
  { id: "bass_music", label: "Bass Music" },
  { id: "hiphop_rnb", label: "Hip Hop / R&B" },
  { id: "latin_global", label: "Latin / Global" },
  { id: "disco_funk", label: "Disco / Funk" },
  { id: "rock_indie", label: "Rock / Indie" },
  { id: "chill_lounge", label: "Chill / Lounge" },
  { id: "open_format", label: "Open Format" },
] as const;

const AGENT_ROLES: Record<string, string> = {
  groove: "Rhythm",
  harmony: "Tonal",
  crowd: "Floor",
};

function pixelAgent(agent: string) {
  return (
    <span className="pixel-agent" data-agent={agent} aria-hidden="true">
      <span className="pixel-agent-body" />
    </span>
  );
}

function agentLabel(name: string, showRole: boolean = false) {
  const display = name.charAt(0).toUpperCase() + name.slice(1);
  const role = AGENT_ROLES[name];
  return (
    <>
      {pixelAgent(name)}
      {display}
      {showRole && role && <span className="agent-role">{role}</span>}
    </>
  );
}

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

export default function Home() {
  return (
    <Suspense>
      <HomeContent />
    </Suspense>
  );
}

function previewScenarioData(state: PreviewState) {
  if (!state) return null;
  if (state.kind === "snapshot") return state.scenario;
  return state.current;
}

function HomeContent() {
  const previewState = usePreview();
  const [currentTheme, setTheme] = useTheme();
  const stream = useSessionStream({ enabled: !previewState });

  // In preview mode, use fixture data; otherwise use SSE stream
  const previewData = previewScenarioData(previewState);
  const session = previewData ? previewData.session : stream.session;
  const proposals = previewData ? previewData.proposals : stream.proposals;
  const feedback = previewData ? previewData.feedback : stream.feedback;
  const decision = previewData ? previewData.decision : stream.decision;
  const connected = previewState ? true : stream.connected;
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
          <span className="pixel-cat" aria-hidden="true">
            <span className="pixel-cat-face" />
            <span className="pixel-cat-gear" />
          </span>
          <h1 className="app-title">DeckCrew</h1>
          <span className="pixel-cat" aria-hidden="true">
            <span className="pixel-cat-face" />
            <span className="pixel-cat-gear" />
          </span>
        </div>

        {previewState ? (
          <div className="preview-banner">
            <span className="preview-label">Preview</span>
            <span className="preview-scenario">
              {previewState.kind === "timeline"
                ? previewState.timeline.name
                : previewState.scenario.name}
            </span>

            {/* Timeline step navigation */}
            {previewState.kind === "timeline" && (
              <div className="timeline-nav">
                <button
                  type="button"
                  className="timeline-nav-button"
                  disabled={!previewState.hasPrev}
                  onClick={previewState.goToPrev}
                >
                  ◀ Prev
                </button>
                <div className="timeline-steps">
                  {previewState.timeline.steps.map((step, i) => (
                    <span
                      key={step.label}
                      className={`timeline-step-dot ${i === previewState.stepIndex ? "active" : ""} ${i < previewState.stepIndex ? "visited" : ""}`}
                      title={step.label}
                    >
                      {step.label}
                    </span>
                  ))}
                </div>
                <button
                  type="button"
                  className="timeline-nav-button"
                  disabled={!previewState.hasNext}
                  onClick={previewState.goToNext}
                >
                  Next ▶
                </button>
              </div>
            )}

            {/* Snapshot scenarios */}
            <div className="preview-nav">
              <span className="preview-nav-group-label">Snapshots</span>
              {SCENARIO_NAMES.map((s) => {
                const activeName =
                  previewState.kind === "snapshot"
                    ? previewState.scenario.name
                    : "";
                return (
                  <a
                    key={s}
                    href={`?preview=${s}${currentTheme !== "tokyo-night" ? `&theme=${currentTheme}` : ""}`}
                    className={`preview-link ${s === activeName ? "active" : ""}`}
                  >
                    {s}
                  </a>
                );
              })}
            </div>

            {/* Timeline scenarios */}
            <div className="preview-nav">
              <span className="preview-nav-group-label">Timelines</span>
              {TIMELINE_NAMES.map((s) => {
                const activeName =
                  previewState.kind === "timeline"
                    ? previewState.timeline.name
                    : "";
                return (
                  <a
                    key={s}
                    href={`?preview=${s}${currentTheme !== "tokyo-night" ? `&theme=${currentTheme}` : ""}`}
                    className={`preview-link ${s === activeName ? "active" : ""}`}
                  >
                    {s.replace("timeline-", "")}
                  </a>
                );
              })}
            </div>

            {/* Theme switcher */}
            <div className="preview-nav">
              {THEMES.map((t) => {
                const currentPreviewName =
                  previewState.kind === "timeline"
                    ? previewState.timeline.name
                    : previewState.scenario.name;
                return (
                  <a
                    key={t.id}
                    href={`?preview=${currentPreviewName}${t.id !== "tokyo-night" ? `&theme=${t.id}` : ""}`}
                    className={`preview-link ${t.id === currentTheme ? "active" : ""}`}
                  >
                    {t.label}
                  </a>
                );
              })}
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
        <ThemeSelector currentTheme={currentTheme} onSelect={setTheme} />
      </header>

      {/* Now Playing */}
      <section className="section">
        <h2 className="section-label">
          <span className="record-dot" />
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

        {session?.section && (
          <div className="section-progress">
            {SECTION_ORDER.map((s, i) => {
              const currentIdx = SECTION_ORDER.indexOf(
                session.section!.current_section as typeof SECTION_ORDER[number],
              );
              const state =
                i === currentIdx ? "current" : i < currentIdx ? "visited" : "upcoming";
              return (
                <span key={s} className={`section-step ${state}`}>
                  {s}
                </span>
              );
            })}
          </div>
        )}

        {session?.venue && (
          <div className="venue-badge">
            {session.venue.room_size} · {session.venue.time_of_night.replace("_", " ")} · {session.venue.event_vibe}
          </div>
        )}

        <GenreSelector
          current={session?.current_params.genre_group ?? "house_party"}
          disabled={!isRunning || !!previewState}
          isPreview={!!previewState}
        />

        <div className="now-playing-params">
          <div className="param">
            <span className="param-key">Mood</span>
            <span className="param-value">
              {session?.current_params.mood ?? "—"}
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
          <div className="param-divider" />
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
            {session && (
              <span className="energy-meter">
                {Array.from({ length: 10 }, (_, i) => (
                  <span
                    key={i}
                    className={`energy-block ${i < Math.round(session.current_params.energy * 10) ? "filled" : ""}`}
                  />
                ))}
              </span>
            )}
          </div>
          {isRunning && (
            <span
              className={`booth-mascot ${session?.section?.current_section === "peak" ? "mascot-peak" : session?.section?.current_section === "release" ? "mascot-idle" : ""}`}
              aria-hidden="true"
            >
              <span className="mascot-headphone" />
              <span className="mascot-head">
                <span className="mascot-visor" />
              </span>
              <span className="mascot-body" />
            </span>
          )}
        </div>
      </section>

      {/* DJ Proposals */}
      <section className="section">
        <h2 className="section-label"><span className="record-dot" /> DJ</h2>
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
                {agentLabel(p.agent_name, true)}
              </div>
              <p className="proposal-text">{p.summary}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Room Feedback */}
      <section className="section">
        <h2 className="section-label"><span className="record-dot" /> Feedback</h2>
        {feedback.length === 0 ? (
          <p className="feedback-placeholder">
            {session ? "Waiting for feedback..." : "Waiting for session..."}
          </p>
        ) : (
          <div className="feedback-grid">
            {/* Critic */}
            <div className="feedback-card" data-source="critic">
              <div className="feedback-header">
                <span className="feedback-source-label">{pixelAgent("critic")}Critic</span>
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
                    &ldquo;{(critic.content as CriticFeedbackContent).issue}&rdquo;
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
              {audiences.map((a) => {
                const content = a.content as AudienceFeedbackContent;
                const delta = content.energy_delta;
                const deltaStr = delta > 0 ? `+${delta.toFixed(2)}` : delta.toFixed(2);
                return (
                  <div
                    key={a.name}
                    className="feedback-card"
                    data-source="audience"
                    data-persona={a.name}
                  >
                    <div className="feedback-header">
                      <span className="feedback-source-label">
                        {pixelAgent("audience")}
                        {a.name.charAt(0).toUpperCase() + a.name.slice(1)}
                      </span>
                      <span className="feedback-energy-delta">{deltaStr}</span>
                    </div>
                    <p className="feedback-main">&ldquo;{content.reaction}&rdquo;</p>
                    <p className="feedback-detail">{content.reason}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </section>

      {/* Decision */}
      <DecisionSection decision={decision} session={session} />

      {/* Request (hidden in preview mode) */}
      {!previewState && (
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

      {/* Memory (debug panel, hidden in preview mode) */}
      {!previewState && <MemoryPanel />}
    </div>
  );
}

function ThemeSelector({
  currentTheme,
  onSelect,
}: {
  currentTheme: string;
  onSelect: (themeId: string) => void;
}) {
  return (
    <div className="theme-selector">
      {THEMES.map((t) => (
        <button
          key={t.id}
          type="button"
          className={`theme-chip ${t.id === currentTheme ? "active" : ""}`}
          title={t.label}
          onClick={() => onSelect(t.id)}
        >
          {THEME_SHORT[t.id] ?? t.id}
        </button>
      ))}
    </div>
  );
}

function GenreSelector({
  current,
  disabled,
  isPreview,
}: {
  current: string;
  disabled: boolean;
  isPreview: boolean;
}) {
  const [updating, setUpdating] = useState(false);

  async function handleSelect(id: string) {
    if (id === current || disabled || updating) return;
    setUpdating(true);
    try {
      await updateGenreGroup(id);
    } catch {
      // SSE will reflect the actual state
    } finally {
      setUpdating(false);
    }
  }

  return (
    <div className={`genre-selector ${isPreview ? "preview-disabled" : ""}`}>
      {GENRE_GROUPS.map((g) => (
        <button
          key={g.id}
          type="button"
          className={`genre-chip ${g.id === current ? "active" : ""}`}
          disabled={disabled || updating}
          onClick={() => handleSelect(g.id)}
        >
          {g.label}
        </button>
      ))}
    </div>
  );
}

function DecisionSection({
  decision,
  session,
}: {
  decision: import("@/types/session").Decision | null;
  session: import("@/types/session").SessionState | null;
}) {
  const [rejectionsOpen, setRejectionsOpen] = useState(false);
  const rejectionCount = decision?.rejections?.length ?? 0;

  // Reset open state when decision changes
  const decisionKey = decision ? `${decision.adopted}-${decision.reason}` : "";
  const prevKeyRef = useRef(decisionKey);
  if (decisionKey !== prevKeyRef.current) {
    prevKeyRef.current = decisionKey;
    setRejectionsOpen(false);
  }

  return (
    <section className="section">
      <h2 className="section-label"><span className="record-dot" /> Decision</h2>
      <div className="decision-content">
        {decision ? (
          <>
            <div className="decision-adopted-block">
              <p className="decision-adopted-agent" data-agent={decision.adopted}>
                Adopted: {agentLabel(decision.adopted)}
                {decision.kind && (
                  <span className={`decision-kind-badge ${decision.kind === "major" ? "kind-major" : "kind-minor"}`}>
                    {decision.kind}
                  </span>
                )}
                {decision.dialogue?.mode === "semi_free" && (
                  <span className="dialogue-mode-badge">semi_free</span>
                )}
              </p>
              <p className="decision-reason">{decision.reason}</p>
              <p className="decision-applied">
                mood={decision.applied_params.mood}{" "}
                bpm={decision.applied_params.bpm}{" "}
                energy={(decision.applied_params.energy * 100).toFixed(0)}%{" "}
                texture={decision.applied_params.texture}{" "}
                focus={decision.applied_params.focus}
              </p>
            </div>

            {rejectionCount > 0 && (
              <div className="decision-rejections">
                <button
                  type="button"
                  className="decision-rejections-toggle"
                  onClick={() => setRejectionsOpen((v) => !v)}
                >
                  <span>{rejectionsOpen ? "▼" : "▶"}</span>
                  <span>Rejected ({rejectionCount})</span>
                </button>
                {rejectionsOpen &&
                  decision.rejections!.map((r) => (
                    <div
                      key={r.agent_name}
                      className="decision-rejection-item"
                      data-agent={r.agent_name}
                    >
                      <p className="rejection-agent">
                        {agentLabel(r.agent_name)}
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
  );
}

function MemoryPanel() {
  const [open, setOpen] = useState(false);
  const [profile, setProfile] = useState<MemoryProfile | null>(null);
  const [interventions, setInterventions] = useState<
    MemoryIntervention[] | null
  >(null);
  const [clearing, setClearing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [p, i] = await Promise.all([
        fetchProfile(),
        fetchInterventions(),
      ]);
      setProfile(p);
      setInterventions(i);
    } catch {
      // Backend not available; leave null
    }
  }, []);

  function handleToggle() {
    const next = !open;
    setOpen(next);
    if (next) {
      loadData();
    }
  }

  async function handleClear() {
    setClearing(true);
    try {
      await clearMemory();
      await loadData();
    } catch {
      // ignore
    } finally {
      setClearing(false);
    }
  }

  return (
    <section className="section memory-panel">
      <button
        type="button"
        className="memory-toggle"
        onClick={handleToggle}
      >
        <span>{open ? "▼" : "▶"}</span>
        <span className="section-label" style={{ marginBottom: 0 }}>
          Local Memory
          {interventions !== null && (
            <span className="memory-count">
              {interventions.length} intervention
              {interventions.length !== 1 ? "s" : ""}
            </span>
          )}
        </span>
      </button>

      {open && (
        <div className="memory-content">
          {profile && (
            <div className="memory-profile">
              <span className="memory-field">
                mood={profile.preferred_mood ?? "—"}
              </span>
              <span className="memory-field">
                energy={profile.min_energy.toFixed(2)}-
                {profile.max_energy.toFixed(2)}
              </span>
              <span className="memory-field">
                focus={profile.preferred_focus ?? "—"}
              </span>
            </div>
          )}

          {interventions && interventions.length > 0 && (
            <ul className="memory-interventions">
              {interventions.map((iv, idx) => (
                <li key={idx} className="memory-intervention">
                  Turn {iv.turn}: &quot;{iv.text}&quot; → {iv.adopted_agent}
                </li>
              ))}
            </ul>
          )}

          {interventions && interventions.length === 0 && (
            <p className="memory-empty">No interventions recorded</p>
          )}

          <button
            type="button"
            className="memory-clear"
            disabled={clearing || (interventions?.length ?? 0) === 0}
            onClick={handleClear}
          >
            {clearing ? "Clearing..." : "Clear Memory"}
          </button>
        </div>
      )}
    </section>
  );
}
