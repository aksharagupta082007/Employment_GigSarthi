import json
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_time_series():
    # Resolve path to the cleaned dataset dynamically
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/gig_cleaned_data.csv'))
    
    if not os.path.exists(data_path):
        return {
            "status": "error",
            "message": f"Data file not found at {data_path}"
        }

    try:
        df = pd.read_csv(data_path)
        
        # Ensure 'date' column is datetime
        if 'date' not in df.columns:
            return {"status": "error", "message": "'date' column is missing in dataset."}
            
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date
        df = df.sort_values('date')
        
        # Group by date to get daily averages
        daily_data = df.groupby('date').agg({
            'earnings_per_day': 'mean',
            'hours_worked': 'mean'
        }).reset_index()
        
        # Calculate 7-day rolling averages
        daily_data['income_rolling_7'] = daily_data['earnings_per_day'].rolling(window=7, min_periods=1).mean()
        daily_data['workload_rolling_7'] = daily_data['hours_worked'].rolling(window=7, min_periods=1).mean()
        
        # Classify trends
        # We will compare the average of the first third of the period vs the last third
        n_days = len(daily_data)
        if n_days > 3:
            first_third_income = daily_data['earnings_per_day'].head(n_days // 3).mean()
            last_third_income = daily_data['earnings_per_day'].tail(n_days // 3).mean()
            
            first_third_workload = daily_data['hours_worked'].head(n_days // 3).mean()
            last_third_workload = daily_data['hours_worked'].tail(n_days // 3).mean()
            
            income_pct_change = (last_third_income - first_third_income) / first_third_income
            workload_pct_change = (last_third_workload - first_third_workload) / first_third_workload
            
            def classify(pct):
                if pct > 0.05: return "Growth"
                elif pct < -0.05: return "Decline"
                else: return "Stable"
                
            income_trend = classify(income_pct_change)
            workload_trend = classify(workload_pct_change)
        else:
            income_trend = "Stable"
            workload_trend = "Stable"
            
        # Plotting (Dark theme as in other features)
        os.makedirs("outputs", exist_ok=True)
        income_chart_path = "outputs/f07_income_trend.png"
        workload_chart_path = "outputs/f07_workload_trend.png"
        
        DARK = {"bg": "#0f172a", "card": "#1e293b", "border": "#334155", "text": "#f1f5f9", "muted": "#94a3b8"}
        
        def setup_plot(ax, title, ylabel):
            ax.set_title(title, fontsize=14, pad=14, color=DARK["text"], fontweight="bold")
            ax.set_facecolor(DARK["card"])
            ax.tick_params(colors=DARK["muted"])
            for spine in ax.spines.values():
                spine.set_color(DARK["border"])
            ax.grid(axis="y", linestyle="--", alpha=0.5, color="#334155")
            ax.set_ylabel(ylabel, color=DARK["muted"])
            ax.set_xlabel("Date", color=DARK["muted"])
            
        fig_facecolor = DARK["bg"]
        
        # 1. Income Trend Chart
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        fig1.patch.set_facecolor(fig_facecolor)
        setup_plot(ax1, "Average Daily Income Trend", "Income ($)")
        ax1.plot(daily_data['date'], daily_data['earnings_per_day'], color="#f472b6", alpha=0.3, label="Daily Avg")
        ax1.plot(daily_data['date'], daily_data['income_rolling_7'], color="#ec4899", linewidth=2.5, label="7-Day Rolling")
        ax1.legend(facecolor=DARK["card"], edgecolor=DARK["border"], labelcolor=DARK["text"])
        plt.tight_layout()
        plt.savefig(income_chart_path, dpi=150, facecolor=fig_facecolor)
        plt.close(fig1)
        
        # 2. Workload Trend Chart
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        fig2.patch.set_facecolor(fig_facecolor)
        setup_plot(ax2, "Average Daily Workload Trend", "Hours Worked")
        ax2.plot(daily_data['date'], daily_data['hours_worked'], color="#38bdf8", alpha=0.3, label="Daily Avg")
        ax2.plot(daily_data['date'], daily_data['workload_rolling_7'], color="#0ea5e9", linewidth=2.5, label="7-Day Rolling")
        ax2.legend(facecolor=DARK["card"], edgecolor=DARK["border"], labelcolor=DARK["text"])
        plt.tight_layout()
        plt.savefig(workload_chart_path, dpi=150, facecolor=fig_facecolor)
        plt.close(fig2)
        
        return {
            "status": "success",
            "message": "Time series intelligence completed.",
            "data": {
                "income_trend": income_trend,
                "workload_trend": workload_trend,
                "total_days_analyzed": n_days
            },
            "charts": [
                {
                    "title": "Income Trend Line Chart",
                    "path": income_chart_path,
                    "insight": f"Income is showing a {income_trend} trend."
                },
                {
                    "title": "Workload Trend Chart",
                    "path": workload_chart_path,
                    "insight": f"Workload is showing a {workload_trend} trend."
                }
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    result = analyze_time_series()
    print(json.dumps(result))
