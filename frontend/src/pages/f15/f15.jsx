import React, { useState, useEffect } from "react";
import "./f15.css";

const API = "http://localhost:5000/api/features/15";

function Feature15() {
  const [loading, setLoading] = useState(false);
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState(null);

  // Simulation Parameters
  const [baseRate, setBaseRate] = useState(50);
  const [gigsPerMonth, setGigsPerMonth] = useState(20);
  const [volatility, setVolatility] = useState(25);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);

    try {
      const requestBody = {
        base_rate: baseRate,
        gigs_per_month: gigsPerMonth,
        market_volatility: volatility
      };

      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody)
      });

      if (!res.ok) throw new Error(`Server returned status: ${res.status}`);
      const data = await res.json();
      
      // Cache-bust the image due to identical filename overwrite by python
      if(data.charts && data.charts.length > 0) {
         data.charts[0].pathUrl = `http://localhost:5000/${data.charts[0].path}?cb=${new Date().getTime()}`;
      }
      
      setPayload(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Run a default simulation on mount
  useEffect(() => {
    runSimulation();
    // eslint-disable-next-line
  }, []);

  const { metrics_before, metrics_after, charts = [], data = [], logs = [], csv_path } = payload || {};

  return (
    <div className="f15-layout">
      {/* Abstract Backgrounds */}
      <div className="f15-bg-orb orb-primary"></div>
      <div className="f15-bg-orb orb-secondary"></div>

      <div className="f15-container">
        
        {/* Header Section */}
        <header className="f15-header">
          <div className="f15-badge">Module 15 / Simulation Engine</div>
          <h1 className="f15-title">What-<span className="f15-gradient-text">If</span> Simulation</h1>
          <p className="f15-subtitle">
            Compare historical baselines against hypothetical parameters using a 5,000-path Monte Carlo engine. 
            Instantly view risk boundaries and income projections based on shifting market turbulence.
          </p>
        </header>

        {/* Input Parameters Dashboard */}
        <div className="f15-control-panel glass-card">
          <div className="f15-panel-title">
            <h3>Simulation Parameters (After Shock)</h3>
            <button 
              className="f15-btn f15-btn-simulate"
              onClick={runSimulation}
              disabled={loading}
            >
              {loading ? "Computing Paths..." : "Run Monte Carlo Simulation"}
            </button>
          </div>

          <div className="f15-sliders-grid">
            
            <div className="f15-slider-group">
              <div className="f15-slider-header">
                <label>Avg Rate Per Gig</label>
                <span className="f15-slider-val">${baseRate}</span>
              </div>
              <input 
                type="range" min="10" max="250" step="5"
                value={baseRate} 
                onChange={(e) => setBaseRate(Number(e.target.value))}
                className="f15-range"
              />
            </div>

            <div className="f15-slider-group">
              <div className="f15-slider-header">
                <label>Gigs Per Month</label>
                <span className="f15-slider-val">{gigsPerMonth}</span>
              </div>
              <input 
                type="range" min="1" max="100" step="1"
                value={gigsPerMonth} 
                onChange={(e) => setGigsPerMonth(Number(e.target.value))}
                className="f15-range"
              />
            </div>

            <div className="f15-slider-group">
              <div className="f15-slider-header">
                <label>Market Volatility (%)</label>
                <span className="f15-slider-val">{volatility}%</span>
              </div>
              <input 
                type="range" min="0" max="100" step="5"
                value={volatility} 
                onChange={(e) => setVolatility(Number(e.target.value))}
                className="f15-range"
              />
            </div>

          </div>
        </div>

        {error && (
          <div className="f15-error-msg">
            ⚠️ {error}
          </div>
        )}

        {/* Results Block */}
        {payload && (
          <div className={`f15-results-block ${loading ? "simulating" : ""}`}>
            
            {/* KPI Cards Before / After */}
            {metrics_before && metrics_after && (
              <div className="f15-comparison-section">
                <h3 className="comparison-title">Simulation Analysis: Baseline vs Shocked</h3>
                <div className="f15-metrics-grid">
                  <div className="f15-metric highlight-blue">
                    <span className="m-label">Mean Expected Yearly</span>
                    <div className="m-compare-row">
                      <span className="m-before">${metrics_before.mean_yearly.toLocaleString()}</span>
                      <span className="m-icon">➔</span>
                      <span className="m-val">${metrics_after.mean_yearly.toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="f15-metric highlight-green">
                    <span className="m-label">Best Case (95th %ile)</span>
                    <div className="m-compare-row">
                      <span className="m-before">${metrics_before.best_case.toLocaleString()}</span>
                      <span className="m-icon">➔</span>
                      <span className="m-val">${metrics_after.best_case.toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="f15-metric highlight-orange">
                    <span className="m-label">Worst Case (5th %ile)</span>
                    <div className="m-compare-row">
                      <span className="m-before">${metrics_before.worst_case.toLocaleString()}</span>
                      <span className="m-icon">➔</span>
                      <span className="m-val">${metrics_after.worst_case.toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="f15-metric highlight-red">
                    <span className="m-label">Bankruptcy Risk (&lt;60%)</span>
                    <div className="m-compare-row">
                      <span className="m-before">{metrics_before.risk_percentage}%</span>
                      <span className="m-icon">➔</span>
                      <span className="m-val">{metrics_after.risk_percentage}%</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Graphs & Data */}
            <div className="f15-visualization-grid">
              
              {/* Monte Carlo Graph */}
              {charts.length > 0 && (
                <div className="f15-chart-wrapper glass-card">
                  <div className="f15-chart-header">
                    <h4>{charts[0].title}</h4>
                  </div>
                  <div className="f15-img-box">
                    <img src={charts[0].pathUrl} alt="Monte Carlo" />
                  </div>
                  <div className="f15-insight-box">
                    <strong>💡 Insight:</strong> {charts[0].insight}
                  </div>
                </div>
              )}

              {/* Data Table */}
              <div className="f15-data-wrapper glass-card">
                <div className="f15-table-header">
                  <h4>Monthly Path Analytics</h4>
                  {csv_path && (
                    <a href={`http://localhost:5000/${csv_path}`} download className="f15-btn-export">
                      Export CSV
                    </a>
                  )}
                </div>
                <div className="f15-table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Month</th>
                        <th>Mean Before</th>
                        <th>Mean After</th>
                        <th>Difference</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.map((row, i) => (
                        <tr key={i}>
                          <td>{row.month}</td>
                          <td className="text-muted">${row.before_mean.toLocaleString()}</td>
                          <td className="text-highlight">${row.after_mean.toLocaleString()}</td>
                          <td className={row.diff >= 0 ? "text-green" : "text-red"}>
                            {row.diff > 0 ? "+" : ""}{row.diff.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {/* Embedded Mini Logs */}
                <div className="f15-mini-logs">
                  {logs.slice(-2).map((l, i) => (
                    <div key={i} className="mini-log">&gt; {l}</div>
                  ))}
                </div>
              </div>

            </div>

          </div>
        )}

      </div>
    </div>
  );
}

export default Feature15;