import json
import os
import sys
import numpy as np
import csv

def run_monte_carlo(base_rate, gigs_per_month, market_volatility, simulations=5000, months=12):
    expected_monthly = base_rate * gigs_per_month
    paths = np.zeros((simulations, months))
    
    for i in range(simulations):
        for m in range(months):
            shock = np.random.normal(loc=0.0, scale=market_volatility)
            paths[i, m] = expected_monthly * max(0.1, (1.0 + shock))
            
    yearly_totals = paths.sum(axis=1)
    return {
        "paths": paths,
        "yearly_totals": yearly_totals,
        "mean_yearly": float(np.mean(yearly_totals)),
        "worst_case": float(np.percentile(yearly_totals, 5)),
        "best_case": float(np.percentile(yearly_totals, 95)),
        "risk_percentage": float(np.sum(yearly_totals < (expected_monthly*12*0.60)) / simulations * 100)
    }

import csv
import os

def get_dirty_baseline():
    dirty_path = "outputs/raw_dataset.csv"
    base_prices = []
    
    if os.path.exists(dirty_path):
        with open(dirty_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                val = row.get("price")
                # Dirty parsing: accounts for missing, strange formatting, etc.
                if val and type(val) is str and "$" in val:
                    try:
                        nums = [int(s) for s in val.replace("$", "").replace(",", "").split() if s.isdigit()]
                        if nums:
                            base_prices.append(sum(nums) / len(nums))
                    except:
                        pass
                        
    if base_prices:
        avg_rate = sum(base_prices) / len(base_prices)
    else:
        avg_rate = 40.0

    return {
        "base_rate": round(avg_rate, 2),
        "base_gigs": 18, # Market average baseline
        "base_volatility": 0.18 # Market baseline volatility
    }

def generate_what_if_simulation(params):
    # AFTER parameters (user inputs)
    sim_rate = float(params.get("base_rate", 50.0))
    sim_gigs = int(params.get("gigs_per_month", 20))
    sim_volatility = float(params.get("market_volatility", 25.0)) / 100.0
    
    # BEFORE parameters (Extract directly from DIRTY Dataset)
    dirty_baseline = get_dirty_baseline()
    base_rate = dirty_baseline["base_rate"]
    base_gigs = dirty_baseline["base_gigs"]
    base_volatility = dirty_baseline["base_volatility"]
    
    months = 12
    simulations = 5000
    
    res_before = run_monte_carlo(base_rate, base_gigs, base_volatility, simulations, months)
    res_after = run_monte_carlo(sim_rate, sim_gigs, sim_volatility, simulations, months)
    
    logs = [
        f"Initialized Monte Carlo engine. Paths per scenario: {simulations}",
        f"BEFORE (Baseline): Rate ${base_rate}, Gigs {base_gigs}, Volatility {base_volatility*100}%",
        f"AFTER (Simulated): Rate ${sim_rate}, Gigs {sim_gigs}, Volatility {sim_volatility*100}%"
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
        
        fig, ax = plt.subplots(figsize=(10, 5))
        x_axis = [f"M{m+1}" for m in range(months)]
        
        # Plot AFTER paths in background (Blue)
        for path in res_after["paths"][:30]:
            ax.plot(x_axis, path, color="#38bdf8", alpha=0.1, linewidth=1)
            
        # Plot BEFORE paths in background (Pink)
        for path in res_before["paths"][:30]:
            ax.plot(x_axis, path, color="#f472b6", alpha=0.1, linewidth=1)
            
        # Means
        ax.plot(x_axis, res_before["paths"].mean(axis=0), color="#ec4899", linewidth=3, label="Before (Baseline Mean)")
        ax.plot(x_axis, res_after["paths"].mean(axis=0), color="#0ea5e9", linewidth=3, label="After (Shocked Mean)")
        
        ax.set_title("Before vs After Variance Trajectories", fontsize=14, pad=14, color=DARK["text"], fontweight="bold")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.legend(facecolor=DARK["card"], edgecolor=DARK["border"])
        
        os.makedirs("outputs", exist_ok=True)
        chart_path = "outputs/f15_monte_carlo.png"
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
        plt.close()
        
        logs.append("Chart: Before/After Spaghetti Plotted")
        charts.append({
            "path": chart_path,
            "title": "Stochastic Variance Projection",
            "insight": f"Compares the exact bounds of the historical baseline against your modified After parameters."
        })
    except Exception as e:
        logs.append(f"Chart generation failed: {e}")

    preview_data = []
    for m in range(months):
        col_before = res_before["paths"][:, m]
        col_after = res_after["paths"][:, m]
        preview_data.append({
            "month": f"M{m+1}",
            "before_mean": round(float(np.mean(col_before)), 2),
            "after_mean": round(float(np.mean(col_after)), 2),
            "diff": round(float(np.mean(col_after)) - float(np.mean(col_before)), 2)
        })

    csv_path = "outputs/f15_simulated_paths.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["month", "before_mean", "after_mean", "diff"])
        writer.writeheader()
        writer.writerows(preview_data)

    return {
        "status": "success",
        "message": "What-If Simulation computed successfully.",
        "params": params,
        "metrics_before": {
            "mean_yearly": round(res_before["mean_yearly"], 2),
            "worst_case": round(res_before["worst_case"], 2),
            "best_case": round(res_before["best_case"], 2),
            "risk_percentage": round(res_before["risk_percentage"], 1)
        },
        "metrics_after": {
            "mean_yearly": round(res_after["mean_yearly"], 2),
            "worst_case": round(res_after["worst_case"], 2),
            "best_case": round(res_after["best_case"], 2),
            "risk_percentage": round(res_after["risk_percentage"], 1)
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
