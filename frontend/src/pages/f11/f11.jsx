import React, { useState } from "react";
import "./f11.css";

function Feature11() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const runFeature = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const res = await fetch("http://localhost:5000/api/features/11");
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      if (data.status === "error") {
        throw new Error(data.message);
      }
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="f11-container">
      <div className="f11-header">
        <h2 className="f11-title">Model Optimization Engine</h2>
        <p className="f11-subtitle">
          Dynamically train multiple machine learning architectures, compare predictive performance, and auto-select the optimal model constraint.
        </p>
      </div>

      <button className="optimize-btn" onClick={runFeature} disabled={loading}>
        {loading ? (
          <>
            <div className="spinner-ml"></div> Auto-Tuning Models...
          </>
        ) : (
          "Run Optimization Pipeline"
        )}
      </button>

      {error && (
        <div className="ml-alert error">
          <span>⚠️</span> Pipeline Failed: {error}
        </div>
      )}

      {results && (
        <div className="ml-dashboard">
          <div className="ml-alert success">
            <span>🚀</span> {results.message}
          </div>

          <div className="dashboard-layout">
            
            <div className="best-model-panel">
              <div className="trophy-icon">🏆 Champion Model</div>
              <h3 className="champion-name">{results.best_model.name}</h3>
              <p className="champion-reasoning">{results.best_model.reasoning}</p>
            </div>

            <div className="comparison-table-panel">
              <h3 className="panel-title">Architectural Comparison</h3>
              <table className="ml-table">
                <thead>
                  <tr>
                    <th>Algorithm</th>
                    <th>R² Score</th>
                    <th>RMSE</th>
                    <th>MAE</th>
                  </tr>
                </thead>
                <tbody>
                  {results.comparison.map((mod, idx) => (
                    <tr key={idx} className={mod.modelName === results.best_model.name ? "winner-row" : ""}>
                      <td>{mod.modelName} {mod.modelName === results.best_model.name && '★'}</td>
                      <td className="score highlight">{mod.r2}</td>
                      <td className="score">{mod.rmse}</td>
                      <td className="score">{mod.mae}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

          </div>

          <div className="graph-panel">
            <h3 className="panel-title">Evaluation Visualization</h3>
            <div className="graph-container">
              <img 
                src={`http://localhost:5000/${results.graph_path}`} 
                alt="Model R2 Comparison Chart" 
                className="f11-graph"
              />
            </div>
          </div>

        </div>
      )}
    </div>
  );
}

export default Feature11;