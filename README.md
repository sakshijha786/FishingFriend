# ⚓ FishingFriend - ORCA Marine Ecosystem AI & Tactical Maritime Cockpit

> **Problem Statement:** ISRO Smart India Hackathon **SIH26176 / sih_176**  
> *ORCA: Marine EcOsystem Reasoning with Collaborative Agents*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Folium](https://img.shields.io/badge/Folium-Leaflet-green.svg)](https://python-visualization.github.io/folium/)
[![Open-Meteo](https://img.shields.io/badge/Telemetry-Open--Meteo%20Marine%20(Free)-0284c7.svg)](https://open-meteo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FishingFriend** is an advanced, production-grade geospatial and multi-agent marine advisory platform built for coastal skippers, artisanal fishermen, and harbor authorities across India. It bridges live satellite oceanography, real-time wave/current telemetry, deterministic INCOIS/IMD physical safety rules, and collaborative AI agents to provide zero-hallucination **Go / No-Go clearances**, fuel-optimized **Potential Fishing Zone (PFZ) routing**, and **multilingual skipper advisories** in English, Hindi (हिन्दी), and Tamil (தமிழ்).

---

## 🌟 Key Architecture & Features

### 1. 🌊 Interactive Leaflet Map with Animated Ocean Layers
Adapted from [`leaflet-velocity`](https://github.com/topics/leaflet-velocity), [`openwatersio`](https://github.com/openwatersio), and [`erddap-leaflet-velocity-demo`](https://github.com/IrishMarineInstitute/erddap-leaflet-velocity-demo):
- **Windy.com Style Particle Streamlines:** Animated GPU-accelerated ocean current streamlines that continuously flow across the map in real time.
- **Directional Velocity Barbs:** Rotating arrow indicators showing drift bearing and velocity in km/h.
- **OpenSeaMap Seamarks Layer:** Overlays navigational buoys, lighthouses, sector beacons, and shallow shoal hazards.
- **ESRI Ocean Bathymetry Basemap:** Detailed GEBCO/NOAA submarine contours for inspecting the continental shelf break.
- **Live RainViewer Doppler Radar:** Live coastal rain radar and cloud squall overlay.
- **Marine Protected Areas (MPAs):** Polygons for Gulf of Mannar, Malvan, Gulf of Kutch, and Gahirmatha with legal restrictions and statutory warnings under the Wildlife Protection Act and state Marine Fishing Regulation Acts (adapted from [`underbluewaters/marinemap`](https://github.com/underbluewaters/marinemap)).

### 2. ⚡ Complete Weather & Marine Engine (Adapted from [`andrewcourtice/ocula`](https://github.com/andrewcourtice/ocula))
- **3 Dynamic Themes:**
  1. `☀️ Ocula Sky Day`: Neumorphic, clean light theme with ocean blue `#0284c7`.
  2. `🌙 Ocula Oceanic Dark`: Deep abyss navy `#071322` with glowing cyan `#38bdf8`.
  3. `⚡ Tactical Radar Cockpit`: Cyber-GIS dark `#030712` with emerald radar phosphor `#10b981`.
- **Astronomical Tides Engine:**
  - Calibrated with Survey of India & NIO harmonic constituents ($M_2, S_2, K_1, O_1$).
  - High & Low tide extreme observation cards with formatted IST times, elevations, and clearance tags.
  - Harbor Bar Navigational Keel Clearance warning (bar depth vs trawler draft).
  - 48-Hour smooth continuous spline tide elevation curve with gradient fill and Mean Sea Level (MSL) line.
- **48-Hour Hourly Marine Forecast:**
  - Multi-series interactive chart plotting wave height, swell, and wind gusts with the **INCOIS 2.5m Red Alert threshold line**.
  - Horizontal hourly observation cards with weather pictograms and safety badges.
- **Live Doppler Radar & Satellite Playback:**
  - Interactive RainViewer radar playback frame with dBZ precipitation reflectivity scale and skipper directives.

### 3. 🤖 Collaborative Multi-Agent System (ORCA Engine)
Implemented in `agent_core.py`:
1. **SupervisorAgent:** Natural language intent decomposition & multilingual parsing (English, Hindi, Tamil) for species, port, vessel class, and departure window.
2. **OceanDataDiscoveryAgent:** Queries real-time Open-Meteo telemetry and simulates ISRO Oceansat-3 chlorophyll-$a$ proxies.
3. **HazardRiskAgent:** Strict deterministic evaluation of physical safety thresholds:
   - Swell wave height $> 2.5\text{ m} \implies$ **Immediate NO-GO** (INCOIS High Wave Red Alert)
   - Wind speed $> 45\text{ km/h} \implies$ **Immediate NO-GO** (IMD Squall Warning)
   - Distance to IMBL $< 10\text{ nm} \implies$ Border security breach danger
4. **GeoRoutingAgent:** Selects highest-probability PFZ hotspots, calculates fuel-optimized rhumb-line waypoints, and computes diesel savings.
5. **ExplainableSynthesisAgent:** Generates plain-language skipper advisories in **English**, **Hindi (हिन्दी)**, and **Tamil (தமிழ்)** with numeric rule audit logs.

### 4. 🚨 Emergency Shore Guard & Mayday SOS Beacon
- Comprehensive 24x7 emergency contacts for all 7 major Indian maritime ports:
  - Indian Coast Guard (ICG Toll-Free: **1554**, VHF Ch 16 / Ch 67)
  - Coastal Marine Police (**1093**)
  - State Disaster Management (**1070 / 1077**)
  - Sea Ambulance (**108**)
- Interactive Mayday SOS Distress Beacon generator formatted for IMO/ICG VHF DSC Channel 70 with one-click simulated broadcast.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/FishingFriend.git
cd FishingFriend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🧪 Testing & Verification

Run the automated test suite:
```bash
# Run Unit Tests
python test_fishingfriend.py

# Run Full End-to-End System Tests
python run_system_tests.py
```

---

## 📁 Repository Structure

```text
├── FishingFriend/
│   ├── app.py               # Main Streamlit Tactical Cockpit & UI
│   ├── agent_core.py        # ORCA Multi-Agent Pipeline (5 Collaborative Agents)
│   ├── marine_tools.py      # Marine physics, Open-Meteo telemetry, tides, & routing
│   └── requirements.txt     # Python dependency specifications
├── app.py                   # Root launcher script
├── agent_core.py            # Root re-export
├── marine_tools.py          # Root re-export
├── run_system_tests.py      # End-to-end integration test suite (6 test suites)
├── test_fishingfriend.py    # Unit test suite (9 test suites)
├── implementation_plan.md   # System architectural design document
├── requirements.txt         # Core dependencies
└── README.md                # Project documentation
```

---

## 🤝 Open-Source Acknowledgements
- [`leaflet-velocity`](https://github.com/topics/leaflet-velocity) & [`IrishMarineInstitute/erddap-leaflet-velocity-demo`](https://github.com/IrishMarineInstitute/erddap-leaflet-velocity-demo) for animated vector flow concepts.
- [`andrewcourtice/ocula`](https://github.com/andrewcourtice/ocula) for PWA weather UI, harmonic tide modeling, and radar playback architecture.
- [`underbluewaters/marinemap`](https://github.com/underbluewaters/marinemap) for marine spatial planning and protected area boundaries.
- [`OpenSeaMap`](http://www.openseamap.org/) and [`Open-Meteo`](https://open-meteo.com/) for open oceanographic telemetry.

---

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for details.
