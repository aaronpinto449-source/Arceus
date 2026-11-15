<script lang="ts">
  import { ShieldAlert } from "@lucide/svelte";
  import Badge from "../ui/Badge.svelte";
</script>

<footer
  class="border-t border-ares-border bg-ares-deep px-4 py-2 flex flex-col md:flex-row items-center justify-between gap-2 text-[11px] font-mono text-slate-400 select-none"
>
  <div
    class="flex items-center gap-2 text-slate-400 text-center md:text-left flex-wrap"
  >
    <ShieldAlert size={14} class="text-ares-amber shrink-0 hidden sm:inline" />
    <span>
      <strong class="text-slate-300">SCIENTIFIC TRANSPARENCY:</strong> MOLA colourized
      tiles are visual rendering products. Slopes and elevations derived from pixel
      colours are model-based.
    </span>
    <Badge provenance="measured" label="IAU 2000 COORD" />
  </div>

  <div class="flex items-center gap-3 shrink-0 text-slate-400">
    <span>NASA Space Apps 2026</span>
    <span class="text-slate-600">|</span>
    <span class="text-ares-cyan font-bold">TEAM ARCEUS</span>
    <span class="text-slate-600">|</span>
    <span class="text-slate-500">DS 1.0</span>
  </div>
</footer>
