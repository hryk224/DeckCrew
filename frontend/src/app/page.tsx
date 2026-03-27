export default function Home() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">DeckCrew</h1>
      </header>

      {/* Now Playing */}
      <section className="section">
        <h2 className="section-label">Now Playing</h2>
        <div className="now-playing-params">
          <div className="param">
            <span className="param-key">Mood</span>
            <span className="param-value">—</span>
          </div>
          <div className="param">
            <span className="param-key">BPM</span>
            <span className="param-value">—</span>
          </div>
          <div className="param">
            <span className="param-key">Energy</span>
            <span className="param-value">—</span>
          </div>
          <div className="param">
            <span className="param-key">Texture</span>
            <span className="param-value">—</span>
          </div>
          <div className="param">
            <span className="param-key">Focus</span>
            <span className="param-value">—</span>
          </div>
        </div>
      </section>

      {/* DJ Proposals */}
      <section className="section">
        <h2 className="section-label">DJ Proposals</h2>
        <div className="proposals-grid">
          <div className="proposal-card" data-agent="groove">
            <div className="proposal-agent">Groove</div>
            <p className="proposal-text">Waiting for session...</p>
          </div>
          <div className="proposal-card" data-agent="harmony">
            <div className="proposal-agent">Harmony</div>
            <p className="proposal-text">Waiting for session...</p>
          </div>
          <div className="proposal-card" data-agent="crowd">
            <div className="proposal-agent">Crowd</div>
            <p className="proposal-text">Waiting for session...</p>
          </div>
        </div>
      </section>

      {/* Decision */}
      <section className="section">
        <h2 className="section-label">Decision</h2>
        <div className="decision-content">
          <p className="decision-adopted">No decision yet</p>
          <p className="decision-reason">Session has not started</p>
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
            disabled
          />
          <button className="request-button" type="button" disabled>
            Send
          </button>
        </div>
      </section>
    </div>
  );
}
