<script lang="ts">
  import { mission } from '../../stores/mission.svelte';
  import { Layers, Info, Mountain, ShieldAlert } from '@lucide/svelte';
  import Card from '../ui/Card.svelte';
  import Badge from '../ui/Badge.svelte';
  import Table from '../ui/Table.svelte';

  const elevationColumns = [
    { key: 'swatch', header: 'COLOR', width: '70px', render: (row: any) => row.swatch },
    { key: 'label', header: 'BAND NAME', width: '150px', mono: true },
    { key: 'range', header: 'ELEVATION SPAN', width: '160px', mono: true },
    { key: 'desc', header: 'GEOMORPHIC FEATURE' },
  ];

  const elevationBands = [
    {
      swatch: 'violet',
      colorBg: 'bg-[#3b2d6a]',
      label: 'VIOLET / NAVY',
      desc: 'Deep impact basin floors (Hellas, Argyre, Gale crater floor)',
      range: '< -4,000 m',
    },
    {
      swatch: 'cyan',
      colorBg: 'bg-[#29788f]',
      label: 'CYAN / LIGHT BLUE',
      desc: 'Vast northern lowlands (Vastitas Borealis), ancient depositional surfaces',
      range: '-4,000 to -1,500 m',
    },
    {
      swatch: 'green',
      colorBg: 'bg-[#4da851]',
      label: 'GREEN / YELLOW',
      desc: 'Martian datum reference plains, ancient river delta floors',
      range: '-1,500 to +2,000 m',
    },
    {
      swatch: 'orange',
      colorBg: 'bg-[#c75e2e]',
      label: 'ORANGE / RED',
      desc: 'Southern cratered highlands, volcanic shield aprons',
      range: '+2,000 to +8,000 m',
    },
    {
      swatch: 'white',
      colorBg: 'bg-[#f4ebe6]',
      label: 'WHITE / PINK',
      desc: 'High-altitude volcanic caldera peaks (Olympus Mons summit)',
      range: '+8,000 to +21,000 m+',
    },
  ];
</script>

<div class="p-4 md:p-6 flex flex-col gap-5 max-w-7xl mx-auto">
  <!-- Geodetic Notice Banner -->
  <div class="ares-panel p-4 border-l-4 border-l-ares-cyan flex items-start gap-3 text-xs leading-relaxed text-slate-300">
    <Info size={18} class="text-ares-cyan shrink-0 mt-0.5" />
    <div class="space-y-1">
      <div class="flex items-center gap-2">
        <span class="text-ares-cyan font-title font-bold uppercase tracking-wider text-xs">
          MARTIAN AREOID GEODETIC DATUM STANDARD
        </span>
        <Badge provenance="measured" label="IAU 610 Pa DATUM" />
      </div>
      <p class="font-sans">
        Unlike Earth, Mars has no ocean surface. Elevations are defined relative to the Martian &ldquo;areoid&rdquo;&mdash;an equipotential gravitational surface where atmospheric pressure averages <strong>610 Pascals</strong> (the triple point of water).
        MOLA colourized tiles render these elevation ranges qualitatively.
      </p>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
    <!-- Left Column: Elevation Palette Key -->
    <Card variant="panel" title="MOLA ELEVATION PALETTE KEY">
      {#snippet headerRight()}
        <Badge provenance="simulated" label="QUALITATIVE BANDS" />
      {/snippet}

      <div class="space-y-2 mt-1">
        {#each elevationBands as band}
          <div class="p-2.5 rounded-ares bg-ares-deep/60 border border-ares-border flex items-center gap-3 text-xs font-mono">
            <div class={`w-4 h-4 rounded-ares-sm shrink-0 border border-white/20 ${band.colorBg}`}></div>
            <div class="flex-1 flex flex-col sm:flex-row sm:items-center justify-between gap-1">
              <div>
                <span class="font-bold text-white text-xs">{band.label}</span>
                <span class="text-[11px] text-slate-400 font-sans block sm:inline sm:ml-2">{band.desc}</span>
              </div>
              <span class="text-ares-green font-semibold text-xs shrink-0">{band.range}</span>
            </div>
          </div>
        {/each}
      </div>
    </Card>

    <!-- Right Column: Regional Topographic Profile -->
    <div class="space-y-4">
      <Card variant="elevated" title="SECTOR ELEVATION SPAN">
        {#snippet headerRight()}
          <Badge provenance="measured" />
        {/snippet}

        <div class="space-y-2 font-mono text-xs">
          <div class="text-lg font-bold text-white">{mission.currentRegion.elevation_approx}</div>
          <p class="text-slate-300 font-sans leading-relaxed text-xs">
            {mission.currentRegion.elevation_summary}
          </p>
        </div>
      </Card>

      <Card variant="panel" title="REGIONAL GEOLOGY &amp; MORPHOLOGY">
        <p class="text-xs text-slate-300 font-sans leading-relaxed">
          {mission.currentRegion.geology}
        </p>
      </Card>

      <!-- Altimetry Caution Card -->
      <div class="ares-panel p-4 border-l-2 border-l-ares-amber space-y-1.5 text-xs font-mono">
        <div class="flex items-center gap-2 text-ares-amber font-bold">
          <ShieldAlert size={15} />
          <span>ALTIMETRY DERIVATION INTEGRITY</span>
        </div>
        <p class="text-slate-300 font-sans text-xs leading-relaxed">
          PNG image pixels represent color-quantized cartography. In Phase 4, the backend will calculate true quantitative slopes and surface roughness profiles directly via mathematical coordinate interpolation, avoiding false pixel-hue elevation calculations.
        </p>
      </div>
    </div>
  </div>
</div>
