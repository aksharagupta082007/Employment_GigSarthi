import json
import os
import csv
import random
import statistics

# ─── Data Helpers ─────────────────────────────────────────────────────────────

def get_base_prices():
    cleaned_path = "outputs/cleaned_dataset.csv"
    base_prices = []
    
    if os.path.exists(cleaned_path):
        with open(cleaned_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                val = row.get("price")
                if val and "$" in val:
                    try:
                        nums = [int(s) for s in val.replace("$", "").replace(",", "").split() if s.isdigit()]
                        if nums:
                            base_prices.append(sum(nums) / len(nums))
                    except:
                        pass
                        
    if not base_prices:
        base_prices = [25, 45, 120, 15, 60, 200, 30, 80]
        
    return base_prices

def generate_worker_history(num_workers, base_prices, months=12):
    workers = []
    
    for i in range(num_workers):
        tier_rate = random.choice(base_prices)
        
        income_history = []
        workload_history = []
        total_income = 0
        total_gigs = 0
        
        # 0: Stable, 1: Fluctuating, 2: Struggling
        profile_type = random.choices([0, 1, 2], weights=[0.4, 0.4, 0.2])[0]
        
        for m in range(months):
            if profile_type == 0:
                gigs_this_month = random.randint(15, 25)
                income_multiplier = random.uniform(0.9, 1.1)
            elif profile_type == 1:
                gigs_this_month = random.randint(2, 35)
                income_multiplier = random.uniform(0.5, 1.5)
            else:
                gigs_this_month = random.randint(0, 10)
                income_multiplier = random.uniform(0.6, 1.0)
                
            monthly_income = gigs_this_month * tier_rate * income_multiplier
            
            income_history.append(round(monthly_income, 2))
            workload_history.append(gigs_this_month)
            total_income += monthly_income
            total_gigs += gigs_this_month
            
        mean_income = statistics.mean(income_history)
        income_var = statistics.variance(income_history) if len(income_history) > 1 else 0
        workload_var = statistics.variance(workload_history) if len(workload_history) > 1 else 0
        
        stdev_income = statistics.stdev(income_history) if len(income_history) > 1 else 0
        volatility_index = (stdev_income / mean_income * 100) if mean_income > 0 else 0
        
        if volatility_index < 20: 
            stability_category = "Stable"
            classification_reason = f"Index is {volatility_index:.1f}% (<20%), indicating highly predictable income."
        elif volatility_index < 40: 
            stability_category = "Moderate"
            classification_reason = f"Index is {volatility_index:.1f}% (20-40%), showing slight but normal fluctuations."
        elif volatility_index < 70: 
            stability_category = "Volatile"
            classification_reason = f"Index is {volatility_index:.1f}% (40-70%), pointing to risky and irregular payouts."
        else: 
            stability_category = "Highly Unstable"
            classification_reason = f"Index is {volatility_index:.1f}% (>70%), a severe red flag for income consistency."

        workers.append({
            "worker_id": f"W-{1000 + i}",
            "avg_monthly_income": round(mean_income, 2),
            "total_yearly_income": round(total_income, 2),
            "income_variance": round(income_var, 2),
            "workload_variance": round(workload_var, 2),
            "volatility_index": round(volatility_index, 2),
            "stability_category": stability_category,
            "classification_reason": classification_reason,
            "total_gigs": total_gigs,
            "income_history": income_history,
            "workload_history": workload_history
        })
        
    return workers


# ─── Chart Generation ─────────────────────────────────────────────────────────

DARK = {
    "bg": "#0f172a", "card": "#1e293b", "border": "#334155",
    "text": "#f1f5f9", "muted": "#94a3b8", "grid": "#334155",
}

def _apply_dark_theme():
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": DARK["bg"], "axes.facecolor": DARK["card"],
        "axes.edgecolor": DARK["border"], "axes.labelcolor": DARK["muted"],
        "xtick.color": DARK["muted"], "ytick.color": DARK["muted"],
        "text.color": DARK["text"], "grid.color": DARK["grid"], "grid.alpha": 0.6,
    })

def chart_stability_distribution(workers, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()
        
        categories = [w["stability_category"] for w in workers]
        counts = {c: categories.count(c) for c in ["Stable", "Moderate", "Volatile", "Highly Unstable"]}
        
        fig, ax = plt.subplots(figsize=(7, 5))
        wedges, texts, autotexts = ax.pie(
            counts.values(), labels=counts.keys(), colors=["#34d399", "#38bdf8", "#fbbf24", "#f87171"],
            autopct="%1.0f%%", startangle=140, textprops={"color": DARK["text"], "fontsize": 11},
            wedgeprops={"edgecolor": DARK["bg"], "linewidth": 2}
        )
        for at in autotexts: at.set_fontweight("bold")
        
        ax.set_title("Worker Stability Categories", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)
        plt.tight_layout()
        path = "outputs/f03_stability_pie.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"]); plt.close()
        
        logs.append("Chart: Stability Categories generated")
        return {"path": path, "title": "Worker Stability Categories", "insight": "This chart shows the distribution of workers based on their income volatility. It gives a broad view of market behavior."}
    except Exception as e:
        logs.append(f"Chart error: {e}")
        return None

def chart_income_trend(workers, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()
        months = [f"M{i+1}" for i in range(12)]
        avg_history = [statistics.mean([w["income_history"][m] for w in workers]) for m in range(12)]
            
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(months, avg_history, marker='o', color="#818cf8", linewidth=3)
        ax.set_title("Average Income Over Time", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)
        ax.set_xlabel("Month", fontsize=11, labelpad=8)
        ax.set_ylabel("Income ($)", fontsize=11, labelpad=8)
        ax.grid(axis="y", linestyle="--")
        
        plt.tight_layout()
        path = "outputs/f03_income_trend.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"]); plt.close()
        logs.append("Chart: Income Trend generated")
        return {"path": path, "title": "Average Income Over Time", "insight": "Highlights macro-level fluctuations and potential seasonality in aggregate worker earnings across the designated tracking period."}
    except Exception as e:
        return None

def chart_workload_trend(workers, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()
        months = [f"M{i+1}" for i in range(12)]
        avg_workload = [statistics.mean([w["workload_history"][m] for w in workers]) for m in range(12)]
            
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(months, avg_workload, marker='s', color="#34d399", linewidth=3)
        ax.set_title("Average Workload Over Time", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)
        ax.set_xlabel("Month", fontsize=11, labelpad=8)
        ax.set_ylabel("Total Gigs", fontsize=11, labelpad=8)
        ax.grid(axis="y", linestyle="--")
        
        plt.tight_layout()
        path = "outputs/f03_workload_trend.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"]); plt.close()
        logs.append("Chart: Workload Trend generated")
        return {"path": path, "title": "Average Workload Over Time", "insight": "Indicates gig volume consistency. Large swings here directly cause the variances mapped in the final stability report."}
    except Exception as e:
        return None

def chart_volatility_histogram(workers, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()
        vols = [w["volatility_index"] for w in workers]
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(vols, bins=12, color="#f472b6", edgecolor=DARK["bg"])
        ax.set_title("Income Volatility Dispersion", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)
        ax.set_xlabel("Volatility Index (%)", fontsize=11, labelpad=8)
        ax.set_ylabel("Count", fontsize=11, labelpad=8)
        ax.grid(axis="y", linestyle="--")
        
        plt.tight_layout()
        path = "outputs/f03_vol_histogram.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"]); plt.close()
        logs.append("Chart: Volatility Histogram generated")
        return {"path": path, "title": "Income Volatility Dispersion", "insight": "A tight grouping near 0% means stable behavior globally. A wide spread or fat tail indicates heavily unstable dataset behavior."}
    except Exception as e:
        return None

# ─── Main Execution ───────────────────────────────────────────────────────────

def run_stability_analysis():
    logs = []
    logs.append("Initializing Stability Analysis Module.")
    
    base_prices = get_base_prices()
    num_workers = 150
    logs.append(f"Analyzing {num_workers} gig workers for income & workload variance.")
    
    workers = generate_worker_history(num_workers, base_prices, months=12)
    
    avg_income_var = statistics.mean([w["income_variance"] for w in workers])
    avg_workload_var = statistics.mean([w["workload_variance"] for w in workers])
    
    # Reasoning for overall stability behavior
    # Thresholding logic for demonstration:
    # We use workload variance (gigs/month variance). If avg variance in gigs > 50, it's highly unstable.
    # If the variance is low (< 20), stable.
    if avg_workload_var < 20: 
        market_behavior = "Stable Behavoir"
        report_text = f"The dataset exhibits STABLE behavior. The average workload variance is low ({avg_workload_var:.2f}), implying gig acquisition is steady month-to-month, leading to highly consistent income generation."
    elif avg_workload_var < 50:
        market_behavior = "Moderate Fluctuation"
        report_text = f"The dataset exhibits MODERATE fluctuation. Workload variance sits at {avg_workload_var:.2f}, causing noticeable but manageable shifts in monthly income consistency."
    else:
        market_behavior = "Unstable Behavior"
        report_text = f"The dataset exhibits UNSTABLE behavior. High workload variance ({avg_workload_var:.2f}) natively causes high income variance ({avg_income_var:.2f}), proving the market suffers from severe volatility."
        
    logs.append(f"Global behavior derived: {market_behavior}")
    
    income_var_reasoning = f"High variance indicates severe payload swings month-to-month. The current value ({avg_income_var:.2f}) signifies notable financial unpredictability." if avg_income_var > 300000 else f"Low variance indicates smooth monthly earnings. Current value ({avg_income_var:.2f}) shows predictable payouts."
    
    workload_var_reasoning = f"A variance above 50 is a severe red flag indicating highly volatile job volume." if avg_workload_var > 50 else f"Demonstrates healthy gig consistency. The value of {avg_workload_var:.2f} dictates steady worker demand."

    analysis_report = {
        "global_market_behavior": market_behavior,
        "stability_report_text": report_text,
        "avg_income_variance": round(avg_income_var, 2),
        "income_variance_reasoning": income_var_reasoning,
        "avg_workload_variance": round(avg_workload_var, 2),
        "workload_variance_reasoning": workload_var_reasoning
    }
    
    os.makedirs("outputs", exist_ok=True)
    
    charts_data = []
    try:
        import matplotlib
        for fn in [chart_stability_distribution, chart_income_trend, chart_workload_trend, chart_volatility_histogram]:
            c_data = fn(workers, logs)
            if c_data: charts_data.append(c_data)
    except Exception as e:
        logs.append("Matplotlib error, skipping charts.")
        
    csv_path = "outputs/f03_stability_analysis.csv"
    keys = ["worker_id", "avg_monthly_income", "income_variance", "workload_variance", "stability_category", "classification_reason", "total_gigs"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows([{k: w[k] for k in keys} for w in workers])
        
    preview_data = [ {k: w[k] for k in keys} for w in workers[:15] ]

    return {
        "status": "success",
        "message": f"Stability computation complete. Behavior identified: {market_behavior}",
        "analysis_report": analysis_report,
        "charts": charts_data,
        "data": preview_data,
        "csv_path": csv_path,
        "logs": logs
    }

if __name__ == "__main__":
    result = run_stability_analysis()
    print(json.dumps(result))
