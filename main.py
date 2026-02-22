import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Where Should I Work?",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dark Mode CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .stApp { background-color: #0e1117; color: #e8eaed; }

  section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
  }

  .city-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 14px;
    transition: transform 0.2s;
  }
  .city-card:hover { transform: translateY(-2px); border-color: #58a6ff; }

  .rank-badge {
    display: inline-block;
    width: 36px; height: 36px;
    border-radius: 50%;
    text-align: center; line-height: 36px;
    font-weight: 700; font-size: 16px;
    margin-right: 12px;
  }
  .rank-1 { background: linear-gradient(135deg, #ffd700, #ffa500); color: #0e1117; }
  .rank-2 { background: linear-gradient(135deg, #c0c0c0, #a8a8a8); color: #0e1117; }
  .rank-3 { background: linear-gradient(135deg, #cd7f32, #b8682a); color: #fff; }
  .rank-other { background: #30363d; color: #e8eaed; }

  .score-pill {
    display: inline-block;
    background: #1f6feb;
    color: white;
    border-radius: 20px;
    padding: 4px 14px;
    font-weight: 600;
    font-size: 14px;
    float: right;
  }

  .factor-bar-label { font-size: 12px; color: #8b949e; margin-bottom: 2px; }
  .hero-title {
    font-size: 2.8rem; font-weight: 700;
    background: linear-gradient(135deg, #58a6ff, #bc8cff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
  }
  .hero-sub { color: #8b949e; font-size: 1.05rem; margin-bottom: 32px; }
  .section-header {
    color: #58a6ff; font-size: 0.75rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 8px; margin-top: 20px;
  }
  div[data-testid="stSlider"] label { color: #c9d1d9 !important; font-size: 13px; }
  .stSelectbox label, .stNumberInput label { color: #c9d1d9 !important; }
</style>
""", unsafe_allow_html=True)

# ── City Data ─────────────────────────────────────────────────────────────────
# Scores are 0–100 (higher = better for job seeker)
CITIES = {
    "New York, NY":        {"col": 28, "jobs": 98, "weather": 55, "nightlife": 98, "nature": 45, "transit": 97, "avg_salary_ds": 130000, "emoji": "🗽"},
    "San Francisco, CA":   {"col": 15, "jobs": 95, "weather": 78, "nightlife": 75, "nature": 80, "transit": 80, "avg_salary_ds": 155000, "emoji": "🌉"},
    "Seattle, WA":         {"col": 45, "jobs": 90, "weather": 48, "nightlife": 70, "nature": 95, "transit": 72, "avg_salary_ds": 145000, "emoji": "🌲"},
    "Austin, TX":          {"col": 62, "jobs": 82, "weather": 65, "nightlife": 88, "nature": 60, "transit": 38, "avg_salary_ds": 115000, "emoji": "🤠"},
    "Boston, MA":          {"col": 40, "jobs": 85, "weather": 50, "nightlife": 72, "nature": 65, "transit": 85, "avg_salary_ds": 125000, "emoji": "🦞"},
    "Chicago, IL":         {"col": 58, "jobs": 80, "weather": 40, "nightlife": 85, "nature": 55, "transit": 88, "avg_salary_ds": 110000, "emoji": "🌬️"},
    "Denver, CO":          {"col": 55, "jobs": 72, "weather": 72, "nightlife": 74, "nature": 97, "transit": 58, "avg_salary_ds": 105000, "emoji": "⛰️"},
    "Miami, FL":           {"col": 50, "jobs": 65, "weather": 88, "nightlife": 95, "nature": 70, "transit": 45, "avg_salary_ds": 100000, "emoji": "🌴"},
    "Washington, D.C.":    {"col": 42, "jobs": 83, "weather": 60, "nightlife": 76, "nature": 60, "transit": 90, "avg_salary_ds": 120000, "emoji": "🏛️"},
    "Los Angeles, CA":     {"col": 32, "jobs": 80, "weather": 92, "nightlife": 90, "nature": 75, "transit": 42, "avg_salary_ds": 130000, "emoji": "🎬"},
    "Atlanta, GA":         {"col": 65, "jobs": 73, "weather": 70, "nightlife": 80, "nature": 58, "transit": 50, "avg_salary_ds": 105000, "emoji": "🍑"},
    "Minneapolis, MN":     {"col": 68, "jobs": 65, "weather": 30, "nightlife": 60, "nature": 72, "transit": 65, "avg_salary_ds": 100000, "emoji": "❄️"},
    "Portland, OR":        {"col": 52, "jobs": 62, "weather": 50, "nightlife": 72, "nature": 92, "transit": 70, "avg_salary_ds": 105000, "emoji": "🌹"},
    "Nashville, TN":       {"col": 60, "jobs": 65, "weather": 65, "nightlife": 90, "nature": 68, "transit": 35, "avg_salary_ds": 100000, "emoji": "🎸"},
    "Raleigh, NC":         {"col": 70, "jobs": 75, "weather": 68, "nightlife": 62, "nature": 72, "transit": 40, "avg_salary_ds": 108000, "emoji": "🔬"},
}

FACTOR_META = {
    "col":       {"label": "Cost of Living",       "icon": "💰", "key": "cost_of_living"},
    "jobs":      {"label": "Job Market Density",   "icon": "💼", "key": "job_market"},
    "weather":   {"label": "Weather",              "icon": "☀️", "key": "weather"},
    "nightlife": {"label": "Social / Nightlife",   "icon": "🎉", "key": "nightlife"},
    "nature":    {"label": "Proximity to Nature",  "icon": "🏞️", "key": "nature"},
    "transit":   {"label": "Public Transit",       "icon": "🚇", "key": "transit"},
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏙️ Your Profile")
    st.markdown('<div class="section-header">Your Role</div>', unsafe_allow_html=True)
    role = st.selectbox("Job Title", [
        "Data Scientist", "Data Analyst", "ML Engineer",
        "Software Engineer", "Product Manager", "Finance Analyst",
        "UX Designer", "Marketing Manager"
    ], index=0)

    desired_salary = st.number_input("Target Salary ($)", min_value=50000, max_value=300000,
                                      value=115000, step=5000, format="%d")

    st.markdown('<div class="section-header">Factor Weights</div>', unsafe_allow_html=True)
    st.caption("Slide to prioritize what matters most to you")

    w_col       = st.slider("💰 Cost of Living",      0, 10, 8)
    w_jobs      = st.slider("💼 Job Market Density",  0, 10, 9)
    w_weather   = st.slider("☀️ Weather",              0, 10, 5)
    w_nightlife = st.slider("🎉 Social / Nightlife",  0, 10, 6)
    w_nature    = st.slider("🏞️ Proximity to Nature", 0, 10, 5)
    w_transit   = st.slider("🚇 Public Transit",      0, 10, 7)

    st.markdown('<div class="section-header">Filter Cities</div>', unsafe_allow_html=True)
    selected_cities = st.multiselect(
        "Include cities",
        options=list(CITIES.keys()),
        default=list(CITIES.keys())
    )

weights = {
    "col": w_col, "jobs": w_jobs, "weather": w_weather,
    "nightlife": w_nightlife, "nature": w_nature, "transit": w_transit
}
total_weight = sum(weights.values()) or 1

# ── Score Calculation ─────────────────────────────────────────────────────────
def compute_scores(cities, weights, desired_salary):
    rows = []
    for city, data in cities.items():
        if city not in selected_cities:
            continue
        # Salary affordability: how much of desired salary is met (capped at 100)
        sal_ratio = min(data["avg_salary_ds"] / desired_salary, 1.0) * 100
        # Blend salary ratio into cost of living score
        effective_col = (data["col"] * 0.6 + sal_ratio * 0.4)

        factor_scores = {
            "col":       effective_col,
            "jobs":      data["jobs"],
            "weather":   data["weather"],
            "nightlife": data["nightlife"],
            "nature":    data["nature"],
            "transit":   data["transit"],
        }
        weighted_sum = sum(factor_scores[k] * weights[k] for k in weights)
        final_score = weighted_sum / total_weight

        rows.append({
            "city": city,
            "emoji": data["emoji"],
            "score": round(final_score, 1),
            "avg_salary": data["avg_salary_ds"],
            "salary_gap": data["avg_salary_ds"] - desired_salary,
            **factor_scores
        })

    df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df

df = compute_scores(CITIES, weights, desired_salary)

# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Where Should You Work? 🏙️</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-sub">Personalized city rankings for <strong>{role}s</strong> targeting <strong>${desired_salary:,}/yr</strong></div>', unsafe_allow_html=True)

# Top 3 highlight strip
col1, col2, col3 = st.columns(3)
medals = ["🥇", "🥈", "🥉"]
colors = ["#ffd700", "#c0c0c0", "#cd7f32"]
for i, col in enumerate([col1, col2, col3]):
    if i < len(df):
        row = df.iloc[i]
        col.markdown(f"""
        <div style="background:linear-gradient(135deg,#161b22,#1c2333);border:1px solid {colors[i]};
        border-radius:16px;padding:20px;text-align:center;">
          <div style="font-size:2rem">{row['emoji']}</div>
          <div style="font-size:1.1rem;font-weight:700;color:{colors[i]}">{medals[i]} {row['city']}</div>
          <div style="font-size:2rem;font-weight:700;color:#e8eaed;margin:8px 0">{row['score']:.0f}<span style="font-size:1rem;color:#8b949e">/100</span></div>
          <div style="font-size:0.85rem;color:#{'4caf50' if row['salary_gap']>=0 else 'f85149'}">
            {'▲' if row['salary_gap']>=0 else '▼'} ${abs(row['salary_gap']):,} vs your target
          </div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Full Rankings", "📊 Factor Breakdown", "🗺️ Salary Map"])

with tab1:
    for _, row in df.iterrows():
        rank = int(row["rank"])
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        sal_arrow = "▲" if row["salary_gap"] >= 0 else "▼"
        sal_color = "green" if row["salary_gap"] >= 0 else "red"

        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"### {medal} {row['emoji']} {row['city']}")
                st.caption(f"Avg DS Salary: ${row['avg_salary']:,}  |  :{sal_color}[{sal_arrow} ${abs(row['salary_gap']):,} vs your ${desired_salary:,} target]")
            with right:
                st.markdown(f"<div style='text-align:right;font-size:2rem;font-weight:700;color:#58a6ff;padding-top:8px'>{row['score']:.0f}<span style='font-size:1rem;color:#8b949e'>/100</span></div>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            factor_list = list(FACTOR_META.items())
            for i, (fk, fm) in enumerate(factor_list):
                pct = int(row[fk])
                target_col = col_a if i % 2 == 0 else col_b
                with target_col:
                    st.caption(f"{fm['icon']} {fm['label']}")
                    st.progress(pct / 100)

with tab2:
    top_n = min(10, len(df))
    top_df = df.head(top_n)

    # Radar chart for top 5
    st.markdown("#### 🕸️ Factor Radar — Top 5 Cities")
    fig_radar = go.Figure()
    categories = [FACTOR_META[k]["label"] for k in FACTOR_META]
    categories_closed = categories + [categories[0]]

    colors_radar = [
        ("rgba(88,166,255,0.8)",  "rgba(88,166,255,0.15)"),
        ("rgba(188,140,255,0.8)", "rgba(188,140,255,0.15)"),
        ("rgba(76,175,80,0.8)",   "rgba(76,175,80,0.15)"),
        ("rgba(255,215,0,0.8)",   "rgba(255,215,0,0.15)"),
        ("rgba(248,81,73,0.8)",   "rgba(248,81,73,0.15)"),
    ]
    for i, (_, row) in enumerate(top_df.head(5).iterrows()):
        values = [row[k] for k in FACTOR_META] + [row[list(FACTOR_META.keys())[0]]]
        line_color, fill_color = colors_radar[i % len(colors_radar)]
        fig_radar.add_trace(go.Scatterpolar(
            r=values, theta=categories_closed,
            fill='toself', name=row["city"],
            line=dict(color=line_color, width=2),
            fillcolor=fill_color,
        ))

    fig_radar.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(visible=True, range=[0, 100], color="#8b949e", gridcolor="#30363d"),
            angularaxis=dict(color="#c9d1d9", gridcolor="#30363d")
        ),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#e8eaed", family="Inter"),
        legend=dict(bgcolor="#161b22", bordercolor="#30363d"),
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Bar chart of overall scores
    st.markdown("#### 🏆 Overall Score Comparison")
    fig_bar = px.bar(
        top_df, x="score", y="city", orientation="h",
        color="score", color_continuous_scale=["#1f6feb", "#58a6ff", "#bc8cff"],
        labels={"score": "Score", "city": ""},
        text="score"
    )
    fig_bar.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig_bar.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
        font=dict(color="#e8eaed", family="Inter"),
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending", color="#c9d1d9"),
        xaxis=dict(color="#8b949e", gridcolor="#30363d", range=[0, 110]),
        margin=dict(t=10, b=10)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.markdown("#### 💵 Average Data Science Salary by City")

    # Salary vs cost of living scatter
    fig_scatter = px.scatter(
        df,
        x="col", y="avg_salary",
        size="score", color="score",
        hover_name="city",
        color_continuous_scale=["#1f6feb", "#58a6ff", "#bc8cff"],
        labels={"col": "Cost of Living Score (higher = cheaper)", "avg_salary": "Avg DS Salary ($)", "score": "Total Score"},
        text="emoji",
        size_max=45
    )
    fig_scatter.update_traces(textposition="middle center", textfont=dict(size=16))
    fig_scatter.add_hline(y=desired_salary, line_dash="dash", line_color="#f85149",
                           annotation_text=f"Your target: ${desired_salary:,}", annotation_font_color="#f85149")
    fig_scatter.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
        font=dict(color="#e8eaed", family="Inter"),
        coloraxis_showscale=False,
        xaxis=dict(color="#8b949e", gridcolor="#30363d"),
        yaxis=dict(color="#8b949e", gridcolor="#30363d"),
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("Bubble size = overall city score. Cities in the top-right are best value: affordable AND high salaries.")

    # Salary table
    st.markdown("#### 📊 Salary vs. Your Target")
    salary_df = df[["emoji", "city", "avg_salary", "salary_gap", "score"]].copy()
    salary_df["vs. Target"] = salary_df["salary_gap"].apply(
        lambda x: f"▲ +${x:,}" if x >= 0 else f"▼ -${abs(x):,}"
    )
    salary_df = salary_df.rename(columns={
        "emoji": "", "city": "City", "avg_salary": "Avg DS Salary", "score": "Total Score"
    })
    st.dataframe(
        salary_df[["", "City", "Avg DS Salary", "vs. Target", "Total Score"]],
        use_container_width=True, hide_index=True
    )

st.markdown("---")
st.markdown('<div style="color:#8b949e;font-size:0.8rem;text-align:center">Data is curated for illustrative purposes. Salary figures reflect approximate data science market rates. Adjust weights in the sidebar to match your priorities.</div>', unsafe_allow_html=True)
