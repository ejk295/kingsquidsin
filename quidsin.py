import os
import csv
import requests
from datetime import datetime
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# 1. Page Configurations & Branding Styles
st.set_page_config(
    page_title="King Family World Cup Sweepstake", 
    page_icon="⚽", 
    layout="wide"
)

# Run page auto-refresh every 3 minutes to keep live scores syncing from the sheet
st_autorefresh(interval=180 * 1000, key="datarefresh")

# Custom branding & layout safety styles with strict light-mode overrides and Figtree font
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300..900;1,300..900&display=swap');

        /* Force global app body background, standard text, and Figtree font */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #FAFAFA !important;
            color: #333333 !important;
            font-family: 'Figtree', sans-serif !important;
        }
        
        p, span, div, label, small, td, th, b {
            color: #333333 !important;
            font-family: 'Figtree', sans-serif !important;
        }
        
        h1, h2, h3 {
            color: #006847 !important;
            font-family: 'Figtree', sans-serif !important;
            font-weight: 800 !important;
        }
        
        .title-area h1 {
            margin: 0px !important;
            font-size: 28px;
            font-weight: 900 !important;
        }
        .title-area p {
            margin: 4px 0px 0px 0px !important;
            color: #555555 !important;
            font-weight: 700 !important;
            font-size: 16px;
        }

        /* --- MATCH BANNER LAYOUT (DYNAMIC COLOURS) --- */
        .match-banner-container {
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
            margin: 8px 0px;
            overflow: hidden;
            font-family: 'Figtree', sans-serif !important;
            text-align: center;
            border: 2px solid #DDDDDD;
        }

        .banner-top-pane {
            background-color: #111111;
            padding: 10px 20px;
        }

        .next-match-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.15);
            padding: 6px 12px;
            border-radius: 6px;
            display: inline-block;
        }

        /* In-play banner top pane */
        .inplay-top-pane {
            background-color: #8B0000;
            padding: 10px 20px;
        }

        .matchup-split-screen {
            display: flex;
            position: relative;
            align-items: center;
        }

        .team-panel {
            width: 50%;
            display: flex;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
            height: 100%;
            min-height: 80px;
        }

        .home-panel {
            justify-content: flex-end;
            padding-right: 45px;
            border-right: 2px solid #FFFFFF;
        }

        .away-panel {
            justify-content: flex-start;
            padding-left: 45px;
        }

        .team-panel-text {
            color: #FFFFFF !important;
            font-size: 20px;
            font-weight: 900 !important;
            text-shadow: 0px 1px 4px rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
        }

        .team-panel-text span {
            font-size: 13px;
            font-weight: 400 !important;
            opacity: 0.9;
            color: #FFFFFF !important;
            margin: 0 4px;
        }

        .vs-marker-bubble {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            z-index: 10;
            background-color: #111111;
            color: #FFFFFF !important;
            font-size: 13px;
            font-weight: 900 !important;
            padding: 6px 10px;
            border-radius: 50%;
            border: 2px solid #FFFFFF;
            box-shadow: 0 2px 5px rgba(0,0,0,0.4);
        }

        /* Score bubble for in-play matches */
        .score-bubble {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            z-index: 10;
            background-color: #8B0000;
            color: #FFFFFF !important;
            font-size: 18px;
            font-weight: 900 !important;
            padding: 8px 14px;
            border-radius: 8px;
            border: 2px solid #FFFFFF;
            box-shadow: 0 2px 5px rgba(0,0,0,0.4);
            white-space: nowrap;
        }

        .banner-bottom-time {
            background-color: #111111;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }

        /* In-play bottom bar */
        .inplay-bottom-bar {
            background-color: #8B0000;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }
        
        .banner-flag {
            width: 32px !important;
            height: 22px !important;
            object-fit: cover !important;
            border-radius: 3px;
            border: 1px solid rgba(255,255,255,0.4);
            display: inline-block;
            margin: 0 10px;
            vertical-align: middle;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.3);
        }

        .stat-banner-box {
            background: #FFFFFF !important;
            padding: 12px 20px;
            border-radius: 8px;
            border: 2px solid #EAEAEA;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
            height: auto;
            min-height: 50px;
        }
        .stat-banner-box medium {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 800 !important;
            color: #006847 !important;
        }
        .stat-banner-box span {
            font-size: 14px;
            font-weight: 800 !important;
            text-align: right;
            color: #333333 !important;
        }

        /* --- IN-GROUP TEAM PLAYERS ROW --- */
        .group-players-container {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 8px !important; 
            margin-bottom: 0px !important;
            justify-content: center;
        }
        .group-player-card {
            background: #FFFFFF;
            border: 1px solid #EAEAEA;
            border-radius: 8px;
            width: 120px;
            text-align: center;
            padding: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }
        .group-player-card img {
            width: 100%;
            height: auto;
            border-radius: 4px;
            object-fit: cover;
            background: #F5F5F5;
        }
        .group-player-card-name {
            font-size: 11px;
            font-weight: 800 !important;
            color: #333333 !important;
            margin-top: 3px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .group-player-card-team {
            font-size: 9px;
            font-weight: 600 !important;
            color: #006847 !important;
            text-transform: uppercase;
            margin-top: 1px;
        }

        .group-row-spacer {
            margin-bottom: 15px !important;
        }

        .table-responsive-wrapper {
            width: 100%;
            overflow-x: auto;
            margin-bottom: 8px !important;
        }
        
        .custom-dashboard-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
            white-space: nowrap;
        }
        .custom-dashboard-table th {
            background-color: #FAFAFA !important;
            color: #333333 !important;
            font-weight: 700 !important;
            padding: 6px 6px !important;
            border-bottom: 2px solid #006847;
        }
        .custom-dashboard-table td {
            padding: 6px 6px !important;
            border-bottom: 1px solid #EAEAEA;
            vertical-align: middle;
            background-color: #FFFFFF !important;
            color: #333333 !important;
        }
        
        .fixture-row {
            background-color: #FFFFFF !important;
            padding: 6px 8px !important;
            border-radius: 4px;
            margin-bottom: 3px !important;
            border: 1px solid #EAEAEA;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .fixture-row-live {
            background-color: #FFF5F5 !important;
            border: 1px solid #FFCCCC !important;
        }
        .flag-img {
            vertical-align: middle;
            margin: 0px 4px;
            width: 20px !important;
            height: 14px !important;
            object-fit: cover !important;
            display: inline-block;
        }
        .group-header-text {
            color: #006847 !important;
            font-size: 18px;
            font-weight: 800 !important;
            margin-bottom: 4px !important;
            margin-top: 0px !important;
            display: inline-block;
        }

        @media (max-width: 800px) {
            .match-banner-container {
                flex-direction: column;
            }
            .matchup-split-screen {
                flex-direction: column;
                width: 100%;
            }
            .team-panel {
                width: 100% !important;
                justify-content: center !important;
                padding: 15px !important;
                font-size: 16px;
            }
            .home-panel {
                border-right: none !important;
                border-bottom: 2px solid #FFFFFF;
                padding-right: 20px !important;
            }
            .away-panel {
                padding-left: 20px !important;
            }
            .vs-marker-bubble {
                top: auto;
                bottom: -14px;
                left: 50%;
                transform: translateX(-50%);
            }
            .score-bubble {
                top: auto;
                bottom: -18px;
                left: 50%;
                transform: translateX(-50%);
            }
        }
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & Spreadsheet Settings
# TODO: Replace this with your dynamic Published CSV URL from Step 1!
SPREADSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQeLButP4o4374i0KJP_YdOnTW1wN-Wzgqabuulvd1cMVmIuCfFTEM3CjJ4FmFIbBW6FLNDfaB9Hg4w/pub?output=csv"

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

TEAM_COLORS = {
    "Mexico": "#006847", "South Africa": "#007A4D", "Canada": "#FF0000", "Switzerland": "#D52B1E",
    "Argentina": "#74ACDF", "France": "#002395", "Brazil": "#009739", "Spain": "#AA151B",
    "Bosnia-Herzegovina": "#002F6C", "Czechia": "#11457E", "Qatar": "#8A1538", "Morocco": "#C1272D",
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
    "Cape Verde Islands": {"player_name": "Ryan Mendes", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/ryan-mendes-cape-verde-midfielder-profile-full.png"},
    "Curaçao": {"player_name": "Juninho Bacuna", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/juninho-bacuna-curacao-midfielder-profile-full.png"},
    "Haiti": {"player_name": "Wilson Isidor", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/wilson-isidor-haiti-forward-profile-full.png"},
    "Congo DR": {"player_name": "Aaron Wan-Bissaka", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/aaron-wan-bissaka-dr-congo-defender-profile-full.png"},
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

DEFAULT_LEFT_COLOR = "#006847"
DEFAULT_RIGHT_COLOR = "#006847"

# Team groups definition matrix to build group standings directly from fixture rows
GROUPS_DEFINITION = {
    "Group A": ["Mexico", "South Africa", "Canada", "Switzerland"],
    "Group B": ["Argentina", "France", "Brazil", "Spain"],
    "Group C": ["Bosnia-Herzegovina", "Czechia", "Qatar", "Morocco"],
    "Group D": ["Haiti", "Turkey", "Paraguay", "Germany"],
    "Group E": ["Curaçao", "Ecuador", "Japan", "Belgium"],
    "Group F": ["Egypt", "Tunisia", "Netherlands", "Ivory Coast"],
    "Group G": ["Australia", "Cape Verde Islands", "Uruguay", "Sweden"],
    "Group H": ["Saudi Arabia", "Scotland", "United States", "Senegal"],
    "Group I": ["New Zealand", "Iran", "Iraq", "Norway"],
    "Group J": ["Algeria", "Austria", "Jordan", "Congo DR"],
    "Group K": ["Portugal", "Uzbekistan", "Colombia", "England"],
    "Group L": ["Panama", "Ghana", "Croatia", "South Korea"]
}

def format_sheet_time(date_str):
    """Safely converts spreadsheet date strings or returns fallback string."""
    if not date_str:
        return "TBD"
    return str(date_str).strip()

def build_match_banner(match, is_live=False):
    h_name = match.get("homeTeam", "TBD")
    a_name = match.get("awayTeam", "TBD")

    left_color = TEAM_COLORS.get(h_name, DEFAULT_LEFT_COLOR)
    right_color = TEAM_COLORS.get(a_name, DEFAULT_RIGHT_COLOR)
    if left_color == right_color:
        right_color = "#222222" if left_color != "#222222" else "#555555"

    h_flag = "" # Crest assets can be omitted or fallback styled if not loaded dynamically
    a_flag = ""

    h_owner = f" ({SWEEPSTAKE_MAPPING.get(h_name, 'Unassigned')})"
    a_owner = f" ({SWEEPSTAKE_MAPPING.get(a_name, 'Unassigned')})"

    if is_live:
        top_pane = '<div class="inplay-top-pane"><div class="next-match-title">🔴 Live Now</div></div>'
        centre_bubble = f'<div class="score-bubble">{match.get("homeScore", 0)} – {match.get("awayScore", 0)}</div>'
        bottom_bar = f'<div class="inplay-bottom-bar">⚽ Match in progress ({match.get("status")})</div>'
    else:
        date_str = format_sheet_time(match.get("date"))
        top_pane = '<div class="banner-top-pane"><div class="next-match-title">⏳ Next Match</div></div>'
        centre_bubble = '<div class="vs-marker-bubble">VS</div>'
        bottom_bar = f'<div class="banner-bottom-time">🗓️ {date_str}</div>'

    return f"""
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
    """

# ── Data Fetching (Protected TTL Cache updates every 60 seconds) ─────
@st.cache_data(ttl=60)  
def fetch_sheet_data():
    all_matches = []
    
    if "YOUR_PUBLISHED_ID" in SPREADSHEET_CSV_URL:
        return all_matches

    try:
        response = requests.get(SPREADSHEET_CSV_URL, timeout=10)
        if response.status_code == 200:
            lines = response.text.splitlines()
            reader = csv.reader(lines)
            
            # Read header row
            headers = [h.strip().lower() for h in next(reader)]
            
            # Identify columns based on header indexes safely
            try:
                date_idx = headers.index("date")
                time_idx = headers.index("time") if "time" in headers else -1
                home_idx = next(i for i, h in enumerate(headers) if "home" in h and "team" in h)
                away_idx = next(i for i, h in enumerate(headers) if "away" in h and "team" in h)
                status_idx = next(i for i, h in enumerate(headers) if "status" in h or "state" in h)
                h_score_idx = next(i for i, h in enumerate(headers) if "home" in h and ("score" in h or "goal" in h))
                a_score_idx = next(i for i, h in enumerate(headers) if "away" in h and ("score" in h or "goal" in h))
            except Exception as e:
                # Absolute static index array fallbacks if titles mismatched
                date_idx, home_idx, away_idx, status_idx, h_score_idx, a_score_idx = 0, 2, 3, 4, 5, 6
                time_idx = 1

            for row in reader:
                if len(row) <= max(home_idx, away_idx):
                    continue
                
                # Rebuild full timestamp representation
                date_val = row[date_idx]
                if time_idx != -1 and len(row) > time_idx and row[time_idx]:
                    date_val += f" {row[time_idx]}"

                # Parse numerical strings into safe integer types
                try:
                    h_score = int(float(row[h_score_idx])) if row[h_score_idx].strip() not in ["-", ""] else 0
                    a_score = int(float(row[a_score_idx])) if row[a_score_idx].strip() not in ["-", ""] else 0
                except ValueError:
                    h_score, a_score = 0, 0

                all_matches.append({
                    "date": date_val,
                    "homeTeam": row[home_idx].strip(),
                    "awayTeam": row[away_idx].strip(),
                    "status": row[status_idx].strip(),
                    "homeScore": h_score,
                    "awayScore": a_score
                })
    except Exception as e:
        st.error(f"Error fetching data from spreadsheet: {e}")
        
    return all_matches

# Fetch match data row rows matrix from Google Sheet
all_matches = fetch_sheet_data()

# ── Re-calculate Standings Internally based on Fixtures Matrix ──────────
standings_map = {}
# Initialize all active team rows from map definitions
for team in SWEEPSTAKE_MAPPING.keys():
    standings_map[team] = {"name": team, "played": 0, "won": 0, "draw": 0, "lost": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0}

for m in all_matches:
    status_upper = m["status"].upper()
    h, a = m["homeTeam"], m["awayTeam"]
    
    # Process only if game row represents valid team references and is Finished
    if h in standings_map and a in standings_map and "FINISHED" in status_upper:
        hs, as_ = m["homeScore"], m["awayScore"]
        
        standings_map[h]["played"] += 1
        standings_map[a]["played"] += 1
        standings_map[h]["gf"] += hs
        standings_map[h]["ga"] += as_
        standings_map[a]["gf"] += as_
        standings_map[a]["ga"] += hs
        standings_map[h]["gd"] += (hs - as_)
        standings_map[a]["gd"] += (as_ - hs)
        
        if hs > as_:
            standings_map[h]["won"] += 1
            standings_map[h]["pts"] += 3
            standings_map[a]["lost"] += 1
        elif as_ > hs:
            standings_map[a]["won"] += 1
            standings_map[a]["pts"] += 3
            standings_map[h]["lost"] += 1
        else:
            standings_map[h]["draw"] += 1
            standings_map[a]["draw"] += 1
            standings_map[h]["pts"] += 1
            standings_map[a]["pts"] += 1

# Flatten to sort master leaderboard row arrays
master_flat_leaderboard = list(standings_map.values())
top_performer_text = "N/A"

if master_flat_leaderboard:
    master_flat_leaderboard.sort(key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"], x["name"]))
    for idx, team_item in enumerate(master_flat_leaderboard, start=1):
        team_item["actual_rank"] = idx
        team_item["expected_rank"] = EXPECTED_RANKINGS.get(team_item["name"], 25)
        team_item["overperformance"] = team_item["expected_rank"] - idx

    best = max(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]))
    op_owner = SWEEPSTAKE_MAPPING.get(best["name"], "Unassigned")
    top_performer_text = f"{best['name']} ({op_owner})"

# ── Dynamic Match Filtering ─────────────────────────────────────────────
live_matches = [m for m in all_matches if m["status"].upper() in ["LIVE", "IN_PLAY", "FIRST HALF", "SECOND HALF", "HALF TIME", "PAUSED"]]
upcoming_matches = [m for m in all_matches if m["status"].upper() in ["TIMED", "SCHEDULED"]]

next_kickoff_matches = []
if upcoming_matches:
    # Safely show the immediate next matches in the list queue
    first_date = upcoming_matches[0]["date"]
    next_kickoff_matches = [m for m in upcoming_matches if m["date"] == first_date]

# ── HEADER ─────────────────────────────────────────────────────────────
st.markdown("""
    <div class="title-area">
        <h1>🏆 KING FAMILY WORLD CUP SWEEPSTAKE</h1>
        <p>Live Standings (Synced from Spreadsheet)</p>
    </div>
""", unsafe_allow_html=True)

# Render hero banners directly
if live_matches:
    for live_match in live_matches:
        st.markdown(build_match_banner(live_match, is_live=True), unsafe_allow_html=True)

if next_kickoff_matches:
    for next_match in next_kickoff_matches:
        st.markdown(build_match_banner(next_match, is_live=False), unsafe_allow_html=True)

if not live_matches and not next_kickoff_matches:
    st.info("⏳ No upcoming matches listed in sheet. Check back later!")

# ── STATS ROW ──────────────────────────────────────────────────────────
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-banner-box"><medium>💰 Prize Pot</medium><span>£30</span></div>', unsafe_allow_html=True)
with stat_cols[1]:
    fave_owner = SWEEPSTAKE_MAPPING.get("France", "Unassigned")
    st.markdown(f'<div class="stat-banner-box"><medium>⭐ Favourites</medium><span>France ({fave_owner})</span></div>', unsafe_allow_html=True)
with stat_cols[2]:
    st.markdown(f'/div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>{top_performer_text}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px 25px 0px; border-top: 2px solid #006847;'>", unsafe_allow_html=True)

# ── GROUPS CANVAS ─────────────────────────────────────────────────────────
if "YOUR_PUBLISHED_ID" in SPREADSHEET_CSV_URL:
    st.warning("⚠️ Please insert your Published Web CSV URL inside the script file to connect the data live.")
else:
    groups_keys = list(GROUPS_DEFINITION.keys())
    for i in range(0, len(groups_keys), 2):
        row_cols = st.columns(2)
        for j in range(2):
            if i + j < len(groups_keys):
                group_name = groups_keys[i + j]
                teams_in_group = GROUPS_DEFINITION[group_name]

                with row_cols[j]:
                    st.markdown('<div class="group-row-spacer">', unsafe_allow_html=True)
                    st.markdown(f"<span class='group-header-text'>🔹 {group_name}</span>", unsafe_allow_html=True)

                    # Build internal standings sorted subset array
                    group_teams_data = [standings_map[t] for t in teams_in_group if t in standings_map]
                    group_teams_data.sort(key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"]))

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
                    for t_row in group_teams_data:
                        t_name = t_row["name"]
                        owner = SWEEPSTAKE_MAPPING.get(t_name, "Unassigned")
                        table_html += f"""<tr>
                            <td><b>{t_name}</b> <span style="font-size:11px; color:#666;">({owner})</span></td>
                            <td style="text-align:center;">{t_row["played"]}</td>
                            <td style="text-align:center;">{t_row["won"]}</td>
                            <td style="text-align:center;">{t_row["draw"]}</td>
                            <td style="text-align:center;">{t_row["lost"]}</td>
                            <td style="text-align:center;">{t_row["gf"]}</td>
                            <td style="text-align:center;">{t_row["ga"]}</td>
                            <td style="text-align:center;">{t_row["gd"]}</td>
                            <td style="text-align:center;"><b>{t_row["pts"]}</b></td>
                        </tr>"""
                    table_html += "</tbody></table></div>"
                    st.markdown(table_html, unsafe_allow_html=True)

                    # Group Fixtures parsed out from Sheet matrix
                    st.markdown("<div style='margin-bottom:6px;'><span style='font-size:12px; font-weight:700; color:#006847;'>📅 Group fixtures & results</span></div>", unsafe_allow_html=True)
                    group_fixtures = [
                        m for m in all_matches
                        if m["homeTeam"] in teams_in_group or m["awayTeam"] in teams_in_group
                    ]

                    if not group_fixtures:
                        st.caption("No fixtures currently listed for this group.")
                    else:
                        for match in group_fixtures[:6]:
                            m_status = match["status"].upper()
                            h_name = match["homeTeam"]
                            a_name = match["awayTeam"]
                            h_owner = SWEEPSTAKE_MAPPING.get(h_name, "Unassigned")
                            a_owner = SWEEPSTAKE_MAPPING.get(a_name, "Unassigned")

                            local_time_str = match["date"]

                            if "FINISHED" in m_status:
                                display_score = f"<b>{match['homeScore']} - {match['awayScore']}</b>"
                                row_class = "fixture-row"
                            elif m_status in ["LIVE", "IN_PLAY", "FIRST HALF", "SECOND HALF", "HALF TIME", "PAUSED"]:
                                display_score = f"<span style='color:#CC0000; font-weight:800;'>LIVE🔴 {match['homeScore']}-{match['awayScore']}</span>"
                                row_class = "fixture-row fixture-row-live"
                            else:
                                display_score = f"<span style='color:#777; font-weight:500;'>{local_time_str}</span>"
                                row_class = "fixture-row"

                            st.markdown(f"""
                                <div class="{row_class}">
                                    <div style="text-align: left; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                        <span>{h_name}</span> <span style="font-size:9px; color:#777;">({h_owner})</span>
                                    </div>
                                    <div style="text-align: center; width: 16%; font-size:11px;">
                                        {display_score}
                                    </div>
                                    <div style="text-align: right; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                        <span style="font-size:9px; color:#777;">({a_owner})</span> <span>{a_name}</span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                    # Key players component layout
                    import streamlit.components.v1 as components

                    active_cards = []
                    for team_name in teams_in_group:
                        if team_name in GROUP_PLAYERS:
                            p = GROUP_PLAYERS[team_name]
                            card = f"""
                            <div style="background: #FFFFFF; border: 1px solid #EAEAEA; border-radius: 8px; width: 130px; height: 130px; padding: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); text-align: center;">
                                <img src="{p['img_url']}" style="width: 100%; height: 90px; object-fit: contain; object-position: top; border-radius: 4px;" loading="eager" referrerpolicy="no-referrer">
                                <div style="font-size: 10px; font-weight: 800; color: #33; margin-top: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 2px;">{p['player_name']}</div>
                                <div style="font-size: 8px; font-weight: 600; color: #006847; text-transform: uppercase; margin-top: 2px;">{team_name}</div>
                            </div>
                            """
                            active_cards.append(card)

                    if active_cards:
                        st.markdown("<div style='text-align: center; margin-top: 10px;'><span style='font-size:12px; font-weight:700; color:#006847;'>🌟 Key players</span></div>", unsafe_allow_html=True)
                        full_html = f"""
                        <div style="display: flex; flex-wrap: wrap; justify-content: center; width: 100%; font-family: sans-serif;">
                            {"".join(active_cards)}
                        </div>
                        """
                        components.html(full_html, height=155, scrolling=False)

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
                    <th style="width: 60px;">Pos</th>
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
        pos_str = f"🚀 {display_idx}" if display_idx == 1 else (f"💩 {display_idx}" if display_idx == 48 else str(display_idx))
        op_val = team_row["overperformance"]
        op_formatted = f"+{op_val}" if op_val > 0 else str(op_val)
        score_color = "#107C41" if op_val > 0 else ("#A80000" if op_val < 0 else "#333333")

        master_table_html += f"""<tr>
            <td><b>{pos_str}</b></td>
            <td><b>{team_row['name']}</b> <span style='font-size:11px; color:#666;'>({owner})</span></td>
            <td style='text-align:center; color:#555;'>#{team_row['expected_rank']}</td>
            <td style='text-align:center; color:#555;'>#{team_row['actual_rank']}</td>
            <td style='text-align:center;'>{team_row['played']}</td>
            <td style='text-align:center;'>{team_row['gd']}</td>
            <td style='text-align:center;'><b>{team_row['pts']}</b></td>
            <td style='text-align:right; padding-right:15px; font-weight:800; color:{score_color};'>{op_formatted}</td>
        </tr>"""

    master_table_html += "</tbody></table></div>"
    st.markdown(master_table_html, unsafe_allow_html=True)
