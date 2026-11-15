<script lang="ts">
  import { mission } from './lib/stores/mission.svelte';
  import Header from './lib/components/layout/Header.svelte';
  import Sidebar from './lib/components/layout/Sidebar.svelte';
  import TelemetryBar from './lib/components/layout/TelemetryBar.svelte';
  import RightInfoPanel from './lib/components/layout/RightInfoPanel.svelte';
  import Footer from './lib/components/layout/Footer.svelte';
  import TabletFieldView from './lib/components/layout/TabletFieldView.svelte';

  import OverviewView from './lib/components/views/OverviewView.svelte';
  import ExplorerView from './lib/components/views/ExplorerView.svelte';
  import RoutePlannerView from './lib/components/views/RoutePlannerView.svelte';
  import TerrainView from './lib/components/views/TerrainView.svelte';
  import HazardsView from './lib/components/views/HazardsView.svelte';
  import ScienceView from './lib/components/views/ScienceView.svelte';
</script>

{#if mission.interfaceMode === 'field'}
  <!-- Dedicated Distinct Astronaut Field Interface (Tablet / EVA) -->
  <TabletFieldView />
{:else}
  <!-- Desktop Mission Control Foundation -->
  <div class="h-screen w-screen bg-ares-deep text-slate-200 flex flex-col font-sans overflow-hidden select-none">
    <!-- Top Mission Status Bar -->
    <Header />

    <!-- Central Workspace: Left Sidebar + Central Work Area + Right Info Panel -->
    <div class="flex flex-1 overflow-hidden relative">
      <!-- Left Navigation Sidebar -->
      <Sidebar />

      <!-- Central Map & Module Workspace (DOMINATES WORKSPACE) -->
      <main class="flex-1 overflow-y-auto bg-ares-deep relative flex flex-col">
        {#if mission.activePage === 'Mission Overview'}
          <OverviewView />
        {:else if mission.activePage === 'Mars Explorer'}
          <ExplorerView />
        {:else if mission.activePage === 'Route Planner'}
          <RoutePlannerView />
        {:else if mission.activePage === 'Terrain Intelligence'}
          <TerrainView />
        {:else if mission.activePage === 'Hazard Analysis'}
          <HazardsView />
        {:else if mission.activePage === 'Science Discovery'}
          <ScienceView />
        {/if}
      </main>

      <!-- Collapsible Right Information Panel -->
      <RightInfoPanel />
    </div>

    <!-- Bottom Data & Telemetry Strip -->
    <TelemetryBar />

    <!-- Bottom Scientific Citations & Disclaimers Strip -->
    <Footer />
  </div>
{/if}
