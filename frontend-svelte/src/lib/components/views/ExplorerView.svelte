<script lang="ts">
  import { mission } from "../../stores/mission.svelte";
  import { api } from "../../services/api";
  import MarsCanvas from "../explorer/MarsCanvas.svelte";
  import type { SelectedTarget, GroundResolution } from "../../types";
  import {
    Crosshair,
    Info,
    ShieldCheck,
    MapPin,
    ArrowRight,
    PanelRight,
    Layers,
  } from "@lucide/svelte";
  import Badge from "../ui/Badge.svelte";
  import Button from "../ui/Button.svelte";

  let manualLat = $state(
    mission.selectedTarget?.lat ?? mission.currentRegion.lat,
  );
  let manualLon = $state(
    mission.selectedTarget?.lon ?? mission.currentRegion.lon,
  );
  let resolution = $state<GroundResolution | null>(null);

  $effect(() => {
    if (mission.selectedTarget) {
      manualLat = mission.selectedTarget.lat;
      manualLon = mission.selectedTarget.lon;
    } else {
      manualLat = mission.currentRegion.lat;
      manualLon = mission.currentRegion.lon;
    }

    api.getSpatialResolution(manualLat).then((res) => {
      resolution = res;
    });
  });

  function handleManualPin(e: Event) {
    e.preventDefault();
    mission.selectTarget({
      lat: Number(manualLat.toFixed(4)),
      lon: Number(manualLon.toFixed(4)),
      name: `Waypoint (${manualLat.toFixed(2)}°N, ${manualLon.toFixed(2)}°E)`,
    });
  }

  const mapUrl = $derived(api.getRegionMapUrl(mission.currentRegion.id));
</script>

<div class="h-full flex flex-col gap-3 p-3 md:p-4 overflow-y-auto">
  <!-- Top Tactical Sub-header -->
  <div class="flex flex-wrap items-center justify-between gap-2 px-1">
    <div class="flex items-center gap-2.5">
      <h2
        class="font-title text-base md:text-lg font-bold text-white uppercase tracking-wider flex items-center gap-2"
      >
        <Crosshair size={18} class="text-ares-cyan" />
        SURFACE CARTOGRAPHY — {mission.currentRegion.name}
      </h2>
      <Badge provenance="measured" label="MOLA MEG256" />
    </div>

    <!-- Right Controls -->
    <div class="flex items-center gap-2 text-xs font-mono">
      <span class="text-slate-400 hidden lg:inline">
        FRAME: {mission.currentRegion.bounds.lat_convention} / {mission
          .currentRegion.bounds.lon_convention}
      </span>
      <Button
        variant="tactical"
        size="sm"
        onclick={() => mission.toggleRightDrawer()}
      >
        <PanelRight size={13} />
        <span
          >{mission.rightDrawerOpen ? "COLLAPSE INTEL" : "EXPAND INTEL"}</span
        >
      </Button>
    </div>
  </div>

  <!-- Primary Map Workspace (DOMINATES WORKSPACE) -->
  <div class="flex-1 w-full relative min-h-[460px] md:min-h-[580px]">
    <MarsCanvas
      region={mission.currentRegion}
      imageUrl={mapUrl}
      pois={mission.currentPois}
      selectedTarget={mission.selectedTarget}
      onSelectTarget={(target) => mission.selectTarget(target)}
    />
  </div>

  <!-- Bottom Workspace Strip: Coordinate Input Bar & Provenance Disclaimer -->
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 items-stretch">
    <!-- Manual Precision Input (4 Cols) -->
    <form
      onsubmit={handleManualPin}
      class="lg:col-span-5 ares-panel p-3 flex items-center gap-3"
    >
      <div class="hud-label text-ares-cyan shrink-0 flex items-center gap-1">
        <MapPin size={12} />
        <span>LOCK COORD</span>
      </div>

      <div class="flex-1 grid grid-cols-2 gap-2">
        <input
          type="number"
          step="0.01"
          placeholder="Lat °N"
          min={mission.currentRegion.bounds.lat_min}
          max={mission.currentRegion.bounds.lat_max}
          bind:value={manualLat}
          class="w-full bg-ares-deep border border-ares-border rounded-ares px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-ares-cyan"
          title={`Latitude between ${mission.currentRegion.bounds.lat_min}° and ${mission.currentRegion.bounds.lat_max}°`}
        />
        <input
          type="number"
          step="0.01"
          placeholder="Lon °E"
          min={mission.currentRegion.bounds.lon_min}
          max={mission.currentRegion.bounds.lon_max}
          bind:value={manualLon}
          class="w-full bg-ares-deep border border-ares-border rounded-ares px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-ares-cyan"
          title={`Longitude between ${mission.currentRegion.bounds.lon_min}° and ${mission.currentRegion.bounds.lon_max}°`}
        />
      </div>

      <Button type="submit" variant="tactical" size="sm" class="shrink-0">
        LOCK <ArrowRight size={12} />
      </Button>
    </form>

    <!-- Scientific Cartography Notice (7 Cols) -->
    <div
      class="lg:col-span-7 ares-panel p-3 flex items-center gap-2.5 text-[11px] leading-relaxed text-slate-300 font-mono"
    >
      <Info size={16} class="text-ares-amber shrink-0" />
      <div class="truncate">
        <strong class="text-white">NASA MGS MOLA MEG256:</strong>
        Equatorial scale is ~231 m/px. Longitude compresses toward poles as cosine
        of latitude. Traversal impedance is calculated algorithmically.
      </div>
    </div>
  </div>
</div>
