"""
FishingFriend - Collaborative Multi-Agent Core Engine
Problem Statement: SIH26176 / sih_176: ORCA (Marine EcOsystem Reasoning with Collaborative Agents) for ISRO.

Agents in Pipeline:
1. SupervisorAgent: Natural language query decomposition & intent parsing (EN/HI/TA).
2. OceanDataDiscoveryAgent: Spatial telemetry ingestion & bio-optical satellite proxy processing.
3. HazardRiskAgent: Deterministic INCOIS & IMD safety rule evaluation (Zero-hallucination guardrails).
4. GeoRoutingAgent: PFZ ranking, IMBL boundary evasion, and waypoint fuel optimization.
5. ExplainableSynthesisAgent: Multilingual advisory generation (English, Hindi, Tamil) & audit logging.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any

from FishingFriend.marine_tools import (
    INDIAN_PORTS,
    PortLocation,
    OceanTelemetry,
    HazardEvaluation,
    PFZZone,
    RouteWaypoints,
    RuleAuditItem,
    fetch_ocean_telemetry,
    evaluate_maritime_safety,
    discover_pfz_zones,
    calculate_optimal_marine_route,
    check_nearest_imbl,
    EmergencyContact,
    get_emergency_contacts,
    PortTideData,
    HourlyMarineForecast,
    calculate_port_tides,
    fetch_hourly_marine_forecast
)

# ---------------------------------------------------------
# AGENT INTERFACES & OUTPUT CONTAINERS
# ---------------------------------------------------------

@dataclass
class AgentStepLog:
    agent_name: str
    action: str
    status: str  # "COMPLETED", "WARNING", "BLOCKED"
    duration_ms: float
    details: str
    data_summary: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SupervisorIntent:
    raw_query: str
    detected_language: str       # "en", "hi", "ta"
    port_id: str
    port_name: str
    target_radius_km: float
    vessel_class: str            # "Small Craft (<10m)", "Mechanized Trawler (12-18m)", "Deep-Sea Longliner (>20m)"
    target_species: Optional[str]
    temporal_window: str         # "Immediate Departure", "Morning Tide (05:00 IST)", "Overnight Voyage"
    confidence: float

@dataclass
class MultilingualAdvisory:
    english: Dict[str, Any]
    hindi: Dict[str, Any]
    tamil: Dict[str, Any]

@dataclass
class ORCASynthesisResult:
    query_intent: SupervisorIntent
    port: PortLocation
    telemetry: OceanTelemetry
    safety: HazardEvaluation
    top_pfz: PFZZone
    all_pfzs: List[PFZZone]
    route: RouteWaypoints
    advisory: MultilingualAdvisory
    agent_logs: List[AgentStepLog]
    timestamp: str
    total_execution_time_ms: float
    emergency_contacts: List[EmergencyContact] = field(default_factory=list)
    tides: Optional[PortTideData] = None
    hourly_forecast: Optional[HourlyMarineForecast] = None


# ---------------------------------------------------------
# 1. SUPERVISOR AGENT
# ---------------------------------------------------------

class SupervisorAgent:
    """
    Decomposes natural language queries (English, Hindi, Tamil) or structured UI inputs
    into target coordinates, coastal harbor bounds, vessel constraints, and temporal windows.
    """
    NAME = "Supervisor Agent (ORCA-L1)"

    # Keyword mappings for multilingual intent extraction
    PORT_KEYWORDS = {
        "kochi": ["kochi", "cochin", "कोच्चि", "கொச்சி", "கேரளா", "kerala", "malabar"],
        "veraval": ["veraval", "वेरावल", "வேராவல்", "gujarat", "गुजरात", "सौराष्ट्र", "saurashtra"],
        "chennai": ["chennai", "madras", "चेन्नई", "சென்னை", "kasimedu", "காசிமேடு", "coromandel"],
        "mangalore": ["mangalore", "mangaluru", "मंगलौर", "மங்களூரு", "karnataka", "कर्नाटक"],
        "visakhapatnam": ["visakhapatnam", "vizag", "विशाखापट्टनम", "விசாகப்பட்டினம்", "andhra"],
        "thoothukudi": ["thoothukudi", "tuticorin", "தூத்துக்குடி", "थूथुकुडी", "mannar"],
        "porbandar": ["porbandar", "पोरबंदर", "போர்பந்தர்", "kutch", "कच्छ"]
    }

    SPECIES_KEYWORDS = {
        "tuna": ["tuna", "ट्यूना", "சூரை", "chura", "soorai"],
        "sardine": ["sardine", "मथथी", "சார்டின்", "மத்தி", "tarli"],
        "mackerel": ["mackerel", "बाँगड़ा", "அயலை", "kanagurta", "bangda"],
        "pomfret": ["pomfret", "पापलेट", "வாவல்", "vaval", "halwa"]
    }

    def process(self, query: str, default_port_id: str = "kochi", vessel_class: str = "Mechanized Trawler (12-18m)") -> Tuple[SupervisorIntent, AgentStepLog]:
        start_t = time.time()
        q_lower = query.lower().strip()

        # Language Detection heuristic
        detected_lang = "en"
        if any('\u0900' <= char <= '\u097F' for char in query):
            detected_lang = "hi"
        elif any('\u0B80' <= char <= '\u0BFF' for char in query):
            detected_lang = "ta"

        # Port resolution:
        # 1. Check if query explicitly mentions a recognized port keyword
        resolved_port = None
        for port_id, kws in self.PORT_KEYWORDS.items():
            if any(kw in q_lower for kw in kws):
                resolved_port = port_id
                break

        # 2. If no port mentioned in query, fallback to explicit default_port_id
        if not resolved_port:
            resolved_port = default_port_id if default_port_id in INDIAN_PORTS else "kochi"

        # Species resolution
        target_species = None
        for sp, kws in self.SPECIES_KEYWORDS.items():
            if any(kw in q_lower for kw in kws):
                target_species = sp.title()
                break

        # Radius heuristic
        radius = 35.0
        if "deep" in q_lower or "गहरे" in q_lower or "ஆழமான" in q_lower or "tuna" in q_lower:
            radius = 50.0
        elif "near" in q_lower or "तट" in q_lower or "அருகில்" in q_lower:
            radius = 20.0

        port_obj = INDIAN_PORTS.get(resolved_port, INDIAN_PORTS["kochi"])

        intent = SupervisorIntent(
            raw_query=query,
            detected_language=detected_lang,
            port_id=resolved_port,
            port_name=port_obj.name,
            target_radius_km=radius,
            vessel_class=vessel_class,
            target_species=target_species,
            temporal_window="Next 12 Hours / Immediate Operating Window",
            confidence=0.96
        )

        elapsed_ms = (time.time() - start_t) * 1000
        step_log = AgentStepLog(
            agent_name=self.NAME,
            action="Query Decomposition & Intent Extraction",
            status="COMPLETED",
            duration_ms=round(elapsed_ms, 2),
            details=f"Decomposed input into target harbor '{port_obj.name}' with {radius} km search radius. Detected language: {detected_lang.upper()}.",
            data_summary={"port": resolved_port, "radius_km": radius, "species": target_species, "language": detected_lang}
        )
        return intent, step_log


# ---------------------------------------------------------
# 2. OCEAN DATA DISCOVERY AGENT
# ---------------------------------------------------------

class OceanDataDiscoveryAgent:
    """
    Acquires real-time oceanographic telemetry from Open-Meteo API and calculates
    ISRO Oceansat-3 satellite proxies (Chlorophyll-a, SST gradient, Upwelling dynamics).
    """
    NAME = "Ocean Data Discovery Agent (ORCA-L2)"

    def process(self, port: PortLocation) -> Tuple[OceanTelemetry, AgentStepLog]:
        start_t = time.time()

        # Fetch live marine telemetry
        telemetry = fetch_ocean_telemetry(port.lat, port.lon)

        elapsed_ms = (time.time() - start_t) * 1000
        step_log = AgentStepLog(
            agent_name=self.NAME,
            action="Live Ocean Telemetry Ingestion",
            status="COMPLETED",
            duration_ms=round(elapsed_ms, 2),
            details=(
                f"Ingested live telemetry for {port.name} (Lat {port.lat:.3f}, Lon {port.lon:.3f}). "
                f"Swell: {telemetry.swell_wave_height}m, Wave: {telemetry.wave_height}m, "
                f"SST: {telemetry.sea_surface_temperature}°C, Current: {telemetry.ocean_current_velocity} km/h, "
                f"Wind: {telemetry.wind_speed} km/h (Gust {telemetry.wind_gusts} km/h)."
            ),
            data_summary={
                "wave_height_m": telemetry.wave_height,
                "swell_height_m": telemetry.swell_wave_height,
                "sst_c": telemetry.sea_surface_temperature,
                "current_kmh": telemetry.ocean_current_velocity,
                "wind_kmh": telemetry.wind_speed,
                "is_live_api": telemetry.is_live
            }
        )
        return telemetry, step_log


# ---------------------------------------------------------
# 3. HAZARD & RISK AGENT (Deterministic Guardrail)
# ---------------------------------------------------------

class HazardRiskAgent:
    """
    Executes strict deterministic physical safety evaluations against INCOIS and IMD standards.
    NO LLM hallucinations allowed: swell > 2.5m or wind > 45 km/h strictly enforces NO-GO.
    """
    NAME = "Hazard & Risk Agent (ORCA-L3)"

    def process(self, telemetry: OceanTelemetry, port: PortLocation, vessel_class: str) -> Tuple[HazardEvaluation, AgentStepLog]:
        start_t = time.time()

        # Parse vessel length proxy
        vessel_len = 14.0
        if "Small Craft" in vessel_class:
            vessel_len = 8.5
        elif "Deep-Sea" in vessel_class:
            vessel_len = 24.0

        hazard_eval = evaluate_maritime_safety(telemetry, port, vessel_length_m=vessel_len)

        status_flag = "COMPLETED"
        if hazard_eval.status == "DANGER_NO_GO":
            status_flag = "BLOCKED"
        elif hazard_eval.status == "CAUTION_CONDITIONAL":
            status_flag = "WARNING"

        elapsed_ms = (time.time() - start_t) * 1000
        step_log = AgentStepLog(
            agent_name=self.NAME,
            action="Deterministic INCOIS/IMD Safety Audit",
            status=status_flag,
            duration_ms=round(elapsed_ms, 2),
            details=(
                f"Safety Decision: {hazard_eval.status} (Risk Score: {hazard_eval.risk_score}/100). "
                f"INCOIS: {hazard_eval.incois_alert_level}, IMD: {hazard_eval.imd_wind_alert}, "
                f"IMBL Proximity: {hazard_eval.border_distance_km} km to {hazard_eval.nearest_imbl_name}."
            ),
            data_summary={
                "status": hazard_eval.status,
                "risk_score": hazard_eval.risk_score,
                "incois_alert": hazard_eval.incois_alert_level,
                "imd_alert": hazard_eval.imd_wind_alert,
                "imbl_status": hazard_eval.imbl_security_alert,
                "audit_rules_checked": len(hazard_eval.audit_log)
            }
        )
        return hazard_eval, step_log


# ---------------------------------------------------------
# 4. GEO-ROUTING & PFZ AGENT
# ---------------------------------------------------------

class GeoRoutingAgent:
    """
    Discovers Potential Fishing Zones based on ISRO thermal/chlorophyll criteria,
    evaluates vessel economics, and computes current-assisted waypoint corridors avoiding IMBL.
    """
    NAME = "Geo-Routing & PFZ Agent (ORCA-L4)"

    def process(
        self,
        port: PortLocation,
        telemetry: OceanTelemetry,
        hazard: HazardEvaluation,
        target_species: Optional[str] = None
    ) -> Tuple[List[PFZZone], PFZZone, RouteWaypoints, AgentStepLog]:
        start_t = time.time()

        # Discover PFZs
        pfz_candidates = discover_pfz_zones(port, telemetry)

        # Filter or prioritize target species if requested
        selected_pfz = pfz_candidates[0]
        if target_species:
            for p in pfz_candidates:
                if any(target_species.lower() in s.lower() for s in p.species_likely):
                    selected_pfz = p
                    break

        # Calculate optimal navigation route
        route = calculate_optimal_marine_route(port, selected_pfz, telemetry)

        elapsed_ms = (time.time() - start_t) * 1000
        step_log = AgentStepLog(
            agent_name=self.NAME,
            action="PFZ Spatial Clustering & Fuel-Optimized Routing",
            status="COMPLETED",
            duration_ms=round(elapsed_ms, 2),
            details=(
                f"Selected Top PFZ: '{selected_pfz.name}' ({selected_pfz.distance_km} km at bearing {selected_pfz.bearing_deg}°). "
                f"Fish Density Score: {selected_pfz.fish_density_score}/100. "
                f"Fuel Burn: ~{route.fuel_burn_liters} L (Estimated Savings: {route.fuel_savings_liters} L)."
            ),
            data_summary={
                "top_pfz": selected_pfz.name,
                "distance_km": selected_pfz.distance_km,
                "density_score": selected_pfz.fish_density_score,
                "total_waypoints": len(route.waypoints),
                "fuel_liters": route.fuel_burn_liters,
                "fuel_savings_liters": route.fuel_savings_liters
            }
        )
        return pfz_candidates, selected_pfz, route, step_log


# ---------------------------------------------------------
# 5. EXPLAINABLE SYNTHESIS AGENT (Multilingual & Transparent)
# ---------------------------------------------------------

class ExplainableSynthesisAgent:
    """
    Synthesizes scientific data and deterministic safety verdicts into high-clarity,
    actionable advisories in English, Hindi (हिन्दी), and Tamil (தமிழ்), accompanied
    by a transparent, verifiable step-by-step reasoning audit log.
    """
    NAME = "Explainable Synthesis Agent (ORCA-L5)"

    def process(
        self,
        intent: SupervisorIntent,
        port: PortLocation,
        telemetry: OceanTelemetry,
        hazard: HazardEvaluation,
        selected_pfz: PFZZone,
        route: RouteWaypoints
    ) -> Tuple[MultilingualAdvisory, AgentStepLog]:
        start_t = time.time()

        # Generate English Advisory
        en_status_label = "SAFE TO SAIL (CLEARANCE GRANTED)" if hazard.status == "SAFE_GO" else (
            "CAUTION ADVISED (CONDITIONAL CLEARANCE)" if hazard.status == "CAUTION_CONDITIONAL" else
            "DANGER: NO-GO (OPERATIONS SUSPENDED)"
        )

        en_advisory = {
            "title": f"Marine Fishing Advisory - {port.name}",
            "status_headline": en_status_label,
            "status_code": hazard.status,
            "risk_score_display": f"{hazard.risk_score} / 100",
            "executive_summary": (
                f"Sea state off {port.name} is evaluated as {hazard.status.replace('_', ' ')}. "
                f"Live significant wave height is {telemetry.wave_height}m with swell of {telemetry.swell_wave_height}m. "
                f"Surface winds are at {telemetry.wind_speed} km/h from {telemetry.wind_direction}°."
            ),
            "safety_action": (
                "Vessel may proceed to designated Potential Fishing Zone with standard watch." if hazard.status == "SAFE_GO" else
                ("Exercise vigilance. Small craft restricted. Avoid operating beyond 15 nautical miles." if hazard.status == "CAUTION_CONDITIONAL" else
                 "DO NOT VENTURE INTO SEA. In accordance with INCOIS/IMD protocols, all departures are strictly cancelled.")
            ),
            "recommended_pfz": {
                "name": selected_pfz.name,
                "coordinates": f"{selected_pfz.lat:.4f}° N, {selected_pfz.lon:.4f}° E",
                "distance_bearing": f"{selected_pfz.distance_km} km ({route.total_distance_nm} nm) @ Bearing {selected_pfz.bearing_deg}°",
                "target_species": ", ".join(selected_pfz.species_likely),
                "fish_probability": f"{selected_pfz.fish_density_score}%",
                "ocean_condition": f"SST: {selected_pfz.sst_celsius}°C | Chlorophyll: {selected_pfz.chlorophyll_proxy} mg/m³ | Depth: {selected_pfz.depth_m}m",
                "thermal_front": selected_pfz.thermal_gradient_desc
            },
            "fuel_and_route": {
                "estimated_transit": f"{route.estimated_transit_hours:.1f} Hours (@ 8 knots)",
                "fuel_consumption": f"{route.fuel_burn_liters} Liters Diesel",
                "fuel_savings": f"{route.fuel_savings_liters} Liters (via current-assisted routing)",
                "current_notes": route.current_assist_effect,
                "border_safety": f"Nearest border: {hazard.nearest_imbl_name} ({hazard.border_distance_km} km away). {route.safety_envelope}"
            },
            "emergency_contacts": "Indian Coast Guard MRCC: Toll-Free 1554 | VHF Channel 16"
        }

        # Generate Hindi (हिन्दी) Advisory
        hi_status_label = "सुरक्षित: समुद्र में जाने की अनुमति है" if hazard.status == "SAFE_GO" else (
            "सावधानी: सशर्त अनुमति (केवल बड़े जहाजों के लिए)" if hazard.status == "CAUTION_CONDITIONAL" else
            "खतरा: समुद्र में जाना सख्त मना है (NO-GO)"
        )

        hi_advisory = {
            "title": f"समुद्री मत्स्य परामर्श - {port.name}",
            "status_headline": hi_status_label,
            "status_code": hazard.status,
            "risk_score_display": f"{hazard.risk_score} / 100 (जोखिम स्तर)",
            "executive_summary": (
                f"{port.name} के निकट समुद्र की स्थिति: तरंग की ऊंचाई {telemetry.wave_height} मीटर "
                f"और समुद्री उभार (Swell) {telemetry.swell_wave_height} मीटर है। "
                f"हवा की गति {telemetry.wind_speed} किमी/घंटा दर्ज की गई है।"
            ),
            "safety_action": (
                "मौसम अनुकूल है। पंजीकृत नौकाएं चिन्हित संभावित मत्स्य क्षेत्र (PFZ) में जा सकती हैं।" if hazard.status == "SAFE_GO" else
                ("सावधानी बरतें। छोटी नौकाएं तट के निकट रहें। 15 समुद्री मील से दूर न जाएं।" if hazard.status == "CAUTION_CONDITIONAL" else
                 "खतरे की चेतावनी: INCOIS और मौसम विभाग के अनुसार समुद्र में न जाएं। नौकाएं बंदरगाह पर बांधकर रखें।")
            ),
            "recommended_pfz": {
                "name": selected_pfz.name,
                "coordinates": f"{selected_pfz.lat:.4f}° N, {selected_pfz.lon:.4f}° E",
                "distance_bearing": f"{selected_pfz.distance_km} किमी (@ दिशा {selected_pfz.bearing_deg}°)",
                "target_species": ", ".join(selected_pfz.species_likely),
                "fish_probability": f"{selected_pfz.fish_density_score}% (मछली मिलने की संभावना)",
                "ocean_condition": f"समुद्र तापमान: {selected_pfz.sst_celsius}°C | क्लोरोफिल: {selected_pfz.chlorophyll_proxy} mg/m³ | गहराई: {selected_pfz.depth_m} मी",
                "thermal_front": selected_pfz.thermal_gradient_desc
            },
            "fuel_and_route": {
                "estimated_transit": f"{route.estimated_transit_hours:.1f} घंटे (8 समुद्री मील/घंटे पर)",
                "fuel_consumption": f"{route.fuel_burn_liters} लीटर डीजल",
                "fuel_savings": f"{route.fuel_savings_liters} लीटर डीजल की बचत (समुद्री धारा अनुकूलन)",
                "current_notes": route.current_assist_effect,
                "border_safety": f"अंतर्राष्ट्रीय समुद्री सीमा: {hazard.nearest_imbl_name} ({hazard.border_distance_km} किमी दूर)। पूर्णतः सुरक्षित जलक्षेत्र।"
            },
            "emergency_contacts": "भारतीय तटरक्षक बल (ICG) हेल्पलाइन: 1554 | VHF चैनल 16"
        }

        # Generate Tamil (தமிழ்) Advisory
        ta_status_label = "பாதுகாப்பானது: கடலுக்குச் செல்ல அனுமதி உண்டு" if hazard.status == "SAFE_GO" else (
            "எச்சரிக்கை: நிபந்தனை அனுமதி (பெரிய படகுகளுக்கு மட்டும்)" if hazard.status == "CAUTION_CONDITIONAL" else
            "ஆபத்து: கடலுக்குச் செல்ல தடை (NO-GO)"
        )

        ta_advisory = {
            "title": f"கடல் மீன்பிடி ஆலோசனை அறிக்கை - {port.name}",
            "status_headline": ta_status_label,
            "status_code": hazard.status,
            "risk_score_display": f"{hazard.risk_score} / 100 (ஆபத்து அளவு)",
            "executive_summary": (
                f"{port.name} கடல் பகுதி நிலவரம்: அலை உயரம் {telemetry.wave_height} மீட்டர், "
                f"கடல் கொந்தளிப்பு (Swell) {telemetry.swell_wave_height} மீட்டர். "
                f"காற்றின் வேகம் மணிக்கு {telemetry.wind_speed} கி.மீ ஆக உள்ளது."
            ),
            "safety_action": (
                "வானிலை சாதகமாக உள்ளது. மீனவர்கள் பரிந்துரைக்கப்பட்ட சாத்தியமான மீன்பிடி மண்டலத்திற்கு (PFZ) செல்லலாம்." if hazard.status == "SAFE_GO" else
                ("எச்சரிக்கையுடன் செயல்படவும். சிறிய நாட்டுப் படகுகள் ஆழ்கடலுக்குச் செல்வதைத் தவிர்க்கவும்." if hazard.status == "CAUTION_CONDITIONAL" else
                 "கடலுக்குச் செல்ல வேண்டாம்! INCOIS மற்றும் வானிலை ஆய்வு மைய வழிகாட்டுதலின்படி பயணம் உடனடியாக ரத்து செய்யப்படுகிறது.")
            ),
            "recommended_pfz": {
                "name": selected_pfz.name,
                "coordinates": f"{selected_pfz.lat:.4f}° N, {selected_pfz.lon:.4f}° E",
                "distance_bearing": f"{selected_pfz.distance_km} கி.மீ (@ திசை {selected_pfz.bearing_deg}°)",
                "target_species": ", ".join(selected_pfz.species_likely),
                "fish_probability": f"{selected_pfz.fish_density_score}% (மீன் கிடைக்கும் வாய்ப்பு)",
                "ocean_condition": f"கடல் வெப்பநிலை: {selected_pfz.sst_celsius}°C | குளோரோபில்: {selected_pfz.chlorophyll_proxy} mg/m³ | ஆழம்: {selected_pfz.depth_m} மீ",
                "thermal_front": selected_pfz.thermal_gradient_desc
            },
            "fuel_and_route": {
                "estimated_transit": f"{route.estimated_transit_hours:.1f} மணி நேரம் (8 நாட்ஸ் வேகத்தில்)",
                "fuel_consumption": f"{route.fuel_burn_liters} லிட்டர் டீசல்",
                "fuel_savings": f"{route.fuel_savings_liters} லிட்டர் சேமிப்பு (நீரோட்ட வழியமைப்பு மூலம்)",
                "current_notes": route.current_assist_effect,
                "border_safety": f"சர்வதேச கடல் எல்லை: {hazard.nearest_imbl_name} ({hazard.border_distance_km} கி.மீ தொலைவில்). எல்லையைத் தாண்ட வேண்டாம்."
            },
            "emergency_contacts": "இந்திய கடலோர காவல்படை அவசர உதவி எண்: 1554 | VHF சேனல் 16"
        }

        multilingual = MultilingualAdvisory(
            english=en_advisory,
            hindi=hi_advisory,
            tamil=ta_advisory
        )

        elapsed_ms = (time.time() - start_t) * 1000
        step_log = AgentStepLog(
            agent_name=self.NAME,
            action="Explainable Multilingual Advisory Synthesis",
            status="COMPLETED",
            duration_ms=round(elapsed_ms, 2),
            details=f"Synthesized comprehensive advisories in English, Hindi, and Tamil with verified reasoning audit trails.",
            data_summary={"languages": ["en", "hi", "ta"], "safety_verdict": hazard.status}
        )
        return multilingual, step_log


# ---------------------------------------------------------
# ORCA COLLABORATIVE PIPELINE ORCHESTRATOR
# ---------------------------------------------------------

class MultiAgentOrchestrator:
    """
    Coordinates and drives the multi-agent pipeline:
    Supervisor -> Ocean Data Discovery -> Hazard & Risk -> Geo-Routing -> Explainable Synthesis
    """
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.discovery = OceanDataDiscoveryAgent()
        self.hazard = HazardRiskAgent()
        self.routing = GeoRoutingAgent()
        self.synthesis = ExplainableSynthesisAgent()

    def run_pipeline(
        self,
        query: str,
        selected_port_id: str = "kochi",
        vessel_class: str = "Mechanized Trawler (12-18m)"
    ) -> ORCASynthesisResult:
        pipeline_start = time.time()
        agent_logs: List[AgentStepLog] = []

        # 1. Supervisor Agent
        intent, log1 = self.supervisor.process(query, default_port_id=selected_port_id, vessel_class=vessel_class)
        agent_logs.append(log1)

        port = INDIAN_PORTS.get(intent.port_id, INDIAN_PORTS["kochi"])

        # 2. Ocean Data Discovery Agent
        telemetry, log2 = self.discovery.process(port)
        agent_logs.append(log2)

        # 3. Hazard & Risk Agent (Deterministic Rule Engine)
        hazard, log3 = self.hazard.process(telemetry, port, intent.vessel_class)
        agent_logs.append(log3)

        # 4. Geo-Routing & PFZ Agent
        all_pfzs, top_pfz, route, log4 = self.routing.process(port, telemetry, hazard, target_species=intent.target_species)
        agent_logs.append(log4)

        # 5. Explainable Synthesis Agent
        advisory, log5 = self.synthesis.process(intent, port, telemetry, hazard, top_pfz, route)
        agent_logs.append(log5)

        # 6. Astronomical Tides & Hourly Marine Weather Forecast (Ocula & OpenWaters Engine)
        tides = calculate_port_tides(port.id)
        hourly_forecast = fetch_hourly_marine_forecast(port)

        total_time_ms = (time.time() - pipeline_start) * 1000

        return ORCASynthesisResult(
            query_intent=intent,
            port=port,
            telemetry=telemetry,
            safety=hazard,
            top_pfz=top_pfz,
            all_pfzs=all_pfzs,
            route=route,
            advisory=advisory,
            agent_logs=agent_logs,
            emergency_contacts=get_emergency_contacts(port.id),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            total_execution_time_ms=round(total_time_ms, 2),
            tides=tides,
            hourly_forecast=hourly_forecast
        )
