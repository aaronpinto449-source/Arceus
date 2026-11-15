<script lang="ts">
  import { mission } from "../../stores/mission.svelte";
  import type {
    RoutePriority,
    RoverType,
    SlopeAnalysisData,
    ElevationProfileData,
  } from "../../types";
  import { REGIONAL_HAZARDS } from "../../data/hazards";
  import {
    Compass,
    Info,
    AlertTriangle,
    ShieldAlert,
    Route,
    CheckCircle2,
    XCircle,
    ArrowRight,
    MapPin,
    Clock,
    Zap,
    ExternalLink,
    RefreshCw,
    Gauge,
    TrendingUp,
    TrendingDown,
    Mountain,
    Activity,
    Sparkles,
    Layers,
  } from "@lucide/svelte";
  import Card from "../ui/Card.svelte";
  import Button from "../ui/Button.svelte";
  import Badge from "../ui/Badge.svelte";
  import MarsCanvas from "../explorer/MarsCanvas.svelte";

  let startPoiName = $state(mission.currentPois[0]?.name || "Bradbury Landing");
  let destPoiName = $state(
    mission.currentPois[1]?.name || "Mount Sharp Base (Aeolis Mons)",
  );
  let vehicleType = $state<RoverType>("PCR");
  let traversalPriority = $state<RoutePriority>("BALANCED");

  let customStart = $state<{ name: string; lat: number; lon: number } | null>(
    null,
  );
  let customDest = $state<{ name: string; lat: number; lon: number } | null>(
    null,
  );

  $effect(() => {
    const handleSetStart = (e: any) => {
      if (e.detail) {
        customStart = e.detail;
        startPoiName = e.detail.name;
      }
    };
    const handleSetDest = (e: any) => {
      if (e.detail) {
        customDest = e.detail;
        destPoiName = e.detail.name;
      }
    };
    window.addEventListener("ares-set-start", handleSetStart);
    window.addEventListener("ares-set-dest", handleSetDest);
    return () => {
      window.removeEventListener("ares-set-start", handleSetStart);
      window.removeEventListener("ares-set-dest", handleSetDest);
    };
  });

  $effect(() => {
    if (mission.currentPois.length >= 2) {
      if (!mission.currentPois.some((p) => p.name === startPoiName)) {
        startPoiName = mission.currentPois[0].name;
      }
      if (!mission.currentPois.some((p) => p.name === destPoiName)) {
        destPoiName = mission.currentPois[1].name;
      }
    }
  });

  const vehicles: {
    id: RoverType;
    name: string;
    speed: string;
    range: string;
    crew: string;
  }[] = [
    {
      id: "PCR",
      name: "Pressurized Crew Rover (PCR-1)",
      speed: "12 km/h",
      range: "120 km",
      crew: "2 Astronauts",
    },
    {
      id: "LUV",
      name: "Lightweight Unpressurized Scout (LUV)",
      speed: "18 km/h",
      range: "45 km",
      crew: "1 EVA Suit",
    },
    {
      id: "HCH",
      name: "Heavy Cargo & Habitat Hauler (HCH)",
      speed: "6 km/h",
      range: "80 km",
      crew: "4 Crew / Cargo",
    },
  ];

  const selectedVehicle = $derived(
    vehicles.find((v) => v.id === vehicleType) || vehicles[0],
  );

  const startPoi = $derived(
    mission.currentPois.find((p) => p.name === startPoiName),
  );
  const destPoi = $derived(
    mission.currentPois.find((p) => p.name === destPoiName),
  );

  const slopeData = $derived(
    mission.routeResult?.slope_data?.supported
      ? (mission.routeResult.slope_data as SlopeAnalysisData)
      : null,
  );

  const elevProfile = $derived(
    mission.routeResult?.elevation_profile?.supported
      ? (mission.routeResult.elevation_profile as ElevationProfileData)
      : null,
  );

  const nearbyHazards = $derived.by(() => {
    const hazards = REGIONAL_HAZARDS[mission.currentRegion.id] || [];
    if (
      !mission.routeResult ||
      !mission.routeResult.coordinates ||
      mission.routeResult.coordinates.length < 2
    ) {
      return [];
    }
    const coords = mission.routeResult.coordinates;

    return hazards
      .map((h) => {
        let minD = 999999;
        for (const c of coords) {
          const dLat = (c.lat - h.lat) * (Math.PI / 180.0);
          const dLon = (c.lon - h.lon) * (Math.PI / 180.0);
          const latMid = ((c.lat + h.lat) / 2.0) * (Math.PI / 180.0);
          const x = dLon * Math.cos(latMid);
          const y = dLat;
          const distKm = Math.sqrt(x * x + y * y) * 3389.5;
          if (distKm < minD) minD = distKm;
        }
        return {
          ...h,
          distanceToRouteKm: Math.round(minD * 10) / 10,
        };
      })
      .sort((a, b) => a.distanceToRouteKm - b.distanceToRouteKm);
  });

  const profileSvg = $derived.by(() => {
    if (!elevProfile || !elevProfile.samples || elevProfile.samples.length < 2)
      return null;
    const samples = elevProfile.samples;
    const minE = elevProfile.min_elevation_m;
    const maxE = elevProfile.max_elevation_m;
    const range = maxE - minE || 1.0;
    const totalDist = mission.routeResult?.total_distance_km || 1.0;

    const w = 560;
    const h = 130;
    const padX = 35;
    const padY = 18;
    const plotW = w - 2 * padX;
    const plotH = h - 2 * padY;

    const points = samples.map((s) => {
      const px = padX + (s.distance_km / totalDist) * plotW;
      const py = padY + plotH - ((s.elevation_m - minE) / range) * plotH;
      return `${px.toFixed(1)},${py.toFixed(1)}`;
    });

    const pathD = `M ${points.join(" L ")}`;
    const areaD = `M ${padX},${padY + plotH} L ${points.join(" L ")} L ${padX + plotW},${padY + plotH} Z`;

    return {
      w,
      h,
      pathD,
      areaD,
      minE,
      maxE,
      startE: samples[0].elevation_m,
      endE: samples[samples.length - 1].elevation_m,
    };
  });

  async function handleComputeRoute() {
    const startCoord =
      customStart ||
      (startPoi
        ? { lat: startPoi.lat, lon: startPoi.lon, name: startPoi.name }
        : null);
    const destCoord =
      customDest ||
      (destPoi
        ? { lat: destPoi.lat, lon: destPoi.lon, name: destPoi.name }
        : null);

    if (!startCoord || !destCoord) {
      mission.routeError =
        "Please select valid Departure and Destination coordinates.";
      return;
    }

    if (
      Math.abs(startCoord.lat - destCoord.lat) < 1e-6 &&
      Math.abs(startCoord.lon - destCoord.lon) < 1e-6
    ) {
      mission.routeError =
        "Departure and Destination points must be different.";
      return;
    }

    await mission.planRoute(
      { lat: startCoord.lat, lon: startCoord.lon },
      { lat: destCoord.lat, lon: destCoord.lon },
      vehicleType,
      traversalPriority,
    );
  }

  function handleViewOnMap() {
    mission.setActivePage("Mars Explorer");
  }
</script>

<div class="p-4 md:p-6 flex flex-col gap-5 max-w-7xl mx-auto">
  <!-- Scientific Transparency Notice Banner -->
  <div
    class="ares-panel p-4 border-l-4 border-l-ares-cyan flex items-start gap-3 text-xs leading-relaxed text-slate-300"
  >
    <Info size={18} class="text-ares-cyan shrink-0 mt-0.5" />
    <div class="space-y-1">
      <div class="flex items-center gap-2">
        <span
          class="text-white font-title font-bold uppercase tracking-wider text-xs"
        >
          EXPEDITION ROUTE PLANNING SYSTEM
        </span>
        <Badge provenance="calculated" label="IAU GEODESY" />
        <Badge provenance="estimated" label="FLAT-GROUND SPEED" />
      </div>
      <p class="font-sans text-slate-300 text-[11px]">
        Route legs are geometric great-circle approximations on a spherical Mars
        model (IAU mean radius 3389.5 km). Topographical slope, elevation
        models, and real-time hazard layers are explicitly flagged as
        unavailable.
      </p>
    </div>
  </div>

  <!-- Error Alert Banner -->
  {#if mission.routeError}
    <div
      class="ares-panel p-3.5 border-l-4 border-l-ares-red bg-ares-red/10 flex items-start justify-between gap-3 text-xs text-red-200"
    >
      <div class="flex items-center gap-2.5">
        <AlertTriangle size={18} class="text-ares-red shrink-0" />
        <div>
          <strong class="text-white block font-mono"
            >ROUTE PLANNING FAILED:</strong
          >
          <span>{mission.routeError}</span>
        </div>
      </div>
      <button
        onclick={handleComputeRoute}
        class="px-2.5 py-1 rounded bg-ares-red/20 hover:bg-ares-red/30 border border-ares-red text-white text-[11px] font-mono flex items-center gap-1.5 transition-colors cursor-pointer shrink-0"
      >
        <RefreshCw size={12} />
        RETRY
      </button>
    </div>
  {/if}

  <!-- INTERACTIVE MARS NAVIGATION MAP (MAIN CENTRAL WORKSPACE) -->
  <div class="ares-panel p-2 flex flex-col gap-2 shadow-ares-panel">
    <div class="flex flex-wrap items-center justify-between px-2 pt-1 gap-2">
      <div class="flex items-center gap-2">
        <Route size={16} class="text-ares-cyan" />
        <span
          class="font-title font-bold text-white text-sm uppercase tracking-wider"
        >
          INTERACTIVE MARS NAVIGATION MAP — {mission.currentRegion.name}
        </span>
        {#if mission.routeResult}
          <Badge provenance="calculated" label="ACTIVE TRAVERSAL ROUTE" />
        {/if}
      </div>
      <div class="text-[11px] font-mono text-slate-400">
        Interactive Leaflet Map • Click any POI or coordinate to set Start/Dest
        • Drag to pan • Scroll to zoom
      </div>
    </div>

    <div
      class="h-[460px] md:h-[560px] w-full rounded-ares border border-ares-border overflow-hidden relative shadow-inner"
    >
      <MarsCanvas
        region={mission.currentRegion}
        pois={mission.currentPois}
        selectedTarget={mission.selectedTarget}
        onSelectTarget={(target) => mission.selectTarget(target)}
      />
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
    <!-- Left Column: Expedition Parameters Configuration -->
    <Card variant="panel" title="TRAVERSAL CONFIGURATION">
      {#snippet headerRight()}
        <Compass size={16} class="text-ares-cyan" />
      {/snippet}

      <div class="space-y-4 font-mono text-xs">
        <!-- Departure POI -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label
              for="departure-select"
              class="hud-label text-slate-300 block"
            >
              DEPARTURE POINT (START WAYPOINT)
            </label>
            {#if customStart}
              <button
                type="button"
                class="text-[9px] text-ares-cyan underline hover:text-white"
                onclick={() => {
                  customStart = null;
                  startPoiName = mission.currentPois[0]?.name || "";
                }}
              >
                Reset to POI
              </button>
            {/if}
          </div>
          {#if customStart}
            <div
              class="w-full bg-ares-deep border border-ares-green rounded-ares px-3 py-2 text-xs font-mono text-ares-green flex items-center justify-between"
            >
              <span>{customStart.name}</span>
              <span class="text-[10px] text-slate-400">MAP PINNED</span>
            </div>
          {:else}
            <select
              id="departure-select"
              bind:value={startPoiName}
              onchange={() => {
                customStart = null;
              }}
              class="w-full bg-ares-deep border border-ares-border rounded-ares px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-ares-cyan cursor-pointer"
            >
              {#each mission.currentPois as p}
                <option value={p.name}>
                  {p.name} ({p.type})
                </option>
              {/each}
            </select>
          {/if}
          {#if startPoi && !customStart}
            <div
              class="text-[10px] text-slate-400 flex items-center gap-1 px-1"
            >
              <MapPin size={10} class="text-ares-green" />
              <span
                >{startPoi.lat.toFixed(2)}°N, {startPoi.lon.toFixed(2)}°E</span
              >
            </div>
          {/if}
        </div>

        <!-- Destination POI -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label for="dest-select" class="hud-label text-slate-300 block">
              TARGET DESTINATION (END WAYPOINT)
            </label>
            {#if customDest}
              <button
                type="button"
                class="text-[9px] text-ares-cyan underline hover:text-white"
                onclick={() => {
                  customDest = null;
                  destPoiName = mission.currentPois[1]?.name || "";
                }}
              >
                Reset to POI
              </button>
            {/if}
          </div>
          {#if customDest}
            <div
              class="w-full bg-ares-deep border border-ares-red rounded-ares px-3 py-2 text-xs font-mono text-ares-red flex items-center justify-between"
            >
              <span>{customDest.name}</span>
              <span class="text-[10px] text-slate-400">MAP PINNED</span>
            </div>
          {:else}
            <select
              id="dest-select"
              bind:value={destPoiName}
              onchange={() => {
                customDest = null;
              }}
              class="w-full bg-ares-deep border border-ares-border rounded-ares px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-ares-cyan cursor-pointer"
            >
              {#each mission.currentPois as p}
                <option value={p.name}>
                  {p.name} ({p.type})
                </option>
              {/each}
            </select>
          {/if}
          {#if destPoi && !customDest}
            <div
              class="text-[10px] text-slate-400 flex items-center gap-1 px-1"
            >
              <MapPin size={10} class="text-ares-cyan" />
              <span>{destPoi.lat.toFixed(2)}°N, {destPoi.lon.toFixed(2)}°E</span
              >
            </div>
          {/if}
        </div>

        <!-- Vehicle Selector -->
        <div class="space-y-1.5">
          <label for="vehicle-select" class="hud-label text-slate-300 block">
            SURFACE VEHICLE CONFIGURATION
          </label>
          <select
            id="vehicle-select"
            bind:value={vehicleType}
            class="w-full bg-ares-deep border border-ares-border rounded-ares px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-ares-cyan cursor-pointer"
          >
            {#each vehicles as v}
              <option value={v.id}>{v.name} — {v.speed}</option>
            {/each}
          </select>
        </div>

        <!-- Traversal Priority Preference -->
        <div class="space-y-1.5">
          <span class="hud-label text-slate-300 block"
            >PLANNING PREFERENCE (OBJECTIVE)</span
          >
          <div class="space-y-1.5 font-mono text-xs">
            {#each [{ id: "BALANCED", label: "BALANCED (POI Graph Dijkstra)", desc: "Routes via verified intermediate POIs" }, { id: "DISTANCE", label: "DISTANCE (Direct Haversine)", desc: "Straight line between start and dest" }, { id: "SAFETY", label: "SAFETY (POI Graph + Survey Warning)", desc: "Recommends pre-survey reconnaissance" }] as opt}
              <label
                class="flex flex-col p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border cursor-pointer hover:bg-ares-elevated transition-colors"
              >
                <div class="flex items-center gap-2">
                  <input
                    type="radio"
                    name="priority"
                    value={opt.id}
                    bind:group={traversalPriority}
                    class="text-ares-cyan focus:ring-0"
                  />
                  <span class="text-white text-xs font-bold">{opt.label}</span>
                </div>
                <span class="text-slate-400 text-[10px] ml-5 mt-0.5"
                  >{opt.desc}</span
                >
              </label>
            {/each}
          </div>
        </div>

        <!-- Action Button -->
        <div class="pt-2">
          <button
            onclick={handleComputeRoute}
            disabled={mission.routeLoading ||
              !startPoi ||
              !destPoi ||
              startPoi.name === destPoi.name}
            class="w-full py-2.5 px-4 rounded-ares bg-ares-cyan hover:bg-ares-cyan/90 disabled:bg-slate-700 disabled:cursor-not-allowed text-ares-deep font-title font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all cursor-pointer shadow-lg shadow-ares-cyan/10"
          >
            {#if mission.routeLoading}
              <RefreshCw size={15} class="animate-spin" />
              <span>COMPUTING ROUTE...</span>
            {:else}
              <Route size={15} />
              <span>CALCULATE EXPEDITION ROUTE</span>
            {/if}
          </button>
        </div>
      </div>
    </Card>

    <!-- Right 2 Columns: Status, Plan Output & Route Analysis -->
    <div class="lg:col-span-2 space-y-4">
      <!-- Top Telemetry Status Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="ares-panel p-3">
          <div class="hud-label text-slate-400">PLANNING STATE</div>
          {#if mission.routeResult}
            <div
              class="text-sm font-mono font-bold text-ares-green mt-1 flex items-center gap-1.5"
            >
              <CheckCircle2 size={14} /> ACTIVE PLAN
            </div>
            <div class="text-[10px] font-mono text-slate-400 mt-0.5 truncate">
              {mission.routeResult.algorithm_used}
            </div>
          {:else if mission.routeLoading}
            <div
              class="text-sm font-mono font-bold text-ares-cyan mt-1 flex items-center gap-1.5"
            >
              <RefreshCw size={14} class="animate-spin" /> SOLVING
            </div>
            <div class="text-[10px] font-mono text-slate-400 mt-0.5">
              Connecting API...
            </div>
          {:else}
            <div class="text-sm font-mono font-bold text-ares-amber mt-1">
              CONFIGURED
            </div>
            <div class="text-[10px] font-mono text-slate-400 mt-0.5">
              Ready for plan request
            </div>
          {/if}
        </div>

        <div class="ares-panel p-3">
          <div class="hud-label text-slate-400">TOTAL DISTANCE</div>
          {#if mission.routeResult}
            <div class="text-sm font-mono font-bold text-ares-cyan mt-1">
              {mission.routeResult.total_distance_km.toFixed(2)} km
            </div>
            <Badge provenance="calculated" label="HAVERSINE" />
          {:else}
            <div class="text-sm font-mono text-slate-400 mt-1">--</div>
            <div class="text-[10px] font-mono text-slate-500 mt-0.5">
              Awaiting solve
            </div>
          {/if}
        </div>

        <div class="ares-panel p-3">
          <div class="hud-label text-slate-400">ESTIMATED TIME</div>
          {#if mission.routeResult?.travel_time}
            <div class="text-sm font-mono font-bold text-white mt-1">
              {mission.routeResult.travel_time.estimated_duration_min.toFixed(
                0,
              )} min
            </div>
            <div class="text-[10px] font-mono text-slate-400 mt-0.5">
              ({mission.routeResult.travel_time.estimated_duration_hrs.toFixed(
                1,
              )} hrs @ {mission.routeResult.travel_time.rover_nominal_speed_kmh}
              km/h)
            </div>
          {:else}
            <div class="text-sm font-mono text-slate-400 mt-1">--</div>
            <div class="text-[10px] font-mono text-slate-500 mt-0.5">
              Flat terrain model
            </div>
          {/if}
        </div>

        <div class="ares-panel p-3">
          <div class="hud-label text-slate-400">VEHICLE RANGE & RETURN</div>
          {#if mission.routeResult?.feasibility}
            {#if mission.routeResult.feasibility.within_range}
              <div
                class="text-sm font-mono font-bold text-ares-green mt-1 flex items-center gap-1"
              >
                <CheckCircle2 size={13} />
                {mission.routeResult.feasibility.return_feasible
                  ? "RETURN FEASIBLE"
                  : "1-WAY ONLY"}
              </div>
              <div class="text-[10px] font-mono text-slate-400 mt-0.5">
                {#if mission.routeResult.feasibility.return_trip_km}
                  Round: {mission.routeResult.feasibility.return_trip_km.toFixed(1)} km ({(mission.routeResult.feasibility.return_margin_km ?? 0) > 0 ? "+" : ""}{(mission.routeResult.feasibility.return_margin_km ?? 0).toFixed(1)} km)
                {:else}
                  1-Way Margin: +{mission.routeResult.feasibility.margin_km.toFixed(1)} km
                {/if}
              </div>
            {:else}
              <div
                class="text-sm font-mono font-bold text-ares-red mt-1 flex items-center gap-1"
              >
                <XCircle size={13} /> EXCEEDS RANGE
              </div>
              <div class="text-[10px] font-mono text-ares-red mt-0.5">
                Deficit: {mission.routeResult.feasibility.margin_km.toFixed(1)} km
              </div>
            {/if}
          {:else}
            <div class="text-sm font-mono text-slate-400 mt-1">--</div>
            <div class="text-[10px] font-mono text-slate-500 mt-0.5">
              {selectedVehicle.range} limit
            </div>
          {/if}
        </div>
      </div>

      <!-- Active Plan Details (When Route Result is Available) -->
      {#if mission.routeResult}
        <Card variant="tactical" title="COMPUTED TRAVERSAL ROUTE DETAILS">
          {#snippet headerRight()}
            <div class="flex items-center gap-2">
              <Button size="sm" variant="secondary" onclick={handleViewOnMap}>
                <ExternalLink size={13} class="mr-1" />
                VIEW ON MARS CANVAS
              </Button>
            </div>
          {/snippet}

          <div class="space-y-4">
            <!-- Segments Table -->
            <div class="space-y-2">
              <div class="hud-label text-slate-300">
                ROUTE SEGMENT SEQUENCE ({mission.routeResult.segments.length} LEGS)
              </div>
              <div
                class="overflow-x-auto border border-ares-border rounded-ares"
              >
                <table class="w-full text-left font-mono text-xs">
                  <thead
                    class="bg-ares-deep/90 text-slate-400 uppercase text-[10px] border-b border-ares-border"
                  >
                    <tr>
                      <th class="p-2.5">#</th>
                      <th class="p-2.5">From Waypoint</th>
                      <th class="p-2.5">To Waypoint</th>
                      <th class="p-2.5 text-right">Distance (km)</th>
                      <th class="p-2.5 text-right">Bearing</th>
                      <th class="p-2.5">Terrain Caveat</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-ares-border bg-ares-navy/40">
                    {#each mission.routeResult.segments as seg}
                      <tr class="hover:bg-ares-elevated/50 transition-colors">
                        <td class="p-2.5 text-ares-cyan font-bold"
                          >{seg.index + 1}</td
                        >
                        <td class="p-2.5 text-white">{seg.from_label}</td>
                        <td class="p-2.5 text-white">{seg.to_label}</td>
                        <td class="p-2.5 text-right text-ares-green font-bold">
                          {seg.distance_km.toFixed(2)} km
                        </td>
                        <td class="p-2.5 text-right text-slate-300">
                          {seg.bearing_deg.toFixed(1)}°
                        </td>
                        <td
                          class="p-2.5 text-[10px] text-slate-400 max-w-xs truncate"
                          title={seg.geometry_caveat}
                        >
                          {seg.geometry_caveat}
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            </div>

            <!-- COMPACT MISSION DASHBOARD: TOPOGRAPHY, RISKS, HAZARDS, OBJECTIVES -->
            <div
              class="border border-ares-cyan/30 rounded-ares p-3.5 bg-ares-deep/80 space-y-4"
            >
              <div
                class="flex items-center justify-between pb-2 border-b border-ares-border"
              >
                <div class="flex items-center gap-2">
                  <Gauge size={16} class="text-ares-cyan" />
                  <span
                    class="font-title font-bold text-white text-xs uppercase tracking-wider"
                  >
                    EXPEDITION MISSION DASHBOARD & INTEGRITY SUMMARY
                  </span>
                </div>
                <div class="flex items-center gap-1.5">
                  <Badge provenance="calculated" label="200m USGS DEM" />
                  <Badge provenance="calculated" label="IAU AREOID DATUM" />
                </div>
              </div>

              <!-- 1. Elevation Profile Chart (SVG) -->
              {#if profileSvg}
                <div
                  class="space-y-1.5 bg-ares-navy/60 p-3 rounded-ares border border-ares-border"
                >
                  <div class="flex items-center justify-between text-xs">
                    <span
                      class="hud-label text-slate-300 flex items-center gap-1.5"
                    >
                      <Mountain size={13} class="text-ares-cyan" />
                      TOPOGRAPHIC RELIEF PROFILE (ELEVATION ALONG ROUTE)
                    </span>
                    <span class="text-[10px] text-ares-cyan font-mono">
                      Min: {profileSvg.minE.toFixed(0)}m | Max: {profileSvg.maxE.toFixed(
                        0,
                      )}m | Net: {elevProfile?.elevation_change_m !== undefined
                        ? (elevProfile.elevation_change_m > 0 ? "+" : "") +
                          elevProfile.elevation_change_m.toFixed(0)
                        : "--"}m
                    </span>
                  </div>

                  <div
                    class="w-full overflow-hidden bg-ares-deep/90 rounded border border-ares-border p-2"
                  >
                    <svg
                      viewBox="0 0 {profileSvg.w} {profileSvg.h}"
                      class="w-full h-28 overflow-visible"
                    >
                      <defs>
                        <linearGradient
                          id="elevGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stop-color="#36C5E8"
                            stop-opacity="0.4"
                          />
                          <stop
                            offset="100%"
                            stop-color="#36C5E8"
                            stop-opacity="0.02"
                          />
                        </linearGradient>
                      </defs>
                      <!-- Area fill under line -->
                      <path d={profileSvg.areaD} fill="url(#elevGradient)" />
                      <!-- Profile curve -->
                      <path
                        d={profileSvg.pathD}
                        fill="none"
                        stroke="#36C5E8"
                        stroke-width="2.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <!-- Start and End markers -->
                      <circle
                        cx="35"
                        cy={130 -
                          18 -
                          ((profileSvg.startE - profileSvg.minE) /
                            (profileSvg.maxE - profileSvg.minE || 1)) *
                            94}
                        r="4"
                        fill="#54C99A"
                        stroke="#080D16"
                        stroke-width="1.5"
                      />
                      <circle
                        cx={560 - 35}
                        cy={130 -
                          18 -
                          ((profileSvg.endE - profileSvg.minE) /
                            (profileSvg.maxE - profileSvg.minE || 1)) *
                            94}
                        r="4"
                        fill="#EF5555"
                        stroke="#080D16"
                        stroke-width="1.5"
                      />
                    </svg>
                    <div
                      class="flex justify-between items-center text-[9px] font-mono text-slate-400 mt-1 px-1"
                    >
                      <span class="text-ares-green"
                        >Start ({profileSvg.startE.toFixed(0)} m)</span
                      >
                      <span class="text-slate-500"
                        >Distance: {mission.routeResult.total_distance_km.toFixed(
                          1,
                        )} km</span
                      >
                      <span class="text-ares-red"
                        >Dest ({profileSvg.endE.toFixed(0)} m)</span
                      >
                    </div>
                  </div>
                </div>
              {/if}

              <!-- 2. Dual Column: Terrain Risk & Nearby Hazards -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <!-- Terrain Risk Assessment -->
                <div
                  class="p-3 bg-ares-navy/60 rounded-ares border border-ares-border space-y-2"
                >
                  <div
                    class="hud-label text-slate-300 flex items-center justify-between"
                  >
                    <span class="flex items-center gap-1.5">
                      <Activity size={13} class="text-ares-cyan" />
                      TERRAIN RISK & WHEEL SLIP
                    </span>
                    {#if slopeData}
                      <span
                        class="px-1.5 py-0.2 rounded text-[9px] font-bold {slopeData.steep_slopes_detected
                          ? 'bg-ares-red/30 text-red-300 border border-ares-red/40'
                          : 'bg-ares-green/20 text-green-300 border border-ares-green/30'}"
                      >
                        {slopeData.steep_slopes_detected
                          ? "STEEP INCLINES DETECTED"
                          : "TRAVERSABLE GRADIENTS"}
                      </span>
                    {/if}
                  </div>

                  {#if slopeData}
                    <div
                      class="grid grid-cols-2 gap-2 text-center text-xs font-mono"
                    >
                      <div
                        class="bg-ares-deep/70 p-1.5 rounded border border-ares-border"
                      >
                        <span class="text-[9px] text-slate-400 block"
                          >MEAN SLOPE</span
                        >
                        <strong class="text-ares-cyan text-sm"
                          >{slopeData.mean_slope_deg.toFixed(1)}°</strong
                        >
                      </div>
                      <div
                        class="bg-ares-deep/70 p-1.5 rounded border border-ares-border"
                      >
                        <span class="text-[9px] text-slate-400 block"
                          >MAX SLOPE</span
                        >
                        <strong
                          class="{slopeData.max_slope_deg > 15
                            ? 'text-ares-red'
                            : 'text-ares-green'} text-sm"
                          >{slopeData.max_slope_deg.toFixed(1)}°</strong
                        >
                      </div>
                    </div>
                    <div class="text-[10px] space-y-1 font-mono">
                      <div class="flex justify-between">
                        <span class="text-slate-400">VEHICLE CLIMB LIMIT:</span>
                        <span class="text-white"
                          >{slopeData.max_recommended_slope_deg}° operational
                          max</span
                        >
                      </div>
                      <div class="flex justify-between">
                        <span class="text-slate-400">KINEMATIC SLIP RISK:</span>
                        <span
                          class="font-bold {slopeData.max_slope_deg > 15
                            ? 'text-ares-red'
                            : slopeData.max_slope_deg > 5
                              ? 'text-ares-amber'
                              : 'text-ares-green'}"
                        >
                          {slopeData.max_slope_deg > 15
                            ? "HIGH (SLIP > 40%)"
                            : slopeData.max_slope_deg > 5
                              ? "MODERATE (SLIP 10-25%)"
                              : "NOMINAL (< 5%)"}
                        </span>
                      </div>
                    </div>
                  {:else}
                    <p class="text-[10px] text-slate-400 italic">
                      Numerical slope data unavailable for this route.
                    </p>
                  {/if}
                </div>

                <!-- Nearby Hazards Proximity Screening -->
                <div
                  class="p-3 bg-ares-navy/60 rounded-ares border border-ares-border space-y-2"
                >
                  <div
                    class="hud-label text-slate-300 flex items-center justify-between"
                  >
                    <span class="flex items-center gap-1.5">
                      <AlertTriangle size={13} class="text-ares-amber" />
                      HAZARD PROXIMITY SCREENING
                    </span>
                    <span class="text-[9px] text-slate-400 font-mono"
                      >Regional Registry</span
                    >
                  </div>

                  {#if nearbyHazards.length > 0}
                    <div class="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                      {#each nearbyHazards as hz}
                        <div
                          class="p-1.5 rounded bg-ares-deep/70 border border-ares-border flex items-start justify-between gap-2 text-[10px] font-mono"
                        >
                          <div class="space-y-0.5">
                            <span class="font-bold text-white block"
                              >{hz.name}</span
                            >
                            <span class="text-slate-400 block text-[9px]"
                              >{hz.slopeRisk}</span
                            >
                          </div>
                          <div class="text-right shrink-0">
                            <span
                              class="font-bold px-1.5 py-0.5 rounded text-[9px] {hz.distanceToRouteKm <
                              5
                                ? 'bg-ares-red/30 text-red-300 border border-ares-red/40'
                                : hz.distanceToRouteKm < 15
                                  ? 'bg-ares-amber/30 text-amber-300 border border-ares-amber/40'
                                  : 'bg-slate-800 text-slate-400'}"
                            >
                              ~{hz.distanceToRouteKm} km away
                            </span>
                          </div>
                        </div>
                      {/each}
                    </div>
                  {:else}
                    <p class="text-[10px] text-slate-400 italic">
                      No mapped regional hazards in proximity.
                    </p>
                  {/if}
                </div>
              </div>

              <!-- 3. Scientific Objectives & Field Investigation at Stops -->
              <div
                class="p-3 bg-ares-navy/60 rounded-ares border border-ares-border space-y-2"
              >
                <div class="hud-label text-slate-300 flex items-center gap-1.5">
                  <Sparkles size={13} class="text-ares-cyan" />
                  SCIENTIFIC OBJECTIVES AT WAYPOINTS
                </div>

                <div
                  class="grid grid-cols-1 md:grid-cols-2 gap-3 text-[11px] font-mono"
                >
                  {#if startPoi}
                    <div
                      class="bg-ares-deep/80 p-2.5 rounded border border-ares-border space-y-1"
                    >
                      <div
                        class="flex items-center justify-between border-b border-ares-border pb-1"
                      >
                        <strong class="text-ares-green"
                          >START: {startPoi.name}</strong
                        >
                        <span
                          class="text-[9px] px-1 rounded bg-ares-green/20 text-green-300"
                        >
                          {startPoi.data_provenance_type ||
                            "VERIFIED GROUND TRUTH"}
                        </span>
                      </div>
                      <p
                        class="text-[10px] font-sans text-slate-300 leading-snug"
                      >
                        {startPoi.description}
                      </p>
                      {#if startPoi.investigation_focus}
                        <div class="text-[9px] text-ares-cyan pt-0.5">
                          <strong class="text-slate-400">FIELD TASK:</strong>
                          {startPoi.investigation_focus}
                        </div>
                      {/if}
                      <div class="text-[9px] text-slate-500 italic">
                        Mission: {startPoi.nasa_mission ||
                          startPoi.source_reference ||
                          "NASA PDS"}
                      </div>
                    </div>
                  {/if}

                  {#if destPoi}
                    <div
                      class="bg-ares-deep/80 p-2.5 rounded border border-ares-border space-y-1"
                    >
                      <div
                        class="flex items-center justify-between border-b border-ares-border pb-1"
                      >
                        <strong class="text-ares-red"
                          >DEST: {destPoi.name}</strong
                        >
                        <span
                          class="text-[9px] px-1 rounded bg-ares-cyan/20 text-cyan-300"
                        >
                          {destPoi.data_provenance_type || "EXPLORATION TARGET"}
                        </span>
                      </div>
                      <p
                        class="text-[10px] font-sans text-slate-300 leading-snug"
                      >
                        {destPoi.description}
                      </p>
                      {#if destPoi.investigation_focus}
                        <div class="text-[9px] text-ares-cyan pt-0.5">
                          <strong class="text-slate-400">FIELD TASK:</strong>
                          {destPoi.investigation_focus}
                        </div>
                      {/if}
                      <div class="text-[9px] text-slate-500 italic">
                        Mission: {destPoi.nasa_mission ||
                          destPoi.source_reference ||
                          "NASA PDS"}
                      </div>
                    </div>
                  {/if}
                </div>
              </div>
            </div>

            <!-- Operational Warnings & Limitations -->
            {#if mission.routeResult.warnings.length > 0}
              <div
                class="p-3 bg-ares-amber/10 border border-ares-amber/30 rounded-ares space-y-1.5"
              >
                <div
                  class="hud-label text-ares-amber flex items-center gap-1.5"
                >
                  <AlertTriangle size={13} />
                  <span
                    >OPERATIONAL ADVISORIES ({mission.routeResult.warnings
                      .length})</span
                  >
                </div>
                <ul
                  class="text-[11px] font-sans text-amber-200/90 list-disc list-inside space-y-1"
                >
                  {#each mission.routeResult.warnings as warn}
                    <li>{warn}</li>
                  {/each}
                </ul>
              </div>
            {/if}

            <!-- Rover Range Caveat -->
            <div
              class="p-3 bg-ares-deep/60 border border-ares-border rounded-ares space-y-1 text-xs font-mono"
            >
              <span class="hud-label text-slate-400"
                >VEHICLE OPERATIONAL ASSUMPTION:</span
              >
              <p class="text-[11px] font-sans text-slate-300 leading-relaxed">
                {mission.routeResult.feasibility.range_caveat}
              </p>
            </div>

            <!-- Scientific Transparency Disclaimer -->
            <div
              class="p-3 bg-ares-deep/90 border border-ares-cyan/30 rounded-ares space-y-1 text-xs"
            >
              <div class="hud-label text-ares-cyan flex items-center gap-1.5">
                <ShieldAlert size={13} />
                <span>SCIENTIFIC INTEGRITY CONTRACT</span>
              </div>
              <p class="text-[11px] font-sans text-slate-300 leading-relaxed">
                {mission.routeResult.scientific_disclaimer}
              </p>
            </div>
          </div>
        </Card>
      {/if}

      <!-- Vehicle Specifications -->
      <Card
        variant="panel"
        title="ACTIVE ROVER SPECIFICATIONS"
        subtitle={selectedVehicle.name}
      >
        <div class="grid grid-cols-3 gap-3 font-mono text-xs">
          <div
            class="bg-ares-deep/60 p-2.5 rounded-ares border border-ares-border"
          >
            <span class="text-slate-400 text-[10px] block">NOMINAL SPEED</span>
            <strong class="text-ares-cyan text-sm"
              >{selectedVehicle.speed}</strong
            >
            <span class="text-slate-500 text-[9px] block">flat ground</span>
          </div>
          <div
            class="bg-ares-deep/60 p-2.5 rounded-ares border border-ares-border"
          >
            <span class="text-slate-400 text-[10px] block">MAX RANGE</span>
            <strong class="text-ares-green text-sm"
              >{selectedVehicle.range}</strong
            >
            <span class="text-slate-500 text-[9px] block">planning limit</span>
          </div>
          <div
            class="bg-ares-deep/60 p-2.5 rounded-ares border border-ares-border"
          >
            <span class="text-slate-400 text-[10px] block">PAYLOAD / CREW</span>
            <strong class="text-ares-amber text-sm"
              >{selectedVehicle.crew}</strong
            >
            <span class="text-slate-500 text-[9px] block"
              >operational capacity</span
            >
          </div>
        </div>
      </Card>

      <!-- Honest Data Transparency Panel (Terrain & Sensor Layers) -->
      <Card variant="panel" title="TERRAIN & SENSOR LAYER STATUS">
        {#snippet headerRight()}
          {#if mission.routeResult?.data_source.dem_available}
            <Badge provenance="calculated" label="200m DEM ACTIVE" />
          {:else}
            <Badge provenance="unavailable" label="DEM ABSENT" />
          {/if}
        {/snippet}

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
          <div
            class="p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border space-y-1"
          >
            <div class="flex items-center justify-between">
              <span class="hud-label text-slate-300">SLOPE ANALYSIS</span>
              {#if slopeData}
                <Badge provenance="calculated" label="CALCULATED" />
              {:else}
                <Badge provenance="unavailable" label="UNAVAILABLE" />
              {/if}
            </div>
            {#if slopeData}
              <div class="text-[11px] text-ares-cyan font-bold">
                Mean: {slopeData.mean_slope_deg.toFixed(1)}° | Max: {slopeData.max_slope_deg.toFixed(
                  1,
                )}°
              </div>
              <p class="text-[10px] font-sans text-slate-400 leading-relaxed">
                Physical surface gradient evaluated from USGS HRSC/MOLA 200m
                blended numerical DEM.
              </p>
            {:else}
              <p class="text-[10px] font-sans text-slate-400 leading-relaxed">
                MOLA colourised PNG tiles are visual products only; RGB values
                do not encode numerical elevation.
              </p>
            {/if}
          </div>

          <div
            class="p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border space-y-1"
          >
            <div class="flex items-center justify-between">
              <span class="hud-label text-slate-300">HAZARD EXPOSURE</span>
              <Badge provenance="unavailable" label="UNAVAILABLE" />
            </div>
            <p class="text-[10px] font-sans text-slate-400 leading-relaxed">
              Hazard classification raster is not currently loaded; no synthetic
              safety scores are invented.
            </p>
          </div>

          <div
            class="p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border space-y-1"
          >
            <div class="flex items-center justify-between">
              <span class="hud-label text-slate-300">ELEVATION PROFILE</span>
              {#if elevProfile}
                <Badge provenance="calculated" label="CALCULATED" />
              {:else}
                <Badge provenance="unavailable" label="UNAVAILABLE" />
              {/if}
            </div>
            {#if elevProfile}
              <div class="text-[11px] text-ares-cyan font-bold">
                Min: {elevProfile.min_elevation_m.toFixed(0)} m | Max: {elevProfile.max_elevation_m.toFixed(
                  0,
                )} m
              </div>
              <p class="text-[10px] font-sans text-slate-400 leading-relaxed">
                Topographic relief profile sampled along route relative to IAU
                MOLA Areoid datum.
              </p>
            {:else}
              <p class="text-[10px] font-sans text-slate-400 leading-relaxed">
                Numerical DEM data required for 3D topological profiles is
                deferred to subsequent milestones.
              </p>
            {/if}
          </div>

          <div
            class="p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border space-y-1"
          >
            <div class="flex items-center justify-between">
              <span class="hud-label text-slate-300">POI SNAP THRESHOLD</span>
              <Badge provenance="calculated" label="0.05° (~3 km)" />
            </div>
            <p class="text-[10px] font-sans text-slate-400 leading-relaxed">
              Coordinates within 0.05° are snapped to nearest verified NASA
              landing or science site.
            </p>
          </div>
        </div>
      </Card>
    </div>
  </div>
</div>
