# ARES Planetary Data Inventory & Manifest

## 0. Official NASA Space Apps Challenge 2026 Resources Alignment

Challenge Reference: [Interplanetary Survival Guide: Martian Map](https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/?tab=resources)

| Challenge Resource | Authority / Source URL | Key Capabilities / Data Provided | Coordinate System & Datum | Resolution / Format | ARES Integration & Cross-Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **JPL Mars Trek** | NASA JPL / Solar System Treks<br>`https://trek.nasa.gov/mars/` | Global & landing site GIS portal; MOLA elevation, CTX, HiRISE, THEMIS IR, landing site ellipses, 3D print models | Mars 2000 Sphere ($R=3396.19\text{ km}$), Planetocentric | Multi-resolution (MOLA 128 ppd to HiRISE 0.25 m/px); WMTS/REST | **Cross-Check**: Confirms MOLA/HRSC elevation datum (MOLA Areoid). ARES regional DEMs match Mars Trek elevation profiles at Bradbury and Octavia Butler landing sites. |
| **USGS Planetary Geologic Mapping** | USGS Astrogeology Science Center<br>`https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars` | Standardized Geologic Map of Mars (SIM 3292, Tanaka et al. 2014); stratigraphy, chronostratigraphic units (Noachian, Hesperian, Amazonian) | Mars 2000 Sphere, Equirectangular | 1:20,000,000 scale vector / GeoTIFF layers | **Cross-Check**: Source of our 200m blended DEM (`Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif`). Identifies rock types and rough chaotic terrain hazards. |
| **Curiosity Proposed Path up Mt Sharp** | NASA Science Mission Directorate / JPL<br>`https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/` | Traversal rationale from Bradbury Landing up lower Mount Sharp; highlights obstacle avoidance (Bagnold Dunes, ventifact scarps, steep slopes >15°) | Planetocentric Lat/Lon, Airy-0 meridian | Traversal corridor visual & waypoint sequence | **ARES Alignment**: Directly validates Gale Crater POIs: Bradbury Landing (-4.59°N, 137.44°E), Yellowknife Bay (-5.08°N, 137.47°E), Mount Sharp Base (-4.53°N, 137.85°E). |
| **NASA Worldview** | NASA Earthdata (ESDIS)<br>`https://worldview.earthdata.nasa.gov/` | Multi-sensor satellite exploration, dynamic layer compositing, timeline controls | Geographic, Web Mercator | Multi-sensor raster tile services | **ARES Architecture**: Serves as architectural inspiration for layered multi-spectral/topographic map viewing. |
| **Mars Perseverance Raw Images Gallery** | NASA Mars 2020 / JPL-Caltech<br>`https://mars.nasa.gov/mars2020/multimedia/raw-images/` | >1M raw point-of-view surface images (Mastcam-Z, Navcam, Hazcam, SuperCam, WATSON) | Mission Sol, Site ID, Drive ID metadata | JPEG / PDS EDR full resolution | **ARES Integration**: Provides point-of-view (POV) site visualization reference for human Marswalk planning at Jezero delta and landing site. |

---

## 1. Existing Available Datasets

The repository currently contains **three regional cartographic basemaps** (visual only), **three verified numerical elevation models (DEMs)**, and **high-resolution imagery and mineralogical datasets** in `data/raw/`:

### 1.1 Regional Cartographic Basemaps (Visual Context)

| Dataset Identifier | Target Region | File Format | Dimensions | Projection | Bounds (Lat, Lon) | Verified Angular Res. | Derived Ground Res. | Stored Units | Scientific Classification | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `mola_color_N-30_120.png` | Gale Crater / Mt Sharp | PNG (24-bit RGB) | 7680 × 7680 | Equirectangular | -30° to 0°N, 120° to 150°E | 256 pixels/degree | ~231.2 m/px latitudinal | RGB integer [0–255] | **Visual Cartography Only** (Hypsometric color tint) | Verified Present |
| `mola_color_N00_060.png` | Jezero Crater & Delta | PNG (24-bit RGB) | 7680 × 7680 | Equirectangular | 0° to 30°N, 60° to 90°E | 256 pixels/degree | ~231.2 m/px latitudinal | RGB integer [0–255] | **Visual Cartography Only** (Hypsometric color tint) | Verified Present |
| `mola_color_N00_210.png` | Olympus Mons | PNG (24-bit RGB) | 7680 × 7680 | Equirectangular | 0° to 30°N, 210° to 240°E | 256 pixels/degree | ~231.2 m/px latitudinal | RGB integer [0–255] | **Visual Cartography Only** (Hypsometric color tint) | Verified Present |

### Verified vs. Assumed Properties:
- **Verified Facts (Directly Inspected from Headers):**
  - Dimensions: Exactly `7680 × 7680` pixels.
  - Channels: 3-band TrueColor (`mode: 'RGB'`).
  - Spatial angular sampling: `256 pixels/degree` across `30.0° × 30.0°`.
  - Projection: Equirectangular (Simple Cylindrical / Plate Carrée).
  - Geodetic Frame: Planetocentric Latitude (°N), East Longitude (°E), Airy-0 reference meridian.
- **Calculated / Assumed Metrics (Derived by Formulation):**
  - Latitudinal ground resolution: `~231.2 m/px` is derived assuming the IAU 2000 Mars mean radius ($R = 3389.5\text{ km}$). Using the equatorial radius ($R = 3396.2\text{ km}$) yields `~231.5 m/px`.
  - Longitudinal cell width: `231.2 × cos(latitude) m/px`, converging from `231.2 m/px` at the equator to `200.1 m/px` at `30.0°N/S`.
- **Physical Quantities:**
  - **Zero numerical elevation stored.** Pixel values are RGB display values. Slope and elevation are **unavailable** from these files.

### 1.2 Verified Regional Numerical Elevation Models (DEMs)

Derived via windowed HTTP range extraction directly from the USGS Mars MGS MOLA - MEX HRSC Blended DEM Global 200m (v2) (`Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif`):

| Dataset Identifier | Target Region | Format | Shape | Bounds (Lat, Lon) | Angular Res. | Ground Res. (Lat/Lon) | Elevation Range | Units & Datum | Scientific Classification | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gale_crater_dem.npy` | Gale Crater & Mt Sharp | NumPy 2D Int16 | 593 × 593 | -6.00° to -4.00°N, 136.50° to 138.50°E | 0.003374°/px (~296.37 ppd) | 200.0 m/px / ~199.2 m/px | -4688 m to +813 m | Meters rel. to MOLA Areoid | **Genuine Numerical Elevation DEM** | **Verified Present & Ingested** |
| `jezero_crater_dem.npy` | Jezero Crater & Delta | NumPy 2D Int16 | 594 × 594 | 17.49° to 19.50°N, 76.50° to 78.50°E | 0.003374°/px (~296.37 ppd) | 200.0 m/px / ~189.8 m/px | -3469 m to -500 m | Meters rel. to MOLA Areoid | **Genuine Numerical Elevation DEM** | **Verified Present & Ingested** |
| `olympus_mons_dem.npy` | Olympus Mons Caldera & Flanks | NumPy 2D Int16 | 1039 × 1483 | 16.99° to 20.50°N, -137.50° to -132.50°E (222.5° to 227.5°E) | 0.003374°/px (~296.37 ppd) | 200.0 m/px / ~189.5 m/px | +7094 m to +21226 m | Meters rel. to MOLA Areoid | **Genuine Numerical Elevation DEM** | **Verified Present & Ingested** |

- **Physical Verification:**
  - Data type: Single-band signed 16-bit integers (`int16`).
  - Vertical Datum: Mars MOLA Areoid (IAU/IAG 2000 Mars Sphere $R = 3,396,190\text{ m}$).
  - NoData value: `-32768`.
  - Coordinates: Planetocentric Latitude (°N), East Longitude (°E) (both -180..+180 and 0..360 supported).
  - Derived Slopes: Calculated via `terrain_pipeline.calculate_slope_grid` with latitude-dependent cosine cell convergence and NoData masking. Gale Crater max slope: 46.57° (mean: 7.03°); Jezero Crater max slope: 43.28° (mean: 4.34°); Olympus Mons max slope: 47.66° (mean: 4.08°).

### 1.3 Verified High-Resolution Imagery & Mineralogical Datasets

| Dataset Identifier | Target Region | Format | Dimensions | Projection | Bounds (Lat, Lon) | Angular / Ground Res. | Stored Units | Scientific Classification | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0.tif` | Jezero Crater Exploration Corridor | GeoTIFF (Grayscale Byte) | 5322 × 5040 | Equirectangular ($lon_0=0, lat_{ts}=0$), Mars 2000 Sphere ($R=3396190\text{ m}$) | 18.2110° to 18.7212°N, 77.1605° to 77.6992°E | 6.0 m/pixel | 8-bit Calibrated Radiance DN | **High-Resolution Context Imagery (MRO CTX)** | **Verified Present & Ingested** |
| `hydrous_sites_geo_map.csv` | Jezero Crater Paleolake & Delta | Tabular CSV | 5 Verified Regional Detections | Equirectangular Planetocentric | 18.40° to 18.55°N, 77.30° to 77.55°E | Point Spectroscopy Footprints | Spectral Target IDs & Mineral Classes | **MRO CRISM Hydrous Mineralogy Ground Truth** | **Verified Present & Ingested** |

- **Physical Verification:**
  - CTX Orthomosaic: Calibrated 6m/px image mosaic covering the Neretva Vallis delta, Séítah formation, and Octavia E. Butler landing site. Tiepoint: $X = 4573663.25\text{ m}$, $Y = 1109693.14\text{ m}$.
  - CRISM Detections: Identifies ancient water-altered smectite clays, Fe/Mg phyllosilicates, and carbonate-bearing rocks with high astrobiological preservation potential.

---

## 2. Incoming Datasets Inventory Template

When new datasets (GeoTIFFs, single-band TIFFs, CSVs, DTMs) arrive in `data/raw/`, document their metadata using this template:

```markdown
### [DATASET_ID]
- **File Name / Path:** `data/raw/[filename]`
- **Target Exploration Zone:** `Gale Crater` | `Jezero Crater` | `Olympus Mons` | `Regional`
- **Data Category:** `Numerical Elevation Model (DEM)` | `Rover Traverse Record` | `Slope Raster` | `Hazard Classification`
- **Primary Data Format:** `GeoTIFF (Float32 / Int16)` | `NumPy Array (.npy)` | `Tabular CSV`

#### Verified Properties:
- **File Size:** `[X] bytes`
- **Raster Dimensions / Row Count:** `[Width × Height]` pixels or `[N]` rows
- **Band Count & Data Type:** `Single-band Float32` | `Single-band Int16` | `Tabular`
- **NoData Value:** `e.g. -32768` | `-9999` | `NaN`
- **Coordinate Reference System (CRS):** `IAU 2000 Mars Planetocentric`
- **Geographic Bounding Box:** `[Lat Min, Lat Max, Lon Min, Lon Max]` (Degrees North, Degrees East)
- **Grid Resolution:** `[X] pixels/degree` or `[Y] meters/pixel`
- **Authoritative Provenance:** `NASA PDS Geosciences Node` | `USGS Astrogeology` | `ESA PSA (HRSC)`

#### Assumptions & Models:
- **Reference Datum:** `MOLA Areoid (610.5 Pa CO2 triple point potential surface)`
- **Planetary Radii Used:** `R_mean = 3389.5 km, R_eq = 3396.2 km, R_pol = 3376.2 km`
- **Interpolation Model:** `Bilinear (for point queries)` | `Central Difference (for slope)`
- **Verification Status:** `Integrity verified (validated single-band numerical DEM, no RGB contamination)`
```

---

## 3. Required Incoming Datasets Manifest

### 3.1 Regional Numerical Elevation Models (DEMs) [INGESTED]
1. **Gale Crater DEM**: `data/raw/gale_crater_dem.npy` + `data/raw/gale_crater_dem.json` (593 × 593, 200 m/px) - **Status: Ingested & Verified**
2. **Jezero Crater DEM**: `data/raw/jezero_crater_dem.npy` + `data/raw/jezero_crater_dem.json` (594 × 594, 200 m/px) - **Status: Ingested & Verified**
3. **Olympus Mons DEM**: `data/raw/olympus_mons_dem.npy` + `data/raw/olympus_mons_dem.json` (1039 × 1483, 200 m/px) - **Status: Ingested & Verified**

### 3.2 Rover Traverse Records [AWAITING]
4. **NASA Perseverance (Mars 2020) Traverse CSV**:
   - *Expected filename:* `perseverance_traverse.csv`
   - *Columns recognized:* Sol, Site, Drive, Latitude, Longitude, Elevation (m), Distance (m), Timestamp UTC.
   - *Coordinate convention:* Planetocentric Latitude (°N), East Longitude (°E).
   - *Requirement:* Verified NASA PDS Analyst's Notebook / USGS mission archive export.
