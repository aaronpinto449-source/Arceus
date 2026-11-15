
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { X } from '@lucide/svelte';

  interface Props {
    open: boolean;
    title: string;
    subtitle?: string;
    maxWidth?: string;
    onclose?: () => void;
    children?: Snippet;
    footer?: Snippet;
  }

  let {
    open = false,
    title,
    subtitle,
    maxWidth = 'max-w-xl',
    onclose,
    children,
    footer,
  }: Props = $props();

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && open && onclose) {
      onclose();
    }
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      onclose?.();
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <!-- Backdrop -->
  <div
    role="presentation"
    onclick={handleBackdropClick}
    class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-opacity animate-fade-in"
  >
    <!-- Modal Window -->
    <div
      role="dialog"
      aria-modal="true"
      aria-label={title}
      tabindex="-1"
      class={`w-full ${maxWidth} bg-ares-navy border border-ares-border rounded-ares-md shadow-ares-panel relative overflow-hidden flex flex-col`}
    >
      <!-- Aerospace Reticle Corners -->
      <div class="pointer-events-none absolute top-1.5 left-1.5 w-2 h-2 border-t border-l border-ares-cyan/50"></div>
      <div class="pointer-events-none absolute top-1.5 right-1.5 w-2 h-2 border-t border-r border-ares-cyan/50"></div>
      <div class="pointer-events-none absolute bottom-1.5 left-1.5 w-2 h-2 border-b border-l border-ares-cyan/50"></div>
      <div class="pointer-events-none absolute bottom-1.5 right-1.5 w-2 h-2 border-b border-r border-ares-cyan/50"></div>

      <!-- Header -->
      <div class="px-5 py-3.5 border-b border-ares-border flex items-center justify-between bg-ares-deep/40">
        <div class="flex flex-col gap-0.5">
          <h2 class="font-title text-base font-bold text-white tracking-wide uppercase">
            {title}
          </h2>
          {#if subtitle}
            <span class="text-[11px] font-mono text-slate-400">{subtitle}</span>
          {/if}
        </div>

        <button
          onclick={onclose}
          class="p-1 rounded text-slate-400 hover:text-white hover:bg-ares-elevated border border-transparent hover:border-ares-border transition-colors"
          aria-label="Close modal"
        >
          <X size={16} />
        </button>
      </div>

      <!-- Content -->
      <div class="p-5 overflow-y-auto max-h-[75vh] space-y-4 text-xs">
        {#if children}
          {@render children()}
        {/if}
      </div>

      <!-- Footer -->
      {#if footer}
        <div class="px-5 py-3 border-t border-ares-border bg-ares-deep/40 flex items-center justify-end gap-2.5">
          {@render footer()}
        </div>
      {/if}
    </div>
  </div>
{/if}
