import React, { useState } from "react";
import "./f01.css";

function Feature01() {
  const [loading, setLoading] = useState(false);
  const [dataPayload, setDataPayload] = useState(null);
  const [error, setError] = useState(null);

  const runFeature = async () => {
    setLoading(true);
    setError(null);
    setDataPayload(null);
    
    try {
      const res = await fetch("http://localhost:5000/api/features/01");
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const result = await res.json();
      setDataPayload(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="f01-container">
      <div className="f01-header">
        <h2 className="f01-title">Data Awakening</h2>
        <p className="f01-subtitle">
          Extract raw gig economy data dynamically, filter garbage, and yield a clean CSV dataset.
        </p>
      </div>

      <button className="extract-btn" onClick={runFeature} disabled={loading}>
        {loading ? (
          <>
            <div className="spinner"></div> Extracting & Validating...
          </>
        ) : (
          "Initialize Scraper & Validate"
        )}
      </button>

      {error && (
        <div className="status-message error">
          ❌ Failed to collect data: {error}
        </div>
      )}

      {dataPayload && (
        <div className={`status-message ${dataPayload.status === 'fallback' ? 'fallback' : 'success'}`}>
          {dataPayload.status === 'fallback' ? '⚠️' : '✅'} {dataPayload.message}
        </div>
      )}

      {dataPayload && (
        <div className="results-container">
          
          <div className="dashboard-grid">
            {/* Validation Report Table */}
            <div className="dashboard-card">
              <h3>Validation Report</h3>
              <table className="stats-table">
                <tbody>
                  <tr>
                    <td>Total Raw Rows</td>
                    <td className="stat-val">{dataPayload.validation_report.total_raw_rows}</td>
                  </tr>
                  <tr>
                    <td>Missing Values Removed</td>
                    <td className="stat-val warning">{dataPayload.validation_report.missing_values_count}</td>
                  </tr>
                  <tr>
                    <td>Duplicate Entries Removed</td>
                    <td className="stat-val warning">{dataPayload.validation_report.duplicate_entries_count}</td>
                  </tr>
                  <tr>
                    <td><strong>Clean Valid Rows</strong></td>
                    <td className="stat-val success"><strong>{dataPayload.validation_report.valid_rows}</strong></td>
                  </tr>
                </tbody>
              </table>
              <a href={`http://localhost:5000/${dataPayload.csv_path}`} download className="download-btn">
                Download Clean CSV
              </a>
            </div>

            {/* Logs Panel */}
            <div className="dashboard-card logs-card">
              <h3>Scraping Logs</h3>
              <div className="log-window">
                <p><strong>Pages Scraped: </strong> {dataPayload.logs.pages_scraped}</p>
                <div className="log-events">
                  {dataPayload.logs.events.map((log, idx) => (
                    <div key={idx} className="log-line">➔ {log}</div>
                  ))}
                  {dataPayload.logs.errors.map((err, idx) => (
                    <div key={`err-${idx}`} className="log-line error-line">✖ Error: {err}</div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Dataset Preview */}
          <div className="dashboard-card full-width">
            <h3>Dataset Preview</h3>
            <div className="table-responsive">
              <table className="preview-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Price</th>
                    <th>Skills</th>
                  </tr>
                </thead>
                <tbody>
                  {dataPayload.data.slice(0, 5).map((job) => (
                    <tr key={job.id}>
                      <td>{job.id}</td>
                      <td>{job.title}</td>
                      <td><span className="price-badge">{job.price}</span></td>
                      <td>{job.skills}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {dataPayload.data.length > 5 && (
              <p className="table-footer">Showing 5 of {dataPayload.validation_report.valid_rows} rows...</p>
            )}
          </div>

        </div>
      )}
    </div>
  );
}

export default Feature01;