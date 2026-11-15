import type { Region } from '../types';

export const INITIAL_REGIONS: Region[] = [
  {
    id: 'gale-crater',
    name: 'Gale Crater',
    lat: -5.4,
    lon: 137.4,
    elevation_approx: '-4.5 km to +5.5 km relative to Mars datum',
    diameter: '154 km',
    geology: 'Ancient impact basin hosting Mount Sharp (Aeolis Mons), a 5.5 km high layered sedimentary central mound.',
    description: 'Ancient sedimentary environment and Curiosity rover exploration zone.',
    objective: 'Investigate geological transition from wet fluvial environments to hyper-arid conditions.',
    mission_context: 'NASA Mars Science Laboratory (Curiosity Rover, landed August 2012).',
    elevation_summary: 'Floor depression at -4.5 km transitioning into central layered mountain.',
    bounds: {
      lat_min: -30.0,
      lat_max: 0.0,
      lon_min: 120.0,
      lon_max: 150.0,
      pixel_width: 7680,
      pixel_height: 7680,
      pixels_per_degree: 256.0,
      lat_convention: 'Planetocentric Latitude (°N)',
      lon_convention: 'East Longitude (°E)',
      projection: 'Equirectangular (Simple Cylindrical)',
      reference_meridian: 'Airy-0 Crater (0° Longitude)'
    },
    poi_count: 3,
    pois: [
      {
        id: 'GC-POI-01',
        name: 'Bradbury Landing',
        lat: -4.59,
        lon: 137.44,
        type: 'Historical Landing Site',
        description: 'Touchdown location of the NASA Curiosity rover on August 6, 2012 (UTC).',
        significance: 'Initial exploration baseline in northern crater floor plains.',
        source_reference: 'NASA PDS / MSL Science Team (Grotzinger et al., Science 2014)'
      },
      {
        id: 'GC-POI-02',
        name: 'Yellowknife Bay',
        lat: -4.53,
        lon: 137.44,
        type: 'Lacustrine Mudstone',
        description: 'Fine-grained mudstone examined by Curiosity\'s drill indicating ancient freshwater conditions.',
        significance: 'First verified evidence of an ancient habitable freshwater Martian lake.',
        source_reference: 'NASA PDS / Curiosity CheMin & SAM instruments (Vaniman et al., Science 2014)'
      },
      {
        id: 'GC-POI-03',
        name: 'Mount Sharp Base (Aeolis Mons)',
        lat: -5.08,
        lon: 137.85,
        type: 'Sedimentary Mound / Central Peak',
        description: 'Layered clay- and sulfate-bearing strata preserving Mars\' climatic drying transition.',
        significance: 'Primary long-term stratigraphy tracking Mars\' wet-to-arid transition.',
        source_reference: 'USGS Astrogeology / NASA MSL Mission Archive (IAU WGPSN)'
      }
    ]
  },
  {
    id: 'jezero-crater',
    name: 'Jezero Crater',
    lat: 18.4,
    lon: 77.5,
    elevation_approx: '-2.5 km relative to Mars datum',
    diameter: '45 km',
    geology: 'Ancient open-basin paleolake fed by Neretva and Sava Valles with preserved river fan delta.',
    description: 'Ancient lake basin and Perseverance rover exploration zone.',
    objective: 'Investigate ancient lakebed delta deposits and collect astrobiological core samples.',
    mission_context: 'NASA Mars 2020 (Perseverance Rover & Ingenuity Helicopter, landed February 2021).',
    elevation_summary: 'Relatively flat crater floor bounded by western delta scarps and rim massifs.',
    bounds: {
      lat_min: 0.0,
      lat_max: 30.0,
      lon_min: 60.0,
      lon_max: 90.0,
      pixel_width: 7680,
      pixel_height: 7680,
      pixels_per_degree: 256.0,
      lat_convention: 'Planetocentric Latitude (°N)',
      lon_convention: 'East Longitude (°E)',
      projection: 'Equirectangular (Simple Cylindrical)',
      reference_meridian: 'Airy-0 Crater (0° Longitude)'
    },
    poi_count: 3,
    pois: [
      {
        id: 'JC-POI-01',
        name: 'Octavia E. Butler Landing',
        lat: 18.44,
        lon: 77.45,
        type: 'Historical Landing Site',
        description: 'Touchdown location of the NASA Perseverance rover on February 18, 2021 (UTC).',
        significance: 'Crater floor basaltic plains unit, site of early flight tests for Ingenuity.',
        source_reference: 'NASA Mars 2020 Mission Archive / IAU Gazetteer of Planetary Nomenclature'
      },
      {
        id: 'JC-POI-02',
        name: 'Western Delta Front',
        lat: 18.43,
        lon: 77.38,
        type: 'Fluvial River Delta',
        description: 'Fan-shaped river delta sediment deposit where Neretva Vallis entered the Jezero paleolake.',
        significance: 'Highest astrobiological priority for potential biosignature preservation.',
        source_reference: 'NASA PDS / Perseverance Mastcam-Z & SuperCam (Mangold et al., Science 2021)'
      },
      {
        id: 'JC-POI-03',
        name: 'Séítah Formation',
        lat: 18.42,
        lon: 77.44,
        type: 'Igneous Bedrock & Sand Dunes',
        description: 'Layered cumulate igneous rocks rich in coarse-grained olivine and pyroxene crystals.',
        significance: 'Provides precise radiometric age constraints for Jezero crater floor.',
        source_reference: 'NASA PDS / PIXL & SHERLOC instrument science teams (Farley et al., Science 2022)'
      }
    ]
  },
  {
    id: 'olympus-mons',
    name: 'Olympus Mons',
    lat: 18.65,
    lon: 226.2,
    elevation_approx: '+21.3 km relative to Mars datum',
    diameter: '624 km',
    geology: 'Giant basaltic shield volcano with multi-ring caldera depressions and peripheral 6–8 km high basal scarps.',
    description: 'The largest volcano in the Solar System, crowning the Tharsis volcanic plateau.',
    objective: 'Survey shield volcano morphology, basalt flow fields, and high-altitude atmospheric dynamics.',
    mission_context: 'Planetary volcanic landmark surveyed by Mariner 9, Viking, MGS, and MRO orbiters.',
    elevation_summary: 'Ascending shield slopes reaching summit caldera at ~21 km elevation.',
    bounds: {
      lat_min: 0.0,
      lat_max: 30.0,
      lon_min: 210.0,
      lon_max: 240.0,
      pixel_width: 7680,
      pixel_height: 7680,
      pixels_per_degree: 256.0,
      lat_convention: 'Planetocentric Latitude (°N)',
      lon_convention: 'East Longitude (°E)',
      projection: 'Equirectangular (Simple Cylindrical)',
      reference_meridian: 'Airy-0 Crater (0° Longitude)'
    },
    poi_count: 3,
    pois: [
      {
        id: 'OM-POI-01',
        name: 'Summit Caldera Rim',
        lat: 18.65,
        lon: 226.2,
        type: 'Volcanic Collapse Caldera',
        description: 'Complex nested caldera depression up to 3 km deep and 80 km across at peak elevation (~21.3 km).',
        significance: 'Preserves sequential magma chamber drain-and-collapse events.',
        source_reference: 'USGS Astrogeology MOLA Planetary Topography / IAU Planetary Nomenclature'
      },
      {
        id: 'OM-POI-02',
        name: 'Basal Scarp Base',
        lat: 18.0,
        lon: 223.5,
        type: 'Peripheral Cliff Boundary',
        description: 'Towering vertical scarp cliff ring rising 6 to 8 km above the surrounding Martian plains.',
        significance: 'Major structural boundary formed by massive flank landslides and gravity spreading.',
        source_reference: 'NASA MGS MOLA Global Topography (Smith et al., JGR 2001)'
      },
      {
        id: 'OM-POI-03',
        name: 'Western Lava Channels',
        lat: 19.2,
        lon: 224.8,
        type: 'Basaltic Lava Flow Field',
        description: 'Braided lava tubes and thermal erosion channels showing low-viscosity basalt eruptions.',
        significance: 'Youngest volcanic activity indicators on the Tharsis volcanic plateau.',
        source_reference: 'ESA HRSC & NASA MRO CTX / HiRISE Volcanology Surveys'
      }
    ]
  }
];

