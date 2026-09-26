"""
FishingFriend - ORCA Marine Ecosystem AI & Tactical Maritime Cockpit
Problem Statement: ISRO Smart India Hackathon SIH26176 / sih_176

Entirely Rebuilt UI from Scratch adapting premier open-source marine & weather stacks:
1. smlum/netcdf-vis, leaflet-velocity & IrishMarineInstitute/erddap-leaflet-velocity-demo:
   - Windy.com style animated vector current streamlines
   - Real-time current drift vector arrows and velocity intensity color scale
2. buche/leaflet-openweathermap & openwatersio:
   - OpenSeaMap nautical seamarks, buoys, beacons, fairways, and shoal hazard overlays
   - ESRI Ocean Bathymetry basemap (GEBCO / NOAA submarine contours)
   - Live RainViewer Doppler precipitation radar layer
3. underbluewaters/marinemap:
   - Marine Protected Areas (MPAs) & sensitive Coral Reef conservation buffer zones (MSP)
   - Spatial decision support alerts with statutory fishing restrictions
4. andrewcourtice/ocula:
   - Complete PWA cockpit with 3 switchable themes:
     * ☀️ Ocula Sky Day (Airy, clean, neumorphic light with vibrant ocean blue)
     * 🌙 Ocula Oceanic Dark (Deep abyss navy with glowing sky-blue & radar green)
     * ⚡ Tactical Radar Cockpit (Cyber-GIS dark with neon phosphor & amber warnings)
   - Astronomical Tide Engine with Survey of India harmonic constituents (M2, S2, K1, O1)
   - Ocula High/Low Tide extreme observation cards with formatted IST times & heights
   - Harbor Bar Navigational Keel Clearance depth warning
   - 48-Hour smooth spline tidal elevation chart with gradient area & MSL line
   - 48-Hour Hourly Marine Weather Forecast with INCOIS 2.5m Red Alert threshold line
   - Interactive Live Doppler Radar & Satellite playback viewer
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
    page_title="FishingFriend | ORCA Marine AI Cockpit",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# THEME INJECTION SYSTEM (3 Ocula-Inspired Themes)
# ---------------------------------------------------------

def inject_theme(theme_name: str):
    """Injects high-end, responsive CSS tokens adapted from Ocula design system."""
    
    if "Day" in theme_name:
        # ☀️ Ocula Sky Day: Crisp, airy, neumorphic modern light
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&family=DM+Sans:wght@400;500;700&display=swap');
        
        :root {
            --bg-base: #f0f7ff;
            --bg-gradient: linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%);
            --card-bg: #ffffff;
            --card-border: #bae6fd;
            --text-main: #0f172a;
            --text-muted: #475569;
            --primary: #0284c7;
            --secondary: #0ea5e9;
            --accent: #38bdf8;
            --success: #15803d;
            --warning: #b45309;
            --danger: #b91c1c;
        }

        .stApp {
            background: var(--bg-gradient) !important;
            color: var(--text-main) !important;
            font-family: 'Plus Jakarta Sans', 'DM Sans', -apple-system, sans-serif !important;
        }

        .app-header-card {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 16px 24px;
            margin-bottom: 18px;
            box-shadow: 0 4px 20px rgba(2, 132, 199, 0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .ocula-card {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.06);
            transition: all 0.2s ease-in-out;
        }
        .ocula-card:hover {
            border-color: var(--secondary);
            box-shadow: 0 8px 24px rgba(2, 132, 199, 0.12);
        }

        .telemetry-chip {
            background: #f8fbff;
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }
        .telemetry-val {
            font-size: 24px;
            font-weight: 800;
            color: var(--primary);
            font-family: 'JetBrains Mono', monospace;
        }
        .telemetry-lbl {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 4px;
        }

        .tide-box {
            background: #f8fbff;
            border: 1px solid #bae6fd;
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }

        .hourly-tile {
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.04);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 2px solid var(--card-border);
            padding-bottom: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 8px 18px;
            font-weight: 600;
            color: var(--text-muted);
            font-size: 13px;
        }
        .stTabs [aria-selected="true"] {
            background: #e0f2fe !important;
            color: var(--primary) !important;
        }

        @keyframes flowCurrentStream {
            from { stroke-dashoffset: 40; }
            to { stroke-dashoffset: 0; }
        }
        path.animated-current-flow {
            stroke-dasharray: 8, 14 !important;
            animation: flowCurrentStream 1.3s linear infinite !important;
        }
        </style>
        """, unsafe_allow_html=True)

    elif "Tactical" in theme_name:
        # ⚡ Tactical Radar Cockpit: Cyber-GIS phosphor cockpit
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&family=DM+Sans:wght@400;500;700&display=swap');

        :root {
            --bg-base: #030712;
            --bg-gradient: linear-gradient(180deg, #030712 0%, #0a0f1d 100%);
            --card-bg: #0b1324;
            --card-border: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #10b981;
            --secondary: #00ff88;
            --accent: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }

        .stApp {
            background: var(--bg-gradient) !important;
            color: var(--text-main) !important;
            font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace !important;
        }

        .app-header-card {
            background: #0b1324;
            border: 1px solid #10b981;
            border-radius: 16px;
            padding: 16px 24px;
            margin-bottom: 18px;
            box-shadow: 0 0 25px rgba(16, 185, 129, 0.15);
        }

        .ocula-card {
            background: #0b1324;
            border: 1px solid #1e293b;
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            transition: all 0.2s ease-in-out;
        }
        .ocula-card:hover {
            border-color: #10b981;
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
        }

        .telemetry-chip {
            background: #060e1d;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }
        .telemetry-val {
            font-size: 24px;
            font-weight: 800;
            color: #10b981;
            font-family: 'JetBrains Mono', monospace;
            text-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
        }
        .telemetry-lbl {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #94a3b8;
            margin-bottom: 4px;
        }

        .tide-box {
            background: #060e1d;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }

        .hourly-tile {
            background: #060e1d;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 12px;
            text-align: center;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 2px solid #1e293b;
            padding-bottom: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 8px 18px;
            font-weight: 600;
            color: #94a3b8;
            font-size: 13px;
        }
        .stTabs [aria-selected="true"] {
            background: #0f231c !important;
            color: #10b981 !important;
            border-bottom: 2px solid #10b981;
        }

        @keyframes flowCurrentStream {
            from { stroke-dashoffset: 40; }
            to { stroke-dashoffset: 0; }
        }
        path.animated-current-flow {
            stroke-dasharray: 8, 14 !important;
            animation: flowCurrentStream 1.1s linear infinite !important;
            filter: drop-shadow(0 0 4px #10b981);
        }
        </style>
        """, unsafe_allow_html=True)

    else:
        # 🌙 Ocula Oceanic Dark: Deep abyss navy with neon sky-blue accents (Default Dark)
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&family=DM+Sans:wght@400;500;700&display=swap');

        :root {
            --bg-base: #071322;
            --bg-gradient: linear-gradient(180deg, #071322 0%, #0c1b30 100%);
            --card-bg: #0d2138;
            --card-border: #1e3a5f;
            --text-main: #f0f9ff;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --secondary: #0ea5e9;
            --accent: #7dd3fc;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
        }

        .stApp {
            background: var(--bg-gradient) !important;
            color: var(--text-main) !important;
            font-family: 'Plus Jakarta Sans', 'DM Sans', -apple-system, sans-serif !important;
        }

        .app-header-card {
            background: #0d2138;
            border: 1px solid var(--secondary);
            border-radius: 16px;
            padding: 16px 24px;
            margin-bottom: 18px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }

        .ocula-card {
            background: #0d2138;
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
            transition: all 0.2s ease-in-out;
        }
        .ocula-card:hover {
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.18);
        }

        .telemetry-chip {
            background: #112845;
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }
        .telemetry-val {
            font-size: 24px;
            font-weight: 800;
            color: var(--primary);
            font-family: 'JetBrains Mono', monospace;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
        }
        .telemetry-lbl {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-bottom: 4px;
        }

        .tide-box {
            background: #0b1d33;
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }

        .hourly-tile {
            background: #0d2138;
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 2px solid var(--card-border);
            padding-bottom: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 8px 18px;
            font-weight: 600;
            color: var(--text-muted);
            font-size: 13px;
        }
        .stTabs [aria-selected="true"] {
            background: #112845 !important;
            color: var(--primary) !important;
        }

        @keyframes flowCurrentStream {
            from { stroke-dashoffset: 40; }
            to { stroke-dashoffset: 0; }
        }
        path.animated-current-flow {
            stroke-dasharray: 8, 14 !important;
            animation: flowCurrentStream 1.3s linear infinite !important;
            filter: drop-shadow(0 0 4px #38bdf8);
        }
        </style>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------
# INTERACTIVE GEOSPATIAL MAP ENGINE (Leaflet & MarineMap)
# ---------------------------------------------------------

def render_interactive_map(
    port: PortLocation,
    telemetry: OceanTelemetry,
    safety: HazardEvaluation,
    all_pfzs: List[PFZZone],
    selected_pfz: PFZZone,
    route: RouteWaypoints,
    theme_name: str
):
    """
    Renders an interactive Leaflet geospatial map containing:
    1. Base tiles (CartoDB & ESRI Ocean Bathymetry)
    2. OpenSeaMap seamarks & nautical aids
    3. Live RainViewer Doppler precipitation radar
    4. Marine Protected Areas (MarineMap)
    5. PFZ Hotspots & fuel route
    6. IMBL boundary security polygon
    7. Windy.com style animated ocean current streamlines
    """
    base_tiles = "cartodbpositron" if "Day" in theme_name else "cartodbdark_matter"

    m = folium.Map(
        location=[port.lat, port.lon],
        zoom_start=9,
        tiles=base_tiles,
        name="CartoDB Standard" if "Day" in theme_name else "CartoDB Dark",
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

    # Layer 3: Live Doppler Rain Radar (RainViewer / Ocula)
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
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 12px; color: #0f172a; min-width: 250px;">
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

    # Layer Controls
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    # Inject DOM Animation Trigger for Leaflet SVG Paths
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

    st_folium(m, height=480, use_container_width=True)


# ---------------------------------------------------------
# APPLICATION STATE & PIPELINE
# ---------------------------------------------------------

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = MultiAgentOrchestrator()

if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "☀️ Ocula Sky Day"

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
# TOP BRAND NAVIGATION & CONTROLS
# ---------------------------------------------------------

inject_theme(st.session_state.selected_theme)

# Top Bar with Title, Port Selection, Theme Toggle, Guide & SOS Buttons
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([3.5, 2.5, 2.2, 1.8, 2.0])

with nav_col1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:34px;">⚓</span>
        <div>
            <div style="font-size:22px; font-weight:800; color:var(--primary); line-height:1.1;">FishingFriend</div>
            <div style="font-size:12px; opacity:0.8;">ORCA Marine Multi-Agent AI · ISRO SIH26176</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    port_list = list(INDIAN_PORTS.keys())
    port_names = [f"{INDIAN_PORTS[k].name} ({INDIAN_PORTS[k].state})" for k in port_list]
    cur_idx = port_list.index(st.session_state.active_port_id)
    selected_p = st.selectbox(
        "Base Harbor",
        options=range(len(port_list)),
        format_func=lambda i: port_names[i],
        index=cur_idx,
        label_visibility="collapsed"
    )
    if port_list[selected_p] != st.session_state.active_port_id:
        st.session_state.active_port_id = port_list[selected_p]
        st.rerun()

with nav_col3:
    # 3 Themes: Sky Day, Oceanic Dark, Tactical Cockpit
    theme_options = ["☀️ Ocula Sky Day", "🌙 Ocula Oceanic Dark", "⚡ Tactical Radar"]
    cur_t_idx = 0
    if "Dark" in st.session_state.selected_theme:
        cur_t_idx = 1
    elif "Tactical" in st.session_state.selected_theme:
        cur_t_idx = 2

    chosen_theme = st.selectbox(
        "Cockpit Theme",
        options=theme_options,
        index=cur_t_idx,
        label_visibility="collapsed"
    )
    if chosen_theme != st.session_state.selected_theme:
        st.session_state.selected_theme = chosen_theme
        st.rerun()

with nav_col4:
    if st.button("💡 Guide & SOP", use_container_width=True):
        st.session_state.show_guide_modal = not st.session_state.show_guide_modal

with nav_col5:
    if st.button("🚨 EMERGENCY SOS", type="primary", use_container_width=True):
        st.session_state.show_sos_modal = not st.session_state.show_sos_modal

# ---------------------------------------------------------
# 1-TAP COASTAL PORT QUICK SELECTOR PILLS
# ---------------------------------------------------------
st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
coast_col1, coast_col2 = st.columns([1, 1])

west_ports = [("kochi", "⚓ Kochi"), ("veraval", "⚓ Veraval"), ("mangalore", "⚓ Mangalore"), ("porbandar", "⚓ Porbandar")]
east_ports = [("chennai", "⚓ Chennai"), ("vizag", "⚓ Visakhapatnam"), ("tuticorin", "⚓ Thoothukudi")]

with coast_col1:
    st.markdown("<span style='font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;'>🌊 West Coast (Arabian Sea):</span>", unsafe_allow_html=True)
    w_btn_cols = st.columns(len(west_ports))
    for col, (pid, pname) in zip(w_btn_cols, west_ports):
        with col:
            is_active = (st.session_state.active_port_id == pid)
            if st.button(pname, key=f"quick_port_{pid}", type="primary" if is_active else "secondary", use_container_width=True):
                st.session_state.active_port_id = pid
                st.rerun()

with coast_col2:
    st.markdown("<span style='font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;'>🌊 East Coast (Bay of Bengal):</span>", unsafe_allow_html=True)
    e_btn_cols = st.columns(len(east_ports))
    for col, (pid, pname) in zip(e_btn_cols, east_ports):
        with col:
            is_active = (st.session_state.active_port_id == pid)
            if st.button(pname, key=f"quick_port_{pid}", type="primary" if is_active else "secondary", use_container_width=True):
                st.session_state.active_port_id = pid
                st.rerun()

# ---------------------------------------------------------
# VESSEL SPECIFICATION & VOYAGE CONTROLS EXPANDER
# ---------------------------------------------------------
with st.expander("⛵ Vessel Classification, Departure Timing & Unit Settings", expanded=False):
    v_col1, v_col2, v_col3 = st.columns(3)
    with v_col1:
        vessel_options = [
            "Mechanized Trawler (12-18m)",
            "Small Craft (<10m)",
            "FRP / Fiber Boat (8-10m)",
            "Deep-Sea Longliner (>20m)"
        ]
        cur_v_idx = vessel_options.index(st.session_state.vessel_class) if st.session_state.vessel_class in vessel_options else 0
        sel_vessel = st.selectbox(
            "Vessel Classification & OAL",
            options=vessel_options,
            index=cur_v_idx,
            help="Small Craft (<10m) enforces stricter wave limits (<1.8m) under INCOIS/IMD safety standards."
        )
        if sel_vessel != st.session_state.vessel_class:
            st.session_state.vessel_class = sel_vessel
            st.session_state.last_pipeline_result = None
            st.rerun()

    with v_col2:
        dep_options = [
            "Immediate (Current Tide)",
            "Next High Water Window",
            "Dawn Departure (04:00 IST)",
            "Dusk Departure (17:00 IST)"
        ]
        cur_dep_idx = dep_options.index(st.session_state.departure_window) if st.session_state.departure_window in dep_options else 0
        sel_dep = st.selectbox(
            "Departure Timing Window",
            options=dep_options,
            index=cur_dep_idx,
            help="Harmonizes vessel departure with bar depth & tidal stream."
        )
        if sel_dep != st.session_state.departure_window:
            st.session_state.departure_window = sel_dep
            st.rerun()

    with v_col3:
        unit_options = ["Metric (km/h, km)", "Nautical (knots, nm)"]
        cur_u_idx = unit_options.index(st.session_state.unit_system) if st.session_state.unit_system in unit_options else 0
        sel_unit = st.selectbox(
            "Display Unit System",
            options=unit_options,
            index=cur_u_idx,
            help="Choose between metric units (km/h, km) and maritime nautical units (knots, nm)."
        )
        if sel_unit != st.session_state.unit_system:
            st.session_state.unit_system = sel_unit
            st.rerun()

# ---------------------------------------------------------
# INTERACTIVE SKIPPER'S FIELD GUIDE & ONBOARDING DRAWER
# ---------------------------------------------------------
if st.session_state.show_guide_modal:
    st.markdown("""
    <div class="ocula-card" style="border: 2px solid var(--primary); background: rgba(2, 132, 199, 0.05); margin-top: 10px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:18px; font-weight:800; color:var(--primary);">
                💡 SKIPPER'S FIELD GUIDE & MARITIME ADVISORY STANDARD OPERATING PROCEDURE (SOP)
            </div>
            <div style="font-size:11px; font-weight:700; color:var(--primary); background:rgba(2, 132, 199, 0.15); padding:4px 8px; border-radius:6px;">
                INCOIS / IMD / ICG CODIFIED RULES
            </div>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin-top: 12px;">
            <div style="background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; padding: 10px 12px; border-radius: 6px;">
                <b style="color:#16a34a;">🟢 SAFE OPERATIONAL CLEARANCE (GO)</b>
                <p style="font-size:12px; margin:4px 0 0 0; line-height:1.4;">
                    • Swell &lt; 1.80m & Wind &lt; 32 km/h.<br>
                    • Safe distance from International Maritime Boundaries (&gt;10 nm).<br>
                    • All registered craft permitted for unrestricted offshore voyage.
                </p>
            </div>
            <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 10px 12px; border-radius: 6px;">
                <b style="color:#d97706;">🟡 CONDITIONAL CLEARANCE (CAUTION)</b>
                <p style="font-size:12px; margin:4px 0 0 0; line-height:1.4;">
                    • Swell 1.80m - 2.50m or Wind 32 - 45 km/h.<br>
                    • Traditional craft (&lt;10m) restricted within 12 nm.<br>
                    • Mechanized trawlers maintain continuous VHF Ch 16 watch.
                </p>
            </div>
            <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 10px 12px; border-radius: 6px;">
                <b style="color:#dc2626;">🔴 OPERATIONAL SUSPENSION (NO-GO)</b>
                <p style="font-size:12px; margin:4px 0 0 0; line-height:1.4;">
                    • Swell &gt; 2.50m (INCOIS High Wave Red Alert).<br>
                    • Wind &gt; 45.0 km/h (IMD Squall / Gale Warning).<br>
                    • Proximity to IMBL &lt; 10.0 nm (Apprehension Danger). All vessels remain moored.
                </p>
            </div>
        </div>
        <div style="font-size:12px; margin-top:10px; line-height:1.5; opacity:0.85;">
            🐟 <b>Potential Fishing Zones (PFZs):</b> Calculated using ISRO Oceansat-3 chlorophyll-a and SST thermal boundaries. Convergence lines congregate pelagic fish, cutting searching fuel by 20-30%.<br>
            🚨 <b>Emergency Protocols:</b> Indian Coast Guard Toll-Free: <b>1554</b> | Coastal Security Police: <b>1093</b> | VHF Distress Channel: <b>16</b> | DSC Alert: <b>Channel 70</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# INTERACTIVE QUERY BAR & VOICE PRESETS
# ---------------------------------------------------------
st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)

search_col, run_col = st.columns([8, 2])
with search_col:
    user_q = st.text_input(
        "Voice / Natural Query Input:",
        value=st.session_state.query_text,
        placeholder="Type query or tap a quick voice preset in English, Hindi, or Tamil...",
        label_visibility="collapsed"
    )

with run_col:
    trigger_analyze = st.button("🔍 Analyze Sea", type="secondary", use_container_width=True)

# Quick Voice Preset Pills
p1, p2, p3, p4 = st.columns(4)
with p1:
    if st.button("🎙️ EN: Kochi Tuna", use_container_width=True):
        st.session_state.query_text = "Can we sail from Kochi harbor for Yellowfin Tuna?"
        st.session_state.active_port_id = "kochi"
        st.session_state.advisory_lang = "English"
        st.rerun()
with p2:
    if st.button("🎙️ HI: वेरावल मछली", use_container_width=True):
        st.session_state.query_text = "क्या कल सुबह वेरावल से समुद्र में जाना सुरक्षित है?"
        st.session_state.active_port_id = "veraval"
        st.session_state.advisory_lang = "हिन्दी (Hindi)"
        st.rerun()
with p3:
    if st.button("🎙️ TA: கொச்சி சூரை", use_container_width=True):
        st.session_state.query_text = "கொச்சியிலிருந்து இன்று சூரை மீன் பிடிக்க கடலுக்குச் செல்லலாமா?"
        st.session_state.active_port_id = "kochi"
        st.session_state.advisory_lang = "தமிழ் (Tamil)"
        st.rerun()
with p4:
    if st.button("🎙️ EN: Chennai Pomfret", use_container_width=True):
        st.session_state.query_text = "Chennai harbor to deep Bay of Bengal for Pomfret"
        st.session_state.active_port_id = "chennai"
        st.session_state.advisory_lang = "English"
        st.rerun()

# Run Multi-Agent Pipeline
if trigger_analyze or st.session_state.last_pipeline_result is None or user_q != st.session_state.query_text:
    st.session_state.query_text = user_q
    with st.spinner("Fetching live ocean telemetry, astronomical tides & checking INCOIS rules..."):
        res: ORCASynthesisResult = st.session_state.orchestrator.run_pipeline(
            query=user_q,
            selected_port_id=st.session_state.active_port_id,
            vessel_class=st.session_state.vessel_class
        )
        st.session_state.last_pipeline_result = res

res: ORCASynthesisResult = st.session_state.last_pipeline_result

# Safe fallback for astronomical tides and hourly forecast
port_tides: PortTideData = res.tides if res.tides is not None else calculate_port_tides(res.port.id)
port_hourly: HourlyMarineForecast = res.hourly_forecast if res.hourly_forecast is not None else fetch_hourly_marine_forecast(res.port)


# ---------------------------------------------------------
# INTERACTIVE EMERGENCY SOS BROADCAST DRAWER
# ---------------------------------------------------------
if st.session_state.show_sos_modal:
    st.markdown("""
    <div class="ocula-card" style="border: 2px solid #ef4444; background: rgba(239, 68, 68, 0.05); margin-top: 10px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:20px; font-weight:800; color:#ef4444;">
                🚨 DISTRESS EMERGENCY BEACON GENERATOR (MAYDAY PROTOCOL)
            </div>
            <div style="font-size:12px; font-weight:700; color:#ef4444; background:rgba(239, 68, 68, 0.15); padding:4px 8px; border-radius:6px;">
                VHF CH 16 / DSC CHANNEL 70
            </div>
        </div>
        <p style="font-size:13px; margin:8px 0 12px 0;">
            Immediate broadcast payload for Indian Coast Guard (1554) and Coastal Security Police (1093).
        </p>
    </div>
    """, unsafe_allow_html=True)

    sos_col1, sos_col2 = st.columns([7, 3])
    with sos_col1:
        distress_payload = (
            f"MAYDAY MAYDAY MAYDAY\n"
            f"VESSEL: Mechanized Fishing Trawler (Reg: IND-{res.port.id.upper()}-402)\n"
            f"CURRENT POSITION: Lat {res.port.lat:.4f}° N, Lon {res.port.lon:.4f}° E\n"
            f"NEAREST BASE: {res.port.name}, {res.port.state} (Coast: {res.port.coast})\n"
            f"NEAREST INT'L BOUNDARY: {res.safety.nearest_imbl_name} ({res.safety.border_distance_km} km away)\n"
            f"CURRENT WAVE / SWELL: {res.telemetry.wave_height}m (Swell {res.telemetry.swell_wave_height}m)\n"
            f"EMERGENCY FREQUENCY: VHF Ch 16 (156.800 MHz) | Distress Relay: 1554"
        )
        st.code(distress_payload, language="text")

    with sos_col2:
        st.markdown(f"""
        <div style="font-size:13px; line-height:1.7;">
            <b>📞 Immediate Direct Dials:</b><br>
            • <b>Coast Guard MRCC:</b> <a href="tel:1554" style="color:var(--primary); font-weight:bold;">1554</a> (Toll-Free)<br>
            • <b>Coastal Marine Police:</b> <a href="tel:1093" style="color:var(--primary); font-weight:bold;">1093</a> (24x7)<br>
            • <b>Disaster Management:</b> 1070 / 1077<br>
            • <b>Sea Ambulance:</b> 108
        </div>
        """, unsafe_allow_html=True)
        if st.button("📡 Broadcast Distress Alert (Simulated)", type="primary", use_container_width=True):
            st.success("✅ Simulated Mayday Packet transmitted to nearest Coast Guard MRCC Station and Marine Police.")


# ---------------------------------------------------------
# UNIFIED STATUS HERO & LIVE METRICS CHIPS
# ---------------------------------------------------------
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# 1. Operational Clearance Banner
if res.safety.status == "SAFE_GO":
    st.markdown(f"""
    <div class="ocula-card" style="border-left: 6px solid #22c55e; background: rgba(34, 197, 94, 0.08);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-size:22px; font-weight:800; color:#16a34a;">🟢 SAFE OPERATIONAL CLEARANCE: GO</span><br>
                <span style="font-size:13px; opacity:0.9;">
                    Normal sea state off {res.port.name}. Wave swell within safe limit (&lt;2.5m). Unrestricted fishing permitted.
                </span>
            </div>
            <div style="text-align:right;">
                <div style="font-size:22px; font-weight:800; color:#16a34a;">{res.safety.risk_score} / 100</div>
                <div style="font-size:11px; text-transform:uppercase; font-weight:700;">Risk Score</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
elif res.safety.status == "CAUTION_CONDITIONAL":
    st.markdown(f"""
    <div class="ocula-card" style="border-left: 6px solid #f59e0b; background: rgba(245, 158, 11, 0.08);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-size:22px; font-weight:800; color:#d97706;">🟡 CONDITIONAL CLEARANCE: CAUTION</span><br>
                <span style="font-size:13px; opacity:0.9;">
                    Moderate swell or wind gusts off {res.port.name}. Traditional craft &lt;10m advised to stay within 12 nm.
                </span>
            </div>
            <div style="text-align:right;">
                <div style="font-size:22px; font-weight:800; color:#d97706;">{res.safety.risk_score} / 100</div>
                <div style="font-size:11px; text-transform:uppercase; font-weight:700;">Risk Score</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="ocula-card" style="border-left: 6px solid #ef4444; background: rgba(239, 68, 68, 0.08);">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-size:22px; font-weight:800; color:#dc2626;">🔴 DANGER: NO-GO (OPERATIONS SUSPENDED)</span><br>
                <span style="font-size:13px; opacity:0.9;">
                    INCOIS/IMD threshold breached: Swell &gt; 2.5m or wind &gt; 45 km/h. All vessels ordered to remain moored.
                </span>
            </div>
            <div style="text-align:right;">
                <div style="font-size:22px; font-weight:800; color:#dc2626;">{res.safety.risk_score} / 100</div>
                <div style="font-size:11px; text-transform:uppercase; font-weight:700;">Risk Score</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 2. Live Telemetry Chips (5 clean metric cards with Dynamic Units)
is_naut = "Nautical" in st.session_state.unit_system

if is_naut:
    curr_disp = f"{res.telemetry.ocean_current_velocity * 0.539957:.1f}"
    curr_unit = "kts"
    wind_disp = f"{res.telemetry.wind_speed * 0.539957:.1f}"
    wind_unit = "kts"
    gust_disp = f"Gusts {res.telemetry.wind_gusts * 0.539957:.1f} kts"
else:
    curr_disp = f"{res.telemetry.ocean_current_velocity:.1f}"
    curr_unit = "km/h"
    wind_disp = f"{res.telemetry.wind_speed:.1f}"
    wind_unit = "km/h"
    gust_disp = f"Gusts {res.telemetry.wind_gusts:.1f} km/h"

tc1, tc2, tc3, tc4, tc5 = st.columns(5)
with tc1:
    st.markdown(f"""
    <div class="telemetry-chip">
        <div class="telemetry-lbl">🌊 Swell Height</div>
        <div class="telemetry-val">{res.telemetry.swell_wave_height} <span style="font-size:14px;">m</span></div>
        <div style="font-size:11px; opacity:0.75;">Period {res.telemetry.swell_wave_period}s</div>
    </div>
    """, unsafe_allow_html=True)

with tc2:
    st.markdown(f"""
    <div class="telemetry-chip">
        <div class="telemetry-lbl">🌡️ Sea Temp (SST)</div>
        <div class="telemetry-val">{res.telemetry.sea_surface_temperature}°<span style="font-size:14px;">C</span></div>
        <div style="font-size:11px; opacity:0.75;">Thermal Edge</div>
    </div>
    """, unsafe_allow_html=True)

with tc3:
    st.markdown(f"""
    <div class="telemetry-chip">
        <div class="telemetry-lbl">💨 Ocean Current</div>
        <div class="telemetry-val">{curr_disp} <span style="font-size:14px;">{curr_unit}</span></div>
        <div style="font-size:11px; opacity:0.75;">Drift {res.telemetry.ocean_current_direction:.0f}°</div>
    </div>
    """, unsafe_allow_html=True)

with tc4:
    st.markdown(f"""
    <div class="telemetry-chip">
        <div class="telemetry-lbl">🌬️ Wind Speed</div>
        <div class="telemetry-val">{wind_disp} <span style="font-size:14px;">{wind_unit}</span></div>
        <div style="font-size:11px; opacity:0.75;">{gust_disp}</div>
    </div>
    """, unsafe_allow_html=True)

with tc5:
    st.markdown(f"""
    <div class="telemetry-chip">
        <div class="telemetry-lbl">🧪 Chlorophyll-a</div>
        <div class="telemetry-val">{res.telemetry.chlorophyll_proxy} <span style="font-size:12px;">mg/m³</span></div>
        <div style="font-size:11px; opacity:0.75;">Oceansat-3 Proxy</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# STREAMLINED TABBED WORKSPACE (7 Rich Dedicated Workspaces)
# ---------------------------------------------------------
st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

tab_map, tab_tides, tab_hourly, tab_radar, tab_emergency, tab_advisory, tab_audit = st.tabs([
    "🗺️ Tactical Map & Layers",
    "🌊 Astronomical Tides (Ocula)",
    "⏱️ 48h Forecast (Ocula)",
    "📡 Live Radar & Satellite (Ocula)",
    "🚨 Emergency Shore Contacts",
    "📢 Actionable Advisory (EN/HI/TA)",
    "🛡️ Zero-Hallucination Audit"
])

# =========================================================
# TAB 1: TACTICAL MAP & OCEAN LAYERS
# =========================================================
with tab_map:
    map_col, info_col = st.columns([7, 5])
    
    with map_col:
        st.markdown("##### 📍 Interactive Tactical Map (OpenSeaMap, ESRI Bathymetry & Animated Currents)")
        st.caption("Layer control (top-right): Toggle Nautical Marks, Bathymetry, MPAs, PFZ Hotspots, & Windy Streamlines.")
        render_interactive_map(
            port=res.port,
            telemetry=res.telemetry,
            safety=res.safety,
            all_pfzs=res.all_pfzs,
            selected_pfz=res.top_pfz,
            route=res.route,
            theme_name=st.session_state.selected_theme
        )
    
    with info_col:
        st.markdown("##### 🐟 Recommended Potential Fishing Zones (PFZ)")
        for pfz in res.all_pfzs:
            is_top = (pfz.zone_id == res.top_pfz.zone_id)
            badge_border = "border: 2px solid var(--primary);" if is_top else "border: 1px solid var(--card-border);"
            bg_accent = "background: rgba(2, 132, 199, 0.05);" if is_top else ""
            
            st.markdown(f"""
            <div class="ocula-card" style="{badge_border} {bg_accent} padding: 14px 16px; margin-bottom: 10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:700; font-size:15px; color:var(--primary);">
                        {'⭐ ' if is_top else ''}{pfz.name}
                    </div>
                    <div style="font-size:14px; font-weight:800; color:#059669;">
                        {pfz.fish_density_score}% Catch Score
                    </div>
                </div>
                <div style="font-size:12px; margin-top:6px; line-height:1.5;">
                    <b>Range:</b> {pfz.distance_km} km @ {pfz.bearing_deg}° | <b>Depth:</b> {pfz.depth_m}m<br>
                    <b>Species:</b> <span style="color:var(--primary);">{', '.join(pfz.species_likely[:3])}</span><br>
                    <b>Thermal Edge:</b> {pfz.thermal_gradient_desc}
                </div>
            </div>
            """, unsafe_allow_html=True)

        dist_label = f"{res.route.total_distance_nm:.1f} nm" if is_naut else f"{res.route.total_distance_nm * 1.852:.1f} km"
        st.markdown(f"""
        <div style="font-size:12px; opacity:0.85; margin-top:8px;">
            ⛽ <b>Navigation Plan:</b> {dist_label} · Transit ~{res.route.estimated_transit_hours:.1f} hrs · 
            Diesel ~{res.route.fuel_burn_liters} L (Savings: <span style="color:#059669; font-weight:bold;">{res.route.fuel_savings_liters} L</span>).
        </div>
        """, unsafe_allow_html=True)

        # Voyage Manifest & Clearance Slip Generator
        if st.button("📋 View / Print Voyage Clearance Manifest", key="btn_toggle_manifest", type="secondary", use_container_width=True):
            st.session_state.show_manifest_modal = not st.session_state.show_manifest_modal

        if st.session_state.show_manifest_modal:
            status_color = "#16a34a" if res.safety.status == "SAFE_GO" else ("#d97706" if res.safety.status == "CAUTION_CONDITIONAL" else "#dc2626")
            manifest_ref = f"IND-MARITIME-{res.port.id.upper()}-{abs(hash(res.port.id + res.top_pfz.zone_id)) % 100000:05d}"
            
            st.markdown(f"""
            <div class="ocula-card" style="border: 2px dashed {status_color}; background: rgba(2, 132, 199, 0.04); margin-top: 10px; padding: 16px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom: 1px solid var(--card-border); padding-bottom: 8px;">
                    <div>
                        <div style="font-size:15px; font-weight:800; color:var(--primary);">📑 OFFICIAL VOYAGE MANIFEST & CLEARANCE SLIP</div>
                        <div style="font-size:11px; opacity:0.8;">Ref: <b>{manifest_ref}</b> · {datetime.now().strftime('%d-%b-%Y %H:%M IST')}</div>
                    </div>
                    <span style="font-size:12px; font-weight:800; color:{status_color}; background:rgba(0,0,0,0.06); padding:2px 8px; border-radius:4px; border:1px solid {status_color};">
                        {res.safety.status.replace('_', ' ')}
                    </span>
                </div>
                <div style="font-size:12px; line-height:1.6; margin-top:8px;">
                    • <b>Vessel:</b> {st.session_state.vessel_class} (Port: {res.port.name})<br>
                    • <b>Departure:</b> {st.session_state.departure_window} | Water Level: {port_tides.current_water_level_m:.2f}m<br>
                    • <b>Target PFZ:</b> {res.top_pfz.name} ({dist_label} · Bearing {res.top_pfz.bearing_deg}°)<br>
                    • <b>Target Species:</b> {', '.join(res.top_pfz.species_likely[:3])}<br>
                    • <b>Tide & Harbor Bar:</b> {port_tides.tide_phase.split('(')[0]} · Depth {port_tides.harbor_bar_depth_m:.1f}m<br>
                    • <b>Fuel Estimate:</b> ~{res.route.fuel_burn_liters} L (Saved: {res.route.fuel_savings_liters} L)<br>
                    • <b>Safety Guard:</b> IMBL {res.safety.border_distance_km} km ({res.safety.nearest_imbl_name})<br>
                    • <b>Emergency SAR:</b> Coast Guard 1554 · VHF Ch 16 (156.800 MHz) · Police 1093
                </div>
                <div style="margin-top:10px; text-align:right;">
                    <button onclick="window.print()" style="background:var(--primary); color:#ffffff; font-weight:700; border:none; padding:6px 14px; border-radius:6px; cursor:pointer; font-size:12px;">
                        🖨️ Print Voyage Slip
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Marine Spatial Planning (MarineMap)
        st.markdown("---")
        st.markdown("##### 🛡️ Marine Spatial Planning & MPA Reserves (MarineMap)")
        mpas_local = get_marine_spatial_zones(res.port.id)
        if mpas_local:
            for m in mpas_local[:2]:
                st.markdown(f"""
                <div style="font-size:12px; padding:8px 12px; background:rgba(234, 88, 12, 0.08); border-left:3px solid #ea580c; border-radius:6px; margin-bottom:6px;">
                    <b>{m.name}:</b> {m.restriction[:110]}...
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No restricted marine sanctuaries immediately adjacent to this harbor fairway.")


# =========================================================
# TAB 2: ASTRONOMICAL TIDES & WATER LEVELS (Ocula Engine)
# =========================================================
with tab_tides:
    st.markdown(f"##### 🌊 Astronomical Tides & Coastal Water Levels for **{port_tides.port_name}**")
    st.caption("Harmonic constituents calibrated against Survey of India & NIO tidal benchmarks (Adapted from Ocula PWA Architecture).")

    # 1. Tidal Bar & Keel Warning
    tb1, tb2, tb3, tb4 = st.columns(4)
    with tb1:
        st.markdown(f"""
        <div class="tide-box">
            <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">Water Level</div>
            <div style="font-size:24px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono'; margin:4px 0;">
                {port_tides.current_water_level_m:.2f} <span style="font-size:14px;">m</span>
            </div>
            <div style="font-size:11px; opacity:0.8;">Above Chart Datum</div>
        </div>
        """, unsafe_allow_html=True)

    with tb2:
        st.markdown(f"""
        <div class="tide-box">
            <div style="font-size:11px; font-weight:700; color:#059669; text-transform:uppercase;">Tidal Phase</div>
            <div style="font-size:18px; font-weight:800; color:#059669; margin:6px 0;">
                {port_tides.tide_phase.split('(')[0].strip()}
            </div>
            <div style="font-size:11px; opacity:0.8;">{port_tides.time_to_next_extreme}</div>
        </div>
        """, unsafe_allow_html=True)

    with tb3:
        st.markdown(f"""
        <div class="tide-box">
            <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">Stream Velocity</div>
            <div style="font-size:24px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono'; margin:4px 0;">
                {port_tides.tidal_stream_velocity_knots:.1f} <span style="font-size:14px;">kts</span>
            </div>
            <div style="font-size:11px; opacity:0.8;">Spring Range: {port_tides.mean_spring_range_m:.2f}m</div>
        </div>
        """, unsafe_allow_html=True)

    with tb4:
        st.markdown(f"""
        <div class="tide-box">
            <div style="font-size:11px; font-weight:700; color:#d97706; text-transform:uppercase;">Harbor Bar Depth</div>
            <div style="font-size:24px; font-weight:800; color:#d97706; font-family:'JetBrains Mono'; margin:4px 0;">
                {port_tides.harbor_bar_depth_m:.1f} <span style="font-size:14px;">m</span>
            </div>
            <div style="font-size:11px; opacity:0.8;">At Low Water Datum</div>
        </div>
        """, unsafe_allow_html=True)

    if port_tides.harbor_bar_keel_warning:
        st.markdown(f"""
        <div style="background:rgba(217, 119, 6, 0.1); border-left:4px solid #d97706; padding:10px 16px; border-radius:8px; margin: 12px 0; font-size:13px;">
            ⚠️ <b>HARBOR BAR NOTICE:</b> {port_tides.harbor_bar_keel_warning}
        </div>
        """, unsafe_allow_html=True)

    # 2. Ocula Observation Extreme Cards
    st.markdown("###### 📊 Today's & Tomorrow's High / Low Tide Extremes (Ocula Observations)")
    all_extremes = port_tides.extremes_today + port_tides.extremes_tomorrow[:2]
    ext_cols = st.columns(len(all_extremes))
    
    for c, ext in zip(ext_cols, all_extremes):
        with c:
            # Resilient attribute extraction
            ext_type_str = getattr(ext, 'type', getattr(ext, 'extreme_type', 'Tide'))
            is_high = "High" in ext_type_str
            type_icon = "▲" if is_high else "▼"
            type_color = "#0284c7" if is_high else "#059669"
            
            st.markdown(f"""
            <div class="tide-box" style="border-top:3px solid {type_color};">
                <div style="font-size:11px; font-weight:700; color:{type_color}; text-transform:uppercase;">
                    {type_icon} {ext_type_str}
                </div>
                <div style="font-size:18px; font-weight:800; font-family:'JetBrains Mono'; margin:4px 0;">
                    {ext.time_str}
                </div>
                <div style="font-size:14px; font-weight:700; color:{type_color};">
                    {ext.height_m:.2f} m
                </div>
                <div style="font-size:10px; opacity:0.75; margin-top:4px;">
                    {'Optimal Clearance' if is_high else 'Shallow Water'}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. Continuous 48-Hour Spline Tide Elevation Chart
    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    st.markdown("###### 📈 48-Hour Continuous Spline Tide Elevation Chart")
    
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
    ).configure_title(fontSize=14, anchor="start", color=chart_color)

    st.altair_chart(final_tide_chart, use_container_width=True)
    st.caption("ℹ️ Spline curve computed using M2, S2, K1, O1 principal astronomical harmonic constituents.")


# =========================================================
# TAB 3: 48-HOUR MARINE FORECAST (Ocula Hourly Trends)
# =========================================================
with tab_hourly:
    st.markdown(f"##### ⏱️ 48-Hour Marine Weather & Swell Forecast for **{port_hourly.port_name}**")
    st.caption("Detailed hourly wave heights, swell periods, current vectors, and wind squall indicators (Ocula Architecture).")

    # Overview Cards Row
    hc1, hc2, hc3 = st.columns(3)
    with hc1:
        st.markdown(f"""
        <div class="ocula-card" style="text-align:center; padding:12px;">
            <div style="font-size:11px; font-weight:700; color:var(--primary);">48H PEAK SWELL HEIGHT</div>
            <div style="font-size:24px; font-weight:800; color:var(--primary); font-family:'JetBrains Mono'; margin:4px 0;">
                {port_hourly.max_wave_height:.2f} <span style="font-size:14px;">m</span>
            </div>
            <div style="font-size:11px; opacity:0.8;">INCOIS Status: <b>{port_hourly.incois_wave_risk}</b></div>
        </div>
        """, unsafe_allow_html=True)

    with hc2:
        st.markdown(f"""
        <div class="ocula-card" style="text-align:center; padding:12px;">
            <div style="font-size:11px; font-weight:700; color:#d97706;">48H MAX WIND GUST</div>
            <div style="font-size:24px; font-weight:800; color:#d97706; font-family:'JetBrains Mono'; margin:4px 0;">
                {port_hourly.max_wind_gust:.1f} <span style="font-size:14px;">km/h</span>
            </div>
            <div style="font-size:11px; opacity:0.8;">IMD Status: <b>{port_hourly.imd_wind_risk}</b></div>
        </div>
        """, unsafe_allow_html=True)

    with hc3:
        st.markdown(f"""
        <div class="ocula-card" style="text-align:center; padding:12px;">
            <div style="font-size:11px; font-weight:700; color:#059669;">TELEMETRY DATA SOURCE</div>
            <div style="font-size:20px; font-weight:800; color:#059669; margin:6px 0;">
                {'Live Open-Meteo' if port_hourly.is_live else 'Synthetic Marine Physics'}
            </div>
            <div style="font-size:11px; opacity:0.8;">Forecast Horizon: 48 Hours Ahead</div>
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

    chart_wave = alt.Chart(df_hourly).mark_line(
        interpolate="monotone",
        color="#0284c7" if "Day" in st.session_state.selected_theme else ("#10b981" if "Tactical" in st.session_state.selected_theme else "#38bdf8"),
        strokeWidth=3
    ).encode(
        x=alt.X("Hour:N", title="Forecast Timeline", axis=alt.Axis(labelAngle=-45)),
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
    ).configure_title(fontSize=14, anchor="start", color="var(--primary)")

    st.altair_chart(final_forecast_chart, use_container_width=True)

    # Horizontal Hourly Observation Cards (Next 6 Steps)
    st.markdown("###### ⏱️ Upcoming Hourly Marine Windows")
    step_cols = st.columns(6)
    for idx, (c, h_entry) in enumerate(zip(step_cols, port_hourly.hours[::3][:6])):
        with c:
            is_danger_wave = h_entry.swell_wave_height_m >= 2.5
            is_caution_wave = h_entry.swell_wave_height_m >= 1.8 and not is_danger_wave
            badge_color = "#ef4444" if is_danger_wave else ("#f59e0b" if is_caution_wave else "#059669")
            badge_text = "DANGER" if is_danger_wave else ("CAUTION" if is_caution_wave else "SAFE")
            
            st.markdown(f"""
            <div class="hourly-tile" style="border-top:3px solid {badge_color};">
                <div style="font-size:11px; font-weight:700; color:var(--primary);">{h_entry.hour_label.split(' ')[1]}</div>
                <div style="font-size:16px; font-weight:800; margin:4px 0;">{h_entry.wave_height_m:.1f} m</div>
                <div style="font-size:10px; color:#64748b;">Swell: {h_entry.swell_wave_height_m:.1f}m ({h_entry.swell_wave_period_s}s)</div>
                <div style="font-size:10px; color:#64748b;">Wind: {h_entry.wind_speed_kmh:.0f} km/h</div>
                <div style="font-size:10px; color:#64748b;">Rain: {h_entry.precipitation_probability_pct}%</div>
                <div style="font-size:10px; font-weight:700; color:{badge_color}; margin-top:4px;">{badge_text}</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# TAB 4: LIVE RADAR & SATELLITE (Ocula Radar)
# =========================================================
with tab_radar:
    st.markdown("##### 📡 Live Doppler Precipitation Radar & Cloud Motion Playback")
    st.caption("Real-time telemetry frames adapted from Ocula weather radar playback & RainViewer Global Weather Service.")

    rad_col1, rad_col2 = st.columns([8, 4])
    with rad_col1:
        st.markdown(f"""
        <div class="ocula-card" style="padding:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; font-size:14px; color:var(--primary);">
                    🌧️ Active Coastal Precipitation & Storm Squalls: {res.port.name}
                </span>
                <span style="font-size:11px; background:rgba(2, 132, 199, 0.1); color:var(--primary); padding:2px 8px; border-radius:4px; font-weight:600;">
                    LIVE DOPPLER FEED
                </span>
            </div>
            <iframe 
                src="https://www.rainviewer.com/map.html?loc={res.port.lat},{res.port.lon},8&oFa=0&oC=1&oU=0&oCS=1&oF=0&oAP=1&c=3&o=83&lm=1&layer=radar&sm=1&sn=1" 
                width="100%" 
                height="450" 
                style="border:none; border-radius:10px;"
                allowfullscreen>
            </iframe>
        </div>
        """, unsafe_allow_html=True)

    with rad_col2:
        st.markdown(f"""
        <div class="ocula-card">
            <h4 style="margin:0 0 10px 0; color:var(--primary); font-size:16px;">🌦️ Doppler Radar Interpretation</h4>
            <div style="font-size:12px; line-height:1.7;">
                • <b>Indian Radar Network:</b> Connected to coastal Doppler radars (IMD Kochi, Chennai, Mumbai, Visakhapatnam, Machilipatnam).<br>
                • <b>Reflectivity Scale (dBZ):</b><br>
                  &nbsp;&nbsp;🟦 <b>15 - 25 dBZ:</b> Light coastal drizzle / mist.<br>
                  &nbsp;&nbsp;🟩 <b>25 - 35 dBZ:</b> Moderate rain showers.<br>
                  &nbsp;&nbsp;🟨 <b>35 - 45 dBZ:</b> Heavy monsoon squalls & reduced visibility.<br>
                  &nbsp;&nbsp;🟥 <b>> 45 dBZ:</b> Severe storm cell with gale gusts (&gt;45 km/h).
            </div>
            <div style="background:rgba(2, 132, 199, 0.08); border-left:3px solid var(--primary); padding:10px 12px; border-radius:6px; font-size:12px; margin-top:12px;">
                💡 <b>Skipper Directive:</b> If red or dark orange squall echoes develop within 15 nm of the return fairway, immediately abort deep-sea transit.
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# TAB 5: EMERGENCY SHORE GUARD & CONTACTS
# =========================================================
with tab_emergency:
    st.markdown(f"##### 🚨 24x7 Emergency Coastal Shore Guards, Marine Police & Port Helplines for **{res.port.name}**")
    st.caption("Official direct dispatch channels for sea emergencies, search & rescue (SAR), and border alerts.")

    # Top National Toll-Free Helplines Row
    em_h1, em_h2, em_h3, em_h4 = st.columns(4)
    with em_h1:
        st.markdown("""
        <div class="ocula-card" style="text-align:center; border-top: 3px solid #0284c7;">
            <div style="font-size:12px; font-weight:700; color:#0284c7;">INDIAN COAST GUARD</div>
            <div style="font-size:24px; font-weight:800; color:#0284c7; margin:4px 0;">1554</div>
            <div style="font-size:11px; opacity:0.8;">Toll-Free 24x7 Maritime SAR</div>
        </div>
        """, unsafe_allow_html=True)

    with em_h2:
        st.markdown("""
        <div class="ocula-card" style="text-align:center; border-top: 3px solid #059669;">
            <div style="font-size:12px; font-weight:700; color:#059669;">COASTAL MARINE POLICE</div>
            <div style="font-size:24px; font-weight:800; color:#059669; margin:4px 0;">1093</div>
            <div style="font-size:11px; opacity:0.8;">Toll-Free Coastal Security</div>
        </div>
        """, unsafe_allow_html=True)

    with em_h3:
        st.markdown("""
        <div class="ocula-card" style="text-align:center; border-top: 3px solid #d97706;">
            <div style="font-size:12px; font-weight:700; color:#d97706;">DISASTER MANAGEMENT</div>
            <div style="font-size:24px; font-weight:800; color:#d97706; margin:4px 0;">1070 / 1077</div>
            <div style="font-size:11px; opacity:0.8;">State / District SEOC</div>
        </div>
        """, unsafe_allow_html=True)

    with em_h4:
        st.markdown("""
        <div class="ocula-card" style="text-align:center; border-top: 3px solid #dc2626;">
            <div style="font-size:12px; font-weight:700; color:#dc2626;">SEA AMBULANCE / MEDICAL</div>
            <div style="font-size:24px; font-weight:800; color:#dc2626; margin:4px 0;">108</div>
            <div style="font-size:11px; opacity:0.8;">Emergency Medical Evacuation</div>
        </div>
        """, unsafe_allow_html=True)

    # Detailed Port-Specific Agencies
    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    contacts = res.emergency_contacts if res.emergency_contacts else get_emergency_contacts(res.port.id)
    
    c_left, c_right = st.columns(2)
    for idx, c in enumerate(contacts):
        target_col = c_left if idx % 2 == 0 else c_right
        with target_col:
            badge_color = "#0284c7" if "Coast Guard" in c.category else ("#059669" if "Police" in c.category else "#d97706")
            st.markdown(f"""
            <div class="emergency-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <span style="font-size:11px; font-weight:700; color:{badge_color}; text-transform:uppercase;">
                            {c.category}
                        </span>
                        <div style="font-size:15px; font-weight:700; margin-top:2px;">{c.agency_name}</div>
                    </div>
                    <span style="font-size:12px; font-weight:700; background:rgba(2, 132, 199, 0.1); color:#0284c7; padding:2px 8px; border-radius:4px;">
                        {c.toll_free}
                    </span>
                </div>
                <div style="font-size:12px; margin-top:8px; line-height:1.6;">
                    📞 <b>Direct Phone:</b> {c.phone}<br>
                    📻 <b>Radio Channel:</b> <span style="font-weight:600; color:#0284c7;">{c.vhf_channel}</span><br>
                    📍 <b>Station Base:</b> {c.location} | <b>Sector:</b> {c.jurisdiction}<br>
                    🛡️ <b>Response Role:</b> {c.response_role}
                </div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# TAB 6: MULTILINGUAL ADVISORY
# =========================================================
with tab_advisory:
    st.markdown("##### 🌐 Actionable Multilingual Maritime Guidance")

    lang_pill = st.segmented_control(
        "Select Language",
        options=["English", "हिन्दी (Hindi)", "தமிழ் (Tamil)"],
        default=st.session_state.advisory_lang
    )
    if lang_pill:
        st.session_state.advisory_lang = lang_pill

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
    <div style="background:rgba(2, 132, 199, 0.08); border:1px solid #0284c7; border-radius:10px; padding:12px 18px; margin-bottom: 14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; font-family:'Plus Jakarta Sans', sans-serif;">
        <div>
            <div style="font-weight:700; font-size:14px; color:#0284c7;">{speech_label}</div>
            <div style="font-size:12px; color:#64748b;">Spoken audio voice advisory for skippers & deckhands with zero reading required.</div>
        </div>
        <div style="display:flex; gap:8px;">
            <button id="tts-play-btn" onclick="playAdvisorySpeech()" style="background:#0284c7; color:#ffffff; border:none; padding:8px 16px; border-radius:6px; font-weight:700; cursor:pointer; font-size:13px;">
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
        <div class="ocula-card">
            <h3 style="margin:0 0 10px 0; color:var(--primary); font-size:18px;">{adv['title']}</h3>
            <div style="font-weight:700; font-size:15px; margin-bottom:8px;">{adv['status_headline']}</div>
            <p style="font-size:13px; line-height:1.6; opacity:0.9;">{adv['executive_summary']}</p>
            <div style="background:rgba(2, 132, 199, 0.08); border-left:3px solid var(--primary); padding:10px 14px; border-radius:6px; font-size:13px; margin:12px 0;">
                <b>Directive:</b> {adv['safety_action']}
            </div>
            <div style="font-size:13px; line-height:1.6;">
                <b>Target Fish Species:</b> {adv['recommended_pfz']['target_species']}<br>
                <b>Recommended Zone:</b> {adv['recommended_pfz']['name']} ({adv['recommended_pfz']['coordinates']})<br>
                <b>Distance & Heading:</b> {adv['recommended_pfz']['distance_bearing']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with adv_col2:
        st.markdown(f"""
        <div class="ocula-card">
            <div style="font-size:15px; font-weight:700; color:var(--primary); margin-bottom:8px;">⛽ Transit & Fuel Economics</div>
            <div style="font-size:13px; line-height:1.7;">
                • <b>Transit Duration:</b> {adv['fuel_and_route']['estimated_transit']}<br>
                • <b>Diesel Consumption:</b> {adv['fuel_and_route']['fuel_consumption']}<br>
                • <b>Fuel Saved:</b> <span style="color:#059669; font-weight:bold;">{adv['fuel_and_route']['fuel_savings']}</span><br>
                • <b>Ocean Current Assist:</b> {adv['fuel_and_route']['current_notes']}<br>
                • <b>Boundary Safety:</b> {adv['fuel_and_route']['border_safety']}
            </div>
            <div style="margin-top:14px; padding:10px; background:rgba(2, 132, 199, 0.06); border-radius:6px; font-size:12px;">
                📞 <b>Emergency Assistance:</b> {adv['emergency_contacts']}
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# TAB 7: RULE AUDIT TRAIL
# =========================================================
with tab_audit:
    st.markdown("##### 🛡️ Deterministic Rule Compliance Matrix (Zero-Hallucination Guardrails)")
    st.caption("Every physical threshold is strictly evaluated in pure Python before synthesis. LLMs cannot hallucinate safety.")

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
    st.dataframe(audit_table, width=1000)

    with st.expander("Collaborative Multi-Agent Execution Telemetry"):
        st.write(f"Total Execution Time: **{res.total_execution_time_ms} ms** across 5 collaborative agents.")
        step_cols = st.columns(len(res.agent_logs))
        for col, log in zip(step_cols, res.agent_logs):
            with col:
                st.markdown(f"""
                <div class="ocula-card" style="padding:10px; text-align:center;">
                    <div style="font-size:11px; font-weight:700; color:var(--primary);">{log.agent_name.split('(')[0]}</div>
                    <div style="font-size:12px; font-weight:700; margin:4px 0;">{log.duration_ms} ms</div>
                    <div style="font-size:10px; color:{'#059669' if log.status=='COMPLETED' else '#ef4444'}; font-weight:600;">{log.status}</div>
                </div>
                """, unsafe_allow_html=True)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
st.caption("FishingFriend · ISRO SIH26176 / sih_176 · 100% Free Open Telemetry & Open-Source Marine Architecture · Designed for Indian Fishermen & Harbor Authorities.")
