"""
FishingFriend - ORCA Marine Multi-Agent AI & Tactical Maritime Cockpit
Problem Statement: ISRO Smart India Hackathon SIH26176 / sih_176

Professional Marine Intelligence & Fishing Operations Platform Redesign:
- 5 Primary Navigation Sections: Dashboard, Explore, Conditions, Safety & Advisory, Settings
- Sub-navigation via progressive disclosure & dedicated views
- Global App Shell Header: Harbor selector, Theme, Language, Guide & SOP, Emergency SOS
- Unified Semantic Token CSS System (Ocula Sky Day, Ocula Oceanic Dark, Tactical Radar)
- 100% Functionality Preservation (ISRO PFZ, INCOIS/IMD Safety, Astronomical Tides,
  48h Forecast, OpenSeaMap & ESRI Bathymetry, RainViewer Radar, MarineMap MPAs,
  Animated Current Streamlines, Multilingual TTS Advisory, Zero-Hallucination Audit)
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
    page_title="FishingFriend | ORCA Marine Operations Cockpit",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CENTRALIZED SEMANTIC THEME TOKEN SYSTEM
# ---------------------------------------------------------

def inject_theme(theme_name: str):
    """
    Injects a centralized semantic design-token system that globally guarantees
    perfect contrast, high legibility, and zero invisible text across all screens.
    """
    if "Day" in theme_name:
        # ☀️ Ocula Sky Day (Light Mode)
        theme_vars = """
            --bg-base: #f0f7ff;
            --bg-gradient: linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%);
            --bg-surface: #ffffff;
            --bg-surface-hover: #f8fbff;
            --bg-elevated: #ffffff;
            --card-bg: #ffffff;
            --card-border: #cbd5e1;
            --card-border-active: #0284c7;
            --text-primary: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            --text-inverse: #ffffff;
            --primary: #0284c7;
            --primary-hover: #0369a1;
            --primary-subtle: rgba(2, 132, 199, 0.08);
            --secondary: #0ea5e9;
            --accent: #38bdf8;
            --success: #15803d;
            --success-bg: rgba(21, 128, 61, 0.08);
            --warning: #b45309;
            --warning-bg: rgba(180, 83, 9, 0.08);
            --danger: #b91c1c;
            --danger-bg: rgba(185, 28, 28, 0.08);
            --border: #e2e8f0;
            --border-subtle: #cbd5e1;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);
            --shadow-md: 0 4px 14px rgba(2, 132, 199, 0.08);
            --shadow-lg: 0 8px 24px rgba(2, 132, 199, 0.12);
            --chart-main: #0284c7;
            --chart-sec: #0ea5e9;
            --chart-subtle: #38bdf8;
        """
        leaflet_tile = "cartodbpositron"
    elif "Tactical" in theme_name:
        # ⚡ Tactical Radar Cockpit (Cyber-GIS Phosphor Dark)
        theme_vars = """
            --bg-base: #030712;
            --bg-gradient: linear-gradient(180deg, #030712 0%, #0a0f1d 100%);
            --bg-surface: #0b1324;
            --bg-surface-hover: #111c34;
            --bg-elevated: #14223d;
            --card-bg: #0b1324;
            --card-border: #1e293b;
            --card-border-active: #10b981;
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --text-inverse: #030712;
            --primary: #10b981;
            --primary-hover: #059669;
            --primary-subtle: rgba(16, 185, 129, 0.12);
            --secondary: #00ff88;
            --accent: #06b6d4;
            --success: #10b981;
            --success-bg: rgba(16, 185, 129, 0.12);
            --warning: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.12);
            --danger: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.12);
            --border: #1e293b;
            --border-subtle: #131e30;
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.4);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.45);
            --shadow-lg: 0 8px 28px rgba(0, 0, 0, 0.55);
            --chart-main: #10b981;
            --chart-sec: #06b6d4;
            --chart-subtle: #94a3b8;
        """
        leaflet_tile = "cartodbdark_matter"
    else:
        # 🌙 Ocula Oceanic Dark (Deep Abyss Navy - Default)
        theme_vars = """
            --bg-base: #071322;
            --bg-gradient: linear-gradient(180deg, #071322 0%, #0c1b30 100%);
            --bg-surface: #0d2138;
            --bg-surface-hover: #112845;
            --bg-elevated: #132a48;
            --card-bg: #0d2138;
            --card-border: #1e3a5f;
            --card-border-active: #38bdf8;
            --text-primary: #f0f9ff;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --text-inverse: #071322;
            --primary: #38bdf8;
            --primary-hover: #0ea5e9;
            --primary-subtle: rgba(56, 189, 248, 0.12);
            --secondary: #0ea5e9;
            --accent: #7dd3fc;
            --success: #34d399;
            --success-bg: rgba(52, 211, 153, 0.12);
            --warning: #fbbf24;
            --warning-bg: rgba(251, 191, 36, 0.12);
            --danger: #f87171;
            --danger-bg: rgba(248, 113, 113, 0.12);
            --border: #1e3a5f;
            --border-subtle: #152c48;
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.35);
            --shadow-lg: 0 8px 28px rgba(0, 0, 0, 0.45);
            --chart-main: #38bdf8;
            --chart-sec: #0ea5e9;
            --chart-subtle: #94a3b8;
        """
        leaflet_tile = "cartodbdark_matter"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;500;600;700&display=swap');

    :root {{
        {theme_vars}
    }}

    /* Global App Container */
    .stApp {{
        background: var(--bg-gradient) !important;
        color: var(--text-primary) !important;
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
    }}

    /* Streamlit Global Text Overrides for 100% Theme Contrast */
    h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: inherit;
    }}
    .stMarkdown, .stText {{
        color: var(--text-primary) !important;
    }}

    /* Streamlit Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: var(--bg-surface) !important;
        border-right: 1px solid var(--border) !important;
    }}
    [data-testid="stSidebar"] * {{
        color: var(--text-primary) !important;
    }}
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    /* Header Shell */
    .ff-header-shell {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 12px 20px;
        margin-bottom: 16px;
        box-shadow: var(--shadow-sm);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    /* Modern Card Container */
    .ff-card {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: var(--shadow-sm);
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}
    .ff-card:hover {{
        border-color: var(--card-border-active);
        box-shadow: var(--shadow-md);
    }}

    /* Operational Clearance Hero Card */
    .ff-clearance-hero {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: var(--shadow-sm);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }}
    .ff-clearance-safe {{
        border-left: 6px solid var(--success);
        background: var(--success-bg);
    }}
    .ff-clearance-caution {{
        border-left: 6px solid var(--warning);
        background: var(--warning-bg);
    }}
    .ff-clearance-danger {{
        border-left: 6px solid var(--danger);
        background: var(--danger-bg);
    }}

    /* Compact Telemetry Chips */
    .ff-telemetry-chip {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 14px;
        text-align: center;
        box-shadow: var(--shadow-sm);
        transition: transform 0.15s ease;
    }}
    .ff-telemetry-chip:hover {{
        border-color: var(--primary);
    }}
    .ff-telemetry-lbl {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-muted);
        margin-bottom: 4px;
    }}
    .ff-telemetry-val {{
        font-size: 22px;
        font-weight: 800;
        color: var(--primary);
        font-family: 'JetBrains Mono', monospace;
    }}

    /* Navigation Tabs & Segmented Controls */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        border-bottom: 2px solid var(--border);
        padding-bottom: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        font-weight: 600;
        color: var(--text-muted);
        font-size: 13px;
        border: 1px solid transparent;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--primary-subtle) !important;
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
    }}

    /* Streamlit Form Controls & Inputs */
    .stSelectbox label, .stTextInput label, .stRadio label {{
        color: var(--text-secondary) !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: var(--bg-surface) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }}
    div[data-baseweb="input"] > div {{
        background-color: var(--bg-surface) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }}
    input, textarea {{
        color: var(--text-primary) !important;
    }}

    /* Button Enhancements */
    button[kind="primary"] {{
        background-color: var(--primary) !important;
        color: var(--text-inverse) !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        box-shadow: var(--shadow-sm) !important;
    }}
    button[kind="secondary"] {{
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }}
    button[kind="secondary"]:hover {{
        border-color: var(--primary) !important;
        color: var(--primary) !important;
    }}

    /* SOS Distress Header Button */
    .ff-sos-btn {{
        background: #dc2626 !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        box-shadow: 0 0 14px rgba(220, 38, 38, 0.4) !important;
        animation: pulseSOS 2s infinite;
    }}
    @keyframes pulseSOS {{
        0% {{ box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.6); }}
        70% {{ box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }}
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

    /* Modals & Drawers Overlay */
    .ff-modal-box {{
        background: var(--bg-surface);
        border: 2px solid var(--border);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: var(--shadow-lg);
    }}

    /* High / Low Tide Box */
    .ff-tide-tile {{
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 14px;
        text-align: center;
    }}

    /* Clean Table and Dataframe overrides */
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
    Renders the interactive Leaflet geospatial map containing all navigational,
    oceanographic, PFZ, bathymetric, and animated streamline layers.
    """
    base_tiles = "cartodbpositron" if "Day" in theme_name else "cartodbdark_matter"

    m = folium.Map(
        location=[port.lat, port.lon],
        zoom_start=9,
        tiles=base_tiles,
        name="Base Chart",
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
    route_color = "#0284c7" if "Day" in theme_name else ("#10b981" if "Tactical" in theme_name else "#38bdf8")
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
# APPLICATION STATE MANAGEMENT
# ---------------------------------------------------------

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = MultiAgentOrchestrator()

# Primary Navigation State (EXACTLY 5 TABS)
if "nav_section" not in st.session_state:
    st.session_state.nav_section = "🏠 Dashboard"

# Sub-navigation states
if "sub_explore" not in st.session_state:
    st.session_state.sub_explore = "🗺️ Tactical Map"

if "sub_conditions" not in st.session_state:
    st.session_state.sub_conditions = "⏱️ Current & Forecast"

if "sub_safety" not in st.session_state:
    st.session_state.sub_safety = "🟢 Operational Status"

if "sub_settings" not in st.session_state:
    st.session_state.sub_settings = "⛵ Vessel & Voyage"

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

if "show_manifest_modal" not in st.session_state:
    st.session_state.show_manifest_modal = False

if "vessel_class" not in st.session_state:
    st.session_state.vessel_class = "Mechanized Trawler (12-18m)"

if "departure_window" not in st.session_state:
    st.session_state.departure_window = "Immediate (Current Tide)"

if "unit_system" not in st.session_state:
    st.session_state.unit_system = "Metric (km/h, km)"


# ---------------------------------------------------------
# EXECUTE DATA PIPELINE
# ---------------------------------------------------------

# Pipeline execution check
if (
    st.session_state.last_pipeline_result is None or
    st.session_state.last_pipeline_result.port.id != st.session_state.active_port_id or
    st.session_state.last_pipeline_result.query_intent.vessel_class != st.session_state.vessel_class
):
    with st.spinner("Fetching live telemetry, bio-optics & INCOIS safety constraints..."):
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
# GLOBAL APP SHELL: TOP HEADER BAR
# ---------------------------------------------------------

head_col1, head_col2, head_col3, head_col4, head_col5, head_col6 = st.columns([3.2, 2.6, 1.6, 1.4, 1.4, 1.8])

with head_col1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:28px;">⚓</span>
        <div>
            <div style="font-size:18px; font-weight:800; color:var(--primary); line-height:1.1;">FishingFriend</div>
            <div style="font-size:11px; color:var(--text-muted);">ORCA Marine AI · ISRO SIH26176</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with head_col2:
    # Grouped harbor selector (West Coast vs East Coast)
    port_list = list(INDIAN_PORTS.keys())
    port_names = []
    for k in port_list:
        p = INDIAN_PORTS[k]
        coast_tag = "West" if "West" in p.coast else "East"
        port_names.append(f"📍 {p.name} ({coast_tag} Coast)")
    
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
        st.session_state.last_pipeline_result = None
        st.rerun()

with head_col3:
    theme_options = ["☀️ Sky Day", "🌙 Oceanic Dark", "⚡ Tactical Radar"]
    cur_t_idx = 1
    if "Day" in st.session_state.selected_theme:
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
    # Map back to full name
    theme_map = {
        "☀️ Sky Day": "☀️ Ocula Sky Day",
        "🌙 Oceanic Dark": "🌙 Ocula Oceanic Dark",
        "⚡ Tactical Radar": "⚡ Tactical Radar"
    }
    if theme_map[chosen_t] != st.session_state.selected_theme:
        st.session_state.selected_theme = theme_map[chosen_t]
        st.rerun()

with head_col4:
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

with head_col5:
    if st.button("💡 Guide & SOP", use_container_width=True, key="hdr_guide_btn"):
        st.session_state.show_guide_modal = not st.session_state.show_guide_modal
        st.session_state.show_sos_modal = False
        st.rerun()

with head_col6:
    if st.button("🚨 EMERGENCY SOS", type="primary", use_container_width=True, key="hdr_sos_btn"):
        st.session_state.show_sos_modal = not st.session_state.show_sos_modal
        st.session_state.show_guide_modal = False
        st.rerun()


# ---------------------------------------------------------
# GLOBAL MODALS (GUIDE & SOP / EMERGENCY SOS)
# ---------------------------------------------------------

if st.session_state.show_guide_modal:
    st.markdown("""
    <div class="ff-modal-box" style="border-left: 6px solid var(--primary); margin-top: 8px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:17px; font-weight:800; color:var(--primary);">
                💡 SKIPPER'S FIELD GUIDE & MARITIME ADVISORY STANDARD OPERATING PROCEDURE (SOP)
            </div>
            <div style="font-size:11px; font-weight:700; color:var(--primary); background:var(--primary-subtle); padding:4px 8px; border-radius:6px;">
                INCOIS / IMD / ICG CODIFIED RULES
            </div>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin-top: 12px;">
            <div style="background: rgba(34, 197, 94, 0.08); border-left: 4px solid #22c55e; padding: 10px 12px; border-radius: 6px;">
                <b style="color:#16a34a;">🟢 SAFE OPERATIONAL CLEARANCE (GO)</b>
                <p style="font-size:12px; margin:4px 0 0 0; line-height:1.4;">
                    • Swell &lt; 1.80m & Wind &lt; 32 km/h.<br>
                    • Safe distance from International Maritime Boundaries (&gt;10 nm).<br>
                    • All registered craft permitted for unrestricted offshore voyage.
                </p>
            </div>
            <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid #f59e0b; padding: 10px 12px; border-radius: 6px;">
                <b style="color:#d97706;">🟡 CONDITIONAL CLEARANCE (CAUTION)</b>
                <p style="font-size:12px; margin:4px 0 0 0; line-height:1.4;">
                    • Swell 1.80m - 2.50m or Wind 32 - 45 km/h.<br>
                    • Traditional craft (&lt;10m) restricted within 12 nm.<br>
                    • Mechanized trawlers maintain continuous VHF Ch 16 watch.
                </p>
            </div>
            <div style="background: rgba(239, 68, 68, 0.08); border-left: 4px solid #ef4444; padding: 10px 12px; border-radius: 6px;">
                <b style="color:#dc2626;">🔴 OPERATIONAL SUSPENSION (NO-GO)</b>
                <p style="font-size:12px; margin:4px 0 0 0; line-height:1.4;">
                    • Swell &gt; 2.50m (INCOIS High Wave Red Alert).<br>
                    • Wind &gt; 45.0 km/h (IMD Squall / Gale Warning).<br>
                    • Proximity to IMBL &lt; 10.0 nm (Apprehension Danger). All vessels remain moored.
                </p>
            </div>
        </div>
        <div style="font-size:12px; margin-top:10px; line-height:1.5; color:var(--text-secondary);">
            🐟 <b>Potential Fishing Zones (PFZs):</b> Calculated using ISRO Oceansat-3 chlorophyll-a and SST thermal boundaries. Convergence lines congregate pelagic fish, cutting searching fuel by 20-30%.<br>
            🚨 <b>Emergency Protocols:</b> Indian Coast Guard Toll-Free: <b>1554</b> | Coastal Security Police: <b>1093</b> | VHF Distress Channel: <b>16</b> | DSC Alert: <b>Channel 70</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✕ Close Guide", key="btn_close_guide"):
        st.session_state.show_guide_modal = False
        st.rerun()

if st.session_state.show_sos_modal:
    st.markdown(f"""
    <div class="ff-modal-box" style="border: 2px solid #ef4444; background: rgba(239, 68, 68, 0.06); margin-top: 8px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:18px; font-weight:800; color:#ef4444;">
                🚨 DISTRESS EMERGENCY BEACON GENERATOR (MAYDAY PROTOCOL)
            </div>
            <div style="font-size:11px; font-weight:700; color:#ef4444; background:rgba(239, 68, 68, 0.15); padding:4px 8px; border-radius:6px;">
                VHF CH 16 / DSC CHANNEL 70
            </div>
        </div>
        <p style="font-size:13px; margin:6px 0 10px 0; color:var(--text-primary);">
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
            f"NEAREST BASE: {res.port.name}, {res.port.state} (Coast: {res.port.coast})\n"
            f"NEAREST INT'L BOUNDARY: {res.safety.nearest_imbl_name} ({res.safety.border_distance_km} km away)\n"
            f"CURRENT WAVE / SWELL: {res.telemetry.wave_height}m (Swell {res.telemetry.swell_wave_height}m)\n"
            f"EMERGENCY FREQUENCY: VHF Ch 16 (156.800 MHz) | Distress Relay: 1554"
        )
        st.code(distress_payload, language="text")

    with sos_col2:
        st.markdown(f"""
        <div style="font-size:13px; line-height:1.7; color:var(--text-primary);">
            <b>📞 Immediate Direct Dials:</b><br>
            • <b>Coast Guard MRCC:</b> <a href="tel:1554" style="color:var(--primary); font-weight:bold;">1554</a><br>
            • <b>Coastal Marine Police:</b> <a href="tel:1093" style="color:var(--primary); font-weight:bold;">1093</a><br>
            • <b>Disaster Management:</b> 1070 / 1077<br>
            • <b>Sea Ambulance:</b> 108
        </div>
        """, unsafe_allow_html=True)
        if st.button("📡 Broadcast Distress Alert (Simulated)", type="primary", use_container_width=True, key="btn_send_sos"):
            st.success("✅ Simulated Mayday Packet transmitted to nearest Coast Guard MRCC Station and Marine Police.")
        if st.button("✕ Close SOS Modal", use_container_width=True, key="btn_close_sos"):
            st.session_state.show_sos_modal = False
            st.rerun()


# ---------------------------------------------------------
# PROFESSIONAL SIDEBAR: EXACTLY FIVE PRIMARY NAVIGATION TABS
# ---------------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div style="padding: 6px 0 14px 0; border-bottom: 1px solid var(--border); margin-bottom: 12px;">
        <div style="font-size: 11px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px;">
            OPERATIONAL NAVIGATION
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5 Primary Navigation Tabs ONLY
    primary_tabs = [
        "🏠 Dashboard",
        "🗺 Explore",
        "🌦 Conditions",
        "🛟 Safety & Advisory",
        "⚙ Settings"
    ]
    
    cur_nav_idx = primary_tabs.index(st.session_state.nav_section) if st.session_state.nav_section in primary_tabs else 0
    selected_nav = st.radio(
        "Primary View",
        options=primary_tabs,
        index=cur_nav_idx,
        label_visibility="collapsed",
        key="primary_nav_radio"
    )
    if selected_nav != st.session_state.nav_section:
        st.session_state.nav_section = selected_nav
        st.rerun()

    st.markdown("<div style='margin-top: 18px; border-top: 1px solid var(--border); padding-top: 14px;'></div>", unsafe_allow_html=True)

    # Natural Language / Voice Query bar in Sidebar
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;'>🤖 ORCA Natural Query</div>", unsafe_allow_html=True)
    side_q = st.text_input(
        "Query",
        value=st.session_state.query_text,
        placeholder="Type query or tap voice preset...",
        label_visibility="collapsed",
        key="side_query_input"
    )
    if st.button("🔍 Run Sea Analysis", use_container_width=True, key="btn_side_analyze"):
        if side_q != st.session_state.query_text:
            st.session_state.query_text = side_q
            st.session_state.last_pipeline_result = None
            st.rerun()

    # Quick Voice Preset Pills in Sidebar
    st.markdown("<div style='font-size: 10px; font-weight: 600; color: var(--text-muted); margin-top: 6px;'>🎙️ Multi-lingual Voice Presets:</div>", unsafe_allow_html=True)
    vp1, vp2 = st.columns(2)
    with vp1:
        if st.button("EN: Kochi Tuna", use_container_width=True, key="vp_en_kochi"):
            st.session_state.query_text = "Can we sail from Kochi harbor for Yellowfin Tuna?"
            st.session_state.active_port_id = "kochi"
            st.session_state.advisory_lang = "English"
            st.session_state.last_pipeline_result = None
            st.rerun()
        if st.button("TA: கொச்சி சூரை", use_container_width=True, key="vp_ta_kochi"):
            st.session_state.query_text = "கொச்சியிலிருந்து இன்று சூரை மீன் பிடிக்க கடலுக்குச் செல்லலாமா?"
            st.session_state.active_port_id = "kochi"
            st.session_state.advisory_lang = "தமிழ்"
            st.session_state.last_pipeline_result = None
            st.rerun()
    with vp2:
        if st.button("HI: वेरावल मछली", use_container_width=True, key="vp_hi_veraval"):
            st.session_state.query_text = "क्या कल सुबह वेरावल से समुद्र में जाना सुरक्षित है?"
            st.session_state.active_port_id = "veraval"
            st.session_state.advisory_lang = "हिन्दी"
            st.session_state.last_pipeline_result = None
            st.rerun()
        if st.button("EN: Pomfret Vizag", use_container_width=True, key="vp_en_vizag"):
            st.session_state.query_text = "Visakhapatnam harbor to deep Bay of Bengal for Pomfret"
            st.session_state.active_port_id = "visakhapatnam"
            st.session_state.advisory_lang = "English"
            st.session_state.last_pipeline_result = None
            st.rerun()

    st.markdown("""
    <div style="margin-top: 24px; padding: 10px; background: var(--bg-base); border-radius: 8px; border: 1px solid var(--border); font-size: 11px; line-height: 1.4;">
        <div style="font-weight: 700; color: var(--primary);">🟢 SYSTEM STATUS: LIVE</div>
        <div style="color: var(--text-muted); margin-top: 2px;">
            Open-Meteo & INCOIS Rules Sync<br>
            ISRO Oceansat-3 Bio-Optics Ready
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SECTION 1: 🏠 DASHBOARD (OPERATIONAL OVERVIEW)
# =========================================================

if st.session_state.nav_section == "🏠 Dashboard":
    # Header Area
    dash_h1, dash_h2 = st.columns([8, 4])
    with dash_h1:
        st.markdown(f"""
        <div style="display:flex; align-items:baseline; gap:12px; margin-bottom: 4px;">
            <h2 style="margin:0; font-size:24px; font-weight:800; color:var(--text-primary);">Fishing Operations Dashboard</h2>
            <span style="font-size:14px; font-weight:600; color:var(--primary); background:var(--primary-subtle); padding:3px 10px; border-radius:6px;">
                📍 {res.port.name} ({res.port.coast})
            </span>
        </div>
        <div style="font-size:12px; color:var(--text-muted); margin-bottom:12px;">
            Real-time Marine Intelligence · {datetime.now().strftime('%d-%b-%Y %H:%M IST')} · Telemetry Source: {'Live Open-Meteo' if res.telemetry.is_live else 'Synthetic Marine Model'}
        </div>
        """, unsafe_allow_html=True)

    with dash_h2:
        # Quick summary badge
        st.markdown(f"""
        <div style="text-align:right; font-size:12px; color:var(--text-muted);">
            Active Vessel: <b>{st.session_state.vessel_class.split('(')[0]}</b><br>
            Departure Window: <b>{st.session_state.departure_window.split('(')[0]}</b>
        </div>
        """, unsafe_allow_html=True)

    # 1. Primary Status: Operational Clearance Hero Card
    if res.safety.status == "SAFE_GO":
        clearance_cls = "ff-clearance-safe"
        clearance_icon = "🟢"
        clearance_title = "SAFE OPERATIONAL CLEARANCE: GO"
        clearance_color = "#16a34a"
        clearance_desc = f"Normal sea state off {res.port.name}. Swell ({res.telemetry.swell_wave_height}m) within safe limits (<2.5m). Unrestricted offshore voyage cleared."
    elif res.safety.status == "CAUTION_CONDITIONAL":
        clearance_cls = "ff-clearance-caution"
        clearance_icon = "🟡"
        clearance_title = "CONDITIONAL CLEARANCE: CAUTION"
        clearance_color = "#d97706"
        clearance_desc = f"Moderate swell ({res.telemetry.swell_wave_height}m) or wind gusts off {res.port.name}. Traditional small craft (<10m) restricted within 12 nm."
    else:
        clearance_cls = "ff-clearance-danger"
        clearance_icon = "🔴"
        clearance_title = "OPERATIONAL SUSPENSION: NO-GO"
        clearance_color = "#dc2626"
        clearance_desc = f"INCOIS/IMD threshold breached off {res.port.name}: Swell > 2.5m or wind > 45 km/h. All fishing operations ordered to remain moored."

    st.markdown(f"""
    <div class="ff-clearance-hero {clearance_cls}">
        <div>
            <div style="font-size:20px; font-weight:800; color:{clearance_color};">
                {clearance_icon} {clearance_title}
            </div>
            <div style="font-size:13px; color:var(--text-secondary); margin-top:3px; max-width:700px; line-height:1.4;">
                {clearance_desc}
            </div>
        </div>
        <div style="text-align:right; min-width:110px;">
            <div style="font-size:26px; font-weight:800; color:{clearance_color}; font-family:'JetBrains Mono';">
                {res.safety.risk_score} <span style="font-size:14px; font-weight:600; color:var(--text-muted);">/ 100</span>
            </div>
            <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Risk Index</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Compact Marine Conditions Metrics (5 items)
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="ff-telemetry-chip">
            <div class="ff-telemetry-lbl">🌊 Swell Height</div>
            <div class="ff-telemetry-val">{res.telemetry.swell_wave_height} <span style="font-size:13px;">m</span></div>
            <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">Period {res.telemetry.swell_wave_period}s</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="ff-telemetry-chip">
            <div class="ff-telemetry-lbl">🌡️ Sea Temp (SST)</div>
            <div class="ff-telemetry-val">{res.telemetry.sea_surface_temperature}°<span style="font-size:13px;">C</span></div>
            <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">Thermal Edge</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="ff-telemetry-chip">
            <div class="ff-telemetry-lbl">🌀 Ocean Current</div>
            <div class="ff-telemetry-val">{curr_disp} <span style="font-size:13px;">{curr_unit}</span></div>
            <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">Drift {res.telemetry.ocean_current_direction:.0f}°</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="ff-telemetry-chip">
            <div class="ff-telemetry-lbl">💨 Wind Speed</div>
            <div class="ff-telemetry-val">{wind_disp} <span style="font-size:13px;">{wind_unit}</span></div>
            <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">{gust_disp}</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.markdown(f"""
        <div class="ff-telemetry-chip">
            <div class="ff-telemetry-lbl">🌿 Chlorophyll-A</div>
            <div class="ff-telemetry-val">{res.telemetry.chlorophyll_proxy} <span style="font-size:11px;">mg/m³</span></div>
            <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">Oceansat-3 Proxy</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # 3. Two-Column Operational Split: Recommended Fishing Zones & ORCA AI Insight
    col_pfz, col_ai = st.columns([7, 5])

    with col_pfz:
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div style="font-size:15px; font-weight:800; color:var(--text-primary);">
                🎣 Top Recommended Fishing Zones (PFZ)
            </div>
            <span style="font-size:11px; color:var(--text-muted);">ISRO Bio-Optical Fronts</span>
        </div>
        """, unsafe_allow_html=True)

        for pfz in res.all_pfzs[:3]:
            is_top = (pfz.zone_id == res.top_pfz.zone_id)
            accent_border = "border-left: 4px solid var(--primary);" if is_top else "border-left: 4px solid var(--border);"
            star_tag = "⭐ " if is_top else ""
            
            st.markdown(f"""
            <div class="ff-card" style="{accent_border} padding: 12px 14px; margin-bottom: 8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:700; font-size:14px; color:var(--primary);">
                        {star_tag}{pfz.name}
                    </div>
                    <div style="font-size:13px; font-weight:800; color:#059669; font-family:'JetBrains Mono';">
                        {pfz.fish_density_score}% Catch Score
                    </div>
                </div>
                <div style="font-size:12px; color:var(--text-secondary); margin-top:4px; line-height:1.4;">
                    <b>Range:</b> {pfz.distance_km} km @ {pfz.bearing_deg}° | <b>Depth:</b> {pfz.depth_m}m | <b>SST:</b> {pfz.sst_celsius}°C<br>
                    <b>Target Species:</b> {', '.join(pfz.species_likely[:2])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("View All Fishing Zones & Ocean Analysis →", key="btn_dash_to_pfz", use_container_width=True):
            st.session_state.nav_section = "🗺 Explore"
            st.session_state.sub_explore = "🐟 Fishing Zones"
            st.rerun()

    with col_ai:
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div style="font-size:15px; font-weight:800; color:var(--text-primary);">
                🤖 ORCA AI Operational Insight
            </div>
            <span style="font-size:11px; color:var(--text-muted);">Collaborative Reasoning</span>
        </div>
        """, unsafe_allow_html=True)

        # Extract localized advisory data
        if "Hindi" in st.session_state.advisory_lang or "हिन्दी" in st.session_state.advisory_lang:
            adv_dash = res.advisory.hindi
        elif "Tamil" in st.session_state.advisory_lang or "தமிழ்" in st.session_state.advisory_lang:
            adv_dash = res.advisory.tamil
        else:
            adv_dash = res.advisory.english

        st.markdown(f"""
        <div class="ff-card" style="padding: 14px 16px;">
            <div style="font-weight:700; font-size:14px; color:var(--primary); margin-bottom:6px;">
                {adv_dash['status_headline']}
            </div>
            <div style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin-bottom:10px;">
                {adv_dash['executive_summary']}
            </div>
            <div style="background:var(--primary-subtle); border-left:3px solid var(--primary); padding:8px 10px; border-radius:6px; font-size:12px; color:var(--text-primary); margin-bottom:8px;">
                <b>Directive:</b> {adv_dash['safety_action']}
            </div>
            <div style="font-size:11px; color:var(--text-muted); line-height:1.4;">
                ⛽ <b>Transit Plan:</b> {adv_dash['fuel_and_route']['estimated_transit']} · Diesel {adv_dash['fuel_and_route']['fuel_consumption']} (Savings: <span style="color:#059669; font-weight:bold;">{adv_dash['fuel_and_route']['fuel_savings']}</span>).
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View Full Multilingual Advisory & Audio →", key="btn_dash_to_adv", use_container_width=True):
            st.session_state.nav_section = "🛟 Safety & Advisory"
            st.session_state.sub_safety = "📢 Actionable Advisory"
            st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # 4. Compact Operational Map Preview
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <div style="font-size:15px; font-weight:800; color:var(--text-primary);">
            🗺️ Tactical Operational Map Preview
        </div>
        <span style="font-size:11px; color:var(--text-muted);">OpenSeaMap & Animated Current Vectors</span>
    </div>
    """, unsafe_allow_html=True)

    map_prev_col, quick_act_col = st.columns([8, 4])
    with map_prev_col:
        render_tactical_map(
            port=res.port,
            telemetry=res.telemetry,
            safety=res.safety,
            all_pfzs=res.all_pfzs[:3],
            selected_pfz=res.top_pfz,
            route=res.route,
            theme_name=st.session_state.selected_theme,
            height=340
        )

    with quick_act_col:
        st.markdown("""
        <div class="ff-card" style="height:100%; display:flex; flex-direction:column; justify-content:space-between;">
            <div>
                <div style="font-size:13px; font-weight:700; color:var(--primary); margin-bottom:8px;">⚡ Quick Actions</div>
                <div style="font-size:12px; color:var(--text-secondary); line-height:1.5;">
                    Direct shortcuts to detailed maritime intelligence workspaces:
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗺️ Open Full Tactical Map", key="btn_qa_map", use_container_width=True):
            st.session_state.nav_section = "🗺 Explore"
            st.session_state.sub_explore = "🗺️ Tactical Map"
            st.rerun()

        if st.button("⏱️ 48h Swell & Wave Forecast", key="btn_qa_forecast", use_container_width=True):
            st.session_state.nav_section = "🌦 Conditions"
            st.session_state.sub_conditions = "⏱️ Current & Forecast"
            st.rerun()

        if st.button("🌊 Astronomical Tides & Bar Depth", key="btn_qa_tides", use_container_width=True):
            st.session_state.nav_section = "🌦 Conditions"
            st.session_state.sub_conditions = "🌊 Tides"
            st.rerun()

        if st.button("📡 Live Doppler Rain Radar", key="btn_qa_radar", use_container_width=True):
            st.session_state.nav_section = "🌦 Conditions"
            st.session_state.sub_conditions = "📡 Radar & Satellite"
            st.rerun()


# =========================================================
# SECTION 2: 🗺 EXPLORE (TACTICAL MAP / ZONES / SEA ANALYSIS)
# =========================================================

elif st.session_state.nav_section == "🗺 Explore":
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <h2 style="margin:0; font-size:22px; font-weight:800; color:var(--text-primary);">🗺️ Marine Exploration & Spatial Intelligence</h2>
        <span style="font-size:13px; font-weight:600; color:var(--primary);">📍 {res.port.name}</span>
    </div>
    """, unsafe_allow_html=True)

    # Secondary Segmented Control for Explore
    explore_tabs = ["🗺️ Tactical Map", "🐟 Fishing Zones", "🌊 Sea Analysis"]
    cur_exp_idx = explore_tabs.index(st.session_state.sub_explore) if st.session_state.sub_explore in explore_tabs else 0
    sub_exp = st.segmented_control("Explore View", options=explore_tabs, default=explore_tabs[cur_exp_idx], label_visibility="collapsed")
    if sub_exp and sub_exp != st.session_state.sub_explore:
        st.session_state.sub_explore = sub_exp
        st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 2.1: TACTICAL MAP
    # -----------------------------------------------------
    if st.session_state.sub_explore == "🗺️ Tactical Map":
        st.caption("Layer control (top-right of map): Toggle Nautical Marks, ESRI Bathymetry, Marine Protected Areas, PFZ Hotspots, and Animated Windy Current Streamlines.")
        
        # Expanded full-width Tactical Map
        render_tactical_map(
            port=res.port,
            telemetry=res.telemetry,
            safety=res.safety,
            all_pfzs=res.all_pfzs,
            selected_pfz=res.top_pfz,
            route=res.route,
            theme_name=st.session_state.selected_theme,
            height=580
        )

        # Map Footer Information Strip
        st.markdown(f"""
        <div class="ff-card" style="margin-top:12px; padding:12px 18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div style="font-size:12px; color:var(--text-secondary);">
                🎯 <b>Target PFZ:</b> {res.top_pfz.name} ({dist_label_top} · Bearing {res.top_pfz.bearing_deg}°) | 
                ⛽ <b>Fuel Transit:</b> ~{res.route.fuel_burn_liters} L (Saved: <span style="color:#059669; font-weight:bold;">{res.route.fuel_savings_liters} L</span>) |
                🛑 <b>Nearest IMBL:</b> {res.safety.border_distance_km} km ({res.safety.nearest_imbl_name})
            </div>
            <div>
                <span style="font-size:11px; background:var(--primary-subtle); color:var(--primary); padding:4px 8px; border-radius:4px; font-weight:700;">
                    CartoDB & OpenSeaMap Layers Active
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 2.2: FISHING ZONES
    # -----------------------------------------------------
    elif st.session_state.sub_explore == "🐟 Fishing Zones":
        st.markdown("##### 🐟 All Discovered Potential Fishing Zones (ISRO Oceansat-3 Frontiers)")
        st.caption("Thermal front gradients and chlorophyll upwelling zones prioritized for pelagic fish aggregations.")

        for idx, pfz in enumerate(res.all_pfzs):
            is_top = (pfz.zone_id == res.top_pfz.zone_id)
            badge_border = "border: 2px solid var(--primary);" if is_top else "border: 1px solid var(--card-border);"
            bg_accent = "background: var(--primary-subtle);" if is_top else ""
            
            with st.container():
                st.markdown(f"""
                <div class="ff-card" style="{badge_border} {bg_accent} padding: 16px; margin-bottom: 12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:16px; font-weight:800; color:var(--primary);">
                                {'⭐ ' if is_top else ''}{pfz.name}
                            </span>
                            <span style="font-size:11px; margin-left:8px; background:rgba(0,0,0,0.06); padding:2px 8px; border-radius:4px; font-weight:600;">
                                {pfz.confidence_level}
                            </span>
                        </div>
                        <div style="font-size:16px; font-weight:800; color:#059669; font-family:'JetBrains Mono';">
                            {pfz.fish_density_score}% Catch Score
                        </div>
                    </div>
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top:10px; font-size:12px; color:var(--text-secondary);">
                        <div><b>Range & Heading:</b> {pfz.distance_km} km @ {pfz.bearing_deg}°</div>
                        <div><b>Bathymetry Depth:</b> {pfz.depth_m} meters</div>
                        <div><b>SST / Chl-a:</b> {pfz.sst_celsius}°C / {pfz.chlorophyll_proxy} mg/m³</div>
                        <div><b>Thermal Edge:</b> {pfz.thermal_gradient_desc}</div>
                    </div>
                    <div style="margin-top:8px; font-size:12px; color:var(--text-primary);">
                        <b>Primary Pelagic Species:</b> <span style="color:var(--primary); font-weight:600;">{', '.join(pfz.species_likely)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="ff-card" style="padding:14px; font-size:12px; color:var(--text-secondary);">
            ⛽ <b>Navigation & Fuel Optimization:</b> Routing to top PFZ ({res.top_pfz.name}) spans {dist_label_top} (~{res.route.estimated_transit_hours:.1f} hrs transit).
            Assisted by ocean current vector, saving approximately <b style="color:#059669;">{res.route.fuel_savings_liters} Liters</b> of diesel compared to linear blind cruising.
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 2.3: SEA ANALYSIS
    # -----------------------------------------------------
    elif st.session_state.sub_explore == "🌊 Sea Analysis":
        st.markdown("##### 🌊 Oceanographic Environmental Intelligence & Spatial Sanctuaries")
        
        sa_col1, sa_col2 = st.columns([6, 6])
        with sa_col1:
            st.markdown(f"""
            <div class="ff-card">
                <div style="font-size:14px; font-weight:700; color:var(--primary); margin-bottom:8px;">
                    🌊 Physical Oceanography Parameters
                </div>
                <div style="font-size:13px; line-height:1.7; color:var(--text-secondary);">
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
                <div style="font-size:14px; font-weight:700; color:var(--primary); margin-bottom:8px;">
                    🛡️ Marine Spatial Planning (MarineMap MSP)
                </div>
                <div style="font-size:13px; line-height:1.6; color:var(--text-secondary);">
                    Sensitive coral reefs, marine parks, and statutory fishing reserves surrounding <b>{res.port.name}</b>:
                </div>
            </div>
            """, unsafe_allow_html=True)

            mpas_local = get_marine_spatial_zones(res.port.id)
            if mpas_local:
                for m in mpas_local:
                    st.markdown(f"""
                    <div style="font-size:12px; padding:10px 14px; background:rgba(234, 88, 12, 0.08); border-left:4px solid #ea580c; border-radius:6px; margin-bottom:8px;">
                        <b style="color:#ea580c;">🛡️ {m.name} ({m.category})</b><br>
                        <span style="color:var(--text-secondary);">{m.restriction}</span><br>
                        <span style="font-size:10px; color:var(--text-muted);">Legal Basis: {m.legal_source}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No restricted marine sanctuaries immediately adjacent to this harbor fairway.")


# =========================================================
# SECTION 3: 🌦 CONDITIONS (FORECAST / TIDES / RADAR)
# =========================================================

elif st.session_state.nav_section == "🌦 Conditions":
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <h2 style="margin:0; font-size:22px; font-weight:800; color:var(--text-primary);">🌦️ Marine Weather, Tides & Live Radar</h2>
        <span style="font-size:13px; font-weight:600; color:var(--primary);">📍 {res.port.name}</span>
    </div>
    """, unsafe_allow_html=True)

    # Secondary Segmented Control for Conditions
    cond_tabs = ["⏱️ Current & Forecast", "🌊 Tides", "📡 Radar & Satellite"]
    cur_c_idx = cond_tabs.index(st.session_state.sub_conditions) if st.session_state.sub_conditions in cond_tabs else 0
    sub_cond = st.segmented_control("Conditions View", options=cond_tabs, default=cond_tabs[cur_c_idx], label_visibility="collapsed")
    if sub_cond and sub_cond != st.session_state.sub_conditions:
        st.session_state.sub_conditions = sub_cond
        st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 3.1: CURRENT & FORECAST
    # -----------------------------------------------------
    if st.session_state.sub_conditions == "⏱️ Current & Forecast":
        # Overview Cards Row
        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center; padding:12px;">
                <div style="font-size:11px; font-weight:700; color:var(--primary);">48H PEAK SWELL HEIGHT</div>
                <div style="font-size:24px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono'; margin:4px 0;">
                    {port_hourly.max_wave_height:.2f} <span style="font-size:14px;">m</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">INCOIS Status: <b>{port_hourly.incois_wave_risk}</b></div>
            </div>
            """, unsafe_allow_html=True)

        with hc2:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center; padding:12px;">
                <div style="font-size:11px; font-weight:700; color:#d97706;">48H MAX WIND GUST</div>
                <div style="font-size:24px; font-weight:800; color:#d97706; font-family:'JetBrains Mono'; margin:4px 0;">
                    {port_hourly.max_wind_gust:.1f} <span style="font-size:14px;">km/h</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">IMD Status: <b>{port_hourly.imd_wind_risk}</b></div>
            </div>
            """, unsafe_allow_html=True)

        with hc3:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center; padding:12px;">
                <div style="font-size:11px; font-weight:700; color:#059669;">TELEMETRY DATA SOURCE</div>
                <div style="font-size:20px; font-weight:800; color:#059669; margin:6px 0;">
                    {'Live Open-Meteo' if port_hourly.is_live else 'Synthetic Marine Physics'}
                </div>
                <div style="font-size:11px; color:var(--text-muted);">Forecast Horizon: 48 Hours Ahead</div>
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

        chart_color = "#0284c7" if "Day" in st.session_state.selected_theme else ("#10b981" if "Tactical" in st.session_state.selected_theme else "#38bdf8")

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
            color="#38bdf8" if "Day" in st.session_state.selected_theme else "#94a3b8",
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

        # Horizontal Hourly Observation Cards
        st.markdown("###### ⏱️ Upcoming Hourly Marine Windows")
        step_cols = st.columns(6)
        for idx, (c, h_entry) in enumerate(zip(step_cols, port_hourly.hours[::3][:6])):
            with c:
                is_danger_wave = h_entry.swell_wave_height_m >= 2.5
                is_caution_wave = h_entry.swell_wave_height_m >= 1.8 and not is_danger_wave
                badge_color = "#ef4444" if is_danger_wave else ("#f59e0b" if is_caution_wave else "#059669")
                badge_text = "DANGER" if is_danger_wave else ("CAUTION" if is_caution_wave else "SAFE")
                
                st.markdown(f"""
                <div class="ff-card" style="border-top:3px solid {badge_color}; padding:10px; text-align:center;">
                    <div style="font-size:11px; font-weight:700; color:var(--primary);">{h_entry.hour_label.split(' ')[1]}</div>
                    <div style="font-size:16px; font-weight:800; margin:4px 0; font-family:'JetBrains Mono';">{h_entry.wave_height_m:.1f} m</div>
                    <div style="font-size:10px; color:var(--text-muted);">Swell {h_entry.swell_wave_height_m:.1f}m ({h_entry.swell_wave_period_s}s)</div>
                    <div style="font-size:10px; color:var(--text-muted);">Wind {h_entry.wind_speed_kmh:.0f} km/h</div>
                    <div style="font-size:10px; color:var(--text-muted);">Rain {h_entry.precipitation_probability_pct}%</div>
                    <div style="font-size:10px; font-weight:700; color:{badge_color}; margin-top:4px;">{badge_text}</div>
                </div>
                """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 3.2: TIDES
    # -----------------------------------------------------
    elif st.session_state.sub_conditions == "🌊 Tides":
        st.markdown(f"##### 🌊 Astronomical Tides & Coastal Water Levels for **{port_tides.port_name}**")
        st.caption("Harmonic constituents calibrated against Survey of India & NIO tidal benchmarks.")

        tb1, tb2, tb3, tb4 = st.columns(4)
        with tb1:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center;">
                <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">Water Level</div>
                <div style="font-size:24px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono'; margin:4px 0;">
                    {port_tides.current_water_level_m:.2f} <span style="font-size:14px;">m</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">Above Chart Datum</div>
            </div>
            """, unsafe_allow_html=True)

        with tb2:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center;">
                <div style="font-size:11px; font-weight:700; color:#059669; text-transform:uppercase;">Tidal Phase</div>
                <div style="font-size:18px; font-weight:800; color:#059669; margin:6px 0;">
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
                    {port_tides.tidal_stream_velocity_knots:.1f} <span style="font-size:14px;">kts</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">Spring Range: {port_tides.mean_spring_range_m:.2f}m</div>
            </div>
            """, unsafe_allow_html=True)

        with tb4:
            st.markdown(f"""
            <div class="ff-card" style="text-align:center;">
                <div style="font-size:11px; font-weight:700; color:#d97706; text-transform:uppercase;">Harbor Bar Depth</div>
                <div style="font-size:24px; font-weight:800; color:#d97706; font-family:'JetBrains Mono'; margin:4px 0;">
                    {port_tides.harbor_bar_depth_m:.1f} <span style="font-size:14px;">m</span>
                </div>
                <div style="font-size:11px; color:var(--text-muted);">At Low Water Datum</div>
            </div>
            """, unsafe_allow_html=True)

        if port_tides.harbor_bar_keel_warning:
            st.markdown(f"""
            <div style="background:rgba(217, 119, 6, 0.1); border-left:4px solid #d97706; padding:10px 16px; border-radius:8px; margin: 12px 0; font-size:13px; color:var(--text-primary);">
                ⚠️ <b>HARBOR BAR NOTICE:</b> {port_tides.harbor_bar_keel_warning}
            </div>
            """, unsafe_allow_html=True)

        # High / Low Tide Extremes
        st.markdown("###### 📊 High / Low Tide Extremes (Today & Tomorrow)")
        all_extremes = port_tides.extremes_today + port_tides.extremes_tomorrow[:2]
        ext_cols = st.columns(len(all_extremes))
        
        for c, ext in zip(ext_cols, all_extremes):
            with c:
                ext_type_str = getattr(ext, 'type', getattr(ext, 'extreme_type', 'Tide'))
                is_high = "High" in ext_type_str
                type_icon = "▲" if is_high else "▼"
                type_color = "#0284c7" if is_high else "#059669"
                
                st.markdown(f"""
                <div class="ff-card" style="border-top:3px solid {type_color}; text-align:center; padding:10px;">
                    <div style="font-size:11px; font-weight:700; color:{type_color}; text-transform:uppercase;">
                        {type_icon} {ext_type_str}
                    </div>
                    <div style="font-size:18px; font-weight:800; font-family:'JetBrains Mono'; margin:4px 0;">
                        {ext.time_str}
                    </div>
                    <div style="font-size:14px; font-weight:700; color:{type_color};">
                        {ext.height_m:.2f} m
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Continuous 48-Hour Spline Tide Chart
        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
        st.markdown("###### 📈 48-Hour Continuous Spline Tide Elevation Curve")
        
        tide_plot_data = []
        for p in port_tides.hourly_heights_48h:
            tide_plot_data.append({
                "Time": p.time_str,
                "Tide Height (m)": p.height_m,
                "Is Extreme": p.is_extreme,
                "Label": p.extreme_label if p.extreme_label else ""
            })
        df_tides = pd.DataFrame(tide_plot_data)

        chart_color = "#0284c7" if "Day" in st.session_state.selected_theme else ("#10b981" if "Tactical" in st.session_state.selected_theme else "#38bdf8")

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

    # -----------------------------------------------------
    # SUBVIEW 3.3: RADAR & SATELLITE
    # -----------------------------------------------------
    elif st.session_state.sub_conditions == "📡 Radar & Satellite":
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
                      &nbsp;&nbsp;🟨 <b>35 - 45 dBZ:</b> Heavy monsoon squalls & reduced visibility.<br>
                      &nbsp;&nbsp;🟥 <b>> 45 dBZ:</b> Severe storm cell with gale gusts (&gt;45 km/h).
                </div>
                <div style="background:var(--primary-subtle); border-left:3px solid var(--primary); padding:10px 12px; border-radius:6px; font-size:12px; margin-top:12px; color:var(--text-primary);">
                    💡 <b>Skipper Directive:</b> If red squall echoes develop within 15 nm of fairway, abort deep-sea transit.
                </div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# SECTION 4: 🛟 SAFETY & ADVISORY (STATUS / ADVISORY / EMERGENCY)
# =========================================================

elif st.session_state.nav_section == "🛟 Safety & Advisory":
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <h2 style="margin:0; font-size:22px; font-weight:800; color:var(--text-primary);">🛟 Maritime Safety, Advisories & Emergency Rescue</h2>
        <span style="font-size:13px; font-weight:600; color:var(--primary);">📍 {res.port.name}</span>
    </div>
    """, unsafe_allow_html=True)

    # Secondary Segmented Control for Safety & Advisory
    safety_tabs = ["🟢 Operational Status", "📢 Actionable Advisory", "🚨 Emergency"]
    cur_s_idx = safety_tabs.index(st.session_state.sub_safety) if st.session_state.sub_safety in safety_tabs else 0
    sub_safe = st.segmented_control("Safety View", options=safety_tabs, default=safety_tabs[cur_s_idx], label_visibility="collapsed")
    if sub_safe and sub_safe != st.session_state.sub_safety:
        st.session_state.sub_safety = sub_safe
        st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 4.1: OPERATIONAL STATUS
    # -----------------------------------------------------
    if st.session_state.sub_safety == "🟢 Operational Status":
        # Hero Clearance Banner
        st.markdown(f"""
        <div class="ff-clearance-hero {clearance_cls}">
            <div>
                <div style="font-size:20px; font-weight:800; color:{clearance_color};">
                    {clearance_icon} {clearance_title}
                </div>
                <div style="font-size:13px; color:var(--text-secondary); margin-top:3px; max-width:700px; line-height:1.4;">
                    {clearance_desc}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:26px; font-weight:800; color:{clearance_color}; font-family:'JetBrains Mono';">
                    {res.safety.risk_score} <span style="font-size:14px; font-weight:600; color:var(--text-muted);">/ 100</span>
                </div>
                <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Risk Score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Safety alerts & Rule Audit Log
        st.markdown("##### 🛡️ Deterministic Rule Compliance Matrix (Zero-Hallucination Guardrails)")
        st.caption("All physical safety limits are evaluated deterministically in Python before AI synthesis.")

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

        # Multi-Agent Telemetry Log
        with st.expander("Collaborative Multi-Agent Execution Telemetry"):
            st.write(f"Total Execution Time: **{res.total_execution_time_ms} ms** across 5 collaborative agents.")
            step_cols = st.columns(len(res.agent_logs))
            for col, log in zip(step_cols, res.agent_logs):
                with col:
                    st.markdown(f"""
                    <div class="ff-card" style="padding:10px; text-align:center;">
                        <div style="font-size:11px; font-weight:700; color:var(--primary);">{log.agent_name.split('(')[0]}</div>
                        <div style="font-size:12px; font-weight:700; margin:4px 0;">{log.duration_ms} ms</div>
                        <div style="font-size:10px; color:{'#059669' if log.status=='COMPLETED' else '#ef4444'}; font-weight:600;">{log.status}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 4.2: ACTIONABLE ADVISORY
    # -----------------------------------------------------
    elif st.session_state.sub_safety == "📢 Actionable Advisory":
        st.markdown("##### 🌐 Actionable Multilingual Maritime Guidance")

        # Select language within advisory
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

        audio_html = f"""
        <div style="background:var(--primary-subtle); border:1px solid var(--primary); border-radius:10px; padding:12px 18px; margin-bottom: 14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; font-family:'Plus Jakarta Sans', sans-serif;">
            <div>
                <div style="font-weight:700; font-size:14px; color:var(--primary);">{speech_label}</div>
                <div style="font-size:12px; color:var(--text-muted);">Spoken audio voice advisory for skippers & deckhands with zero reading required.</div>
            </div>
            <div style="display:flex; gap:8px;">
                <button id="tts-play-btn" onclick="playAdvisorySpeech()" style="background:var(--primary); color:#ffffff; border:none; padding:8px 16px; border-radius:6px; font-weight:700; cursor:pointer; font-size:13px;">
                    ▶ Play Voice
                </button>
                <button id="tts-stop-btn" onclick="stopAdvisorySpeech()" style="background:#64748b; color:#ffffff; border:none; padding:8px 14px; border-radius:6px; font-weight:700; cursor:pointer; font-size:13px;">
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
                    • <b>Fuel Saved:</b> <span style="color:#059669; font-weight:bold;">{adv['fuel_and_route']['fuel_savings']}</span><br>
                    • <b>Ocean Current Assist:</b> {adv['fuel_and_route']['current_notes']}<br>
                    • <b>Boundary Safety:</b> {adv['fuel_and_route']['border_safety']}
                </div>
                <div style="margin-top:14px; padding:10px; background:var(--primary-subtle); border-radius:6px; font-size:12px; color:var(--text-primary);">
                    📞 <b>Emergency Assistance:</b> {adv['emergency_contacts']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 4.3: EMERGENCY
    # -----------------------------------------------------
    elif st.session_state.sub_safety == "🚨 Emergency":
        st.markdown(f"##### 🚨 24x7 Emergency Coastal Shore Guards & Helplines for **{res.port.name}**")
        st.caption("Official direct dispatch channels for sea emergencies, search & rescue (SAR), and border alerts.")

        # Top National Toll-Free Helplines Row
        em_h1, em_h2, em_h3, em_h4 = st.columns(4)
        with em_h1:
            st.markdown("""
            <div class="ff-card" style="text-align:center; border-top: 3px solid #0284c7;">
                <div style="font-size:12px; font-weight:700; color:#0284c7;">INDIAN COAST GUARD</div>
                <div style="font-size:24px; font-weight:800; color:#0284c7; margin:4px 0; font-family:'JetBrains Mono';">1554</div>
                <div style="font-size:11px; color:var(--text-muted);">Toll-Free 24x7 Maritime SAR</div>
            </div>
            """, unsafe_allow_html=True)

        with em_h2:
            st.markdown("""
            <div class="ff-card" style="text-align:center; border-top: 3px solid #059669;">
                <div style="font-size:12px; font-weight:700; color:#059669;">COASTAL MARINE POLICE</div>
                <div style="font-size:24px; font-weight:800; color:#059669; margin:4px 0; font-family:'JetBrains Mono';">1093</div>
                <div style="font-size:11px; color:var(--text-muted);">Toll-Free Coastal Security</div>
            </div>
            """, unsafe_allow_html=True)

        with em_h3:
            st.markdown("""
            <div class="ff-card" style="text-align:center; border-top: 3px solid #d97706;">
                <div style="font-size:12px; font-weight:700; color:#d97706;">DISASTER MANAGEMENT</div>
                <div style="font-size:24px; font-weight:800; color:#d97706; margin:4px 0; font-family:'JetBrains Mono';">1070 / 1077</div>
                <div style="font-size:11px; color:var(--text-muted);">State / District SEOC</div>
            </div>
            """, unsafe_allow_html=True)

        with em_h4:
            st.markdown("""
            <div class="ff-card" style="text-align:center; border-top: 3px solid #dc2626;">
                <div style="font-size:12px; font-weight:700; color:#dc2626;">SEA AMBULANCE / MEDICAL</div>
                <div style="font-size:24px; font-weight:800; color:#dc2626; margin:4px 0; font-family:'JetBrains Mono';">108</div>
                <div style="font-size:11px; color:var(--text-muted);">Emergency Medical Evacuation</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
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

elif st.session_state.nav_section == "⚙ Settings":
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <h2 style="margin:0; font-size:22px; font-weight:800; color:var(--text-primary);">⚙️ System Settings & Voyage Configuration</h2>
        <span style="font-size:13px; font-weight:600; color:var(--primary);">📍 {res.port.name}</span>
    </div>
    """, unsafe_allow_html=True)

    # Secondary Segmented Control for Settings
    settings_tabs = ["⛵ Vessel & Voyage", "⚙ Preferences"]
    cur_set_idx = settings_tabs.index(st.session_state.sub_settings) if st.session_state.sub_settings in settings_tabs else 0
    sub_set = st.segmented_control("Settings View", options=settings_tabs, default=settings_tabs[cur_set_idx], label_visibility="collapsed")
    if sub_set and sub_set != st.session_state.sub_settings:
        st.session_state.sub_settings = sub_set
        st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 5.1: VESSEL & VOYAGE
    # -----------------------------------------------------
    if st.session_state.sub_settings == "⛵ Vessel & Voyage":
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

        # Official Voyage Manifest & Clearance Slip Generator
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 📋 Official Voyage Manifest & Port Clearance Slip")
        
        status_color = "#16a34a" if res.safety.status == "SAFE_GO" else ("#d97706" if res.safety.status == "CAUTION_CONDITIONAL" else "#dc2626")
        manifest_ref = f"IND-MARITIME-{res.port.id.upper()}-{abs(hash(res.port.id + res.top_pfz.zone_id)) % 100000:05d}"
        
        st.markdown(f"""
        <div class="ff-card" style="border: 2px dashed {status_color}; background: var(--primary-subtle); padding: 18px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom: 1px solid var(--border); padding-bottom: 10px;">
                <div>
                    <div style="font-size:16px; font-weight:800; color:var(--primary);">📑 OFFICIAL VOYAGE MANIFEST & CLEARANCE SLIP</div>
                    <div style="font-size:11px; color:var(--text-muted);">Ref: <b>{manifest_ref}</b> · Generated {datetime.now().strftime('%d-%b-%Y %H:%M IST')}</div>
                </div>
                <span style="font-size:12px; font-weight:800; color:{status_color}; background:rgba(0,0,0,0.06); padding:4px 10px; border-radius:4px; border:1px solid {status_color};">
                    {res.safety.status.replace('_', ' ')}
                </span>
            </div>
            <div style="font-size:13px; line-height:1.7; margin-top:10px; color:var(--text-secondary);">
                • <b>Vessel Registered:</b> {st.session_state.vessel_class} (Base Port: {res.port.name})<br>
                • <b>Departure Time:</b> {st.session_state.departure_window} | Water Level: {port_tides.current_water_level_m:.2f}m<br>
                • <b>Target PFZ Frontier:</b> {res.top_pfz.name} ({dist_label_top} · Bearing {res.top_pfz.bearing_deg}°)<br>
                • <b>Target Pelagic Species:</b> {', '.join(res.top_pfz.species_likely[:3])}<br>
                • <b>Tide & Harbor Bar:</b> {port_tides.tide_phase.split('(')[0]} · Depth {port_tides.harbor_bar_depth_m:.1f}m<br>
                • <b>Fuel Estimate:</b> ~{res.route.fuel_burn_liters} L (Current Assisted Saved: <b style="color:#059669;">{res.route.fuel_savings_liters} L</b>)<br>
                • <b>Safety Guard:</b> IMBL {res.safety.border_distance_km} km ({res.safety.nearest_imbl_name})<br>
                • <b>Emergency SAR Dispatch:</b> Coast Guard 1554 · VHF Ch 16 (156.800 MHz) · Police 1093
            </div>
            <div style="margin-top:12px; text-align:right;">
                <button onclick="window.print()" style="background:var(--primary); color:#ffffff; font-weight:700; border:none; padding:8px 18px; border-radius:6px; cursor:pointer; font-size:13px;">
                    🖨️ Print Official Slip
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # SUBVIEW 5.2: PREFERENCES
    # -----------------------------------------------------
    elif st.session_state.sub_settings == "⚙ Preferences":
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

        with p_col2:
            st.markdown("##### 🎨 Cockpit Visual Theme")
            t_opts = ["☀️ Ocula Sky Day", "🌙 Ocula Oceanic Dark", "⚡ Tactical Radar"]
            cur_t = 1
            if "Day" in st.session_state.selected_theme:
                cur_t = 0
            elif "Tactical" in st.session_state.selected_theme:
                cur_t = 2

            sel_t = st.selectbox("Select Theme", options=t_opts, index=cur_t)
            if sel_t != st.session_state.selected_theme:
                st.session_state.selected_theme = sel_t
                st.rerun()

            st.markdown("""
            <div class="ff-card" style="margin-top:14px; font-size:12px; color:var(--text-secondary);">
                <b>Platform Specifications:</b><br>
                • Problem Statement: ISRO SIH26176 / sih_176<br>
                • Architecture: ORCA Multi-Agent AI (5 Collaborative Sub-Agents)<br>
                • Ingestion: ISRO Oceansat-3, INCOIS Rules, Open-Meteo, OpenSeaMap<br>
                • Zero-Hallucination Deterministic Safety Enforcement
            </div>
            """, unsafe_allow_html=True)


# ---------------------------------------------------------
# GLOBAL FOOTER
# ---------------------------------------------------------
st.markdown("<div style='margin-top: 30px; border-top: 1px solid var(--border); padding-top: 14px;'></div>", unsafe_allow_html=True)
st.caption("FishingFriend · ORCA Marine Multi-Agent AI · ISRO SIH26176 · 100% Free Open Telemetry & Open-Source Marine Architecture · Designed for Indian Fishermen & Harbor Authorities.")
