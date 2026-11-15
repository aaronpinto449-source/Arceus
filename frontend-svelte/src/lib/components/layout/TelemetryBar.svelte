<script lang="ts">
  import { mission } from "../../stores/mission.svelte";
  import {
    MapPin,
    Gauge,
    Mountain,
    Thermometer,
    ShieldCheck,
  } from "@lucide/svelte";
  import Badge from "../ui/Badge.svelte";

  const lat = $derived(mission.currentRegion.lat);
  const cosLat = $derived(Math.cos((lat * Math.PI) / 180.0));
  const mLat = $derived((2 * Math.PI * 3389500) / (360 * 256));
  const mLon = $derived(Math.round(mLat * Math.abs(cosLat) * 10) / 10);
</script>

<div
  class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 p-2.5 bg-ares-deep border-b border-ares-border text-xs font-mono select-none"
>
  <!-- Card 1: Regional Center -->
  <div
    class="ares-panel p-2.5 flex items-center justify-between border-l-2 border-l-ares-cyan"
  >
    <div class="flex flex-col gap-0.5 overflow-hidden">
      <div class="flex items-center gap-1.5">
        <span class="hud-label flex items-center gap-1 text-ares-ice">
          <MapPin size={11} class="text-ares-cyan" />
          TARGET ZONE
        </span>
        <Badge provenance="measured" />
      </div>
      <span class="text-white font-bold tracking-tight text-sm truncate">
        {mission.currentRegion.name}
      </span>
      <span class="text-[10px] text-slate-400">
        {mission.currentRegion.lat.toFixed(2)}°N, {mission.currentRegion.lon.toFixed(
          2,
        )}°E
      </span>
    </div>
    <div
      class="w-7 h-7 rounded-ares bg-ares-deep border border-ares-border flex items-center justify-center text-ares-cyan font-bold text-[10px] shrink-0"
    >
      MOLA
    </div>
  </div>

  <!-- Card 2: Ground Resolution & Longitude Compression -->
  <div
    class="ares-panel p-2.5 flex items-center justify-between border-l-2 border-l-ares-green"
  >
    <div class="flex flex-col gap-0.5 overflow-hidden">
      <div class="flex items-center gap-1.5">
        <span class="hud-label flex items-center gap-1 text-slate-400">
          <Gauge size={11} class="text-ares-green" />
          GROUND RESOLUTION
        </span>
        <Badge provenance="calculated" />
      </div>
      <span class="text-white font-bold tracking-tight text-sm">
        {mLon} m/px
        <span class="text-[10px] font-normal text-slate-400">LON</span>
      </span>
      <span class="text-[10px] text-slate-400">
        LAT: {mLat} m/px | cos(φ): {cosLat.toFixed(3)}
      </span>
    </div>
    <div
      class="w-7 h-7 rounded-ares bg-ares-deep border border-ares-border flex items-center justify-center text-ares-green font-bold text-[10px] shrink-0"
    >
      256
    </div>
  </div>

  <!-- Card 3: Elevation & Areoid Reference -->
  <div
    class="ares-panel p-2.5 flex items-center justify-between border-l-2 border-l-ares-amber"
  >
    <div class="flex flex-col gap-0.5 overflow-hidden">
      <div class="flex items-center gap-1.5">
        <span class="hud-label flex items-center gap-1 text-slate-400">
          <Mountain size={11} class="text-ares-amber" />
          AREOID DATUM
        </span>
        <Badge provenance="measured" />
      </div>
      <span
        class="text-white font-bold tracking-tight text-xs truncate max-w-[170px]"
        title={mission.currentRegion.elevation_approx}
      >
        {mission.currentRegion.elevation_approx}
      </span>
      <span class="text-[10px] text-slate-400"> IAU 0-km reference geoid </span>
    </div>
    <div
      class="w-7 h-7 rounded-ares bg-ares-deep border border-ares-border flex items-center justify-center text-ares-amber font-bold text-[10px] shrink-0"
    >
      DATUM
    </div>
  </div>

  <!-- Card 4: Environmental & EVA Safety Model -->
  <div
    class="ares-panel p-2.5 flex items-center justify-between border-l-2 border-l-ares-red"
  >
    <div class="flex flex-col gap-0.5 overflow-hidden">
      <div class="flex items-center gap-1.5">
        <span class="hud-label flex items-center gap-1 text-slate-400">
          <Thermometer size={11} class="text-ares-red" />
          SURFACE AMBIENT
        </span>
        <Badge provenance="simulated" />
      </div>
      <div class="flex items-center gap-2">
        <span class="text-white font-bold tracking-tight text-sm">
          {mission.telemetry.surfaceTemp}
        </span>
        <span
          class="text-[10px] px-1.5 py-0.2 rounded-ares bg-ares-deep text-slate-300 border border-ares-border"
        >
          {mission.telemetry.atmosphericPressure}
        </span>
      </div>
      <span
        class="text-[10px] text-ares-green flex items-center gap-1 truncate"
      >
        <ShieldCheck size={10} /> HAB &amp; SUIT NOMINAL
      </span>
    </div>
    <div
      class="w-7 h-7 rounded-ares bg-ares-deep border border-ares-border flex items-center justify-center text-ares-red font-bold text-[10px] shrink-0"
    >
      EVA
    </div>
  </div>
</div>
