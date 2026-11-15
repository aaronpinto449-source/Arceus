<script lang="ts">
  import { mission } from '../../stores/mission.svelte';
  import { api } from '../../services/api';
  import { 
    Crosshair, 
    MapPin, 
    ShieldCheck, 
    AlertTriangle, 
    ExternalLink, 
    Compass, 
    Layers, 
    Route, 
    X,
    Maximize2
  } from '@lucide/svelte';
  import Badge from '../ui/Badge.svelte';
  import Button from '../ui/Button.svelte';

  let resolution = $state<{ meters_per_pixel_lat: number; meters_per_pixel_lon: number } | null>(null);

  $effect(() => {
    const lat = mission.selectedTarget ? mission.selectedTarget.lat : mission.currentRegion.lat;
    api.getSpatialResolution(lat).then(res => {
      resolution = res;
    });
  });
</script>

<aside 
  class={`bg-ares-navy border-l border-ares-border flex flex-col justify-between transition-all duration-200 z-30 select-none
    ${mission.rightDrawerOpen ? 'w-80 md:w-96 min-w-[20rem]' : 'w-0 hidden'}
  `}
>
  <!-- Header -->
  <div class="px-4 py-3 border-b border-ares-border flex items-center justify-between bg-ares-deep/40">
    <div class="flex items-center gap-2">
      <Crosshair size={15} class="text-ares-cyan" />
      <h3 class="font-title text-xs font-bold text-white uppercase tracking-wider">
        TARGET &amp; REGION INTELLIGENCE
      </h3>
    </div>
    <button
      onclick={() => mission.setRightDrawer(false)}
      class="p-1 rounded text-slate-400 hover:text-white hover:bg-ares-elevated border border-transparent hover:border-ares-border transition-colors"
      title="Close Panel"
    >
      <X size={16} />
    </button>
  </div>

  <!-- Content -->
  <div class="p-4 flex-1 overflow-y-auto space-y-4 font-mono text-xs">
    <!-- Active Locked Target Card -->
    <div class="p-3.5 rounded-ares-md bg-ares-elevated border border-ares-border space-y-2.5">
      <div class="flex items-center justify-between">
        <span class="hud-label text-ares-ice flex items-center gap-1">
          <MapPin size={11} class="text-ares-cyan" />
          ACTIVE TARGET LOCK
        </span>
        {#if mission.selectedPoi}
          <Badge provenance="measured" label="NASA PDS" />
        {:else if mission.selectedTarget}
          <Badge provenance="calculated" label="COORDINATE" />
        {:else}
          <Badge variant="neutral" label="STANDBY" />
        {/if}
      </div>

      {#if mission.selectedTarget}
        <div class="text-sm font-bold text-white leading-tight">
          {mission.selectedTarget.name}
        </div>

        <div class="p-2.5 rounded-ares bg-ares-deep border border-ares-border text-[11px] space-y-1">
          <div class="flex justify-between">
            <span class="text-slate-400">LATITUDE:</span>
            <span class="text-ares-cyan font-bold">{mission.selectedTarget.lat.toFixed(4)}° N</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">LONGITUDE:</span>
            <span class="text-ares-cyan font-bold">{mission.selectedTarget.lon.toFixed(4)}° E</span>
          </div>
          {#if mission.selectedTarget.type}
            <div class="flex justify-between pt-1 border-t border-ares-border/60">
              <span class="text-slate-400">TYPE:</span>
              <span class="text-ares-green font-semibold">{mission.selectedTarget.type}</span>
            </div>
          {/if}
        </div>

        {#if mission.selectedPoi}
          <p class="text-xs text-slate-300 font-sans leading-relaxed pt-1">
            {mission.selectedPoi.description}
          </p>
          <div class="text-[10px] text-ares-amber">
            <strong>SIGNIFICANCE:</strong> {mission.selectedPoi.significance}
          </div>
        {/if}
      {:else}
        <p class="text-slate-400 text-xs italic py-2">
          Click any feature on the central MOLA canvas or select a scientific POI to view telemetry and terrain metrics.
        </p>
      {/if}
    </div>

    <!-- Spatial Scale Resolution -->
    {#if resolution}
      <div class="p-3.5 rounded-ares-md bg-ares-navy border border-ares-border space-y-2">
        <div class="flex items-center justify-between">
          <span class="hud-label text-slate-400">SPATIAL RESOLUTION</span>
          <Badge provenance="calculated" />
        </div>
        <div class="space-y-1 text-[11px]">
          <div class="flex justify-between text-slate-300">
            <span>Latitudinal Scale:</span>
            <strong class="text-white">{resolution.meters_per_pixel_lat} m/px</strong>
          </div>
          <div class="flex justify-between text-slate-300">
            <span>Cosine Longitude Scale:</span>
            <strong class="text-ares-cyan">{resolution.meters_per_pixel_lon} m/px</strong>
          </div>
        </div>
      </div>
    {/if}

    <!-- Regional Geodetic Frame -->
    <div class="p-3.5 rounded-ares-md bg-ares-navy border border-ares-border space-y-2">
      <div class="flex items-center justify-between">
        <span class="hud-label text-slate-400">GEODETIC FRAME</span>
        <Badge provenance="measured" label="IAU 2000" />
      </div>
      <div class="space-y-1 text-[10px] text-slate-300">
        <div class="flex justify-between">
          <span class="text-slate-400">PROJECTION:</span>
          <span class="text-white">{mission.currentRegion.bounds.projection}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">PRIME MERIDIAN:</span>
          <span class="text-white">{mission.currentRegion.bounds.reference_meridian}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">BOUNDS (LAT):</span>
          <span class="text-white">{mission.currentRegion.bounds.lat_min}°N to {mission.currentRegion.bounds.lat_max}°N</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">BOUNDS (LON):</span>
          <span class="text-white">{mission.currentRegion.bounds.lon_min}°E to {mission.currentRegion.bounds.lon_max}°E</span>
        </div>
      </div>
    </div>

    <!-- Rover Operating Thresholds & Hazard Safety -->
    <div class="p-3.5 rounded-ares-md bg-ares-navy border border-ares-border space-y-2">
      <div class="flex items-center justify-between">
        <span class="hud-label text-ares-amber">TERRAIN SAFETY PROTOCOL</span>
        <Badge hazardLevel="elevated" label="SLOPE &gt; 15°" />
      </div>
      <div class="space-y-1.5 text-[11px] text-slate-300">
        <div class="flex justify-between">
          <span class="text-slate-400">Auto-Drive Cap:</span>
          <strong class="text-ares-amber">15.0° Incline</strong>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">Static Stability:</span>
          <strong class="text-ares-green">&gt; 40.0° on Rock</strong>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">Wheel Slip Limit:</span>
          <strong class="text-ares-red">80% Slip on Regolith</strong>
        </div>
      </div>
    </div>
  </div>

  <!-- Footer Actions -->
  <div class="p-3 border-t border-ares-border bg-ares-deep/60 flex flex-col gap-2">
    <Button
      variant="tactical"
      size="sm"
      fullWidth
      onclick={() => mission.setActivePage('Route Planner')}
    >
      <Route size={13} /> STAGE EXPEDITION TRAVERSE
    </Button>
  </div>
</aside>

