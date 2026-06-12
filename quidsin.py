import os
from datetime import datetime
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

# Run page auto-refresh every 3 minutes to pick up spreadsheet updates automatically
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
            color: #333333;
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

        /* --- MATCH BANNER LAYOUT --- */
        .match-banner-wrapper {
            width: 100%;
            margin: 12px 0px;
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

        /* Special variant container for the small sidebar result widget */
        .compact-sidebar-card {
            max-width: 460px !important;
            margin-left: auto;
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
            padding: 4px 10px;
            border-radius: 6px;
            display: inline-block;
        }

        /* In-play/Result banner top panes */
        .inplay-top-pane {
            background-color: #8B0000;
            padding: 8px 15px;
        }
        
        .result-top-pane {
            background-color: #444444;
            padding: 6px 12px;
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
        
        .team-panel-compact {
            padding: 6px 12px !important;
        }

        .home-panel {
            justify-content: flex-end;
            padding-right: 50px;
            border-right: 1px solid rgba(255, 255, 255, 0.15);
        }
        
        .home-panel-compact {
            padding-right: 35px !important;
        }

        .away-panel {
            justify-content: flex-start;
            padding-left: 50px;
        }
        
        .away-panel-compact {
            padding-left: 35px !important;
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
        
        .team-panel-text-compact {
            font-size: 13px !important;
        }

        .team-panel-text span {
            font-size: 12px;
            font-weight: 400 !important;
            opacity: 0.95;
            color: #FFFFFF !important;
            margin: 0 6px;
        }
        
        .team-panel-text-compact span {
            font-size: 10px !important;
            margin: 0 4px;
        }

        .vs-marker-bubble, .score-bubble {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            z-index: 10;
            border: 2px solid #FFFFFF;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            white-space: nowrap;
        }

        .vs-marker-bubble {
            background-color: #111111;
            color: #FFFFFF !important;
            font-size: 12px;
            font-weight: 900 !important;
            padding: 5px 9px;
            border-radius: 50%;
        }

        .score-bubble {
            background-color: #8B0000;
            color: #FFFFFF !important;
            font-size: 16px;
            font-weight: 900 !important;
            padding: 6px 14px;
            border-radius: 6px;
        }
        
        .score-bubble-compact {
            background-color: #444444 !important;
            font-size: 13px !important;
            padding: 4px 10px !important;
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
            background-color: #FFFFFF !important;
            padding: 10px 15px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            border-top: 1px solid #EEEEEE !important;
        }
        
        .highlights-btn {
            background-color: #FF0000 !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 11px !important;
            text-transform: uppercase;
            text-decoration: none !important;
            padding: 6px 16px;
            border-radius: 5px;
            display: inline-flex !important;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 4px rgba(255,0,0,0.2);
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
        
        .banner-flag-compact {
            width: 22px !important;
            height: 14px !important;
            margin: 0 5px !important;
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
    </style>
""", unsafe_allow_html=True)

# 2. Config & Team Data Setup
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
    "Argentina": {"player_name": "Lionel Messi", "img_url": "https://graphics-cdn.theathletic.com/world-cup-stars-2026/images/lionel-mesi-argentina-forward-profile-full.png"},
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

# Define static country flag mappings to mimic standard tournament crest icons safely
COUNTRY_FLAGS = {
    "Mexico": "https://flagcdn.com/w40/mx.png", "South Africa": "https://flagcdn.com/w40/za.png", 
    "Canada": "https://flagcdn.com/w40/ca.png", "Switzerland": "https://flagcdn.com/w40/ch.png",
    "Argentina": "https://flagcdn.com/w40/ar.png", "France": "https://flagcdn.com/w40/fr.png", 
    "Brazil": "https://flagcdn.com/w40/br.png", "Spain": "https://flagcdn.com/w40/es.png",
    "Bosnia-Herzegovina": "https://flagcdn.com/w40/ba.png", "Czechia": "https://flagcdn.com/w40/cz.png", 
    "Qatar": "https://flagcdn.com/w40/qa.png", "Morocco": "https://flagcdn.com/w40/ma.png",
    "Haiti": "https://flagcdn.com/w40/ht.png", "Turkey": "https://flagcdn.com/w40/tr.png", 
    "Paraguay": "https://flagcdn.com/w40/py.png", "Germany": "https://flagcdn.com/w40/de.png",
    "Curaçao": "https://flagcdn.com/w40/cw.png", "Ecuador": "https://flagcdn.com/w40/ec.png", 
    "Japan": "https://flagcdn.com/w40/jp.png", "Belgium": "https://flagcdn.com/w40/be.png",
    "Egypt": "https://flagcdn.com/w40/eg.png", "Tunisia": "https://flagcdn.com/w40/tn.png", 
    "Netherlands": "https://flagcdn.com/w40/nl.png", "Ivory Coast": "https://flagcdn.com/w40/ci.png",
    "Australia": "https://flagcdn.com/w40/au.png", "Cape Verde Islands": "https://flagcdn.com/w40/cv.png", 
    "Cape Verde": "https://flagcdn.com/w40/cv.png", "Uruguay": "https://flagcdn.com/w40/uy.png", 
    "Sweden": "https://flagcdn.com/w40/se.png", "Saudi Arabia": "https://flagcdn.com/w40/sa.png", 
    "Scotland": "https://flagcdn.com/w40/gb-sct.png", "United States": "https://flagcdn.com/w40/us.png", 
    "Senegal": "https://flagcdn.com/w40/sn.png", "New Zealand": "https://flagcdn.com/w40/nz.png", 
    "Iran": "https://flagcdn.com/w40/ir.png", "Iraq": "https://flagcdn.com/w40/iq.png", 
    "Norway": "https://flagcdn.com/w40/no.png", "Algeria": "https://flagcdn.com/w40/dz.png", 
    "Austria": "https://flagcdn.com/w40/at.png", "Jordan": "https://flagcdn.com/w40/jo.png", 
    "Congo DR": "https://flagcdn.com/w40/cd.png", "DR Congo": "https://flagcdn.com/w40/cd.png", 
    "Portugal": "https://flagcdn.com/w40/pt.png", "Uzbekistan": "https://flagcdn.com/w40/uz.png", 
    "Colombia": "https://flagcdn.com/w40/co.png", "England": "https://flagcdn.com/w40/gb-eng.png", 
    "Panama": "https://flagcdn.com/w40/pa.png", "Ghana": "https://flagcdn.com/w40/gh.png", 
    "Croatia": "https://flagcdn.com/w40/hr.png", "South Korea": "https://flagcdn.com/w40/kr.png"
}

def get_flag_html(team_name, extra_class="flag-img"):
    url = COUNTRY_FLAGS.get(team_name.strip())
    if url:
        return f'<img src="{url}" class="{extra_class}" alt="{team_name}">'
    return ''

# ── 3. SPREADSHEET-FIRST MASTER REPOSITORY LOAD ENGINE ──
def load_all_fixtures_from_spreadsheet():
    """
    Scans the system directory directly for the primary spreadsheet configuration file.
    Parses and sanitizes all matches directly out of the file to build master tournament states.
    """
    possible_files = ["fixtures.xlsx", "data.xlsx", "sweepstake.xlsx", "world_cup.xlsx"]
    
    sheet_path = st.secrets.get("SPREADSHEET_PATH", None)
    if sheet_path and os.path.exists(sheet_path):
        possible_files.insert(0, sheet_path)
        
    fixtures_list = []
    
    for file_name in possible_files:
        if os.path.exists(file_name):
            try:
                # Load the target tab explicitly 
                df = pd.read_excel(file_name, sheet_name='Fixtures')
                if df.empty or len(df.columns) < 5:
                    continue
                
                # Strip and read left-to-right columns reliably via position mapping:
                # Col A/0 = Group/Stage, Col B/1 = Date/Time, Col C/2 = Home Team, 
                # Col D/3 = Away Team, Col E/4 = Status, Col F/5 = Score (e.g., 2-1)
                for idx, row in df.iterrows():
                    vals = [str(val).strip() for val in row.values]
                    
                    if len(vals) >= 4:
                        group_val = vals[0] if pd.notna(row.values[0]) else "Group Stage"
                        date_str = vals[1] if pd.notna(row.values[1]) else "TBD"
                        home_team = vals[2]
                        away_team = vals[3]
                        
                        # Set default status flags
                        status = vals[4].upper() if len(vals) > 4 and vals[4] != "nan" else "TIMED"
                        score_text = vals[5] if len(vals) > 5 and vals[5] != "nan" else "0-0"
                        
                        # Scan row automatically for highlights/video URLs
                        custom_url = "https://www.youtube.com/@fifa/videos"
                        for column_item in vals:
                            if column_item.startswith("http://") or column_item.startswith("https://"):
                                custom_url = column_item
                                break
                                
                        fixtures_list.append({
                            "group": group_val,
                            "date_text": date_str,
                            "homeTeam": {"name": home_team},
                            "awayTeam": {"name": away_team},
                            "status": status,
                            "score_text": score_text,
                            "custom_url": custom_url
                        })
                return fixtures_list
            except Exception as e:
                pass
                
    return fixtures_list

# Load absolute truth configuration source
all_matches = load_all_fixtures_from_spreadsheet()

if not all_matches:
    st.error("🚨 Error: Could not locate 'fixtures.xlsx' or 'Fixtures' tab in root directory. Please verify file placements.")
    st.stop()

# ── 4. LIVE GROUP STATS CALCULATOR ──
def compute_group_standings(matches):
    """
    Dynamically recalculates point boards from scratch using spreadsheet scores 
    to prevent manual update lag or external synchronization misalignments.
    """
    standings = {}
    
    # Initialize all known teams
    for team in SWEEPSTAKE_MAPPING.keys():
        standings[team] = {"played": 0, "won": 0, "draw": 0, "lost": 0, "gf": 0, "ga": 0, "gd": 0, "pts": 0, "group": "Group Stage"}

    for m in matches:
        h_name = m["homeTeam"]["name"]
        a_name = m["awayTeam"]["name"]
        
        # Track Group categorization names dynamically
        if h_name in standings: standings[h_name]["group"] = m["group"]
        if a_name in standings: standings[a_name]["group"] = m["group"]
        
        if m["status"] in ["FINISHED", "IN_PLAY", "PAUSED"]:
            try:
                score_parts = m["score_text"].split("-")
                h_goals = int(score_parts[0].strip())
                a_goals = int(score_parts[1].strip())
            except Exception:
                continue # Skip parsing lines without numeric assignments
                
            if h_name in standings and a_name in standings:
                standings[h_name]["played"] += 1
                standings[a_name]["played"] += 1
                standings[h_name]["gf"] += h_goals
                standings[h_name]["ga"] += a_goals
                standings[a_name]["gf"] += a_goals
                standings[a_name]["ga"] += h_goals
                
                if h_goals > a_goals:
                    standings[h_name]["won"] += 1
                    standings[h_name]["pts"] += 3
                    standings[a_name]["lost"] += 1
                elif a_goals > h_goals:
                    standings[a_name]["won"] += 1
                    standings[a_name]["pts"] += 3
                    standings[h_name]["lost"] += 1
                else:
                    standings[h_name]["draw"] += 1
                    standings[h_name]["pts"] += 1
                    standings[a_name]["draw"] += 1
                    standings[a_name]["pts"] += 1

    for t in standings:
        standings[t]["gd"] = standings[t]["gf"] - standings[t]["ga"]
        
    return standings

calculated_stats = compute_group_standings(all_matches)

# Process Leaderboard Structure
master_flat_leaderboard = []
for name, stats in calculated_stats.items():
    master_flat_leaderboard.append({
        "name": name, "played": stats["played"], "won": stats["won"],
        "draw": stats["draw"], "lost": stats["lost"], "gd": stats["gd"],
        "gf": stats["gf"], "ga": stats["ga"], "pts": stats["pts"]
    })

master_flat_leaderboard.sort(key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"], x["name"]))

top_performer_text = "N/A"
if master_flat_leaderboard:
    for idx, team_item in enumerate(master_flat_leaderboard, start=1):
        team_item["actual_rank"] = idx
        team_item["expected_rank"] = EXPECTED_RANKINGS.get(team_item["name"], 25)
        team_item["overperformance"] = team_item["expected_rank"] - idx

    best = max(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]))
    op_owner = SWEEPSTAKE_MAPPING.get(best["name"], "Unassigned")
    top_performer_text = f"{best['name']} ({op_owner})"

# ── 5. MATCH BANNER BUILDER ──
def build_match_banner(match, is_live=False, is_result=False):
    h_name = match["homeTeam"]["name"]
    a_name = match["awayTeam"]["name"]

    left_color = TEAM_COLORS.get(h_name, DEFAULT_LEFT_COLOR)
    right_color = TEAM_COLORS.get(a_name, DEFAULT_RIGHT_COLOR)
    if left_color == right_color:
        right_color = "#222222" if left_color != "#222222" else "#555555"

    flag_class = "banner-flag banner-flag-compact" if is_result else "banner-flag"
    h_flag = get_flag_html(h_name, extra_class=flag_class)
    a_flag = get_flag_html(a_name, extra_class=flag_class)

    h_owner = f" ({SWEEPSTAKE_MAPPING.get(h_name, 'Unassigned')})"
    a_owner = f" ({SWEEPSTAKE_MAPPING.get(a_name, 'Unassigned')})"

    panel_text_class = "team-panel-text team-panel-text-compact" if is_result else "team-panel-text"
    home_panel_class = "team-panel home-panel team-panel-compact home-panel-compact" if is_result else "team-panel home-panel"
    away_panel_class = "team-panel away-panel team-panel-compact away-panel-compact" if is_result else "team-panel away-panel"
    span_class = "team-panel-text-compact" if is_result else ""
    container_class = "match-banner-container compact-sidebar-card" if is_result else "match-banner-container"

    if is_live:
        top_pane = '<div class="inplay-top-pane"><div class="next-match-title">🔴 Live now</div></div>'
        centre_bubble = f'<div class="score-bubble">{match["score_text"]}</div>'
        bottom_bar = '<div class="inplay-bottom-bar">⚽ Match in progress</div>'
    elif is_result:
        top_pane = '<div class="result-top-pane"><div class="next-match-title" style="background: rgba(0,0,0,0.2);">✅ Latest Result</div></div>'
        centre_bubble = f'<div class="score-bubble score-bubble-compact">{match["score_text"]}</div>'
        bottom_bar = f'<div class="result-bottom-bar"><a href="{match["custom_url"]}" target="_blank" class="highlights-btn">📺 Watch Highlights</a></div>'
    else:
        top_pane = '<div class="banner-top-pane"><div class="next-match-title">⏳ Next match</div></div>'
        centre_bubble = '<div class="vs-marker-bubble">VS</div>'
        bottom_bar = f'<div class="banner-bottom-time">🗓️ {match["date_text"]}</div>'

    return f"""
    <div class="match-banner-wrapper">
        <div class="{container_class}">
            {top_pane}
            <div class="matchup-split-screen">
                <div class="{home_panel_class}" style="background-color: {left_color};">
                    <div class="{panel_text_class}">
                        {h_flag} {h_name} <span class="{span_class}">{h_owner}</span>
                    </div>
                </div>
                {centre_bubble}
                <div class="{away_panel_class}" style="background-color: {right_color};">
                    <div class="{panel_text_class}">
                        <span class="{span_class}">{a_owner}</span> {a_name} {a_flag}
                    </div>
                </div>
            </div>
            {bottom_bar}
        </div>
    </div>
    """

# Categorize and Filter match matrices dynamically out of parsed data
live_matches = [m for m in all_matches if m["status"] in ["IN_PLAY", "LIVE", "PAUSED"]]
upcoming_matches = [m for m in all_matches if m["status"] in ["TIMED", "SCHEDULED"]]
finished_matches = [m for m in all_matches if m["status"] in ["FINISHED", "COMPLETED"]]

# ── 6. HEADER & LATEST RESULT LAYOUT ROW ──
header_cols = st.columns([0.55, 0.45], gap="medium")

with header_cols[0]:
    st.markdown("""
        <div class="title-area" style="padding-top: 15px;">
            <h1>🏆 KING FAMILY WORLD CUP SWEEPSTAKE</h1>
            <p>Live standings</p>
        </div>
    """, unsafe_allow_html=True)

with header_cols[1]:
    if finished_matches:
        latest_match = finished_matches[-1] # Pull the latest updated result entry
        st.markdown(build_match_banner(latest_match, is_live=False, is_result=True), unsafe_allow_html=True)
    else:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# Render main display boards dynamically
if live_matches:
    for live_m in live_matches:
        st.markdown(build_match_banner(live_m, is_live=True), unsafe_allow_html=True)
elif upcoming_matches:
    st.markdown(build_match_banner(upcoming_matches[0], is_live=False), unsafe_allow_html=True)
else:
    st.info("⏳ No upcoming matches currently listed inside the spreadsheet.")

# ── STATS ROW ──
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-banner-box"><medium>💰 Prize pot</medium><span>£30</span></div>', unsafe_allow_html=True)
with stat_cols[1]:
    fave_owner = SWEEPSTAKE_MAPPING.get("France", "Unassigned")
    st.markdown(f'<div class="stat-banner-box"><medium>⭐ Favourites</medium><span>France ({fave_owner})</span></div>', unsafe_allow_html=True)
with stat_cols[2]:
    st.markdown(f'<div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>{top_performer_text}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px 25px 0px; border-top: 2px solid #006847;'>", unsafe_allow_html=True)

# ── 7. RENDERING DYNAMIC GROUPS CANVAS ──
unique_groups = sorted(list(set([m["group"] for m in all_matches if "Group" in m["group"]])))

if unique_groups:
    for i in range(0, len(unique_groups), 2):
        row_cols = st.columns(2)
        for j in range(2):
            if i + j < len(unique_groups):
                g_name = unique_groups[i + j]
                
                # Fetch sorted leaderboard subset for this specific group container
                g_teams = [t for t in master_flat_leaderboard if calculated_stats[t["name"]]["group"] == g_name]
                g_team_names = [t["name"] for t in g_teams]
                
                with row_cols[j]:
                    st.markdown('<div class="group-row-spacer">', unsafe_allow_html=True)
                    st.markdown(f"<span class='group-header-text'>🔹 {g_name}</span>", unsafe_allow_html=True)

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
                    for t_row in g_teams:
                        t_name = t_row["name"]
                        owner = SWEEPSTAKE_MAPPING.get(t_name, "Unassigned")
                        flag_html = get_flag_html(t_name)
                        table_html += f"""<tr>
                            <td>{flag_html} <b>{t_name}</b> <span style="font-size:11px; color:#666;">({owner})</span></td>
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

                    # Filter group specific row lines
                    st.markdown("<div style='margin-bottom:6px;'><span style='font-size:12px; font-weight:700; color:#006847;'>📅 Group fixtures & results</span></div>", unsafe_allow_html=True)
                    group_fixtures = [m for m in all_matches if m["group"] == g_name]

                    for match in group_fixtures:
                        m_status = match["status"]
                        h_name = match["homeTeam"]["name"]
                        a_name = match["awayTeam"]["name"]
                        h_owner = SWEEPSTAKE_MAPPING.get(h_name, "Unassigned")
                        a_owner = SWEEPSTAKE_MAPPING.get(a_name, "Unassigned")

                        h_flag = get_flag_html(h_name)
                        a_flag = get_flag_html(a_name)

                        if m_status in ["FINISHED", "COMPLETED"]:
                            display_score = f"<b>{match['score_text']}</b>"
                            row_class = "fixture-row"
                        elif m_status in ["IN_PLAY", "LIVE", "PAUSED"]:
                            display_score = f"<span style='color:#CC0000; font-weight:800;'>LIVE 🔴 {match['score_text']}</span>"
                            row_class = "fixture-row fixture-row-live"
                        else:
                            display_score = f"<span style='color:#777; font-weight:500;'>{match['date_text']}</span>"
                            row_class = "fixture-row"

                        st.markdown(f"""
                            <div class="{row_class}">
                                <div style="text-align: left; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                    {h_flag} <span>{h_name}</span> <span style="font-size:9px; color:#777;">({h_owner})</span>
                                </div>
                                <div style="text-align: center; width: 16%; font-size:11px;">
                                    {display_score}
                                </div>
                                <div style="text-align: right; width: 42%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                    <span style="font-size:9px; color:#777;">({a_owner})</span> <span>{a_name}</span> {a_flag}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    # Dynamic Key Star Player Render Grid
                    active_cards = []
                    for team_name in g_team_names:
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

# ── 8. CALCULATED OVERPERFORMANCE LEADERBOARD BOARD ──
st.markdown("<hr style='margin:30px 0px 20px 0px; border-top: 3px solid #006847;'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>📈 Overperformance table</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 13px; margin-bottom: 20px;'>Ranked by overperformance: (Expected Seed Rank - Actual Group Rank Position)</p>", unsafe_allow_html=True)

master_flat_leaderboard.sort(key=lambda x: (-x["overperformance"], x["actual_rank"]))

master_table_html = """
<div class="table-responsive-wrapper">
    <table class="custom-dashboard-table" style="width:100%;">
        <thead>
            <tr>
                <th style="width: 100px;">Pos</th>
                <th>Team</th>
                <th style="text-align:center;">Seed Rank</th>
                <th style="text-align:center;">Actual Pos</th>
                <th style="text-align:center;">P</th>
                <th style="text-align:center;">GD</th>
                <th style="text-align:center;">Pts</th>
                <th style="text-align:right; padding-right:15px;">Differential Score</th>
            </tr>
        </thead>
        <tbody>
"""
for display_idx, team_row in enumerate(master_flat_leaderboard, start=1):
    owner = SWEEPSTAKE_MAPPING.get(team_row["name"], "Unassigned")
    flag_html = get_flag_html(team_row["name"])
    
    if display_idx == 1:
        pos_str = "1 🚀"
    elif display_idx == len(master_flat_leaderboard):
        pos_str = f"{display_idx} 💩"
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
