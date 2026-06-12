import os
import requests
from datetime import datetime
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components
import pandas as pd

# 1. Page Configurations & Branding Styles
st.set_page_config(
    page_title="King Family World Cup Sweepstake", 
    page_icon="⚽", 
    layout="wide"
)

# Run page auto-refresh every 3 minutes
st_autorefresh(interval=180 * 1000, key="datarefresh")

if "revealed_scores" not in st.session_state:
    st.session_state.revealed_scores = set()

# CSS Injection
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300..900;1,300..900&display=swap');
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #FAFAFA !important; color: #333333 !important; font-family: 'Figtree', sans-serif !important; }
        p, span, div, label, small, td, th, b { color: #333333; font-family: 'Figtree', sans-serif !important; }
        h1, h2, h3 { color: #006847 !important; font-family: 'Figtree', sans-serif !important; font-weight: 800 !important; }
        .table-responsive-wrapper { width: 100%; overflow-x: auto; margin-bottom: 8px !important; }
        .custom-dashboard-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; white-space: nowrap; }
        .custom-dashboard-table th { background-color: #FAFAFA !important; color: #333333 !important; font-weight: 700 !important; padding: 6px 6px !important; border-bottom: 2px solid #006847; }
        .custom-dashboard-table td { padding: 6px 6px !important; border-bottom: 1px solid #EAEAEA; vertical-align: middle; background-color: #FFFFFF !important; color: #333333 !important; }
        .flag-img { vertical-align: middle; margin: 0px 4px; width: 20px !important; height: 14px !important; object-fit: cover !important; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# Configurations
API_TOKEN = st.secrets.get("FOOTBALL_API_TOKEN", os.environ.get("FOOTBALL_API_TOKEN", "placeholder"))
COMPETITION_CODE = "WC"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_TOKEN}

SWEEPSTAKE_MAPPING = {
    "Mexico": "Izzy", "South Africa": "Ellis", "Canada": "Ella", "Switzerland": "Barbara",
    "Argentina": "Izzy", "France": "Ella", "Brazil": "Ellis", "Spain": "Jeff",
    "Bosnia-Herzegovina": "Izzy", "Czechia": "Jeff", "Qatar": "Ella", "Morocco": "Ellis",
    "Haiti": "Jeff", "Turkey": "Sam", "Paraguay": "Sam", "Germany": "Jeff",
    "Curaçao": "Barbara", "Ecuador": "Ellis", "Japan": "Jeff", "Belgium": "Izzy",
    "Egypt": "Izzy", "Tunisia": "Sam", "Netherlands": "Barbara", "Ivory Coast": "Sam",
    "Australia": "Ellis", "Cape Verde Islands": "Ella", "Uruguay": "Barbara", "Sweden": "Ellis",
    "Saudi Arabia": "Izzy", "Scotland": "Ella", "United States": "Izzy", "Senegal": "Jeff",
    "New Zealand": "Sam", "Iran": "Ella", "Iraq": "Barbara", "Norway": "Barbara",
    "Algeria": "Barbara", "Austria": "Ella", "Jordan": "Sam", "Congo DR": "Jeff",
    "Portugal": "Sam", "Uzbekistan": "Jeff", "Colombia": "Ella", "England": "Barbara",
    "Panama": "Izzy", "Ghana": "Ellis", "Croatia": "Sam", "South Korea": "Ellis",
}

EXPECTED_RANKINGS = {
    "France": 1, "Spain": 2, "Argentina": 3, "England": 4, "Portugal": 5, "Brazil": 6,
    "Netherlands": 7, "Morocco": 8, "Belgium": 9, "Germany": 10, "Croatia": 11, "Colombia": 12,
    "Senegal": 13, "Mexico": 14, "United States": 15, "Uruguay": 16, "Japan": 17, "Switzerland": 18,
    "Iran": 19, "Turkey": 20, "Ecuador": 21, "Austria": 22, "South Korea": 23, "Australia": 24,
    "Algeria": 25, "Egypt": 26, "Canada": 27, "Norway": 28, "Panama": 29, "Ivory Coast": 30,
    "Sweden": 31, "Paraguay": 32, "Czechia": 33, "Scotland": 34, "Tunisia": 35, "Congo DR": 36, 
    "DR Congo": 36, "Uzbekistan": 37, "Qatar": 38, "Iraq": 39, "South Africa": 40, "Saudi Arabia": 41,
    "Jordan": 42, "Bosnia-Herzegovina": 43, "Cape Verde Islands": 44, "Cape Verde": 44, "Ghana": 45, 
    "Curaçao": 46, "Haiti": 47, "New Zealand": 48
}

@st.cache_data(ttl=86400)
def get_cached_team_crests():
    crests = {}
    if API_TOKEN == "placeholder": return crests
    try:
        res = requests.get(f"{BASE_URL}/competitions/{COMPETITION_CODE}/teams", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            for t in res.json().get("teams", []):
                name, crest_url = t.get("name"), t.get("crest")
                if name and crest_url:
                    crests[name] = crest_url
                    if name == "DR Congo": crests["Congo DR"] = crest_url
                    if name == "Congo DR": crests["DR Congo"] = crest_url
                    if name == "Cape Verde": crests["Cape Verde Islands"] = crest_url
    except Exception: pass
    return crests

CACHED_CRESTS = get_cached_team_crests()

def get_flag_html(team_name, extra_class="flag-img"):
    crest_url = CACHED_CRESTS.get(team_name)
    return f'<img src="{crest_url}" class="{extra_class}" alt="{team_name}">' if crest_url else ''

@st.cache_data(ttl=120)  
def fetch_football_data():
    if API_TOKEN == "placeholder": return [], []
    try:
        s = requests.get(f"{BASE_URL}/competitions/{COMPETITION_CODE}/standings", headers=HEADERS, timeout=10)
        m = requests.get(f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches", headers=HEADERS, timeout=10)
        return m.json().get("matches", []), s.json().get("standings", [])
    except: return [], []

all_matches, standings_list = fetch_football_data()

# Process Leaderboard
master_flat_leaderboard = []
for group in standings_list:
    for row in group.get("table", []):
        t_info = row.get("team", {})
        master_flat_leaderboard.append({
            "name": t_info.get("name", "Unknown"),
            "played": row.get("playedGames", 0),
            "won": row.get("won", 0),
            "gd": row.get("goalDifference", 0),
            "gf": row.get("goalsFor", 0),
            "pts": row.get("points", 0),
        })

if master_flat_leaderboard:
    master_flat_leaderboard.sort(key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"], x["name"]))
    for idx, team_item in enumerate(master_flat_leaderboard, start=1):
        team_item["actual_rank"] = idx
        team_item["expected_rank"] = EXPECTED_RANKINGS.get(team_item["name"], 25)
        team_item["overperformance"] = team_item["expected_rank"] - idx

# App UI
st.title("🏆 King Family World Cup Sweepstake")

# Overperformance Table
st.markdown("<hr style='margin:30px 0px 20px 0px; border-top: 3px solid #006847;'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>📈 Overperformance table</h2>", unsafe_allow_html=True)
if master_flat_leaderboard:
    master_flat_leaderboard.sort(key=lambda x: (-x["overperformance"], x["actual_rank"]))
    master_table_html = """
    <div class="table-responsive-wrapper">
        <table class="custom-dashboard-table" style="width:100%;">
            <thead>
                <tr><th>Pos</th><th>Team</th><th style="text-align:center;">Rank</th><th style="text-align:center;">Actual</th><th style="text-align:center;">Pts</th><th style="text-align:right;">Score</th></tr>
            </thead>
            <tbody>
    """
    for display_idx, team_row in enumerate(master_flat_leaderboard, start=1):
        owner = SWEEPSTAKE_MAPPING.get(team_row["name"], "Unassigned")
        flag_html = get_flag_html(team_row["name"])
        
        # Emoji Logic
        if display_idx == 1:
            pos_str = "1 🚀"
        elif display_idx == 48:
            pos_str = "48 💩"
        else:
            pos_str = str(display_idx)
            
        op_val = team_row["overperformance"]
        op_formatted = f"+{op_val}" if op_val > 0 else str(op_val)
        score_color = "#107C41" if op_val > 0 else ("#A80000" if op_val < 0 else "#333333")
        
        master_table_html += f"""<tr>
            <td><b>{pos_str}</b></td>
            <td>{flag_html} <b>{team_row['name']}</b> <span style='font-size:11px; color:#666;'>({owner})</span></td>
            <td style='text-align:center;'>#{team_row['expected_rank']}</td>
            <td style='text-align:center;'>#{team_row['actual_rank']}</td>
            <td style='text-align:center;'><b>{team_row['pts']}</b></td>
            <td style='text-align:right; font-weight:800; color:{score_color};'>{op_formatted}</td>
        </tr>"""
    master_table_html += "</tbody></table></div>"
    st.markdown(master_table_html, unsafe_allow_html=True)
