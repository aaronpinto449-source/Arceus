"""
ARES Mission Control - Planetary Configuration & Geodetic Standards
"""

from pathlib import Path
from typing import Dict, Any, List

# Base directory paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Mars Geodetic Constants (IAU/IAG Working Group Standards)
MARS_MEAN_RADIUS_KM: float = 3389.5
MARS_EQUATORIAL_RADIUS_KM: float = 3396.2
MARS_POLAR_RADIUS_KM: float = 3376.2
MARS_FLATTENING: float = 0.00589

# Official NASA Space Apps Challenge 2026 Resources
# https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/?tab=resources
SPACE_APPS_2026_RESOURCES: Dict[str, Dict[str, Any]] = {
    "mars_trek": {
        "title": "NASA Jet Propulsion Laboratory (JPL) Mars Trek",
        "url": "https://trek.nasa.gov/mars/",
        "description": "NASA web-based portal for exploration of Mars, showcasing data collected by NASA at various landing sites, including global MOLA, CTX, and HiRISE layers.",
        "category": "Mars Planetary Portal & Tile Services",
        "authority": "NASA JPL / Solar System Treks",
        "is_mars_specific": True
    },
    "usgs_geologic_maps": {
        "title": "USGS-NASA Planetary Geologic Mapping Program",
        "url": "https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars",
        "description": "High-quality standardized geologic map of Mars (SIM 3292) providing stratigraphic terrain and surface material classifications.",
        "category": "Mars Geological Cartography & Surface Material",
        "authority": "USGS Astrogeology Science Center / NASA",
        "is_mars_specific": True
    },
    "curiosity_mount_sharp_route": {
        "title": "Curiosity's Proposed Path up Mount Sharp",
        "url": "https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/",
        "description": "NASA Science mission visual depicting Curiosity's traversal corridor from Bradbury Landing up lower Mount Sharp, illustrating obstacle avoidance through sand dunes and steep slopes.",
        "category": "Mars Traversability Ground Truth & Route Planning",
        "authority": "NASA Science Mission Directorate / JPL",
        "is_mars_specific": True
    },
    "perseverance_raw_images": {
        "title": "NASA Mars Perseverance Raw Images Gallery",
        "url": "https://mars.nasa.gov/mars2020/multimedia/raw-images/",
        "description": "Over 1 million surface point-of-view images captured by the Perseverance rover (Mastcam-Z, Navcam, Hazcam, SuperCam) across Jezero Crater.",
        "category": "Mars Point-of-View Visual Ground Truth",
        "authority": "NASA Mars 2020 Mission / JPL-Caltech",
        "is_mars_specific": True
    },
    "nasa_worldview": {
        "title": "NASA Worldview (Earthdata)",
        "url": "https://worldview.earthdata.nasa.gov/",
        "description": "General supplementary reference cited on the official challenge page as an exemplar for multi-sensor layer compositing and temporal satellite visualization (Earth observation reference, not a Mars dataset).",
        "category": "General Supplementary Resource (Earth Observation Exemplar)",
        "authority": "NASA Earth Science Data and Information System (ESDIS)",
        "is_mars_specific": False
    }
}

# Map files mapping
MAP_FILES: Dict[str, Path] = {
    "gale-crater": DATA_RAW_DIR / "mola_color_N-30_120.png",
    "jezero-crater": DATA_RAW_DIR / "mola_color_N00_060.png",
    "olympus-mons": DATA_RAW_DIR / "mola_color_N00_210.png"
}

# Regional exploration profiles
REGIONS: Dict[str, Dict[str, Any]] = {
    "gale-crater": {
        "id": "gale-crater",
        "name": "Gale Crater",
        "lat": -5.4,
        "lon": 137.4,
        "elevation_approx": "-4.5 km to +5.5 km relative to Mars datum",
        "diameter": "154 km",
        "geology": "Ancient impact basin hosting Mount Sharp (Aeolis Mons), a 5.5 km high layered sedimentary central mound.",
        "description": "Ancient sedimentary environment and Curiosity rover exploration zone.",
        "objective": "Investigate geological transition from wet fluvial environments to hyper-arid conditions.",
        "mission_context": "NASA Mars Science Laboratory (Curiosity Rover, landed August 2012).",
        "elevation_summary": "Floor depression at -4.5 km transitioning into central layered mountain."
    },
    "jezero-crater": {
        "id": "jezero-crater",
        "name": "Jezero Crater",
        "lat": 18.4,
        "lon": 77.5,
        "elevation_approx": "-2.5 km relative to Mars datum",
        "diameter": "45 km",
        "geology": "Ancient open-basin paleolake fed by Neretva and Sava Valles with preserved river fan delta.",
        "description": "Ancient lake basin and Perseverance rover exploration zone.",
        "objective": "Investigate ancient lakebed delta deposits and collect astrobiological core samples.",
        "mission_context": "NASA Mars 2020 (Perseverance Rover & Ingenuity Helicopter, landed February 2021).",
        "elevation_summary": "Relatively flat crater floor bounded by western delta scarps and rim massifs."
    },
    "olympus-mons": {
        "id": "olympus-mons",
        "name": "Olympus Mons",
        "lat": 18.65,
        "lon": 226.2,
        "elevation_approx": "+21.3 km relative to Mars datum",
        "diameter": "624 km",
        "geology": "Giant basaltic shield volcano with multi-ring caldera depressions and peripheral 6–8 km high basal scarps.",
        "description": "The largest volcano in the Solar System, crowning the Tharsis volcanic plateau.",
        "objective": "Survey shield volcano morphology, basalt flow fields, and high-altitude atmospheric dynamics.",
        "mission_context": "Planetary volcanic landmark surveyed by Mariner 9, Viking, MGS, and MRO orbiters.",
        "elevation_summary": "Ascending shield slopes reaching summit caldera at ~21 km elevation."
    }
}

# Mathematical Coordinate Bounding Boxes (MOLA MEG256 30° × 30° Tiles)
REGION_BOUNDS: Dict[str, Dict[str, Any]] = {
    "gale-crater": {
        "lat_min": -30.0,
        "lat_max": 0.0,
        "lon_min": 120.0,
        "lon_max": 150.0,
        "pixel_width": 7680,
        "pixel_height": 7680,
        "pixels_per_degree": 256.0,
        "lat_convention": "Planetocentric Latitude (°N)",
        "lon_convention": "East Longitude (°E)",
        "projection": "Equirectangular (Simple Cylindrical)",
        "reference_meridian": "Airy-0 Crater (0° Longitude)"
    },
    "jezero-crater": {
        "lat_min": 0.0,
        "lat_max": 30.0,
        "lon_min": 60.0,
        "lon_max": 90.0,
        "pixel_width": 7680,
        "pixel_height": 7680,
        "pixels_per_degree": 256.0,
        "lat_convention": "Planetocentric Latitude (°N)",
        "lon_convention": "East Longitude (°E)",
        "projection": "Equirectangular (Simple Cylindrical)",
        "reference_meridian": "Airy-0 Crater (0° Longitude)"
    },
    "olympus-mons": {
        "lat_min": 0.0,
        "lat_max": 30.0,
        "lon_min": 210.0,
        "lon_max": 240.0,
        "pixel_width": 7680,
        "pixel_height": 7680,
        "pixels_per_degree": 256.0,
        "lat_convention": "Planetocentric Latitude (°N)",
        "lon_convention": "East Longitude (°E)",
        "projection": "Equirectangular (Simple Cylindrical)",
        "reference_meridian": "Airy-0 Crater (0° Longitude)"
    }
}

# Verified NASA Scientific Points of Interest (POIs) with authoritative citations
REGION_POIS: Dict[str, List[Dict[str, Any]]] = {
    "gale-crater": [
        {
            "id": "GC-POI-01",
            "name": "Bradbury Landing",
            "lat": -4.59,
            "lon": 137.44,
            "type": "Historical Landing Site",
            "description": "Touchdown location of the NASA Curiosity rover on August 6, 2012 (UTC).",
            "significance": "Initial exploration baseline in northern crater floor plains.",
            "investigation_focus": "Baseline calibration of rover environmental monitoring (REMS) and soil isotopic measurements.",
            "data_provenance_type": "VERIFIED GROUND TRUTH",
            "nasa_mission": "NASA Mars Science Laboratory (Curiosity)",
            "source_reference": "NASA PDS / MSL Science Team (Grotzinger et al., Science 2014)"
        },
        {
            "id": "GC-POI-02",
            "name": "Yellowknife Bay",
            "lat": -4.53,
            "lon": 137.44,
            "type": "Lacustrine Mudstone",
            "description": "Fine-grained mudstone examined by Curiosity's drill indicating ancient freshwater conditions.",
            "significance": "First verified evidence of an ancient habitable freshwater Martian lake.",
            "investigation_focus": "Drill core extraction of smectite clays, sulfur/nitrogen/oxygen/phosphorus biosignature precursors.",
            "data_provenance_type": "VERIFIED GROUND TRUTH",
            "nasa_mission": "NASA Mars Science Laboratory (Curiosity)",
            "source_reference": "NASA PDS / Curiosity CheMin & SAM instruments (Vaniman et al., Science 2014)"
        },
        {
            "id": "GC-POI-03",
            "name": "Mount Sharp Base (Aeolis Mons)",
            "lat": -5.08,
            "lon": 137.85,
            "type": "Sedimentary Mound / Central Peak",
            "description": "Layered clay- and sulfate-bearing strata preserving Mars' climatic drying transition.",
            "significance": "Primary long-term stratigraphy tracking Mars' wet-to-arid transition.",
            "investigation_focus": "Stratigraphic profiling of sulfate-bearing layers to model atmospheric desiccation timeline.",
            "data_provenance_type": "VERIFIED GROUND TRUTH",
            "nasa_mission": "NASA Mars Science Laboratory (Curiosity)",
            "source_reference": "USGS Astrogeology / NASA MSL Mission Archive (IAU WGPSN)"
        }
    ],
    "jezero-crater": [
        {
            "id": "JC-POI-01",
            "name": "Octavia E. Butler Landing",
            "lat": 18.44,
            "lon": 77.45,
            "type": "Historical Landing Site",
            "description": "Touchdown location of the NASA Perseverance rover on February 18, 2021 (UTC).",
            "significance": "Crater floor basaltic plains unit, site of early flight tests for Ingenuity.",
            "investigation_focus": "Inspection of descent stage blast zone, regolith compaction, and atmospheric dust dynamics.",
            "data_provenance_type": "VERIFIED GROUND TRUTH",
            "nasa_mission": "NASA Mars 2020 (Perseverance & Ingenuity)",
            "source_reference": "NASA Mars 2020 Mission Archive / IAU Gazetteer of Planetary Nomenclature"
        },
        {
            "id": "JC-POI-02",
            "name": "Western Delta Front",
            "lat": 18.43,
            "lon": 77.38,
            "type": "Fluvial River Delta",
            "description": "Fan-shaped river delta sediment deposit where Neretva Vallis entered the Jezero paleolake.",
            "significance": "Highest astrobiological priority for potential biosignature preservation.",
            "investigation_focus": "Raman spectroscopy and micro-mapping of organic matter in fine-grained bottomset delta mudstones.",
            "data_provenance_type": "VERIFIED GROUND TRUTH",
            "nasa_mission": "NASA Mars 2020 (Perseverance)",
            "source_reference": "NASA PDS / Perseverance Mastcam-Z & SuperCam (Mangold et al., Science 2021)"
        },
        {
            "id": "JC-POI-03",
            "name": "Séítah Formation",
            "lat": 18.42,
            "lon": 77.44,
            "type": "Igneous Bedrock & Sand Dunes",
            "description": "Layered cumulate igneous rocks rich in coarse-grained olivine and pyroxene crystals.",
            "significance": "Provides precise radiometric age constraints for Jezero crater floor.",
            "investigation_focus": "Geochronological sample caching of unaltered cumulate olivine grains via robotic coring arm.",
            "data_provenance_type": "VERIFIED GROUND TRUTH",
            "nasa_mission": "NASA Mars 2020 (Perseverance)",
            "source_reference": "NASA PDS / PIXL & SHERLOC instrument science teams (Farley et al., Science 2022)"
        }
    ],
    "olympus-mons": [
        {
            "id": "OM-POI-01",
            "name": "Summit Caldera Rim",
            "lat": 18.65,
            "lon": 226.20,
            "type": "Volcanic Collapse Caldera",
            "description": "Complex nested caldera depression up to 3 km deep and 80 km across at peak elevation (~21.3 km).",
            "significance": "Preserves sequential magma chamber drain-and-collapse events.",
            "investigation_focus": "High-altitude atmospheric sampling, boundary layer pressure telemetry, and nested caldera rim scarps.",
            "data_provenance_type": "ORBITAL SURVEY TARGET",
            "nasa_mission": "NASA MGS MOLA & ESA Mars Express HRSC",
            "source_reference": "USGS Astrogeology MOLA Planetary Topography / IAU Planetary Nomenclature"
        },
        {
            "id": "OM-POI-02",
            "name": "Basal Scarp Base",
            "lat": 18.00,
            "lon": 223.50,
            "type": "Peripheral Cliff Boundary",
            "description": "Towering vertical scarp cliff ring rising 6 to 8 km above the surrounding Martian plains.",
            "significance": "Major structural boundary formed by massive flank landslides and gravity spreading.",
            "investigation_focus": "Geotechnical stability evaluation of avalanche debris aprons and basal detachment faults.",
            "data_provenance_type": "ORBITAL SURVEY TARGET",
            "nasa_mission": "NASA MGS MOLA & MRO CTX",
            "source_reference": "NASA MGS MOLA Global Topography (Smith et al., JGR 2001)"
        },
        {
            "id": "OM-POI-03",
            "name": "Western Lava Channels",
            "lat": 19.20,
            "lon": 224.80,
            "type": "Basaltic Lava Flow Field",
            "description": "Braided lava tubes and thermal erosion channels showing low-viscosity basalt eruptions.",
            "significance": "Youngest volcanic activity indicators on the Tharsis volcanic plateau.",
            "investigation_focus": "Exploration of lava tube entrance skylights as candidate subsurface radiation-shielded crew habitats.",
            "data_provenance_type": "ORBITAL SURVEY TARGET",
            "nasa_mission": "ESA HRSC & NASA MRO CTX / HiRISE",
            "source_reference": "ESA HRSC & NASA MRO CTX / HiRISE Volcanology Surveys"
        }
    ]
}

# Regional Geotechnical Terrain Hazards
REGIONAL_HAZARDS: Dict[str, List[Dict[str, Any]]] = {
    "gale-crater": [
        {
            "id": "HZ-GC-01",
            "name": "Bagnold Dunes Eolian Sand Trap",
            "lat": -4.68,
            "lon": 137.38,
            "type": "SAND_TRAP",
            "severity": "CRITICAL",
            "description": "Active basaltic sand dunes with minimal shear strength; severe wheel sinkage and entrapment hazard.",
            "slope_risk": "Slopes 12°–18° with >80% wheel slip"
        },
        {
            "id": "HZ-GC-02",
            "name": "Gediz Vallis Ridge Scarp",
            "lat": -4.75,
            "lon": 137.35,
            "type": "STEEP_SCARP",
            "severity": "CRITICAL",
            "description": "Precipitous debris-flow boulder ridge with vertical wall segments exceeding rover climb limits.",
            "slope_risk": "Slopes >25° exceeding vehicle stability threshold"
        },
        {
            "id": "HZ-GC-03",
            "name": "Peace Vallis Alluvial Blockfield",
            "lat": -4.48,
            "lon": 137.52,
            "type": "BOULDER_FIELD",
            "severity": "WARNING",
            "description": "Fractured conglomerate and perched boulder clusters risking belly-pan strike and wheel puncture.",
            "slope_risk": "Local micro-topographic gradient variations 10°–16°"
        }
    ],
    "jezero-crater": [
        {
            "id": "HZ-JC-01",
            "name": "South Séítah Megaripple Sand Field",
            "lat": 18.41,
            "lon": 77.44,
            "type": "SAND_TRAP",
            "severity": "CRITICAL",
            "description": "Low-bearing-capacity olivine-rich sand dunes bypassed by NASA Perseverance during campaign planning.",
            "slope_risk": "Slopes 10°–15° with high immobilization probability"
        },
        {
            "id": "HZ-JC-02",
            "name": "Western Fan Delta Front Scarp",
            "lat": 18.44,
            "lon": 77.36,
            "type": "STEEP_SCARP",
            "severity": "CRITICAL",
            "description": "60-meter high near-vertical eroded delta front scarp; completely impassable for wheeled vehicles.",
            "slope_risk": "Cliffs >35° vertical relief"
        },
        {
            "id": "HZ-JC-03",
            "name": "Belva Crater Impact Ejecta Zone",
            "lat": 18.52,
            "lon": 77.38,
            "type": "BOULDER_FIELD",
            "severity": "WARNING",
            "description": "Dense field of meter-scale impact ejecta boulders exceeding rover ground clearance limits.",
            "slope_risk": "Crater rim slope 15°–22°"
        }
    ],
    "olympus-mons": [
        {
            "id": "HZ-OM-01",
            "name": "Central Caldera Rim Sheer Precipice",
            "lat": 18.90,
            "lon": 225.35,
            "type": "STEEP_SCARP",
            "severity": "CRITICAL",
            "description": "Up to 3,000-meter vertical drop into nested summit caldera sinkhole depressions.",
            "slope_risk": "Sheer vertical drops >45°"
        },
        {
            "id": "HZ-OM-02",
            "name": "Subsurface Lava Tube Skylight Collapse",
            "lat": 18.45,
            "lon": 226.70,
            "type": "COLLAPSE_VOID",
            "severity": "CRITICAL",
            "description": "Fragile basaltic roof crust prone to structural collapse under vehicle mass.",
            "slope_risk": "Overhangs and sheer collapse margins"
        },
        {
            "id": "HZ-OM-03",
            "name": "Basal Scarp Avalanche Chute",
            "lat": 18.15,
            "lon": 223.20,
            "type": "STEEP_SCARP",
            "severity": "CRITICAL",
            "description": "Massive catastrophic landslide fault scarps with unconsolidated scree and active rockfall hazards.",
            "slope_risk": "Unconsolidated scree slopes 30°–45°"
        }
    ]
}

