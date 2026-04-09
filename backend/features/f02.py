import json
import os
import csv
import re
from collections import Counter

# ─── Data Loader ────────────────────────────────────────────────────────────────

FALLBACK_DATA = [
    {"id": "job-1",  "title": "React Developer Needed",        "description": "Need a React dev for a fullstack app.", "price": "$15 - $25 / hr", "skills": "React.js, Javascript"},
    {"id": "job-2",  "title": "Python Data Scraper",           "description": "Scrape e-commerce sites.",              "price": "$100",           "skills": "Python, Web Scraping"},
    {"id": "job-3",  "title": "Logo Design",                   "description": "Create a modern logo for a startup.",  "price": "$50",            "skills": "Graphic Design, Logo Design"},
    {"id": "job-4",  "title": "SEO Expert",                    "description": "Improve ranking for my website.",       "price": "$20 / hr",       "skills": "SEO, Marketing"},
    {"id": "job-5",  "title": "WordPress Developer",           "description": "Build a WordPress site.",               "price": "$200",           "skills": "WordPress, PHP"},
    {"id": "job-6",  "title": "Mobile App Developer",          "description": "iOS app development.",                  "price": "$30 - $50 / hr", "skills": "Swift, iOS"},
    {"id": "job-7",  "title": "Content Writer",                "description": "Write SEO blog posts in detail.",       "price": "$25",            "skills": "Writing, SEO"},
    {"id": "job-8",  "title": "Data Analyst",                  "description": "Analyse sales data quickly.",           "price": "$40 / hr",       "skills": "Python, Excel, SQL"},
    {"id": "job-9",  "title": "UI/UX Designer",                "description": "Design mobile interfaces today.",       "price": "$35 / hr",       "skills": "Figma, UI Design"},
    {"id": "job-10", "title": "Machine Learning Engineer",     "description": "Build ML models using pytorch.",        "price": "$60 / hr",       "skills": "Python, TensorFlow, ML"},
    {"id": "job-11", "title": "Backend Developer",             "description": "",                                      "price": "$45 / hr",       "skills": "Node.js, Express"},
    {"id": "job-12", "title": "Blockchain Developer",          "description": "Smart contract dev.",                   "price": "$80 / hr",       "skills": "Solidity, Ethereum"},
    {"id": "job-13", "title": "React Developer Needed",        "description": "Duplicate entry.",                      "price": "$20 / hr",       "skills": "React.js"},
    {"id": "job-14", "title": "Video Editor",                  "description": "Edit YouTube shorts.",                  "price": "$30",            "skills": "Premiere Pro, After Effects"},
    {"id": "job-15", "title": "Cloud Architect",               "description": "AWS infrastructure design.",            "price": "$120 / hr",      "skills": "AWS, DevOps, Terraform"},
]


def load_dataset():
    csv_path = "outputs/raw_dataset.csv"
    if os.path.exists(csv_path):
        data = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        return data, True
    return [dict(r) for r in FALLBACK_DATA], False


# ─── Helpers ───────────────────────────────────────────────────────────────

def parse_price(price_str):
    if not price_str:
        return None
    numbers = re.findall(r"\d+(?:\.\d+)?", price_str.replace(",", ""))
    if not numbers:
        return None
    nums = [float(n) for n in numbers]
    return sum(nums) / len(nums)


def categorize_price(val):
    if val is None:
        return "Unknown"
    if val < 30:
        return "Low (<$30)"
    elif val < 75:
        return "Mid ($30–$75)"
    elif val < 150:
        return "High ($75–$150)"
    else:
        return "Premium (>$150)"


# ─── Chart Generation ─────────────────────────────────────────────────────────────

DARK = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "border": "#334155",
    "text": "#f1f5f9",
    "muted": "#94a3b8",
    "grid": "#334155",
}
PALETTE = ["#38bdf8", "#818cf8", "#c084fc", "#f472b6", "#34d399", "#fb923c", "#facc15", "#4ade80"]


def _apply_dark_theme():
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor":  DARK["bg"],
        "axes.facecolor":    DARK["card"],
        "axes.edgecolor":    DARK["border"],
        "axes.labelcolor":   DARK["muted"],
        "xtick.color":       DARK["muted"],
        "ytick.color":       DARK["muted"],
        "text.color":        DARK["text"],
        "grid.color":        DARK["grid"],
        "grid.alpha":        0.6,
    })


def chart_price_distribution(cleaned_data, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()

        cats = [row["price_category"] for row in cleaned_data]
        order = ["Low (<$30)", "Mid ($30–$75)", "High ($75–$150)", "Premium (>$150)", "Unknown"]
        counts = {c: cats.count(c) for c in order if cats.count(c) > 0}

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(list(counts.keys()), list(counts.values()),
                      color=PALETTE[:len(counts)], width=0.55, edgecolor="none")
        ax.set_title("Price Category Distribution", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)
        ax.set_xlabel("Category", fontsize=11, labelpad=8)
        ax.set_ylabel("Jobs", fontsize=11, labelpad=8)
        ax.grid(axis="y", linestyle="--")
        ax.set_axisbelow(True)
        for bar, val in zip(bars, counts.values()):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(val), ha="center", va="bottom", color=DARK["text"], fontweight="bold", fontsize=12)

        plt.tight_layout()
        path = "outputs/f02_price_distribution.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
        plt.close()
        logs.append("Chart generated: Price Category Distribution")
        
        most_common = max(counts, key=counts.get) if counts else "Unknown"
        return {
            "path": path,
            "title": "Price Category Distribution",
            "insight": f"Most of the jobs in the dataset fall into the '{most_common}' pricing tier."
        }
    except Exception as e:
        logs.append(f"Chart 1 error: {e}")
        return None

def chart_top_skills(cleaned_data, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()

        all_skills = []
        for row in cleaned_data:
            for s in row.get("skills", "").split(","):
                s = s.strip()
                if s and s.lower() != "general":
                    all_skills.append(s)

        top = Counter(all_skills).most_common(8)
        if not top:
            return None

        labels = [t[0] for t in top][::-1]
        vals   = [t[1] for t in top][::-1]

        fig, ax = plt.subplots(figsize=(8, 5))
        colors = PALETTE[:len(labels)]
        bars = ax.barh(labels, vals, color=colors[::-1], edgecolor="none", height=0.6)
        ax.set_title("Top Skills in Demand", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)
        ax.set_xlabel("Frequency", fontsize=11, labelpad=8)
        ax.grid(axis="x", linestyle="--")
        ax.set_axisbelow(True)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", color=DARK["text"], fontweight="bold", fontsize=12)

        plt.tight_layout()
        path = "outputs/f02_top_skills.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
        plt.close()
        logs.append("Chart generated: Top Skills in Demand")
        return {
            "path": path,
            "title": "Top Skills in Demand",
            "insight": f"The most frequently requested skill currently is '{top[0][0]}' ({top[0][1]} mentions)."
        }
    except Exception as e:
        logs.append(f"Chart 2 error: {e}")
        return None

def chart_data_quality(report, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()

        items = [
            ("Clean Rows",       report["rows_after_cleaning"],   "#34d399"),
            ("Duplicates Rm'd",  report["duplicates_removed"],    "#f87171"),
            ("Missing Filled",   report["missing_values_filled"], "#fbbf24"),
        ]
        items = [(l, v, c) for l, v, c in items if v > 0]
        if not items:
            items = [("Clean Rows", report["rows_after_cleaning"], "#34d399")]

        labels = [i[0] for i in items]
        vals   = [i[1] for i in items]
        colors = [i[2] for i in items]

        fig, ax = plt.subplots(figsize=(6, 5))
        wedges, texts, autotexts = ax.pie(
            vals, labels=labels, colors=colors,
            autopct="%1.0f%%", startangle=90,
            textprops={"color": DARK["text"], "fontsize": 11},
            wedgeprops={"edgecolor": DARK["bg"], "linewidth": 2},
        )
        for at in autotexts:
            at.set_fontweight("bold")
        ax.set_title("Data Quality Breakdown", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)

        plt.tight_layout()
        path = "outputs/f02_data_quality.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
        plt.close()
        logs.append("Chart generated: Data Quality Breakdown")
        return {
            "path": path,
            "title": "Data Quality Breakdown",
            "insight": f"Data quality process resulted in {report['rows_after_cleaning']} clean rows with an overall quality score of {report['data_quality_score']}%."
        }
    except Exception as e:
        logs.append(f"Chart 3 error: {e}")
        return None

def chart_skills_per_job(cleaned_data, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()

        counts = [len([s for s in row.get("skills", "").split(",") if s.strip() and s.strip().lower() != "general"]) for row in cleaned_data]
        distribution = Counter(counts)
        
        labels = sorted(distribution.keys())
        vals = [distribution[l] for l in labels]

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar([str(l) for l in labels], vals, color="#818cf8", width=0.55, edgecolor="none")
        ax.set_title("Number of Skills Required Per Job", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)
        ax.set_xlabel("Number of Skills", fontsize=11, labelpad=8)
        ax.set_ylabel("Number of Jobs", fontsize=11, labelpad=8)
        ax.grid(axis="y", linestyle="--")
        ax.set_axisbelow(True)

        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(val), ha="center", va="bottom", color=DARK["text"], fontweight="bold", fontsize=12)

        plt.tight_layout()
        path = "outputs/f02_skills_per_job.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
        plt.close()
        logs.append("Chart generated: Skills Per Job")
        return {
            "path": path,
            "title": "Skills Complexity (Skills per Job)",
            "insight": "Shows job complexity by observing how many distinct skills an average gig asks for."
        }
    except Exception as e:
        logs.append(f"Chart 4 error: {e}")
        return None

def chart_description_length(cleaned_data, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()

        lengths = [len(row.get("description", "").split()) for row in cleaned_data if row.get("description")]
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(lengths, bins=10, color="#f472b6", edgecolor=DARK["bg"])
        ax.set_title("Job Description Length (Words)", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)
        ax.set_xlabel("Word Count", fontsize=11, labelpad=8)
        ax.set_ylabel("Frequency", fontsize=11, labelpad=8)
        ax.grid(axis="y", linestyle="--")
        ax.set_axisbelow(True)

        plt.tight_layout()
        path = "outputs/f02_desc_length.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
        plt.close()
        logs.append("Chart generated: Description Length")
        
        avg_len = sum(lengths) / len(lengths) if lengths else 0
        return {
            "path": path,
            "title": "Description Word Count",
            "insight": f"The average job description is {avg_len:.0f} words long. Longer descriptions usually indicate clearer client expectations."
        }
    except Exception as e:
        logs.append(f"Chart 5 error: {e}")
        return None

def chart_price_histogram(cleaned_data, logs):
    try:
        import matplotlib.pyplot as plt
        _apply_dark_theme()

        prices = [row["price_numeric"] for row in cleaned_data if row.get("price_numeric") is not None]
        
        fig, ax = plt.subplots(figsize=(8, 5))
        # Remove massive outliers for better visual if needed
        # We'll just plot it normally
        ax.hist(prices, bins=15, color="#facc15", edgecolor=DARK["bg"])
        ax.set_title("Numeric Price Value Distribution", fontsize=14, fontweight="bold", color=DARK["text"], pad=16)
        ax.set_xlabel("Estimated Price (Numeric Avg)", fontsize=11, labelpad=8)
        ax.set_ylabel("Number of Jobs", fontsize=11, labelpad=8)
        ax.grid(axis="y", linestyle="--")
        ax.set_axisbelow(True)

        plt.tight_layout()
        path = "outputs/f02_price_histogram.png"
        plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
        plt.close()
        logs.append("Chart generated: Price Histogram")
        return {
            "path": path,
            "title": "Exact Price Histogram",
            "insight": "Visualizes the strict numerical distribution of expected payouts, helping spot normal ranges versus high-paying outlier gigs."
        }
    except Exception as e:
        logs.append(f"Chart 6 error: {e}")
        return None

# ─── Main Feature ─────────────────────────────────────────────────────────────────

def run_cleaning_and_eda():
    logs = []

    # 1. Load
    raw_data, from_file = load_dataset()
    source_label = "raw_dataset.csv" if from_file else "fallback dataset"
    logs.append(f"Loaded {source_label} — {len(raw_data)} rows")
    original_rows = len(raw_data)

    # 2. Remove duplicates by title
    seen = set()
    dedup, duplicates_removed = [], 0
    for row in raw_data:
        key = row.get("title", "").strip().lower()
        if key not in seen:
            seen.add(key)
            dedup.append(row)
        else:
            duplicates_removed += 1
    logs.append(f"Duplicate removal: {duplicates_removed} entries dropped")

    # 3. Fill missing values
    missing_filled = 0
    for row in dedup:
        if not row.get("description", "").strip():
            row["description"] = "No description provided"
            missing_filled += 1
        if not row.get("skills", "").strip():
            row["skills"] = "General"
            missing_filled += 1
        if not row.get("price", "").strip():
            row["price"] = "Negotiable"
            missing_filled += 1
    logs.append(f"Missing value fill: {missing_filled} fields patched")

    # 4. Enrich with price meta
    for row in dedup:
        val = parse_price(row.get("price", ""))
        row["price_numeric"] = round(val, 2) if val is not None else None
        row["price_category"] = categorize_price(val)

    cleaned_data = dedup
    rows_after_cleaning = len(cleaned_data)
    logs.append(f"Cleaning complete — {rows_after_cleaning} rows retained")

    os.makedirs("outputs", exist_ok=True)

    cleaning_report = {
        "original_rows":        original_rows,
        "rows_after_cleaning":  rows_after_cleaning,
        "duplicates_removed":   duplicates_removed,
        "missing_values_filled": missing_filled,
        "data_quality_score":   round((rows_after_cleaning / original_rows) * 100, 1) if original_rows else 100,
    }

    # 5. Generate EDA charts
    charts_data = []
    try:
        import matplotlib  # noqa: F401
        for fn in [chart_price_distribution, chart_top_skills, chart_data_quality, chart_skills_per_job, chart_description_length, chart_price_histogram]:
            c_data = fn(cleaned_data, logs) if fn != chart_data_quality else fn(cleaning_report, logs)
            if c_data:
                charts_data.append(c_data)
    except ImportError:
        logs.append("matplotlib not installed — charts skipped")

    # 6. Save cleaned CSV
    cleaned_csv = "outputs/cleaned_dataset.csv"
    if cleaned_data:
        export_keys = [k for k in cleaned_data[0].keys() if k != "price_numeric"]
        with open(cleaned_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=export_keys, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(cleaned_data)
        logs.append(f"Cleaned dataset saved → {cleaned_csv}")

    return {
        "status":          "success",
        "message":         f"Cleaning & EDA complete. {rows_after_cleaning}/{original_rows} rows retained.",
        "cleaning_report": cleaning_report,
        "charts":          charts_data,
        "data":            [{k: v for k, v in r.items() if k != "price_numeric"} for r in cleaned_data],
        "csv_path":        cleaned_csv,
        "logs":            logs,
    }


if __name__ == "__main__":
    result = run_cleaning_and_eda()
    print(json.dumps(result))
