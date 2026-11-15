<script lang="ts">
  import { mission } from '../../stores/mission.svelte';
  import { AlertTriangle, AlertOctagon, ShieldCheck, Info, ShieldAlert, Thermometer, Wind } from '@lucide/svelte';
  import Card from '../ui/Card.svelte';
  import Badge from '../ui/Badge.svelte';

  const hazards = [
    {
      title: 'SLOPE INCLINE & WHEEL SLIP',
      level: 'critical' as const,
      sub: 'Kinematic Suspension Limit',
      desc: 'On bedrock, rovers can ascend moderate slopes safely. However, on loose regolith (sand dunes), wheel slip exceeds 80% on slopes as low as 12°–15°, creating severe motor stall and immobilization risks.',
    },
    {
      title: 'EOLIAN SAND TRAPS & MEGARIPPLES',
      level: 'critical' as const,
      sub: 'Soil Shear Strength Deficit',
      desc: 'Fine-grained basaltic dust and sulfate-rich sands (such as the deposit that permanently entrapped NASA\'s Spirit rover at "Troy" in 2009) present negligible bearing capacity, risking wheel sinkage.',
    },
    {
      title: 'DUST STORMS & OPTICAL OPACITY (TAU)',
      level: 'elevated' as const,
      sub: 'Atmospheric Dynamics & Tau Index',
      desc: 'Martian dust storms drastically elevate atmospheric optical depth (tau). This curtails solar array power generation and severely degrades autonomous stereo hazard cameras.',
    },
    {
      title: 'THERMAL CYCLING & SOLAR RADIATION',
      level: 'elevated' as const,
      sub: 'Space Environment Subsystem Fatigue',
      desc: 'Diurnal temperature swings from -90°C at night to +10°C at midday induce thermal fatigue on welds and electronics. Lack of an intrinsic global magnetic field exposes crews and electronics to cosmic rays.',
    },
  ];
</script>

<div class="p-4 md:p-6 flex flex-col gap-5 max-w-7xl mx-auto">
  <!-- Engineering Fact Banner -->
  <div class="ares-panel p-4 border-l-4 border-l-ares-red flex items-start gap-3 text-xs leading-relaxed text-slate-300">
    <Info size={18} class="text-ares-red shrink-0 mt-0.5" />
    <div class="space-y-1">
      <div class="flex items-center gap-2">
        <span class="text-ares-red font-title font-bold uppercase tracking-wider text-xs">
          ROVER KINEMATICS &amp; SOIL MECHANICS PRINCIPLES
        </span>
        <Badge provenance="calculated" label="ROCKER-BOGIE MECHANICS" />
      </div>
      <p class="font-sans">
        There is <strong>no single universal slope safety limit</strong> on Mars. Safe traversal angles depend on chassis suspension (e.g. NASA's 6-wheel rocker-bogie), wheel diameter, and soil shear strength. While NASA rovers possess static stability beyond 40° on firm bedrock, mission flight rules typically restrict autonomous driving to slopes below <strong>15°–20°</strong> to prevent uncontrollable wheel slip.
      </p>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
    <!-- Left Column: Hazard Profiles -->
    <div class="space-y-3">
      <div class="hud-label text-slate-200 flex items-center gap-2 mb-1">
        <AlertTriangle size={15} class="text-ares-red" />
        <span>MARTIAN ENVIRONMENTAL HAZARDS</span>
      </div>

      {#each hazards as hz}
        <Card variant="panel">
          <div class="flex flex-col gap-2 font-mono text-xs">
            <div class="flex justify-between items-start gap-2">
              <span class="font-title font-bold text-white text-sm">{hz.title}</span>
              <Badge hazardLevel={hz.level} label={hz.sub} />
            </div>
            <p class="text-slate-300 font-sans text-xs leading-relaxed">{hz.desc}</p>
          </div>
        </Card>
      {/each}
    </div>

    <!-- Right Column: Sector Protocols & Mitigation -->
    <div class="space-y-4">
      <Card variant="elevated" title="SECTOR SAFETY CORRIDOR STATUS">
        {#snippet headerRight()}
          <Badge hazardLevel="nominal" label="MONITORED" />
        {/snippet}

        <div class="space-y-2 font-mono text-xs">
          <div class="text-lg font-bold text-ares-green">OPERATIONAL CORRIDOR CLEAR</div>
          <div class="text-slate-300">
            Active Zone: <strong class="text-white">{mission.currentRegion.name}</strong> ({mission.currentRegion.lat.toFixed(2)}°N, {mission.currentRegion.lon.toFixed(2)}°E)
          </div>
        </div>
      </Card>

      <Card variant="panel" title="EXPLORATION SAFETY PROTOCOLS">
        <div class="space-y-2.5 text-xs text-slate-300 font-mono">
          <div class="p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border">
            ● <strong class="text-white">Autonomous Drive Threshold:</strong> Flight rules cap automatic drive steps when slopes exceed 15°.
          </div>
          <div class="p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border">
            ● <strong class="text-white">Visual Odometry:</strong> Rover compares successive camera frames to detect wheel slippage before getting stuck.
          </div>
          <div class="p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border">
            ● <strong class="text-white">Ventifact Avoidance:</strong> Sharp, wind-sculpted rocks are actively avoided to preserve aluminum wheel treads.
          </div>
          <div class="p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border">
            ● <strong class="text-white">Solar Margin:</strong> Minimum 30% battery reserve required before entering shaded crater wall areas.
          </div>
        </div>
      </Card>
    </div>
  </div>
</div>
