<script lang="ts">
  import { mission } from '../../stores/mission.svelte';
  import { Radio, Monitor, Tablet, Menu, Activity, PanelRight, ShieldCheck, WifiOff, Wifi } from '@lucide/svelte';
  import Badge from '../ui/Badge.svelte';
</script>

<header class="h-14 border-b border-ares-border bg-ares-navy/95 px-4 flex items-center justify-between sticky top-0 z-40 select-none">
  <!-- Left: Brand & Mobile/Sidebar Toggle -->
  <div class="flex items-center gap-3">
    <button 
      onclick={() => mission.toggleSidebar()}
      class="p-2 text-slate-400 hover:text-white rounded-ares border border-ares-border hover:border-ares-border-bright transition-colors"
      aria-label="Toggle navigation"
      title="Toggle Navigation Sidebar"
    >
      <Menu size={18} />
    </button>

    <div class="flex items-center gap-2.5">
      <div class="w-2.5 h-2.5 rounded-full bg-ares-cyan shadow-ares-glow-cyan animate-pulse"></div>
      <h1 class="font-title font-bold tracking-wider text-base text-white">
        ARES <span class="text-xs font-sans font-normal text-slate-400 hidden sm:inline">| MISSION CONTROL</span>
      </h1>
    </div>

    <!-- Active Region Badge -->
    <div class="hidden md:flex items-center gap-1.5 ml-4 px-2.5 py-1 rounded-ares bg-ares-deep border border-ares-border text-xs font-mono">
      <span class="text-slate-400">ZONE:</span>
      <span class="text-ares-cyan font-bold uppercase">{mission.currentRegion.name}</span>
    </div>
  </div>

  <!-- Center: Scientific Mission Clock & Status (Desktop) -->
  <div class="hidden lg:flex items-center gap-6 font-mono text-xs">
    <div class="flex items-center gap-2">
      <span class="hud-label text-slate-400">SOL:</span>
      <span class="text-white font-bold tracking-wider">{mission.telemetry.sol}</span>
      <Badge provenance="measured" label="IAU MTC" />
    </div>

    <div class="flex items-center gap-2">
      <span class="hud-label text-slate-400">COMM DELAY:</span>
      <span class="text-ares-amber font-bold">{mission.telemetry.commDelay}</span>
      <Badge provenance="calculated" label="ORBITAL GEOM" />
    </div>

    <div class="flex items-center gap-1.5">
      <span class="hud-label text-slate-400">SYS:</span>
      <Badge variant="green">
        <Activity size={10} class="animate-pulse" />
        {mission.telemetry.systemStatus}
      </Badge>
    </div>
  </div>

  <!-- Right: Persistent Offline Connectivity & Interface Mode Toggle -->
  <div class="flex items-center gap-2.5">
    <!-- Persistent Offline / Telemetry Sync Indicator -->
    <div 
      class={`flex items-center gap-1.5 px-2.5 py-1 rounded-ares text-[11px] font-mono border transition-all ${
        mission.backendConnected 
          ? 'bg-ares-green/10 text-ares-green border-ares-green/40 shadow-ares-glow-green/20' 
          : 'bg-ares-amber/10 text-ares-amber border-ares-amber/40'
      }`}
      title={mission.backendConnected ? 'Telemetry Stream Active (FastAPI Connected)' : 'Operating in Autonomous Offline / Field Cache Mode'}
    >
      {#if mission.backendConnected}
        <Wifi size={12} class="animate-pulse text-ares-green" />
        <span class="font-bold hidden sm:inline">LINK ONLINE</span>
      {:else}
        <WifiOff size={12} class="text-ares-amber" />
        <span class="font-bold hidden sm:inline">FIELD CACHE (OFFLINE)</span>
      {/if}
    </div>

    <!-- Mode Toggle: Desktop Mission Control vs Astronaut Field Interface -->
    <div class="flex items-center rounded-ares bg-ares-deep p-0.5 border border-ares-border">
      <button
        onclick={() => mission.setInterfaceMode('desktop')}
        class={`flex items-center gap-1.5 px-2.5 py-1 rounded-ares text-xs font-mono transition-all duration-150 ${
          mission.interfaceMode === 'desktop'
            ? 'bg-ares-cyan/20 text-ares-cyan font-bold border border-ares-cyan/50 shadow-ares-glow-cyan/20'
            : 'text-slate-400 hover:text-white'
        }`}
        title="Desktop Mission Control (Full Telemetry & Panels)"
      >
        <Monitor size={14} />
        <span class="hidden md:inline">DESKTOP</span>
      </button>

      <button
        onclick={() => mission.setInterfaceMode('field')}
        class={`flex items-center gap-1.5 px-2.5 py-1 rounded-ares text-xs font-mono transition-all duration-150 ${
          mission.interfaceMode === 'field'
            ? 'bg-ares-amber/20 text-ares-amber font-bold border border-ares-amber/50 shadow-ares-glow-amber/20'
            : 'text-slate-400 hover:text-white'
        }`}
        title="Astronaut Field Interface (Touch Optimized Tablet / EVA)"
      >
        <Tablet size={14} />
        <span class="hidden md:inline">TABLET FIELD</span>
      </button>
    </div>

    <!-- Toggle Right Collapsible Information Drawer -->
    <button
      onclick={() => mission.toggleRightDrawer()}
      class={`p-2 rounded-ares border transition-colors ${
        mission.rightDrawerOpen 
          ? 'bg-ares-cyan/15 border-ares-cyan text-ares-cyan' 
          : 'bg-ares-deep border-ares-border text-slate-400 hover:text-white hover:border-ares-border-bright'
      }`}
      title="Toggle Information Drawer"
      aria-label="Toggle Information Drawer"
    >
      <PanelRight size={16} />
    </button>
  </div>
</header>
