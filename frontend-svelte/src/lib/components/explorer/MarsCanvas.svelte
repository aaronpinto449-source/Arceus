<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import type { Region, PointOfInterest, SelectedTarget, SlopeAnalysisData, PointElevationResponse, CrismHydrousSite } from "../../types";
  import { mission } from "../../stores/mission.svelte";
  import { api } from "../../services/api";
  import { REGIONAL_HAZARDS, type TerrainHazard } from "../../data/hazards";
  import L from "leaflet";
  import {
    ZoomIn,
    ZoomOut,
    RotateCcw,
    Layers,
    MapPin,
    AlertTriangle,
    Compass,
    Crosshair,
    Maximize2,
    Eye,
    EyeOff,
    Navigation,
    Route,
    Activity,
    Mountain,
    Gauge,
    Sparkles,
    Gem
  } from "@lucide/svelte";

  interface Props {
    region: Region;
    imageUrl?: string;
    pois?: PointOfInterest[];
    selectedTarget?: SelectedTarget | null;
    onSelectTarget?: (target: SelectedTarget) => void;
    showControls?: boolean;
    compact?: boolean;
  }

  let {
    region,
    imageUrl,
    pois = [],
    selectedTarget = null,
    onSelectTarget,
    showControls = true,
    compact = false,
  }: Props = $props();

  let mapContainer: HTMLDivElement | null = $state(null);
  let map: L.Map | null = null;

  // Leaflet Layer Groups & Overlays
  let basemapLayer: L.ImageOverlay | null = null;
  let slopeLayer: L.ImageOverlay | null = null;
  let elevationTintLayer: L.ImageOverlay | null = null;
  let ctxLayer: L.ImageOverlay | null = null;
  let poisGroup: L.LayerGroup | null = null;
  let hazardsGroup: L.LayerGroup | null = null;
  let crismGroup: L.LayerGroup | null = null;
  let routeGroup: L.LayerGroup | null = null;
  let targetMarker: L.Marker | null = null;

  // UI States & Layer Toggles
  let showPois = $state(true);
  let showHazards = $state(true);
  let showSlopeHeatmap = $state(false);
  let showElevationTint = $state(false);
  let showCtxOverlay = $state(false);
  let showCrismSites = $state(false);
  let showLegend = $state(true);
  let crismSites = $state<CrismHydrousSite[]>([]);
  let hoverLatLon = $state<{ lat: number; lon: number } | null>(null);
  let clickedPointInfo = $state<{
    lat: number;
    lon: number;
    elevation_m: number | null;
    slope_deg: number | null;
    difficulty_level?: string;
    traversability_rating?: string;
    slip_risk?: string;
    resolution_m?: number;
    source?: string;
    loading: boolean;
  } | null>(null);

  $effect(() => {
    if (compact) {
      showLegend = false;
    }
  });

  const routeSlope = $derived(
    mission.routeResult?.slope_data?.supported
      ? (mission.routeResult.slope_data as SlopeAnalysisData)
      : null
  );

  // Regional High-Resolution 200m DEM bounding coordinates (from data/raw/*_dem.json)
  const DEM_BOUNDS: Record<string, L.LatLngBoundsLiteral> = {
    "gale-crater": [
      [-6.0005, 136.4993],
      [-3.9996, 138.5001],
    ],
    "jezero-crater": [
      [17.4969, 76.4973],
      [19.5011, 78.5015],
    ],
    "olympus-mons": [
      [16.9975, 222.4971],
      [20.5032, 227.5009],
    ],
  };

  // Jezero High-Resolution 6m/px CTX Orthomosaic geographic bounds (from JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0.tif)
  const JEZERO_CTX_BOUNDS: L.LatLngBoundsLiteral = [
    [18.2110, 77.1605],
    [18.7212, 77.6992],
  ];

  // Center points and default zoom levels for regional focus
  const REGION_CENTERS: Record<string, { center: [number, number]; zoom: number }> = {
    "gale-crater": { center: [-5.0, 137.5], zoom: 4.8 },
    "jezero-crater": { center: [18.4, 77.5], zoom: 5.2 },
    "olympus-mons": { center: [18.7, 225.5], zoom: 3.8 },
  };

  const currentHazards = $derived<TerrainHazard[]>(
    REGIONAL_HAZARDS[region.id] || []
  );

  onMount(() => {
    if (!mapContainer) return;

    // Initialize Leaflet Map using Simple Cartesian coordinate system
    // Maps planetocentric Latitude (°N) directly to Y and East Longitude (°E) to X
    map = L.map(mapContainer, {
      crs: L.CRS.Simple,
      minZoom: -1,
      maxZoom: 9,
      zoomSnap: 0.1,
      zoomDelta: 0.4,
      attributionControl: false,
      zoomControl: false,
    });

    // Create layer groups
    poisGroup = L.layerGroup().addTo(map);
    hazardsGroup = L.layerGroup().addTo(map);
    crismGroup = L.layerGroup().addTo(map);
    routeGroup = L.layerGroup().addTo(map);

    // Event listeners for coordinate tracking
    map.on("mousemove", (e: L.LeafletMouseEvent) => {
      hoverLatLon = {
        lat: Number(e.latlng.lat.toFixed(4)),
        lon: Number(e.latlng.lng.toFixed(4)),
      };
    });

    map.on("mouseout", () => {
      hoverLatLon = null;
    });

    map.on("click", async (e: L.LeafletMouseEvent) => {
      const lat = Number(e.latlng.lat.toFixed(4));
      const lon = Number(e.latlng.lng.toFixed(4));

      clickedPointInfo = {
        lat,
        lon,
        elevation_m: null,
        slope_deg: null,
        difficulty_level: undefined,
        traversability_rating: undefined,
        slip_risk: undefined,
        resolution_m: undefined,
        source: undefined,
        loading: true,
      };

      if (onSelectTarget) {
        onSelectTarget({
          lat,
          lon,
          name: `Point (${lat >= 0 ? "+" : ""}${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E)`,
        });
      }

      // Query real numerical elevation & slope from backend
      try {
        const data = await api.getPointElevation(region.id, lat, lon);
        if (clickedPointInfo && clickedPointInfo.lat === lat && clickedPointInfo.lon === lon) {
          clickedPointInfo.elevation_m = data.elevation_m;
          clickedPointInfo.slope_deg = data.slope_deg;
          clickedPointInfo.difficulty_level = data.difficulty_level;
          clickedPointInfo.traversability_rating = data.traversability_rating;
          clickedPointInfo.slip_risk = data.slip_risk;
          clickedPointInfo.resolution_m = data.resolution_m;
          clickedPointInfo.source = data.source;
          clickedPointInfo.loading = false;
        }
      } catch {
        if (clickedPointInfo) clickedPointInfo.loading = false;
      }
    });

    // Initial render for active region
    loadRegionBasemap();
    updateMarkers();
    updateRoute();

    // Invalidate size to ensure proper tile layout
    setTimeout(() => {
      map?.invalidateSize();
    }, 100);
  });

  onDestroy(() => {
    if (map) {
      map.remove();
      map = null;
    }
  });

  // Watch for region change
  $effect(() => {
    const regId = region.id;
    if (map) {
      if (regId !== "jezero-crater") {
        showCtxOverlay = false;
        showCrismSites = false;
        removeCtxLayer();
        if (crismGroup) crismGroup.clearLayers();
      }
      loadRegionBasemap();
      updateMarkers();
      updateRoute();
      if (showCrismSites && regId === "jezero-crater") {
        loadCrismSites();
      }
    }
  });

  // Watch for POIs toggle
  $effect(() => {
    const p = showPois;
    if (poisGroup && map) {
      if (p) {
        if (!map.hasLayer(poisGroup)) map.addLayer(poisGroup);
      } else {
        if (map.hasLayer(poisGroup)) map.removeLayer(poisGroup);
      }
    }
  });

  // Watch for Hazards toggle
  $effect(() => {
    const h = showHazards;
    if (hazardsGroup && map) {
      if (h) {
        if (!map.hasLayer(hazardsGroup)) map.addLayer(hazardsGroup);
      } else {
        if (map.hasLayer(hazardsGroup)) map.removeLayer(hazardsGroup);
      }
    }
  });

  // Watch for Slope Heatmap toggle
  $effect(() => {
    const s = showSlopeHeatmap;
    if (map) {
      if (s) {
        addSlopeLayer();
      } else {
        removeSlopeLayer();
      }
    }
  });

  // Watch for 200m Elevation Tint toggle
  $effect(() => {
    const e = showElevationTint;
    if (map) {
      if (e) {
        addElevationTintLayer();
      } else {
        removeElevationTintLayer();
      }
    }
  });

  // Watch for 6m Jezero CTX toggle
  $effect(() => {
    const c = showCtxOverlay;
    if (map) {
      if (c && region.id === "jezero-crater") {
        addCtxLayer();
      } else {
        removeCtxLayer();
      }
    }
  });

  // Watch for CRISM Hydrous Sites toggle
  $effect(() => {
    const crism = showCrismSites;
    if (crismGroup && map) {
      if (crism && region.id === "jezero-crater") {
        if (!map.hasLayer(crismGroup)) map.addLayer(crismGroup);
        loadCrismSites();
      } else {
        if (map.hasLayer(crismGroup)) map.removeLayer(crismGroup);
      }
    }
  });

  // Watch for routeResult updates from mission store
  $effect(() => {
    const result = mission.routeResult;
    if (map) {
      updateRoute();
    }
  });

  // Watch for selectedTarget
  $effect(() => {
    const target = selectedTarget;
    if (map) {
      updateTargetMarker();
    }
  });

  function loadRegionBasemap() {
    if (!map) return;

    // Remove existing overlays
    if (basemapLayer) {
      map.removeLayer(basemapLayer);
      basemapLayer = null;
    }
    removeSlopeLayer();
    removeElevationTintLayer();
    removeCtxLayer();

    const bounds = region.bounds;
    // Bounding box for MOLA 30° × 30° equirectangular basemap
    const mapBounds: L.LatLngBoundsLiteral = [
      [bounds.lat_min, bounds.lon_min],
      [bounds.lat_max, bounds.lon_max],
    ];

    const mapSrc = imageUrl || api.getRegionMapUrl(region.id);

    basemapLayer = L.imageOverlay(mapSrc, mapBounds, {
      opacity: 1.0,
      className: "ares-basemap-layer",
    }).addTo(map);

    // Re-add overlays if enabled
    if (showSlopeHeatmap) {
      addSlopeLayer();
    }
    if (showElevationTint) {
      addElevationTintLayer();
    }
    if (showCtxOverlay && region.id === "jezero-crater") {
      addCtxLayer();
    }

    // Center map on region focal area
    resetMapView();
  }

  function addSlopeLayer() {
    if (!map || slopeLayer) return;
    const demB = DEM_BOUNDS[region.id];
    if (!demB) return;

    const slopeSrc = api.getRegionSlopeMapUrl(region.id);
    slopeLayer = L.imageOverlay(slopeSrc, demB, {
      opacity: 0.72,
      className: "ares-slope-layer",
      zIndex: 10,
    }).addTo(map);
  }

  function removeSlopeLayer() {
    if (map && slopeLayer) {
      map.removeLayer(slopeLayer);
      slopeLayer = null;
    }
  }

  function addElevationTintLayer() {
    if (!map || elevationTintLayer) return;
    const demB = DEM_BOUNDS[region.id];
    if (!demB) return;

    const tintSrc = api.getRegionElevationMapUrl(region.id);
    elevationTintLayer = L.imageOverlay(tintSrc, demB, {
      opacity: 0.78,
      className: "ares-elevation-tint-layer",
      zIndex: 8,
    }).addTo(map);
  }

  function removeElevationTintLayer() {
    if (map && elevationTintLayer) {
      map.removeLayer(elevationTintLayer);
      elevationTintLayer = null;
    }
  }

  function addCtxLayer() {
    if (!map || ctxLayer || region.id !== "jezero-crater") return;
    const ctxSrc = api.getJezeroCtxMapUrl();
    ctxLayer = L.imageOverlay(ctxSrc, JEZERO_CTX_BOUNDS, {
      opacity: 0.95,
      className: "ares-ctx-layer",
      zIndex: 12,
    }).addTo(map);
  }

  function removeCtxLayer() {
    if (map && ctxLayer) {
      map.removeLayer(ctxLayer);
      ctxLayer = null;
    }
  }

  export function zoomToCtx() {
    if (!map || region.id !== "jezero-crater") return;
    map.fitBounds(JEZERO_CTX_BOUNDS, { padding: [40, 40], animate: true });
  }

  async function loadCrismSites() {
    const cGroup = crismGroup;
    if (!map || !cGroup) return;
    cGroup.clearLayers();

    if (region.id !== "jezero-crater") return;

    try {
      crismSites = await api.getHydrousSites("jezero-crater");
      if (!crismGroup || !showCrismSites) return;

      crismSites.forEach((site) => {
        const iconHtml = `
          <div class="ares-map-pin crism-pin">
            <div class="pin-gem bg-[#9333ea] border-2 border-[#d8b4fe] shadow-[0_0_10px_rgba(168,85,247,0.9)]">
              <svg class="w-2.5 h-2.5 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l8 8-8 12L4 10l8-8z"/>
              </svg>
            </div>
            <span class="pin-title text-[#d8b4fe]">${site.target_id}</span>
          </div>
        `;

        const customIcon = L.divIcon({
          className: "custom-div-icon",
          html: iconHtml,
          iconSize: [22, 22],
          iconAnchor: [11, 11],
          popupAnchor: [0, -12],
        });

        const marker = L.marker([site.lat, site.lon], { icon: customIcon });

        const popupHtml = `
          <div class="ares-popup font-mono text-xs">
            <div class="flex items-center justify-between mb-1 pb-1 border-b border-purple-500/40">
              <span class="font-bold text-[#d8b4fe] uppercase text-[11px]">${site.name}</span>
              <span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">MRO CRISM</span>
            </div>
            <div class="text-[10px] text-purple-200/90 mb-1 font-bold">${site.mineral_type}</div>
            <div class="bg-ares-deep/80 p-1.5 rounded border border-purple-500/30 mb-2 space-y-0.5 text-[10px]">
              <div><strong class="text-slate-400">LAT:</strong> <span class="text-purple-300">${site.lat >= 0 ? "+" : ""}${site.lat.toFixed(4)}°N</span></div>
              <div><strong class="text-slate-400">LON:</strong> <span class="text-purple-300">${site.lon.toFixed(4)}°E</span></div>
              <div><strong class="text-slate-400">TARGET:</strong> <span class="text-white">${site.target_id}</span></div>
            </div>
            <p class="text-[10px] font-sans text-slate-300 leading-snug mb-2">${site.description}</p>
            <div class="text-[9px] text-slate-500 italic mb-2">${site.instrument}</div>
            <div class="flex gap-1.5 pt-1 border-t border-purple-500/30">
              <button class="flex-1 py-1 px-2 rounded bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 text-[10px] font-bold border border-purple-500/40 cursor-pointer" onclick="window.dispatchEvent(new CustomEvent('ares-set-start', { detail: { name: '${site.name.replace(/'/g, "\\'")}', lat: ${site.lat}, lon: ${site.lon} } }))">
                SET START
              </button>
              <button class="flex-1 py-1 px-2 rounded bg-ares-amber/20 hover:bg-ares-amber/30 text-ares-amber text-[10px] font-bold border border-ares-amber/40 cursor-pointer" onclick="window.dispatchEvent(new CustomEvent('ares-set-dest', { detail: { name: '${site.name.replace(/'/g, "\\'")}', lat: ${site.lat}, lon: ${site.lon} } }))">
                SET DEST
              </button>
            </div>
          </div>
        `;

        marker.bindPopup(popupHtml, { className: "ares-leaflet-popup" });
        cGroup.addLayer(marker);
      });
    } catch {
      // ignore
    }
  }

  export function resetMapView() {
    if (!map) return;
    const conf = REGION_CENTERS[region.id] || {
      center: [region.lat, region.lon],
      zoom: 4.5,
    };
    map.setView(conf.center, conf.zoom, { animate: true });
  }

  export function fitToRoute() {
    if (!map || !mission.routeResult || mission.routeResult.coordinates.length < 2) return;
    const latLngs = mission.routeResult.coordinates.map((c) => L.latLng(c.lat, c.lon));
    const polyline = L.polyline(latLngs);
    map.fitBounds(polyline.getBounds(), {
      padding: [70, 70],
      maxZoom: 6.5,
      animate: true,
    });
  }

  function updateMarkers() {
    const pGroup = poisGroup;
    const hGroup = hazardsGroup;
    if (!map || !pGroup || !hGroup) return;

    pGroup.clearLayers();
    hGroup.clearLayers();

    // 1. Scientific POIs
    pois.forEach((poi) => {
      const isLanding = poi.type.toLowerCase().includes("landing");

      const iconHtml = isLanding
        ? `<div class="ares-map-pin landing-site">
             <div class="pin-pulse"></div>
             <div class="pin-core bg-ares-cyan border-2 border-ares-deep shadow-[0_0_10px_rgba(54,197,232,0.8)]">
               <svg class="w-3 h-3 text-ares-deep" viewBox="0 0 24 24" fill="currentColor">
                 <path d="M12 2L4 20h16L12 2zm0 4l5.5 12h-11L12 6z"/>
               </svg>
             </div>
             <span class="pin-title">${poi.name}</span>
           </div>`
        : `<div class="ares-map-pin science-site">
             <div class="pin-core bg-ares-amber border-2 border-ares-deep shadow-[0_0_8px_rgba(242,169,59,0.8)]">
               <div class="w-1.5 h-1.5 rounded-full bg-ares-deep"></div>
             </div>
             <span class="pin-title">${poi.name}</span>
           </div>`;

      const customIcon = L.divIcon({
        className: "custom-div-icon",
        html: iconHtml,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -14],
      });

      const marker = L.marker([poi.lat, poi.lon], { icon: customIcon });

      const popupHtml = `
        <div class="ares-popup font-mono text-xs">
          <div class="flex items-center gap-1.5 mb-1 pb-1 border-b border-ares-border">
            <span class="w-2 h-2 rounded-full ${isLanding ? "bg-ares-cyan" : "bg-ares-amber"}"></span>
            <span class="font-bold text-white uppercase text-[11px]">${poi.name}</span>
          </div>
          <div class="text-[10px] text-slate-400 mb-1.5">${poi.type}</div>
          <div class="bg-ares-deep/80 p-1.5 rounded border border-ares-border mb-2 space-y-0.5 text-[10px]">
            <div><strong class="text-slate-400">LAT:</strong> <span class="text-ares-cyan">${poi.lat >= 0 ? "+" : ""}${poi.lat.toFixed(4)}°N</span></div>
            <div><strong class="text-slate-400">LON:</strong> <span class="text-ares-cyan">${poi.lon.toFixed(4)}°E</span></div>
          </div>
          <p class="text-[10px] font-sans text-slate-300 leading-snug mb-2">${poi.description}</p>
          <div class="text-[9px] text-slate-500 italic mb-2">Ref: ${poi.source_reference || "NASA PDS / IAU"}</div>
          <div class="flex gap-1.5 pt-1 border-t border-ares-border">
            <button class="flex-1 py-1 px-2 rounded bg-ares-cyan/20 hover:bg-ares-cyan/30 text-ares-cyan text-[10px] font-bold border border-ares-cyan/40" onclick="window.dispatchEvent(new CustomEvent('ares-set-start', { detail: { name: '${poi.name.replace(/'/g, "\\'")}', lat: ${poi.lat}, lon: ${poi.lon} } }))">
              SET START
            </button>
            <button class="flex-1 py-1 px-2 rounded bg-ares-amber/20 hover:bg-ares-amber/30 text-ares-amber text-[10px] font-bold border border-ares-amber/40" onclick="window.dispatchEvent(new CustomEvent('ares-set-dest', { detail: { name: '${poi.name.replace(/'/g, "\\'")}', lat: ${poi.lat}, lon: ${poi.lon} } }))">
              SET DEST
            </button>
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml, { className: "ares-leaflet-popup" });
      pGroup.addLayer(marker);
    });

    // 2. Terrain Hazards
    currentHazards.forEach((hz) => {
      const isCritical = hz.severity === "CRITICAL";

      const hazardHtml = `
        <div class="ares-map-pin hazard-pin">
          <div class="pin-diamond ${isCritical ? "bg-ares-red shadow-[0_0_10px_rgba(239,85,85,0.9)]" : "bg-ares-amber shadow-[0_0_8px_rgba(242,169,59,0.8)]"}">
            <span class="hazard-exclamation">!</span>
          </div>
          <span class="pin-title text-ares-red">${hz.name}</span>
        </div>
      `;

      const hazardIcon = L.divIcon({
        className: "custom-div-icon",
        html: hazardHtml,
        iconSize: [22, 22],
        iconAnchor: [11, 11],
        popupAnchor: [0, -12],
      });

      const marker = L.marker([hz.lat, hz.lon], { icon: hazardIcon });

      const popupHtml = `
        <div class="ares-popup font-mono text-xs">
          <div class="flex items-center justify-between mb-1 pb-1 border-b border-ares-border">
            <span class="font-bold ${isCritical ? "text-ares-red" : "text-ares-amber"} uppercase text-[11px]">${hz.name}</span>
            <span class="px-1.5 py-0.2 rounded text-[9px] font-bold ${isCritical ? "bg-ares-red/30 text-red-300 border border-ares-red/50" : "bg-ares-amber/30 text-amber-300 border border-ares-amber/50"}">${hz.severity}</span>
          </div>
          <div class="text-[10px] text-slate-400 mb-1.5">${hz.type.replace(/_/g, " ")}</div>
          <div class="bg-ares-deep/80 p-1.5 rounded border border-ares-border mb-2 space-y-0.5 text-[10px]">
            <div><strong class="text-slate-400">LAT:</strong> <span class="text-slate-200">${hz.lat >= 0 ? "+" : ""}${hz.lat.toFixed(4)}°N</span></div>
            <div><strong class="text-slate-400">LON:</strong> <span class="text-slate-200">${hz.lon.toFixed(4)}°E</span></div>
            <div><strong class="text-slate-400">RISK:</strong> <span class="text-ares-red">${hz.slopeRisk}</span></div>
          </div>
          <p class="text-[10px] font-sans text-slate-300 leading-snug">${hz.description}</p>
        </div>
      `;

      marker.bindPopup(popupHtml, { className: "ares-leaflet-popup" });
      hGroup.addLayer(marker);
    });
  }

  function updateTargetMarker() {
    if (!map) return;
    if (targetMarker) {
      map.removeLayer(targetMarker);
      targetMarker = null;
    }

    if (!selectedTarget) return;

    const crosshairHtml = `
      <div class="ares-crosshair-marker">
        <div class="ring-pulse"></div>
        <div class="crosshair-center"></div>
      </div>
    `;

    const icon = L.divIcon({
      className: "custom-div-icon",
      html: crosshairHtml,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    });

    targetMarker = L.marker([selectedTarget.lat, selectedTarget.lon], {
      icon,
      zIndexOffset: 1000,
    }).addTo(map);
  }

  function updateRoute() {
    const rGroup = routeGroup;
    if (!map || !rGroup) return;
    rGroup.clearLayers();

    const result = mission.routeResult;
    if (!result || !result.coordinates || result.coordinates.length < 2) return;

    const coords = result.coordinates.map((c) => L.latLng(c.lat, c.lon));

    // Outer glow polyline
    const glowLine = L.polyline(coords, {
      color: "#36C5E8",
      weight: 8,
      opacity: 0.35,
      lineCap: "round",
    });

    // Inner bright dashed line
    const mainLine = L.polyline(coords, {
      color: "#A5E8F5",
      weight: 3.5,
      opacity: 0.95,
      dashArray: "8, 6",
      lineCap: "round",
    });

    rGroup.addLayer(glowLine);
    rGroup.addLayer(mainLine);

    // Start Location Marker (Green Rover)
    const startCoord = result.coordinates[0];
    const startHtml = `
      <div class="ares-route-node rover-start">
        <div class="node-pulse bg-ares-green"></div>
        <div class="node-core bg-ares-green text-ares-deep shadow-[0_0_12px_rgba(84,201,154,0.9)]">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 13h-2V9h-2v4H9V9H7v4H5c-1.1 0-2 .9-2 2v4c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-4c0-1.1-.9-2-2-2zM6 19c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm12 0c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/>
          </svg>
        </div>
        <div class="node-flag">START: ${startCoord.label || "Origin"}</div>
      </div>
    `;

    const startIcon = L.divIcon({
      className: "custom-div-icon",
      html: startHtml,
      iconSize: [30, 30],
      iconAnchor: [15, 15],
      popupAnchor: [0, -18],
    });

    const startMarker = L.marker([startCoord.lat, startCoord.lon], {
      icon: startIcon,
      zIndexOffset: 500,
    });
    startMarker.bindPopup(
      `<div class="font-mono text-xs text-white">
        <strong class="text-ares-green">DEPARTURE WAYPOINT</strong>
        <div class="text-[10px] text-slate-300 mt-1">${startCoord.label || "Start"}</div>
        <div class="text-[10px] text-ares-cyan">${startCoord.lat >= 0 ? "+" : ""}${startCoord.lat.toFixed(4)}°N, ${startCoord.lon.toFixed(4)}°E</div>
      </div>`,
      { className: "ares-leaflet-popup" }
    );
    rGroup.addLayer(startMarker);

    // Destination Marker (Red Flag)
    const endCoord = result.coordinates[result.coordinates.length - 1];
    const endHtml = `
      <div class="ares-route-node route-dest">
        <div class="node-pulse bg-ares-red"></div>
        <div class="node-core bg-ares-red text-white shadow-[0_0_12px_rgba(239,85,85,0.9)]">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6z"/>
          </svg>
        </div>
        <div class="node-flag">DEST: ${endCoord.label || "Arrival"}</div>
      </div>
    `;

    const endIcon = L.divIcon({
      className: "custom-div-icon",
      html: endHtml,
      iconSize: [30, 30],
      iconAnchor: [15, 15],
      popupAnchor: [0, -18],
    });

    const endMarker = L.marker([endCoord.lat, endCoord.lon], {
      icon: endIcon,
      zIndexOffset: 500,
    });
    endMarker.bindPopup(
      `<div class="font-mono text-xs text-white">
        <strong class="text-ares-red">DESTINATION TARGET</strong>
        <div class="text-[10px] text-slate-300 mt-1">${endCoord.label || "Destination"}</div>
        <div class="text-[10px] text-ares-cyan">${endCoord.lat >= 0 ? "+" : ""}${endCoord.lat.toFixed(4)}°N, ${endCoord.lon.toFixed(4)}°E</div>
      </div>`,
      { className: "ares-leaflet-popup" }
    );
    rGroup.addLayer(endMarker);

    // Intermediate Waypoint nodes
    if (result.coordinates.length > 2) {
      for (let i = 1; i < result.coordinates.length - 1; i++) {
        const wp = result.coordinates[i];
        const wpHtml = `
          <div class="ares-route-waypoint">
            <span class="wp-num">${i}</span>
          </div>
        `;
        const wpIcon = L.divIcon({
          className: "custom-div-icon",
          html: wpHtml,
          iconSize: [18, 18],
          iconAnchor: [9, 9],
        });
        rGroup.addLayer(L.marker([wp.lat, wp.lon], { icon: wpIcon }));
      }
    }

    // Auto-fit bounds to display the entire planned route
    fitToRoute();
  }

  function handleZoomIn() {
    map?.zoomIn();
  }

  function handleZoomOut() {
    map?.zoomOut();
  }
</script>

<div class="w-full h-full relative overflow-hidden bg-ares-deep select-none font-mono">
  <!-- The Leaflet Map Mount Container -->
  <div bind:this={mapContainer} class="w-full h-full z-0 bg-ares-deep cursor-crosshair"></div>

  <!-- TOP-LEFT: Region Switcher & Breadcrumb HUD -->
  <div class="absolute top-3 left-3 z-[400] flex flex-wrap items-center gap-2 pointer-events-auto">
    <div class="bg-ares-deep/90 backdrop-blur border border-ares-border rounded-ares p-1 shadow-ares-panel flex items-center gap-1.5">
      <span class="text-[10px] text-slate-400 font-bold px-2 py-0.5 border-r border-ares-border flex items-center gap-1.5">
        <Navigation size={12} class="text-ares-cyan" />
        ZONE:
      </span>
      {#each mission.regions as reg}
        <button
          type="button"
          class="px-2.5 py-1 rounded text-xs transition-all {reg.id === region.id
            ? 'bg-ares-cyan text-ares-deep font-bold shadow-[0_0_8px_rgba(54,197,232,0.5)]'
            : 'text-slate-300 hover:text-white hover:bg-ares-navy'}"
          onclick={() => mission.setActiveRegion(reg.id)}
        >
          {reg.name}
        </button>
      {/each}
    </div>
  </div>

  <!-- TOP-RIGHT: Map Controls Toolbar -->
  {#if showControls}
    <div class="absolute top-3 right-3 z-[400] flex flex-col gap-2 pointer-events-auto items-end">
      <!-- Zoom & Reset -->
      <div class="bg-ares-deep/90 backdrop-blur border border-ares-border rounded-ares p-1 flex flex-col gap-1 shadow-ares-panel">
        <button
          type="button"
          class="p-2 rounded hover:bg-ares-navy text-slate-300 hover:text-ares-cyan transition-colors cursor-pointer"
          title="Zoom In"
          onclick={handleZoomIn}
        >
          <ZoomIn size={16} />
        </button>
        <button
          type="button"
          class="p-2 rounded hover:bg-ares-navy text-slate-300 hover:text-ares-cyan transition-colors cursor-pointer"
          title="Zoom Out"
          onclick={handleZoomOut}
        >
          <ZoomOut size={16} />
        </button>
        <div class="w-full h-px bg-ares-border"></div>
        <button
          type="button"
          class="p-2 rounded hover:bg-ares-navy text-slate-300 hover:text-ares-cyan transition-colors cursor-pointer"
          title="Reset Regional Focus"
          onclick={resetMapView}
        >
          <RotateCcw size={15} />
        </button>
        {#if region.id === "jezero-crater"}
          <button
            type="button"
            class="p-2 rounded hover:bg-ares-navy text-slate-300 hover:text-purple-300 transition-colors cursor-pointer"
            title="Focus 6m CTX Traversal Area"
            onclick={zoomToCtx}
          >
            <Maximize2 size={15} />
          </button>
        {/if}
        {#if mission.routeResult}
          <button
            type="button"
            class="p-2 rounded bg-ares-cyan/20 hover:bg-ares-cyan/30 text-ares-cyan transition-colors cursor-pointer"
            title="Fit Route to Viewport"
            onclick={fitToRoute}
          >
            <Route size={15} />
          </button>
        {/if}
      </div>

      <!-- Layer Toggles -->
      <div class="bg-ares-deep/90 backdrop-blur border border-ares-border rounded-ares p-2 shadow-ares-panel flex flex-col gap-1.5 text-xs text-slate-300 min-w-[170px]">
        <div class="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-0.5 border-b border-ares-border pb-1 flex items-center justify-between">
          <span>DATA LAYERS</span>
          <Layers size={11} class="text-ares-cyan" />
        </div>
        <label class="flex items-center gap-2 cursor-pointer hover:text-white">
          <input
            type="checkbox"
            bind:checked={showPois}
            class="rounded border-ares-border bg-ares-navy text-ares-amber focus:ring-0 w-3.5 h-3.5"
          />
          <span class="text-[11px] flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-ares-amber"></span>
            Science POIs
          </span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer hover:text-white">
          <input
            type="checkbox"
            bind:checked={showHazards}
            class="rounded border-ares-border bg-ares-navy text-ares-red focus:ring-0 w-3.5 h-3.5"
          />
          <span class="text-[11px] flex items-center gap-1.5">
            <span class="w-2 h-2 rotate-45 bg-ares-red"></span>
            Terrain Hazards
          </span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer hover:text-white">
          <input
            type="checkbox"
            bind:checked={showSlopeHeatmap}
            class="rounded border-ares-border bg-ares-navy text-ares-green focus:ring-0 w-3.5 h-3.5"
          />
          <span class="text-[11px] flex items-center gap-1.5">
            <Activity size={12} class="text-ares-green" />
            200m Slope DEM
          </span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer hover:text-white">
          <input
            type="checkbox"
            bind:checked={showElevationTint}
            class="rounded border-ares-border bg-ares-navy text-ares-cyan focus:ring-0 w-3.5 h-3.5"
          />
          <span class="text-[11px] flex items-center gap-1.5">
            <Mountain size={12} class="text-ares-cyan" />
            200m Elevation Tint
          </span>
        </label>

        {#if region.id === 'jezero-crater'}
          <div class="w-full h-px bg-ares-border my-0.5"></div>
          <label class="flex items-center gap-2 cursor-pointer hover:text-white">
            <input
              type="checkbox"
              bind:checked={showCtxOverlay}
              class="rounded border-ares-border bg-ares-navy text-slate-200 focus:ring-0 w-3.5 h-3.5"
            />
            <span class="text-[11px] flex items-center gap-1.5 text-slate-200">
              <span class="w-2 h-2 rounded-sm bg-slate-400"></span>
              6m Jezero CTX (MRO)
            </span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer hover:text-white">
            <input
              type="checkbox"
              bind:checked={showCrismSites}
              class="rounded border-ares-border bg-ares-navy text-purple-400 focus:ring-0 w-3.5 h-3.5"
            />
            <span class="text-[11px] flex items-center gap-1.5 text-purple-300">
              <Sparkles size={12} class="text-purple-400" />
              CRISM Hydrous Sites
            </span>
          </label>
        {/if}
      </div>
    </div>
  {/if}

  <!-- ACTIVE ROUTE TELEMETRY HUD (Appears when route is planned) -->
  {#if mission.routeResult}
    <div class="absolute top-16 left-3 z-[400] bg-ares-deep/95 backdrop-blur border border-ares-cyan/40 rounded-ares p-3 shadow-[0_0_15px_rgba(8,13,22,0.9)] max-w-sm pointer-events-auto">
      <div class="flex items-center justify-between gap-3 mb-2 pb-1.5 border-b border-ares-border">
        <div class="flex items-center gap-1.5">
          <Route size={14} class="text-ares-cyan" />
          <span class="text-xs font-bold text-white uppercase tracking-wider">ACTIVE TRAVERSAL ROUTE</span>
        </div>
        <span class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-ares-cyan/20 text-ares-cyan border border-ares-cyan/40 uppercase">
          {mission.routeResult.priority_used}
        </span>
      </div>

      <div class="grid grid-cols-2 gap-2 text-xs mb-2">
        <div class="bg-ares-navy/60 p-1.5 rounded border border-ares-border">
          <span class="text-[9px] text-slate-400 block">TOTAL DISTANCE</span>
          <strong class="text-ares-green text-sm">{mission.routeResult.total_distance_km.toFixed(2)} km</strong>
        </div>
        <div class="bg-ares-navy/60 p-1.5 rounded border border-ares-border">
          <span class="text-[9px] text-slate-400 block">EST. DURATION</span>
          <strong class="text-ares-cyan text-sm">{mission.routeResult.travel_time?.estimated_duration_min ?? '--'} min</strong>
        </div>
      </div>

      {#if routeSlope}
        <div class="bg-ares-navy/40 p-1.5 rounded border border-ares-border text-[10px] flex items-center justify-between mb-2">
          <span class="text-slate-400">MEASURED SLOPE:</span>
          <span class="text-ares-cyan font-bold">
            Mean {routeSlope.mean_slope_deg.toFixed(1)}° | Max {routeSlope.max_slope_deg.toFixed(1)}°
          </span>
        </div>
      {/if}

      {#if mission.routeResult.warnings.length > 0}
        <div class="text-[10px] text-amber-300/90 flex items-start gap-1 bg-ares-amber/10 p-1.5 rounded border border-ares-amber/30">
          <AlertTriangle size={12} class="text-ares-amber shrink-0 mt-0.5" />
          <span class="leading-tight">{mission.routeResult.warnings[0]}</span>
        </div>
      {/if}
    </div>
  {/if}

  <!-- BOTTOM-LEFT: Interactive Point Inspector & Real DEM Elevation readout -->
  {#if clickedPointInfo}
    <div class="absolute bottom-10 left-3 z-[400] bg-ares-deep/95 backdrop-blur border border-ares-border rounded-ares p-3 shadow-ares-panel pointer-events-auto max-w-xs animate-in fade-in slide-in-from-bottom-2">
      <div class="flex items-center justify-between gap-2 mb-1.5 pb-1 border-b border-ares-border">
        <span class="text-[10px] text-ares-cyan font-bold flex items-center gap-1">
          <Crosshair size={12} />
          SURFACE INSPECTION
        </span>
        <button
          type="button"
          class="text-slate-400 hover:text-white text-xs px-1 cursor-pointer"
          onclick={() => (clickedPointInfo = null)}
        >
          ✕
        </button>
      </div>

      <div class="space-y-1.5 text-xs">
        <div class="flex justify-between text-[11px]">
          <span class="text-slate-400">COORDINATE:</span>
          <span class="text-white font-bold">{clickedPointInfo.lat >= 0 ? "+" : ""}{clickedPointInfo.lat.toFixed(4)}°N, {clickedPointInfo.lon.toFixed(4)}°E</span>
        </div>

        {#if clickedPointInfo.loading}
          <div class="text-[10px] text-ares-cyan animate-pulse py-1">Querying USGS 200m DEM...</div>
        {:else if clickedPointInfo.elevation_m !== null}
          <div class="flex justify-between text-[11px]">
            <span class="text-slate-400">ELEVATION:</span>
            <span class="text-ares-green font-bold">{clickedPointInfo.elevation_m > 0 ? '+' : ''}{clickedPointInfo.elevation_m.toFixed(0)} m (Areoid)</span>
          </div>
          {#if clickedPointInfo.slope_deg !== null}
            <div class="flex justify-between text-[11px]">
              <span class="text-slate-400">SLOPE GRADIENT:</span>
              <span class="font-bold {clickedPointInfo.slope_deg > 15 ? 'text-ares-red' : clickedPointInfo.slope_deg > 5 ? 'text-ares-amber' : 'text-ares-cyan'}">
                {clickedPointInfo.slope_deg.toFixed(1)}°
              </span>
            </div>
          {/if}

          {#if clickedPointInfo.difficulty_level}
            <div class="flex justify-between items-center text-[10px] pt-0.5 border-t border-ares-border/50">
              <span class="text-slate-400">TERRAIN TIER:</span>
              <span class="px-1.5 py-0.2 rounded font-bold {clickedPointInfo.difficulty_level.includes('LEVEL 4') ? 'bg-ares-red/30 text-red-300 border border-ares-red/40' : clickedPointInfo.difficulty_level.includes('LEVEL 3') ? 'bg-ares-amber/30 text-amber-300 border border-ares-amber/40' : 'bg-ares-green/20 text-green-300 border border-ares-green/30'}">
                {clickedPointInfo.difficulty_level}
              </span>
            </div>
          {/if}

          {#if clickedPointInfo.slip_risk}
            <div class="flex justify-between text-[10px]">
              <span class="text-slate-400">WHEEL SLIP RISK:</span>
              <span class="text-slate-200">{clickedPointInfo.slip_risk}</span>
            </div>
          {/if}

          {#if clickedPointInfo.traversability_rating}
            <div class="flex justify-between text-[10px]">
              <span class="text-slate-400">TRAVERSABILITY:</span>
              <span class="text-ares-cyan font-bold">{clickedPointInfo.traversability_rating}</span>
            </div>
          {/if}

          <div class="text-[9px] text-slate-500 pt-1 border-t border-ares-border/40">
            Source: {clickedPointInfo.source || 'USGS MOLA-HRSC 200m Blended DEM'}
          </div>
        {:else}
          <div class="text-[10px] text-slate-500 italic py-1">DEM elevation unavailable at this coordinate (outside 200m regional grid)</div>
        {/if}
      </div>

      <!-- Quick Action Buttons -->
      <div class="flex gap-1.5 mt-2 pt-1.5 border-t border-ares-border">
        <button
          type="button"
          class="flex-1 py-1 px-1.5 rounded bg-ares-cyan/20 hover:bg-ares-cyan/30 text-ares-cyan text-[10px] font-bold border border-ares-cyan/40 text-center cursor-pointer"
          onclick={() => {
            if (clickedPointInfo) {
              window.dispatchEvent(
                new CustomEvent("ares-set-start", {
                  detail: {
                    name: `Coord (${clickedPointInfo.lat.toFixed(2)}, ${clickedPointInfo.lon.toFixed(2)})`,
                    lat: clickedPointInfo.lat,
                    lon: clickedPointInfo.lon,
                  },
                })
              );
            }
          }}
        >
          SET AS START
        </button>
        <button
          type="button"
          class="flex-1 py-1 px-1.5 rounded bg-ares-amber/20 hover:bg-ares-amber/30 text-ares-amber text-[10px] font-bold border border-ares-amber/40 text-center cursor-pointer"
          onclick={() => {
            if (clickedPointInfo) {
              window.dispatchEvent(
                new CustomEvent("ares-set-dest", {
                  detail: {
                    name: `Coord (${clickedPointInfo.lat.toFixed(2)}, ${clickedPointInfo.lon.toFixed(2)})`,
                    lat: clickedPointInfo.lat,
                    lon: clickedPointInfo.lon,
                  },
                })
              );
            }
          }}
        >
          SET AS DEST
        </button>
      </div>
    </div>
  {/if}

  <!-- BOTTOM-RIGHT: Tactical Legend & Scale -->
  {#if showLegend}
    <div class="absolute bottom-10 right-3 z-[400] bg-ares-deep/90 backdrop-blur border border-ares-border rounded-ares p-2.5 shadow-ares-panel pointer-events-auto text-[10px] text-slate-300 flex flex-col gap-1.5 max-w-[210px]">
      <div class="flex items-center justify-between gap-2 border-b border-ares-border pb-1 font-bold text-slate-400">
        <span>CARTOGRAPHY LEGEND</span>
        <button type="button" class="text-slate-500 hover:text-white cursor-pointer" onclick={() => (showLegend = false)}>✕</button>
      </div>
      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full bg-ares-cyan border border-white"></span>
        <span>Historical Landing Site</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full bg-ares-amber border border-white"></span>
        <span>Science Exploration Site</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rotate-45 bg-ares-red border border-white"></span>
        <span>Environmental Hazard</span>
      </div>
      {#if region.id === 'jezero-crater' && showCrismSites}
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rotate-45 bg-[#9333ea] border border-[#d8b4fe]"></span>
          <span class="text-purple-300">CRISM Hydrous Mineral Site</span>
        </div>
      {/if}
      <div class="flex items-center gap-2">
        <span class="w-4 h-0.5 bg-ares-cyan border-b border-white"></span>
        <span>Computed Traversal Route</span>
      </div>
      {#if showSlopeHeatmap}
        <div class="mt-1 pt-1 border-t border-ares-border space-y-1">
          <span class="text-[9px] text-slate-400 block font-bold">200m SLOPE GRADIENTS:</span>
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-1.5 rounded-sm bg-[#54C99A]"></span>
            <span>&lt; 5° (Traversable Bedrock)</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-1.5 rounded-sm bg-[#F2A93B]"></span>
            <span>5° – 15° (Moderate Slope)</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-1.5 rounded-sm bg-[#EF5555]"></span>
            <span>&gt; 15° (Kinematic Slip Risk)</span>
          </div>
        </div>
      {/if}
      {#if showElevationTint}
        <div class="mt-1 pt-1 border-t border-ares-border space-y-1">
          <span class="text-[9px] text-slate-400 block font-bold">200m ELEVATION TINT:</span>
          <div class="h-2 rounded bg-gradient-to-r from-blue-700 via-teal-500 via-emerald-400 via-yellow-400 to-amber-600"></div>
          <div class="flex justify-between text-[8px] text-slate-400">
            <span>Low Basin</span>
            <span>High Peak</span>
          </div>
        </div>
      {/if}
      {#if showCtxOverlay && region.id === 'jezero-crater'}
        <div class="mt-1 pt-1 border-t border-ares-border text-[9px] text-slate-400">
          <span class="font-bold text-slate-200">6m CTX:</span> MRO High-Res (~30km Jezero swath)
        </div>
      {/if}
    </div>
  {:else}
    <button
      type="button"
      class="absolute bottom-10 right-3 z-[400] bg-ares-deep/90 border border-ares-border rounded-ares p-1.5 text-[10px] text-slate-400 hover:text-white shadow-ares-panel pointer-events-auto cursor-pointer"
      onclick={() => (showLegend = true)}
    >
      LEGEND
    </button>
  {/if}

  <!-- BOTTOM STATUS STRIP: Live Coordinate Cursor & Planetary Baseline -->
  <div class="absolute bottom-0 left-0 right-0 z-[400] bg-ares-deep/95 backdrop-blur border-t border-ares-border px-3 py-1.5 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-400 pointer-events-auto">
    <div class="flex items-center gap-4">
      <span class="flex items-center gap-1.5">
        <Crosshair size={13} class="text-ares-cyan" />
        {#if hoverLatLon}
          <strong class="text-white">{hoverLatLon.lat >= 0 ? "+" : ""}{hoverLatLon.lat.toFixed(4)}°N, {hoverLatLon.lon.toFixed(4)}°E</strong>
        {:else}
          <span class="text-slate-500">CURSOR OUTSIDE FRAME</span>
        {/if}
      </span>
      <span class="hidden md:inline text-slate-600">|</span>
      <span class="hidden md:inline text-slate-400">
        RADIUS: 3,389.5 km (IAU Mean)
      </span>
    </div>

    <div class="flex items-center gap-3 text-[10px]">
      <span class="text-slate-400 hidden sm:inline">
        BASEMAP: MOLA MEG256
        {#if showSlopeHeatmap} + Slope DEM{/if}
        {#if showElevationTint} + Elev Tint{/if}
        {#if showCtxOverlay} + 6m CTX{/if}
      </span>
      {#if mission.routeResult}
        <span class="text-ares-green font-bold flex items-center gap-1">
          <Route size={11} />
          ROUTE RENDERED ({mission.routeResult.segments.length} LEGS)
        </span>
      {/if}
    </div>
  </div>
</div>

<style>
  :global(.leaflet-container) {
    background-color: #080d16 !important;
    font-family: inherit;
  }

  :global(.ares-basemap-layer) {
    filter: brightness(0.95) contrast(1.08);
  }

  :global(.ares-ctx-layer) {
    filter: brightness(1.05) contrast(1.15);
  }

  :global(.ares-elevation-tint-layer) {
    mix-blend-mode: screen;
  }

  :global(.custom-div-icon) {
    background: transparent;
    border: none;
  }

  :global(.ares-map-pin) {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
  }

  :global(.crism-pin .pin-gem) {
    width: 14px;
    height: 14px;
    transform: rotate(45deg);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 2px;
    transition: transform 0.15s ease-out;
  }

  :global(.crism-pin:hover .pin-gem) {
    transform: rotate(45deg) scale(1.3);
  }

  :global(.ares-map-pin .pin-core) {
    width: 14px;
    height: 14px;
    border-radius: 9999px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.15s ease-out;
  }

  :global(.ares-map-pin:hover .pin-core) {
    transform: scale(1.3);
  }

  :global(.ares-map-pin .pin-pulse) {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 24px;
    height: 24px;
    border-radius: 9999px;
    background: rgba(54, 197, 232, 0.35);
    animation: aresPulse 2s infinite ease-out;
    pointer-events: none;
  }

  :global(.ares-map-pin .pin-title) {
    position: absolute;
    top: 16px;
    white-space: nowrap;
    font-size: 9px;
    font-weight: 700;
    color: #e2e8f0;
    background: rgba(8, 13, 22, 0.85);
    padding: 1px 4px;
    border-radius: 2px;
    border: 1px solid #1e2d42;
    pointer-events: none;
  }

  :global(.ares-map-pin.hazard-pin .pin-diamond) {
    width: 13px;
    height: 13px;
    transform: rotate(45deg);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1.5px solid #ffffff;
    transition: transform 0.15s ease-out;
  }

  :global(.ares-map-pin.hazard-pin:hover .pin-diamond) {
    transform: rotate(45deg) scale(1.3);
  }

  :global(.hazard-exclamation) {
    transform: rotate(-45deg);
    font-size: 8px;
    font-weight: 900;
    color: #ffffff;
    line-height: 1;
  }

  :global(.ares-route-node) {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
  }

  :global(.ares-route-node .node-core) {
    width: 22px;
    height: 22px;
    border-radius: 9999px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #ffffff;
    z-index: 2;
  }

  :global(.ares-route-node .node-pulse) {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 34px;
    height: 34px;
    border-radius: 9999px;
    opacity: 0.4;
    animation: aresPulse 1.8s infinite ease-out;
  }

  :global(.ares-route-node .node-flag) {
    position: absolute;
    bottom: 24px;
    white-space: nowrap;
    font-size: 10px;
    font-weight: 800;
    background: rgba(8, 13, 22, 0.95);
    padding: 2px 6px;
    border-radius: 3px;
    border: 1px solid #36c5e8;
    color: #ffffff;
  }

  :global(.ares-route-waypoint) {
    width: 14px;
    height: 14px;
    border-radius: 9999px;
    background: #101a29;
    border: 2px solid #36c5e8;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 6px rgba(54, 197, 232, 0.8);
  }

  :global(.ares-route-waypoint .wp-num) {
    font-size: 8px;
    font-weight: 800;
    color: #36c5e8;
  }

  :global(.ares-crosshair-marker) {
    width: 24px;
    height: 24px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  :global(.ares-crosshair-marker .crosshair-center) {
    width: 6px;
    height: 6px;
    border-radius: 9999px;
    background: #36c5e8;
    border: 1.5px solid #ffffff;
  }

  :global(.ares-crosshair-marker .ring-pulse) {
    position: absolute;
    width: 24px;
    height: 24px;
    border-radius: 9999px;
    border: 1.5px dashed #36c5e8;
    animation: spin 10s linear infinite;
  }

  :global(.ares-leaflet-popup .leaflet-popup-content-wrapper) {
    background: rgba(16, 26, 41, 0.95) !important;
    backdrop-filter: blur(8px);
    border: 1px solid #1e2d42 !important;
    border-radius: 6px !important;
    color: #f1f5f9 !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.7) !important;
    padding: 4px !important;
  }

  :global(.ares-leaflet-popup .leaflet-popup-tip) {
    background: rgba(16, 26, 41, 0.95) !important;
    border: 1px solid #1e2d42 !important;
  }

  :global(.ares-leaflet-popup .leaflet-popup-close-button) {
    color: #94a3b8 !important;
    padding: 6px !important;
  }

  :global(.ares-leaflet-popup .leaflet-popup-close-button:hover) {
    color: #ffffff !important;
  }

  @keyframes aresPulse {
    0% {
      transform: translate(-50%, -50%) scale(0.6);
      opacity: 0.8;
    }
    100% {
      transform: translate(-50%, -50%) scale(1.6);
      opacity: 0;
    }
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
</style>
