import { useState } from 'react';
import './f07.css';

export default function Feature07() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runFeature = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:5000/api/features/07");
      const json = await res.json();
      if (json.status === "success") {
        setData(json);
      } else {
        setError(json.message || "An error occurred");
      }
    } catch (err) {
      setError("Failed to fetch data from backend. Is the server running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="f07-container">
      <div className="f07-header">
        <h1>Time Series Intelligence 📈</h1>
        <p>A temporal analysis of gig worker income and workload trends using rolling averages.</p>
      </div>

      <div className="f07-actions">
        <button className="f07-trigger-btn" onClick={runFeature} disabled={loading}>
          {loading ? "Generating Report..." : "Generate Trend Summary Report"}
        </button>
      </div>

      {error && <div className="f07-error">❌ {error}</div>}

      {data && (
        <div className="f07-content animated-fade-up">
          <div className="f07-summary-cards">
            <div className={`f07-card trend-card ${data.data.income_trend.toLowerCase()}`}>
              <h3>Income Trend</h3>
              <div className="trend-value">{data.data.income_trend}</div>
              <p>Over {data.data.total_days_analyzed} days analyzed</p>
            </div>
            
            <div className={`f07-card trend-card ${data.data.workload_trend.toLowerCase()}`}>
              <h3>Workload Trend</h3>
              <div className="trend-value">{data.data.workload_trend}</div>
              <p>Based on hours worked</p>
            </div>
          </div>

          <div className="f07-charts-grid">
            {data.charts && data.charts.map((chart, idx) => (
              <div className="f07-chart-wrapper" key={idx}>
                <h3>{chart.title}</h3>
                <img 
                  src={`http://localhost:5000/${chart.path}`} 
                  alt={chart.title} 
                  className="f07-chart-image"
                />
                <div className="f07-insight">
                  💡 <strong>Insight:</strong> {chart.insight}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}