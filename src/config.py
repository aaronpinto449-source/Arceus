"""
ARES Mission Configuration & Planetary Constants
Holds region coordinates, MOLA file references, coordinate bounds,
and verified NASA scientific POIs with authoritative source citations.
"""

from typing import Dict, Any, List

# Mars Geodetic Reference Standards (IAU/IAG Working Group on Cartographic Coordinates)
MARS_MEAN_RADIUS_KM: float = 3389.5
MARS_EQUATORIAL_RADIUS_KM: float = 3396.2
MARS_POLAR_RADIUS_KM: float = 3376.2
MARS_FLATTENING: float = 0.00589

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

# Mathematical Coordinate Bounding Boxes for MOLA 256 pixel/deg Equirectangular Tiles
# Coordinate Standard: Planetocentric Latitude (°N, -90 to +90) and East Longitude (°E, 0 to 360)
REGION_BOUNDS: Dict[str, Dict[str, Any]] = {
    "Gale Crater": {
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
    "Jezero Crater": {
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
    "Olympus Mons": {
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
            "significance": "Initial baseline exploration point in northern Gale Crater plains.",
            "source_reference": "NASA PDS / MSL Science Team (Grotzinger et al., Science 2014)"
        },
        {
            "id": "GC-POI-02",
            "name": "Yellowknife Bay",
            "lat": -4.53,
            "lon": 137.44,
            "type": "Lacustrine Mudstone",
            "description": "Fine-grained sedimentary mudstone formation examined by Curiosity's drill.",
            "significance": "First definitive evidence of an ancient habitable freshwater Martian lake.",
            "source_reference": "NASA PDS / Curiosity CheMin & SAM instruments (Vaniman et al., Science 2014)"
        },
        {
            "id": "GC-POI-03",
            "name": "Mount Sharp Base (Aeolis Mons)",
            "lat": -5.08,
            "lon": 137.85,
            "type": "Sedimentary Mound / Central Peak",
            "description": "Layered clay- and sulfate-bearing strata preserving hundreds of millions of years of Martian climate history.",
            "significance": "Primary long-term scientific target tracking Mars' transition from wet to arid.",
            "source_reference": "USGS Astrogeology / NASA MSL Mission Archive (IAU WGPSN)"
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
            "significance": "Crater floor basaltic plains unit, site of early flight tests for Ingenuity.",
            "source_reference": "NASA Mars 2020 Mission Archive / IAU Gazetteer of Planetary Nomenclature"
        },
        {
            "id": "JC-POI-02",
            "name": "Western Delta Front",
            "lat": 18.43,
            "lon": 77.38,
            "type": "Fluvial River Delta",
            "description": "Fan-shaped sedimentary deposit formed where ancient Neretva Vallis emptied into Jezero lake.",
            "significance": "Highest astrobiological priority for biosignature preservation in fine-grained silts.",
            "source_reference": "NASA PDS / Perseverance Mastcam-Z & SuperCam (Mangold et al., Science 2021)"
        },
        {
            "id": "JC-POI-03",
            "name": "Séítah Formation",
            "lat": 18.42,
            "lon": 77.44,
            "type": "Igneous Bedrock & Sand Dunes",
            "description": "Layered cumulate igneous rocks rich in coarse-grained olivine and pyroxene crystals.",
            "significance": "Provides precise radiometric age dating for the early history of Jezero Crater floor.",
            "source_reference": "NASA PDS / PIXL & SHERLOC instrument science teams (Farley et al., Science 2022)"
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
            "significance": "Reveals multiple magma chamber drain-and-collapse cycles over volcanic history.",
            "source_reference": "USGS Astrogeology MOLA Planetary Topography / IAU Planetary Nomenclature"
        },
        {
            "id": "OM-POI-02",
            "name": "Basal Scarp Base",
            "lat": 18.00,
            "lon": 223.50,
            "type": "Peripheral Cliff Boundary",
            "description": "Towering vertical scarp cliff ring rising 6 to 8 km above the surrounding Martian plains.",
            "significance": "Major geological structural boundary formed by massive flank landslides and gravity spreading.",
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
            "source_reference": "ESA HRSC & NASA MRO CTX / HiRISE Volcanology Surveys"
        }
    ]
}
