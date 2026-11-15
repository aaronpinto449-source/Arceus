<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    text: string;
    position?: 'top' | 'bottom' | 'left' | 'right';
    children: Snippet;
  }

  let { text, position = 'top', children }: Props = $props();
  let visible = $state(false);

  const posClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-1.5',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-1.5',
    left: 'right-full top-1/2 -translate-y-1/2 mr-1.5',
    right: 'left-full top-1/2 -translate-y-1/2 ml-1.5',
  };
</script>

<div
role="group"
  class="relative inline-flex items-center"
  onmouseenter={() => visible = true}
  onmouseleave={() => visible = false}
  onfocusin={() => visible = true}
  onfocusout={() => visible = false}
>
  {@render children()}

  {#if visible}
    <div
      role="tooltip"
      class={`absolute z-50 pointer-events-none px-2.5 py-1 rounded-ares bg-ares-deep/95 border border-ares-border-bright text-slate-200 text-[11px] font-mono shadow-ares-panel whitespace-nowrap
        ${posClasses[position]}
      `}
    >
      {text}
    </div>
  {/if}
</div>

