<script lang="ts">
  import { mission } from '../../stores/mission.svelte';
  import { Navigation, Compass, Info, CheckCircle2, AlertTriangle, ArrowRight, Shield } from '@lucide/svelte';
  import Card from '../ui/Card.svelte';
  import Button from '../ui/Button.svelte';
  import Badge from '../ui/Badge.svelte';

  let startPoiName = $state(mission.currentPois[0]?.name || 'Base Camp');
  let destPoiName = $state(mission.currentPois[1]?.name || 'Science Target Alpha');
  let vehicleType = $state('pcr');
  let traversalPriority = $state('balanced');

  $effect(() => {
    if (mission.currentPois.length >= 2) {
      startPoiName = mission.currentPois[0].name;
      destPoiName = mission.currentPois[1].name;
    }
  });

  const vehicles = [
    { id: 'pcr', name: 'Pressurized Crew Rover (PCR-1)', speed: '12 km/h', range: '120 km', crew: '2 Astronauts' },
    { id: 'luv', name: 'Lightweight Unpressurized Scout (LUV)', speed: '18 km/h', range: '45 km', crew: '1 EVA Suit' },
    { id: 'hch', name: 'Heavy Cargo & Habitat Hauler (HCH)', speed: '6 km/h', range: '80 km', crew: '4 Crew / Cargo' }
  ];

  const selectedVehicle = $derived(vehicles.find(v => v.id === vehicleType) || vehicles[0]);
</script>

<div class="p-4 md:p-6 flex flex-col gap-5 max-w-7xl mx-auto">
  <!-- Simulation Notice Banner -->
  <div class="ares-panel p-4 border-l-4 border-l-ares-amber flex items-start gap-3 text-xs leading-relaxed text-slate-300">
    <Info size={18} class="text-ares-amber shrink-0 mt-0.5" />
    <div class="space-y-1">
      <div class="flex items-center gap-2">
        <span class="text-ares-amber font-title font-bold uppercase tracking-wider text-xs">
          EXPEDITION PLANNING ENGINE (PHASE 4 FOUNDATION)
        </span>
        <Badge provenance="simulated" label="TRAVERSE MODEL" />
      </div>
      <p class="font-sans">
        This module defines mission parameters and waypoint nodes. Algorithmic pathfinding (A* graph search over synthetic terrain cost grids)
        and dynamic astronaut life-support consumption models are scheduled for subsequent milestones.
      </p>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
    <!-- Left Column: Mission Expedition Configuration -->
    <Card variant="panel" title="EXPEDITION CONFIGURATION">
      {#snippet headerRight()}
        <Compass size={16} class="text-ares-cyan" />
      {/snippet}

      <div class="space-y-4 font-mono text-xs">
        <div class="space-y-1.5">
          <label for="departure-select" class="hud-label text-slate-300 block">
            DEPARTURE POINT (START WAYPOINT)
          </label>
          <select
            id="departure-select"
            bind:value={startPoiName}
            class="w-full bg-ares-deep border border-ares-border rounded-ares px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-ares-cyan cursor-pointer"
          >
            {#each mission.currentPois as p}
              <option value={p.name}>
                {p.name} ({p.type})
              </option>
            {/each}
          </select>
        </div>

        <div class="space-y-1.5">
          <label for="dest-select" class="hud-label text-slate-300 block">
            TARGET DESTINATION (END WAYPOINT)
          </label>
          <select
            id="dest-select"
            bind:value={destPoiName}
            class="w-full bg-ares-deep border border-ares-border rounded-ares px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-ares-cyan cursor-pointer"
          >
            {#each mission.currentPois as p}
              <option value={p.name}>
                {p.name} ({p.type})
              </option>
            {/each}
          </select>
        </div>

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

        <div class="space-y-1.5">
          <span class="hud-label text-slate-300 block">TRAVERSAL PRIORITY</span>
          <div class="space-y-1.5 font-mono text-xs">
            {#each [
              { id: 'balanced', label: 'Balanced (Optimal Energy & Moderate Slope)' },
              { id: 'safety', label: 'Minimum Slope (Conservative Safety First)' },
              { id: 'direct', label: 'Direct Traversal (Distance Minimization)' }
            ] as opt}
              <label class="flex items-center gap-2.5 p-2 rounded-ares bg-ares-deep/60 border border-ares-border cursor-pointer hover:bg-ares-elevated transition-colors">
                <input
                  type="radio"
                  name="priority"
                  value={opt.id}
                  bind:group={traversalPriority}
                  class="text-ares-cyan focus:ring-0"
                />
                <span class="text-slate-300 text-[11px]">{opt.label}</span>
              </label>
            {/each}
          </div>
        </div>
      </div>
    </Card>

    <!-- Right 2 Columns: Route Staging & Telemetry Preview -->
    <div class="lg:col-span-2 space-y-4">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="ares-panel p-3">
          <div class="hud-label text-slate-400">EXPEDITION STATUS</div>
          <div class="text-base font-mono font-bold text-ares-amber mt-1">CONFIGURED</div>
          <div class="text-[10px] font-mono text-slate-400 mt-0.5">Ready for A* solver</div>
        </div>

        <div class="ares-panel p-3">
          <div class="hud-label text-slate-400">DEPARTURE</div>
          <div class="text-xs font-mono font-bold text-white mt-1 truncate" title={startPoiName}>{startPoiName}</div>
          <div class="text-[10px] font-mono text-slate-400 mt-0.5">{mission.currentRegion.name}</div>
        </div>

        <div class="ares-panel p-3">
          <div class="hud-label text-slate-400">DESTINATION</div>
          <div class="text-xs font-mono font-bold text-ares-cyan mt-1 truncate" title={destPoiName}>{destPoiName}</div>
          <div class="text-[10px] font-mono text-slate-400 mt-0.5">Target waypoint</div>
        </div>

        <div class="ares-panel p-3">
          <div class="hud-label text-slate-400">ROUTER ENGINE</div>
          <div class="text-base font-mono font-bold text-ares-coral mt-1">PHASE 4</div>
          <div class="text-[10px] font-mono text-slate-400 mt-0.5">NetworkX solver</div>
        </div>
      </div>

      <!-- Vehicle Specifications -->
      <Card variant="panel" title="ACTIVE ROVER SPECIFICATIONS" subtitle={selectedVehicle.name}>
        <div class="grid grid-cols-3 gap-3 font-mono text-xs">
          <div class="bg-ares-deep/60 p-2.5 rounded-ares border border-ares-border">
            <span class="text-slate-400 text-[10px] block">NOMINAL SPEED</span>
            <strong class="text-ares-cyan text-sm">{selectedVehicle.speed}</strong>
          </div>
          <div class="bg-ares-deep/60 p-2.5 rounded-ares border border-ares-border">
            <span class="text-slate-400 text-[10px] block">MAX RANGE</span>
            <strong class="text-ares-green text-sm">{selectedVehicle.range}</strong>
          </div>
          <div class="bg-ares-deep/60 p-2.5 rounded-ares border border-ares-border">
            <span class="text-slate-400 text-[10px] block">PAYLOAD / CREW</span>
            <strong class="text-ares-amber text-sm">{selectedVehicle.crew}</strong>
          </div>
        </div>
      </Card>

      <!-- Architecture Breakdown -->
      <Card variant="tactical" title="TERRAIN-AWARE ROUTE PLANNING ARCHITECTURE">
        {#snippet headerRight()}
          <Badge provenance="simulated" label="NETWORKX GRAPH" />
        {/snippet}

        <p class="text-xs text-slate-300 font-sans leading-relaxed mb-3">
          In Phase 4, ARES will evaluate surface traversability by transforming the regional MOLA basemap into a weighted grid graph:
        </p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono">
          <div class="p-3 rounded-ares bg-ares-deep/60 border border-ares-border flex flex-col gap-1">
            <span class="text-ares-cyan font-bold block">1. SLOPE PENALTY</span>
            <span class="text-slate-400 text-[11px] font-sans leading-relaxed">
              Costs scale exponentially as incline approaches rover wheel slippage thresholds (~15°–20°).
            </span>
          </div>
          <div class="p-3 rounded-ares bg-ares-deep/60 border border-ares-border flex flex-col gap-1">
            <span class="text-ares-amber font-bold block">2. REGOLITH RISKS</span>
            <span class="text-slate-400 text-[11px] font-sans leading-relaxed">
              Identified eolian sand dunes receive high traversal impedance to avoid entrapment.
            </span>
          </div>
          <div class="p-3 rounded-ares bg-ares-deep/60 border border-ares-border flex flex-col gap-1">
            <span class="text-ares-green font-bold block">3. POWER &amp; TIME</span>
            <span class="text-slate-400 text-[11px] font-sans leading-relaxed">
              Calculates watt-hour consumption and sol sunlight windows along safe bedrock corridors.
            </span>
          </div>
        </div>
      </Card>
    </div>
  </div>
</div>
