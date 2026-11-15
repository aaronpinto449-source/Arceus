<script lang="ts">
  import type { Snippet } from 'svelte';

  export interface TableColumn<T = any> {
    key: string;
    header: string;
    align?: 'left' | 'center' | 'right';
    width?: string;
    mono?: boolean;
    render?: (row: T) => any;
  }

  interface Props {
    columns?: TableColumn[];
    data?: any[];
    dense?: boolean;
    striped?: boolean;
    children?: Snippet;
    class?: string;
  }

  let {
    columns = [],
    data = [],
    dense = false,
    striped = false,
    children,
    class: extraClass = ''
  }: Props = $props();
</script>

<div class={`w-full overflow-x-auto border border-ares-border rounded-ares-md bg-ares-navy ${extraClass}`}>
  <table class="w-full border-collapse text-left select-text">
    {#if columns.length > 0}
      <thead>
        <tr class="border-b border-ares-border bg-ares-deep/60">
          {#each columns as col}
            <th
              style={col.width ? `width: ${col.width}` : ''}
              class={`hud-label px-3 py-2 text-slate-400 font-mono text-[10px] uppercase tracking-wider
                ${col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'}
              `}
            >
              {col.header}
            </th>
          {/each}
        </tr>
      </thead>
      <tbody class="divide-y divide-ares-border/60 text-xs">
        {#each data as row, idx}
          <tr class={`transition-colors duration-100 hover:bg-ares-elevated/50 
            ${striped && idx % 2 === 1 ? 'bg-ares-deep/30' : ''}
          `}>
            {#each columns as col}
              <td
                class={`px-3 ${dense ? 'py-1.5' : 'py-2.5'} text-slate-200
                  ${col.mono ? 'font-mono' : 'font-sans'}
                  ${col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'}
                `}
              >
                {#if col.render}
                  {col.render(row)}
                {:else}
                  {row[col.key] ?? '—'}
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    {:else if children}
      {@render children()}
    {/if}
  </table>
</div>

