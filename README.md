# ARES — Autonomous Reconnaissance & Exploration System

**ARES** is an interactive Mars surface mission control and planetary exploration platform developed by **Team Arceus** for the **NASA Space Apps Challenge 2026** under the challenge:  
👉 **[Interplanetary Survival Guide: Martian Map](https://www.spaceappschallenge.org/2026/challenges/interplanetary-survival-guide-martian-map/?tab=resources)**

---

## 1. Official NASA Space Apps Challenge 2026 Resource Alignment

ARES directly aligns with and incorporates data, standards, and methodologies from the official resources specified for this challenge:

| Challenge Resource | Authority | Role in ARES | Classification |
| :--- | :--- | :--- | :--- |
| **[Jet Propulsion Laboratory’s (JPL) Mars Trek](https://trek.nasa.gov/mars/)** | NASA JPL / Solar System Treks | Primary reference for planetary coordinate systems (Mars 2000 Sphere), MOLA areoid datum, and regional landing site verification. | **Mars-Specific Official Resource** |
| **[USGS-NASA Planetary Geologic Mapping Program](https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars)** | USGS Astrogeology Science Center / NASA | Direct source of the 200 m Blended DEM (`Mars_HRSC_MOLA_BlendDEM_Global_200mp_v2.tif`) and standardized Mars geologic map units (SIM 3292). | **Mars-Specific Official Resource** |
| **[Curiosity's Proposed Path up Mount Sharp](https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/)** | NASA Science Mission Directorate / JPL | Traversal ground truth used to validate Gale Crater POIs (Bradbury Landing, Yellowknife Bay, Mount Sharp Base) and steep slope/dune obstacle avoidance. | **Mars-Specific Official Resource** |
| **[NASA Mars Perseverance Raw Images Gallery](https://mars.nasa.gov/mars2020/multimedia/raw-images/)** | NASA Mars 2020 / JPL-Caltech | Surface ground-truth visual references for Jezero Crater points of interest (Octavia E. Butler Landing, Delta Front, Neretva Vallis). | **Mars-Specific Official Resource** |
| **[NASA Worldview](https://worldview.earthdata.nasa.gov/)** | NASA Earthdata (ESDIS) | UI/UX architectural exemplar for multi-sensor layer compositing and temporal satellite visualization. | **General Supplementary Resource** *(Earth Observation Exemplar)* |

---

## 2. Scientific Data Provenance & Integrity Framework

To uphold scientific honesty, ARES explicitly categorizes and badges all planetary information:

1. **Measured Numerical DEM Data (`MEASURED`)**:
   - Sourced from the **USGS Mars MGS MOLA – MEX HRSC Blended DEM Global 200m (v2)**.
   - Single-band signed 16-bit integer elevation matrix (`int16`, NoData: `-32768`).
   - Vertical Datum: **Mars MOLA Areoid** ($610.5\text{ Pa } CO_2$ triple-point potential surface on Mars 2000 Sphere $R = 3,396,190\text{ m}$).
   - Horizontal CRS: **Planetocentric Latitude (°N), East Longitude (°E)**, Airy-0 reference meridian.
   - Ground Resolution: **200.00 m/pixel** along meridians.

2. **Calculated Slope Gradients (`CALCULATED`)**:
   - Derived mathematically via central finite differences on the 2D elevation grid.
   - Accounts for spherical Mars planetary radius and latitude-dependent cosine longitudinal cell convergence:  
     $$dx(\text{lat}) = dx_0 \cdot \cos(\text{lat})$$
   - Explicitly masks NoData cells (`-32768`) to eliminate synthetic cliff edge artifacts.

3. **Simulated Route Estimates (`SIMULATED`)**:
   - Great-circle Haversine distances ($R_{\text{mean}} = 3,389.5\text{ km}$, $R_{\text{eq}} = 3,396.2\text{ km}$).
   - Three deterministic routing priorities:
     - **`DISTANCE`**: Direct minimum great-circle Haversine path between coordinates.
     - **`BALANCED`**: Graph-based path routing through intermediate surveyed POI waypoints.
     - **`SAFETY`**: Hazard-weighted routing avoiding steep terrain massifs and rough scarps.

4. **External Ground Truth Cross-Checks (`GROUND TRUTH`)**:
   - **Gale Crater (Curiosity MSL)**: Bradbury Landing DEM elevation query returns **$-4,494.58\text{ m}$** (NASA landing telemetry: $-4,501\text{ m}$; within 0.14% error margin).
   - **Jezero Crater (Perseverance M2020)**: Octavia E. Butler Landing DEM query returns **$-2,580.79\text{ m}$** (crater floor ground truth: ~$-2,570\text{ m}$).
   - **Olympus Mons Summit Caldera Floor**: DEM query returns **$+19,581.49\text{ m}$** (basal escarpment slopes reach $47.66^\circ$).

---

## 3. Explored Regions & Target Zones

1. **Gale Crater & Mount Sharp** ($-6.00^\circ\text{ to }-4.00^\circ\text{N}, 136.50^\circ\text{ to }138.50^\circ\text{E}$):
   - Elevation Range: $-4,688\text{ m}$ to $+813\text{ m}$ (Mount Sharp central mound).
   - Slopes: $0.00^\circ$ to $46.57^\circ$ (mean: $7.03^\circ$).
2. **Jezero Crater & Fan Delta** ($17.49^\circ\text{ to }19.50^\circ\text{N}, 76.50^\circ\text{ to }78.50^\circ\text{E}$):
   - Elevation Range: $-3,469\text{ m}$ to $-500\text{ m}$ (crater rim and delta front).
   - Slopes: $0.00^\circ$ to $43.28^\circ$ (mean: $4.34^\circ$).
3. **Olympus Mons & Caldera** ($16.99^\circ\text{ to }20.50^\circ\text{N}, 222.50^\circ\text{ to }227.50^\circ\text{E}$ / $-137.5^\circ\text{ to }-132.5^\circ\text{E}$):
   - Elevation Range: $+7,094\text{ m}$ to $+21,226\text{ m}$ (Solar System's largest shield volcano).
   - Slopes: $0.00^\circ$ to $47.66^\circ$ (mean: $4.08^\circ$).

---

## 4. System Architecture

- **Backend**: Python 3.13 + FastAPI + NumPy + Pillow (serving REST API on port `8001` with fallback to `8000`).
- **Frontend**: Svelte 5 (Runes) + Vite + TypeScript + Tailwind CSS + Lucide Icons (modern aerospace telemetry UI).
- **Zero Heavy RAM Load**: Tiled HTTP byte range windowing downloads only ~4.4 MB for all regional DEMs, avoiding 11.38 GB global raster bloat.

---

## 5. Quickstart & Verification Commands

### Step 1: Run the Backend Test Suite
```bash
python backend/test_suite.py
```
*Executes all 9 automated test suites verifying API health, regions, POIs, telemetry resolution, official Space Apps resources, route priorities, vehicle caveats, terrain DEM ingestion, and slope calculus.*

### Step 2: Start the FastAPI Backend
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
```
*API interactive documentation is available at `http://127.0.0.1:8001/docs`.*

### Step 3: Run Frontend Verification & Build
```bash
# Verify TypeScript & Svelte diagnostics (0 errors, 0 warnings)
pnpm --prefix frontend-svelte check

# Compile production bundle
pnpm --prefix frontend-svelte build
```

### Step 4: Start the Frontend Dev Server
```bash
pnpm --prefix frontend-svelte dev
```
*Access the ARES Mission Control Interface in your browser at `http://localhost:5173`.*

---

## 6. Critical Scientific Limitations & Caveats

1. **Resolution Boundary**: The numerical DEMs are sampled at $200\text{ m/pixel}$. Calculated route corridors represent regional planning paths; sub-meter surface obstacles (such as individual boulders or meter-scale crevasses) are not resolved at this scale and require local rover Hazcam/Navcam inspection.
2. **Vehicle Range Caveats**: Rover battery and range feasibility values are illustrative engineering assumptions, not flight-certified mission limits.
3. **POI Snapping Threshold**: Start and destination coordinates snap to known surveyed POIs within a documented radius of $0.05^\circ$ ($\approx 3.0\text{ km}$ at the equator).
4. **Visual Imagery Distinction**: Regional MOLA color maps (`mola_color_*.png`) and CTX images are 8-bit visual rendering basemaps; they are not used for elevation or slope calculus. All physical topography is derived strictly from the single-band 200 m numerical DEM grids.
