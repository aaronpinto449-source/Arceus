
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'panel' | 'elevated' | 'tactical' | 'interactive';
    title?: string;
    subtitle?: string;
    reticles?: boolean;
    headerRight?: Snippet;
    footer?: Snippet;
    children?: Snippet;
    class?: string;
    onclick?: (e: MouseEvent) => void;
  }

  let {
    variant = 'panel',
    title,
    subtitle,
    reticles = false,
    headerRight,
    footer,
    children,
    class: extraClass = '',
    onclick,
  }: Props = $props();

  const variantClasses = {
    panel: 'bg-ares-navy border border-ares-border shadow-ares-panel',
    elevated: 'bg-ares-elevated border border-ares-border shadow-ares-panel',
    tactical: 'bg-ares-navy border border-ares-border shadow-ares-panel relative',
    interactive: 'bg-ares-navy hover:bg-ares-elevated border border-ares-border hover:border-ares-border-bright cursor-pointer transition-all duration-150',
  };
</script>

{#if onclick}
  <button
    type="button"
    class={`block w-full text-left rounded-ares-md overflow-hidden relative ${variantClasses[variant]} ${extraClass}`}
    onclick={onclick}
  >
    {#if reticles || variant === 'tactical'}
      <div class="pointer-events-none absolute top-1 left-1 w-1.5 h-1.5 border-t border-l border-ares-cyan/40"></div>
      <div class="pointer-events-none absolute top-1 right-1 w-1.5 h-1.5 border-t border-r border-ares-cyan/40"></div>
      <div class="pointer-events-none absolute bottom-1 left-1 w-1.5 h-1.5 border-b border-l border-ares-cyan/40"></div>
      <div class="pointer-events-none absolute bottom-1 right-1 w-1.5 h-1.5 border-b border-r border-ares-cyan/40"></div>
    {/if}

    {#if title || headerRight}
      <div class="px-4 py-3 border-b border-ares-border flex items-center justify-between gap-2 bg-ares-deep/30">
        <div class="flex flex-col gap-0.5 overflow-hidden">
          {#if title}
            <h3 class="font-title text-xs md:text-sm font-bold text-white tracking-wide truncate uppercase">{title}</h3>
          {/if}
          {#if subtitle}
            <span class="text-[10px] font-mono text-slate-400 truncate">{subtitle}</span>
          {/if}
        </div>
        {#if headerRight}
          <div class="shrink-0 flex items-center gap-2">
            {@render headerRight()}
          </div>
        {/if}
      </div>
    {/if}

    {#if children}
      <div class="p-4">
        {@render children()}
      </div>
    {/if}

    {#if footer}
      <div class="px-4 py-2.5 border-t border-ares-border bg-ares-deep/40 font-mono text-xs">
        {@render footer()}
      </div>
    {/if}
  </button>
{:else}
  <div class={`rounded-ares-md overflow-hidden relative ${variantClasses[variant]} ${extraClass}`}>
    {#if reticles || variant === 'tactical'}
      <div class="pointer-events-none absolute top-1 left-1 w-1.5 h-1.5 border-t border-l border-ares-cyan/40"></div>
      <div class="pointer-events-none absolute top-1 right-1 w-1.5 h-1.5 border-t border-r border-ares-cyan/40"></div>
      <div class="pointer-events-none absolute bottom-1 left-1 w-1.5 h-1.5 border-b border-l border-ares-cyan/40"></div>
      <div class="pointer-events-none absolute bottom-1 right-1 w-1.5 h-1.5 border-b border-r border-ares-cyan/40"></div>
    {/if}

    {#if title || headerRight}
      <div class="px-4 py-3 border-b border-ares-border flex items-center justify-between gap-2 bg-ares-deep/30">
        <div class="flex flex-col gap-0.5 overflow-hidden">
          {#if title}
            <h3 class="font-title text-xs md:text-sm font-bold text-white tracking-wide truncate uppercase">{title}</h3>
          {/if}
          {#if subtitle}
            <span class="text-[10px] font-mono text-slate-400 truncate">{subtitle}</span>
          {/if}
        </div>
        {#if headerRight}
          <div class="shrink-0 flex items-center gap-2">
            {@render headerRight()}
          </div>
        {/if}
      </div>
    {/if}

    {#if children}
      <div class="p-4">
        {@render children()}
      </div>
    {/if}

    {#if footer}
      <div class="px-4 py-2.5 border-t border-ares-border bg-ares-deep/40 font-mono text-xs">
        {@render footer()}
      </div>
    {/if}
  </div>
{/if}
