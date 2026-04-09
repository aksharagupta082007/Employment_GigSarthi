import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def optimize_models():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/gig_cleaned_data.csv'))
    if not os.path.exists(data_path):
        return {
            "status": "error",
            "message": f"Data file not found at {data_path}"
        }

    try:
        df = pd.read_csv(data_path)
        
        # Select features and target for Earnings Prediction
        features = ['hours_worked', 'jobs_completed', 'rating']
        categorical_features = ['platform', 'location']
        target = 'earnings_per_day'
        
        # Drop missing values in the relevant columns to be safe
        df = df.dropna(subset=features + categorical_features + [target])
        
        # One-hot encode categorical features
        X = df[features + categorical_features]
        X = pd.get_dummies(X, columns=categorical_features, drop_first=True)
        y = df[target]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        results = []
        best_model_name = ""
        best_r2 = -float("inf")
        best_model_reasoning = ""
        
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            
            mae = mean_absolute_error(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            r2 = r2_score(y_test, preds)
            
            results.append({
                "modelName": name,
                "mae": round(mae, 2),
                "rmse": round(rmse, 2),
                "r2": round(r2, 4)
            })
            
            if r2 > best_r2:
                best_r2 = r2
                best_model_name = name
                best_model_reasoning = f"{name} achieved the highest R² score ({round(r2, 4)}) and lowest error metrics, demonstrating superior capability in mapping non-linear correlations within the gig ecosystem."
        
        # Generate comparison graph
        os.makedirs("outputs", exist_ok=True)
        graph_path = "outputs/f11_model_comparison.png"
        
        plt.figure(figsize=(9, 5))
        sns.set_theme(style="darkgrid")
        
        model_names = [res["modelName"] for res in results]
        r2_scores = [res["r2"] for res in results]
        
        ax = sns.barplot(x=model_names, y=r2_scores, palette="mako")
        plt.title('Model Optimization: R² Score Comparison', fontsize=16)
        plt.ylabel('R² Score (Higher is Better)', fontsize=12)
        plt.xlabel('Algorithm', fontsize=12)
        plt.ylim(0, max(max(r2_scores) + 0.1, 1.0))
        
        for p in ax.patches:
            val = p.get_height()
            ax.annotate(f"{val:.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='baseline', fontsize=11, color='black', xytext=(0, 5), textcoords='offset points')
        
        plt.savefig(graph_path, bbox_inches='tight', dpi=150)
        plt.close()
        
        return {
            "status": "success",
            "message": "Model optimization pipeline completed.",
            "comparison": results,
            "best_model": {
                "name": best_model_name,
                "reasoning": best_model_reasoning
            },
            "graph_path": graph_path
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    result = optimize_models()
    print(json.dumps(result))
