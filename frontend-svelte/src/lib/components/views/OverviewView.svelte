<script lang="ts">
  import { mission } from '../../stores/mission.svelte';
  import { 
    Compass, 
    Route, 
    Layers, 
    Rocket, 
    Crosshair,
    ShieldCheck,
    Bookmark
  } from '@lucide/svelte';
  import Card from '../ui/Card.svelte';
  import Button from '../ui/Button.svelte';
  import Badge from '../ui/Badge.svelte';
</script>

<div class="p-4 md:p-6 flex flex-col gap-5 max-w-7xl mx-auto">
  <!-- Top Banner / Region Header Card -->
  <div class="ares-panel p-5 border-l-4 border-l-ares-cyan flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
    <div class="flex flex-col gap-1.5">
      <div class="flex items-center gap-2">
        <span class="hud-label text-ares-ice">EXPLORATION REGION</span>
        <Badge provenance="measured" label={mission.currentRegion.bounds.projection} />
      </div>
      <h1 class="text-2xl md:text-3xl font-title font-bold tracking-tight text-white flex items-center gap-3">
        {mission.currentRegion.name}
      </h1>
      <p class="text-slate-300 text-sm max-w-3xl font-sans leading-relaxed">
        {mission.currentRegion.description}
      </p>
    </div>

    <!-- Quick Navigation Action Buttons -->
    <div class="flex flex-wrap md:flex-col gap-2 shrink-0 w-full md:w-auto">
      <Button
        variant="primary"
        size="md"
        onclick={() => mission.setActivePage('Mars Explorer')}
      >
        <Compass size={15} /> OPEN MOLA CARTOGRAPHY
      </Button>
      <Button
        variant="secondary"
        size="md"
        onclick={() => mission.setActivePage('Route Planner')}
      >
        <Route size={15} /> PLAN SURFACE TRAVERSE
      </Button>
    </div>
  </div>

  <!-- 3-Column Tactical Details Grid -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <!-- Col 1: Geological Context -->
    <Card variant="panel" title="GEOLOGICAL CONTEXT">
      {#snippet headerRight()}
        <Badge provenance="measured" />
      {/snippet}

      <div class="flex flex-col gap-3 font-mono text-xs">
        <p class="text-slate-300 font-sans leading-relaxed text-xs">
          {mission.currentRegion.geology}
        </p>

        <div class="bg-ares-deep/60 p-2.5 rounded-ares border border-ares-border flex flex-col gap-1.5">
          <div class="flex justify-between text-slate-400">
            <span>FEATURE DIAMETER:</span>
            <strong class="text-white">{mission.currentRegion.diameter}</strong>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>ELEVATION SPAN:</span>
            <strong class="text-white truncate max-w-[150px]">{mission.currentRegion.elevation_approx}</strong>
          </div>
        </div>
      </div>
    </Card>

    <!-- Col 2: Mission Science Objective -->
    <Card variant="panel" title="PRIMARY OBJECTIVE">
      {#snippet headerRight()}
        <Rocket size={14} class="text-ares-green" />
      {/snippet}

      <div class="flex flex-col gap-3 font-mono text-xs">
        <p class="text-slate-300 font-sans leading-relaxed text-xs">
          {mission.currentRegion.objective}
        </p>

        <div class="bg-ares-deep/60 p-2.5 rounded-ares border border-ares-border flex flex-col gap-1">
          <span class="text-slate-400 text-[10px]">HISTORICAL PRECEDENT:</span>
          <span class="text-ares-green font-semibold leading-tight">
            {mission.currentRegion.mission_context}
          </span>
        </div>
      </div>
    </Card>

    <!-- Col 3: Geodetic Framing & Bounds -->
    <Card variant="panel" title="GEODETIC BOUNDS (30°×30°)">
      {#snippet headerRight()}
        <Crosshair size={14} class="text-ares-amber" />
      {/snippet}

      <div class="flex flex-col gap-3 font-mono text-xs">
        <div class="flex flex-col gap-1.5 text-slate-300">
          <div class="flex justify-between">
            <span class="text-slate-400">LAT SPAN:</span>
            <span>{mission.currentRegion.bounds.lat_min}°N to {mission.currentRegion.bounds.lat_max}°N</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">LON SPAN:</span>
            <span>{mission.currentRegion.bounds.lon_min}°E to {mission.currentRegion.bounds.lon_max}°E</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">GRID SIZE:</span>
            <span>{mission.currentRegion.bounds.pixel_width} × {mission.currentRegion.bounds.pixel_height} px</span>
          </div>
        </div>

        <div class="bg-ares-deep/60 p-2.5 rounded-ares border border-ares-border text-[10px] text-slate-400 flex flex-col gap-0.5">
          <span>MERIDIAN: {mission.currentRegion.bounds.reference_meridian}</span>
          <span>CONVENTION: {mission.currentRegion.bounds.lat_convention}</span>
        </div>
      </div>
    </Card>
  </div>

  <!-- Sourced NASA Points of Interest -->
  <Card variant="tactical" title="VERIFIED NASA SCIENCE TARGETS" subtitle={`${mission.currentPois.length} Ground Features Catalogued`}>
    {#snippet headerRight()}
      <Badge provenance="measured" label="NASA PDS ARCHIVE" />
    {/snippet}

    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      {#each mission.currentPois as poi}
        {@const isSelected = mission.selectedPoi?.id === poi.id}
        <button
          onclick={() => mission.selectPoi(poi)}
          class={`text-left rounded-ares p-3.5 transition-all duration-150 flex flex-col justify-between gap-2.5 border 
            ${isSelected 
              ? 'bg-ares-cyan/15 border-ares-cyan text-white shadow-ares-glow-cyan/20' 
              : 'bg-ares-deep/60 hover:bg-ares-elevated border-ares-border hover:border-ares-border-bright text-slate-300'
            }
          `}
        >
          <div class="flex flex-col gap-1">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-mono px-1.5 py-0.5 rounded-ares bg-ares-deep border border-ares-border text-ares-cyan font-bold">
                {poi.id}
              </span>
              <span class="text-[10px] font-mono text-slate-400">
                {poi.lat.toFixed(2)}°N, {poi.lon.toFixed(2)}°E
              </span>
            </div>
            <h4 class="font-title font-bold text-sm text-white mt-0.5">{poi.name}</h4>
            <p class="text-xs text-slate-300 font-sans line-clamp-2 leading-relaxed">{poi.description}</p>
          </div>

          <div class="pt-2 border-t border-ares-border text-[10px] font-mono text-slate-400 flex flex-col gap-0.5">
            <span class="text-ares-green font-semibold truncate">{poi.significance}</span>
            {#if poi.source_reference}
              <span class="text-slate-500 truncate" title={poi.source_reference}>Source: {poi.source_reference}</span>
            {/if}
          </div>
        </button>
      {/each}
    </div>
  </Card>
</div>
