"""
Comprehensive Unit & Integration Test Suite for FishingFriend
SIH26176 / sih_176: ORCA Marine Ecosystem Reasoning with Collaborative Agents
"""

import unittest
from FishingFriend.marine_tools import (
    INDIAN_PORTS,
    PortLocation,
    OceanTelemetry,
    HazardEvaluation,
    fetch_ocean_telemetry,
    evaluate_maritime_safety,
    discover_pfz_zones,
    calculate_optimal_marine_route,
    check_nearest_imbl
)
from FishingFriend.agent_core import (
    MultiAgentOrchestrator,
    SupervisorAgent,
    OceanDataDiscoveryAgent,
    HazardRiskAgent,
    GeoRoutingAgent,
    ExplainableSynthesisAgent
)

class TestMarinePhysicsAndTools(unittest.TestCase):

    def test_indian_ports_coverage(self):
        self.assertIn("kochi", INDIAN_PORTS)
        self.assertIn("veraval", INDIAN_PORTS)
        self.assertIn("chennai", INDIAN_PORTS)
        self.assertIn("mangalore", INDIAN_PORTS)
        self.assertIn("visakhapatnam", INDIAN_PORTS)
        self.assertIn("thoothukudi", INDIAN_PORTS)
        self.assertIn("porbandar", INDIAN_PORTS)

    def test_live_telemetry_fetch(self):
        port = INDIAN_PORTS["kochi"]
        telemetry = fetch_ocean_telemetry(port.lat, port.lon)
        self.assertIsInstance(telemetry, OceanTelemetry)
        self.assertGreater(telemetry.wave_height, 0.0)
        self.assertGreater(telemetry.sea_surface_temperature, 15.0)
        self.assertGreater(telemetry.wind_speed, 0.0)
        self.assertGreater(telemetry.chlorophyll_proxy, 0.0)

    def test_deterministic_safety_guardrails_pass(self):
        calm_telemetry = OceanTelemetry(
            lat=9.96, lon=76.24, timestamp="test",
            wave_height=1.0, wave_direction=240.0, wave_period=6.0,
            swell_wave_height=0.8, swell_wave_period=7.0,
            ocean_current_velocity=1.0, ocean_current_direction=180.0,
            sea_surface_temperature=28.0, chlorophyll_proxy=0.6,
            air_temperature=28.0, wind_speed=15.0, wind_direction=270.0,
            wind_gusts=20.0, weather_code=1, weather_description="Clear",
            is_live=True
        )
        port = INDIAN_PORTS["kochi"]
        eval_res = evaluate_maritime_safety(calm_telemetry, port)
        self.assertEqual(eval_res.status, "SAFE_GO")
        self.assertEqual(eval_res.incois_alert_level, "GREEN_NORMAL")
        self.assertEqual(eval_res.imd_wind_alert, "NORMAL")

    def test_deterministic_safety_guardrails_danger_swell(self):
        # Swell > 2.5m MUST trigger immediate DANGER_NO_GO as per INCOIS protocol
        rough_telemetry = OceanTelemetry(
            lat=9.96, lon=76.24, timestamp="test",
            wave_height=2.8, wave_direction=240.0, wave_period=9.0,
            swell_wave_height=2.85, swell_wave_period=11.0, # > 2.5m trigger
            ocean_current_velocity=1.2, ocean_current_direction=180.0,
            sea_surface_temperature=27.5, chlorophyll_proxy=0.8,
            air_temperature=27.0, wind_speed=20.0, wind_direction=270.0,
            wind_gusts=28.0, weather_code=61, weather_description="Rain",
            is_live=True
        )
        port = INDIAN_PORTS["kochi"]
        eval_res = evaluate_maritime_safety(rough_telemetry, port)
        self.assertEqual(eval_res.status, "DANGER_NO_GO")
        self.assertEqual(eval_res.incois_alert_level, "RED_HIGH_WAVE")

    def test_deterministic_safety_guardrails_danger_wind(self):
        # Wind > 45 km/h MUST trigger DANGER_NO_GO
        squall_telemetry = OceanTelemetry(
            lat=9.96, lon=76.24, timestamp="test",
            wave_height=1.5, wave_direction=240.0, wave_period=6.0,
            swell_wave_height=1.2, swell_wave_period=7.0,
            ocean_current_velocity=1.0, ocean_current_direction=180.0,
            sea_surface_temperature=28.0, chlorophyll_proxy=0.6,
            air_temperature=28.0, wind_speed=52.0, wind_direction=270.0, # > 45 km/h trigger
            wind_gusts=68.0, weather_code=95, weather_description="Squall",
            is_live=True
        )
        port = INDIAN_PORTS["kochi"]
        eval_res = evaluate_maritime_safety(squall_telemetry, port)
        self.assertEqual(eval_res.status, "DANGER_NO_GO")
        self.assertEqual(eval_res.imd_wind_alert, "GALE_STORM")

    def test_imbl_proximity_detection(self):
        # Near Sri Lanka border in Palk Strait
        border_lat, border_lon = 9.20, 79.52
        name, dist = check_nearest_imbl(border_lat, border_lon)
        self.assertIn("Sri Lanka", name)
        self.assertLess(dist, 10.0) # Within 10 km

    def test_pfz_discovery_and_routing(self):
        port = INDIAN_PORTS["veraval"]
        telemetry = fetch_ocean_telemetry(port.lat, port.lon)
        zones = discover_pfz_zones(port, telemetry)
        self.assertGreaterEqual(len(zones), 3)
        self.assertGreater(zones[0].fish_density_score, 70)

        route = calculate_optimal_marine_route(port, zones[0], telemetry)
        self.assertGreater(len(route.waypoints), 3)
        self.assertGreater(route.total_distance_nm, 5.0)
        self.assertGreater(route.fuel_burn_liters, 0.0)


class TestAgentCollaborativePipeline(unittest.TestCase):

    def setUp(self):
        self.orchestrator = MultiAgentOrchestrator()

    def test_supervisor_language_detection(self):
        sup = SupervisorAgent()
        
        # English
        intent_en, _ = sup.process("Can we sail from Kochi for Yellowfin Tuna?")
        self.assertEqual(intent_en.detected_language, "en")
        self.assertEqual(intent_en.port_id, "kochi")
        self.assertEqual(intent_en.target_species, "Tuna")

        # Hindi
        intent_hi, _ = sup.process("क्या कल सुबह वेरावल से समुद्र में जाना सुरक्षित है?")
        self.assertEqual(intent_hi.detected_language, "hi")
        self.assertEqual(intent_hi.port_id, "veraval")

        # Tamil
        intent_ta, _ = sup.process("கொச்சியிலிருந்து இன்று சூரை மீன் பிடிக்க கடலுக்குச் செல்லலாமா?")
        self.assertEqual(intent_ta.detected_language, "ta")
        self.assertEqual(intent_ta.port_id, "kochi")

    def test_full_pipeline_orchestration(self):
        res = self.orchestrator.run_pipeline("Can we sail from Chennai for Pomfret?", "chennai")
        self.assertEqual(res.port.id, "chennai")
        self.assertIn(res.safety.status, ["SAFE_GO", "CAUTION_CONDITIONAL", "DANGER_NO_GO"])
        self.assertEqual(len(res.agent_logs), 5)
        self.assertIn("english", res.advisory.__dict__)
        self.assertIn("hindi", res.advisory.__dict__)
        self.assertIn("tamil", res.advisory.__dict__)
        self.assertGreater(len(res.all_pfzs), 0)

if __name__ == "__main__":
    unittest.main()
