import React, { useState } from "react";
import "./f03.css";

const API = "http://localhost:5000/api/features/03";

// ── Components ───────────────────────────────────────────────────────────────

const MetricCard = ({ title, value, icon, accentColor, reasoning }) => (
  <div className="f03-metric-card" style={{ borderBottomColor: accentColor }}>
    <div className="f03-metric-header">
      <span className="f03-metric-icon">{icon}</span>
      <h4 className="f03-metric-title">{title}</h4>
    </div>
    <div className="f03-metric-value">{value}</div>
    {reasoning && (
      <div className="f03-metric-reasoning">
        <strong>Insights:</strong> {reasoning}
      </div>
    )}
  </div>
);

// ── Main UI ──────────────────────────────────────────────────────────────────

function Feature03() {
  const [loading, setLoading] = useState(false);
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState(null);

  const executeAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API);
      if (!res.ok) throw new Error(`Server returned status: ${res.status}`);
      const data = await res.json();
      setPayload(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const { analysis_report: report, charts = [], data = [], logs = [], csv_path } = payload || {};

  return (
    <div className="f03-layout">
      {/* ── Background Elements ── */}
      <div className="f03-glow f03-glow-left"></div>
      <div className="f03-glow f03-glow-right"></div>

      <div className="f03-content-wrapper">
        <header className="f03-hero">
          <div className="f03-tag">Module 03 // Deep Analytics</div>
          <h1 className="f03-heading">Stability <span className="f03-highlight">Analysis</span></h1>
          <p className="f03-description">
            Evaluate income consistency, compute critical variances, and definitively identify whether the gig ecosystem displays stable or unstable behavior.
          </p>
          
          <button 
            className={`f03-action-btn ${loading ? 'loading' : ''}`}
            onClick={executeAnalysis}
            disabled={loading}
          >
            {loading ? (
              <><span className="f03-spinner"></span> Synthesizing Data...</>
            ) : (
              <><span className="f03-btn-icon">📈</span> Run Stability Analysis</>
            )}
          </button>
        </header>

        {error && (
          <div className="f03-error-banner">
            <span className="error-icon">⚠️</span> {error}
          </div>
        )}

        {payload && (
          <div className="f03-dashboard animate-in">
            {/* Success Message */}
            <div className="f03-success-banner">
              ✅ {payload.message}
            </div>

            {/* Stability Report & Reasoning Block */}
            <div className="f03-stability-report-box">
              <div className="f03-report-header">
                <h2>Final Dataset Stability Report</h2>
                <div className={`f03-behavior-badge ${report.global_market_behavior.includes('Unstable') ? 'badge-red' : 'badge-green'}`}>
                  {report.global_market_behavior}
                </div>
              </div>
              <p className="f03-report-text">
                {report.stability_report_text}
              </p>
            </div>

            {/* KPI Row */}
            <div className="f03-kpi-grid">
              <MetricCard 
                title="Avg Income Variance" 
                value={report.avg_income_variance} 
                icon="💸" 
                accentColor="#c084fc"
                reasoning={report.income_variance_reasoning}
              />
              <MetricCard 
                title="Avg Workload Variance" 
                value={report.avg_workload_variance} 
                icon="📦" 
                accentColor="#f472b6"
                reasoning={report.workload_variance_reasoning}
              />
            </div>

            {/* Chart Grid */}
            {charts.length > 0 && (
              <div className="f03-graphs-section">
                <div className="f03-section-title">
                  <h2>Statistical Graphs & Insights</h2>
                  <div className="f03-title-line"></div>
                </div>
                
                <div className="f03-chart-grid">
                  {charts.map((chart, idx) => (
                    <div key={idx} className="f03-chart-card">
                      <div className="f03-chart-image-wrap">
                        <img src={`http://localhost:5000/${chart.path}`} alt={chart.title} />
                      </div>
                      <div className="f03-chart-info">
                        <h3>{chart.title}</h3>
                        <p className="f03-chart-insight">
                          <span className="insight-badge">INSIGHT</span>
                          {chart.insight}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Bottom Row: Logs & Data Preview */}
            <div className="f03-bottom-grid">
              
              <div className="f03-panel f03-logs-panel">
                <h3>Execution Logs</h3>
                <div className="f03-log-container">
                  {logs.map((log, i) => (
                    <div key={i} className="f03-log-entry">
                      <span className="log-bullet">•</span> {log}
                    </div>
                  ))}
                </div>
              </div>

              <div className="f03-panel f03-data-panel">
                <div className="f03-panel-header">
                  <h3>Worker Extracted Data Preview</h3>
                  {csv_path && (
                    <a href={`http://localhost:5000/${csv_path}`} download className="f03-export-btn">
                      Export CSV
                    </a>
                  )}
                </div>
                
                <div className="f03-table-container">
                  <table className="f03-table">
                    <thead>
                      <tr>
                        <th>Worker ID</th>
                        <th>Avg/Mo</th>
                        <th>Income Var</th>
                        <th>Workload Var</th>
                        <th>Status</th>
                        <th>Reasoning</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.map((row, i) => (
                        <tr key={i}>
                          <td className="f03-id-cell">{row.worker_id}</td>
                          <td>${row.avg_monthly_income}</td>
                          <td className="f03-volatility-cell">{row.income_variance}</td>
                          <td className="f03-volatility-cell">{row.workload_variance}</td>
                          <td>
                            <span className={`f03-status-badge status-${row.stability_category.replace(/\s+/g, '-').toLowerCase()}`}>
                              {row.stability_category}
                            </span>
                          </td>
                          <td className="f03-reason-cell">{row.classification_reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Feature03;