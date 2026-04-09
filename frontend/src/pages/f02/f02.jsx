import React, { useState } from "react";
import "./f02.css";

const API = "http://localhost:5000/api/features/02";

// ── Small helpers ──────────────────────────────────────────────────────────────
const QualityRing = ({ score }) => {
  const r = 38;
  const circ = 2 * Math.PI * r;
  const fill = (score / 100) * circ;
  const color = score >= 90 ? "#34d399" : score >= 70 ? "#fbbf24" : "#f87171";

  return (
    <div className="quality-ring-wrap" aria-label={`Data quality score: ${score}%`}>
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#1e293b" strokeWidth="10" />
        <circle
          cx="50" cy="50" r={r}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={`${fill} ${circ}`}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          style={{ transition: "stroke-dasharray 1s ease" }}
        />
      </svg>
      <span className="quality-score" style={{ color }}>{score}%</span>
      <span className="quality-label">Quality</span>
    </div>
  );
};

const StatCard = ({ label, value, color, icon }) => (
  <div className="stat-card">
    <span className="stat-icon">{icon}</span>
    <span className="stat-value" style={{ color }}>{value}</span>
    <span className="stat-label">{label}</span>
  </div>
);

const LogPanel = ({ logs }) => (
  <div className="log-window" role="log" aria-live="polite">
    {logs.map((line, i) => (
      <div key={i} className="log-line">
        <span className="log-arrow">➔</span> {line}
      </div>
    ))}
  </div>
);

// ── Main Component ────────────────────────────────────────────────────────────
function Feature02() {
  const [loading, setLoading]     = useState(false);
  const [payload, setPayload]     = useState(null);
  const [error, setError]         = useState(null);
  const [activeChart, setActiveChart] = useState(0);

  const runFeature = async () => {
    setLoading(true);
    setError(null);
    setPayload(null);

    try {
      const res = await fetch(API);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setPayload(data);
      setActiveChart(0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const { cleaning_report: cr, charts = [], data = [], logs = [], csv_path } = payload || {};

  return (
    <div className="f02-container">

      {/* ── Header ── */}
      <header className="f02-header">
        <div className="f02-badge">Feature 02 · Medium</div>
        <h1 className="f02-title">
          <span className="gradient-text">Cleaning &amp; EDA</span> Engine
        </h1>
        <p className="f02-subtitle">
          Scrub the dataset of noise, fill gaps, eliminate duplicates, and illuminate
          hidden patterns through multiple exploratory data analysis graphs.
        </p>
      </header>

      {/* ── Run Button ── */}
      <button
        id="run-f02-btn"
        className="run-btn"
        onClick={runFeature}
        disabled={loading}
        aria-busy={loading}
      >
        {loading ? (
          <>
            <span className="spinner" aria-hidden="true" />
            Cleaning &amp; Analysing…
          </>
        ) : (
          <>
            <span className="btn-icon" aria-hidden="true">⚡</span>
            Run Cleaning
          </>
        )}
      </button>

      {/* ── Error ── */}
      {error && (
        <div className="alert alert-error" role="alert">
          ❌ {error}
        </div>
      )}

      {/* ── Results ── */}
      {payload && (
        <div className="results-wrapper">

          {/* Status banner */}
          <div className="alert alert-success" role="status">
            ✅ {payload.message}
          </div>

          {/* ── Stat Cards Row ── */}
          <div className="stats-row">
            <QualityRing score={cr.data_quality_score} />

            <div className="stat-cards-grid">
              <StatCard
                label="Original Rows"
                value={cr.original_rows}
                color="#94a3b8"
                icon="📄"
              />
              <StatCard
                label="Clean Rows"
                value={cr.rows_after_cleaning}
                color="#34d399"
                icon="✅"
              />
              <StatCard
                label="Duplicates Removed"
                value={cr.duplicates_removed}
                color="#f87171"
                icon="🗑"
              />
              <StatCard
                label="Missing Filled"
                value={cr.missing_values_filled}
                color="#fbbf24"
                icon="🔧"
              />
            </div>
          </div>

          {/* ── EDA Chart Gallery ── */}
          {charts.length > 0 && (
            <div className="card chart-section">
              <h2 className="card-title">Exploratory Data Analysis Graphs</h2>
              
              <div className="charts-grid-layout">
                {charts.map((chart, i) => (
                  <div key={i} className="chart-item">
                    <h3 className="chart-item-title">{chart.title}</h3>
                    <div className="chart-img-wrap">
                      <img
                        src={`http://localhost:5000/${chart.path}`}
                        alt={chart.title}
                        className="chart-img-fluid"
                      />
                    </div>
                    <div className="chart-insight-box">
                      <span className="insight-icon">💡</span>
                      <p className="insight-text">{chart.insight}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Logs + Download ── */}
          <div className="two-col">
            <div className="card">
              <h2 className="card-title">Processing Logs</h2>
              <LogPanel logs={logs} />
            </div>

            <div className="card action-card">
              <h2 className="card-title">Export Cleaned Data</h2>
              <p className="export-desc">
                Download the scrubbed, enriched dataset ready for the next pipeline stage.
              </p>
              {csv_path && (
                <a
                  href={`http://localhost:5000/${csv_path}`}
                  download
                  id="download-cleaned-csv"
                  className="download-btn"
                >
                  ⬇ Download Cleaned CSV
                </a>
              )}
              <div className="export-meta">
                <span>Rows: <strong>{cr.rows_after_cleaning}</strong></span>
                <span>Columns: <strong>{data[0] ? Object.keys(data[0]).length : "—"}</strong></span>
              </div>
            </div>
          </div>

          {/* ── Dataset Preview ── */}
          {data.length > 0 && (
            <div className="card full-width">
              <h2 className="card-title">Cleaned Dataset Preview</h2>
              <div className="table-scroll">
                <table className="preview-table" aria-label="Cleaned dataset preview">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Price</th>
                      <th>Category</th>
                      <th>Skills</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.slice(0, 8).map((row, i) => (
                      <tr key={row.id || i}>
                        <td><span className="id-badge">{row.id}</span></td>
                        <td>{row.title}</td>
                        <td><span className="price-badge">{row.price}</span></td>
                        <td>
                          <span className={`cat-badge cat-${(row.price_category || "unknown").split(" ")[0].toLowerCase()}`}>
                            {row.price_category || "Unknown"}
                          </span>
                        </td>
                        <td className="skills-cell">{row.skills}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {data.length > 8 && (
                <p className="table-footer">Showing 8 of {data.length} rows</p>
              )}
            </div>
          )}

        </div>
      )}
    </div>
  );
}

export default Feature02;