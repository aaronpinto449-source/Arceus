<script lang="ts">
  import { mission } from '../../stores/mission.svelte';
  import { api } from '../../services/api';
  import MarsCanvas from '../explorer/MarsCanvas.svelte';
  import Button from '../ui/Button.svelte';
  import Badge from '../ui/Badge.svelte';
  import Card from '../ui/Card.svelte';
  import { 
    Tablet, 
    Monitor, 
    Compass, 
    AlertTriangle, 
    Route, 
    Atom, 
    Wifi, 
    WifiOff, 
    Crosshair, 
    ShieldCheck, 
    Mountain, 
    Activity,
    Thermometer,
    Gauge
  } from '@lucide/svelte';

  type FieldTab = 'map' | 'hazards' | 'route' | 'science';
  let activeTab = $state<FieldTab>('map');

  const mapUrl = $derived(api.getRegionMapUrl(mission.currentRegion.id));
</script>

<div class="min-h-screen bg-ares-deep text-white flex flex-col font-sans select-none border-4 border-ares-amber/40">
  <!-- Top EVA Status Strip (Large Touch Targets & Field-Readable Font) -->
  <header class="bg-ares-navy border-b-2 border-ares-border px-4 py-3 flex items-center justify-between gap-3">
    <!-- Left: Sol, Region & EVA Mode -->
    <div class="flex items-center gap-3">
      <div class="w-3.5 h-3.5 rounded-full bg-ares-amber shadow-ares-glow-amber animate-pulse"></div>
      <div>
        <div class="flex items-center gap-2">
          <span class="font-title text-base md:text-lg font-bold text-white tracking-wide">
            EVA FIELD HUD | {mission.currentRegion.name.toUpperCase()}
          </span>
          <Badge variant="amber" label="FIELD PROTOCOL" />
        </div>
        <div class="text-xs font-mono text-slate-300">
          SOL {mission.telemetry.sol} &bull; MTC COORD &bull; {mission.currentRegion.lat.toFixed(2)}°N, {mission.currentRegion.lon.toFixed(2)}°E
        </div>
      </div>
    </div>

    <!-- Right: Persistent Offline Status & Exit to Desktop -->
    <div class="flex items-center gap-3">
      <!-- Persistent Offline / Standalone Indicator -->
      <div class={`px-3 py-1.5 rounded-ares border flex items-center gap-2 font-mono text-xs ${
        mission.backendConnected 
          ? 'bg-ares-green/20 text-ares-green border-ares-green/50' 
          : 'bg-ares-amber/20 text-ares-amber border-ares-amber/50 font-bold'
      }`}>
        {#if mission.backendConnected}
          <Wifi size={14} class="animate-pulse" />
          <span>LINK OK</span>
        {:else}
          <WifiOff size={14} />
          <span>FIELD CACHE (AUTONOMOUS)</span>
        {/if}
      </div>

      <!-- Switch to Desktop Mode (Minimum 48px touch target) -->
      <button
        onclick={() => mission.setInterfaceMode('desktop')}
        class="min-h-[48px] px-3.5 py-2 bg-ares-elevated hover:bg-space-700 border border-ares-border-bright rounded-ares font-mono text-xs text-slate-200 flex items-center gap-2"
        title="Switch to Desktop Mission Control"
      >
        <Monitor size={16} />
        <span class="hidden sm:inline">DESKTOP</span>
      </button>
    </div>
  </header>

  <!-- Prominent Hazard & Route Warning Banner -->
  <section class="bg-ares-elevated border-b-2 border-ares-border px-4 py-2.5 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
    <div class="flex items-center gap-2">
      <Badge hazardLevel="critical" label="INCLINE THRESHOLD 15°–20°" />
      <span class="text-slate-300 hidden md:inline">
        Loose regolith reduces wheel traction by &gt;80%. Maintain autonomous drive limit.
      </span>
    </div>

    <div class="flex items-center gap-4 text-slate-300">
      <div class="flex items-center gap-1.5">
        <Thermometer size={13} class="text-ares-red" />
        <span>AMBIENT: <strong class="text-white">{mission.telemetry.surfaceTemp}</strong></span>
      </div>
      <div class="flex items-center gap-1.5">
        <Gauge size={13} class="text-ares-cyan" />
        <span>PRESS: <strong class="text-white">{mission.telemetry.atmosphericPressure}</strong></span>
      </div>
    </div>
  </section>

  <!-- Main Field Touch Workspace -->
  <main class="flex-1 overflow-y-auto p-3 md:p-4 flex flex-col gap-3 relative">
    {#if activeTab === 'map'}
      <!-- Large Touch Map Canvas (Dominates Screen) -->
      <div class="flex-1 w-full min-h-[500px] relative rounded-ares-md overflow-hidden border-2 border-ares-border-bright">
        <MarsCanvas
          region={mission.currentRegion}
          imageUrl={mapUrl}
          pois={mission.currentPois}
          selectedTarget={mission.selectedTarget}
          onSelectTarget={(target) => mission.selectTarget(target)}
        />

        <!-- Active Locked Target Floating HUD -->
        {#if mission.selectedTarget}
          <div class="absolute top-3 left-3 bg-ares-deep/95 border-2 border-ares-cyan p-3 rounded-ares-md shadow-ares-panel font-mono z-10 max-w-xs">
            <div class="flex items-center justify-between gap-2 mb-1">
              <span class="text-[10px] text-ares-cyan font-bold flex items-center gap-1">
                <Crosshair size={12} />
                LOCKED TARGET
              </span>
              <Badge provenance="measured" />
            </div>
            <div class="text-sm font-bold text-white truncate">{mission.selectedTarget.name}</div>
            <div class="text-xs text-ares-ice mt-0.5">
              {mission.selectedTarget.lat.toFixed(3)}°N &bull; {mission.selectedTarget.lon.toFixed(3)}°E
            </div>
          </div>
        {/if}
      </div>

    {:else if activeTab === 'hazards'}
      <!-- High-Contrast EVA Hazard Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card variant="elevated" title="REGOLITH TRACTION HAZARD">
          <div class="space-y-2 text-xs font-mono">
            <Badge hazardLevel="critical" label="SAND DUNE IMMOBILIZATION" />
            <p class="text-slate-200 text-sm leading-relaxed">
              Fine-grained eolian sand ripples lack bearing capacity. Do not traverse transverse dunes with slope &gt; 12°.
            </p>
            <div class="p-2.5 rounded bg-ares-deep border border-ares-border text-slate-300">
              Flight Rule: Turn rover downhill immediately if wheel slip exceeds 75%.
            </div>
          </div>
        </Card>

        <Card variant="elevated" title="SOLAR RADIATION &amp; THERMAL SWINGS">
          <div class="space-y-2 text-xs font-mono">
            <Badge hazardLevel="elevated" label="DIURNAL CYCLE -90°C TO +10°C" />
            <p class="text-slate-200 text-sm leading-relaxed">
              Extreme diurnal range creates mechanical stress on rover suspension and spacesuit thermal control loops.
            </p>
            <div class="p-2.5 rounded bg-ares-deep border border-ares-border text-slate-300">
              EVA Protocol: Maximum single excursion duration 4.5 hours outside pressurized cabin.
            </div>
          </div>
        </Card>
      </div>

    {:else if activeTab === 'route'}
      <!-- Route Staging for Tablet -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card variant="elevated" title="TRAVERSE STAGING">
          <div class="space-y-3 font-mono text-xs">
            <div>
              <span class="text-slate-400 block mb-1">SELECTED ROVER</span>
              <strong class="text-white text-sm">Pressurized Crew Rover (PCR-1) — 12 km/h</strong>
            </div>
            <div>
              <span class="text-slate-400 block mb-1">SAFETY FACTOR</span>
              <strong class="text-ares-green text-sm">Minimum Slope (Conservative Safety First)</strong>
            </div>
            <div class="p-3 bg-ares-deep rounded border border-ares-border">
              <span class="text-ares-amber block font-bold mb-1">PHASE 4 GRAPH SOLVER</span>
              NetworkX A* pathfinding will dynamically avoid slopes &gt;15° and compute watt-hour consumption.
            </div>
          </div>
        </Card>

        <Card variant="elevated" title="TARGET WAYPOINTS">
          <div class="space-y-2 font-mono text-xs">
            {#each mission.currentPois as poi}
              <button
                onclick={() => { mission.selectPoi(poi); activeTab = 'map'; }}
                class="w-full min-h-[48px] p-2.5 rounded bg-ares-navy hover:bg-space-700 border border-ares-border flex items-center justify-between text-left"
              >
                <div>
                  <div class="font-bold text-white text-xs">{poi.name}</div>
                  <div class="text-[10px] text-slate-400">{poi.lat.toFixed(2)}°N, {poi.lon.toFixed(2)}°E</div>
                </div>
                <Badge variant="cyan" label="SET TARGET" />
              </button>
            {/each}
          </div>
        </Card>
      </div>

    {:else if activeTab === 'science'}
      <!-- Science POIs for Tablet -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        {#each mission.currentPois as poi}
          <div class="ares-panel p-4 flex flex-col justify-between gap-3 font-mono">
            <div>
              <div class="flex items-center justify-between mb-1">
                <Badge provenance="measured" label={poi.id} />
                <span class="text-[10px] text-slate-400">{poi.lat.toFixed(2)}°N, {poi.lon.toFixed(2)}°E</span>
              </div>
              <h4 class="font-title text-sm font-bold text-white mt-1">{poi.name}</h4>
              <p class="text-xs text-slate-300 font-sans mt-1 leading-relaxed">{poi.description}</p>
            </div>
            <button
              onclick={() => { mission.selectPoi(poi); activeTab = 'map'; }}
              class="min-h-[48px] w-full py-2 bg-ares-cyan text-ares-deep font-bold rounded-ares flex items-center justify-center gap-2 text-xs"
            >
              <Crosshair size={14} /> LOCK ON SURFACE MAP
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </main>

  <!-- Minimal Tablet Bottom Navigation (48px Touch Targets) -->
  <nav class="bg-ares-navy border-t-2 border-ares-border grid grid-cols-4 select-none">
    <button
      onclick={() => activeTab = 'map'}
      class={`min-h-[56px] flex flex-col items-center justify-center gap-1 font-mono text-xs transition-colors border-r border-ares-border ${
        activeTab === 'map' ? 'bg-ares-cyan/20 text-ares-cyan font-bold border-t-2 border-t-ares-cyan' : 'text-slate-400 hover:text-white'
      }`}
    >
      <Compass size={20} />
      <span>SURFACE MAP</span>
    </button>

    <button
      onclick={() => activeTab === 'hazards'}
      class={`min-h-[56px] flex flex-col items-center justify-center gap-1 font-mono text-xs transition-colors border-r border-ares-border ${
        activeTab === 'hazards' ? 'bg-ares-red/20 text-ares-red font-bold border-t-2 border-t-ares-red' : 'text-slate-400 hover:text-white'
      }`}
    >
      <AlertTriangle size={20} />
      <span>EVA HAZARDS</span>
    </button>

    <button
      onclick={() => activeTab === 'route'}
      class={`min-h-[56px] flex flex-col items-center justify-center gap-1 font-mono text-xs transition-colors border-r border-ares-border ${
        activeTab === 'route' ? 'bg-ares-amber/20 text-ares-amber font-bold border-t-2 border-t-ares-amber' : 'text-slate-400 hover:text-white'
      }`}
    >
      <Route size={20} />
      <span>ROUTE PLAN</span>
    </button>

    <button
      onclick={() => activeTab === 'science'}
      class={`min-h-[56px] flex flex-col items-center justify-center gap-1 font-mono text-xs transition-colors ${
        activeTab === 'science' ? 'bg-ares-green/20 text-ares-green font-bold border-t-2 border-t-ares-green' : 'text-slate-400 hover:text-white'
      }`}
    >
      <Atom size={20} />
      <span>TARGETS</span>
    </button>
  </nav>
</div>

