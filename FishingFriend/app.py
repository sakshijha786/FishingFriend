"""
FishingFriend - ORCA Marine Multi-Agent AI & Tactical Maritime Cockpit
Problem Statement: ISRO Smart India Hackathon SIH26176 / sih_176

Redesigned with ChargeFlow SaaS UI Design System:
- Clean, crisp ultra-light slate background (#F8FAFC / #F1F5F9) & white surface cards (#FFFFFF)
- Deep Electric / Royal Blue (#2563EB / #1D4ED8) accents & pill navigation
- Replicated 2-Tier Navigation: Top Global Navigation Bar + Portal Sub-Navigation
- Replicated 7 Core Views:
  1. Overview / Landing Hero
  2. Harbor Admin Portal (KPIs + Tactical Ocean Map)
  3. Harbor Fleet Grid (Vessel Registry & Clearance Table)
  4. Mission Dispatch & PFZ (Walk-In Customer / Skipper Desk)
  5. Safety & IMBL Queue (Priority Queue & Deterministic Rule Audit Trail)
  6. SOS & Emergency Desk (Coast Guard SAR & Distress Modal)
  7. Marine Reports & Analytics (Tides, 48h Wave Forecast, Doppler Radar)
- 100% Preservation of all Open-Meteo live telemetry, ISRO Oceansat-3 bio-optical proxy,
  deterministic INCOIS/IMD safety guardrails, PFZ discovery, fuel routing, and audio synthesis.
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
    page_title="FishingFriend | ChargeFlow Marine SaaS",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CENTRALIZED CHARGEFLOW SEMANTIC DESIGN SYSTEM & CSS TOKENS
# ---------------------------------------------------------

def inject_theme(theme_name: str = "⚡ ChargeFlow Clean Light"):
    """
    Injects the ChargeFlow modern enterprise SaaS design tokens into Streamlit.
    Default: Ultra-clean light grey-white with crisp cards and royal blue primary accent.
    """
    if "Dark" in theme_name or "Oceanic" in theme_name:
        # Dark Mode option
        theme_vars = """
            --bg-page: #0b132b;
            --bg-surface: #111e38;
            --bg-surface-hover: #192b4d;
            --bg-elevated: #162544;
            --bg-subtle: #0f274a;
            --bg-nav: #080f21;
            --card-bg: #111e38;
            --card-border: #1e355c;
            --card-border-active: #3b82f6;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #8fa0b5;
            --text-on-primary: #ffffff;
            --border: #1e355c;
            --border-strong: #2e4d80;
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --primary-subtle: rgba(59, 130, 246, 0.15);
            --secondary: #0ea5e9;
            --accent: #60a5fa;
            --success: #22c55e;
            --success-bg: rgba(34, 197, 94, 0.15);
            --success-border: #166534;
            --warning: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.15);
            --warning-border: #92400e;
            --danger: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.15);
            --danger-border: #991b1b;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 14px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.5);
            --btn-bg: #182846;
            --btn-bg-hover: #20355b;
            --btn-text: #f8fafc;
            --btn-border: #294470;
            --btn-primary-bg: #2563eb;
            --btn-primary-bg-hover: #1d4ed8;
            --btn-primary-text: #ffffff;
            --btn-primary-border: #2563eb;
            --badge-avail-bg: #064e3b;
            --badge-avail-text: #6ee7b7;
            --badge-avail-border: #047857;
            --badge-inuse-bg: #78350f;
            --badge-inuse-text: #fde68a;
            --badge-inuse-border: #b45309;
            --badge-danger-bg: #7f1d1d;
            --badge-danger-text: #fca5a5;
            --badge-danger-border: #b91c1c;
            --badge-info-bg: #0c4a6e;
            --badge-info-text: #7dd3fc;
            --badge-info-border: #0284c7;
        """
        leaflet_tile = "cartodbdark_matter"
    elif "Tactical" in theme_name:
        # Tactical Radar Mode
        theme_vars = """
            --bg-page: #030712;
            --bg-surface: #0b1426;
            --bg-surface-hover: #11203b;
            --bg-elevated: #142544;
            --bg-subtle: #082f23;
            --bg-nav: #02040a;
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
            --primary-subtle: rgba(16, 185, 129, 0.15);
            --secondary: #00ff88;
            --accent: #06b6d4;
            --success: #10b981;
            --success-bg: rgba(16, 185, 129, 0.15);
            --success-border: #047857;
            --warning: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.15);
            --warning-border: #b45309;
            --danger: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.15);
            --danger-border: #b91c1c;
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.4);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.45);
            --shadow-lg: 0 8px 28px rgba(0, 0, 0, 0.55);
            --btn-bg: #0f1f38;
            --btn-bg-hover: #172f53;
            --btn-text: #f8fafc;
            --btn-border: #244169;
            --btn-primary-bg: #10b981;
            --btn-primary-bg-hover: #059669;
            --btn-primary-text: #030712;
            --btn-primary-border: #10b981;
            --badge-avail-bg: #064e3b;
            --badge-avail-text: #6ee7b7;
            --badge-avail-border: #047857;
            --badge-inuse-bg: #78350f;
            --badge-inuse-text: #fde68a;
            --badge-inuse-border: #b45309;
            --badge-danger-bg: #7f1d1d;
            --badge-danger-text: #fca5a5;
            --badge-danger-border: #b91c1c;
            --badge-info-bg: #0c4a6e;
            --badge-info-text: #7dd3fc;
            --badge-info-border: #0284c7;
        """
        leaflet_tile = "cartodbdark_matter"
    else:
        # ⚡ ChargeFlow Clean SaaS Light Mode (Default & Master Palette)
        theme_vars = """
            --bg-page: #f8fafc;
            --bg-surface: #ffffff;
            --bg-surface-hover: #f1f5f9;
            --bg-elevated: #ffffff;
            --bg-subtle: #eff6ff;
            --bg-nav: #ffffff;
            --card-bg: #ffffff;
            --card-border: #e2e8f0;
            --card-border-active: #2563eb;
            --text-primary: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            --text-on-primary: #ffffff;
            --border: #e2e8f0;
            --border-strong: #cbd5e1;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --primary-subtle: #eff6ff;
            --secondary: #3b82f6;
            --accent: #2563eb;
            --success: #166534;
            --success-bg: #dcfce7;
            --success-border: #bbf7d0;
            --warning: #92400e;
            --warning-bg: #fef3c7;
            --warning-border: #fde68a;
            --danger: #991b1b;
            --danger-bg: #fee2e2;
            --danger-border: #fecaca;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
            --btn-bg: #ffffff;
            --btn-bg-hover: #f8fafc;
            --btn-text: #0f172a;
            --btn-border: #e2e8f0;
            --btn-primary-bg: #2563eb;
            --btn-primary-bg-hover: #1d4ed8;
            --btn-primary-text: #ffffff;
            --btn-primary-border: #2563eb;
            --badge-avail-bg: #dcfce7;
            --badge-avail-text: #166534;
            --badge-avail-border: #bbf7d0;
            --badge-inuse-bg: #fef3c7;
            --badge-inuse-text: #92400e;
            --badge-inuse-border: #fde68a;
            --badge-danger-bg: #fee2e2;
            --badge-danger-text: #991b1b;
            --badge-danger-border: #fecaca;
            --badge-info-bg: #e0f2fe;
            --badge-info-text: #0369a1;
            --badge-info-border: #bae6fd;
        """
        leaflet_tile = "cartodbpositron"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    :root {{
        {theme_vars}
    }}

    /* Global Base Reset */
    .stApp {{
        background-color: var(--bg-page) !important;
        background: var(--bg-page) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        letter-spacing: -0.01em;
    }}

    /* Container Spacing */
    .main .block-container {{
        max-width: 1400px !important;
        padding-top: 1.0rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2.0rem !important;
        padding-right: 2.0rem !important;
    }}

    /* Top Global Navigation Bar Container */
    .cf-topbar {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 10px 18px;
        margin-bottom: 22px;
        box-shadow: var(--shadow-sm);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: wrap;
    }}

    /* ChargeFlow Card System */
    .cf-card {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }}
    .cf-card:hover {{
        border-color: var(--border-strong);
        box-shadow: var(--shadow-md);
    }}

    /* Stat KPI Cards (ChargeFlow 4-Grid Style) */
    .cf-stat-card {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: var(--shadow-sm);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .cf-stat-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--card-border-active);
    }}
    .cf-stat-label {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .cf-stat-value {{
        font-size: 26px;
        font-weight: 800;
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        margin: 6px 0 2px 0;
        letter-spacing: -0.03em;
    }}
    .cf-stat-delta {{
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }}
    .cf-delta-up {{
        color: #16a34a;
    }}
    .cf-delta-down {{
        color: #dc2626;
    }}
    .cf-delta-neutral {{
        color: var(--text-muted);
    }}

    /* ChargeFlow Pill Status Badges (11px, Uppercase, Bold) */
    .cf-badge {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 3px 10px;
        border-radius: 9999px;
        line-height: 1.3;
    }}
    .cf-badge-available {{
        background: var(--badge-avail-bg);
        color: var(--badge-avail-text);
        border: 1px solid var(--badge-avail-border);
    }}
    .cf-badge-inuse {{
        background: var(--badge-inuse-bg);
        color: var(--badge-inuse-text);
        border: 1px solid var(--badge-inuse-border);
    }}
    .cf-badge-danger {{
        background: var(--badge-danger-bg);
        color: var(--badge-danger-text);
        border: 1px solid var(--badge-danger-border);
    }}
    .cf-badge-info {{
        background: var(--badge-info-bg);
        color: var(--badge-info-text);
        border: 1px solid var(--badge-info-border);
    }}

    /* Status Banner / Operational Hero Bar */
    .cf-status-hero {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 22px 26px;
        margin-bottom: 22px;
        box-shadow: var(--shadow-sm);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }}
    .cf-status-hero-safe {{
        border-left: 6px solid #16a34a !important;
        background: linear-gradient(90deg, var(--success-bg) 0%, var(--card-bg) 35%) !important;
    }}
    .cf-status-hero-caution {{
        border-left: 6px solid #d97706 !important;
        background: linear-gradient(90deg, var(--warning-bg) 0%, var(--card-bg) 35%) !important;
    }}
    .cf-status-hero-danger {{
        border-left: 6px solid #dc2626 !important;
        background: linear-gradient(90deg, var(--danger-bg) 0%, var(--card-bg) 35%) !important;
    }}

    /* Circular SVG Gauge for Biomass / Sea State */
    .cf-gauge-wrap {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 18px 0;
    }}

    /* Sleek Dark Toast Pill */
    .cf-toast-pill {{
        background: #0f172a;
        color: #ffffff;
        font-size: 12px;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: var(--shadow-lg);
    }}
    .cf-pulse-dot {{
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        animation: cfPulse 2s infinite cubic-bezier(0.66, 0, 0, 1);
    }}
    @keyframes cfPulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }}
        70% {{ box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
    }}

    /* Clean Tabular Styling (Chargers Registry Replicated) */
    .cf-table-container {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }}
    table.cf-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        text-align: left;
    }}
    table.cf-table th {{
        background: var(--bg-surface-hover);
        color: var(--text-muted);
        font-weight: 700;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        padding: 12px 18px;
        border-bottom: 1px solid var(--border);
    }}
    table.cf-table td {{
        padding: 14px 18px;
        color: var(--text-primary);
        border-bottom: 1px solid var(--border);
        vertical-align: middle;
    }}
    table.cf-table tr:last-child td {{
        border-bottom: none;
    }}
    table.cf-table tr:hover td {{
        background: var(--bg-surface-hover);
    }}

    /* Streamlit Global Button Overrides (ChargeFlow SaaS Aesthetic) */
    div[data-testid="stButton"] > button:not([data-testid*="primary"]):not([kind="primary"]),
    div[data-testid="stButton"] button:not([data-testid*="primary"]):not([kind="primary"]),
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"] {{
        background-color: var(--btn-bg) !important;
        background: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        -webkit-text-fill-color: var(--btn-text) !important;
        border: 1px solid var(--btn-border) !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.0rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.15s ease !important;
    }}
    div[data-testid="stButton"] > button:not([data-testid*="primary"]):not([kind="primary"]):hover,
    div[data-testid="stButton"] button:not([data-testid*="primary"]):not([kind="primary"]):hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover {{
        background-color: var(--bg-surface-hover) !important;
        border-color: var(--primary) !important;
        color: var(--primary) !important;
        -webkit-text-fill-color: var(--primary) !important;
    }}

    /* Primary Action Buttons (Electric Blue) */
    div[data-testid="stButton"] > button[data-testid*="primary"],
    div[data-testid="stButton"] button[data-testid*="primary"],
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stButton"] button[kind="primary"],
    button[data-testid="baseButton-primary"],
    button[kind="primary"] {{
        background-color: var(--btn-primary-bg) !important;
        background: var(--btn-primary-bg) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid var(--btn-primary-border) !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.3) !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.15s ease !important;
    }}
    div[data-testid="stButton"] > button[data-testid*="primary"]:hover,
    div[data-testid="stButton"] button[data-testid*="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[kind="primary"]:hover {{
        background-color: var(--btn-primary-bg-hover) !important;
        background: var(--btn-primary-bg-hover) !important;
        border-color: var(--btn-primary-bg-hover) !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.4) !important;
        transform: translateY(-1px);
    }}

    /* Clean Input Fields */
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] input {{
        background-color: var(--bg-surface) !important;
        background: var(--bg-surface) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        border-radius: 10px !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }}

    /* Sidebar Drawer Reset (Dark Left Rail when expanded) */
    [data-testid="stSidebar"] {{
        background: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }}
    [data-testid="stSidebar"] * {{
        color: #f8fafc !important;
    }}
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg-page);
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-strong);
        border-radius: 4px;
    }}
    </style>
    """, unsafe_allow_html=True)
    return leaflet_tile


def render_clean_html(html_str: str):
    """
    Renders HTML cleanly without leading whitespace on lines to prevent
    Markdown parsers from treating indentation as <pre><code> blocks.
    """
    clean_lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    st.markdown("".join(clean_lines), unsafe_allow_html=True)

# ---------------------------------------------------------

def render_chargeflow_tactical_map(
    port: PortLocation,
    telemetry: OceanTelemetry,
    safety: HazardEvaluation,
    all_pfzs: List[PFZZone],
    selected_pfz: PFZZone,
    route: RouteWaypoints,
    theme_name: str,
    height: int = 540
):
    """
    Renders the modern tactical maritime map container with clean light basemaps,
    PFZ potential fishing hotspots, IMBL border polygons, and nautical markers.
    """
    base_tiles = "cartodbpositron" if ("Light" in theme_name or "ChargeFlow" in theme_name or "Day" in theme_name) else "cartodbdark_matter"

    m = folium.Map(
        location=[port.lat, port.lon],
        zoom_start=9,
        tiles=base_tiles,
        name="CartoDB Standard Chart",
        control_scale=True
    )

    # Layer 1: ESRI World Ocean Bathymetry
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS",
        name="🌊 Ocean Bathymetry (GEBCO / NOAA)",
        overlay=False,
        control=True
    ).add_to(m)

    # Layer 2: OpenSeaMap Nautical Marks & Buoys
    folium.TileLayer(
        tiles="https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
        attr="Map data &copy; <a href='http://www.openseamap.org'>OpenSeaMap</a>",
        name="⚓ OpenSeaMap (Buoys, Beacons, Depth)",
        overlay=True,
        control=True,
        show=True
    ).add_to(m)

    # Layer 3: Marine Protected Areas
    mpa_group = folium.FeatureGroup(name="🛡️ Marine Protected Areas (MSP)", show=True)
    for mpa in get_marine_spatial_zones(port.id):
        folium.Polygon(
            locations=mpa.coordinates,
            color=mpa.color,
            weight=2.5,
            fill=True,
            fill_color=mpa.color,
            fill_opacity=0.20,
            tooltip=f"🛡️ {mpa.name} ({mpa.category})",
            popup=folium.Popup(f"""
            <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #0f172a; min-width: 240px;">
                <h4 style="margin:0 0 6px 0; color:{mpa.color}; font-size:14px;">🛡️ {mpa.name}</h4>
                <b>Category:</b> {mpa.category}<br>
                <p style="margin:6px 0; font-size:11px; line-height:1.4;">{mpa.restriction}</p>
                <span style="font-size:10px; color:#64748b;"><b>Legal Basis:</b> {mpa.legal_source}</span>
            </div>
            """, max_width=300)
        ).add_to(mpa_group)
    mpa_group.add_to(m)

    # Layer 4: Base Harbor Station Marker
    harbor_popup = f"""
    <div style="font-family: 'Inter', sans-serif; font-size: 13px; color: #0f172a; min-width: 220px;">
        <h4 style="margin:0 0 6px 0; color:#2563eb; font-size:15px;">⚓ {port.name} Operations Hub</h4>
        <b>Wave:</b> {telemetry.wave_height}m | <b>Swell:</b> {telemetry.swell_wave_height}m ({telemetry.swell_wave_period}s)<br>
        <b>SST:</b> {telemetry.sea_surface_temperature}°C | <b>Wind:</b> {telemetry.wind_speed} km/h<br>
        <b>Ocean Current:</b> {telemetry.ocean_current_velocity} km/h @ {telemetry.ocean_current_direction:.0f}°<br>
        <span style="display:inline-block; margin-top:6px; font-weight:700; color:{'#166534' if safety.status=='SAFE_GO' else '#991b1b'};">
            ● Status: {safety.status.replace('_', ' ')}
        </span>
    </div>
    """
    folium.Marker(
        location=[port.lat, port.lon],
        tooltip=f"Base Harbor: {port.name}",
        popup=folium.Popup(harbor_popup, max_width=300),
        icon=folium.Icon(color="blue", icon="anchor", prefix="fa")
    ).add_to(m)

    # Layer 5: PFZ Zones (Potential Fishing Zones)
    pfz_group = folium.FeatureGroup(name="🐟 Potential Fishing Zones (PFZ)", show=True)
    for pfz in all_pfzs:
        is_selected = (pfz.zone_id == selected_pfz.zone_id)
        zone_color = "#2563eb" if is_selected else "#60a5fa"

        pfz_popup = f"""
        <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #0f172a; min-width: 230px;">
            <h4 style="margin:0 0 4px 0; color:#2563eb; font-size:14px;">🐟 {pfz.name}</h4>
            <b>PFZ Biomass Score:</b> <span style="color:#16a34a; font-weight:800;">{pfz.fish_density_score}%</span><br>
            <b>Range & Heading:</b> {pfz.distance_km} km @ {pfz.bearing_deg}°<br>
            <b>Target Species:</b> {', '.join(pfz.species_likely[:2])}<br>
            <b>Thermal Edge:</b> {pfz.sst_celsius}°C · Chl-a {pfz.chlorophyll_proxy} mg/m³
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
            tooltip=f"{pfz.name} ({pfz.fish_density_score}% Biomass Score)"
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

    # Layer 6: Fuel-Optimized Navigation Corridor
    route_group = folium.FeatureGroup(name="⛽ Fuel Navigation Corridor", show=True)
    folium.PolyLine(
        locations=route.waypoints,
        color="#2563eb",
        weight=4,
        opacity=0.9,
        dash_array="6, 6",
        tooltip=f"Route to {selected_pfz.name} ({route.total_distance_nm} nm · {route.fuel_burn_liters} L)"
    ).add_to(route_group)
    route_group.add_to(m)

    # Layer 7: International Maritime Boundary Lines (IMBL)
    imbl_group = folium.FeatureGroup(name="🛑 International Boundaries (IMBL)", show=True)
    for b_name, b_coords in IMBL_BOUNDARIES.items():
        folium.PolyLine(
            locations=b_coords,
            color="#ef4444",
            weight=2.5,
            opacity=0.9,
            dash_array="8, 6",
            tooltip=f"RESTRICTED: {b_name}"
        ).add_to(imbl_group)
    imbl_group.add_to(m)

    # Layer Controls
    folium.LayerControl(position="topright", collapsed=True).add_to(m)

    st_folium(m, height=height, use_container_width=True)


# ---------------------------------------------------------
# STATE MANAGEMENT & INITIALIZATION
# ---------------------------------------------------------

_CACHE_SCHEMA_VER = "v4.0_chargeflow_enterprise_saas"
if st.session_state.get("_cache_schema_ver") != _CACHE_SCHEMA_VER:
    st.session_state._cache_schema_ver = _CACHE_SCHEMA_VER
    st.session_state.last_pipeline_result = None

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = MultiAgentOrchestrator()

# Primary 2-Tier Navigation State
if "active_nav_tab" not in st.session_state:
    st.session_state.active_nav_tab = "Overview / Landing"

if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "⚡ ChargeFlow Clean Light"

if "active_port_id" not in st.session_state:
    st.session_state.active_port_id = "kochi"

if "user_role" not in st.session_state:
    st.session_state.user_role = "Harbor Master"

if "query_text" not in st.session_state:
    st.session_state.query_text = "Can we sail from Kochi harbor for Yellowfin Tuna?"

if "advisory_lang" not in st.session_state:
    st.session_state.advisory_lang = "English"

if "vessel_class" not in st.session_state:
    st.session_state.vessel_class = "Mechanized Trawler (12-18m)"

if "show_rule_explainer_modal" not in st.session_state:
    st.session_state.show_rule_explainer_modal = False

if "show_sos_modal" not in st.session_state:
    st.session_state.show_sos_modal = False

if "show_walkin_modal" not in st.session_state:
    st.session_state.show_walkin_modal = False

# Interactive Fleet Registry state (Replicating Chargers Registry Table)
if "fleet_registry" not in st.session_state:
    st.session_state.fleet_registry = [
        {"id": "IND-KC-104", "name": "Sea Queen IV", "harbor": "kochi", "tonnage": "18.5 T (Trawler)", "target": "Yellowfin Tuna", "fuel": "142 L", "status": "AVAILABLE", "clearance": "CLEARED"},
        {"id": "IND-VR-882", "name": "Matsya Raj", "harbor": "veraval", "tonnage": "14.0 T (Gillnetter)", "target": "Indian Mackerel", "fuel": "98 L", "status": "AVAILABLE", "clearance": "CLEARED"},
        {"id": "IND-CH-301", "name": "Ocean Hunter", "harbor": "chennai", "tonnage": "22.0 T (Longliner)", "target": "Yellowfin Tuna", "fuel": "210 L", "status": "SAILING", "clearance": "ACTIVE_VOYAGE"},
        {"id": "IND-MG-519", "name": "Netravati Pearl", "harbor": "mangalore", "tonnage": "12.0 T (Fiber Boat)", "target": "Sardine", "fuel": "64 L", "status": "AVAILABLE", "clearance": "CLEARED"},
        {"id": "IND-VZ-204", "name": "Bay Star", "harbor": "visakhapatnam", "tonnage": "25.0 T (Trawler)", "target": "Silver Pomfret", "fuel": "185 L", "status": "AVAILABLE", "clearance": "CLEARED"},
        {"id": "IND-TT-612", "name": "Pearl Diver III", "harbor": "thoothukudi", "tonnage": "9.5 T (Artisanal)", "target": "Reef Perch", "fuel": "45 L", "status": "RESTRICTED", "clearance": "HOLD_WEATHER"},
        {"id": "IND-PB-091", "name": "Saurashtra Rider", "harbor": "porbandar", "tonnage": "16.0 T (Trawler)", "target": "Indian Salmon", "fuel": "120 L", "status": "AVAILABLE", "clearance": "CLEARED"}
    ]

# Priority Queue Data (Replicating Priority Queue Control)
if "departure_queue" not in st.session_state:
    st.session_state.departure_queue = [
        {"vessel_id": "IND-KC-104", "skipper": "Capt. Rajeev Nair", "class": "COMMERCIAL FLEET", "priority": "P1 - COMMERCIAL", "departure": "05:00 IST", "pfz": "Cochin Ridge PFZ", "status": "APPROVED"},
        {"vessel_id": "IND-MG-519", "skipper": "S. K. Poojary", "class": "ARTISANAL CRAFT", "priority": "P2 - ARTISANAL", "departure": "05:30 IST", "pfz": "Mangalore Deep PFZ", "status": "APPROVED"},
        {"vessel_id": "IND-VR-882", "skipper": "Dinesh Solanki", "class": "COMMERCIAL FLEET", "priority": "P1 - COMMERCIAL", "departure": "06:00 IST", "pfz": "Veraval Southwest PFZ", "status": "QUEUED"},
        {"vessel_id": "IND-TT-612", "skipper": "M. Anthony", "class": "ARTISANAL CRAFT", "priority": "P3 - RESTRICTED", "departure": "HOLD", "pfz": "Tuticorin Bank", "status": "HOLD_INCOIS"}
    ]

# ---------------------------------------------------------
# EXECUTE DATA PIPELINE
# ---------------------------------------------------------

if (
    st.session_state.last_pipeline_result is None or
    st.session_state.last_pipeline_result.port.id != st.session_state.active_port_id or
    st.session_state.last_pipeline_result.query_intent.vessel_class != st.session_state.vessel_class
):
    with st.spinner("Executing Deterministic Marine Rule Engine & Live Telemetry Ingestion..."):
        res: ORCASynthesisResult = st.session_state.orchestrator.run_pipeline(
            query=st.session_state.query_text,
            selected_port_id=st.session_state.active_port_id,
            vessel_class=st.session_state.vessel_class
        )
        st.session_state.last_pipeline_result = res

res: ORCASynthesisResult = st.session_state.last_pipeline_result

# Compute fuel savings percentage
total_nominal_fuel = res.route.fuel_burn_liters + res.route.fuel_savings_liters
fuel_savings_pct = (res.route.fuel_savings_liters / max(1.0, total_nominal_fuel)) * 100.0 if total_nominal_fuel > 0 else 18.5

# Safe fallback for astronomical tides and hourly forecast
port_tides: PortTideData = res.tides if res.tides is not None else calculate_port_tides(res.port.id)
port_hourly: HourlyMarineForecast = res.hourly_forecast if res.hourly_forecast is not None else fetch_hourly_marine_forecast(res.port)

# Inject ChargeFlow CSS
inject_theme(st.session_state.selected_theme)

# ---------------------------------------------------------
# 1. TOP GLOBAL NAVIGATION BAR (TWO-TIER HIERARCHY)
# ---------------------------------------------------------

# Top Header Card Container
render_clean_html("""
<div style="background:var(--bg-surface); border:1px solid var(--border); border-radius:16px; padding:12px 22px; margin-bottom:18px; box-shadow:var(--shadow-sm); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
    <!-- Brand & Sub-badge -->
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:26px; line-height:1;">⚓</span>
        <div>
            <div style="font-size:18px; font-weight:800; color:var(--text-primary); letter-spacing:-0.02em; display:flex; align-items:center; gap:8px;">
                <span>FishingFriend</span>
                <span style="font-size:10px; font-weight:700; background:var(--primary-subtle); color:var(--primary); padding:2px 8px; border-radius:9999px; border:1px solid rgba(37,99,235,0.2);">RULE-BASED MARINE ENGINE</span>
            </div>
            <div style="font-size:11px; color:var(--text-muted); font-weight:500;">
                ISRO SIH26176 · ORCA Marine Ecosystem Reasoning
            </div>
        </div>
    </div>
    <!-- Right Live Pill & Role Badge -->
    <div style="display:flex; align-items:center; gap:12px;">
        <div class="cf-toast-pill">
            <span class="cf-pulse-dot"></span>
            <span>Local Rule Engine Active</span>
        </div>
        <div style="background:var(--bg-surface-hover); border:1px solid var(--border); padding:6px 12px; border-radius:10px; font-size:12px; font-weight:600; color:var(--text-secondary); display:flex; align-items:center; gap:6px;">
            <span>👤</span>
            <span>Harbor Master Desk</span>
        </div>
    </div>
</div>
""")

# 7 Center Primary Navigation Tabs (Pill Structure)
nav_tabs = [
    "Overview / Landing",
    "Harbor Admin Portal",
    "Harbor Fleet Grid",
    "Mission Dispatch & PFZ",
    "Safety & IMBL Queue",
    "SOS & Emergency Desk",
    "Marine Reports & Analytics"
]

# Quick Switcher & Port Bar
t_cols = st.columns([1.1, 1.3, 1.2, 1.4, 1.3, 1.3, 1.4, 1.0])
for idx, tab_name in enumerate(nav_tabs):
    with t_cols[idx]:
        is_active = (st.session_state.active_nav_tab == tab_name)
        btn_type = "primary" if is_active else "secondary"
        tab_short = {
            "Overview / Landing": "🌐 Overview",
            "Harbor Admin Portal": "🏢 Operations",
            "Harbor Fleet Grid": "🚢 Fleet Grid",
            "Mission Dispatch & PFZ": "🎯 Dispatch & PFZ",
            "Safety & IMBL Queue": "🛡️ Safety Queue",
            "SOS & Emergency Desk": "🚨 SOS Desk",
            "Marine Reports & Analytics": "📊 Analytics"
        }.get(tab_name, tab_name)
        
        if st.button(tab_short, key=f"top_tab_{idx}", type=btn_type, use_container_width=True):
            st.session_state.active_nav_tab = tab_name
            st.rerun()

with t_cols[7]:
    if st.button("🚨 SOS", type="primary", key="btn_quick_sos", use_container_width=True):
        st.session_state.show_sos_modal = not st.session_state.show_sos_modal
        st.rerun()

# Harbor Quick Selector Strip
h_c1, h_c2, h_c3, h_c4 = st.columns([4, 3, 3, 2])
with h_c1:
    port_list = list(INDIAN_PORTS.keys())
    cur_p_idx = port_list.index(st.session_state.active_port_id) if st.session_state.active_port_id in port_list else 0
    selected_p = st.selectbox(
        "Active Operational Harbor",
        options=port_list,
        format_func=lambda pid: f"⚓ {INDIAN_PORTS[pid].name} ({INDIAN_PORTS[pid].state} · {INDIAN_PORTS[pid].coast})",
        index=cur_p_idx,
        label_visibility="collapsed",
        key="global_port_selector"
    )
    if selected_p != st.session_state.active_port_id:
        st.session_state.active_port_id = selected_p
        st.session_state.query_text = f"Can we sail from {INDIAN_PORTS[selected_p].name} for Yellowfin Tuna?"
        st.session_state.last_pipeline_result = None
        st.rerun()

with h_c2:
    v_opts = ["Mechanized Trawler (12-18m)", "Traditional Motorized (<10m)", "Deep-Sea Longliner (>20m)", "FRP Fiber Boat (8-10m)"]
    cur_v = v_opts.index(st.session_state.vessel_class) if st.session_state.vessel_class in v_opts else 0
    sel_v = st.selectbox("Vessel Class", options=v_opts, index=cur_v, label_visibility="collapsed", key="global_vessel_sel")
    if sel_v != st.session_state.vessel_class:
        st.session_state.vessel_class = sel_v
        st.session_state.last_pipeline_result = None
        st.rerun()

with h_c3:
    lang_opts = ["English", "हिन्दी (Hindi)", "தமிழ் (Tamil)"]
    cur_l = 0
    if "Hindi" in st.session_state.advisory_lang or "हिन्दी" in st.session_state.advisory_lang:
        cur_l = 1
    elif "Tamil" in st.session_state.advisory_lang or "தமிழ்" in st.session_state.advisory_lang:
        cur_l = 2
    sel_lang = st.selectbox("Language", options=lang_opts, index=cur_l, label_visibility="collapsed", key="global_lang_sel")
    if sel_lang != st.session_state.advisory_lang:
        st.session_state.advisory_lang = sel_lang
        st.rerun()

with h_c4:
    t_opts = ["⚡ ChargeFlow Clean Light", "🌙 Oceanic Dark", "⚡ Tactical Radar"]
    cur_t = 0
    if "Dark" in st.session_state.selected_theme:
        cur_t = 1
    elif "Tactical" in st.session_state.selected_theme:
        cur_t = 2
    sel_t = st.selectbox("Theme", options=t_opts, index=cur_t, label_visibility="collapsed", key="global_theme_sel")
    if sel_t != st.session_state.selected_theme:
        st.session_state.selected_theme = sel_t
        st.rerun()

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# GLOBAL MODALS (SOS / RULE EXPLAINER)
# ---------------------------------------------------------

if st.session_state.show_sos_modal:
    render_clean_html("""
    <div style="background:#fee2e2; border:2px solid #ef4444; border-radius:16px; padding:22px 26px; margin-bottom:20px; box-shadow:var(--shadow-lg);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:18px; font-weight:800; color:#991b1b; display:flex; align-items:center; gap:8px;">
                <span>🚨</span> EMERGENCY MARITIME DISTRESS DESK (MAYDAY PROTOCOL)
            </div>
            <span class="cf-badge cf-badge-danger">VHF CH 16 / SAR 1554</span>
        </div>
        <p style="font-size:13px; color:#7f1d1d; margin:6px 0 14px 0;">
            Immediate broadcast channel for Indian Coast Guard Maritime Rescue Co-ordination Centres (MRCC) & Coastal Police.
        </p>
    </div>
    """)

    s1, s2 = st.columns([7, 3])
    with s1:
        distress_payload = (
            f"MAYDAY MAYDAY MAYDAY\n"
            f"STATION: {res.port.name} Marine Operations Hub\n"
            f"VESSEL CLASS: {st.session_state.vessel_class}\n"
            f"COORDINATES: Lat {res.port.lat:.4f}° N, Lon {res.port.lon:.4f}° E\n"
            f"SEA STATE: Wave {res.telemetry.wave_height}m | Swell {res.telemetry.swell_wave_height}m | Wind {res.telemetry.wind_speed} km/h\n"
            f"IMBL DISTANCE: {res.safety.border_distance_km} km to {res.safety.nearest_imbl_name}\n"
            f"SAR CHANNELS: VHF 156.800 MHz (Ch 16) | Toll-Free Coast Guard: 1554"
        )
        st.code(distress_payload, language="text")
    with s2:
        render_clean_html("""
        <div style="font-size:12px; line-height:1.8; color:var(--text-primary);">
            <b>📞 National Sea Helplines:</b><br>
            • Coast Guard MRCC: <b style="color:#2563eb;">1554</b><br>
            • Coastal Police: <b style="color:#16a34a;">1093</b><br>
            • National Emergency: <b>112</b><br>
            • Sea Ambulance: <b>108</b>
        </div>
        """)
        if st.button("📡 Transmit Simulated Mayday", type="primary", use_container_width=True, key="btn_send_mayday"):
            st.success("✅ Mayday payload acknowledged by Indian Coast Guard SAR Station.")
        if st.button("✕ Close Emergency Desk", use_container_width=True, key="btn_close_sos_modal"):
            st.session_state.show_sos_modal = False
            st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


if st.session_state.show_rule_explainer_modal:
    render_clean_html("""
    <div class="cf-card" style="border-left: 5px solid #2563eb;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:16px; font-weight:800; color:var(--primary);">
                📖 DETERMINISTIC MARINE RULE ARCHITECTURE (ZERO HALLUCINATION)
            </div>
            <span class="cf-badge cf-badge-info">INCOIS / IMD COMPLIANT</span>
        </div>
        <p style="font-size:13px; color:var(--text-secondary); margin:8px 0 14px 0;">
            Unlike generic generative models that fabricate navigation points, FishingFriend executes 100% deterministic physical mathematical algorithms in pure Python before any synthesis.
        </p>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:14px;">
            <div style="background:var(--success-bg); border:1px solid var(--success-border); padding:12px 14px; border-radius:10px;">
                <b style="color:var(--success); font-size:13px;">🌊 1. INCOIS Swell Guardrail</b>
                <p style="font-size:12px; margin:4px 0 0 0; color:var(--text-secondary); line-height:1.4;">
                    Swell wave height > 2.50m triggers instantaneous Hard NO-GO refusal.
                </p>
            </div>
            <div style="background:var(--badge-info-bg); border:1px solid var(--badge-info-border); padding:12px 14px; border-radius:10px;">
                <b style="color:var(--primary); font-size:13px;">🐟 2. Oceansat-3 PFZ Fronts</b>
                <p style="font-size:12px; margin:4px 0 0 0; color:var(--text-secondary); line-height:1.4;">
                    Chlorophyll-a gradients (>0.4 mg/m³) & SST fronts (26-29°C) calculate pelagic fish density.
                </p>
            </div>
            <div style="background:var(--danger-bg); border:1px solid var(--danger-border); padding:12px 14px; border-radius:10px;">
                <b style="color:var(--danger); font-size:13px;">🛑 3. IMBL Geofencing</b>
                <p style="font-size:12px; margin:4px 0 0 0; color:var(--text-secondary); line-height:1.4;">
                    Strict 10 NM safety exclusion corridor off Pakistan, Sri Lanka & Bangladesh borders.
                </p>
            </div>
            <div style="background:var(--warning-bg); border:1px solid var(--warning-border); padding:12px 14px; border-radius:10px;">
                <b style="color:var(--warning); font-size:13px;">⛽ 4. Current-Assisted Drift</b>
                <p style="font-size:12px; margin:4px 0 0 0; color:var(--text-secondary); line-height:1.4;">
                    Vectors calculate fuel burn reductions (~15-22% diesel savings) along rhumb lines.
                </p>
            </div>
        </div>
    </div>
    """)
    if st.button("✕ Close Rule Architecture", key="btn_close_rule_explainer"):
        st.session_state.show_rule_explainer_modal = False
        st.rerun()


# =========================================================
# SCREEN 1: 🌐 OVERVIEW / LANDING HERO
# Replicating ChargeFlow Landing Hero Screen
# =========================================================

if st.session_state.active_nav_tab == "Overview / Landing":

    # Hero Badge Pill
    render_clean_html("""
    <div style="text-align:center; padding: 24px 10px 10px 10px;">
        <div style="display:inline-block; background:var(--primary-subtle); border:1px solid rgba(37,99,235,0.25); color:var(--primary); font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; padding:6px 16px; border-radius:9999px; margin-bottom:16px;">
            ⚡ DETERMINISTIC RULE-BASED MARINE ADVISORY (NO AI/ML HALLUCINATION)
        </div>
        <h1 style="font-size:40px; font-weight:800; color:var(--text-primary); letter-spacing:-0.03em; margin:0 auto 12px auto; max-width:920px; line-height:1.15;">
            Smart Marine Ecosystem Reasoning & Coastal Fleet Safety Engine
        </h1>
        <p style="font-size:16px; color:var(--text-secondary); max-width:780px; margin:0 auto 24px auto; line-height:1.6;">
            Eliminate rough sea navigation risks and boundary cross-overs. Real-time satellite telemetry correlation, strict INCOIS wave thresholds, fuel-efficient PFZ waypoints, and automated regional voice dispatch.
        </p>
    </div>
    """)

    # Dual CTA Buttons
    cta1, cta2, cta3, cta4 = st.columns([3, 3, 3, 3])
    with cta2:
        if st.button("🚀 Launch Operations Demo", type="primary", use_container_width=True, key="hero_cta_demo"):
            st.session_state.active_nav_tab = "Harbor Admin Portal"
            st.rerun()
    with cta3:
        if st.button("📖 How Rule Engine Works", use_container_width=True, key="hero_cta_rules"):
            st.session_state.show_rule_explainer_modal = True
            st.rerun()

    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)

    # 3 Metric Hero Cards Horizontally Stacked
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        render_clean_html("""
        <div class="cf-card" style="text-align:center; padding:24px 20px;">
            <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase; letter-spacing:0.6px;">
                AVAILABLE HARBORS
            </div>
            <div style="font-size:32px; font-weight:800; color:var(--text-primary); margin:8px 0 4px 0;">
                7 Major Ports Active
            </div>
            <div style="font-size:12px; color:var(--text-muted);">
                Veraval, Kochi, Chennai, Vizag, Mangalore, Tuticorin, Porbandar
            </div>
        </div>
        """)

    with mc2:
        wave_status_text = "Favorable" if res.safety.status == "SAFE_GO" else ("Caution" if res.safety.status == "CAUTION_CONDITIONAL" else "Dangerous")
        wave_color = "#16a34a" if res.safety.status == "SAFE_GO" else ("#d97706" if res.safety.status == "CAUTION_CONDITIONAL" else "#dc2626")
        render_clean_html(f"""
        <div class="cf-card" style="text-align:center; padding:24px 20px;">
            <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase; letter-spacing:0.6px;">
                ACTIVE SEA STATE ({res.port.name})
            </div>
            <div style="font-size:32px; font-weight:800; color:{wave_color}; margin:8px 0 4px 0;">
                Swell {res.telemetry.swell_wave_height}m | {wave_status_text}
            </div>
            <div style="font-size:12px; color:var(--text-muted);">
                INCOIS Alert Level: <b>{res.safety.incois_alert_level.replace('_', ' ')}</b>
            </div>
        </div>
        """)

    with mc3:
        render_clean_html("""
        <div class="cf-card" style="text-align:center; padding:24px 20px;">
            <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase; letter-spacing:0.6px;">
                MONITORED COASTAL ZONES
            </div>
            <div style="font-size:32px; font-weight:800; color:var(--text-primary); margin:8px 0 4px 0;">
                EEZ & Border Safety
            </div>
            <div style="font-size:12px; color:var(--text-muted);">
                Arabian Sea, Bay of Bengal, Palk Strait & Gulf of Mannar
            </div>
        </div>
        """)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # Rule Architecture Grid (4 Clean Bordered Cards)
    st.markdown("### ⚙️ Deterministic Marine Rule Architecture")
    r_col1, r_col2, r_col3, r_col4 = st.columns(4)

    with r_col1:
        render_clean_html("""
        <div class="cf-card" style="height:100%; border-top: 4px solid #2563eb;">
            <div style="font-size:14px; font-weight:700; color:var(--text-primary); margin-bottom:8px;">
                🌊 1. Swell & Current Compatibility
            </div>
            <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin:0;">
                Wave swell &gt; 2.5m triggers instantaneous Hard NO-GO under INCOIS safety protocols.
            </p>
            <div style="margin-top:12px;">
                <span class="cf-badge cf-badge-danger">LIMIT: 2.50 M</span>
            </div>
        </div>
        """)

    with r_col2:
        render_clean_html("""
        <div class="cf-card" style="height:100%; border-top: 4px solid #16a34a;">
            <div style="font-size:14px; font-weight:700; color:var(--text-primary); margin-bottom:8px;">
                🐟 2. Bio-Optical Biomass
            </div>
            <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin:0;">
                Chlorophyll-a & SST thermal front correlation identifies high-density pelagic aggregations.
            </p>
            <div style="margin-top:12px;">
                <span class="cf-badge cf-badge-available">ISRO OCEANSAT-3</span>
            </div>
        </div>
        """)

    with r_col3:
        render_clean_html("""
        <div class="cf-card" style="height:100%; border-top: 4px solid #dc2626;">
            <div style="font-size:14px; font-weight:700; color:var(--text-primary); margin-bottom:8px;">
                🛑 3. Maritime Border Fence
            </div>
            <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin:0;">
                Enforces strict 10 NM safety exclusion corridor against international boundary lines (IMBL).
            </p>
            <div style="margin-top:12px;">
                <span class="cf-badge cf-badge-danger">BUFFER: 10 NM</span>
            </div>
        </div>
        """)

    with r_col4:
        render_clean_html("""
        <div class="cf-card" style="height:100%; border-top: 4px solid #d97706;">
            <div style="font-size:14px; font-weight:700; color:var(--text-primary); margin-bottom:8px;">
                🚨 4. Distress Auto-Escalation
            </div>
            <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin:0;">
                Emergency SOS broadcast payload formulation with VHF Ch 16 & Coast Guard MRCC 1554 dispatch.
            </p>
            <div style="margin-top:12px;">
                <span class="cf-badge cf-badge-inuse">VHF 16 & SAR 1554</span>
            </div>
        </div>
        """)


# =========================================================
# SCREEN 2: 🏢 HARBOR ADMIN PORTAL (OPERATIONS CONTROL)
# Replicating ChargeFlow Admin Portal
# =========================================================

elif st.session_state.active_nav_tab == "Harbor Admin Portal":

    # Header with live subtitle + Right Action Buttons
    admin_hdr1, admin_hdr2 = st.columns([7, 3])
    with admin_hdr1:
        render_clean_html(f"""
        <div>
            <h2 style="font-size:26px; font-weight:800; margin:0; color:var(--text-primary); letter-spacing:-0.02em;">
                Harbor Operations Control
            </h2>
            <div style="font-size:13px; color:var(--text-muted); margin-top:2px;">
                📍 <b>{res.port.name} Operations Hub</b> · {res.port.state} ({res.port.coast}) · Live Buoy Sync: {datetime.now().strftime('%d-%b-%Y %H:%M IST')}
            </div>
        </div>
        """)

    with admin_hdr2:
        btn_a1, btn_a2 = st.columns(2)
        with btn_a1:
            if st.button("+ Dispatch Vessel", type="primary", use_container_width=True, key="btn_add_dispatch"):
                st.session_state.active_nav_tab = "Mission Dispatch & PFZ"
                st.rerun()
        with btn_a2:
            if st.button("Walk-In Skipper", use_container_width=True, key="btn_walkin_reg"):
                st.session_state.show_walkin_modal = True
                st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    if st.session_state.show_walkin_modal:
        render_clean_html("""
        <div class="cf-card" style="border-left: 4px solid var(--primary);">
            <div style="font-size:15px; font-weight:700; color:var(--primary); margin-bottom:8px;">
                ⚓ Fast Walk-In Skipper Registration Desk
            </div>
            <div style="font-size:13px; color:var(--text-secondary);">
                Register an incoming artisanal or mechanized boat for immediate harbor clearance and PFZ waypoint calculation.
            </div>
        </div>
        """)
        w_c1, w_c2, w_c3 = st.columns(3)
        with w_c1:
            st.text_input("Skipper Full Name", value="Capt. Ramesh Patel", key="wi_name")
        with w_c2:
            st.text_input("Craft Reg No.", value=f"IND-{res.port.id.upper()}-991", key="wi_reg")
        with w_c3:
            st.selectbox("Craft Category", options=["Mechanized Trawler", "Traditional (<10m)", "FRP Fiber Boat"], key="wi_cat")
        if st.button("Submit Walk-in & Run Route Engine", type="primary", key="btn_wi_submit"):
            st.success("✅ Walk-in skipper registered and cleared for route computation.")
            st.session_state.show_walkin_modal = False
            st.session_state.active_nav_tab = "Mission Dispatch & PFZ"
            st.rerun()

    # 4 Top KPI Stat Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        cleared_count = sum(1 for v in st.session_state.fleet_registry if v["clearance"] == "CLEARED")
        render_clean_html(f"""
        <div class="cf-stat-card">
            <div class="cf-stat-label">
                <span>AVAILABLE FLEET CLEARANCES</span>
                <span class="cf-badge cf-badge-available">LIVE</span>
            </div>
            <div class="cf-stat-value">{cleared_count} Craft Ready</div>
            <div class="cf-stat-delta cf-delta-up">
                <span>↑ 100% Harbor Fairway Open</span>
            </div>
        </div>
        """)

    with kpi2:
        swell_delta = "Safe (<2.0m)" if res.telemetry.swell_wave_height < 2.0 else "Caution (>2.0m)"
        delta_class = "cf-delta-up" if res.telemetry.swell_wave_height < 2.0 else "cf-delta-down"
        render_clean_html(f"""
        <div class="cf-stat-card">
            <div class="cf-stat-label">
                <span>ACTIVE HARBOR WAVE SWELL</span>
                <span class="cf-badge cf-badge-info">INCOIS</span>
            </div>
            <div class="cf-stat-value">{res.telemetry.swell_wave_height:.2f} m</div>
            <div class="cf-stat-delta {delta_class}">
                <span>● Period {res.telemetry.swell_wave_period}s ({swell_delta})</span>
            </div>
        </div>
        """)

    with kpi3:
        queue_len = len(st.session_state.departure_queue)
        render_clean_html(f"""
        <div class="cf-stat-card">
            <div class="cf-stat-label">
                <span>DEPARTURE QUEUE LENGTH</span>
                <span class="cf-badge cf-badge-inuse">TRANSIT</span>
            </div>
            <div class="cf-stat-value">{queue_len} Vessels Scheduled</div>
            <div class="cf-stat-delta cf-delta-neutral">
                <span>Next Tide: {port_tides.tide_phase.split('(')[0].strip()}</span>
            </div>
        </div>
        """)

    with kpi4:
        render_clean_html(f"""
        <div class="cf-stat-card">
            <div class="cf-stat-label">
                <span>AVG DIESEL FUEL SAVINGS</span>
                <span class="cf-badge cf-badge-available">OCEAN DRIFT</span>
            </div>
            <div class="cf-stat-value">{fuel_savings_pct:.1f}% Saved</div>
            <div class="cf-stat-delta cf-delta-up">
                <span>~{res.route.fuel_savings_liters:.1f} L saved via drift corridor</span>
            </div>
        </div>
        """)

    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

    # Operational Clearance Banner
    if res.safety.status == "SAFE_GO":
        hero_cls = "cf-status-hero-safe"
        hero_badge = '<span class="cf-badge cf-badge-available">CLEARED TO SAIL</span>'
        hero_title = "GREEN SAFE: Normal Sea State & Unrestricted Navigation"
    elif res.safety.status == "CAUTION_CONDITIONAL":
        hero_cls = "cf-status-hero-caution"
        hero_badge = '<span class="cf-badge cf-badge-inuse">CAUTION ADVISED</span>'
        hero_title = "AMBER CAUTION: Moderate Swell / Traditional Craft Restrained"
    else:
        hero_cls = "cf-status-hero-danger"
        hero_badge = '<span class="cf-badge cf-badge-danger">OPERATIONS SUSPENDED</span>'
        hero_title = "RED DANGER: High Wave Alert (INCOIS Threshold Breached)"

    render_clean_html(f"""
    <div class="cf-status-hero {hero_cls}">
        <div>
            <div style="margin-bottom:6px;">{hero_badge}</div>
            <div style="font-size:18px; font-weight:800; color:var(--text-primary);">{hero_title}</div>
            <div style="font-size:13px; color:var(--text-secondary); margin-top:4px; max-width:750px;">
                Observed Swell {res.telemetry.swell_wave_height}m | Wind {res.telemetry.wind_speed} km/h | 
                Target Fishing Zone: <b>{res.top_pfz.name}</b> ({res.top_pfz.fish_density_score}% Score).
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:26px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono';">
                {res.safety.risk_score} <span style="font-size:14px; color:var(--text-muted);">/ 100</span>
            </div>
            <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Hazard Risk Score</div>
        </div>
    </div>
    """)

    # Main Tactical Map Card
    render_clean_html("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <div style="font-size:16px; font-weight:700; color:var(--text-primary);">
            Tactical Ocean Map & Geospatial Operations Fairway
        </div>
        <span style="font-size:12px; color:var(--text-muted);">
            CartoDB Light · OpenSeaMap · Oceansat-3 PFZ Hotspots · IMBL Geofencing
        </span>
    </div>
    """)

    render_chargeflow_tactical_map(
        port=res.port,
        telemetry=res.telemetry,
        safety=res.safety,
        all_pfzs=res.all_pfzs,
        selected_pfz=res.top_pfz,
        route=res.route,
        theme_name=st.session_state.selected_theme,
        height=560
    )


# =========================================================
# SCREEN 3: 🚢 HARBOR FLEET GRID (VESSEL REGISTRY TABLE)
# Replicating ChargeFlow Chargers Registry Table
# =========================================================

elif st.session_state.active_nav_tab == "Harbor Fleet Grid":

    render_clean_html("""
    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:18px;">
        <div>
            <h2 style="font-size:26px; font-weight:800; margin:0; color:var(--text-primary);">
                Coastal Fleet & Harbor Registry
            </h2>
            <div style="font-size:13px; color:var(--text-muted); margin-top:2px;">
                Real-time tracking of registered coastal trawlers, artisanal skippers, clearance certificates, and fuel burn metrics.
            </div>
        </div>
    </div>
    """)

    # Search & Filter Strip
    f_c1, f_c2, f_c3 = st.columns([5, 4, 3])
    with f_c1:
        search_query = st.text_input("Search vessel ID or skipper name", placeholder="🔍 Search IND-KC-104, Sea Queen...", label_visibility="collapsed")
    with f_c2:
        filter_status = st.selectbox("Filter Status", options=["All Statuses", "AVAILABLE", "SAILING", "RESTRICTED"], label_visibility="collapsed")
    with f_c3:
        if st.button("↻ Refresh Fleet State", use_container_width=True):
            st.rerun()

    # Replicated Clean HTML Table
    table_rows = []
    for v in st.session_state.fleet_registry:
        if filter_status != "All Statuses" and v["status"] != filter_status:
            continue
        if search_query and search_query.lower() not in v["id"].lower() and search_query.lower() not in v["name"].lower():
            continue

        if v["status"] == "AVAILABLE":
            badge_html = '<span class="cf-badge cf-badge-available">AVAILABLE</span>'
        elif v["status"] == "SAILING":
            badge_html = '<span class="cf-badge cf-badge-info">SAILING / IN USE</span>'
        else:
            badge_html = '<span class="cf-badge cf-badge-danger">RESTRICTED</span>'

        port_name = INDIAN_PORTS.get(v['harbor'], res.port).name
        table_rows.append(f"""<tr><td><b>{v['id']}</b><br><span style="font-size:12px; color:var(--text-muted);">{v['name']}</span></td><td>📍 {port_name}</td><td>{v['tonnage']}</td><td>🐟 {v['target']}</td><td><b>{v['fuel']}</b></td><td>{badge_html}</td><td><span style="font-size:12px; font-weight:700; color:var(--primary);">[ Cleared ]</span></td></tr>""")

    table_html = f"""<div class="cf-table-container"><table class="cf-table"><thead><tr><th>Vessel ID & Name</th><th>Harbor Base</th><th>Engine & Tonnage</th><th>Target Zone</th><th>Est. Fuel Transit</th><th>Clearance Status</th><th>Action</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div>"""
    render_clean_html(table_html)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Interactive Toggle Clearance Action
    st.markdown("##### ⚡ Quick Harbor Clearance Operations")
    tc1, tc2, tc3 = st.columns([4, 4, 4])
    with tc1:
        v_ids = [v["id"] for v in st.session_state.fleet_registry]
        sel_v_id = st.selectbox("Select Vessel ID", options=v_ids)
    with tc2:
        new_status = st.selectbox("New Clearance State", options=["AVAILABLE", "SAILING", "RESTRICTED"])
    with tc3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if st.button("Apply Status Change", type="primary", use_container_width=True):
            for v in st.session_state.fleet_registry:
                if v["id"] == sel_v_id:
                    v["status"] = new_status
                    v["clearance"] = "CLEARED" if new_status == "AVAILABLE" else ("ACTIVE_VOYAGE" if new_status == "SAILING" else "HOLD_WEATHER")
            st.success(f"Status for {sel_v_id} updated to {new_status}!")
            st.rerun()


# =========================================================
# SCREEN 4: 🎯 MISSION DISPATCH & PFZ (WALK-IN DESK FORM)
# Replicating ChargeFlow Walk-In Customer Desk Form
# =========================================================

elif st.session_state.active_nav_tab == "Mission Dispatch & PFZ":

    render_clean_html("""
    <div>
        <h2 style="font-size:26px; font-weight:800; margin:0; color:var(--text-primary);">
            Mission Dispatch Desk & Safe PFZ Calculator
        </h2>
        <div style="font-size:13px; color:var(--text-muted); margin-top:2px;">
            Input vessel voyage parameters to compute deterministic fuel-optimized PFZ rhumb-line corridors.
        </div>
    </div>
    """)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    d_col1, d_col2 = st.columns([7, 5])

    with d_col1:
        render_clean_html("""
        <div class="cf-card">
            <div style="font-size:16px; font-weight:700; color:var(--primary); margin-bottom:14px;">
                📋 Skipper & Craft Registration Form
            </div>
        """)

        fc1, fc2 = st.columns(2)
        with fc1:
            skipper_name = st.text_input("Skipper Full Name", value="Capt. Murugan Velu")
            craft_reg = st.text_input("Vessel Registration No.", value=f"IND-{res.port.id.upper()}-402")
            dep_harbor = st.selectbox(
                "Departure Harbor Base",
                options=list(INDIAN_PORTS.keys()),
                index=list(INDIAN_PORTS.keys()).index(st.session_state.active_port_id),
                format_func=lambda x: f"⚓ {INDIAN_PORTS[x].name} ({INDIAN_PORTS[x].state})"
            )

        with fc2:
            skipper_phone = st.text_input("Skipper Mobile Phone", value="+91 98401 23456")
            target_species = st.selectbox("Target Fish Species", options=["Yellowfin Tuna", "Indian Mackerel", "Sardine", "Silver Pomfret", "Kingfish"])
            adv_lang_choice = st.selectbox("Preferred Voice Language", options=["English", "हिन्दी (Hindi)", "தமிழ் (Tamil)"])

        radius_nm = st.slider("Trip Operational Radius (Nautical Miles)", min_value=10, max_value=60, value=25, step=5)

        

        if st.button("🚀 Compute Safe PFZ Route via Rule Engine", type="primary", use_container_width=True, key="btn_run_dispatch_calc"):
            st.session_state.active_port_id = dep_harbor
            st.session_state.query_text = f"Can we sail from {INDIAN_PORTS[dep_harbor].name} for {target_species}?"
            st.session_state.advisory_lang = adv_lang_choice
            st.session_state.last_pipeline_result = None
            st.success(f"✅ Route successfully computed for {skipper_name} ({craft_reg}) to {res.top_pfz.name}!")
            st.rerun()

    with d_col2:
        render_clean_html(f"""
        <div class="cf-card" style="height:100%; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-muted);">
                    OPTIMIZED FISHING ZONE TARGET
                </div>
                <div style="font-size:20px; font-weight:800; color:var(--primary); margin:6px 0 2px 0;">
                    ⭐ {res.top_pfz.name}
                </div>
                <div style="font-size:13px; color:var(--text-secondary); line-height:1.6; margin-top:8px;">
                    • <b>Catch Probability:</b> <span style="color:#16a34a; font-weight:800;">{res.top_pfz.fish_density_score}%</span><br>
                    • <b>Range & Bearing:</b> {res.route.total_distance_nm:.1f} NM @ {res.top_pfz.bearing_deg}°<br>
                    • <b>Transit Fuel Burn:</b> ~{res.route.fuel_burn_liters:.1f} Liters Diesel<br>
                    • <b>Ocean Current Assisted Savings:</b> <span style="color:#16a34a; font-weight:700;">{res.route.fuel_savings_liters:.1f} L ({fuel_savings_pct:.1f}%)</span><br>
                    • <b>IMBL Nearest Border:</b> {res.safety.border_distance_km} km ({res.safety.nearest_imbl_name})
                </div>
            </div>
            <div style="margin-top:14px; padding:12px; background:var(--primary-subtle); border-radius:10px; font-size:12px; color:var(--text-primary);">
                💡 <b>ISRO Satellite Synthesis:</b> Thermal front edge at {res.top_pfz.sst_celsius}°C with Chlorophyll-a proxy {res.top_pfz.chlorophyll_proxy} mg/m³.
            </div>
        </div>
        """)

    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

    # Discovered PFZ Zones Grid
    st.markdown("##### 🐟 All Discovered Potential Fishing Zones (Oceansat-3)")
    z_cols = st.columns(len(res.all_pfzs))
    for idx, (zc, pz) in enumerate(zip(z_cols, res.all_pfzs)):
        with zc:
            is_top = (pz.zone_id == res.top_pfz.zone_id)
            top_badge = '<span class="cf-badge cf-badge-available">TOP RECOMMENDATION</span>' if is_top else '<span class="cf-badge cf-badge-info">SECONDARY</span>'
            border_color = "var(--primary)" if is_top else "var(--card-border)"
            render_clean_html(f"""
            <div class="cf-card" style="border-color:{border_color}; padding:16px;">
                <div style="margin-bottom:8px;">{top_badge}</div>
                <div style="font-size:16px; font-weight:800; color:var(--primary);">{pz.name}</div>
                <div style="font-size:22px; font-weight:800; color:#16a34a; margin:6px 0;">{pz.fish_density_score}% <span style="font-size:12px; color:var(--text-muted);">Catch</span></div>
                <div style="font-size:12px; color:var(--text-secondary); line-height:1.5;">
                    Distance: {pz.distance_km} km @ {pz.bearing_deg}°<br>
                    Depth: {pz.depth_m}m · SST: {pz.sst_celsius}°C
                </div>
            </div>
            """)


# =========================================================
# SCREEN 5: 🛡️ SAFETY & IMBL QUEUE (PRIORITY QUEUE & AUDIT TRAIL)
# Replicating ChargeFlow Priority Queue Control & Session Audit
# =========================================================

elif st.session_state.active_nav_tab == "Safety & IMBL Queue":

    render_clean_html("""
    <div>
        <h2 style="font-size:26px; font-weight:800; margin:0; color:var(--text-primary);">
            Safety & Priority Departure Queue Control
        </h2>
        <div style="font-size:13px; color:var(--text-muted); margin-top:2px;">
            Deterministic compliance verification, IMBL safety buffers, and prioritized vessel dispatch queue.
        </div>
    </div>
    """)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # Priority Departure Queue Cards
    st.markdown("##### ⏱️ Active Departure Queue & Class Priority")
    q_rows = []
    for q in st.session_state.departure_queue:
        if "COMMERCIAL" in q["class"]:
            p_badge = '<span class="cf-badge cf-badge-info">COMMERCIAL FLEET</span>'
        elif "ARTISANAL" in q["class"]:
            p_badge = '<span class="cf-badge cf-badge-available">ARTISANAL CRAFT</span>'
        else:
            p_badge = '<span class="cf-badge cf-badge-danger">EMERGENCY SOS</span>'

        q_status_badge = '<span class="cf-badge cf-badge-available">APPROVED</span>' if q["status"] == "APPROVED" else ('<span class="cf-badge cf-badge-inuse">QUEUED</span>' if q["status"] == "QUEUED" else '<span class="cf-badge cf-badge-danger">HOLD WEATHER</span>')
        q_rows.append(f"""<tr><td><b>{q['vessel_id']}</b></td><td>{q['skipper']}</td><td>{p_badge}</td><td><b>{q['priority']}</b></td><td>{q['departure']}</td><td>{q['pfz']}</td><td>{q_status_badge}</td></tr>""")

    q_table_html = f"""<div class="cf-table-container"><table class="cf-table"><thead><tr><th>Vessel Reg</th><th>Skipper Name</th><th>Craft Class</th><th>Priority Level</th><th>Departure Window</th><th>Target Frontier</th><th>Queue Status</th></tr></thead><tbody>{''.join(q_rows)}</tbody></table></div>"""
    render_clean_html(q_table_html)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # Deterministic Rule Decision Audit Trail
    st.markdown("##### 📜 Deterministic Rule Engine Decision Audit Trail")
    st.caption("Chronological zero-hallucination verification records for every physical boundary & telemetry metric.")

    for item in res.safety.audit_log:
        is_pass = (item.verdict == "PASS")
        is_caution = (item.verdict == "CAUTION")
        v_badge = '<span class="cf-badge cf-badge-available">RULE_PASS</span>' if is_pass else ('<span class="cf-badge cf-badge-inuse">CAUTION</span>' if is_caution else '<span class="cf-badge cf-badge-danger">FAIL_TRIGGER</span>')
        border_col = "#16a34a" if is_pass else ("#d97706" if is_caution else "#dc2626")

        render_clean_html(f"""
        <div class="cf-card" style="border-left: 4px solid {border_col}; padding: 14px 18px; margin-bottom: 10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:8px;">
                    {v_badge}
                    <b style="font-size:14px; color:var(--text-primary);">{item.metric}</b>
                </div>
                <span style="font-size:11px; color:var(--text-muted); font-weight:600;">{item.regulatory_source}</span>
            </div>
            <div style="font-size:13px; color:var(--text-secondary); margin-top:6px; line-height:1.5;">
                • <b>Observed:</b> {item.observed_value} | <b>Threshold Limit:</b> {item.threshold}<br>
                • <b>Physical Evaluation:</b> {item.explanation}
            </div>
        </div>
        """)


# =========================================================
# SCREEN 6: 🚨 SOS & EMERGENCY DESK (SEARCH & RESCUE)
# Replicating ChargeFlow Emergency Modal & Direct Dispatch
# =========================================================

elif st.session_state.active_nav_tab == "SOS & Emergency Desk":

    render_clean_html("""
    <div>
        <h2 style="font-size:26px; font-weight:800; margin:0; color:#dc2626;">
            🚨 Coastal Search & Rescue (SAR) & Emergency Desk
        </h2>
        <div style="font-size:13px; color:var(--text-muted); margin-top:2px;">
            Official direct dispatch hotlines, VHF radio distress watch, and regional MRCC contacts.
        </div>
    </div>
    """)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # 4 Emergency Hotlines
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        render_clean_html("""
        <div class="cf-card" style="text-align:center; border-top: 4px solid #2563eb;">
            <div style="font-size:11px; font-weight:700; color:#2563eb; text-transform:uppercase;">INDIAN COAST GUARD</div>
            <div style="font-size:30px; font-weight:800; color:#2563eb; margin:6px 0; font-family:'JetBrains Mono';">1554</div>
            <div style="font-size:11px; color:var(--text-muted);">24x7 Toll-Free SAR</div>
        </div>
        """)

    with e2:
        render_clean_html("""
        <div class="cf-card" style="text-align:center; border-top: 4px solid #16a34a;">
            <div style="font-size:11px; font-weight:700; color:#16a34a; text-transform:uppercase;">COASTAL POLICE</div>
            <div style="font-size:30px; font-weight:800; color:#16a34a; margin:6px 0; font-family:'JetBrains Mono';">1093</div>
            <div style="font-size:11px; color:var(--text-muted);">Marine Security</div>
        </div>
        """)

    with e3:
        render_clean_html("""
        <div class="cf-card" style="text-align:center; border-top: 4px solid #d97706;">
            <div style="font-size:11px; font-weight:700; color:#d97706; text-transform:uppercase;">NATIONAL EMERGENCY</div>
            <div style="font-size:30px; font-weight:800; color:#d97706; margin:6px 0; font-family:'JetBrains Mono';">112</div>
            <div style="font-size:11px; color:var(--text-muted);">All Services Relay</div>
        </div>
        """)

    with e4:
        render_clean_html("""
        <div class="cf-card" style="text-align:center; border-top: 4px solid #dc2626;">
            <div style="font-size:11px; font-weight:700; color:#dc2626; text-transform:uppercase;">SEA AMBULANCE</div>
            <div style="font-size:30px; font-weight:800; color:#dc2626; margin:6px 0; font-family:'JetBrains Mono';">108</div>
            <div style="font-size:11px; color:var(--text-muted);">Critical Evacuation</div>
        </div>
        """)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # Direct Station Contacts Grid
    st.markdown(f"##### 📍 Regional Station Contacts for **{res.port.name}**")
    contacts = res.emergency_contacts if res.emergency_contacts else get_emergency_contacts(res.port.id)

    ec_left, ec_right = st.columns(2)
    for idx, c in enumerate(contacts):
        col_target = ec_left if idx % 2 == 0 else ec_right
        with col_target:
            render_clean_html(f"""
            <div class="cf-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <span class="cf-badge cf-badge-info">{c.category}</span>
                        <div style="font-size:16px; font-weight:700; color:var(--text-primary); margin-top:4px;">{c.agency_name}</div>
                    </div>
                    <span style="font-size:14px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono';">{c.toll_free}</span>
                </div>
                <div style="font-size:13px; color:var(--text-secondary); margin-top:8px; line-height:1.6;">
                    📞 <b>Direct Phone:</b> {c.phone}<br>
                    📻 <b>VHF Channel:</b> <b style="color:var(--primary);">{c.vhf_channel}</b><br>
                    📍 <b>Station:</b> {c.location} | <b>Sector:</b> {c.jurisdiction}<br>
                    🛡️ <b>Role:</b> {c.response_role}
                </div>
            </div>
            """)

    # Official Voyage Manifest & Print Slip
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 📋 Official Maritime Dispatch Slip & Port Clearance Manifest")
    manifest_ref = f"IND-MARITIME-{res.port.id.upper()}-{abs(hash(res.port.id + res.top_pfz.zone_id)) % 100000:05d}"
    
    render_clean_html(f"""
    <div class="cf-card" style="border: 2px dashed var(--border-strong); background: var(--bg-subtle);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom:1px solid var(--border); padding-bottom:10px;">
            <div>
                <div style="font-size:16px; font-weight:800; color:var(--primary);">📑 OFFICIAL VOYAGE MANIFEST & CLEARANCE SLIP</div>
                <div style="font-size:11px; color:var(--text-muted);">Ref: <b>{manifest_ref}</b> · Generated {datetime.now().strftime('%d-%b-%Y %H:%M IST')}</div>
            </div>
            <span class="cf-badge cf-badge-available">{res.safety.status.replace('_', ' ')}</span>
        </div>
        <div style="font-size:13px; line-height:1.8; margin-top:12px; color:var(--text-secondary);">
            • <b>Vessel Registered:</b> {st.session_state.vessel_class} (Hub: {res.port.name})<br>
            • <b>Target PFZ Frontier:</b> {res.top_pfz.name} ({res.route.total_distance_nm:.1f} NM @ {res.top_pfz.bearing_deg}°)<br>
            • <b>Target Species:</b> {', '.join(res.top_pfz.species_likely[:3])}<br>
            • <b>Tidal Phase:</b> {port_tides.tide_phase.split('(')[0]} · Bar Depth {port_tides.harbor_bar_depth_m:.1f}m<br>
            • <b>Estimated Transit Fuel:</b> ~{res.route.fuel_burn_liters:.1f} L (Current-Assisted Saved: <b style="color:#16a34a;">{res.route.fuel_savings_liters:.1f} L</b>)<br>
            • <b>Safety Geofence:</b> IMBL {res.safety.border_distance_km} km ({res.safety.nearest_imbl_name})<br>
            • <b>Search & Rescue:</b> Coast Guard 1554 · VHF Ch 16 (156.800 MHz)
        </div>
        <div style="margin-top:14px; text-align:right;">
            <button onclick="window.print()" style="background:#2563eb; color:#ffffff; font-weight:700; border:none; padding:8px 18px; border-radius:8px; cursor:pointer; font-size:13px; box-shadow:0 1px 3px rgba(37,99,235,0.3);">
                🖨️ Print Official Clearance Manifest
            </button>
        </div>
    </div>
    """)


# =========================================================
# SCREEN 7: 📊 MARINE REPORTS & ANALYTICS (TIDES, FORECAST, RADAR)
# Replicating ChargeFlow Analytics Dashboard
# =========================================================

elif st.session_state.active_nav_tab == "Marine Reports & Analytics":

    render_clean_html(f"""
    <div>
        <h2 style="font-size:26px; font-weight:800; margin:0; color:var(--text-primary);">
            Marine Reports & Oceanographic Analytics
        </h2>
        <div style="font-size:13px; color:var(--text-muted); margin-top:2px;">
            48-hour continuous wave forecast, harmonic astronomical tides, and Doppler precipitation radar for <b>{res.port.name}</b>.
        </div>
    </div>
    """)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    # 3 Analytics Sub-tabs
    an_t1, an_t2, an_t3 = st.tabs(["🌊 48-Hour Wave Forecast", "📈 Astronomical Tides", "📡 Live Doppler Radar"])

    with an_t1:
        st.markdown("##### 🌊 48-Hour Wave & Swell Height Forecast (Open-Meteo)")
        st.caption("Includes the INCOIS 2.50m High Wave Red Alert Safety Threshold Line.")

        hourly_plot_data = []
        for h in port_hourly.hours:
            hourly_plot_data.append({
                "Hour": h.hour_label,
                "Significant Wave (m)": h.wave_height_m,
                "Swell Height (m)": h.swell_wave_height_m,
                "Wind Gust (km/h)": h.wind_gusts_kmh,
                "Precipitation (%)": h.precipitation_probability_pct
            })
        df_hourly = pd.DataFrame(hourly_plot_data)

        chart_wave = alt.Chart(df_hourly).mark_line(
            interpolate="monotone",
            color="#2563eb",
            strokeWidth=3
        ).encode(
            x=alt.X("Hour:N", title="Forecast Timeline (IST)", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Significant Wave (m):Q", title="Wave Height (m)", scale=alt.Scale(domain=[0, max(3.0, port_hourly.max_wave_height + 0.5)])),
            tooltip=["Hour:N", "Significant Wave (m):Q", "Swell Height (m):Q", "Wind Gust (km/h):Q"]
        )

        danger_line = alt.Chart(pd.DataFrame([{"y": 2.5}])).mark_rule(
            color="#ef4444",
            strokeWidth=2,
            strokeDash=[6, 4]
        ).encode(y="y:Q")

        final_chart = (chart_wave + danger_line).properties(height=280)
        st.altair_chart(final_chart, use_container_width=True)

    with an_t2:
        st.markdown(f"##### 📈 Astronomical Tidal Curve for **{port_tides.port_name}**")
        st.caption(f"Current Water Level: {port_tides.current_water_level_m:.2f}m · Tidal Phase: {port_tides.tide_phase}")

        tide_plot_data = []
        for p in port_tides.hourly_heights_48h:
            tide_plot_data.append({
                "Time": p.time_str,
                "Tide Height (m)": p.height_m
            })
        df_tides = pd.DataFrame(tide_plot_data)

        tide_line = alt.Chart(df_tides).mark_line(
            interpolate="monotone",
            color="#2563eb",
            strokeWidth=3
        ).encode(
            x=alt.X("Time:N", title="Timeline (IST)", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Tide Height (m):Q", title="Water Level (m Above Datum)", scale=alt.Scale(zero=False)),
            tooltip=["Time:N", "Tide Height (m):Q"]
        )

        tide_area = alt.Chart(df_tides).mark_area(
            interpolate="monotone",
            color="#2563eb",
            opacity=0.15
        ).encode(
            x=alt.X("Time:N"),
            y=alt.Y("Tide Height (m):Q")
        )

        st.altair_chart((tide_area + tide_line).properties(height=280), use_container_width=True)

    with an_t3:
        st.markdown(f"##### 📡 Live Doppler Precipitation Radar for **{res.port.name}**")
        st.caption("Connected to Indian coastal radar network via RainViewer.")
        render_clean_html(f"""
        <div class="cf-card" style="padding:10px;">
            <iframe 
                src="https://www.rainviewer.com/map.html?loc={res.port.lat},{res.port.lon},8&oFa=0&oC=1&oU=0&oCS=1&oF=0&oAP=1&c=3&o=83&lm=1&layer=radar&sm=1&sn=1" 
                width="100%" 
                height="460" 
                style="border:none; border-radius:10px;"
                allowfullscreen>
            </iframe>
        </div>
        """)


# ---------------------------------------------------------
# ACTIVE VOYAGE MONITOR & SPOKEN VOICE SYNTHESIZER
# (Present across bottom of active operational sessions)
# ---------------------------------------------------------

if st.session_state.active_nav_tab in ["Harbor Admin Portal", "Mission Dispatch & PFZ"]:
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    if "Hindi" in st.session_state.advisory_lang or "हिन्दी" in st.session_state.advisory_lang:
        adv = res.advisory.hindi
        speech_code = "hi-IN"
        speech_btn_title = "▶ ऑडियो में सुनें (Listen in Hindi)"
    elif "Tamil" in st.session_state.advisory_lang or "தமிழ்" in st.session_state.advisory_lang:
        adv = res.advisory.tamil
        speech_code = "ta-IN"
        speech_btn_title = "▶ ஆடியோவில் கேளுங்கள் (Listen in Tamil)"
    else:
        adv = res.advisory.english
        speech_code = "en-IN"
        speech_btn_title = "▶ Voice Audio Advisory (Listen in English)"

    clean_speech_text = f"{adv['status_headline']}. {adv['safety_action']}. {adv['executive_summary']}"
    clean_speech_text = clean_speech_text.replace('"', ' ').replace("'", ' ').replace('\n', ' ').replace('\r', ' ')

    # Audio synthesis player
    audio_widget = f"""
    <div style="background:var(--bg-subtle); border:1px solid var(--border); border-radius:14px; padding:14px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; box-shadow:var(--shadow-sm); font-family:'Inter', sans-serif;">
        <div>
            <div style="font-weight:700; font-size:14px; color:var(--primary);">{speech_btn_title}</div>
            <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">Automated regional voice speech companion for fishermen and skippers with zero reading required.</div>
        </div>
        <div style="display:flex; gap:8px;">
            <button onclick="playVoiceSpeech()" style="background:#2563eb; color:#ffffff; border:none; padding:8px 16px; border-radius:8px; font-weight:700; cursor:pointer; font-size:13px; box-shadow:0 1px 3px rgba(37,99,235,0.3);">
                ▶ Play Voice
            </button>
            <button onclick="stopVoiceSpeech()" style="background:#64748b; color:#ffffff; border:none; padding:8px 14px; border-radius:8px; font-weight:700; cursor:pointer; font-size:13px;">
                ⏹ Stop
            </button>
        </div>
    </div>
    <script>
    function playVoiceSpeech() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{clean_speech_text}");
            msg.lang = "{speech_code}";
            msg.rate = 0.92;
            window.speechSynthesis.speak(msg);
        }}
    }}
    function stopVoiceSpeech() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
        }}
    }}
    </script>
    """
    components.html(audio_widget, height=80)

# Global Footer
st.markdown("<div style='margin-top: 36px; border-top: 1px solid var(--border); padding-top: 14px;'></div>", unsafe_allow_html=True)
st.caption("FishingFriend · ORCA Marine Multi-Agent AI · ISRO SIH26176 · Inspired by ChargeFlow Modern SaaS Aesthetic · Designed for Indian Coastal Fishermen & Harbor Authorities.")
