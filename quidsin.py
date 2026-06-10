import os
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

# Run page auto-refresh every 30 seconds to keep live scores syncing
st_autorefresh(interval=30 * 1000, key="datarefresh")

# Custom branding & layout safety styles with strict light-mode overrides and Figtree font
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght=0,300..900;1,300..900&display=swap');

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

        /* --- NEXT MATCH BANNER LAYOUT (DYNAMIC COLOURS) --- */
        .match-banner-container {
            border-radius: 12px;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
            margin: 15px 0px;
            overflow: hidden;
            font-family: 'Figtree', sans-serif !important;
            text-align: center;
            border: 2px solid #DDDDDD; /* Visible boundary for light colours */
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

        /* Middle Split-Screen Wrapper */
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

        /* Home panel pushes text right, AWAY pushes left to keep names near VS */
        .home-panel {
            justify-content: flex-end;
            padding-right: 45px;
            border-right: 2px solid #FFFFFF;
        }

        .away-panel {
            justify-content: flex-start;
            padding-left: 45px;
        }

        /* Team Text Styling with forced visibility shadow */
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

        /* Perfectly Centered VS Symbol locked over the middle divider */
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

        .banner-bottom-time {
            background-color: #111111;
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

        /* Smaller Side-by-Side Stat Blocks */
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

        /* Responsive Table Canvas Controls */
        .table-responsive-wrapper {
            width: 100%;
            overflow-x: auto;
            margin-bottom: 20px;
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
            padding: 8px 6px;
            border-bottom: 2px solid #006847;
        }
        .custom-dashboard-table td {
            padding: 8px 6px;
            border-bottom: 1px solid #EAEAEA;
            vertical-align: middle;
            background-color: #FFFFFF !important;
            color: #333333 !important;
        }
        
        .fixture-row {
            background-color: #FFFFFF !important;
            padding: 8px 10px;
            border-radius: 4px;
            margin-bottom: 4px;
            border: 1px solid #EAEAEA;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
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
            margin-bottom: 12px;
            margin-top: 10px;
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
        }
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & API Settings
API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN", "placeholder")
COMPETITION_CODE = "WC"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_TOKEN}

SWEEPSTAKE_MAPPING = {
    "Mexico": "TBC", "South Africa": "TBC", "Canada": "TBC", "Switzerland": "TBC",
    "Argentina": "TBC", "France": "TBC", "Brazil": "TBC", "Spain": "TBC",
    "Bosnia-Herzegovina": "Izzy", "Czechia": "TBC", "Qatar": "TBC", "Morocco": "TBC",
    "Haiti": "TBC", "Turkey": "TBC", "Paraguay": "TBC", "Germany": "TBC",
    "Curaçao": "TBC", "Ecuador": "TBC", "Japan": "TBC", "Belgium": "TBC",
    "Egypt": "TBC", "Tunisia": "TBC", "Netherlands": "TBC", "Ivory Coast": "TBC",
    "Australia": "TBC", "Cape Verde Islands": "TBC", "Uruguay": "TBC", "Sweden": "TBC",
    "Saudi Arabia": "TBC", "Scotland": "TBC", "United States": "TBC", "Senegal": "TBC",
    "New Zealand": "TBC", "Iran": "TBC", "Iraq": "TBC", "Norway": "TBC",
    "Algeria": "TBC", "Austria": "TBC", "Jordan": "TBC", "Congo DR": "TBC",
    "Portugal": "TBC", "Uzbekistan": "TBC", "Colombia": "TBC", "England": "TBC",
    "Panama": "TBC", "Ghana": "TBC", "Croatia": "TBC", "South Korea": "TBC",
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

# --- DYNAMIC BANNER TEAM COLOR MAPPING ---
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

DEFAULT_LEFT_COLOR = "#006847"   # Mexico Green
DEFAULT_RIGHT_COLOR = "#007A4D"  # South Africa Green

def format_to_uk_time(utc_str):
    try:
        dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = pytz.utc.localize(dt)
        uk_tz = pytz.timezone("Europe/London")
        return dt_utc.astimezone(uk_tz)
    except Exception:
        return None

# Fallbacks
next_home = "Mexico"
next_away = "South Africa"
next_home_owner = " (TBC)"
next_away_owner = " (TBC)"
next_date = "11th June @ 20:00"
next_home_flag = ""
next_away_flag = ""

all_matches = []
standings_list = []
master_flat_leaderboard = []
top_performer_text = "N/A"

# Set initial banner colours to fallbacks
banner_left_color = DEFAULT_LEFT_COLOR
banner_right_color = DEFAULT_RIGHT_COLOR

if API_TOKEN != "placeholder":
    try:
        # Fetch Standings
        standings_url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/standings"
        standings_res = requests.get(standings_url, headers=HEADERS)
        standings_list = standings_res.json().get("standings", [])
        
        for group in standings_list:
            for row in group.get("table", []):
                t_info = row.get("team", {})
                master_flat_leaderboard.append({
                    "name": t_info.get("name", "Unknown"),
                    "crest": t_info.get("crest", ""),
                    "played": row.get("playedGames", 0),
                    "won": row.get("won", 0),
                    "drawn": row.get("draw", 0),
                    "lost": row.get("lost", 0),
                    "gf": row.get("goalsFor", 0),
                    "ga": row.get("goalsAgainst", 0),
                    "gd": row.get("goalDifference", 0),
                    "pts": row.get("points", 0)
                })
        
        if master_flat_leaderboard:
            master_flat_leaderboard.sort(key=lambda x: (-x["pts"], -x["won"], -x["gd"], -x["gf"], x["name"]))
            for idx, team_item in enumerate(master_flat_leaderboard, start=1):
                name = team_item["name"]
                expected_rank = EXPECTED_RANKINGS.get(name, 25)
                team_item["actual_rank"] = idx
                team_item["expected_rank"] = expected_rank
                team_item["overperformance"] = expected_rank - idx
            
            best_overperformer = max(master_flat_leaderboard, key=lambda x: (x["overperformance"], -x["actual_rank"]))
            op_owner = SWEEPSTAKE_MAPPING.get(best_overperformer["name"], "Unassigned")
            top_performer_text = f"{best_overperformer['name']} ({op_owner}) [+{best_overperformer['overperformance']}]"
        
        # Fetch Matches
        matches_url = f"{BASE_URL}/competitions/{COMPETITION_CODE}/matches"
        matches_res = requests.get(matches_url, headers=HEADERS)
        all_matches = matches_res.json().get("matches", [])
        
        if all_matches:
            upcoming_matches = [m for m in all_matches if m.get("status") in ["TIMED", "SCHEDULED"]]
            if upcoming_matches:
                upcoming_matches.sort(key=lambda x: x.get("utcDate", ""))
                next_m = upcoming_matches[0]
                
                home_team_obj = next_m.get("homeTeam", {})
                away_team_obj = next_m.get("awayTeam", {})
                
                next_home = home_team_obj.get("name", "TBD")
                next_away = away_team_obj.get("name", "TBD")
                
                # Fetch dynamically matching colours
                banner_left_color = TEAM_COLORS.get(next_home, DEFAULT_LEFT_COLOR)
                banner_right_color = TEAM_COLORS.get(next_away, DEFAULT_RIGHT_COLOR)
                
                # Special Case: If both countries have the same colour
                if banner_left_color == banner_right_color:
                    banner_right_color = "#222222" if banner_left_color != "#222222" else "#555555"

                if home_team_obj.get("crest"):
                    next_home_flag = f'<img src="{home_team_obj.get("crest")}" class="banner-flag">'
                if away_team_obj.get("crest"):
                    next_away_flag = f'<img src="{away_team_obj.get("crest")}" class="banner-flag">'
                
                next_home_owner = f" ({SWEEPSTAKE_MAPPING.get(next_home, 'Unassigned')})"
                next_away_owner = f" ({SWEEPSTAKE_MAPPING.get(next_away, 'Unassigned')})"
                
                dt_uk = format_to_uk_time(next_m.get("utcDate"))
                if dt_uk:
                    day = dt_uk.day
                    suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
                    next_date = dt_uk.strftime(f"{day}{suffix} %B @ %H:%M")
    except Exception:
        pass

# --- HEADER ---
st.markdown("""
    <div class="title-area">
        <h1>🏆 KING FAMILY WORLD CUP SWEEPSTAKE</h1>
        <p>Live standings</p>
    </div>
""", unsafe_allow_html=True)

# --- DYNAMIC COLOURED, CENTRED MATCHUP BANNER ---
# Explicitly using string chunks to prevent f-string parser collisions with CSS braces
banner_html = (
    '<div class="match-banner-container">'
    '    <div class="banner-top-pane">'
    '        <div class="next-match-title">⏳ Next Match</div>'
    '    </div>'
    '    '
    '    <div class="matchup-split-screen">'
    '        <div class="team-panel home-panel" style="background-color: ' + banner_left_color + ';">'
    '            <div class="team-panel-text">'
    '                ' + next_home_flag + ' ' + next_home + ' <span>' + next_home_owner + '</span>'
    '            </div>'
    '        </div>'
    '        '
    '        <div class="vs-marker-bubble">VS</div>'
    '        '
    '        <div class="team-panel away-panel" style="background-color: ' + banner_right_color + ';">'
    '            <div class="team-panel-text">'
    '                <span>' + next_away_owner + '</span> ' + next_away + ' ' + next_away_flag + ''
    '            </div>'
    '        </div>'
    '    </div>'
    '    '
    '    <div class="banner-bottom-time">🗓️ ' + next_date + '</div>'
    '</div>'
)
st.markdown(banner_html, unsafe_allow_html=True)

# --- STATS ROW ---
stat_cols = st.columns(3)
with stat_cols[0]:
    st.markdown('<div class="stat-banner-box"><medium>💰 Prize Pot</medium><span>£96</span></div>', unsafe_allow_html=True)
with stat_cols[1]:
    fave_owner = SWEEPSTAKE_MAPPING.get("France", "Unassigned")
    st.markdown(f'<div class="stat-banner-box"><medium>⭐ Favourites</medium><span>France ({fave_owner})</span></div>', unsafe_allow_html=True)
with stat_cols[2]:
    st.markdown(f'<div class="stat-banner-box"><medium>🚀 Overperformer</medium><span>{top_performer_text}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px 25px 0px; border-top: 2px solid #006847;'>", unsafe_allow_html=True)

# --- GROUPS CANVAS ---
if API_TOKEN == "placeholder":
    st.warning("⚠️ Using placeholder API key. Please insert your true Football-Data.org token to pull live group lists and matches.")
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
                            t_crest = team_info.get("crest", "")
                            owner = SWEEPSTAKE_MAPPING.get(t_name, "Unassigned")
                            flag_html = f'<img src="{t_crest}" class="flag-img">' if t_crest else ''
                            
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
                        
                        st.markdown("<span style='font-size:12px; font-weight:700; color:#006847; display:block; margin-bottom:6px;'>📅 Group Fixtures & Results</span>", unsafe_allow_html=True)
                        group_fixtures = [m for m in all_matches if m.get("homeTeam", {}).get("name") in teams_in_group or m.get("awayTeam", {}).get("name") in teams_in_group]
                        
                        if not group_fixtures:
                            st.caption("No fixtures currently listed for this group.")
                        else:
                            group_fixtures.sort(key=lambda x: x.get("utcDate", ""))
                            for match in group_fixtures[:6]:
                                m_status = match.get("status")
                                home_t, away_t = match.get("homeTeam", {}), match.get("awayTeam", {})
                                h_name, a_name = home_t.get("name", "TBD"), away_t.get("name", "TBD")
                                h_owner, a_owner = SWEEPSTAKE_MAPPING.get(h_name, "Unassigned"), SWEEPSTAKE_MAPPING.get(a_name, "Unassigned")
                                
                                dt_uk = format_to_uk_time(match.get("utcDate"))
                                local_time_str = dt_uk.strftime("%d/%m %H:%M") if dt_uk else "TBD"
                                h_flag = f'<img src="{home_t.get("crest", "")}" class="flag-img">' if home_t.get("crest") else ''
                                a_flag = f'<img src="{away_t.get("crest", "")}" class="flag-img">' if away_t.get("crest") else ''
                                
                                if m_status == "FINISHED":
                                    display_score = f"<b>{match.get('score', {}).get('fullTime', {}).get('home')} - {match.get('score', {}).get('fullTime', {}).get('away')}</b>"
                                elif m_status in ["IN_PLAY", "PAUSED"]:
                                    display_score = f"<span style='color:red; font-weight:700;'>🔴 {match.get('score', {}).get('fullTime', {}).get('home', 0)}-{match.get('score', {}).get('fullTime', {}).get('away', 0)}</span>"
                                else:
                                    display_score = f"<span style='color:#777; font-weight:500;'>{local_time_str}</span>"
                                
                                st.markdown(f"""
                                    <div class="fixture-row">
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
                        st.markdown("<br>", unsafe_allow_html=True)

        # --- OVERPERFORMANCE LEADERBOARD ---
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
            flag_html = f'<img src="{team_row["crest"]}" class="flag-img">' if team_row["crest"] else ''
            
            pos_str = f"🚀 {display_idx}" if display_idx == 1 else str(display_idx)
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
                <td style='text-align:center;'>{team_row['pts']}</td>
                <td style='text-align:right; padding-right:15px; color:{score_color}; font-weight:bold;'>{op_formatted}</td>
            </tr>"""
            
        master_table_html += "</tbody></table></div>"
        
        m_center_cols = st.columns([1, 10, 1])
        with m_center_cols[1]:
            st.markdown(master_table_html, unsafe_allow_html=True)
