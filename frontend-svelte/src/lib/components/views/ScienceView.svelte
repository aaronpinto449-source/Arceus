<script lang="ts">
  import { onMount } from 'svelte';
  import { mission } from '../../stores/mission.svelte';
  import { api } from '../../services/api';
  import { Microscope, Award, Bookmark, Crosshair, ExternalLink, Globe, Compass, ShieldAlert } from '@lucide/svelte';

  let challengeData = $state<{
    challenge: string;
    challenge_url: string;
    resources: Record<string, any>;
  } | null>(null);

  onMount(async () => {
    try {
      challengeData = await api.getChallengeResources();
    } catch {
      // Handled gracefully via fallback in api.ts
    }
  });
</script>

<div class="p-4 md:p-6 flex flex-col gap-6 max-w-7xl mx-auto">
  <!-- Verified Science Catalog Banner -->
  <div class="aerospace-panel p-4 border-l-4 border-ares-green flex items-start gap-3 text-xs leading-relaxed text-slate-300">
    <Award size={18} class="text-ares-green shrink-0 mt-0.5" />
    <div>
      <div class="text-ares-green font-mono font-bold uppercase mb-1">
        VERIFIED PLANETARY SCIENCE ARCHIVE (NASA PDS / IAU)
      </div>
      The scientific points of interest below represent verified ground targets compiled from NASA mission archives 
      (Curiosity MSL, Perseverance Mars 2020, and MGS/MRO orbital surveys). Coordinates represent true planetocentric locations.
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Left 2 Columns: Detailed POI Cards -->
    <div class="lg:col-span-2 flex flex-col gap-4">
      <div class="hud-label text-slate-200 flex items-center gap-2 mb-1">
        <Microscope size={16} class="text-ares-green" />
        <span>SCIENTIFIC TARGET CATALOG — {mission.currentRegion.name.toUpperCase()}</span>
      </div>

      {#each mission.currentPois as poi}
        {@const isSelected = mission.selectedPoi?.id === poi.id}
        <div class={`aerospace-panel p-5 flex flex-col gap-3 font-mono transition-all duration-150 ${isSelected ? 'border-ares-cyan shadow-[0_0_12px_rgba(0,240,255,0.15)]' : ''}`}>
          <div class="flex items-center justify-between">
            <span class="text-base font-bold text-white">{poi.name}</span>
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-bold text-ares-green bg-ares-green/10 border border-ares-green/30 px-2 py-0.5 rounded">
                {poi.id}
              </span>
              <button
                onclick={() => mission.selectPoi(poi)}
                class={`px-2 py-0.5 rounded text-[10px] font-mono transition-all flex items-center gap-1 ${
                  isSelected 
                    ? 'bg-ares-cyan text-black font-bold' 
                    : 'bg-space-800 text-ares-cyan hover:bg-ares-cyan/20 border border-space-border'
                }`}
              >
                <Crosshair size={11} />
                {isSelected ? 'LOCKED' : 'LOCK TARGET'}
              </button>
            </div>
          </div>

          <div class="text-xs text-ares-cyan flex flex-wrap gap-x-3 gap-y-1">
            <span>COORDINATES: {poi.lat.toFixed(4)}° N, {poi.lon.toFixed(4)}° E</span>
            <span class="text-slate-500">|</span>
            <span>TYPE: {poi.type}</span>
          </div>

          <p class="text-xs text-slate-300 leading-relaxed font-sans">{poi.description}</p>

          <div class="pt-2 border-t border-space-border/60 text-xs flex flex-col gap-1">
            <div>
              <span class="text-ares-amber font-semibold">EXPLORATION VALUE: </span>
              <span class="text-slate-300 font-sans">{poi.significance}</span>
            </div>

            {#if poi.source_reference}
              <div class="text-[10px] text-slate-400 flex items-center gap-1 mt-1">
                <Bookmark size={11} class="text-slate-400 shrink-0" />
                <span class="truncate">Citation: <span class="text-slate-300">{poi.source_reference}</span></span>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>

    <!-- Right Column: Mission Objectives & Sample Caching -->
    <div class="flex flex-col gap-4">
      <div class="aerospace-panel p-5 flex flex-col gap-2">
        <div class="hud-label text-slate-300">PRIMARY GEOLOGICAL GOAL</div>
        <div class="text-base font-bold text-white">{mission.currentRegion.objective}</div>
        <p class="text-xs text-slate-300 font-mono leading-relaxed mt-1">{mission.currentRegion.description}</p>
      </div>

      <div class="aerospace-panel p-5 flex flex-col gap-2">
        <div class="hud-label text-ares-green">MISSION CONTEXT</div>
        <div class="text-sm font-bold text-ares-green">{mission.currentRegion.mission_context}</div>
        <p class="text-xs text-slate-400 font-mono leading-relaxed mt-1">
          NASA surface rovers utilize multispectral imaging, alpha-particle X-ray spectrometers (APXS),
          and robotic rock drills at these exact geological formations.
        </p>
      </div>

      <div class="aerospace-panel p-5 text-xs font-mono flex flex-col gap-3">
        <div class="hud-label text-ares-coral">EXPEDITION SAMPLE CACHING PRIORITIES</div>
        <div class="flex flex-col gap-2 text-slate-300 pt-1">
          <p>
            ● <strong class="text-white">Igneous Cumulates:</strong> Provide precise radiometric crystallization age dating.
          </p>
          <p>
            ● <strong class="text-white">Fine-grained Mudstones:</strong> Highest preservation potential for ancient organic molecules.
          </p>
          <p>
            ● <strong class="text-white">Hydrated Sulfates & Clays:</strong> Reveal timing and chemistry of ancient surface water desiccation.
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- Official NASA Space Apps Challenge 2026 Resources Panel -->
  {#if challengeData}
    <div class="aerospace-panel p-5 flex flex-col gap-4 border-t-2 border-ares-cyan">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-space-border/60 pb-3">
        <div class="flex items-center gap-2">
          <Globe size={18} class="text-ares-cyan" />
          <div>
            <h3 class="text-sm font-bold text-white tracking-wide">
              OFFICIAL NASA SPACE APPS CHALLENGE 2026 RESOURCES
            </h3>
            <p class="text-[11px] text-slate-400 font-mono">
              Challenge: {challengeData.challenge}
            </p>
          </div>
        </div>
        <a
          href={challengeData.challenge_url}
          target="_blank"
          rel="noopener noreferrer"
          class="text-[11px] font-mono text-ares-cyan hover:underline flex items-center gap-1 shrink-0"
        >
          <span>Official Portal</span>
          <ExternalLink size={12} />
        </a>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each Object.entries(challengeData.resources) as [key, res]}
          <div class={`p-4 rounded border flex flex-col justify-between gap-3 font-mono text-xs transition-colors ${
            res.is_mars_specific 
              ? 'bg-space-900/80 border-space-border hover:border-ares-cyan/50' 
              : 'bg-space-950/60 border-space-border/50 opacity-90'
          }`}>
            <div class="flex flex-col gap-1.5">
              <div class="flex items-center justify-between gap-2">
                <span class={`text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase ${
                  res.is_mars_specific
                    ? 'text-ares-cyan bg-ares-cyan/10 border-ares-cyan/30'
                    : 'text-slate-400 bg-slate-800 border-slate-700'
                }`}>
                  {res.is_mars_specific ? 'Mars Resource' : 'General Reference'}
                </span>
                <span class="text-[10px] text-slate-400 truncate">{res.authority}</span>
              </div>

              <div class="font-bold text-white text-sm mt-1">{res.title}</div>
              <div class="text-[11px] text-ares-amber">{res.category}</div>
              <p class="text-[11px] text-slate-300 font-sans leading-relaxed mt-1">{res.description}</p>
            </div>

            <div class="pt-2 border-t border-space-border/50 flex items-center justify-between text-[11px]">
              <span class="text-slate-400 text-[10px]">{key}</span>
              <a
                href={res.url}
                target="_blank"
                rel="noopener noreferrer"
                class="text-ares-cyan hover:underline flex items-center gap-1 font-semibold"
              >
                <span>Access Data</span>
                <ExternalLink size={11} />
              </a>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

