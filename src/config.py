"""
ARES Mission Configuration & Planetary Constants
Holds region coordinates, MOLA file references, and verified NASA scientific POIs.
"""

from typing import Dict, Any, List

# Navigation pages available in Mission Control
NAVIGATION_PAGES: List[str] = [
    "Mission Overview",
    "Mars Explorer",
    "Route Planner",
    "Terrain Intelligence",
    "Hazard Analysis",
    "Science Discovery"
]

# Real NASA MOLA Colorized Elevation tiles
MAP_FILES: Dict[str, str] = {
    "Gale Crater": "data/raw/mola_color_N-30_120.png",
    "Jezero Crater": "data/raw/mola_color_N00_060.png",
    "Olympus Mons": "data/raw/mola_color_N00_210.png"
}

# Regional exploration profiles and verified planetary coordinates
REGIONS: Dict[str, Dict[str, Any]] = {
    "Gale Crater": {
        "lat": -5.4,
        "lon": 137.4,
        "elevation_approx": "-4.5 km to +5.5 km relative to Mars datum",
        "diameter": "154 km",
        "geology": "Impact crater with a massive central sedimentary mound (Mount Sharp / Aeolis Mons).",
        "description": "Ancient sedimentary environment and Curiosity rover exploration region.",
        "objective": "Study geological history and evidence of ancient water.",
        "mission_context": "NASA Mars Science Laboratory (Curiosity Rover, landed Aug 2012).",
        "elevation_summary": "Deep crater floor (~ -4.5 km) transitioning to steep layered mounds rising ~5.5 km high."
    },
    "Jezero Crater": {
        "lat": 18.4,
        "lon": 77.5,
        "elevation_approx": "-2.5 km relative to Mars datum",
        "diameter": "45 km",
        "geology": "Ancient open-basin lake fed by two inbound river channels with an exposed western fan delta.",
        "description": "Ancient lake basin and Perseverance rover exploration region.",
        "objective": "Investigate delta deposits and signs of ancient habitability.",
        "mission_context": "NASA Mars 2020 (Perseverance Rover & Ingenuity Helicopter, landed Feb 2021).",
        "elevation_summary": "Relatively flat crater floor bounded by rugged crater rim scarps and prominent river fan terraces."
    },
    "Olympus Mons": {
        "lat": 18.65,
        "lon": 226.2,
        "elevation_approx": "+21.3 km relative to Mars datum",
        "diameter": "624 km",
        "geology": "Giant basaltic shield volcano featuring complex nested calderas and peripheral basal cliffs.",
        "description": "Home to the largest known volcano in the Solar System.",
        "objective": "Study volcanic terrain and elevation.",
        "mission_context": "Planetary volcanic landmark surveyed by Mariner 9, Viking, MGS, and MRO orbiters.",
        "elevation_summary": "Towering shield slopes with basal scarps rising 6–8 km high and a summit caldera at ~21 km elevation."
    }
}

# Verified Scientific Points of Interest (POIs) based on NASA mission datasets
REGION_POIS: Dict[str, List[Dict[str, Any]]] = {
    "Gale Crater": [
        {
            "id": "GC-POI-01",
            "name": "Bradbury Landing",
            "lat": -4.59,
            "lon": 137.44,
            "type": "Historical Landing Site",
            "description": "Touchdown location of the NASA Curiosity rover on August 6, 2012 (UTC).",
            "significance": "Initial baseline exploration point in northern Gale Crater plains."
        },
        {
            "id": "GC-POI-02",
            "name": "Yellowknife Bay",
            "lat": -4.53,
            "lon": 137.44,
            "type": "Lacustrine Mudstone",
            "description": "Fine-grained sedimentary mudstone formation examined by Curiosity's drill.",
            "significance": "First definitive evidence of an ancient habitable freshwater Martian lake."
        },
        {
            "id": "GC-POI-03",
            "name": "Mount Sharp Base (Aeolis Mons)",
            "lat": -5.08,
            "lon": 137.85,
            "type": "Sedimentary Mound / Central Peak",
            "description": "Layered clay- and sulfate-bearing strata preserving hundreds of millions of years of Martian climate history.",
            "significance": "Primary long-term scientific target tracking Mars' transition from wet to arid."
        }
    ],
    "Jezero Crater": [
        {
            "id": "JC-POI-01",
            "name": "Octavia E. Butler Landing",
            "lat": 18.44,
            "lon": 77.45,
            "type": "Historical Landing Site",
            "description": "Touchdown location of the NASA Perseverance rover on February 18, 2021 (UTC).",
            "significance": "Crater floor basaltic plains unit, site of early flight tests for Ingenuity."
        },
        {
            "id": "JC-POI-02",
            "name": "Western Delta Front",
            "lat": 18.43,
            "lon": 77.38,
            "type": "Fluvial River Delta",
            "description": "Fan-shaped sedimentary deposit formed where ancient Neretva Vallis emptied into Jezero lake.",
            "significance": "Highest astrobiological priority for biosignature preservation in fine-grained silts."
        },
        {
            "id": "JC-POI-03",
            "name": "Séítah Formation",
            "lat": 18.42,
            "lon": 77.44,
            "type": "Igneous Bedrock & Sand Dunes",
            "description": "Layered cumulate igneous rocks rich in coarse-grained olivine and pyroxene crystals.",
            "significance": "Provides precise radiometric age dating for the early history of Jezero Crater floor."
        }
    ],
    "Olympus Mons": [
        {
            "id": "OM-POI-01",
            "name": "Summit Caldera Rim",
            "lat": 18.65,
            "lon": 226.20,
            "type": "Volcanic Collapse Caldera",
            "description": "Complex nested caldera depression up to 3 km deep and 80 km across at peak elevation (~21.3 km).",
            "significance": "Reveals multiple magma chamber drain-and-collapse cycles over volcanic history."
        },
        {
            "id": "OM-POI-02",
            "name": "Basal Scarp Base",
            "lat": 18.00,
            "lon": 223.50,
            "type": "Peripheral Cliff Boundary",
            "description": "Towering vertical scarp cliff ring rising 6 to 8 km above the surrounding Martian plains.",
            "significance": "Major geological structural boundary formed by massive flank landslides and gravity spreading."
        },
        {
            "id": "OM-POI-03",
            "name": "Western Lava Channels",
            "lat": 19.20,
            "lon": 224.80,
            "type": "Basaltic Lava Flow Field",
            "description": "Braided lava tubes and thermal erosion channels showing low-viscosity basalt eruptions.",
            "significance": "Youngest volcanic activity indicators on the Tharsis volcanic plateau."
        }
    ]
}

