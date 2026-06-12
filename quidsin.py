import os
import requests
from datetime import datetime
import pytz
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# 1. Page Configurations & Branding Styles
st.set_page_config(
    page_title="King Family World Cup Sweepstake", 
    page_icon="⚽", 
    layout="wide"
)

# Run page auto-refresh every 3 minutes to keep live scores syncing
st_autorefresh(interval=180 * 1000, key="datarefresh")

# Global baseline dashboard system architecture style tokens
GLOBAL_STYLE_TOKENS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght=0,300..900;1,300..900&display=swap');
    
    body, html {
        background-color: #FAFAFA !important;
        color: #333333 !important;
        font-family: 'Figtree', sans-serif !important;
        margin: 0;
        padding: 0;
    }
    
    p, span, div, label, small, td, th, b {
        color: #333333;
        font-family: 'Figtree', sans-serif !important;
    }

    /* --- MATCH BANNER LAYOUT --- */
    .match-banner-wrapper {
        width: 100%;
        margin: 0px;
        box-sizing: border-box;
    }

    .match-banner-container {
        width: 100%;
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
        overflow: hidden;
        font-family: 'Figtree', sans-serif !important;
        text-align: center;
        border: 1px solid #DDDDDD;
        background-color: #FFFFFF;
    }

    .banner-top-pane {
        background-color: #006847;
        padding: 8px 15px;
    }

    .next-match-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        background: rgba(255, 255, 255, 0.15);
        padding: 8px 15px;
        border-radius: 6px;
        display: inline-block;
    }

    .inplay-top-pane {
        background-color: #8B0000;
        padding: 8px 15px;
    }
    
    .result-top-pane {
        background-color: #444444;
        padding: 6px 10px;
    }

    .matchup-split-screen {
        display: flex;
        position: relative;
        align-items: center;
        height: 75px;
        width: 100%;
    }

    .team-panel {
        width: 50%;
        display: flex;
        align-items: center;
        padding: 10px 25px;
        box-sizing: border-box;
        height: 100%;
        overflow: hidden;
    }
    
    .home-panel {
        justify-content: flex-end;
        padding-right: 50px;
        border-right: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .away-panel {
        justify-content: flex-start;
        padding-left: 50px;
    }

    .team-panel-text {
        color: #FFFFFF !important;
        font-size: 16px;
        font-weight: 800 !important;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        white-space: nowrap;
    }

    .team-panel-text span {
        font-size: 12px;
        font-weight: 400 !important;
        opacity: 0.95;
        color: #FFFFFF !important;
        margin: 0 6px;
    }

    .vs-marker-bubble, .score-bubble, .score-reveal-wrapper {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        z-index: 10;
        white-space: nowrap;
    }

    .vs-marker-bubble {
        background-color: #111111;
        color: #FFFFFF !important;
        font-size: 12px;
        font-weight: 900 !important;
        padding: 5px 9px;
        border-radius: 50%;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    .score-bubble {
        background-color: #444444;
        color: #FFFFFF !important;
        font-size: 16px;
        font-weight: 900 !important;
        padding: 6px 14px;
        border-radius: 6px;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    .reveal-toggle-input {
        display: none !important;
    }

    .score-reveal-label {
        background-color: #111111;
        color: #FFFFFF !important;
        font-size: 11px !important;
        font-weight: 900 !important;
        padding: 6px 12px !important;
        border-radius: 6px;
        cursor: pointer;
        border: 2px solid #FFFFFF;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        user-select: none;
    }

    .reveal-toggle-input:checked ~ .score-reveal-label {
        display: none !important;
    }

    .reveal-toggle-input:checked ~ .score-bubble {
        display: block !important;
    }

    .banner-bottom-time {
        background-color: #006847;
        padding: 8px 15px;
        font-size: 12px;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }

    .inplay-bottom-bar {
        background-color: #8B0000;
        padding: 8px 15px;
        font-size: 12px;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    
    .result-bottom-bar {
        background-color: #444444;
        padding: 8px 15px;
        font-size: 12px;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    
    .highlights-btn {
        background-color: #444444 !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        text-decoration: none !important;
        padding: 6px 10px;
        border-radius: 2px;
        display: inline-flex !important;
        align-items: center;
        gap: 2px;
        box-shadow: 0 1px 2px rgba(255,0,0,0.2);
    }

    .highlights-btn:hover {
        background-color: #CC0000 !important;
        color: #FFFFFF !important;
    }
    
    .banner-flag {
        width: 28px !important;
        height: 19px !important;
        object-fit: cover !important;
        border-radius: 2px;
        border: 1px solid rgba(255,255,255,0.3);
        display: inline-block;
        margin: 0 8px;
        vertical-align: middle;
    }

    /* --- MOBILE OPTIMIZATION OVERRIDES --- */
    @media (max-width: 768px) {
        .team-panel {
            padding: 10px 8px !important;
        }
        .home-panel {
            padding-right: 32px !important;
        }
        .away-panel {
            padding-left: 32px !important;
        }
        .team-panel-text {
            font-size: 11px !important;
        }
        .team-panel-text span {
            font-size: 9px !important;
            margin: 0 2px !important;
        }
        .banner-flag {
            width: 20px !important;
            height: 14px !important;
            margin: 0 4px !important;
        }
        .score-bubble, .vs-marker-bubble {
            font-size: 12px !important;
            padding: 4px 10px !important;
        }
        .score-reveal-label {
            font-size: 9px !important;
            padding: 4px 8px !important;
        }
    }
</style>
"""

st.markdown(GLOBAL_STYLE_TOKENS, unsafe_allow_html=True)
st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #FAFAFA !important;
        }
        h1, h2, h3 {
            color: #006847 !important;
            font-family: 'Figtree', sans-serif !important;
            font-weight: 800 !important;
        }
        .title-area h1 { margin: 0px !important; font-size: 28px; font-weight: 900 !important; }
        .title-area p { margin: 4px 0px 0px 0px !important; color: #555555 !important; font-weight: 700 !important; font-size: 16px; }
        .stat-banner-box { background: #FFFFFF !important; padding: 12px 20px; border-radius: 8px; border: 2px solid #EAEAEA; display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
        .stat-banner-box medium { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 800 !important; color: #006847 !important; }
        .stat-banner-box span { font-size: 14px; font-weight: 800 !important; text-align: right; color: #333333 !important; }
        .group-row-spacer { margin-bottom: 15px !important; }
        .table-responsive-wrapper { width: 100%; overflow-x: auto; margin-bottom: 8px !important; }
        .custom-dashboard-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; white-space: nowrap; }
        .custom-dashboard-table th { background-color: #FAFAFA !important; color: #333333 !important; font-weight: 700 !important; padding: 6px 6px !important; border-bottom: 2px solid #006847; }
        .custom-dashboard-table td { padding: 6px 6px !important; border-bottom: 1px solid #EAEAEA; vertical-align: middle; background-color: #FFFFFF !important; color: #333333 !important; }
        .compact-sweep-container {
            background: #FFFFFF;
            border: 1px solid #DDDDDD;
            border-radius: 10px;
            padding: 8px 12px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
            max-height: 100px;
            overflow: hidden;
        }
        .compact-teams-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 4px;
        }
        .compact-team-item {
            background: #FAFAFA;
            border: 1px solid #EAEAEA;
            font-size: 11px;
            font-weight: 700;
            color: #333333;
            padding: 2px 6px;
            border-radius: 5px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & API Settings - Securely Fetch Token from Secrets
API_TOKEN = st.secrets.get("FOOTBALL_API_TOKEN", os.environ.get("FOOTBALL_API_TOKEN", "placeholder"))
COMPETITION_CODE = "WC"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_TOKEN}

SWEEPSTAKE_MAPPING = {
    "Mexico": "Izzy", "South Africa": "Ellis", "Canada": "Ella", "Switzerland": "Barbara",
    "Argentina": "Izzy", "France": "Ella", "Brazil": "Ellis", "Spain": "Jeff",
    "Bosnia and Herzegovina": "Izzy", "Bosnia-Herzegovina": "Izzy", "Czechia": "Jeff", "Qatar": "Ella", "Morocco": "Ellis",
    "Haiti": "Jeff", "Turkey": "Sam", "Paraguay": "Sam", "Germany": "Jeff",
    "Curaçao": "Barbara", "Ecuador": "Ellis", "Japan": "Jeff", "Belgium": "Izzy",
    "Egypt": "Izzy", "Tunisia": "Sam", "Netherlands": "Barbara", "Ivory Coast": "Sam",
    "Australia": "Ellis", "Cape Verde Islands": "Ella", "Cape Verde": "Ella", "Uruguay": "Barbara", "Sweden": "Ellis",
    "Saudi Arabia": "Izzy", "Scotland": "Ella", "United States": "Izzy", "Senegal": "Jeff",
    "New Zealand": "Sam", "Iran": "Ella", "Iraq": "Barbara", "Norway": "Barbara",
    "Algeria": "Barbara", "Austria": "Ella", "Jordan": "Sam", "Congo DR": "Jeff", "DR Congo": "Jeff",
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
    "Jordan": 42, "Bosnia-Herzegovina": 43, "Bosnia and Herzegovina": 43, "Cape Verde Islands": 44, "Cape Verde": 44, "Ghana": 45, 
    "Curaçao": 46, "Haiti": 47, "New Zealand": 48
}

TEAM_COLORS = {
    "Mexico": "#006847", "South Africa": "#007A4D", "Canada": "#FF0000", "Switzerland": "#D52B1E",
    "Argentina": "#74ACDF", "France": "#002395", "Brazil": "#009739", "Spain": "#AA151B",
    "Bosnia-Herzegovina": "#002F6C", "Bosnia and Herzegovina": "#002F6C", "Czechia": "#11457E", "Qatar": "#8A1538", "Morocco": "#C1272D",
    "Haiti": "#00209F", "Turkey": "#E30A17", "Paraguay": "#D52B1E", "Germany": "#222222",
    "Curaçao": "#002B7F", "Ecuador": "#FFDD00", "Japan": "#00005C", "Belgium": "#E30A17",
    "Egypt": "#C1272D", "Tunisia": "#E70013", "Netherlands": "#E05206", "Ivory Coast": "#E87722",
    "Australia": "#00008B", "Cape Verde Islands": "#003893", "Cape Verde": "#003893", "Uruguay": "#0081C8", 
    "Sweden": "#006AA7", "Saudi Arabia": "#006C35", "Scotland": "#005EB8", "United States": "#002868", 
    "Senegal": "#00853F", "New Zealand": "#111111", "Iran": "#239E46", "Iraq": "#007A3D", 
    "Norway": "#EF2B2D", "Algeria": "#006233", "Austria": "#ED2939", "Jordan": "#1A1A1A", 
    "Congo DR": "#007FFF", "DR Congo": "#007FFF", "Portugal": "#FF0000", "Uzbekistan": "#0099B5", 
    "Colombia": "#FCD116", "England": "#CE1124", "Panama": "#DA121A", "Ghana": "#DA121A", 
    "Croatia": "#FF0000", "South Korea": "#111111"
}

GROUP_PLAYERS = {
    "Spain": {"player_name": "Lamine Yamal", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/lamine-yamal-spain-forward-profile-full.png"},
    "France": {"player_name": "Kylian Mbappe", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/kylian-mbappe-france-forward-profile-full.png"},
    "England": {"player_name": "Bukayo Saka", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/bukayo-saka-england-forward-profile-full.png"},
    "Brazil": {"player_name": "Vinícius Jr.", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/vinicius-junior-brazil-forward-profile-full.png"},
    "Germany": {"player_name": "Kai Havertz", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/kai-havertz-germany-forward-profile-full.png"},
    "Portugal": {"player_name": "Bruno Fernandes", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/bruno-fernandes-portugal-midfielder-profile-full.png"},
    "Netherlands": {"player_name": "Frenkie de Jong", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/frenkie-de-jong-netherlands-midfielder-profile-full.png"},
    "Argentina": {"player_name": "Lionel Messi", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/lionel-messi-argentina-forward-profile-full.png"},
    "Ivory Coast": {"player_name": "Yan Diomande", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/yan-diomande-ivory-coast-forward-profile-full.png"},
    "Bosnia-Herzegovina": {"player_name": "Esmir Bajraktarevic", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/esmir-bajraktarevic-bosnia-and-herzegovina-forward-profile-full.png"},
    "Bosnia and Herzegovina": {"player_name": "Esmir Bajraktarevic", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/esmir-bajraktarevic-bosnia-and-herzegovina-forward-profile-full.png"},
    "Cape Verde Islands": {"player_name": "Ryan Mendes", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ryan-mendes-cape-verde-midfielder-profile-full.png"},
    "Curaçao": {"player_name": "Juninho Bacuna", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/juninho-bacuna-curacao-midfielder-profile-full.png"},
    "Haiti": {"player_name": "Wilson Isidor", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/wilson-isidor-haiti-forward-profile-full.png"},
    "Congo DR": {"player_name": "Aaron Wan-Bissaka", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/aaron-wan-bissaka-dr-congo-defender-profile-full.png"},
    "DR Congo": {"player_name": "Aaron Wan-Bissaka", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/aaron-wan-bissaka-dr-congo-defender-profile-full.png"},
    "Ghana": {"player_name": "Antoine Semenyo", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/antoine-semenyo-ghana-forward-profile-full.png"},
    "Algeria": {"player_name": "Riyad Mahrez", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/riyad-mahrez-algeria-forward-profile-full.png"},
    "Australia": {"player_name": "Jackson Irvine", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/jackson-irvine-australia-midfielder-profile-full.png"},
    "Canada": {"player_name": "Alphonso Davies", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/alphonso-davies-canada-defender-profile-full.png"},
    "Czechia": {"player_name": "Patrik Schick", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/patrik-schick-czech-republic-forward-profile-full.png"},
    "Austria": {"player_name": "Romano Schmid", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/romano-schmid-austria-midfielder-profile-full.png"},
    "New Zealand": {"player_name": "Chris Wood", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/chris-wood-new-zealand-forward-profile-full.png"},
    "Iraq": {"player_name": "Ali Al-Hamadi", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ali-al-hamadi-iraq-forward-profile-full.png"},
    "Jordan": {"player_name": "Ihsan Haddad", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ihsan-haddad-jordan-defender-profile-full.png"},
    "Egypt": {"player_name": "Mohamed Salah", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/mohamed-salah-egypt-forward-profile-full.png"},
    "Ecuador": {"player_name": "Willian Pacho", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/willian-pacho-ecuador-defender-profile-full.png"},
    "Saudi Arabia": {"player_name": "Salem Al-Dawsari", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/salem-al-dawsari-saudi-arabia-forward-profile-full.png"},
    "Belgium": {"player_name": "Jeremy Doku", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/jeremy-doku-belgium-forward-profile-full.png"},
    "Qatar": {"player_name": "Hassan Al-Haydos", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/hassan-al-haydos-qatar-forward-profile-full.png"},
    "Colombia": {"player_name": "Luis Suarez", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/luis-suarez-colombia-forward-profile-full.png"},
    "Iran": {"player_name": "Alireza Beiranvand", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/alireza-beiranvand-iran-goalkeeper-profile-full.png"},
    "South Africa": {"player_name": "Mbekezeli Mbokazi", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/mbekezeli-mbokazi-south-africa-defender-profile-full.png"},
    "Norway": {"player_name": "Erling Haaland", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/erling-haaland-norway-forward-profile-full.png"},
    "Croatia": {"player_name": "Luka Vuskovic", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/luka-vuskovic-croatia-defender-profile-full.png"},
    "Paraguay": {"player_name": "Diego Gomez", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/diego-gomez-paraguay-midfielder-profile-full.png"},
    "Panama": {"player_name": "Adalberto Carrasquilla", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/adalberto-carrasquilla-panama-midfielder-profile-full.png"},
    "Japan": {"player_name": "Ritsu Doan", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ritsu-doan-japan-forward-profile-full.png"},
    "Scotland": {"player_name": "Scott McTominay", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/scott-mctominay-scotland-midfielder-profile-full.png"},
    "Tunisia": {"player_name": "Ellyes Skhiri", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ellyes-skhiri-tunisia-midfielder-profile-full.png"},
    "Sweden": {"player_name": "Viktor Gyökeres", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/viktor-gyokeres-sweden-forward-profile-full.png"},
    "Uzbekistan": {"player_name": "Eldor Shomurodov", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/eldor-shomurodov-uzbekistan-forward-profile-full.png"},
    "Mexico": {"player_name": "Gilberto Mora", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/gilberto-mora-mexico-midfielder-profile-full.png"},
    "South Korea": {"player_name": "Son Heung-min", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/son-heung-min-south-korea-forward-profile-full.png"},
    "Morocco": {"player_name": "Yassine Bounou", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/yassine-bounou-morocco-goalkeeper-profile-full.png"},
    "Senegal": {"player_name": "Sadio Mane", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/sadio-mane-senegal-forward-profile-full.png"},
    "Switzerland": {"player_name": "Johan Manzambi", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/johan-manzambi-switzerland-midfielder-profile-full.png"},
    "United States": {"player_name": "Christian Pulisic", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/christian-pulisic-united-states-forward-profile-full.png"},
    "Uruguay": {"player_name": "Federico Valverde", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/federico-valverde-uruguay-midfielder-profile-full.png"},
    "Turkey": {"player_name": "Kenan Yildiz", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/kenan-yildiz-turkey-forward-profile-full.png"}
}

# 3. Cache Country Flags One Time Daily Only
@st.cache_data(ttl=86400)
def get_cached_team_crests():
    crests = {}
    if API_TOKEN == "placeholder":
        return crests
    try:
        url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/teams"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            teams_data = res.json().get("teams", [])
            for t in teams_data:
                name = t.get("name")
                crest_url = t.get("crest")
                if name and crest_url:
                    crests[name] = crest_url
                    if name == "DR Congo": crests["Congo DR"] = crest_url
                    if name == "Congo DR": crests["DR Congo"] = crest_url
                    if name == "Cape Verde": crests["Cape Verde Islands"] = crest_url
                    if name == "Bosnia and Herzegovina": crests["Bosnia-Herzegovina"] = crest_url
    except Exception:
        pass
    return crests

CACHED_CRESTS = get_cached_team_crests()

def get_flag_html(team_name, extra_class="flag-img"):
    crest_url = CACHED_CRESTS.get(team_name)
    if crest_url:
        return f'<img src="{crest_url}" class="{extra_class}" alt="{team_name}">'
    return ''

# ── SPREADSHEET AS THE MASTER SOURCE OF TRUTH FOR SCHEDULES & SCORES ──
@st.cache_data(ttl=15)
def fetch_spreadsheet_matches_master():
    live_list = []
    upcoming_list = []
    finished_list = []
    try:
        csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQeLButP4o4374i0KJP_YdOnTW1wN-Wzgqabuulvd1cMVmIuCfFTEM3CjJ4FmFIbBW6FLNDfaB9Hg4w/pub?gid=0&single=true&output=csv"
        df = pd.read_csv(csv_url, header=None)
        
        if not df.empty:
            for idx, row in df.iterrows():
                try:
                    if len(row) < 7:
                        continue
                    # Parse using specified layout columns: A=Date, B=Time, C=Home, D=Away, E=Status, F=HomeScore, G=AwayScore, H=Highlights
                    date_str = str(row[0]).strip() if pd.notna(row[0]) else ""
                    time_str = str(row[1]).strip() if pd.notna(row[1]) else ""
                    home_t = str(row[2]).strip() if pd.notna(row[2]) else ""
                    away_t = str(row[3]).strip() if pd.notna(row[3]) else ""
                    status_str = str(row[4]).strip().lower() if pd.notna(row[4]) else ""
                    home_score = str(row[5]).strip() if pd.notna(row[5]) else "0"
                    away_score = str(row[6]).strip() if pd.notna(row[6]) else "0"
                    highlights = str(row[7]).strip() if (len(row) >= 8 and pd.notna(row[7])) else "https://www.youtube.com/@fifa/videos"
                    
                    if not home_t or not away_t or "home team" in home_t.lower():
                        continue
                        
                    time_info = f"{date_str} @ {time_str}" if (date_str and time_str) else "TBD"
                    
                    match_payload = {
                        "homeTeam": {"name": home_t},
                        "awayTeam": {"name": away_t},
                        "homeScore": home_score,
                        "awayScore": away_score,
                        "timeString": time_info,
                        "highlightsUrl": highlights
                    }
                    
                    if "live" in status_str:
                        live_list.append(match_payload)
                    elif "finished" in status_str or "completed" in status_str:
                        finished_list.append(match_payload)
                    else:
                        upcoming_list.append(match_payload)
                except Exception:
                    pass
    except Exception:
        pass
    return live_list, upcoming_list, finished_list

# ── ORIGINAL DESIGN HERO BANNER ENGINE GENERATOR ──
def build_match_banner(match, is_live=False, is_result=False, match_idx=2):
    home_team_obj = match.get("homeTeam", {})
    away_team_obj = match.get("awayTeam", {})

    h_name = home_team_obj.get("name", "TBD")
    a_name = away_team_obj.get("name", "TBD")

    left_color = TEAM_COLORS.get(h_name, "#006847")
    right_color = TEAM_COLORS.get(a_name, "#006847")
    if left_color == right_color:
        right_color = "#222222" if left_color != "#222222" else "#555555"

    h_flag = get_flag_html(h_name, extra_class="banner-flag")
    a_flag = get_flag_html(a_name, extra_class="banner-flag")

    h_owner = f" ({SWEEPSTAKE_MAPPING.get(h_name, 'Unassigned')})"
    a_owner = f" ({SWEEPSTAKE_MAPPING.get(a_name, 'Unassigned')})"

    if is_live:
        h_score = match.get("homeScore", "0")
        a_score = match.get("awayScore", "0")
        top_pane = '<div class="inplay-top-pane"><div class="next-match-title">🔴 Live now</div></div>'
        centre_bubble = f'<div class="score-bubble">{h_score} – {a_score}</div>'
        bottom_bar = '<div class="inplay-bottom-bar">⚽ Match in progress</div>'
    elif is_result:
        h_score = match.get("homeScore", "0")
        a_score = match.get("awayScore", "0")
        highlights_url = match.get("highlightsUrl", "https://www.youtube.com/@fifa/videos")
        
        top_pane = '<div class="result-top-pane"><div class="next-match-title" style="background: rgba(0,0,0,0.2);">✅ Latest result</div></div>'
        centre_bubble = f"""
        <div class="score-reveal-wrapper">
            <input type="checkbox" id="reveal-toggle-{match_idx}" class="reveal-toggle-input">
            <label for="reveal-toggle-{match_idx}" class="score-reveal-label">Show</label>
            <div class="score-bubble" style="display: none;">{h_score} – {a_score}</div>
        </div>
        """
        bottom_bar = f'<div class="result-bottom-bar"><a href="{highlights_url}" target="_blank" class="highlights-btn">📺 SPOILER-FREE HIGHLIGHTS 📺</a></div>'
    else:
        date_str = match.get("timeString", "TBD")
        top_pane = '<div class="banner-top-pane"><div class="next-match-title">⏳ Next match</div></div>'
        centre_bubble = '<div class="vs-marker-bubble">VS</div>'
        bottom_bar = f'<div class="banner-bottom-time">🗓️ {date_str}</div>'

    return f"""
    {GLOBAL_STYLE_TOKENS}
    <div class="match-banner-wrapper">
        <div class="match-banner-container">
            {top_pane}
            <div class="matchup-split-screen">
                <div class="team-panel home-panel" style="background-color: {left_color};">
                    <div class="team-panel-text">
                        {h_flag} {h_name} <span>{h_owner}</span>
                    </div>
                </div>
                {centre_bubble}
                <div class="team-panel away-panel" style="background-color: {right_color};">
                    <div class="team-panel-text">
                        <span>{a_owner}</span> {a_name} {a_flag}
                    </div>
                </div>
            </div>
            {bottom_bar}
        </div>
    </div>
    """
    
# ── Data Ingestion Pipeline ──
@st.cache_data(ttl=120)  
def fetch_football_data_standings_only():
    standings_list = []
    if API_TOKEN == "placeholder":
        return standings_list
    try:
        s_res = requests.get(f"{BASE_URL}/competitions/{COMPETITION_CODE}/standings", headers=HEADERS, timeout=10)
        if s_res.status_code == 200:
            standings_list = s_res.json().get("standings", [])
    except Exception:
        pass
    return standings_list

standings_list = fetch_football_data_standings_only()
live_matches, upcoming_matches, finished_matches = fetch_spreadsheet_matches_master()

# Process Leaderboard Data safely
master_flat_leaderboard = []
top_performer_text = "N/A"

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
            "crest": t_info.get("crest", "")
        })

if master_flat_leaderboard:
    master_flat_leaderboard.sort(key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"], x["name"]))
    for idx, team_item in enumerate(master_flat_leaderboard, start=1):
        team_item["actual_rank"] = idx
        team_item["expected_rank"] = EXPECTED_RANKINGS.get(team_item["name"], 25)
        team_item["overperformance"] = team_item["expected_rank"] - idx

    best = max(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]))
    op_owner = SWEEPSTAKE_MAPPING.get(best["name"], "Unassigned")
    top_performer_text = f"{best['name']} ({op_owner})"

# ── HEADER ROW (TITLE LEFT, DYNAMIC CONTENT CONTAINER RIGHT) ──────────────────
header_cols = st.columns([1, 1], gap="medium")

with header_cols[0]:
    st.markdown("""
        <div class="title-area" style="padding-top: 15px; margin-bottom: 20px;">
            <h1>🏆 KING FAMILY WORLD CUP SWEEPSTAKE</h1>
            <p>Live standings</p>
        </div>
    """, unsafe_allow_html=True)

with header_cols[1]:
    if live_matches:
        payload = build_match_banner(live_matches[0], is_live=True, match_idx=200)
        components.html(payload, height=160, scrolling=False)
    else:
        # Show each person's teams cleanly inside a space-conscious selector component
        requested_people = ["Barbara", "Ella", "Ellis", "Izzy", "Jeff", "Sam"]
        teams_by_person = {p: [] for p in requested_people}
        for team, person in SWEEPSTAKE_MAPPING.items():
            normalized_person = person.capitalize()
            if normalized_person in teams_by_person:
                teams_by_person[normalized_person].append(team)

        st.markdown('<div style="padding-top:10px;">', unsafe_allow_html=True)
        chosen_person = st.radio(
            "Select Person to Show Teams:", 
            options=requested_people, 
            horizontal=True, 
            index=0,
            key="header_sweep_selector"
        )
        
        selected_teams = teams_by_person[chosen_person]
        p_teams_html = ""
        for t in selected_teams:
            p_teams_html += f'<div class="compact-team-item">{get_flag_html(t)} {t}</div>'
        if not p_teams_html:
            p_teams_html = '<span style="font-size:11px; color:#777;">No teams currently assigned.</span>'
            
        st.markdown(f"""
            <div class="compact-sweep-container">
                <div class="compact-teams-grid">
                    {p_teams_html}
                </div>
            </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SECONDARY CONTENT ROW (NEXT FIXTURE LEFT, LATEST RESULT RIGHT SIDE-BY-SIDE) ──
hero_cols = st.columns([1, 1], gap="medium")

with hero_cols[0]:
    if upcoming_matches:
        payload = build_match_banner(upcoming_matches[0], is_live=False, match_idx=100)
        components.html(payload, height=160, scrolling=False)
    else:
        st.info("⏳ No matches currently scheduled. Check back soon for the next fixtures.")

with hero_cols[1]:
    if finished_matches:
        latest_match = finished_matches[0]
        result_banner_html = build_match_banner(latest_match, is_live=False, is_result=True, match_idx=999)
        components.html(result_banner_html, height=160, scrolling=False)
    else:
        st.info("⚽ No results logged yet for this tournament state.")

# ── STATS ROW ──────────────────────────────────────────────────────────
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-banner-box"><medium>💰 Prize pot</medium><span>£30</span></div>', unsafe_allow_html=True)
with stat_cols[1]:
    fave_owner = SWEEPSTAKE_MAPPING.get("France", "Unassigned")
    st.markdown(f'<div class="stat-banner-box"><medium>⭐ Favourites</medium><span>France ({fave_owner})</span></div>', unsafe_allow_html=True)
with stat_cols[2]:
    st.markdown(f'<div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>{top_performer_text}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px 25px 0px; border-top: 2px solid #006847;'>", unsafe_allow_html=True)

# ── GROUPS CANVAS ─────────────────────────────────────────────────────────
if API_TOKEN == "placeholder":
    st.warning("⚠️ Using placeholder API key. Please insert your true Football-Data.org token to pull live group lists.")
else:
    if standings_list:
        for i in range(0, len(standings_list), 2):
            row_cols = st.columns(2)
            for j in range(2):
                if i + j < len(standings_list):
                    group_data = standings_list[i + j]
                    group_name = group_data.get("group")
                    teams_in_group = [row.get("team", {}).get("name") for row in group_data.get("table", [])]

                    with row_cols[j]:
                        st.markdown('<div class="group-row-spacer">', unsafe_allow_html=True)
                        st.markdown(f"<span class='group-header-text'>🔹 {group_name}</span>", unsafe_allow_html=True)

                        table_html = """
                        <div class="table-responsive-wrapper">
                            <table class="custom-dashboard-table">
                                <thead>
                                    <tr>
                                        <th>Team</th>
                                        <th style="text-align:center;">P</th>
                                        <th style="text-align:center;">W</th>
                                        <th style="text-align:center;">D</th>
                                        <th style="text-align:center;">L</th>
                                        <th style="text-align:center;">GF</th>
                                        <th style="text-align:center;">GA</th>
                                        <th style="text-align:center;">GD</th>
                                        <th style="text-align:center;">Pts</th>
                                    </tr>
                                </thead>
                                <tbody>
                        """
                        for row in group_data.get("table", []):
                            team_info = row.get("team", {})
                            t_name = team_info.get("name")
                            owner = SWEEPSTAKE_MAPPING.get(t_name, "Unassigned")
                            flag_html = get_flag_html(t_name)
                            table_html += f"""<tr>
                                <td>{flag_html} <b>{t_name}</b> <span style="font-size:11px; color:#666;">({owner})</span></td>
                                <td style="text-align:center;">{row.get("playedGames")}</td>
                                <td style="text-align:center;">{row.get("won")}</td>
                                <td style="text-align:center;">{row.get("draw")}</td>
                                <td style="text-align:center;">{row.get("lost")}</td>
                                <td style="text-align:center;">{row.get("goalsFor")}</td>
                                <td style="text-align:center;">{row.get("goalsAgainst")}</td>
                                <td style="text-align:center;">{row.get("goalDifference")}</td>
                                <td style="text-align:center;"><b>{row.get("points")}</b></td>
                            </tr>"""
                        table_html += "</tbody></table></div>"
                        st.markdown(table_html, unsafe_allow_html=True)

                        active_cards = []
                        for team_name in teams_in_group:
                            if team_name in GROUP_PLAYERS:
                                p = GROUP_PLAYERS[team_name]
                                card = f"""
                                <div style="background: #FFFFFF; border: 1px solid #EAEAEA; border-radius: 8px; width: 130px; height: 140px; padding: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); text-align: center; margin: 4px;">
                                    <img src="{p['img_url']}" style="width: 100%; height: 90px; object-fit: contain; object-position: top; border-radius: 4px;" loading="eager" referrerpolicy="no-referrer">
                                    <div style="font-size: 10px; font-weight: 800; color: #333; margin-top: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 2px;">{p['player_name']}</div>
                                    <div style="font-size: 8px; font-weight: 600; color: #006847; text-transform: uppercase; margin-top: 2px;">{team_name}</div>
                                </div>
                                """
                                active_cards.append(card)

                        if active_cards:
                            st.markdown("<div style='text-align: center; margin-top: 10px;'><span style='font-size:12px; font-weight:700; color:#006847;'>🔑 Key players</span></div>", unsafe_allow_html=True)
                            full_html = f"""
                            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; width: 100%; font-family: sans-serif; padding: 5px 0;">
                                {"".join(active_cards)}
                            </div>
                            """
                            components.html(full_html, height=170, scrolling=False)

                        st.markdown('</div>', unsafe_allow_html=True)

        # ── OVERPERFORMANCE LEADERBOARD ──────────────────────────────────────
        st.markdown("<hr style='margin:30px 0px 20px 0px; border-top: 3px solid #006847;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>📈 Overperformance table</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 13px; margin-bottom: 20px;'>Ranked by overperformance: (Rank - Performance)</p>", unsafe_allow_html=True)

        master_flat_leaderboard.sort(key=lambda x: (-x["overperformance"], x["actual_rank"]))

        master_table_html = """
        <div class="table-responsive-wrapper">
            <table class="custom-dashboard-table" style="width:100%;">
                <thead>
                    <tr>
                        <th style="width: 100px;">Pos</th>
                        <th>Team</th>
                        <th style="text-align:center;">Rank</th>
                        <th style="text-align:center;">Actual</th>
                        <th style="text-align:center;">P</th>
                        <th style="text-align:center;">GD</th>
                        <th style="text-align:center;">Pts</th>
                        <th style="text-align:right; padding-right:15px;">Score</th>
                    </tr>
                </thead>
                <tbody>
        """
        for display_idx, team_row in enumerate(master_flat_leaderboard, start=1):
            owner = SWEEPSTAKE_MAPPING.get(team_row["name"], "Unassigned")
            flag_html = get_flag_html(team_row["name"])
            
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
                <td style='text-align:center; color:#555;'>#{team_row['expected_rank']}</td>
                <td style='text-align:center; color:#555;'>#{team_row['actual_rank']}</td>
                <td style='text-align:center;'>{team_row['played']}</td>
                <td style='text-align:center;'>{team_row['gd']}</td>
                <td style='text-align:center;'><b>{team_row['pts']}</b></td>
                <td style='text-align:right; padding-right:15px; font-weight:800; color:{score_color};'>{op_formatted}</td>
            </tr>"""

        master_table_html += "</tbody></table></div>"
        st.markdown(master_table_html, unsafe_allow_html=True)
