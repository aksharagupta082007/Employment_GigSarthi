import json
import os
import sys
import numpy as np
import csv

def generate_what_if_simulation(params):
    base_rate = float(params.get("base_rate", 50.0))
    gigs_per_month = int(params.get("gigs_per_month", 20))
    market_volatility = float(params.get("market_volatility", 25.0)) / 100.0
    
    months = 12
    simulations = 5000
    
    # Expected base monthly income
    expected_monthly = base_rate * gigs_per_month
    
    # Generate random paths
    paths = np.zeros((simulations, months))
    
    for i in range(simulations):
        for m in range(months):
            shock = np.random.normal(loc=0.0, scale=market_volatility)
            monthly_income = expected_monthly * max(0.1, (1.0 + shock))
            paths[i, m] = monthly_income
            
    yearly_totals = paths.sum(axis=1)
    
    mean_yearly = float(np.mean(yearly_totals))
    worst_case = float(np.percentile(yearly_totals, 5))
    best_case = float(np.percentile(yearly_totals, 95))
    
    expected_yearly = expected_monthly * 12
    bankruptcy_threshold = expected_yearly * 0.60
    risk_percentage = float(np.sum(yearly_totals < bankruptcy_threshold) / simulations * 100)
    
    logs = [
        f"Initialized Monte Carlo engine. Paths: {simulations}",
        f"Input: Base Rate ${base_rate}, Gigs {gigs_per_month}, Volatility {market_volatility*100}%",
        f"Computed Mean Yearly: ${mean_yearly:,.2f} | 5th PC: ${worst_case:,.2f}"
    ]
    
    charts = []
    try:
        import matplotlib.pyplot as plt
        DARK = {"bg": "#0f172a", "card": "#1e293b", "border": "#334155", "text": "#f1f5f9", "muted": "#94a3b8"}
        plt.rcParams.update({
            "figure.facecolor": DARK["bg"], "axes.facecolor": DARK["card"],
            "axes.edgecolor": DARK["border"], "text.color": DARK["text"],
            "xtick.color": DARK["muted"], "ytick.color": DARK["muted"],
            "grid.color": "#334155"
        })
        
        fig, ax = plt.subplots(figsize=(9, 5))
        
        plot_paths = paths[:50]
        x_axis = [f"M{m+1}" for m in range(months)]
        for path in plot_paths:
            ax.plot(x_axis, path, color="#38bdf8", alpha=0.15, linewidth=1)
            
        mean_path = paths.mean(axis=0)
        ax.plot(x_axis, mean_path, color="#f472b6", linewidth=3, label="Expected Mean")
        
        ax.set_title(f"Monte Carlo Income Simulation ({simulations} Paths)", fontsize=14, pad=14, color=DARK["text"], fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.legend(facecolor=DARK["card"], edgecolor=DARK["border"])
        
        os.makedirs("outputs", exist_ok=True)
        chart_path = "outputs/f15_monte_carlo.png"
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
        plt.close()
        
        logs.append("Chart: Spaghetti Monte Carlo Plotted")
        charts.append({
            "path": chart_path,
            "title": "Stochastic Variance Projection",
            "insight": f"Visualizes possible income trajectories. The solid path is the mean expected income. The scattered lines demonstrate how severe {market_volatility*100:.1f}% volatility impacts stability."
        })
    except Exception as e:
        logs.append(f"Chart generation failed: {e}")

    preview_data = []
    for m in range(months):
        col_data = paths[:, m]
        preview_data.append({
            "month": f"M{m+1}",
            "expected_mean": round(float(np.mean(col_data)), 2),
            "bound_upper": round(float(np.percentile(col_data, 90)), 2),
            "bound_lower": round(float(np.percentile(col_data, 10)), 2)
        })

    csv_path = "outputs/f15_simulated_paths.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["month", "expected_mean", "bound_upper", "bound_lower"])
        writer.writeheader()
        writer.writerows(preview_data)

    return {
        "status": "success",
        "message": "What-If Simulation computed successfully.",
        "params": params,
        "metrics": {
            "mean_yearly": round(mean_yearly, 2),
            "worst_case": round(worst_case, 2),
            "best_case": round(best_case, 2),
            "risk_percentage": round(risk_percentage, 1)
        },
        "charts": charts,
        "data": preview_data,
        "csv_path": csv_path,
        "logs": logs
    }

if __name__ == "__main__":
    params = {}
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                params = json.load(f)

    if not params:
        params = {"base_rate": 50, "gigs_per_month": 20, "market_volatility": 25}

    result = generate_what_if_simulation(params)
    print(json.dumps(result))
