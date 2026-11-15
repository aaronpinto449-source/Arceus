<script lang="ts">
  import type { Component } from 'svelte';

  export interface NavOption<T = string> {
    id: T;
    label: string;
    sublabel?: string;
    icon?: Component<{ size?: number; class?: string }>;
    badge?: string;
  }

  interface Props {
    items: NavOption[];
    selected: string;
    onselect: (id: string) => void;
    variant?: 'tabs' | 'pills' | 'sidebar';
    touchFriendly?: boolean;
    class?: string;
  }

  let {
    items = [],
    selected,
    onselect,
    variant = 'pills',
    touchFriendly = false,
    class: extraClass = ''
  }: Props = $props();
</script>

<nav class={`flex ${variant === 'sidebar' ? 'flex-col gap-1' : 'flex-row gap-1.5 overflow-x-auto'} ${extraClass}`}>
  {#each items as item}
    {@const isActive = selected === item.id}
    {@const IconComponent = item.icon}
    <button
      type="button"
      onclick={() => onselect(item.id)}
      class={`flex items-center gap-2 rounded-ares transition-all duration-150 select-none text-left
        ${touchFriendly ? 'min-h-[48px] px-4 py-2.5 text-xs md:text-sm' : 'px-3 py-1.5 text-xs'}
        ${variant === 'sidebar' 
          ? (isActive 
              ? 'bg-ares-elevated border-l-2 border-ares-cyan text-white font-bold' 
              : 'hover:bg-ares-navy text-slate-400 hover:text-slate-200 border-l-2 border-transparent')
          : (isActive
              ? 'bg-ares-cyan/15 border border-ares-cyan/40 text-ares-cyan font-bold shadow-ares-glow-cyan/20'
              : 'bg-ares-navy/80 hover:bg-ares-elevated border border-ares-border text-slate-300 hover:text-white')
        }
      `}
    >
      {#if IconComponent}
        <IconComponent size={touchFriendly ? 18 : 14} class={isActive ? 'text-ares-cyan' : 'text-slate-400'} />
      {/if}

      <div class="flex flex-col overflow-hidden">
        <span class="font-mono tracking-wide truncate">{item.label}</span>
        {#if item.sublabel}
          <span class="text-[10px] text-slate-500 font-mono truncate">{item.sublabel}</span>
        {/if}
      </div>

      {#if item.badge}
        <span class="ml-auto text-[10px] font-mono px-1.5 py-0.2 rounded bg-ares-deep/80 text-ares-cyan border border-ares-cyan/30">
          {item.badge}
        </span>
      {/if}
    </button>
  {/each}
</nav>

