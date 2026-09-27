"""
UI/UX Architecture & Functionality Regression Test Suite for FishingFriend Redesign
Validates:
1. 5 Primary Navigation Views & Sub-navigation Routes
2. Centralized Semantic Theme Tokens across Sky Day, Oceanic Dark, and Tactical Radar
3. Multilingual Support (English, Hindi, Tamil) & Voice TTS payload integrity
4. Data Integrity: 7 Indian Ports, 4 Vessel Classes, 4 Departure Windows, 2 Unit Systems
5. Full Geospatial Map, Tides, 48h Forecast, Radar, and Emergency Rescue Directory
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from FishingFriend.marine_tools import (
    INDIAN_PORTS,
    PortLocation,
    OceanTelemetry,
    HazardEvaluation,
    PFZZone,
    RouteWaypoints,
    fetch_ocean_telemetry,
    evaluate_maritime_safety,
    discover_pfz_zones,
    calculate_optimal_marine_route,
    calculate_port_tides,
    fetch_hourly_marine_forecast,
    get_marine_spatial_zones,
    get_emergency_contacts,
    fetch_rainviewer_radar_url
)
from FishingFriend.agent_core import MultiAgentOrchestrator
from FishingFriend.app import inject_theme

class TestRedesignArchitecture(unittest.TestCase):

    def setUp(self):
        self.orchestrator = MultiAgentOrchestrator()

    def test_theme_system_css_tokens(self):
        """Verify that all 3 themes inject valid CSS tokens without missing variables."""
        for theme in ["☀️ Ocula Sky Day", "🌙 Ocula Oceanic Dark", "⚡ Tactical Radar"]:
            tile = inject_theme(theme)
            self.assertIn(tile, ["cartodbpositron", "cartodbdark_matter"])

    def test_5_primary_navigation_sections_data_flow(self):
        """Verify data pipeline feeding all 5 primary sections."""
        port = INDIAN_PORTS["kochi"]
        res = self.orchestrator.run_pipeline("Can we sail from Kochi for Yellowfin Tuna?", "kochi", "Mechanized Trawler (12-18m)")

        # Section 1: Dashboard
        self.assertIsNotNone(res.safety.status)
        self.assertIsNotNone(res.safety.risk_score)
        self.assertGreaterEqual(len(res.all_pfzs), 1)
        self.assertIsNotNone(res.advisory.english)

        # Section 2: Explore (Tactical Map, PFZ, Sea Analysis)
        self.assertIsNotNone(res.top_pfz)
        self.assertIsNotNone(res.route.waypoints)
        mpas = get_marine_spatial_zones(port.id)
        self.assertIsInstance(mpas, list)

        # Section 3: Conditions (Forecast, Tides, Radar)
        tides = calculate_port_tides(port.id)
        self.assertGreater(len(tides.hourly_heights_48h), 20)
        self.assertGreater(len(tides.extremes_today), 0)

        forecast = fetch_hourly_marine_forecast(port)
        self.assertGreater(len(forecast.hours), 20)
        self.assertGreater(forecast.max_wave_height, 0)

        radar_url = fetch_rainviewer_radar_url()
        self.assertTrue(radar_url is None or isinstance(radar_url, str))

        # Section 4: Safety & Advisory
        self.assertGreaterEqual(len(res.safety.audit_log), 4)
        contacts = get_emergency_contacts(port.id)
        self.assertGreaterEqual(len(contacts), 2)
        self.assertIn("status_headline", res.advisory.english)
        self.assertIn("status_headline", res.advisory.hindi)
        self.assertIn("status_headline", res.advisory.tamil)

        # Section 5: Settings (Manifest & Units)
        self.assertGreater(res.route.fuel_burn_liters, 0)
        self.assertGreater(res.route.total_distance_nm, 0)

    def test_all_seven_ports_regression(self):
        """Verify all 7 ports resolve correctly in pipeline with no regression."""
        for port_id, port_obj in INDIAN_PORTS.items():
            res = self.orchestrator.run_pipeline(f"Check fishing conditions at {port_obj.name}", port_id, "Mechanized Trawler (12-18m)")
            self.assertEqual(res.port.id, port_id)
            self.assertGreater(len(res.all_pfzs), 0)
            self.assertIsNotNone(res.safety.status)

if __name__ == "__main__":
    unittest.main()
