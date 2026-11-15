<script lang="ts">
  import type { Snippet } from 'svelte';
  import { CheckCircle2, Calculator, Cpu, AlertTriangle, AlertOctagon, ShieldCheck } from '@lucide/svelte';

  interface Props {
    variant?: 'cyan' | 'amber' | 'red' | 'green' | 'neutral';
    provenance?: 'measured' | 'calculated' | 'simulated';
    hazardLevel?: 'nominal' | 'elevated' | 'critical';
    label?: string;
    children?: Snippet;
    class?: string;
  }

  let {
    variant = 'neutral',
    provenance,
    hazardLevel,
    label,
    children,
    class: extraClass = ''
  }: Props = $props();

  const variantStyles = {
    cyan: 'bg-ares-cyan/15 text-ares-cyan border-ares-cyan/40',
    amber: 'bg-ares-amber/15 text-ares-amber border-ares-amber/40',
    red: 'bg-ares-red/15 text-ares-red border-ares-red/40',
    green: 'bg-ares-green/15 text-ares-green border-ares-green/40',
    neutral: 'bg-ares-border/60 text-slate-300 border-ares-border',
  };
</script>

{#if provenance}
  <!-- Scientific Data Provenance Badges -->
  {#if provenance === 'measured'}
    <span class={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-ares-sm text-[10px] font-mono font-bold tracking-wider uppercase border bg-ares-green/15 text-ares-green border-ares-green/40 ${extraClass}`} title="Measured scientific data sourced from NASA orbiters or surface landers">
      <CheckCircle2 size={10} class="shrink-0" />
      <span>[MEASURED]</span>
      {#if label}<span class="font-normal text-slate-300">| {label}</span>{/if}
    </span>
  {:else if provenance === 'calculated'}
    <span class={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-ares-sm text-[10px] font-mono font-bold tracking-wider uppercase border bg-ares-cyan/15 text-ares-cyan border-ares-cyan/40 ${extraClass}`} title="Deterministically calculated metric derived mathematically from planetary constants">
      <Calculator size={10} class="shrink-0" />
      <span>[CALCULATED]</span>
      {#if label}<span class="font-normal text-slate-300">| {label}</span>{/if}
    </span>
  {:else if provenance === 'simulated'}
    <span class={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-ares-sm text-[10px] font-mono font-bold tracking-wider uppercase border bg-ares-amber/15 text-ares-amber border-ares-amber/40 ${extraClass}`} title="Illustrative or simulated model for mission planning">
      <Cpu size={10} class="shrink-0" />
      <span>[SIMULATED]</span>
      {#if label}<span class="font-normal text-slate-300">| {label}</span>{/if}
    </span>
  {/if}

{:else if hazardLevel}
  <!-- Accessible Hazard Level Badges (Never relying on color alone) -->
  {#if hazardLevel === 'nominal'}
    <span class={`inline-flex items-center gap-1 px-2 py-0.5 rounded-ares-sm text-[10px] font-mono font-bold uppercase border bg-ares-green/15 text-ares-green border-ares-green/40 ${extraClass}`}>
      <ShieldCheck size={11} class="shrink-0" />
      <span>NOMINAL: {label || 'SAFE TERRAIN'}</span>
    </span>
  {:else if hazardLevel === 'elevated'}
    <span class={`inline-flex items-center gap-1 px-2 py-0.5 rounded-ares-sm text-[10px] font-mono font-bold uppercase border bg-ares-amber/15 text-ares-amber border-ares-amber/40 ${extraClass}`}>
      <AlertTriangle size={11} class="shrink-0" />
      <span>CAUTION: {label || 'ELEVATED RISK'}</span>
    </span>
  {:else if hazardLevel === 'critical'}
    <span class={`inline-flex items-center gap-1 px-2 py-0.5 rounded-ares-sm text-[10px] font-mono font-bold uppercase border bg-ares-red/20 text-ares-red border-ares-red/50 ${extraClass}`}>
      <AlertOctagon size={11} class="shrink-0 animate-pulse" />
      <span>CRITICAL HAZARD: {label || 'NO-GO CORRIDOR'}</span>
    </span>
  {/if}

{:else}
  <!-- Standard Design System Badges -->
  <span class={`inline-flex items-center gap-1 px-2 py-0.5 rounded-ares-sm text-[10px] font-mono font-bold tracking-wide border ${variantStyles[variant]} ${extraClass}`}>
    {#if children}
      {@render children()}
    {:else}
      {label}
    {/if}
  </span>
{/if}

