<script lang="ts">
  import { onMount } from "svelte";
  import type { Region, PointOfInterest, SelectedTarget } from "../../types";
  import {
    ZoomIn,
    ZoomOut,
    RotateCcw,
    Crosshair,
    Compass,
    Maximize2,
  } from "@lucide/svelte";

  interface Props {
    region: Region;
    imageUrl: string;
    pois: PointOfInterest[];
    selectedTarget: SelectedTarget | null;
    onSelectTarget: (target: SelectedTarget) => void;
  }

  let { region, imageUrl, pois, selectedTarget, onSelectTarget }: Props =
    $props();

  let canvasEl = $state<HTMLCanvasElement | null>(null);
  let containerEl = $state<HTMLDivElement | null>(null);

  let zoom = $state(1.0);
  let panX = $state(0);
  let panY = $state(0);
  let isDragging = $state(false);
  let dragStartX = $state(0);
  let dragStartY = $state(0);
  let hoverCoords = $state<{ lat: number; lon: number } | null>(null);
  let imageLoaded = $state(false);
  let imageFailed = $state(false);

  let img: HTMLImageElement | null = null;

  // Watch for image url or region changes
  $effect(() => {
    const url = imageUrl;
    const regId = region.id;
    imageLoaded = false;
    imageFailed = false;

    const newImg = new Image();
    newImg.crossOrigin = "anonymous";
    newImg.src = url;

    newImg.onload = () => {
      img = newImg;
      imageLoaded = true;
      imageFailed = false;
      zoom = 1.0;
      panX = 0;
      panY = 0;
      render();
    };

    newImg.onerror = () => {
      imageFailed = true;
      imageLoaded = false;
      render();
    };
  });

  function screenToCoords(
    screenX: number,
    screenY: number,
    width: number,
    height: number,
  ) {
    const bounds = region.bounds;
    const mapSize = Math.min(width, height) * zoom;
    const offsetX = (width - mapSize) / 2 + panX;
    const offsetY = (height - mapSize) / 2 + panY;

    const normX = (screenX - offsetX) / mapSize;
    const normY = (screenY - offsetY) / mapSize;

    const lon = bounds.lon_min + normX * (bounds.lon_max - bounds.lon_min);
    const lat = bounds.lat_max - normY * (bounds.lat_max - bounds.lat_min);

    return {
      lat: Math.max(bounds.lat_min, Math.min(bounds.lat_max, lat)),
      lon: Math.max(bounds.lon_min, Math.min(bounds.lon_max, lon)),
      inBounds: normX >= 0 && normX <= 1 && normY >= 0 && normY <= 1,
    };
  }

  function coordsToScreen(
    lat: number,
    lon: number,
    width: number,
    height: number,
  ) {
    const bounds = region.bounds;
    const mapSize = Math.min(width, height) * zoom;
    const offsetX = (width - mapSize) / 2 + panX;
    const offsetY = (height - mapSize) / 2 + panY;

    const normX = (lon - bounds.lon_min) / (bounds.lon_max - bounds.lon_min);
    const normY = (bounds.lat_max - lat) / (bounds.lat_max - bounds.lat_min);

    return {
      x: offsetX + normX * mapSize,
      y: offsetY + normY * mapSize,
    };
  }

  function render() {
    if (!canvasEl) return;
    const ctx = canvasEl.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const width = canvasEl.clientWidth || 600;
    const height = canvasEl.clientHeight || 500;

    if (canvasEl.width !== width * dpr || canvasEl.height !== height * dpr) {
      canvasEl.width = width * dpr;
      canvasEl.height = height * dpr;
    }

    ctx.save();
    ctx.scale(dpr, dpr);

    // Deep space backdrop
    ctx.fillStyle = "#080D16";
    ctx.fillRect(0, 0, width, height);

    const bounds = region.bounds;
    const mapSize = Math.min(width, height) * zoom;
    const offsetX = (width - mapSize) / 2 + panX;
    const offsetY = (height - mapSize) / 2 + panY;

    // Render Image or fallback grid
    if (imageLoaded && img) {
      ctx.imageSmoothingEnabled = zoom < 2.5;
      ctx.drawImage(img, offsetX, offsetY, mapSize, mapSize);
    } else {
      // Standalone procedural MOLA elevation hypsometric visualization
      const grad = ctx.createLinearGradient(
        offsetX,
        offsetY,
        offsetX + mapSize,
        offsetY + mapSize,
      );
      grad.addColorStop(0, "#0a2540");
      grad.addColorStop(0.25, "#1e40af");
      grad.addColorStop(0.45, "#047857");
      grad.addColorStop(0.65, "#ca8a04");
      grad.addColorStop(0.85, "#dc2626");
      grad.addColorStop(1, "#ffffff");

      ctx.fillStyle = grad;
      ctx.fillRect(offsetX, offsetY, mapSize, mapSize);

      ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
      ctx.lineWidth = 1;
      ctx.strokeRect(offsetX, offsetY, mapSize, mapSize);

      ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
      ctx.font = 'bold 12px "Space Grotesk", sans-serif';
      ctx.textAlign = "center";
      ctx.fillText(
        `${region.name.toUpperCase()} (MOLA MEG256 TILE)`,
        offsetX + mapSize / 2,
        offsetY + mapSize / 2 - 10,
      );
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillStyle = "rgba(54, 197, 232, 0.9)";
      ctx.fillText(
        `BOUNDS: [${bounds.lat_min}°N to ${bounds.lat_max}°N] × [${bounds.lon_min}°E to ${bounds.lon_max}°E]`,
        offsetX + mapSize / 2,
        offsetY + mapSize / 2 + 10,
      );
    }

    // Outer border around map
    ctx.strokeStyle = "#36C5E8";
    ctx.lineWidth = 1.5;
    ctx.strokeRect(offsetX, offsetY, mapSize, mapSize);

    // Graticules (Lat / Lon coordinate grid lines)
    ctx.strokeStyle = "rgba(54, 197, 232, 0.2)";
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 4]);

    const step = 5; // every 5 degrees
    ctx.font = '10px "JetBrains Mono", monospace';
    ctx.fillStyle = "rgba(165, 232, 245, 0.75)"; // Ice blue

    for (let lat = bounds.lat_min; lat <= bounds.lat_max; lat += step) {
      const p1 = coordsToScreen(lat, bounds.lon_min, width, height);
      const p2 = coordsToScreen(lat, bounds.lon_max, width, height);
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();

      if (p1.x > 0 && p1.x < width) {
        ctx.textAlign = "right";
        ctx.fillText(`${lat.toFixed(0)}°N`, p1.x - 4, p1.y + 3);
      }
    }

    for (let lon = bounds.lon_min; lon <= bounds.lon_max; lon += step) {
      const p1 = coordsToScreen(bounds.lat_max, lon, width, height);
      const p2 = coordsToScreen(bounds.lat_min, lon, width, height);
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();

      if (p2.y > 0 && p2.y < height) {
        ctx.textAlign = "center";
        ctx.fillText(`${lon.toFixed(0)}°E`, p2.x, p2.y + 12);
      }
    }
    ctx.setLineDash([]);

    // Draw POI markers
    pois.forEach((poi) => {
      const p = coordsToScreen(poi.lat, poi.lon, width, height);
      if (p.x < 0 || p.x > width || p.y < 0 || p.y > height) return;

      const isSelected =
        selectedTarget?.lat === poi.lat && selectedTarget?.lon === poi.lon;

      // Outer reticle ring
      ctx.strokeStyle = isSelected ? "#36C5E8" : "#54C99A";
      ctx.lineWidth = isSelected ? 2.5 : 1.5;
      ctx.beginPath();
      ctx.arc(p.x, p.y, isSelected ? 9 : 6, 0, Math.PI * 2);
      ctx.stroke();

      // Center dot
      ctx.fillStyle = isSelected ? "#36C5E8" : "#54C99A";
      ctx.beginPath();
      ctx.arc(p.x, p.y, 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Label with backing pill
      ctx.font = '10px "JetBrains Mono", monospace';
      const textWidth = ctx.measureText(poi.name).width;

      ctx.fillStyle = "rgba(8, 13, 22, 0.75)";
      ctx.fillRect(p.x + 9, p.y - 7, textWidth + 6, 14);
      ctx.strokeStyle = isSelected ? "#36C5E8" : "rgba(30, 45, 66, 0.8)";
      ctx.lineWidth = 1;
      ctx.strokeRect(p.x + 9, p.y - 7, textWidth + 6, 14);

      ctx.fillStyle = isSelected ? "#36C5E8" : "#ffffff";
      ctx.textAlign = "left";
      ctx.fillText(poi.name, p.x + 12, p.y + 3);
    });

    // Draw custom selected target if not a POI
    if (selectedTarget) {
      const isPoi = pois.some(
        (poi) =>
          poi.lat === selectedTarget.lat && poi.lon === selectedTarget.lon,
      );
      if (!isPoi) {
        const p = coordsToScreen(
          selectedTarget.lat,
          selectedTarget.lon,
          width,
          height,
        );
        if (p.x >= 0 && p.x <= width && p.y >= 0 && p.y <= height) {
          ctx.strokeStyle = "#F2A93B"; // Alert amber
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(p.x, p.y, 8, 0, Math.PI * 2);
          ctx.stroke();

          // Reticle crosshair
          ctx.beginPath();
          ctx.moveTo(p.x - 12, p.y);
          ctx.lineTo(p.x + 12, p.y);
          ctx.moveTo(p.x, p.y - 12);
          ctx.lineTo(p.x, p.y + 12);
          ctx.stroke();

          ctx.font = '10px "JetBrains Mono", monospace';
          ctx.fillStyle = "#F2A93B";
          ctx.textAlign = "left";
          ctx.fillText(selectedTarget.name, p.x + 14, p.y + 4);
        }
      }
    }

    ctx.restore();
  }

  $effect(() => {
    zoom;
    panX;
    panY;
    selectedTarget;
    pois;
    region;
    render();
  });

  onMount(() => {
    render();
    const handleResize = () => render();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  });

  function handleMouseDown(e: MouseEvent) {
    isDragging = true;
    dragStartX = e.clientX - panX;
    dragStartY = e.clientY - panY;
  }

  function handleMouseMove(e: MouseEvent) {
    if (!canvasEl) return;
    const rect = canvasEl.getBoundingClientRect();
    const screenX = e.clientX - rect.left;
    const screenY = e.clientY - rect.top;

    if (isDragging) {
      panX = e.clientX - dragStartX;
      panY = e.clientY - dragStartY;
      render();
    }

    const coords = screenToCoords(
      screenX,
      screenY,
      canvasEl.clientWidth,
      canvasEl.clientHeight,
    );
    if (coords.inBounds) {
      hoverCoords = { lat: coords.lat, lon: coords.lon };
    } else {
      hoverCoords = null;
    }
  }

  function handleMouseUp() {
    isDragging = false;
  }

  function handleClick(e: MouseEvent) {
    if (!canvasEl) return;
    const rect = canvasEl.getBoundingClientRect();
    const screenX = e.clientX - rect.left;
    const screenY = e.clientY - rect.top;

    const coords = screenToCoords(
      screenX,
      screenY,
      canvasEl.clientWidth,
      canvasEl.clientHeight,
    );
    if (coords.inBounds) {
      const clickThreshold = 14; // px
      const clickedPoi = pois.find((poi) => {
        const p = coordsToScreen(
          poi.lat,
          poi.lon,
          canvasEl!.clientWidth,
          canvasEl!.clientHeight,
        );
        const dist = Math.hypot(p.x - screenX, p.y - screenY);
        return dist <= clickThreshold;
      });

      if (clickedPoi) {
        onSelectTarget({
          lat: clickedPoi.lat,
          lon: clickedPoi.lon,
          name: clickedPoi.name,
          type: clickedPoi.type,
          source: clickedPoi.source_reference,
        });
      } else {
        onSelectTarget({
          lat: Math.round(coords.lat * 1000) / 1000,
          lon: Math.round(coords.lon * 1000) / 1000,
          name: `Target (${coords.lat.toFixed(2)}°N, ${coords.lon.toFixed(2)}°E)`,
        });
      }
    }
  }

  function handleWheel(e: WheelEvent) {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
    zoom = Math.max(0.7, Math.min(6.0, zoom * zoomFactor));
    render();
  }

  // Tablet Touch Controls
  let touchStartDist = 0;
  function handleTouchStart(e: TouchEvent) {
    if (e.touches.length === 1) {
      isDragging = true;
      dragStartX = e.touches[0].clientX - panX;
      dragStartY = e.touches[0].clientY - panY;
    } else if (e.touches.length === 2) {
      isDragging = false;
      touchStartDist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY,
      );
    }
  }

  function handleTouchMove(e: TouchEvent) {
    if (e.touches.length === 1 && isDragging) {
      panX = e.touches[0].clientX - dragStartX;
      panY = e.touches[0].clientY - dragStartY;
      render();
    } else if (e.touches.length === 2) {
      const currentDist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY,
      );
      if (touchStartDist > 0) {
        const factor = currentDist / touchStartDist;
        zoom = Math.max(0.7, Math.min(6.0, zoom * factor));
        touchStartDist = currentDist;
        render();
      }
    }
  }

  function handleTouchEnd() {
    isDragging = false;
  }
</script>

<div
  class="relative w-full h-full min-h-[460px] md:min-h-[560px] bg-ares-deep rounded-ares-md overflow-hidden border border-ares-border"
  bind:this={containerEl}
>
  <!-- Canvas Surface -->
  <canvas
    bind:this={canvasEl}
    onmousedown={handleMouseDown}
    onmousemove={handleMouseMove}
    onmouseup={handleMouseUp}
    onclick={handleClick}
    onwheel={handleWheel}
    ontouchstart={handleTouchStart}
    ontouchmove={handleTouchMove}
    ontouchend={handleTouchEnd}
    class="w-full h-full cursor-crosshair block"
  ></canvas>

  <!-- Reticle Corners Overlay -->
  <div
    class="pointer-events-none absolute top-2 left-2 w-2.5 h-2.5 border-t border-l border-ares-cyan/50"
  ></div>
  <div
    class="pointer-events-none absolute top-2 right-2 w-2.5 h-2.5 border-t border-r border-ares-cyan/50"
  ></div>
  <div
    class="pointer-events-none absolute bottom-2 left-2 w-2.5 h-2.5 border-b border-l border-ares-cyan/50"
  ></div>
  <div
    class="pointer-events-none absolute bottom-2 right-2 w-2.5 h-2.5 border-b border-r border-ares-cyan/50"
  ></div>

  <!-- Zoom & Control Toolbar Overlay -->
  <div
    class="absolute top-3 right-3 flex flex-col gap-1.5 bg-ares-navy/90 p-1.5 rounded-ares border border-ares-border shadow-ares-panel z-10"
  >
    <button
      onclick={() => {
        zoom = Math.min(6.0, zoom * 1.25);
        render();
      }}
      class="p-2.5 text-slate-300 hover:text-ares-cyan hover:bg-ares-elevated rounded-ares transition-colors"
      title="Zoom In"
      aria-label="Zoom In"
    >
      <ZoomIn size={16} />
    </button>
    <button
      onclick={() => {
        zoom = Math.max(0.7, zoom / 1.25);
        render();
      }}
      class="p-2.5 text-slate-300 hover:text-ares-cyan hover:bg-ares-elevated rounded-ares transition-colors"
      title="Zoom Out"
      aria-label="Zoom Out"
    >
      <ZoomOut size={16} />
    </button>
    <button
      onclick={() => {
        zoom = 1.0;
        panX = 0;
        panY = 0;
        render();
      }}
      class="p-2.5 text-slate-300 hover:text-ares-cyan hover:bg-ares-elevated rounded-ares transition-colors"
      title="Reset View"
      aria-label="Reset View"
    >
      <RotateCcw size={16} />
    </button>
  </div>

  <!-- Real-Time Cursor HUD Overlay -->
  <div
    class="absolute bottom-3 left-3 bg-ares-navy/90 px-3 py-1.5 rounded-ares border border-ares-border font-mono text-[11px] text-slate-300 flex items-center gap-3 pointer-events-none z-10 shadow-ares-panel"
  >
    <div class="flex items-center gap-1.5 text-ares-cyan">
      <Crosshair size={12} class="animate-pulse" />
      <span class="font-bold">RETICLE:</span>
    </div>
    {#if hoverCoords}
      <span class="font-bold text-white">
        {hoverCoords.lat.toFixed(3)}°N, {hoverCoords.lon.toFixed(3)}°E
      </span>
    {:else}
      <span class="text-slate-500 italic">Off-grid</span>
    {/if}
    <span class="text-slate-600">|</span>
    <span class="text-slate-400">ZOOM: {zoom.toFixed(1)}x</span>
  </div>
</div>
