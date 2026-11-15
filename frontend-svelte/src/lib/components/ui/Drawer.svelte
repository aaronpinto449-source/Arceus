<script lang="ts">
  import type { Snippet } from 'svelte';
  import { X } from '@lucide/svelte';

  interface Props {
    open: boolean;
    title?: string;
    subtitle?: string;
    width?: string;
    onclose?: () => void;
    children?: Snippet;
    footer?: Snippet;
  }

  let {
    open = false,
    title = 'TELEMETRY DRAWER',
    subtitle,
    width = 'w-80 md:w-96',
    onclose,
    children,
    footer,
  }: Props = $props();
</script>

{#if open}
  <!-- Overlay on mobile / tablet -->
  <div
    role="presentation"
    onclick={onclose}
    class="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
  ></div>

  <!-- Drawer Container -->
  <aside
    class={`fixed lg:relative top-0 right-0 bottom-0 h-full ${width} bg-ares-navy border-l border-ares-border shadow-ares-panel z-50 flex flex-col justify-between overflow-hidden transition-all duration-200 select-none`}
  >
    <!-- Header -->
    <div class="px-4 py-3 border-b border-ares-border flex items-center justify-between bg-ares-deep/40">
      <div class="flex flex-col gap-0.5 overflow-hidden">
        <h3 class="font-title text-sm font-bold text-white uppercase tracking-wider truncate">
          {title}
        </h3>
        {#if subtitle}
          <span class="text-[10px] font-mono text-slate-400 truncate">{subtitle}</span>
        {/if}
      </div>

      <button
        onclick={onclose}
        class="p-1 rounded text-slate-400 hover:text-white hover:bg-ares-elevated border border-transparent hover:border-ares-border transition-colors"
        aria-label="Close drawer"
      >
        <X size={16} />
      </button>
    </div>

    <!-- Body -->
    <div class="p-4 flex-1 overflow-y-auto space-y-4 font-mono text-xs">
      {#if children}
        {@render children()}
      {/if}
    </div>

    <!-- Footer -->
    {#if footer}
      <div class="p-3 border-t border-ares-border bg-ares-deep/60">
        {@render footer()}
      </div>
    {/if}
  </aside>
{/if}

