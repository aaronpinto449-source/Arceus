<script lang="ts">
  import { mission } from '../../stores/mission.svelte';
  import type { NavigationPage } from '../../types';
  import { 
    LayoutDashboard, 
    Compass, 
    Route, 
    Mountain, 
    AlertTriangle, 
    Atom, 
    Crosshair,
    ChevronLeft,
    ChevronRight,
    MapPin
  } from '@lucide/svelte';

  interface NavItem {
    id: NavigationPage;
    label: string;
    sublabel: string;
    icon: typeof LayoutDashboard;
  }

  const navItems: NavItem[] = [
    { id: 'Mission Overview', label: 'Mission Overview', sublabel: 'Tactical Status', icon: LayoutDashboard },
    { id: 'Mars Explorer', label: 'Mars Explorer', sublabel: 'MOLA Surface View', icon: Compass },
    { id: 'Route Planner', label: 'Route Planner', sublabel: 'Multi-Waypoints', icon: Route },
    { id: 'Terrain Intelligence', label: 'Terrain Intelligence', sublabel: 'Hypsometry & Slope', icon: Mountain },
    { id: 'Hazard Analysis', label: 'Hazard Analysis', sublabel: 'Slope & Thermal Alert', icon: AlertTriangle },
    { id: 'Science Discovery', label: 'Science Discovery', sublabel: 'NASA Targets', icon: Atom },
  ];
</script>

<aside 
  class={`bg-ares-navy border-r border-ares-border flex flex-col justify-between transition-all duration-200 z-30 select-none
    ${mission.sidebarOpen ? 'w-64 min-w-[16rem]' : 'w-16 min-w-[4rem]'}
    ${mission.interfaceMode === 'field' ? 'bg-ares-deep border-ares-border-bright' : ''}
  `}
>
  <!-- Navigation Sections -->
  <div class="p-3 flex flex-col gap-4 overflow-y-auto">
    <!-- Operational Zone (Region Selector) -->
    <div class="flex flex-col gap-1.5">
      {#if mission.sidebarOpen}
        <div class="flex items-center justify-between px-1">
          <span class="hud-label text-slate-400">OPERATIONAL ZONE</span>
          <span class="text-[10px] font-mono text-ares-cyan font-bold">256 PPD</span>
        </div>
      {/if}

      <div class="flex flex-col gap-1">
        {#each mission.regions as region}
          {@const isSelected = mission.activeRegionId === region.id}
          <button
            onclick={() => mission.setActiveRegion(region.id)}
            class={`text-left rounded-ares transition-all duration-150 flex items-center gap-2.5 
              ${mission.sidebarOpen ? 'px-3 py-2' : 'p-2 justify-center'}
              ${mission.interfaceMode === 'field' ? 'min-h-[48px] py-3' : ''}
              ${isSelected 
                ? 'bg-ares-cyan/15 border border-ares-cyan/50 text-white shadow-ares-glow-cyan/20' 
                : 'bg-ares-deep/60 hover:bg-ares-elevated border border-ares-border text-slate-300 hover:text-white'
              }
            `}
            title={region.name}
          >
            <div class={`w-2 h-2 rounded-full shrink-0 ${isSelected ? 'bg-ares-cyan shadow-ares-glow-cyan animate-pulse' : 'bg-slate-600'}`}></div>
            {#if mission.sidebarOpen}
              <div class="flex flex-col overflow-hidden">
                <span class="text-xs font-mono font-bold tracking-tight truncate">{region.name}</span>
                <span class="text-[10px] font-mono text-slate-400 truncate">{region.lat.toFixed(1)}°N, {region.lon.toFixed(1)}°E</span>
              </div>
            {/if}
          </button>
        {/each}
      </div>
    </div>

    <!-- Divider -->
    <div class="border-t border-ares-border my-0.5"></div>

    <!-- Navigation Modules -->
    <div class="flex flex-col gap-1">
      {#if mission.sidebarOpen}
        <span class="hud-label px-1 text-slate-400">MISSION MODULES</span>
      {/if}

      {#each navItems as item}
        {@const isActive = mission.activePage === item.id}
        {@const IconComponent = item.icon}
        <button
          onclick={() => mission.setActivePage(item.id)}
          class={`flex items-center gap-3 rounded-ares text-left transition-all duration-150 relative group
            ${mission.sidebarOpen ? 'px-3 py-2.5' : 'p-2.5 justify-center'}
            ${mission.interfaceMode === 'field' ? 'min-h-[48px] py-3' : ''}
            ${isActive 
              ? 'bg-ares-elevated border-l-2 border-ares-cyan border-t border-r border-b border-ares-border text-white shadow-sm' 
              : 'hover:bg-ares-elevated/40 border border-transparent text-slate-400 hover:text-slate-200'
            }
          `}
          title={item.label}
        >
          <div class={`shrink-0 ${isActive ? 'text-ares-cyan' : 'text-slate-400 group-hover:text-white'}`}>
            <IconComponent size={mission.interfaceMode === 'field' ? 20 : 17} />
          </div>
          {#if mission.sidebarOpen}
            <div class="flex flex-col overflow-hidden">
              <span class={`text-xs font-mono font-bold truncate ${isActive ? 'text-white' : 'text-slate-300'}`}>
                {item.label}
              </span>
              <span class="text-[10px] font-mono text-slate-500 truncate">{item.sublabel}</span>
            </div>
          {/if}
        </button>
      {/each}
    </div>
  </div>

  <!-- Bottom Coordinates Card / Target Pin -->
  <div class="p-3 border-t border-ares-border bg-ares-deep/60 font-mono">
    {#if mission.sidebarOpen}
      <div class="flex items-center justify-between text-[10px] text-slate-400 mb-1.5">
        <span class="flex items-center gap-1 font-bold text-ares-ice">
          <Crosshair size={11} class="text-ares-cyan" />
          ACTIVE TARGET
        </span>
        <button 
          onclick={() => mission.toggleRightDrawer()}
          class="text-[10px] text-ares-cyan hover:underline"
        >
          INSPECT
        </button>
      </div>
      {#if mission.selectedTarget}
        <div class="bg-ares-navy border border-ares-border p-2 rounded-ares text-[11px] flex flex-col gap-0.5">
          <div class="font-bold text-ares-cyan truncate">{mission.selectedTarget.name}</div>
          <div class="text-[10px] text-slate-400">
            {mission.selectedTarget.lat.toFixed(3)}°N | {mission.selectedTarget.lon.toFixed(3)}°E
          </div>
        </div>
      {:else}
        <div class="bg-ares-navy/60 border border-ares-border/60 p-2 rounded-ares text-[10px] text-slate-500 italic">
          No target locked. Select POI or map coordinate.
        </div>
      {/if}
    {:else}
      <button 
        onclick={() => mission.toggleRightDrawer()}
        class="w-full flex justify-center text-ares-cyan py-1 hover:text-ares-ice" 
        title="View Locked Target Telemetry"
      >
        <Crosshair size={16} />
      </button>
    {/if}
  </div>
</aside>
