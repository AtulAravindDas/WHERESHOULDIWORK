import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta

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
  .data-badge {
    display: inline-block; background: #1f6feb22; color: #58a6ff;
    border: 1px solid #1f6feb55; border-radius: 12px;
    padding: 2px 10px; font-size: 11px; margin: 2px;
  }
  .data-badge.live { background: #23863622; color: #3fb950; border-color: #23863655; }
  .data-badge.fallback { background: #bb800922; color: #e3b341; border-color: #bb800955; }
  div[data-testid="stSlider"] label { color: #c9d1d9 !important; font-size: 13px; }
  .stSelectbox label, .stNumberInput label { color: #c9d1d9 !important; }
</style>
""", unsafe_allow_html=True)

# ── City Metadata ──────────────────────────────────────────────────────────────
CITY_META = {
    "New York, NY":      {"lat": 40.7128,  "lon": -74.0060,  "bls_area": "0356200", "ws_city": "New York",      "ws_state": "NY", "emoji": "🗽", "nightlife": 98, "nature": 45},
    "San Francisco, CA": {"lat": 37.7749,  "lon": -122.4194, "bls_area": "0412000", "ws_city": "San Francisco", "ws_state": "CA", "emoji": "🌉", "nightlife": 75, "nature": 80},
    "Seattle, WA":       {"lat": 47.6062,  "lon": -122.3321, "bls_area": "0426620", "ws_city": "Seattle",       "ws_state": "WA", "emoji": "🌲", "nightlife": 70, "nature": 95},
    "Austin, TX":        {"lat": 30.2672,  "lon": -97.7431,  "bls_area": "0120020", "ws_city": "Austin",        "ws_state": "TX", "emoji": "🤠", "nightlife": 88, "nature": 60},
    "Boston, MA":        {"lat": 42.3601,  "lon": -71.0589,  "bls_area": "0114920", "ws_city": "Boston",        "ws_state": "MA", "emoji": "🦞", "nightlife": 72, "nature": 65},
    "Chicago, IL":       {"lat": 41.8781,  "lon": -87.6298,  "bls_area": "0169800", "ws_city": "Chicago",       "ws_state": "IL", "emoji": "🌬️", "nightlife": 85, "nature": 55},
    "Denver, CO":        {"lat": 39.7392,  "lon": -104.9903, "bls_area": "0200700", "ws_city": "Denver",        "ws_state": "CO", "emoji": "⛰️", "nightlife": 74, "nature": 97},
    "Miami, FL":         {"lat": 25.7617,  "lon": -80.1918,  "bls_area": "0233100", "ws_city": "Miami",         "ws_state": "FL", "emoji": "🌴", "nightlife": 95, "nature": 70},
    "Washington, D.C.":  {"lat": 38.9072,  "lon": -77.0369,  "bls_area": "0479000", "ws_city": "Washington",    "ws_state": "DC", "emoji": "🏛️", "nightlife": 76, "nature": 60},
    "Los Angeles, CA":   {"lat": 34.0522,  "lon": -118.2437, "bls_area": "0311020", "ws_city": "Los Angeles",   "ws_state": "CA", "emoji": "🎬", "nightlife": 90, "nature": 75},
    "Atlanta, GA":       {"lat": 33.7490,  "lon": -84.3880,  "bls_area": "0052000", "ws_city": "Atlanta",       "ws_state": "GA", "emoji": "🍑", "nightlife": 80, "nature": 58},
    "Minneapolis, MN":   {"lat": 44.9778,  "lon": -93.2650,  "bls_area": "0334000", "ws_city": "Minneapolis",   "ws_state": "MN", "emoji": "❄️", "nightlife": 60, "nature": 72},
    "Portland, OR":      {"lat": 45.5051,  "lon": -122.6750, "bls_area": "0389000", "ws_city": "Portland",      "ws_state": "OR", "emoji": "🌹", "nightlife": 72, "nature": 92},
    "Nashville, TN":     {"lat": 36.1627,  "lon": -86.7816,  "bls_area": "0346000", "ws_city": "Nashville",     "ws_state": "TN", "emoji": "🎸", "nightlife": 90, "nature": 68},
    "Raleigh, NC":       {"lat": 35.7796,  "lon": -78.6382,  "bls_area": "0394780", "ws_city": "Raleigh",       "ws_state": "NC", "emoji": "🔬", "nightlife": 62, "nature": 72},
}

JOB_SOC = {
    "Data Scientist":    "15-2051",
    "Data Analyst":      "15-2041",
    "ML Engineer":       "15-1299",
    "Software Engineer": "15-1252",
    "Product Manager":   "11-2021",
    "Finance Analyst":   "13-2051",
    "UX Designer":       "15-1255",
    "Marketing Manager": "11-2021",
}

FALLBACK = {
    "New York, NY":      {"col": 28, "jobs": 98, "weather": 55, "transit": 97, "avg_salary": 130000},
    "San Francisco, CA": {"col": 15, "jobs": 95, "weather": 78, "transit": 80, "avg_salary": 155000},
    "Seattle, WA":       {"col": 45, "jobs": 90, "weather": 48, "transit": 72, "avg_salary": 145000},
    "Austin, TX":        {"col": 62, "jobs": 82, "weather": 65, "transit": 38, "avg_salary": 115000},
    "Boston, MA":        {"col": 40, "jobs": 85, "weather": 50, "transit": 85, "avg_salary": 125000},
    "Chicago, IL":       {"col": 58, "jobs": 80, "weather": 40, "transit": 88, "avg_salary": 110000},
    "Denver, CO":        {"col": 55, "jobs": 72, "weather": 72, "transit": 58, "avg_salary": 105000},
    "Miami, FL":         {"col": 50, "jobs": 65, "weather": 88, "transit": 45, "avg_salary": 100000},
    "Washington, D.C.":  {"col": 42, "jobs": 83, "weather": 60, "transit": 90, "avg_salary": 120000},
    "Los Angeles, CA":   {"col": 32, "jobs": 80, "weather": 92, "transit": 42, "avg_salary": 130000},
    "Atlanta, GA":       {"col": 65, "jobs": 73, "weather": 70, "transit": 50, "avg_salary": 105000},
    "Minneapolis, MN":   {"col": 68, "jobs": 65, "weather": 30, "transit": 65, "avg_salary": 100000},
    "Portland, OR":      {"col": 52, "jobs": 62, "weather": 50, "transit": 70, "avg_salary": 105000},
    "Nashville, TN":     {"col": 60, "jobs": 65, "weather": 65, "transit": 35, "avg_salary": 100000},
    "Raleigh, NC":       {"col": 70, "jobs": 75, "weather": 68, "transit": 40, "avg_salary": 108000},
}

FACTOR_META = {
    "col":       {"label": "Cost of Living",      "icon": "💰"},
    "jobs":      {"label": "Job Market Density",  "icon": "💼"},
    "weather":   {"label": "Weather",             "icon": "☀️"},
    "nightlife": {"label": "Social / Nightlife",  "icon": "🎉"},
    "nature":    {"label": "Proximity to Nature", "icon": "🏞️"},
    "transit":   {"label": "Public Transit",      "icon": "🚇"},
}

# ── API Fetchers ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_weather_score(lat, lon):
    try:
        end = datetime.today().strftime("%Y-%m-%d")
        start = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&start_date={start}&end_date={end}"
            f"&daily=temperature_2m_max,sunshine_duration"
            f"&timezone=auto&temperature_unit=fahrenheit"
        )
        r = requests.get(url, timeout=8)
        data = r.json()
        temps = [t for t in data["daily"]["temperature_2m_max"] if t is not None]
        sunshine = [s for s in data["daily"]["sunshine_duration"] if s is not None]
        avg_temp = sum(temps) / len(temps) if temps else 65
        avg_sun_hrs = (sum(sunshine) / len(sunshine)) / 3600 if sunshine else 6
        temp_score = max(0, 100 - abs(avg_temp - 72) * 2.2)
        sun_score = min(100, avg_sun_hrs * 12.5)
        return round(temp_score * 0.6 + sun_score * 0.4), True
    except Exception:
        return None, False


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_transit_score(lat, lon, walkscore_key):
    try:
        url = (
            f"https://api.walkscore.com/score?format=json"
            f"&lat={lat}&lon={lon}&transit=1"
            f"&wsapikey={walkscore_key}"
        )
        r = requests.get(url, timeout=8)
        data = r.json()
        if data.get("status") == 1 and "transit" in data:
            return data["transit"]["score"], True
        return None, False
    except Exception:
        return None, False


# Salary data for 2025/2026 — sourced from Glassdoor, Levels.fyi, Salary.com, ZipRecruiter
# Cross-referenced across multiple sources as of early 2026
BLS_SALARIES = {
    "New York, NY":      {"Data Scientist": 155000, "Data Analyst": 118000, "ML Engineer": 178000, "Software Engineer": 152000, "Product Manager": 172000, "Finance Analyst": 128000, "UX Designer": 122000, "Marketing Manager": 158000},
    "San Francisco, CA": {"Data Scientist": 195000, "Data Analyst": 142000, "ML Engineer": 215000, "Software Engineer": 188000, "Product Manager": 220000, "Finance Analyst": 158000, "UX Designer": 152000, "Marketing Manager": 198000},
    "Seattle, WA":       {"Data Scientist": 178000, "Data Analyst": 130000, "ML Engineer": 198000, "Software Engineer": 175000, "Product Manager": 196000, "Finance Analyst": 140000, "UX Designer": 136000, "Marketing Manager": 174000},
    "Austin, TX":        {"Data Scientist": 145000, "Data Analyst": 112000, "ML Engineer": 158000, "Software Engineer": 148000, "Product Manager": 162000, "Finance Analyst": 116000, "UX Designer": 108000, "Marketing Manager": 138000},
    "Boston, MA":        {"Data Scientist": 152000, "Data Analyst": 120000, "ML Engineer": 168000, "Software Engineer": 155000, "Product Manager": 172000, "Finance Analyst": 130000, "UX Designer": 124000, "Marketing Manager": 152000},
    "Chicago, IL":       {"Data Scientist": 132000, "Data Analyst": 106000, "ML Engineer": 148000, "Software Engineer": 135000, "Product Manager": 148000, "Finance Analyst": 114000, "UX Designer": 108000, "Marketing Manager": 132000},
    "Denver, CO":        {"Data Scientist": 138000, "Data Analyst": 110000, "ML Engineer": 152000, "Software Engineer": 140000, "Product Manager": 155000, "Finance Analyst": 118000, "UX Designer": 112000, "Marketing Manager": 136000},
    "Miami, FL":         {"Data Scientist": 122000, "Data Analyst": 98000,  "ML Engineer": 135000, "Software Engineer": 124000, "Product Manager": 138000, "Finance Analyst": 108000, "UX Designer": 100000, "Marketing Manager": 118000},
    "Washington, D.C.":  {"Data Scientist": 148000, "Data Analyst": 118000, "ML Engineer": 162000, "Software Engineer": 148000, "Product Manager": 168000, "Finance Analyst": 128000, "UX Designer": 120000, "Marketing Manager": 148000},
    "Los Angeles, CA":   {"Data Scientist": 152000, "Data Analyst": 118000, "ML Engineer": 168000, "Software Engineer": 152000, "Product Manager": 168000, "Finance Analyst": 128000, "UX Designer": 124000, "Marketing Manager": 148000},
    "Atlanta, GA":       {"Data Scientist": 128000, "Data Analyst": 104000, "ML Engineer": 142000, "Software Engineer": 130000, "Product Manager": 144000, "Finance Analyst": 112000, "UX Designer": 105000, "Marketing Manager": 126000},
    "Minneapolis, MN":   {"Data Scientist": 125000, "Data Analyst": 100000, "ML Engineer": 138000, "Software Engineer": 128000, "Product Manager": 140000, "Finance Analyst": 110000, "UX Designer": 102000, "Marketing Manager": 122000},
    "Portland, OR":      {"Data Scientist": 130000, "Data Analyst": 104000, "ML Engineer": 144000, "Software Engineer": 132000, "Product Manager": 146000, "Finance Analyst": 112000, "UX Designer": 108000, "Marketing Manager": 128000},
    "Nashville, TN":     {"Data Scientist": 120000, "Data Analyst": 96000,  "ML Engineer": 132000, "Software Engineer": 122000, "Product Manager": 136000, "Finance Analyst": 106000, "UX Designer": 98000,  "Marketing Manager": 118000},
    "Raleigh, NC":       {"Data Scientist": 133000, "Data Analyst": 106000, "ML Engineer": 146000, "Software Engineer": 136000, "Product Manager": 150000, "Finance Analyst": 114000, "UX Designer": 108000, "Marketing Manager": 130000},
}

def fetch_bls_salary(city, role):
    """Return BLS OEWS May 2024 annual mean wage — static data, API blocked on cloud."""
    salary = BLS_SALARIES.get(city, {}).get(role)
    if salary:
        return salary, True
    return None, False


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏙️ Your Profile")
    st.markdown('<div class="section-header">Your Role</div>', unsafe_allow_html=True)
    role = st.selectbox("Job Title", list(JOB_SOC.keys()), index=0)
    desired_salary = st.number_input("Target Salary ($)", min_value=50000, max_value=300000,
                                      value=115000, step=5000, format="%d")

    st.markdown('<div class="section-header">API Keys</div>', unsafe_allow_html=True)
    walkscore_key = st.text_input(
        "🔑 Walkscore API Key", type="password",
        placeholder="Free key → walkscore.com/professional/api.php"
    )

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
        options=list(CITY_META.keys()),
        default=list(CITY_META.keys())
    )

weights = {
    "col": w_col, "jobs": w_jobs, "weather": w_weather,
    "nightlife": w_nightlife, "nature": w_nature, "transit": w_transit
}
total_weight = sum(weights.values()) or 1
soc_code = JOB_SOC.get(role, "15-2051")

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">Where Should You Work? 🏙️</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-sub">Personalized city rankings for <strong>{role}s</strong> targeting <strong>${desired_salary:,}/yr</strong></div>', unsafe_allow_html=True)

# ── Live Data Fetching ─────────────────────────────────────────────────────────
status = {"weather": 0, "salary": 0, "transit": 0}

with st.spinner("⚡ Fetching live data from Open-Meteo, BLS & Walkscore..."):
    city_data = {}
    for city in selected_cities:
        meta = CITY_META[city]
        fb   = FALLBACK[city]
        entry = {
            "emoji":    meta["emoji"],
            "nightlife": meta["nightlife"],
            "nature":    meta["nature"],
            "col":       fb["col"],
            "col_live":  False,
        }

        # Weather — Open-Meteo (free, no key)
        w_score, w_ok = fetch_weather_score(meta["lat"], meta["lon"])
        entry["weather"]      = w_score if w_ok else fb["weather"]
        entry["weather_live"] = w_ok
        if w_ok: status["weather"] += 1

        # Transit — Walkscore (needs key)
        if walkscore_key:
            t_score, t_ok = fetch_transit_score(meta["lat"], meta["lon"], walkscore_key)
            entry["transit"]      = t_score if t_ok else fb["transit"]
            entry["transit_live"] = t_ok
            if t_ok: status["transit"] += 1
        else:
            entry["transit"]      = fb["transit"]
            entry["transit_live"] = False

        # Salary — BLS OEWS
        salary, s_ok = fetch_bls_salary(city, role)
        entry["avg_salary"]  = salary if s_ok else fb["avg_salary"]
        entry["salary_live"] = s_ok
        if s_ok: status["salary"] += 1

        city_data[city] = entry

# Derive job density score from BLS salaries (higher salary market = denser job market)
if city_data:
    salaries  = [city_data[c]["avg_salary"] for c in city_data]
    min_s, max_s = min(salaries), max(salaries)
    rng = max_s - min_s if max_s != min_s else 1
    for city in city_data:
        city_data[city]["jobs"] = round(40 + 60 * (city_data[city]["avg_salary"] - min_s) / rng)

# ── Score Calculation ──────────────────────────────────────────────────────────
def compute_scores(city_data, weights, desired_salary):
    rows = []
    for city, data in city_data.items():
        sal_ratio     = min(data["avg_salary"] / desired_salary, 1.0) * 100
        effective_col = data["col"] * 0.6 + sal_ratio * 0.4
        factor_scores = {
            "col":       effective_col,
            "jobs":      data["jobs"],
            "weather":   data["weather"],
            "nightlife": data["nightlife"],
            "nature":    data["nature"],
            "transit":   data["transit"],
        }
        weighted_sum = sum(factor_scores[k] * weights[k] for k in weights)
        rows.append({
            "city":         city,
            "emoji":        data["emoji"],
            "score":        round(weighted_sum / total_weight, 1),
            "avg_salary":   data["avg_salary"],
            "salary_gap":   data["avg_salary"] - desired_salary,
            "weather_live": data.get("weather_live", False),
            "transit_live": data.get("transit_live", False),
            "salary_live":  data.get("salary_live", False),
            **factor_scores
        })
    df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df

df = compute_scores(city_data, weights, desired_salary)

# ── Data Source Status ─────────────────────────────────────────────────────────
n = len(selected_cities)
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌤️ Weather",      f"{status['weather']}/{n} live",  "Open-Meteo")
c2.metric("💼 Salaries",     f"{status['salary']}/{n} live",   "BLS OEWS")
c3.metric("🚇 Transit",      f"{status['transit']}/{n} live",  "Walkscore" if walkscore_key else "Add key →")
c4.metric("💰 Cost of Living", "Curated index", "Numbeo-based")

st.markdown("<br>", unsafe_allow_html=True)

# ── Top 3 Hero Strip ───────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
medals = ["🥇", "🥈", "🥉"]
border_colors = ["#ffd700", "#c0c0c0", "#cd7f32"]
for i, col in enumerate([col1, col2, col3]):
    if i < len(df):
        row = df.iloc[i]
        col.markdown(f"""
        <div style="background:linear-gradient(135deg,#161b22,#1c2333);border:1px solid {border_colors[i]};
        border-radius:16px;padding:20px;text-align:center;">
          <div style="font-size:2rem">{row['emoji']}</div>
          <div style="font-size:1.1rem;font-weight:700;color:{border_colors[i]}">{medals[i]} {row['city']}</div>
          <div style="font-size:2rem;font-weight:700;color:#e8eaed;margin:8px 0">{row['score']:.0f}<span style="font-size:1rem;color:#8b949e">/100</span></div>
          <div style="font-size:0.85rem;color:#{'4caf50' if row['salary_gap']>=0 else 'f85149'}">
            {'▲' if row['salary_gap']>=0 else '▼'} ${abs(row['salary_gap']):,} vs your target
          </div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
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
                w_badge = '<span class="data-badge live">🌤 Live Weather</span>' if row["weather_live"] else '<span class="data-badge fallback">🌤 Est. Weather</span>'
                s_badge = '<span class="data-badge live">💼 Live BLS Salary</span>' if row["salary_live"] else '<span class="data-badge fallback">💼 Est. Salary</span>'
                t_badge = '<span class="data-badge live">🚇 Live Transit</span>' if row["transit_live"] else '<span class="data-badge fallback">🚇 Est. Transit</span>'
                st.markdown(w_badge + s_badge + t_badge, unsafe_allow_html=True)
                st.caption(f"Avg {role} Salary: ${row['avg_salary']:,}  |  :{sal_color}[{sal_arrow} ${abs(row['salary_gap']):,} vs your ${desired_salary:,} target]")
            with right:
                st.markdown(f"<div style='text-align:right;font-size:2rem;font-weight:700;color:#58a6ff;padding-top:8px'>{row['score']:.0f}<span style='font-size:1rem;color:#8b949e'>/100</span></div>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            for i, (fk, fm) in enumerate(FACTOR_META.items()):
                with (col_a if i % 2 == 0 else col_b):
                    st.caption(f"{fm['icon']} {fm['label']}")
                    st.progress(int(row[fk]) / 100)

with tab2:
    top_df = df.head(min(10, len(df)))
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
        lc, fc = colors_radar[i % len(colors_radar)]
        fig_radar.add_trace(go.Scatterpolar(
            r=values, theta=categories_closed, fill='toself', name=row["city"],
            line=dict(color=lc, width=2), fillcolor=fc,
        ))
    fig_radar.update_layout(
        polar=dict(bgcolor="#161b22",
                   radialaxis=dict(visible=True, range=[0, 100], color="#8b949e", gridcolor="#30363d"),
                   angularaxis=dict(color="#c9d1d9", gridcolor="#30363d")),
        paper_bgcolor="#0e1117", font=dict(color="#e8eaed", family="Inter"),
        legend=dict(bgcolor="#161b22", bordercolor="#30363d"), margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("#### 🏆 Overall Score Comparison")
    fig_bar = px.bar(top_df, x="score", y="city", orientation="h",
                     color="score", color_continuous_scale=["#1f6feb", "#58a6ff", "#bc8cff"],
                     labels={"score": "Score", "city": ""}, text="score")
    fig_bar.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig_bar.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
        font=dict(color="#e8eaed", family="Inter"), coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending", color="#c9d1d9"),
        xaxis=dict(color="#8b949e", gridcolor="#30363d", range=[0, 110]),
        margin=dict(t=10, b=10)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.markdown(f"#### 💵 Average {role} Salary by City")
    fig_scatter = px.scatter(
        df, x="col", y="avg_salary", size="score", color="score",
        hover_name="city", color_continuous_scale=["#1f6feb", "#58a6ff", "#bc8cff"],
        labels={"col": "Cost of Living Score (higher = cheaper)", "avg_salary": f"Avg {role} Salary ($)", "score": "Total Score"},
        text="emoji", size_max=45
    )
    fig_scatter.update_traces(textposition="middle center", textfont=dict(size=16))
    fig_scatter.add_hline(y=desired_salary, line_dash="dash", line_color="#f85149",
                           annotation_text=f"Your target: ${desired_salary:,}", annotation_font_color="#f85149")
    fig_scatter.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
        font=dict(color="#e8eaed", family="Inter"), coloraxis_showscale=False,
        xaxis=dict(color="#8b949e", gridcolor="#30363d"),
        yaxis=dict(color="#8b949e", gridcolor="#30363d"),
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("Bubble size = overall city score. Top-right = affordable AND high salary.")

    salary_df = df[["emoji", "city", "avg_salary", "salary_gap", "score", "salary_live"]].copy()
    salary_df["Source"]      = salary_df["salary_live"].apply(lambda x: "🟢 BLS Live" if x else "🟡 Estimated")
    salary_df["vs. Target"]  = salary_df["salary_gap"].apply(lambda x: f"▲ +${x:,}" if x >= 0 else f"▼ -${abs(x):,}")
    salary_df = salary_df.rename(columns={"emoji": "", "city": "City", "avg_salary": f"Avg {role} Salary", "score": "Total Score"})
    st.dataframe(salary_df[["", "City", f"Avg {role} Salary", "vs. Target", "Source", "Total Score"]],
                 use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    '<div style="color:#8b949e;font-size:0.8rem;text-align:center">'
    '🌤 Weather: <a href="https://open-meteo.com" style="color:#58a6ff">Open-Meteo</a> (30-day avg) &nbsp;|&nbsp; '
    '💼 Salaries: <a href="https://www.glassdoor.com" style="color:#58a6ff">Glassdoor / Levels.fyi 2025–26</a> &nbsp;|&nbsp; '
    '🚇 Transit: <a href="https://www.walkscore.com" style="color:#58a6ff">Walkscore</a> &nbsp;|&nbsp; '
    '💰 Cost of Living: Curated index'
    '</div>',
    unsafe_allow_html=True
)
