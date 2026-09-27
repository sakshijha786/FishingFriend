"""
FishingFriend - ORCA Marine Multi-Agent AI & Tactical Maritime Cockpit
Problem Statement: ISRO Smart India Hackathon SIH26176 / sih_176

Professional Marine Intelligence & Fishing Operations Platform:
- Collapsible Navigation Drawer & Rail Architecture (Zero radio buttons, clean active states)
- Radically simplified, calm Operational Dashboard
- Reusable, properly spaced SectionTabs navigation
- Centralized semantic token design system (100% dark mode / light mode contrast)
- 100% Functionality Preservation across all APIs, calculations, layers, tides, forecasts, and safety rules
"""

from __future__ import annotations
import sys
import os
import math
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
import altair as alt

from marine_tools import (
    INDIAN_PORTS,
    IMBL_BOUNDARIES,
    PortLocation,
    OceanTelemetry,
    HazardEvaluation,
    PFZZone,
    RouteWaypoints,
    EmergencyContact,
    get_emergency_contacts,
    PortTideData,
    TideExtreme,
    TideHeightPoint,
    HourlyMarineForecast,
    HourlyMarineData,
    calculate_port_tides,
    fetch_hourly_marine_forecast,
    fetch_rainviewer_radar_url,
    get_marine_spatial_zones,
    MarineSpatialZone,
    MARINE_PROTECTED_AREAS
)
from agent_core import MultiAgentOrchestrator, ORCASynthesisResult

# ---------------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="FishingFriend | Marine Operations Platform",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CENTRALIZED SEMANTIC DESIGN SYSTEM & CSS TOKENS
# ---------------------------------------------------------

def inject_theme(theme_name: str):
    """
    Injects a centralized semantic token system that guarantees high contrast,
    subtle modern borders, consistent typography, and zero invisible buttons/text.
    """
    if "Day" in theme_name or "Light" in theme_name:
        # ☀️ Ocula Sky Day (Light Mode)
        theme_vars = """
            --bg-page: #f8fafc;
            --bg-surface: #ffffff;
            --bg-surface-hover: #f1f5f9;
            --bg-elevated: #ffffff;
            --bg-subtle: #f0f9ff;
            --bg-drawer: #ffffff;
            --card-bg: #ffffff;
            --card-border: #e2e8f0;
            --card-border-active: #0284c7;
            --text-primary: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            --text-on-primary: #ffffff;
            --border: #cbd5e1;
            --border-strong: #94a3b8;
            --primary: #0284c7;
            --primary-hover: #0369a1;
            --primary-subtle: rgba(2, 132, 199, 0.12);
            --secondary: #0ea5e9;
            --accent: #0284c7;
            --success: #16a34a;
            --success-bg: rgba(22, 163, 74, 0.10);
            --warning: #d97706;
            --warning-bg: rgba(217, 119, 6, 0.10);
            --danger: #dc2626;
            --danger-bg: rgba(220, 38, 38, 0.10);
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
            --shadow-md: 0 4px 14px rgba(15, 23, 42, 0.08);
            --shadow-lg: 0 8px 24px rgba(15, 23, 42, 0.12);
            --chart-main: #0284c7;
            --chart-sec: #0ea5e9;
            --chart-subtle: #64748b;
            --btn-bg: #f1f5f9;
            --btn-bg-hover: #e2e8f0;
            --btn-text: #0f172a;
            --btn-border: #cbd5e1;
            --btn-primary-bg: #0284c7;
            --btn-primary-bg-hover: #0369a1;
            --btn-primary-text: #ffffff;
            --btn-primary-border: #0284c7;
        """
        leaflet_tile = "cartodbpositron"
    elif "Tactical" in theme_name:
        # ⚡ Tactical Radar Cockpit (Cyber-GIS Dark)
        theme_vars = """
            --bg-page: #030712;
            --bg-surface: #0b1426;
            --bg-surface-hover: #11203b;
            --bg-elevated: #142544;
            --bg-subtle: #0a221a;
            --bg-drawer: #070e1c;
            --card-bg: #0b1426;
            --card-border: #1e2f47;
            --card-border-active: #10b981;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --text-on-primary: #030712;
            --border: #1e2f47;
            --border-strong: #2e4669;
            --primary: #10b981;
            --primary-hover: #059669;
            --primary-subtle: rgba(16, 185, 129, 0.14);
            --secondary: #00ff88;
            --accent: #06b6d4;
            --success: #10b981;
            --success-bg: rgba(16, 185, 129, 0.14);
            --warning: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.14);
            --danger: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.14);
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.4);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.45);
            --shadow-lg: 0 8px 28px rgba(0, 0, 0, 0.55);
            --chart-main: #10b981;
            --chart-sec: #06b6d4;
            --chart-subtle: #94a3b8;
            --btn-bg: #0f1f38;
            --btn-bg-hover: #172f53;
            --btn-text: #f8fafc;
            --btn-border: #244169;
            --btn-primary-bg: #10b981;
            --btn-primary-bg-hover: #059669;
            --btn-primary-text: #030712;
            --btn-primary-border: #10b981;
        """
        leaflet_tile = "cartodbdark_matter"
    else:
        # 🌙 Ocula Oceanic Dark (Deep Abyss Navy - Default)
        theme_vars = """
            --bg-page: #07111f;
            --bg-surface: #0e1d32;
            --bg-surface-hover: #152943;
            --bg-elevated: #14253e;
            --bg-subtle: #0a2240;
            --bg-drawer: #091628;
            --card-bg: #0e1d32;
            --card-border: #1e3552;
            --card-border-active: #38bdf8;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #8da2ba;
            --text-on-primary: #07111f;
            --border: #1e3552;
            --border-strong: #2b4970;
            --primary: #38bdf8;
            --primary-hover: #0ea5e9;
            --primary-subtle: rgba(56, 189, 248, 0.12);
            --secondary: #0ea5e9;
            --accent: #7dd3fc;
            --success: #22c55e;
            --success-bg: rgba(34, 197, 94, 0.12);
            --warning: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.12);
            --danger: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.12);
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.25);
            --shadow-md: 0 4px 14px rgba(0, 0, 0, 0.35);
            --shadow-lg: 0 8px 28px rgba(0, 0, 0, 0.45);
            --chart-main: #38bdf8;
            --chart-sec: #0ea5e9;
            --chart-subtle: #8da2ba;
            --btn-bg: #10223a;
            --btn-bg-hover: #183356;
            --btn-text: #f8fafc;
            --btn-border: #23436a;
            --btn-primary-bg: #38bdf8;
            --btn-primary-bg-hover: #0ea5e9;
            --btn-primary-text: #07111f;
            --btn-primary-border: #38bdf8;
        """
        leaflet_tile = "cartodbdark_matter"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    :root {{
        {theme_vars}
    }}

    /* Global App Container */
    .stApp {{
        background: var(--bg-page) !important;
        color: var(--text-primary) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }}

    .main .block-container {{
        max-width: 1440px !important;
        padding-top: 1.0rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
    }}

    /* Global Text Overrides */
    h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: inherit;
    }}
    .stMarkdown, .stText {{
        color: var(--text-primary) !important;
    }}

    /* Streamlit Native Sidebar Overrides: Drawer Architecture */
    [data-testid="stSidebar"] {{
        background: var(--bg-drawer) !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: var(--shadow-lg);
    }}
    [data-testid="stSidebar"] * {{
        color: var(--text-primary) !important;
    }}
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    /* Top Header Shell */
    .ff-header-shell {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-sm);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: wrap;
    }}

    /* Clean Card Container */
    .ff-card {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: var(--shadow-sm);
        transition: border-color 0.15s ease;
    }}
    .ff-card:hover {{
        border-color: var(--card-border-active);
    }}

    /* Operational Clearance Hero Card */
    .ff-status-panel {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-sm);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }}
    .ff-status-safe {{
        border-left: 5px solid var(--success) !important;
        background: var(--success-bg) !important;
    }}
    .ff-status-caution {{
        border-left: 5px solid var(--warning) !important;
        background: var(--warning-bg) !important;
    }}
    .ff-status-danger {{
        border-left: 5px solid var(--danger) !important;
        background: var(--danger-bg) !important;
    }}

    /* Unified Horizontal Metric Strip */
    .ff-metric-strip {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 20px;
        box-shadow: var(--shadow-sm);
    }}
    .ff-metric-item {{
        text-align: center;
        border-right: 1px solid var(--border);
        padding-right: 12px;
    }}
    .ff-metric-item:last-child {{
        border-right: none;
        padding-right: 0;
    }}
    .ff-metric-label {{
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: var(--text-muted);
        margin-bottom: 4px;
    }}
    .ff-metric-value {{
        font-size: 22px;
        font-weight: 800;
        color: var(--primary);
        font-family: 'JetBrains Mono', monospace;
    }}
    .ff-metric-sub {{
        font-size: 11px;
        color: var(--text-secondary);
        margin-top: 3px;
    }}

    /* ========================================================= */
    /* SELECTBOX & DROPDOWN TOTAL THEME OVERRIDE                 */
    /* Works flawlessly across Light, Dark, and Tactical Themes  */
    /* ========================================================= */

    .stSelectbox,
    div[data-testid="stSelectbox"],
    div[data-baseweb="select"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    /* Outer selectbox control wrapper */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {{
        background-color: var(--bg-surface) !important;
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        min-height: 38px !important;
        box-shadow: var(--shadow-sm) !important;
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
    }}

    /* Hover state for selectboxes */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
    div[data-baseweb="select"] > div:hover {{
        border-color: var(--primary) !important;
        background-color: var(--bg-surface-hover) !important;
        background: var(--bg-surface-hover) !important;
    }}

    /* All inner text nodes in selectbox */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] p,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] input,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] p,
    div[data-baseweb="select"] input {{
        background-color: transparent !important;
        background: transparent !important;
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }}

    /* Dropdown chevron arrow */
    div[data-baseweb="select"] svg,
    div[data-baseweb="select"] svg path {{
        fill: var(--text-primary) !important;
        color: var(--text-primary) !important;
    }}

    /* Dropdown Popover Menus & Lists (Rendered in Portal) */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div {{
        background-color: var(--bg-surface) !important;
        background: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        box-shadow: var(--shadow-lg) !important;
        padding: 4px !important;
    }}

    ul[role="listbox"] {{
        background-color: var(--bg-surface) !important;
        background: var(--bg-surface) !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    li[role="option"] {{
        background-color: var(--bg-surface) !important;
        background: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        border: none !important;
    }}

    li[role="option"] * {{
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        background: transparent !important;
        border: none !important;
    }}

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {{
        background-color: var(--bg-surface-hover) !important;
        background: var(--bg-surface-hover) !important;
        color: var(--primary) !important;
        -webkit-text-fill-color: var(--primary) !important;
    }}

    li[role="option"]:hover *,
    li[role="option"][aria-selected="true"] * {{
        color: var(--primary) !important;
        -webkit-text-fill-color: var(--primary) !important;
    }}

    /* Text Inputs & Textareas */
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] input {{
        background-color: var(--bg-surface) !important;
        background: var(--bg-surface) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        border-radius: 8px !important;
    }}
    input, textarea {{
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        background: transparent !important;
    }}
    input::placeholder, textarea::placeholder {{
        color: var(--text-muted) !important;
        -webkit-text-fill-color: var(--text-muted) !important;
    }}

    /* ========================================================= */
    /* COMPREHENSIVE STREAMLIT BUTTON OVERRIDES                  */
    /* Fixes all white-on-white and dark-on-dark contrast bugs  */
    /* ========================================================= */

    /* 1. Default & Secondary Buttons */
    div[data-testid="stButton"] > button:not([data-testid*="primary"]):not([kind="primary"]),
    div[data-testid="stButton"] button:not([data-testid*="primary"]):not([kind="primary"]),
    div[data-testid="stDownloadButton"] > button:not([data-testid*="primary"]):not([kind="primary"]),
    div[data-testid="stFormSubmitButton"] > button:not([data-testid*="primary"]):not([kind="primary"]),
    button[data-testid="baseButton-secondary"],
    button[data-testid="stBaseButton-secondary"],
    button[kind="secondary"] {{
        background-color: var(--btn-bg) !important;
        background: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        -webkit-text-fill-color: var(--btn-text) !important;
        border: 1px solid var(--btn-border) !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.1rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.15s ease !important;
    }}

    div[data-testid="stButton"] > button:not([data-testid*="primary"]):not([kind="primary"]) *,
    div[data-testid="stButton"] button:not([data-testid*="primary"]):not([kind="primary"]) *,
    button[data-testid="baseButton-secondary"] *,
    button[data-testid="stBaseButton-secondary"] *,
    button[kind="secondary"] * {{
        color: var(--btn-text) !important;
        -webkit-text-fill-color: var(--btn-text) !important;
    }}

    div[data-testid="stButton"] > button:not([data-testid*="primary"]):not([kind="primary"]):hover,
    div[data-testid="stButton"] button:not([data-testid*="primary"]):not([kind="primary"]):hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:hover,
    button[kind="secondary"]:hover {{
        background-color: var(--btn-bg-hover) !important;
        background: var(--btn-bg-hover) !important;
        border-color: var(--primary) !important;
        color: var(--primary) !important;
        -webkit-text-fill-color: var(--primary) !important;
    }}

    div[data-testid="stButton"] > button:not([data-testid*="primary"]):not([kind="primary"]):hover *,
    div[data-testid="stButton"] button:not([data-testid*="primary"]):not([kind="primary"]):hover *,
    button[data-testid="baseButton-secondary"]:hover *,
    button[data-testid="stBaseButton-secondary"]:hover *,
    button[kind="secondary"]:hover * {{
        color: var(--primary) !important;
        -webkit-text-fill-color: var(--primary) !important;
    }}

    /* 2. Primary Buttons (type="primary") */
    div[data-testid="stButton"] > button[data-testid*="primary"],
    div[data-testid="stButton"] button[data-testid*="primary"],
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stButton"] button[kind="primary"],
    button[data-testid="baseButton-primary"],
    button[data-testid="stBaseButton-primary"],
    button[kind="primary"] {{
        background-color: var(--btn-primary-bg) !important;
        background: var(--btn-primary-bg) !important;
        color: var(--btn-primary-text) !important;
        -webkit-text-fill-color: var(--btn-primary-text) !important;
        border: 1px solid var(--btn-primary-border) !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        box-shadow: var(--shadow-sm) !important;
        padding: 0.5rem 1.1rem !important;
    }}

    div[data-testid="stButton"] > button[data-testid*="primary"] *,
    div[data-testid="stButton"] button[data-testid*="primary"] *,
    div[data-testid="stButton"] > button[kind="primary"] *,
    div[data-testid="stButton"] button[kind="primary"] *,
    button[data-testid="baseButton-primary"] *,
    button[data-testid="stBaseButton-primary"] *,
    button[kind="primary"] * {{
        color: var(--btn-primary-text) !important;
        -webkit-text-fill-color: var(--btn-primary-text) !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stButton"] > button[data-testid*="primary"]:hover,
    div[data-testid="stButton"] button[data-testid*="primary"]:hover,
    div[data-testid="stButton"] > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    button[kind="primary"]:hover {{
        background-color: var(--btn-primary-bg-hover) !important;
        background: var(--btn-primary-bg-hover) !important;
        border-color: var(--btn-primary-bg-hover) !important;
        color: var(--btn-primary-text) !important;
        -webkit-text-fill-color: var(--btn-primary-text) !important;
    }}

    div[data-testid="stButton"] > button[data-testid*="primary"]:hover *,
    div[data-testid="stButton"] button[data-testid*="primary"]:hover *,
    button[data-testid="baseButton-primary"]:hover *,
    button[data-testid="stBaseButton-primary"]:hover *,
    button[kind="primary"]:hover * {{
        color: var(--btn-primary-text) !important;
        -webkit-text-fill-color: var(--btn-primary-text) !important;
    }}

    /* 3. Header Emergency SOS Button (6th Column in Header Bar) */
    div[data-testid="column"]:nth-child(6) div[data-testid="stButton"] > button {{
        background-color: #dc2626 !important;
        background: #dc2626 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #b91c1c !important;
        font-weight: 800 !important;
        box-shadow: 0 0 10px rgba(220, 38, 38, 0.4) !important;
        white-space: nowrap !important;
    }}

    div[data-testid="column"]:nth-child(6) div[data-testid="stButton"] > button * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 800 !important;
        white-space: nowrap !important;
    }}

    div[data-testid="column"]:nth-child(6) div[data-testid="stButton"] > button:hover {{
        background-color: #b91c1c !important;
        background: #b91c1c !important;
        border-color: #991b1b !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    /* 4. Sidebar Drawer Navigation Buttons */
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:not([data-testid*="primary"]):not([kind="primary"]),
    [data-testid="stSidebar"] div[data-testid="stButton"] > button {{
        background-color: transparent !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        color: var(--text-secondary) !important;
        -webkit-text-fill-color: var(--text-secondary) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin-bottom: 4px !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebar"] div[data-testid="stButton"] > button * {{
        color: var(--text-secondary) !important;
        -webkit-text-fill-color: var(--text-secondary) !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }}
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
        background-color: var(--bg-surface-hover) !important;
        background: var(--bg-surface-hover) !important;
        border-color: transparent !important;
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
    }}
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover * {{
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
    }}
    [data-testid="stSidebar"] div[data-testid="stButton"] > button[data-testid*="primary"],
    [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {{
        background-color: var(--primary-subtle) !important;
        background: var(--primary-subtle) !important;
        border-left: 4px solid var(--primary) !important;
        border-top: 1px solid transparent !important;
        border-right: 1px solid transparent !important;
        border-bottom: 1px solid transparent !important;
        color: var(--primary) !important;
        -webkit-text-fill-color: var(--primary) !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebar"] div[data-testid="stButton"] > button[data-testid*="primary"] *,
    [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] * {{
        color: var(--primary) !important;
        -webkit-text-fill-color: var(--primary) !important;
        font-weight: 700 !important;
    }}

    /* 5. Segmented Control Buttons */
    div[data-testid="stSegmentedControl"] button,
    div[data-testid="stSegmentedControl"] [data-testid="stBaseButton-secondary"] {{
        background-color: var(--btn-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
    }}
    div[data-testid="stSegmentedControl"] button[aria-checked="true"],
    div[data-testid="stSegmentedControl"] button[aria-selected="true"],
    div[data-testid="stSegmentedControl"] [data-testid="stBaseButton-primary"] {{
        background-color: var(--primary) !important;
        color: var(--text-on-primary) !important;
        border-color: var(--primary) !important;
    }}
    div[data-testid="stSegmentedControl"] button * {{
        color: inherit !important;
    }}

    /* Modals & Overlays */
    .ff-modal-box {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-lg);
    }}

    /* Animated Ocean Current Flow */
    @keyframes flowCurrentStream {{
        from {{ stroke-dashoffset: 40; }}
        to {{ stroke-dashoffset: 0; }}
    }}
    path.animated-current-flow {{
        stroke-dasharray: 8, 14 !important;
        animation: flowCurrentStream 1.2s linear infinite !important;
    }}

    /* Clean Table and Dataframe */
    .stDataFrame {{
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid var(--border);
    }}
    </style>
    """, unsafe_allow_html=True)
    return leaflet_tile


# ---------------------------------------------------------
# INTERACTIVE GEOSPATIAL MAP ENGINE
# ---------------------------------------------------------

def render_tactical_map(
    port: PortLocation,
    telemetry: OceanTelemetry,
    safety: HazardEvaluation,
    all_pfzs: List[PFZZone],
    selected_pfz: PFZZone,
    route: RouteWaypoints,
    theme_name: str,
    height: int = 560
):
    """
    Renders the interactive Leaflet tactical geospatial map containing all
    nautical, bathymetric, bio-optical, and animated streamline layers.
    """
    base_tiles = "cartodbpositron" if ("Day" in theme_name or "Light" in theme_name) else "cartodbdark_matter"

    m = folium.Map(
        location=[port.lat, port.lon],
        zoom_start=9,
        tiles=base_tiles,
        name="Standard Chart",
        control_scale=True
    )

    # Layer 1: ESRI World Ocean Bathymetry (GEBCO / NOAA Submarine Contours)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, National Geographic",
        name="🌊 Ocean Bathymetry (GEBCO / NOAA)",
        overlay=False,
        control=True
    ).add_to(m)

    # Layer 2: OpenSeaMap Nautical Seamarks (Buoys, Beacons, Depths, Shoals)
    folium.TileLayer(
        tiles="https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
        attr="Map data &copy; <a href='http://www.openseamap.org'>OpenSeaMap</a> contributors",
        name="⚓ OpenSeaMap (Nautical Marks, Buoys, Lights)",
        overlay=True,
        control=True,
        show=True
    ).add_to(m)

    # Layer 3: Live Doppler Rain Radar (RainViewer)
    radar_url = fetch_rainviewer_radar_url()
    if radar_url:
        folium.TileLayer(
            tiles=radar_url,
            attr="Weather Radar &copy; RainViewer",
            name="🌧️ Live Doppler Rain Radar",
            overlay=True,
            control=True,
            opacity=0.65,
            show=False
        ).add_to(m)

    # Layer 4: Marine Protected Areas & Conservation Reserves (MarineMap MSP)
    mpa_group = folium.FeatureGroup(name="🛡️ Marine Protected Areas (MarineMap MSP)", show=True)
    for mpa in get_marine_spatial_zones(port.id):
        folium.Polygon(
            locations=mpa.coordinates,
            color=mpa.color,
            weight=2.5,
            fill=True,
            fill_color=mpa.color,
            fill_opacity=0.22,
            tooltip=f"🛡️ {mpa.name} ({mpa.category})",
            popup=folium.Popup(f"""
            <div style="font-family: sans-serif; font-size: 12px; color: #0f172a; min-width: 250px;">
                <h4 style="margin:0 0 6px 0; color:{mpa.color};">🛡️ {mpa.name}</h4>
                <b>Category:</b> {mpa.category}<br>
                <p style="margin:6px 0; font-size:11px; line-height:1.4;">{mpa.restriction}</p>
                <span style="font-size:10px; color:#64748b;"><b>Legal Basis:</b> {mpa.legal_source}</span>
            </div>
            """, max_width=320)
        ).add_to(mpa_group)
    mpa_group.add_to(m)

    # Layer 5: Harbor Base Station Marker
    harbor_popup = f"""
    <div style="font-family: sans-serif; font-size: 13px; color: #0f172a; min-width: 210px;">
        <h4 style="margin:0 0 6px 0; color:#0284c7;">⚓ {port.name}</h4>
        <b>Wave:</b> {telemetry.wave_height}m | <b>Swell:</b> {telemetry.swell_wave_height}m ({telemetry.swell_wave_period}s)<br>
        <b>SST:</b> {telemetry.sea_surface_temperature}°C | <b>Wind:</b> {telemetry.wind_speed} km/h<br>
        <b>Current:</b> {telemetry.ocean_current_velocity} km/h @ {telemetry.ocean_current_direction:.0f}°<br>
        <span style="display:inline-block; margin-top:5px; font-weight:bold; color:{'#16a34a' if safety.status=='SAFE_GO' else '#dc2626'};">
            {safety.status.replace('_', ' ')}
        </span>
    </div>
    """
    folium.Marker(
        location=[port.lat, port.lon],
        tooltip=f"Base Harbor: {port.name}",
        popup=folium.Popup(harbor_popup, max_width=300),
        icon=folium.Icon(color="blue", icon="anchor", prefix="fa")
    ).add_to(m)

    # Layer 6: Potential Fishing Zones (PFZ)
    pfz_group = folium.FeatureGroup(name="🐟 Potential Fishing Zones (PFZ)", show=True)
    for pfz in all_pfzs:
        is_selected = (pfz.zone_id == selected_pfz.zone_id)
        zone_color = "#0284c7" if is_selected else "#38bdf8"

        pfz_popup = f"""
        <div style="font-family: sans-serif; font-size: 12px; color: #0f172a; min-width: 220px;">
            <h4 style="margin:0 0 4px 0; color:#0284c7;">🐟 {pfz.name}</h4>
            <b>Catch Probability:</b> <span style="color:#059669; font-weight:bold;">{pfz.fish_density_score}%</span><br>
            <b>Range & Bearing:</b> {pfz.distance_km} km @ {pfz.bearing_deg}°<br>
            <b>Target Species:</b> {', '.join(pfz.species_likely[:2])}<br>
            <b>SST / Chl-a:</b> {pfz.sst_celsius}°C / {pfz.chlorophyll_proxy} mg/m³ | Depth {pfz.depth_m}m
        </div>
        """
        folium.Circle(
            location=[pfz.lat, pfz.lon],
            radius=4500,
            color=zone_color,
            weight=3 if is_selected else 1.5,
            fill=True,
            fill_color=zone_color,
            fill_opacity=0.35 if is_selected else 0.15,
            tooltip=f"{pfz.name} ({pfz.fish_density_score}% Catch Score)"
        ).add_to(pfz_group)

        folium.CircleMarker(
            location=[pfz.lat, pfz.lon],
            radius=8 if is_selected else 5,
            color="#ffffff",
            weight=2,
            fill=True,
            fill_color=zone_color,
            fill_opacity=1.0,
            popup=folium.Popup(pfz_popup, max_width=300)
        ).add_to(pfz_group)
    pfz_group.add_to(m)

    # Layer 7: Fuel-Optimized Navigation Corridor
    route_group = folium.FeatureGroup(name="⛽ Fuel Navigation Corridor", show=True)
    route_color = "#0284c7" if ("Day" in theme_name or "Light" in theme_name) else ("#10b981" if "Tactical" in theme_name else "#38bdf8")
    folium.PolyLine(
        locations=route.waypoints,
        color=route_color,
        weight=4,
        opacity=0.9,
        dash_array="6, 6",
        tooltip=f"Route to {selected_pfz.name} ({route.total_distance_nm} nm · {route.fuel_burn_liters} L)"
    ).add_to(route_group)
    route_group.add_to(m)

    # Layer 8: International Maritime Boundary Lines (IMBL)
    imbl_group = folium.FeatureGroup(name="🛑 International Boundaries (IMBL)", show=True)
    for b_name, b_coords in IMBL_BOUNDARIES.items():
        folium.PolyLine(
            locations=b_coords,
            color="#ef4444",
            weight=2.5,
            opacity=0.85,
            dash_array="8, 6",
            tooltip=f"RESTRICTED: {b_name}"
        ).add_to(imbl_group)
    imbl_group.add_to(m)

    # Layer 9: Animated Ocean Current Flow Streamlines (Windy.com Style)
    current_group = folium.FeatureGroup(name="🌊 Ocean Current Streamlines (Windy Style)", show=True)
    rad_dir = math.radians(telemetry.ocean_current_direction)
    flow_speed = max(0.5, telemetry.ocean_current_velocity)
    
    is_west = "West" in port.coast
    lon_dir = -1.0 if is_west else 1.0
    
    offsets = [-0.35, -0.22, -0.10, 0.05, 0.18, 0.30, 0.42, 0.55]
    for idx, off in enumerate(offsets):
        start_lat = port.lat + off * 0.8
        start_lon = port.lon + lon_dir * (0.20 + abs(off) * 0.3)
        
        dist_km = 35.0
        d_lat = (dist_km / 111.0) * math.cos(rad_dir)
        d_lon = (dist_km / (111.0 * math.cos(math.radians(port.lat)))) * math.sin(rad_dir)
        
        mid_lat = start_lat + d_lat * 0.5 + 0.02 * math.sin(idx)
        mid_lon = start_lon + d_lon * 0.5 + 0.02 * math.cos(idx)
        end_lat = start_lat + d_lat
        end_lon = start_lon + d_lon
        
        pts = [(start_lat, start_lon), (mid_lat, mid_lon), (end_lat, end_lon)]
        
        flow_color = "#38bdf8" if flow_speed < 1.5 else ("#00f2fe" if flow_speed < 2.5 else "#f59e0b")
        folium.PolyLine(
            locations=pts,
            color=flow_color,
            weight=2.5,
            opacity=0.85,
            dash_array="8, 14",
            tooltip=f"Ocean Current: {telemetry.ocean_current_velocity} km/h @ {telemetry.ocean_current_direction:.0f}°"
        ).add_to(current_group)
        
        arrow_html = f"""
        <div style="transform: rotate({telemetry.ocean_current_direction:.0f}deg); color:{flow_color}; font-size:16px; font-weight:bold; text-shadow:0 0 4px #000;">
            ➔
        </div>
        """
        folium.Marker(
            location=[mid_lat, mid_lon],
            icon=folium.DivIcon(html=arrow_html)
        ).add_to(current_group)

    current_group.add_to(m)

    # Compact Layer Controls
    folium.LayerControl(position="topright", collapsed=True).add_to(m)

    # DOM Animation Trigger for Leaflet SVG Paths
    current_anim_js = """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        setTimeout(function() {
            var paths = document.querySelectorAll("path[stroke-dasharray='8, 14']");
            paths.forEach(function(p) {
                p.classList.add("animated-current-flow");
            });
        }, 800);
    });
    </script>
    """
    m.get_root().html.add_child(folium.Element(current_anim_js))

    st_folium(m, height=height, use_container_width=True)


# ---------------------------------------------------------
# REUSABLE SECTION TABS HELPER (NON-CRAMPED, PROPER SPACING)
# ---------------------------------------------------------

def render_section_tabs(tab_list: List[str], current_tab: str, session_key: str) -> str:
    """
    Renders clean, spacious, reusable secondary navigation tabs with proper
    spacing, hover effects, and active state indicators.
    """
    cols = st.columns(len(tab_list) + 2)
    selected_tab = current_tab
    for idx, tab_name in enumerate(tab_list):
        with cols[idx]:
            is_active = (tab_name == current_tab)
            btn_type = "primary" if is_active else "secondary"
            if st.button(tab_name, key=f"{session_key}_{idx}", type=btn_type, use_container_width=True):
                selected_tab = tab_name
                st.session_state[session_key] = tab_name
                st.rerun()
    return selected_tab


# ---------------------------------------------------------
# APPLICATION STATE MANAGEMENT
# ---------------------------------------------------------

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = MultiAgentOrchestrator()

# Primary Navigation State (EXACTLY 5 SECTIONS)
if "nav_section" not in st.session_state:
    st.session_state.nav_section = "Dashboard"

# Sub-navigation states
if "sub_explore" not in st.session_state:
    st.session_state.sub_explore = "Tactical Map"

if "sub_conditions" not in st.session_state:
    st.session_state.sub_conditions = "Current & Forecast"

if "sub_safety" not in st.session_state:
    st.session_state.sub_safety = "Operational Status"

if "sub_settings" not in st.session_state:
    st.session_state.sub_settings = "Vessel & Voyage"

# Settings & Global State
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "🌙 Ocula Oceanic Dark"

if "active_port_id" not in st.session_state:
    st.session_state.active_port_id = "kochi"

if "query_text" not in st.session_state:
    st.session_state.query_text = "Can we sail from Kochi harbor for Yellowfin Tuna?"

if "advisory_lang" not in st.session_state:
    st.session_state.advisory_lang = "English"

if "last_pipeline_result" not in st.session_state:
    st.session_state.last_pipeline_result = None

if "show_sos_modal" not in st.session_state:
    st.session_state.show_sos_modal = False

if "show_guide_modal" not in st.session_state:
    st.session_state.show_guide_modal = False

if "vessel_class" not in st.session_state:
    st.session_state.vessel_class = "Mechanized Trawler (12-18m)"

port_list = list(INDIAN_PORTS.keys())

# Sync top header widget states immediately on rerun before pipeline execution
if "global_harbor_select" in st.session_state:
    _sel_idx = st.session_state.global_harbor_select
    if 0 <= _sel_idx < len(port_list):
        if st.session_state.active_port_id != port_list[_sel_idx]:
            st.session_state.active_port_id = port_list[_sel_idx]
            st.session_state.query_text = f"Can we sail from {INDIAN_PORTS[st.session_state.active_port_id].name} for Yellowfin Tuna?"
            st.session_state.last_pipeline_result = None

if "global_theme_select" in st.session_state:
    _t_opt = st.session_state.global_theme_select
    _t_map = {
        "☀️ Light": "☀️ Ocula Sky Day",
        "🌙 Dark": "🌙 Ocula Oceanic Dark",
        "⚡ Tactical": "⚡ Tactical Radar"
    }
    if _t_opt in _t_map and st.session_state.selected_theme != _t_map[_t_opt]:
        st.session_state.selected_theme = _t_map[_t_opt]

if "global_lang_select" in st.session_state:
    if st.session_state.advisory_lang != st.session_state.global_lang_select:
        st.session_state.advisory_lang = st.session_state.global_lang_select

# ---------------------------------------------------------
# EXECUTE DATA PIPELINE
# ---------------------------------------------------------

if (
    st.session_state.last_pipeline_result is None or
    st.session_state.last_pipeline_result.port.id != st.session_state.active_port_id or
    st.session_state.last_pipeline_result.query_intent.vessel_class != st.session_state.vessel_class
):
    with st.spinner("Fetching live ocean telemetry & verifying safety rules..."):
        res: ORCASynthesisResult = st.session_state.orchestrator.run_pipeline(
            query=st.session_state.query_text,
            selected_port_id=st.session_state.active_port_id,
            vessel_class=st.session_state.vessel_class
        )
        st.session_state.last_pipeline_result = res

res: ORCASynthesisResult = st.session_state.last_pipeline_result

# Safe fallback for astronomical tides and hourly forecast
port_tides: PortTideData = res.tides if res.tides is not None else calculate_port_tides(res.port.id)
port_hourly: HourlyMarineForecast = res.hourly_forecast if res.hourly_forecast is not None else fetch_hourly_marine_forecast(res.port)

# Dynamic Unit conversions
is_naut = "Nautical" in st.session_state.unit_system
if is_naut:
    curr_disp = f"{res.telemetry.ocean_current_velocity * 0.539957:.1f}"
    curr_unit = "kts"
    wind_disp = f"{res.telemetry.wind_speed * 0.539957:.1f}"
    wind_unit = "kts"
    gust_disp = f"Gusts {res.telemetry.wind_gusts * 0.539957:.1f} kts"
    dist_label_top = f"{res.route.total_distance_nm:.1f} nm"
else:
    curr_disp = f"{res.telemetry.ocean_current_velocity:.1f}"
    curr_unit = "km/h"
    wind_disp = f"{res.telemetry.wind_speed:.1f}"
    wind_unit = "km/h"
    gust_disp = f"Gusts {res.telemetry.wind_gusts:.1f} km/h"
    dist_label_top = f"{res.route.total_distance_nm * 1.852:.1f} km"


# ---------------------------------------------------------
# INJECT THEME CSS
# ---------------------------------------------------------
inject_theme(st.session_state.selected_theme)


# ---------------------------------------------------------
# COLLAPSIBLE NAVIGATION DRAWER (SIDEBAR) — ZERO RADIO BUTTONS!
# ---------------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid var(--border); margin-bottom: 16px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:24px;">⚓</span>
            <div>
                <div style="font-size:16px; font-weight:800; color:var(--primary); line-height:1.1;">FishingFriend</div>
                <div style="font-size:11px; color:var(--text-muted);">ORCA Marine AI · ISRO SIH26176</div>
            </div>
        </div>
    </div>
    <div style="font-size: 11px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px;">
        OPERATIONS
    </div>
    """, unsafe_allow_html=True)

    # 5 Primary Navigation Items rendered as Clean Nav Buttons with Left Indicator Active State
    nav_items = [
        ("Dashboard", "🏠 Dashboard"),
        ("Explore", "🗺 Explore"),
        ("Conditions", "🌦 Conditions"),
        ("Safety & Advisory", "🛟 Safety & Advisory"),
        ("Settings", "⚙ Settings")
    ]

    for key_name, label_name in nav_items:
        is_active = (st.session_state.nav_section == key_name)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label_name, key=f"side_nav_{key_name}", type=btn_type, use_container_width=True):
            st.session_state.nav_section = key_name
            st.rerun()

    # Minimal bottom status indicator in drawer
    st.markdown("""
    <div style="margin-top: 48px; padding: 12px; background: var(--bg-surface); border-radius: 8px; border: 1px solid var(--border); font-size: 11px; line-height: 1.4;">
        <div style="font-weight: 700; color: var(--success); display:flex; align-items:center; gap:6px;">
            <span style="font-size:8px;">●</span> Systems Online
        </div>
        <div style="color: var(--text-muted); font-size: 10px; margin-top: 2px;">
            Live INCOIS & Open-Meteo Sync
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# GLOBAL TOP HEADER BAR (UNCLUTTERED, GENEROUS WIDTHS)
# ---------------------------------------------------------

hdr_col1, hdr_col2, hdr_col3, hdr_col4, hdr_col5, hdr_col6 = st.columns([2.6, 3.4, 1.6, 1.6, 1.4, 2.4])

with hdr_col1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; padding-top:4px;">
        <span style="font-size:22px;">⚓</span>
        <div>
            <div style="font-size:16px; font-weight:800; color:var(--primary); line-height:1.1;">FishingFriend</div>
            <div style="font-size:11px; color:var(--text-muted);">Marine Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hdr_col2:
    port_list = list(INDIAN_PORTS.keys())
    port_names = []
    for k in port_list:
        p = INDIAN_PORTS[k]
        coast_tag = "West" if "West" in p.coast else "East"
        port_names.append(f"📍 {p.name} ({coast_tag})")
    
    cur_idx = port_list.index(st.session_state.active_port_id)
    selected_p = st.selectbox(
        "Base Harbor",
        options=range(len(port_list)),
        format_func=lambda i: port_names[i],
        index=cur_idx,
        label_visibility="collapsed",
        key="global_harbor_select"
    )
    if port_list[selected_p] != st.session_state.active_port_id:
        st.session_state.active_port_id = port_list[selected_p]
        st.session_state.query_text = f"Can we sail from {INDIAN_PORTS[st.session_state.active_port_id].name} for Yellowfin Tuna?"
        st.session_state.last_pipeline_result = None
        st.rerun()

with hdr_col3:
    theme_options = ["☀️ Light", "🌙 Dark", "⚡ Tactical"]
    cur_t_idx = 1
    if "Day" in st.session_state.selected_theme or "Light" in st.session_state.selected_theme:
        cur_t_idx = 0
    elif "Tactical" in st.session_state.selected_theme:
        cur_t_idx = 2

    chosen_t = st.selectbox(
        "Theme",
        options=theme_options,
        index=cur_t_idx,
        label_visibility="collapsed",
        key="global_theme_select"
    )
    theme_map = {
        "☀️ Light": "☀️ Ocula Sky Day",
        "🌙 Dark": "🌙 Ocula Oceanic Dark",
        "⚡ Tactical": "⚡ Tactical Radar"
    }
    if theme_map[chosen_t] != st.session_state.selected_theme:
        st.session_state.selected_theme = theme_map[chosen_t]
        st.rerun()

with hdr_col4:
    lang_options = ["English", "हिन्दी", "தமிழ்"]
    cur_l_idx = 0
    if "Hindi" in st.session_state.advisory_lang or "हिन्दी" in st.session_state.advisory_lang:
        cur_l_idx = 1
    elif "Tamil" in st.session_state.advisory_lang or "தமிழ்" in st.session_state.advisory_lang:
        cur_l_idx = 2

    chosen_l = st.selectbox(
        "Language",
        options=lang_options,
        index=cur_l_idx,
        label_visibility="collapsed",
        key="global_lang_select"
    )
    if chosen_l != st.session_state.advisory_lang:
        st.session_state.advisory_lang = chosen_l
        st.rerun()

with hdr_col5:
    if st.button("💡 Guide", use_container_width=True, key="hdr_guide_btn"):
        st.session_state.show_guide_modal = not st.session_state.show_guide_modal
        st.session_state.show_sos_modal = False
        st.rerun()

with hdr_col6:
    if st.button("🚨 Emergency SOS", type="primary", use_container_width=True, key="hdr_sos_btn"):
        st.session_state.show_sos_modal = not st.session_state.show_sos_modal
        st.session_state.show_guide_modal = False
        st.rerun()


# ---------------------------------------------------------
# GLOBAL MODALS (GUIDE & SOP / EMERGENCY SOS)
# ---------------------------------------------------------

if st.session_state.show_guide_modal:
    st.markdown("""
    <div class="ff-modal-box" style="border-left: 5px solid var(--primary); margin-top: 8px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:16px; font-weight:800; color:var(--primary);">
                💡 SKIPPER'S FIELD GUIDE & OPERATIONAL SOP
            </div>
            <div style="font-size:11px; font-weight:700; color:var(--primary); background:var(--primary-subtle); padding:4px 8px; border-radius:6px;">
                INCOIS / IMD RULES
            </div>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-top: 14px;">
            <div style="background: var(--success-bg); border-left: 3px solid var(--success); padding: 12px 14px; border-radius: 6px;">
                <b style="color:var(--success); font-size:13px;">🟢 SAFE TO SAIL (GO)</b>
                <p style="font-size:12px; margin:4px 0 0 0; line-height:1.4; color:var(--text-secondary);">
                    • Swell &lt; 1.80m & Wind &lt; 32 km/h.<br>
                    • Safe distance from International Maritime Boundaries (&gt;10 nm).<br>
                    • All registered craft cleared for offshore voyage.
                </p>
            </div>
            <div style="background: var(--warning-bg); border-left: 3px solid var(--warning); padding: 12px 14px; border-radius: 6px;">
                <b style="color:var(--warning); font-size:13px;">🟡 CAUTION (CONDITIONAL)</b>
                <p style="font-size:12px; margin:4px 0 0 0; line-height:1.4; color:var(--text-secondary);">
                    • Swell 1.80m - 2.50m or Wind 32 - 45 km/h.<br>
                    • Traditional craft (&lt;10m) restricted within 12 nm.<br>
                    • Maintain continuous VHF Ch 16 radio watch.
                </p>
            </div>
            <div style="background: var(--danger-bg); border-left: 3px solid var(--danger); padding: 12px 14px; border-radius: 6px;">
                <b style="color:var(--danger); font-size:13px;">🔴 NO-GO (SUSPENSION)</b>
                <p style="font-size:12px; margin:4px 0 0 0; line-height:1.4; color:var(--text-secondary);">
                    • Swell &gt; 2.50m (INCOIS High Wave Red Alert).<br>
                    • Wind &gt; 45.0 km/h (IMD Squall Warning).<br>
                    • Proximity to IMBL &lt; 10.0 nm. Operations suspended.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✕ Close Guide", key="btn_close_guide"):
        st.session_state.show_guide_modal = False
        st.rerun()

if st.session_state.show_sos_modal:
    st.markdown(f"""
    <div class="ff-modal-box" style="border: 2px solid var(--danger); background: var(--danger-bg); margin-top: 8px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:17px; font-weight:800; color:var(--danger);">
                🚨 DISTRESS EMERGENCY BEACON (MAYDAY PROTOCOL)
            </div>
            <div style="font-size:11px; font-weight:700; color:var(--danger); background:rgba(239, 68, 68, 0.15); padding:4px 8px; border-radius:6px;">
                VHF CH 16 / DSC CHANNEL 70
            </div>
        </div>
        <p style="font-size:12px; margin:6px 0 10px 0; color:var(--text-primary);">
            Immediate broadcast payload for Indian Coast Guard (1554) and Coastal Security Police (1093).
        </p>
    </div>
    """, unsafe_allow_html=True)

    sos_col1, sos_col2 = st.columns([7, 3])
    with sos_col1:
        distress_payload = (
            f"MAYDAY MAYDAY MAYDAY\n"
            f"VESSEL: {st.session_state.vessel_class} (Reg: IND-{res.port.id.upper()}-402)\n"
            f"CURRENT POSITION: Lat {res.port.lat:.4f}° N, Lon {res.port.lon:.4f}° E\n"
            f"NEAREST BASE: {res.port.name}, {res.port.state} ({res.port.coast})\n"
            f"NEAREST INT'L BOUNDARY: {res.safety.nearest_imbl_name} ({res.safety.border_distance_km} km away)\n"
            f"CURRENT WAVE / SWELL: {res.telemetry.wave_height}m (Swell {res.telemetry.swell_wave_height}m)\n"
            f"EMERGENCY FREQUENCY: VHF Ch 16 (156.800 MHz) | Distress Relay: 1554"
        )
        st.code(distress_payload, language="text")

    with sos_col2:
        st.markdown(f"""
        <div style="font-size:12px; line-height:1.7; color:var(--text-primary);">
            <b>📞 Emergency Contacts:</b><br>
            • <b>Coast Guard MRCC:</b> <a href="tel:1554" style="color:var(--primary); font-weight:bold;">1554</a><br>
            • <b>Marine Police:</b> <a href="tel:1093" style="color:var(--primary); font-weight:bold;">1093</a><br>
            • <b>Disaster SEOC:</b> 1070 / 1077<br>
            • <b>Sea Ambulance:</b> 108
        </div>
        """, unsafe_allow_html=True)
        if st.button("📡 Broadcast Alert (Simulated)", type="primary", use_container_width=True, key="btn_send_sos"):
            st.success("✅ Simulated Mayday Packet transmitted to nearest Coast Guard MRCC Station.")
        if st.button("✕ Close SOS", use_container_width=True, key="btn_close_sos"):
            st.session_state.show_sos_modal = False
            st.rerun()


# =========================================================
# SECTION 1: 🏠 DASHBOARD (RADICALLY SIMPLIFIED OVERVIEW)
# =========================================================

if st.session_state.nav_section == "Dashboard":
    # 1. Page Title & Selected Harbor
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom: 16px;">
        <div>
            <h2 style="margin:0; font-size:28px; font-weight:800; color:var(--text-primary); letter-spacing:-0.4px;">Fishing Operations</h2>
            <div style="font-size:14px; color:var(--text-muted); margin-top:2px;">
                📍 <b>{res.port.name}</b> · {res.port.coast} · {datetime.now().strftime('%d-%b-%Y %H:%M IST')}
            </div>
        </div>
        <div style="font-size:13px; color:var(--text-muted); text-align:right;">
            Vessel: <b>{st.session_state.vessel_class.split('(')[0].strip()}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Primary Status: Clean Operational Clearance Hero Panel
    if res.safety.status == "SAFE_GO":
        status_cls = "ff-status-safe"
        status_icon = "●"
        status_title = "SAFE TO SAIL"
        status_tag = "GO"
        status_color = "var(--success)"
        status_desc = f"Normal sea conditions off {res.port.name}. Wave and swell heights remain well within safe limits (<2.5m). Unrestricted offshore fishing cleared."
    elif res.safety.status == "CAUTION_CONDITIONAL":
        status_cls = "ff-status-caution"
        status_icon = "●"
        status_title = "CAUTION ADVISED"
        status_tag = "CONDITIONAL"
        status_color = "var(--warning)"
        status_desc = f"Moderate swell ({res.telemetry.swell_wave_height}m) or wind gusts off {res.port.name}. Traditional craft (<10m) advised to stay within 12 nm."
    else:
        status_cls = "ff-status-danger"
        status_icon = "●"
        status_title = "NO-GO (OPERATIONS SUSPENDED)"
        status_tag = "DANGER"
        status_color = "var(--danger)"
        status_desc = f"INCOIS threshold breached: Swell > 2.5m or wind > 45 km/h. All fishing vessels ordered to remain moored."

    st.markdown(f"""
    <div class="ff-status-panel {status_cls}">
        <div>
            <div style="font-size:13px; font-weight:700; color:{status_color}; text-transform:uppercase; letter-spacing:0.8px;">
                {status_icon} {status_title}
            </div>
            <div style="font-size:26px; font-weight:800; color:{status_color}; margin: 2px 0 4px 0;">
                {status_tag}
            </div>
            <div style="font-size:13px; color:var(--text-secondary); max-width:720px; line-height:1.5;">
                {status_desc}
            </div>
        </div>
        <div style="text-align:right; min-width:110px;">
            <div style="font-size:28px; font-weight:800; color:{status_color}; font-family:'JetBrains Mono';">
                {res.safety.risk_score} <span style="font-size:14px; font-weight:600; color:var(--text-muted);">/ 100</span>
            </div>
            <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Risk Index</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Current Conditions: Single Compact Horizontal Metric Strip
    st.markdown(f"""
    <div class="ff-metric-strip">
        <div class="ff-metric-item">
            <div class="ff-metric-label">🌊 Swell</div>
            <div class="ff-metric-value">{res.telemetry.swell_wave_height} <span style="font-size:13px;">m</span></div>
            <div class="ff-metric-sub">{res.telemetry.swell_wave_period}s Period</div>
        </div>
        <div class="ff-metric-item">
            <div class="ff-metric-label">🌡️ SST</div>
            <div class="ff-metric-value">{res.telemetry.sea_surface_temperature}°<span style="font-size:13px;">C</span></div>
            <div class="ff-metric-sub">Thermal Edge</div>
        </div>
        <div class="ff-metric-item">
            <div class="ff-metric-label">🌀 Current</div>
            <div class="ff-metric-value">{curr_disp} <span style="font-size:13px;">{curr_unit}</span></div>
            <div class="ff-metric-sub">Drift {res.telemetry.ocean_current_direction:.0f}°</div>
        </div>
        <div class="ff-metric-item">
            <div class="ff-metric-label">💨 Wind</div>
            <div class="ff-metric-value">{wind_disp} <span style="font-size:13px;">{wind_unit}</span></div>
            <div class="ff-metric-sub">{gust_disp}</div>
        </div>
        <div class="ff-metric-item">
            <div class="ff-metric-label">🌿 Chlorophyll-A</div>
            <div class="ff-metric-value">{res.telemetry.chlorophyll_proxy} <span style="font-size:11px;">mg/m³</span></div>
            <div class="ff-metric-sub">Oceansat-3</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Two Compact Summary Cards: ONLY Top 1 Fishing Recommendation & ORCA Summary
    dash_col1, dash_col2 = st.columns(2)

    with dash_col1:
        st.markdown(f"""
        <div class="ff-card" style="height:100%; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-muted); letter-spacing:0.5px;">
                    RECOMMENDED FISHING ZONE
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <div style="font-size:17px; font-weight:800; color:var(--primary);">
                        ⭐ {res.top_pfz.name}
                    </div>
                    <div style="font-size:16px; font-weight:800; color:var(--success); font-family:'JetBrains Mono';">
                        {res.top_pfz.fish_density_score}% Score
                    </div>
                </div>
                <div style="font-size:13px; color:var(--text-secondary); margin-top:8px; line-height:1.5;">
                    <b>Range:</b> {dist_label_top} · <b>Depth:</b> {res.top_pfz.depth_m}m · <b>Bearing:</b> {res.top_pfz.bearing_deg}°<br>
                    <b>Target Species:</b> {', '.join(res.top_pfz.species_likely[:2])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View All Fishing Zones →", key="btn_dash_all_pfz", use_container_width=True):
            st.session_state.nav_section = "Explore"
            st.session_state.sub_explore = "Fishing Zones"
            st.rerun()

    with dash_col2:
        if "Hindi" in st.session_state.advisory_lang or "हिन्दी" in st.session_state.advisory_lang:
            adv_sum = res.advisory.hindi['executive_summary']
        elif "Tamil" in st.session_state.advisory_lang or "தமிழ்" in st.session_state.advisory_lang:
            adv_sum = res.advisory.tamil['executive_summary']
        else:
            adv_sum = res.advisory.english['executive_summary']

        st.markdown(f"""
        <div class="ff-card" style="height:100%; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-muted); letter-spacing:0.5px;">
                    ORCA AI INSIGHT
                </div>
                <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-top:8px;">
                    {res.advisory.english['status_headline']}
                </div>
                <div style="font-size:13px; color:var(--text-secondary); margin-top:8px; line-height:1.5;">
                    {adv_sum[:170]}...
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View Full Advisory & Audio →", key="btn_dash_full_adv", use_container_width=True):
            st.session_state.nav_section = "Safety & Advisory"
            st.session_state.sub_safety = "Actionable Advisory"
            st.rerun()

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # 5. Compact Map Preview
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <div style="font-size:14px; font-weight:700; color:var(--text-primary);">
            Operational Map Preview
        </div>
        <span style="font-size:11px; color:var(--text-muted);">OpenSeaMap & Current Streamlines</span>
    </div>
    """, unsafe_allow_html=True)

    render_tactical_map(
        port=res.port,
        telemetry=res.telemetry,
        safety=res.safety,
        all_pfzs=[res.top_pfz],
        selected_pfz=res.top_pfz,
        route=res.route,
        theme_name=st.session_state.selected_theme,
        height=320
    )

    if st.button("Open Tactical Map →", key="btn_dash_open_map", use_container_width=True):
        st.session_state.nav_section = "Explore"
        st.session_state.sub_explore = "Tactical Map"
        st.rerun()


# =========================================================
# SECTION 2: 🗺 EXPLORE (TACTICAL MAP / ZONES / SEA ANALYSIS)
# =========================================================

elif st.session_state.nav_section == "Explore":
    st.markdown(f"""
    <div style="margin-bottom:14px;">
        <h2 style="margin:0; font-size:26px; font-weight:800; color:var(--text-primary);">Explore</h2>
        <div style="font-size:14px; color:var(--text-muted); margin-top:2px;">
            Marine intelligence, tactical navigation and fishing opportunities off <b>{res.port.name}</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Reusable Spacious SectionTabs
    explore_tabs = ["Tactical Map", "Fishing Zones", "Sea Analysis"]
    st.session_state.sub_explore = render_section_tabs(explore_tabs, st.session_state.sub_explore, "tab_explore")

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # SUBVIEW 2.1: TACTICAL MAP
    if st.session_state.sub_explore == "Tactical Map":
        st.caption("Layer control (top-right of chart): Toggle Nautical Marks, ESRI Bathymetry, MPAs, PFZ Hotspots, and Animated Current Streamlines.")
        
        render_tactical_map(
            port=res.port,
            telemetry=res.telemetry,
            safety=res.safety,
            all_pfzs=res.all_pfzs,
            selected_pfz=res.top_pfz,
            route=res.route,
            theme_name=st.session_state.selected_theme,
            height=600
        )

        st.markdown(f"""
        <div class="ff-card" style="margin-top:14px; padding:14px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="font-size:13px; color:var(--text-secondary);">
                🎯 <b>Target PFZ:</b> {res.top_pfz.name} ({dist_label_top} · Bearing {res.top_pfz.bearing_deg}°) | 
                ⛽ <b>Transit:</b> ~{res.route.fuel_burn_liters} L (Saved: <span style="color:var(--success); font-weight:bold;">{res.route.fuel_savings_liters} L</span>) |
                🛑 <b>IMBL Border:</b> {res.safety.border_distance_km} km ({res.safety.nearest_imbl_name})
            </div>
            <span style="font-size:11px; background:var(--primary-subtle); color:var(--primary); padding:4px 10px; border-radius:4px; font-weight:600;">
                Live OpenSeaMap & Bathymetry Active
            </span>
        </div>
        """, unsafe_allow_html=True)

    # SUBVIEW 2.2: FISHING ZONES
    elif st.session_state.sub_explore == "Fishing Zones":
        st.markdown("##### 🐟 Discovered Potential Fishing Zones (ISRO Oceansat-3 Frontiers)")
        st.caption("Thermal front gradients and chlorophyll upwelling zones prioritized for pelagic fish aggregations.")

        for idx, pfz in enumerate(res.all_pfzs):
            is_top = (pfz.zone_id == res.top_pfz.zone_id)
            badge_border = "border-left: 4px solid var(--primary);" if is_top else "border-left: 4px solid var(--border);"
            bg_accent = "background: var(--bg-subtle);" if is_top else ""
            
            st.markdown(f"""
            <div class="ff-card" style="{badge_border} {bg_accent} padding: 18px; margin-bottom: 14px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:17px; font-weight:800; color:var(--primary);">
                            {'⭐ ' if is_top else ''}{pfz.name}
                        </span>
                        <span style="font-size:11px; margin-left:8px; background:rgba(0,0,0,0.06); padding:2px 8px; border-radius:4px; font-weight:600;">
                            {pfz.confidence_level}
                        </span>
                    </div>
                    <div style="font-size:17px; font-weight:800; color:var(--success); font-family:'JetBrains Mono';">
                        {pfz.fish_density_score}% Catch Score
                    </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin-top:12px; font-size:13px; color:var(--text-secondary);">
                    <div><b>Range & Heading:</b> {pfz.distance_km} km @ {pfz.bearing_deg}°</div>
                    <div><b>Bathymetry Depth:</b> {pfz.depth_m} meters</div>
                    <div><b>SST / Chl-a:</b> {pfz.sst_celsius}°C / {pfz.chlorophyll_proxy} mg/m³</div>
                    <div><b>Thermal Edge:</b> {pfz.thermal_gradient_desc}</div>
                </div>
                <div style="margin-top:10px; font-size:13px; color:var(--text-primary);">
                    <b>Target Species:</b> <span style="color:var(--primary); font-weight:600;">{', '.join(pfz.species_likely)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # SUBVIEW 2.3: SEA ANALYSIS
    elif st.session_state.sub_explore == "Sea Analysis":
        st.markdown("##### 🌊 Oceanographic Analysis & Marine Protected Areas")
        
        sa_col1, sa_col2 = st.columns(2)
        with sa_col1:
            st.markdown(f"""
            <div class="ff-card">
                <div style="font-size:15px; font-weight:700; color:var(--primary); margin-bottom:10px;">
                    🌊 Physical Oceanography Parameters
                </div>
                <div style="font-size:13px; line-height:1.8; color:var(--text-secondary);">
                    • <b>Significant Wave Height:</b> {res.telemetry.wave_height} m (Dir: {res.telemetry.wave_direction:.0f}°)<br>
                    • <b>Dominant Swell Height:</b> {res.telemetry.swell_wave_height} m (Period: {res.telemetry.swell_wave_period} s)<br>
                    • <b>Sea Surface Temperature (SST):</b> {res.telemetry.sea_surface_temperature}°C<br>
                    • <b>Ocean Current Stream:</b> {curr_disp} {curr_unit} @ {res.telemetry.ocean_current_direction:.0f}° drift<br>
                    • <b>Bio-Optical Chlorophyll Proxy:</b> {res.telemetry.chlorophyll_proxy} mg/m³
                </div>
            </div>
            """, unsafe_allow_html=True)

        with sa_col2:
            st.markdown(f"""
            <div class="ff-card">
                <div style="font-size:15px; font-weight:700; color:var(--primary); margin-bottom:10px;">
                    🛡️ Marine Spatial Planning (MarineMap MSP)
                </div>
                <div style="font-size:13px; line-height:1.6; color:var(--text-secondary);">
                    Sensitive coral reefs and statutory conservation reserves off <b>{res.port.name}</b>:
                </div>
            </div>
            """, unsafe_allow_html=True)

            mpas_local = get_marine_spatial_zones(res.port.id)
            if mpas_local:
                for m in mpas_local:
                    st.markdown(f"""
                    <div style="font-size:12px; padding:12px 14px; background:rgba(234, 88, 12, 0.08); border-left:4px solid #ea580c; border-radius:6px; margin-bottom:10px;">
                        <b style="color:#ea580c; font-size:13px;">🛡️ {m.name} ({m.category})</b><br>
                        <span style="color:var(--text-secondary);">{m.restriction}</span><br>
                        <span style="font-size:11px; color:var(--text-muted);">Legal Basis: {m.legal_source}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No restricted marine sanctuaries immediately adjacent to this harbor fairway.")


# =========================================================
# SECTION 3: 🌦 CONDITIONS (FORECAST / TIDES / RADAR)
# =========================================================

elif st.session_state.nav_section == "Conditions":
    st.markdown(f"""
    <div style="margin-bottom:14px;">
        <h2 style="margin:0; font-size:26px; font-weight:800; color:var(--text-primary);">Conditions</h2>
        <div style="font-size:14px; color:var(--text-muted); margin-top:2px;">
            Weather, 48-hour marine forecast, tides and live radar observation for <b>{res.port.name}</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Reusable Spacious SectionTabs
    cond_tabs = ["Current & Forecast", "Tides", "Radar & Satellite"]
    st.session_state.sub_conditions = render_section_tabs(cond_tabs, st.session_state.sub_conditions, "tab_cond")

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # SUBVIEW 3.1: CURRENT & FORECAST
    if st.session_state.sub_conditions == "Current & Forecast":
        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center; padding:14px;">
                <div style="font-size:11px; font-weight:700; color:var(--primary);">48H PEAK SWELL HEIGHT</div>
                <div style="font-size:24px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono'; margin:4px 0;">
                    {port_hourly.max_wave_height:.2f} <span style="font-size:14px;">m</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">INCOIS Status: <b>{port_hourly.incois_wave_risk}</b></div>
            </div>
            """, unsafe_allow_html=True)

        with hc2:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center; padding:14px;">
                <div style="font-size:11px; font-weight:700; color:var(--warning);">48H MAX WIND GUST</div>
                <div style="font-size:24px; font-weight:800; color:var(--warning); font-family:'JetBrains Mono'; margin:4px 0;">
                    {port_hourly.max_wind_gust:.1f} <span style="font-size:14px;">km/h</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">IMD Status: <b>{port_hourly.imd_wind_risk}</b></div>
            </div>
            """, unsafe_allow_html=True)

        with hc3:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center; padding:14px;">
                <div style="font-size:11px; font-weight:700; color:var(--success);">TELEMETRY DATA SOURCE</div>
                <div style="font-size:20px; font-weight:800; color:var(--success); margin:6px 0;">
                    {'Live Open-Meteo' if port_hourly.is_live else 'Synthetic Marine Model'}
                </div>
                <div style="font-size:11px; color:var(--text-muted);">48h Horizon Ahead</div>
            </div>
            """, unsafe_allow_html=True)

        # 48-Hour Wave & Swell Height Interactive Chart
        hourly_plot_data = []
        for h in port_hourly.hours:
            hourly_plot_data.append({
                "Hour": h.hour_label,
                "Significant Wave (m)": h.wave_height_m,
                "Swell Height (m)": h.swell_wave_height_m,
                "Wind Gust (km/h)": h.wind_gusts_kmh,
                "Rain Probability (%)": h.precipitation_probability_pct
            })
        df_hourly = pd.DataFrame(hourly_plot_data)

        chart_color = "#0284c7" if ("Day" in st.session_state.selected_theme or "Light" in st.session_state.selected_theme) else ("#10b981" if "Tactical" in st.session_state.selected_theme else "#38bdf8")

        chart_wave = alt.Chart(df_hourly).mark_line(
            interpolate="monotone",
            color=chart_color,
            strokeWidth=3
        ).encode(
            x=alt.X("Hour:N", title="Forecast Timeline (IST)", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Significant Wave (m):Q", title="Wave / Swell Height (m)", scale=alt.Scale(domain=[0, max(3.0, port_hourly.max_wave_height + 0.5)])),
            tooltip=["Hour:N", "Significant Wave (m):Q", "Swell Height (m):Q", "Wind Gust (km/h):Q", "Rain Probability (%):Q"]
        )

        chart_swell = alt.Chart(df_hourly).mark_line(
            interpolate="monotone",
            color="#38bdf8" if ("Day" in st.session_state.selected_theme or "Light" in st.session_state.selected_theme) else "#94a3b8",
            strokeWidth=2,
            strokeDash=[4, 4]
        ).encode(
            x="Hour:N",
            y="Swell Height (m):Q"
        )

        danger_rule = alt.Chart(pd.DataFrame([{"y": 2.5}])).mark_rule(
            color="#ef4444",
            strokeWidth=2,
            strokeDash=[6, 4]
        ).encode(y="y:Q")

        final_forecast_chart = (chart_wave + chart_swell + danger_rule).properties(
            height=280,
            title="48-Hour Wave & Swell Profile with INCOIS 2.5m Red Alert Threshold Line (Red Dashed)"
        ).configure_title(fontSize=13, anchor="start", color=chart_color)

        st.altair_chart(final_forecast_chart, use_container_width=True)

        # Upcoming Hourly Forecast Windows
        st.markdown("###### ⏱️ Upcoming Hourly Marine Windows")
        step_cols = st.columns(6)
        for idx, (c, h_entry) in enumerate(zip(step_cols, port_hourly.hours[::3][:6])):
            with c:
                is_danger_wave = h_entry.swell_wave_height_m >= 2.5
                is_caution_wave = h_entry.swell_wave_height_m >= 1.8 and not is_danger_wave
                badge_color = "#ef4444" if is_danger_wave else ("#f59e0b" if is_caution_wave else "#16a34a")
                badge_text = "DANGER" if is_danger_wave else ("CAUTION" if is_caution_wave else "SAFE")
                
                st.markdown(f"""
                <div class="ff-card" style="border-top:3px solid {badge_color}; padding:10px; text-align:center;">
                    <div style="font-size:11px; font-weight:700; color:var(--primary);">{h_entry.hour_label.split(' ')[1]}</div>
                    <div style="font-size:16px; font-weight:800; margin:4px 0; font-family:'JetBrains Mono';">{h_entry.wave_height_m:.1f} m</div>
                    <div style="font-size:10px; color:var(--text-muted);">Swell {h_entry.swell_wave_height_m:.1f}m</div>
                    <div style="font-size:10px; color:var(--text-muted);">Wind {h_entry.wind_speed_kmh:.0f} km/h</div>
                    <div style="font-size:10px; font-weight:700; color:{badge_color}; margin-top:4px;">{badge_text}</div>
                </div>
                """, unsafe_allow_html=True)

    # SUBVIEW 3.2: TIDES
    elif st.session_state.sub_conditions == "Tides":
        st.markdown(f"##### 🌊 Astronomical Tides & Coastal Water Levels for **{port_tides.port_name}**")
        st.caption("Harmonic constituents calibrated against Survey of India & NIO tidal benchmarks.")

        tb1, tb2, tb3, tb4 = st.columns(4)
        with tb1:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center;">
                <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">Water Level</div>
                <div style="font-size:24px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono'; margin:4px 0;">
                    {port_tides.current_water_level_m:.2f} <span style="font-size:13px;">m</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">Above Chart Datum</div>
            </div>
            """, unsafe_allow_html=True)

        with tb2:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center;">
                <div style="font-size:11px; font-weight:700; color:var(--success); text-transform:uppercase;">Tidal Phase</div>
                <div style="font-size:18px; font-weight:800; color:var(--success); margin:6px 0;">
                    {port_tides.tide_phase.split('(')[0].strip()}
                </div>
                <div style="font-size:11px; color:var(--text-muted);">{port_tides.time_to_next_extreme}</div>
            </div>
            """, unsafe_allow_html=True)

        with tb3:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center;">
                <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">Stream Velocity</div>
                <div style="font-size:24px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono'; margin:4px 0;">
                    {port_tides.tidal_stream_velocity_knots:.1f} <span style="font-size:13px;">kts</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">Spring Range: {port_tides.mean_spring_range_m:.2f}m</div>
            </div>
            """, unsafe_allow_html=True)

        with tb4:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center;">
                <div style="font-size:11px; font-weight:700; color:var(--warning); text-transform:uppercase;">Harbor Bar Depth</div>
                <div style="font-size:24px; font-weight:800; color:var(--warning); font-family:'JetBrains Mono'; margin:4px 0;">
                    {port_tides.harbor_bar_depth_m:.1f} <span style="font-size:13px;">m</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">At Low Water Datum</div>
            </div>
            """, unsafe_allow_html=True)

        if port_tides.harbor_bar_keel_warning:
            st.markdown(f"""
            <div style="background:var(--warning-bg); border-left:4px solid var(--warning); padding:10px 16px; border-radius:8px; margin: 14px 0; font-size:13px; color:var(--text-primary);">
                ⚠️ <b>HARBOR BAR NOTICE:</b> {port_tides.harbor_bar_keel_warning}
            </div>
            """, unsafe_allow_html=True)

        # 48-Hour Continuous Spline Tide Chart
        tide_plot_data = []
        for p in port_tides.hourly_heights_48h:
            tide_plot_data.append({
                "Time": p.time_str,
                "Tide Height (m)": p.height_m,
                "Is Extreme": p.is_extreme,
                "Label": p.extreme_label if p.extreme_label else ""
            })
        df_tides = pd.DataFrame(tide_plot_data)

        chart_color = "#0284c7" if ("Day" in st.session_state.selected_theme or "Light" in st.session_state.selected_theme) else ("#10b981" if "Tactical" in st.session_state.selected_theme else "#38bdf8")

        line_chart = alt.Chart(df_tides).mark_line(
            interpolate="monotone",
            color=chart_color,
            strokeWidth=3.5
        ).encode(
            x=alt.X("Time:N", title="Timeline (IST)", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Tide Height (m):Q", title="Water Level (m Above Datum)", scale=alt.Scale(zero=False)),
            tooltip=["Time:N", "Tide Height (m):Q", "Label:N"]
        )

        area_chart = alt.Chart(df_tides).mark_area(
            interpolate="monotone",
            color=chart_color,
            opacity=0.15
        ).encode(
            x=alt.X("Time:N"),
            y=alt.Y("Tide Height (m):Q")
        )

        msl_rule = alt.Chart(pd.DataFrame([{"y": 1.0}])).mark_rule(
            color="#94a3b8",
            strokeDash=[4, 4]
        ).encode(y="y:Q")

        final_tide_chart = (area_chart + line_chart + msl_rule).properties(
            height=280,
            title=f"Astronomical Tidal Curve: {port_tides.port_name} (Continuous 48-Hour Trend)"
        ).configure_title(fontSize=13, anchor="start", color=chart_color)

        st.altair_chart(final_tide_chart, use_container_width=True)

    # SUBVIEW 3.3: RADAR & SATELLITE
    elif st.session_state.sub_conditions == "Radar & Satellite":
        st.markdown("##### 📡 Live Doppler Precipitation Radar & Squall Tracking")
        
        rad_col1, rad_col2 = st.columns([8, 4])
        with rad_col1:
            st.markdown(f"""
            <div class="ff-card" style="padding:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-weight:700; font-size:14px; color:var(--primary);">
                        🌧️ Active Coastal Radar: {res.port.name}
                    </span>
                    <span style="font-size:11px; background:var(--primary-subtle); color:var(--primary); padding:2px 8px; border-radius:4px; font-weight:600;">
                        LIVE DOPPLER FEED
                    </span>
                </div>
                <iframe 
                    src="https://www.rainviewer.com/map.html?loc={res.port.lat},{res.port.lon},8&oFa=0&oC=1&oU=0&oCS=1&oF=0&oAP=1&c=3&o=83&lm=1&layer=radar&sm=1&sn=1" 
                    width="100%" 
                    height="460" 
                    style="border:none; border-radius:8px;"
                    allowfullscreen>
                </iframe>
            </div>
            """, unsafe_allow_html=True)

        with rad_col2:
            st.markdown("""
            <div class="ff-card">
                <h4 style="margin:0 0 10px 0; color:var(--primary); font-size:15px;">🌦️ Doppler Radar Interpretation</h4>
                <div style="font-size:12px; line-height:1.7; color:var(--text-secondary);">
                    • <b>Indian Radar Network:</b> Connected to coastal Doppler radars (IMD Kochi, Chennai, Mumbai, Visakhapatnam).<br>
                    • <b>Reflectivity Scale (dBZ):</b><br>
                      &nbsp;&nbsp;🟦 <b>15 - 25 dBZ:</b> Light drizzle / mist.<br>
                      &nbsp;&nbsp;🟩 <b>25 - 35 dBZ:</b> Moderate rain showers.<br>
                      &nbsp;&nbsp;🟨 <b>35 - 45 dBZ:</b> Heavy monsoon squalls.<br>
                      &nbsp;&nbsp;🟥 <b>> 45 dBZ:</b> Severe storm cell (&gt;45 km/h).
                </div>
                <div style="background:var(--primary-subtle); border-left:3px solid var(--primary); padding:10px 12px; border-radius:6px; font-size:12px; margin-top:12px; color:var(--text-primary);">
                    💡 <b>Skipper Directive:</b> If red squall echoes develop within 15 nm of fairway, abort deep-sea transit.
                </div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# SECTION 4: 🛟 SAFETY & ADVISORY (STATUS / ADVISORY / EMERGENCY)
# =========================================================

elif st.session_state.nav_section == "Safety & Advisory":
    st.markdown(f"""
    <div style="margin-bottom:14px;">
        <h2 style="margin:0; font-size:26px; font-weight:800; color:var(--text-primary);">Safety & Advisory</h2>
        <div style="font-size:14px; color:var(--text-muted); margin-top:2px;">
            Deterministic safety evaluation, ORCA AI natural language query, and emergency contacts.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Reusable Spacious SectionTabs
    safety_tabs = ["Operational Status", "Actionable Advisory", "Emergency"]
    st.session_state.sub_safety = render_section_tabs(safety_tabs, st.session_state.sub_safety, "tab_safety")

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # SUBVIEW 4.1: OPERATIONAL STATUS
    if st.session_state.sub_safety == "Operational Status":
        st.markdown(f"""
        <div class="ff-status-panel {status_cls}">
            <div>
                <div style="font-size:13px; font-weight:700; color:{status_color}; text-transform:uppercase; letter-spacing:0.8px;">
                    {status_icon} {status_title}
                </div>
                <div style="font-size:26px; font-weight:800; color:{status_color}; margin: 2px 0 4px 0;">
                    {status_tag}
                </div>
                <div style="font-size:13px; color:var(--text-secondary); max-width:720px; line-height:1.5;">
                    {status_desc}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:28px; font-weight:800; color:{status_color}; font-family:'JetBrains Mono';">
                    {res.safety.risk_score} <span style="font-size:14px; font-weight:600; color:var(--text-muted);">/ 100</span>
                </div>
                <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Risk Score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### 🛡️ Deterministic Rule Compliance Matrix (Zero-Hallucination Guardrails)")
        st.caption("All physical safety limits are evaluated deterministically in pure Python before AI synthesis.")

        audit_table = []
        for item in res.safety.audit_log:
            v_tag = "✅ PASS" if item.verdict == "PASS" else ("⚠️ CAUTION" if item.verdict == "CAUTION" else "❌ FAIL TRIGGER")
            audit_table.append({
                "Metric": item.metric,
                "Observed Telemetry": item.observed_value,
                "Regulatory Limit": item.threshold,
                "Standard / Source": item.regulatory_source,
                "Verdict": v_tag,
                "Physical Rationale": item.explanation
            })
        st.dataframe(audit_table, use_container_width=True)

    # SUBVIEW 4.2: ACTIONABLE ADVISORY & NATURAL QUERY
    elif st.session_state.sub_safety == "Actionable Advisory":
        st.markdown("##### 🤖 Ask ORCA Multi-Agent AI")
        q_col1, q_col2 = st.columns([9, 2])
        with q_col1:
            query_input = st.text_input(
                "Query ORCA:",
                value=st.session_state.query_text,
                placeholder="Ask query (e.g. Can we sail from Kochi for Yellowfin Tuna?)...",
                label_visibility="collapsed",
                key="adv_query_input"
            )
        with q_col2:
            if st.button("🔍 Query AI", use_container_width=True, key="btn_adv_query"):
                if query_input != st.session_state.query_text:
                    st.session_state.query_text = query_input
                    st.session_state.last_pipeline_result = None
                    st.rerun()

        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

        # Select Language
        lang_pills = ["English", "हिन्दी (Hindi)", "தமிழ் (Tamil)"]
        cur_l = 0
        if "Hindi" in st.session_state.advisory_lang or "हिन्दी" in st.session_state.advisory_lang:
            cur_l = 1
        elif "Tamil" in st.session_state.advisory_lang or "தமிழ்" in st.session_state.advisory_lang:
            cur_l = 2

        sel_l = st.segmented_control("Advisory Language", options=lang_pills, default=lang_pills[cur_l])
        if sel_l:
            st.session_state.advisory_lang = sel_l

        if "Hindi" in st.session_state.advisory_lang:
            adv = res.advisory.hindi
        elif "Tamil" in st.session_state.advisory_lang:
            adv = res.advisory.tamil
        else:
            adv = res.advisory.english

        # Audio Speech Synthesis Feature
        speech_lang_code = "hi-IN" if "Hindi" in st.session_state.advisory_lang else ("ta-IN" if "Tamil" in st.session_state.advisory_lang else "en-IN")
        speech_label = "🔊 ऑडियो में सुनें (Listen in Hindi)" if "Hindi" in st.session_state.advisory_lang else ("🔊 ஆடியோவில் கேளுங்கள் (Listen in Tamil)" if "Tamil" in st.session_state.advisory_lang else "🔊 Voice Audio Companion (Listen in English)")
        
        clean_speech_text = f"{adv['status_headline']}. {adv['safety_action']}. {adv['executive_summary']}"
        clean_speech_text = clean_speech_text.replace('"', ' ').replace("'", ' ').replace('\n', ' ').replace('\r', ' ')

        is_dark_theme = ("Dark" in st.session_state.selected_theme or "Tactical" in st.session_state.selected_theme)
        aud_bg = "rgba(56, 189, 248, 0.12)" if is_dark_theme else "rgba(2, 132, 199, 0.08)"
        aud_border = "#38bdf8" if is_dark_theme else "#0284c7"
        aud_text = "#38bdf8" if is_dark_theme else "#0284c7"
        aud_sub = "#cbd5e1" if is_dark_theme else "#64748b"
        aud_btn_primary = "#38bdf8" if is_dark_theme else "#0284c7"
        aud_btn_text = "#07111f" if is_dark_theme else "#ffffff"

        audio_html = f"""
        <div style="background:{aud_bg}; border:1px solid {aud_border}; border-radius:10px; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; font-family:'Plus Jakarta Sans', -apple-system, sans-serif;">
            <div>
                <div style="font-weight:700; font-size:14px; color:{aud_text};">{speech_label}</div>
                <div style="font-size:12px; color:{aud_sub}; margin-top:2px;">Spoken audio voice advisory for skippers & deckhands with zero reading required.</div>
            </div>
            <div style="display:flex; gap:8px;">
                <button id="tts-play-btn" onclick="playAdvisorySpeech()" style="background:{aud_btn_primary}; color:{aud_btn_text}; border:none; padding:8px 16px; border-radius:6px; font-weight:700; cursor:pointer; font-size:13px; box-shadow:0 1px 3px rgba(0,0,0,0.2);">
                    ▶ Play Voice
                </button>
                <button id="tts-stop-btn" onclick="stopAdvisorySpeech()" style="background:#475569; color:#ffffff; border:none; padding:8px 14px; border-radius:6px; font-weight:700; cursor:pointer; font-size:13px;">
                    ⏹ Stop
                </button>
            </div>
        </div>
        <script>
        function playAdvisorySpeech() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var utterance = new SpeechSynthesisUtterance("{clean_speech_text}");
                utterance.lang = "{speech_lang_code}";
                utterance.rate = 0.92;
                utterance.pitch = 1.0;
                window.speechSynthesis.speak(utterance);
            }} else {{
                alert("Speech synthesis is not supported in this browser.");
            }}
        }}
        function stopAdvisorySpeech() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
            }}
        }}
        </script>
        """
        components.html(audio_html, height=75)

        adv_col1, adv_col2 = st.columns([7, 5])
        with adv_col1:
            st.markdown(f"""
            <div class="ff-card">
                <h3 style="margin:0 0 10px 0; color:var(--primary); font-size:18px;">{adv['title']}</h3>
                <div style="font-weight:700; font-size:15px; margin-bottom:8px; color:var(--text-primary);">{adv['status_headline']}</div>
                <p style="font-size:13px; line-height:1.6; color:var(--text-secondary);">{adv['executive_summary']}</p>
                <div style="background:var(--primary-subtle); border-left:3px solid var(--primary); padding:10px 14px; border-radius:6px; font-size:13px; margin:12px 0; color:var(--text-primary);">
                    <b>Directive:</b> {adv['safety_action']}
                </div>
                <div style="font-size:13px; line-height:1.6; color:var(--text-secondary);">
                    <b>Target Fish Species:</b> {adv['recommended_pfz']['target_species']}<br>
                    <b>Recommended Zone:</b> {adv['recommended_pfz']['name']} ({adv['recommended_pfz']['coordinates']})<br>
                    <b>Distance & Heading:</b> {adv['recommended_pfz']['distance_bearing']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with adv_col2:
            st.markdown(f"""
            <div class="ff-card">
                <div style="font-size:15px; font-weight:700; color:var(--primary); margin-bottom:8px;">⛽ Transit & Fuel Economics</div>
                <div style="font-size:13px; line-height:1.7; color:var(--text-secondary);">
                    • <b>Transit Duration:</b> {adv['fuel_and_route']['estimated_transit']}<br>
                    • <b>Diesel Consumption:</b> {adv['fuel_and_route']['fuel_consumption']}<br>
                    • <b>Fuel Saved:</b> <span style="color:var(--success); font-weight:bold;">{adv['fuel_and_route']['fuel_savings']}</span><br>
                    • <b>Ocean Current Assist:</b> {adv['fuel_and_route']['current_notes']}<br>
                    • <b>Boundary Safety:</b> {adv['fuel_and_route']['border_safety']}
                </div>
                <div style="margin-top:14px; padding:10px; background:var(--primary-subtle); border-radius:6px; font-size:12px; color:var(--text-primary);">
                    📞 <b>Emergency Assistance:</b> {adv['emergency_contacts']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # SUBVIEW 4.3: EMERGENCY
    elif st.session_state.sub_safety == "Emergency":
        st.markdown(f"##### 🚨 24x7 Emergency Coastal Shore Guards & Helplines for **{res.port.name}**")
        st.caption("Official direct dispatch channels for sea emergencies, search & rescue (SAR), and border alerts.")

        em_h1, em_h2, em_h3, em_h4 = st.columns(4)
        with em_h1:
            st.markdown("""
            <div class="ff-card" style="text-align:center; border-top: 3px solid #0284c7;">
                <div style="font-size:11px; font-weight:700; color:#0284c7;">INDIAN COAST GUARD</div>
                <div style="font-size:22px; font-weight:800; color:#0284c7; margin:4px 0; font-family:'JetBrains Mono';">1554</div>
                <div style="font-size:11px; color:var(--text-muted);">Toll-Free 24x7 SAR</div>
            </div>
            """, unsafe_allow_html=True)

        with em_h2:
            st.markdown("""
            <div class="ff-card" style="text-align:center; border-top: 3px solid #059669;">
                <div style="font-size:11px; font-weight:700; color:#059669;">MARINE POLICE</div>
                <div style="font-size:22px; font-weight:800; color:#059669; margin:4px 0; font-family:'JetBrains Mono';">1093</div>
                <div style="font-size:11px; color:var(--text-muted);">Coastal Security</div>
            </div>
            """, unsafe_allow_html=True)

        with em_h3:
            st.markdown("""
            <div class="ff-card" style="text-align:center; border-top: 3px solid #d97706;">
                <div style="font-size:11px; font-weight:700; color:#d97706;">DISASTER MANAGEMENT</div>
                <div style="font-size:22px; font-weight:800; color:#d97706; margin:4px 0; font-family:'JetBrains Mono';">1070 / 1077</div>
                <div style="font-size:11px; color:var(--text-muted);">State / District SEOC</div>
            </div>
            """, unsafe_allow_html=True)

        with em_h4:
            st.markdown("""
            <div class="ff-card" style="text-align:center; border-top: 3px solid #dc2626;">
                <div style="font-size:11px; font-weight:700; color:#dc2626;">SEA AMBULANCE</div>
                <div style="font-size:22px; font-weight:800; color:#dc2626; margin:4px 0; font-family:'JetBrains Mono';">108</div>
                <div style="font-size:11px; color:var(--text-muted);">Medical Evacuation</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        contacts = res.emergency_contacts if res.emergency_contacts else get_emergency_contacts(res.port.id)
        
        c_left, c_right = st.columns(2)
        for idx, c in enumerate(contacts):
            target_col = c_left if idx % 2 == 0 else c_right
            with target_col:
                badge_color = "#0284c7" if "Coast Guard" in c.category else ("#059669" if "Police" in c.category else "#d97706")
                st.markdown(f"""
                <div class="ff-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <span style="font-size:11px; font-weight:700; color:{badge_color}; text-transform:uppercase;">
                                {c.category}
                            </span>
                            <div style="font-size:15px; font-weight:700; margin-top:2px; color:var(--text-primary);">{c.agency_name}</div>
                        </div>
                        <span style="font-size:12px; font-weight:700; background:var(--primary-subtle); color:var(--primary); padding:2px 8px; border-radius:4px;">
                            {c.toll_free}
                        </span>
                    </div>
                    <div style="font-size:12px; margin-top:8px; line-height:1.6; color:var(--text-secondary);">
                        📞 <b>Direct Phone:</b> {c.phone}<br>
                        📻 <b>Radio Channel:</b> <span style="font-weight:600; color:var(--primary);">{c.vhf_channel}</span><br>
                        📍 <b>Station Base:</b> {c.location} | <b>Sector:</b> {c.jurisdiction}<br>
                        🛡️ <b>Response Role:</b> {c.response_role}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# =========================================================
# SECTION 5: ⚙ SETTINGS (VESSEL & VOYAGE / PREFERENCES)
# =========================================================

elif st.session_state.nav_section == "Settings":
    st.markdown(f"""
    <div style="margin-bottom:14px;">
        <h2 style="margin:0; font-size:26px; font-weight:800; color:var(--text-primary);">Settings</h2>
        <div style="font-size:14px; color:var(--text-muted); margin-top:2px;">
            Vessel classification, departure timings, voice presets and user preferences.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Reusable Spacious SectionTabs
    settings_tabs = ["Vessel & Voyage", "Preferences"]
    st.session_state.sub_settings = render_section_tabs(settings_tabs, st.session_state.sub_settings, "tab_settings")

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # SUBVIEW 5.1: VESSEL & VOYAGE
    if st.session_state.sub_settings == "Vessel & Voyage":
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.markdown("##### ⛵ Vessel Classification & OAL")
            vessel_options = [
                "Mechanized Trawler (12-18m)",
                "Small Craft (<10m)",
                "FRP / Fiber Boat (8-10m)",
                "Deep-Sea Longliner (>20m)"
            ]
            cur_v_idx = vessel_options.index(st.session_state.vessel_class) if st.session_state.vessel_class in vessel_options else 0
            sel_vessel = st.selectbox(
                "Vessel Classification & Length Overall (OAL)",
                options=vessel_options,
                index=cur_v_idx,
                help="Small Craft (<10m) enforces stricter wave limits (<1.8m) under INCOIS/IMD safety standards."
            )
            if sel_vessel != st.session_state.vessel_class:
                st.session_state.vessel_class = sel_vessel
                st.session_state.last_pipeline_result = None
                st.rerun()

        with v_col2:
            st.markdown("##### ⏰ Departure Timing Window")
            dep_options = [
                "Immediate (Current Tide)",
                "Next High Water Window",
                "Dawn Departure (04:00 IST)",
                "Dusk Departure (17:00 IST)"
            ]
            cur_dep_idx = dep_options.index(st.session_state.departure_window) if st.session_state.departure_window in dep_options else 0
            sel_dep = st.selectbox(
                "Departure Window Synchronization",
                options=dep_options,
                index=cur_dep_idx,
                help="Harmonizes vessel departure with bar depth & tidal stream."
            )
            if sel_dep != st.session_state.departure_window:
                st.session_state.departure_window = sel_dep
                st.rerun()

        # Official Voyage Manifest & Clearance Slip
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 📋 Official Voyage Manifest & Port Clearance Slip")
        
        status_color = "var(--success)" if res.safety.status == "SAFE_GO" else ("var(--warning)" if res.safety.status == "CAUTION_CONDITIONAL" else "var(--danger)")
        manifest_ref = f"IND-MARITIME-{res.port.id.upper()}-{abs(hash(res.port.id + res.top_pfz.zone_id)) % 100000:05d}"
        
        st.markdown(f"""
        <div class="ff-card" style="border: 2px dashed var(--border-strong); background: var(--bg-subtle); padding: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom: 1px solid var(--border); padding-bottom: 12px;">
                <div>
                    <div style="font-size:16px; font-weight:800; color:var(--primary);">📑 OFFICIAL VOYAGE MANIFEST & CLEARANCE SLIP</div>
                    <div style="font-size:11px; color:var(--text-muted);">Ref: <b>{manifest_ref}</b> · Generated {datetime.now().strftime('%d-%b-%Y %H:%M IST')}</div>
                </div>
                <span style="font-size:12px; font-weight:800; color:{status_color}; background:rgba(0,0,0,0.06); padding:4px 10px; border-radius:4px; border:1px solid var(--border);">
                    {res.safety.status.replace('_', ' ')}
                </span>
            </div>
            <div style="font-size:13px; line-height:1.8; margin-top:12px; color:var(--text-secondary);">
                • <b>Vessel Registered:</b> {st.session_state.vessel_class} (Base Port: {res.port.name})<br>
                • <b>Departure Time:</b> {st.session_state.departure_window} | Water Level: {port_tides.current_water_level_m:.2f}m<br>
                • <b>Target PFZ Frontier:</b> {res.top_pfz.name} ({dist_label_top} · Bearing {res.top_pfz.bearing_deg}°)<br>
                • <b>Target Pelagic Species:</b> {', '.join(res.top_pfz.species_likely[:3])}<br>
                • <b>Tide & Harbor Bar:</b> {port_tides.tide_phase.split('(')[0]} · Depth {port_tides.harbor_bar_depth_m:.1f}m<br>
                • <b>Fuel Estimate:</b> ~{res.route.fuel_burn_liters} L (Current Assisted Saved: <b style="color:var(--success);">{res.route.fuel_savings_liters} L</b>)<br>
                • <b>Safety Guard:</b> IMBL {res.safety.border_distance_km} km ({res.safety.nearest_imbl_name})<br>
                • <b>Emergency SAR Dispatch:</b> Coast Guard 1554 · VHF Ch 16 (156.800 MHz) · Police 1093
            </div>
            <div style="margin-top:14px; text-align:right;">
                <button onclick="window.print()" style="background:var(--primary); color:var(--text-on-primary); font-weight:700; border:none; padding:8px 18px; border-radius:6px; cursor:pointer; font-size:13px;">
                    🖨️ Print Official Slip
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # SUBVIEW 5.2: PREFERENCES
    elif st.session_state.sub_settings == "Preferences":
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            st.markdown("##### 📏 Units & Display System")
            unit_options = ["Metric (km/h, km)", "Nautical (knots, nm)"]
            cur_u_idx = unit_options.index(st.session_state.unit_system) if st.session_state.unit_system in unit_options else 0
            sel_unit = st.selectbox(
                "Display Units",
                options=unit_options,
                index=cur_u_idx,
                help="Choose between metric units (km/h, km) and maritime nautical units (knots, nm)."
            )
            if sel_unit != st.session_state.unit_system:
                st.session_state.unit_system = sel_unit
                st.rerun()

            st.markdown("##### 🌐 Default Advisory Language")
            lang_opts = ["English", "हिन्दी (Hindi)", "தமிழ் (Tamil)"]
            cur_l_idx = 0
            if "Hindi" in st.session_state.advisory_lang:
                cur_l_idx = 1
            elif "Tamil" in st.session_state.advisory_lang:
                cur_l_idx = 2
            
            sel_lang = st.selectbox("Preferred Language", options=lang_opts, index=cur_l_idx)
            if sel_lang != st.session_state.advisory_lang:
                st.session_state.advisory_lang = sel_lang
                st.rerun()

            # Multilingual Voice Query Presets
            st.markdown("##### 🎙️ Quick Voice Query Presets")
            vp1, vp2 = st.columns(2)
            with vp1:
                if st.button("EN: Kochi Tuna", use_container_width=True, key="vp_en_kochi_set"):
                    st.session_state.query_text = "Can we sail from Kochi harbor for Yellowfin Tuna?"
                    st.session_state.active_port_id = "kochi"
                    st.session_state.advisory_lang = "English"
                    st.session_state.last_pipeline_result = None
                    st.session_state.nav_section = "Safety & Advisory"
                    st.session_state.sub_safety = "Actionable Advisory"
                    st.rerun()
                if st.button("TA: கொச்சி சூரை", use_container_width=True, key="vp_ta_kochi_set"):
                    st.session_state.query_text = "கொச்சியிலிருந்து இன்று சூரை மீன் பிடிக்க கடலுக்குச் செல்லலாமா?"
                    st.session_state.active_port_id = "kochi"
                    st.session_state.advisory_lang = "தமிழ்"
                    st.session_state.last_pipeline_result = None
                    st.session_state.nav_section = "Safety & Advisory"
                    st.session_state.sub_safety = "Actionable Advisory"
                    st.rerun()
            with vp2:
                if st.button("HI: वेरावल मछली", use_container_width=True, key="vp_hi_veraval_set"):
                    st.session_state.query_text = "क्या कल सुबह वेरावल से समुद्र में जाना सुरक्षित है?"
                    st.session_state.active_port_id = "veraval"
                    st.session_state.advisory_lang = "हिन्दी"
                    st.session_state.last_pipeline_result = None
                    st.session_state.nav_section = "Safety & Advisory"
                    st.session_state.sub_safety = "Actionable Advisory"
                    st.rerun()
                if st.button("EN: Pomfret Vizag", use_container_width=True, key="vp_en_vizag_set"):
                    st.session_state.query_text = "Visakhapatnam harbor to deep Bay of Bengal for Pomfret"
                    st.session_state.active_port_id = "visakhapatnam"
                    st.session_state.advisory_lang = "English"
                    st.session_state.last_pipeline_result = None
                    st.session_state.nav_section = "Safety & Advisory"
                    st.session_state.sub_safety = "Actionable Advisory"
                    st.rerun()

        with p_col2:
            st.markdown("##### 🎨 Cockpit Visual Theme")
            t_opts = ["☀️ Light", "🌙 Dark", "⚡ Tactical"]
            cur_t = 1
            if "Day" in st.session_state.selected_theme or "Light" in st.session_state.selected_theme:
                cur_t = 0
            elif "Tactical" in st.session_state.selected_theme:
                cur_t = 2

            sel_t = st.selectbox("Select Theme", options=t_opts, index=cur_t)
            theme_map_set = {
                "☀️ Light": "☀️ Ocula Sky Day",
                "🌙 Dark": "🌙 Ocula Oceanic Dark",
                "⚡ Tactical": "⚡ Tactical Radar"
            }
            if theme_map_set[sel_t] != st.session_state.selected_theme:
                st.session_state.selected_theme = theme_map_set[sel_t]
                st.rerun()

            st.markdown("""
            <div class="ff-card" style="margin-top:16px; font-size:12px; color:var(--text-secondary);">
                <b>Platform Specifications:</b><br>
                • Problem Statement: ISRO SIH26176 / sih_176<br>
                • Architecture: ORCA Multi-Agent AI (5 Collaborative Agents)<br>
                • Ingestion: ISRO Oceansat-3, INCOIS Rules, Open-Meteo, OpenSeaMap<br>
                • Zero-Hallucination Deterministic Guardrails
            </div>
            """, unsafe_allow_html=True)


# ---------------------------------------------------------
# GLOBAL FOOTER
# ---------------------------------------------------------
st.markdown("<div style='margin-top: 36px; border-top: 1px solid var(--border); padding-top: 14px;'></div>", unsafe_allow_html=True)
st.caption("FishingFriend · ORCA Marine Multi-Agent AI · ISRO SIH26176 · 100% Free Open Telemetry & Open-Source Marine Architecture · Designed for Indian Fishermen & Harbor Authorities.")
