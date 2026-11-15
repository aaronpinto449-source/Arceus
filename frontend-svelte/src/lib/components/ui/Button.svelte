<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'primary' | 'secondary' | 'tactical' | 'warning' | 'hazard' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    touchTarget?: boolean;
    disabled?: boolean;
    loading?: boolean;
    fullWidth?: boolean;
    type?: 'button' | 'submit' | 'reset';
    onclick?: (e: MouseEvent) => void;
    children?: Snippet;
    class?: string;
    title?: string;
    ariaLabel?: string;
  }

  let {
    variant = 'secondary',
    size = 'md',
    touchTarget = false,
    disabled = false,
    loading = false,
    fullWidth = false,
    type = 'button',
    onclick,
    children,
    class: extraClass = '',
    title,
    ariaLabel,
  }: Props = $props();

  const variantClasses = {
    primary: 'bg-ares-cyan text-ares-deep font-bold hover:bg-ares-ice border border-ares-cyan active:bg-cyan-400 shadow-ares-glow-cyan/50',
    secondary: 'bg-ares-navy hover:bg-ares-elevated text-slate-200 border border-ares-border hover:border-ares-border-bright active:bg-space-700',
    tactical: 'bg-ares-cyan/10 hover:bg-ares-cyan/20 text-ares-cyan border border-ares-cyan/40 hover:border-ares-cyan active:bg-ares-cyan/25',
    warning: 'bg-ares-amber/15 hover:bg-ares-amber/25 text-ares-amber border border-ares-amber/50 active:bg-ares-amber/30',
    hazard: 'bg-ares-red/15 hover:bg-ares-red/25 text-ares-red border border-ares-red/50 active:bg-ares-red/30',
    ghost: 'bg-transparent hover:bg-ares-navy/60 text-slate-400 hover:text-white border border-transparent',
  };

  const sizeClasses = {
    sm: 'text-[11px] px-2.5 py-1 gap-1.5',
    md: 'text-xs px-3.5 py-1.5 gap-2',
    lg: 'text-xs md:text-sm px-4 py-2.5 gap-2.5 min-h-[44px]',
  };
</script>

<button
  {type}
  {disabled}
  {onclick}
  {title}
  aria-label={ariaLabel}
  class={`inline-flex items-center justify-center font-mono rounded-ares transition-all duration-150 select-none outline-none focus-visible:ring-1 focus-visible:ring-ares-cyan disabled:opacity-50 disabled:cursor-not-allowed
    ${variantClasses[variant]}
    ${sizeClasses[size]}
    ${touchTarget ? 'min-h-[48px] min-w-[48px] px-4' : ''}
    ${fullWidth ? 'w-full' : ''}
    ${extraClass}
  `}
>
  {#if loading}
    <div class="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin shrink-0"></div>
  {/if}
  {#if children}
    {@render children()}
  {/if}
</button>

