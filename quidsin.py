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
    page_title="Byway World Cup Sweepstake",
    page_icon="⚽",
    layout="wide"
)

# Run page auto-refresh every 3 minutes to keep live scores syncing
st_autorefresh(interval=180 * 1000, key="datarefresh")

# Custom branding & layout styles
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
            color: #ff7d23 !important;
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
        /* Top panes */
        .banner-top-pane {
            background-color: #ff7d23;
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
        /* Match layout */
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
        /* Bottom bars */
        .banner-bottom-time {
            background-color: #ff7d23;
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
            background-color: #444444 !important;
            padding: 10px 15px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            border-top: 1px solid #EEEEEE !important;
        }
        .highlights-btn {
            background-color: #444444 !important;
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
        /* Flags */
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
        /* Additional styles omitted for brevity... (keep your existing styles) */
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & API Settings
API_TOKEN = st.secrets.get("FOOTBALL_API_TOKEN", os.environ.get("FOOTBALL_API_TOKEN", "placeholder"))
COMPETITION_CODE = "WC"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_TOKEN}

# ... (your other code remains unchanged) ...

# ── Modified build_match_banner to include show_score parameter ──
def build_match_banner(match, is_live=False, is_result=False, match_idx=2, show_score=False, score_text=""):
    home_team_obj = match.get("homeTeam", {})
    away_team_obj = match.get("awayTeam", {})

    h_name = home_team_obj.get("name", "TBD")
    a_name = away_team_obj.get("name", "TBD")

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
        h_score, a_score = get_live_score(match)
        top_pane = '<div class="inplay-top-pane"><div class="next-match-title">🔴 Live now</div></div>'
        centre_bubble = f'<div class="score-bubble">{h_score} – {a_score}</div>'
        bottom_bar = '<div class="inplay-bottom-bar">⚽ Match in progress</div>'
    elif is_result:
        h_score, a_score = get_live_score(match)
        highlights_url = get_spreadsheet_url_fallback(h_name, a_name)
        top_pane = '<div class="result-top-pane"><div class="next-match-title" style="background: rgba(0,0,0,0.2);">✅ Latest Result</div></div>'
        # Decide display of score
        if show_score:
            centre_bubble = f'<div class="score-bubble score-bubble-compact">{score_text}</div>'
        else:
            centre_bubble = f'<div class="score-bubble score-bubble-compact" style="cursor:pointer;">Show Score</div>'
        bottom_bar = f'<div class="result-bottom-bar"><a href="{highlights_url}" target="_blank" class="highlights-btn">📺 Watch Highlights</a></div>'
    else:
        dt_uk = format_to_uk_time(match.get("utcDate"))
        if dt_uk:
            day = dt_uk.day
            suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
            date_str = dt_uk.strftime(f"{day}{suffix} %B @ %H:%M")
        else:
            date_str = "TBD"
        top_pane = '<div class="banner-top-pane"><div class="next-match-title">⏳ Next match</div></div>'
        centre_bubble = '<div class="vs-marker-bubble">VS</div>'
        bottom_bar = f'<div class="banner-bottom-time">🗓️ {date_str}</div>'

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

# ── Main code to display header with side-by-side latest result and next match ──
# Create two columns for side-by-side display
header_cols = st.columns([1, 1])

with header_cols[0]:
    if finished_matches:
        latest_match = finished_matches[0]
        chronological_matches = sorted(all_matches, key=lambda x: x.get("utcDate", ""))
        try:
            match_index = chronological_matches.index(latest_match) + 2
        except ValueError:
            match_index = 2

        match_id = id(latest_match)
        show_score_state = st.session_state.get(f"show_score_{match_id}", False)

        # Build banner with toggle logic
        def get_build_html(show_score):
            return build_match_banner(latest_match, is_live=False, is_result=True, match_idx=match_index, show_score=show_score, score_text=f"{get_live_score(latest_match)[0]} – {get_live_score(latest_match)[1]}")

        # Button to toggle score
        if st.button("Show Score", key=f"btn_{match_id}"):
            st.session_state[f"show_score_{match_id}"] = not show_score_state
            show_score_state = not show_score_state

        html_content = get_build_html(show_score_state)
        st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

with header_cols[1]:
    if upcoming_matches:
        next_match = upcoming_matches[0]
        html_next = build_match_banner(next_match, is_live=False)
        st.markdown(html_next, unsafe_allow_html=True)
    else:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
