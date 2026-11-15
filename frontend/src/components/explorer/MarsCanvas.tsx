import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Region, PointOfInterest, SelectedTarget } from '../../types';
import { ZoomIn, ZoomOut, RotateCcw, Crosshair, Compass } from 'lucide-react';

interface MarsCanvasProps {
  region: Region;
  imageUrl: string;
  pois: PointOfInterest[];
  selectedTarget: SelectedTarget;
  onSelectTarget: (target: SelectedTarget) => void;
}

export const MarsCanvas: React.FC<MarsCanvasProps> = ({
  region,
  imageUrl,
  pois,
  selectedTarget,
  onSelectTarget,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Pan & Zoom camera state
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Mouse hover HUD coordinates
  const [hoverCoords, setHoverCoords] = useState<{ lat: number; lon: number } | null>(null);
  const [imageLoaded, setImageLoaded] = useState<boolean>(false);
  const imgRef = useRef<HTMLImageElement | null>(null);

  const bounds = region.bounds;

  // Load MOLA image into memory
  useEffect(() => {
    setImageLoaded(false);
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = imageUrl;
    img.onload = () => {
      imgRef.current = img;
      setImageLoaded(true);
      // Reset view on region change
      setZoom(1.0);
      setPan({ x: 0, y: 0 });
    };
  }, [imageUrl, region.id]);

  // Coordinate conversion helpers
  // Mars Lat/Lon to Image Normalized (0 to 1)
  const coordsToNormalized = useCallback(
    (lat: number, lon: number) => {
      const xNorm = (lon - bounds.lon_min) / (bounds.lon_max - bounds.lon_min);
      const yNorm = (bounds.lat_max - lat) / (bounds.lat_max - bounds.lat_min);
      return { xNorm, yNorm };
    },
    [bounds]
  );

  // Canvas Screen Pixel to Mars Lat/Lon
  const screenToCoords = useCallback(
    (screenX: number, screenY: number, width: number, height: number) => {
      // Base square map dimensions inside canvas
      const mapSize = Math.min(width, height) * zoom;
      const offsetX = (width - mapSize) / 2 + pan.x;
      const offsetY = (height - mapSize) / 2 + pan.y;

      const normX = (screenX - offsetX) / mapSize;
      const normY = (screenY - offsetY) / mapSize;

      const lon = bounds.lon_min + normX * (bounds.lon_max - bounds.lon_min);
      const lat = bounds.lat_max - normY * (bounds.lat_max - bounds.lat_min);

      return {
        lat: Math.max(bounds.lat_min, Math.min(bounds.lat_max, lat)),
        lon: Math.max(bounds.lon_min, Math.min(bounds.lon_max, lon)),
        inBounds: normX >= 0 && normX <= 1 && normY >= 0 && normY <= 1,
      };
    },
    [bounds, zoom, pan]
  );

  // Render Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Handle high DPI
    const dpr = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    if (canvas.width !== width * dpr || canvas.height !== height * dpr) {
      canvas.width = width * dpr;
      canvas.height = height * dpr;
    }

    ctx.save();
    ctx.scale(dpr, dpr);

    // Deep space background
    ctx.fillStyle = '#06080d';
    ctx.fillRect(0, 0, width, height);

    // Map drawing dimensions
    const mapSize = Math.min(width, height) * zoom;
    const offsetX = (width - mapSize) / 2 + pan.x;
    const offsetY = (height - mapSize) / 2 + pan.y;

    if (imageLoaded && imgRef.current) {
      // 1. Draw MOLA Topography Tile
      ctx.drawImage(imgRef.current, offsetX, offsetY, mapSize, mapSize);

      // Subtle topographic border
      ctx.strokeStyle = '#1f2b3e';
      ctx.lineWidth = 1;
      ctx.strokeRect(offsetX, offsetY, mapSize, mapSize);

      // 2. Graticules / Latitude-Longitude Grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.07)';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);

      const step = 5; // 5 degree grid
      for (let lon = bounds.lon_min + step; lon < bounds.lon_max; lon += step) {
        const { xNorm } = coordsToNormalized(bounds.lat_min, lon);
        const gx = offsetX + xNorm * mapSize;
        ctx.beginPath();
        ctx.moveTo(gx, offsetY);
        ctx.lineTo(gx, offsetY + mapSize);
        ctx.stroke();
      }

      for (let lat = bounds.lat_min + step; lat < bounds.lat_max; lat += step) {
        const { yNorm } = coordsToNormalized(lat, bounds.lon_min);
        const gy = offsetY + yNorm * mapSize;
        ctx.beginPath();
        ctx.moveTo(offsetX, gy);
        ctx.lineTo(offsetX + mapSize, gy);
        ctx.stroke();
      }
      ctx.setLineDash([]);

      // 3. Render Verified Scientific POIs
      pois.forEach((poi) => {
        const { xNorm, yNorm } = coordsToNormalized(poi.lat, poi.lon);
        const px = offsetX + xNorm * mapSize;
        const py = offsetY + yNorm * mapSize;

        const isSelected = selectedTarget.name === poi.name;

        // Outer pulse circle
        ctx.beginPath();
        ctx.arc(px, py, isSelected ? 12 : 7, 0, Math.PI * 2);
        ctx.fillStyle = isSelected ? 'rgba(84, 214, 154, 0.25)' : 'rgba(84, 214, 154, 0.15)';
        ctx.fill();

        // Inner solid core
        ctx.beginPath();
        ctx.arc(px, py, isSelected ? 5 : 3.5, 0, Math.PI * 2);
        ctx.fillStyle = '#54d69a';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Label
        ctx.font = '600 11px Inter, sans-serif';
        ctx.fillStyle = isSelected ? '#54d69a' : '#ffffff';
        ctx.shadowColor = 'rgba(0,0,0,0.8)';
        ctx.shadowBlur = 4;
        ctx.fillText(poi.name, px + 10, py + 4);
        ctx.shadowBlur = 0;
      });

      // 4. Render Active Expedition Targeting Reticle
      if (selectedTarget) {
        const { xNorm, yNorm } = coordsToNormalized(selectedTarget.lat, selectedTarget.lon);
        const rx = offsetX + xNorm * mapSize;
        const ry = offsetY + yNorm * mapSize;

        // Reticle Diamond
        ctx.strokeStyle = '#e16d49';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(rx, ry - 14);
        ctx.lineTo(rx + 14, ry);
        ctx.lineTo(rx, ry + 14);
        ctx.lineTo(rx - 14, ry);
        ctx.closePath();
        ctx.stroke();

        // Inner crosshair
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(rx - 8, ry);
        ctx.lineTo(rx + 8, ry);
        ctx.moveTo(rx, ry - 8);
        ctx.lineTo(rx, ry + 8);
        ctx.stroke();

        // Coordinate tag
        ctx.font = '500 10px JetBrains Mono, monospace';
        ctx.fillStyle = '#e16d49';
        ctx.fillText(
          `${selectedTarget.lat.toFixed(2)}°N, ${selectedTarget.lon.toFixed(2)}°E`,
          rx + 18,
          ry - 6
        );
      }
    } else {
      // Loading State HUD
      ctx.font = '500 13px JetBrains Mono, monospace';
      ctx.fillStyle = '#00f0ff';
      ctx.textAlign = 'center';
      ctx.fillText('INITIALIZING MOLA SATELLITE CARTOGRAPHY STREAM...', width / 2, height / 2);
      ctx.textAlign = 'start';
    }

    ctx.restore();
  }, [
    imageLoaded,
    zoom,
    pan,
    pois,
    selectedTarget,
    bounds,
    coordsToNormalized,
  ]);

  // Mouse & Touch Event Handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.clientX - rect.left;
    const clientY = e.clientY - rect.top;

    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }

    // Update hover coordinates
    const coords = screenToCoords(clientX, clientY, canvas.clientWidth, canvas.clientHeight);
    if (coords.inBounds) {
      setHoverCoords({ lat: coords.lat, lon: coords.lon });
    } else {
      setHoverCoords(null);
    }
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    // Detect single click vs drag
    if (isDragging) {
      const moved = Math.hypot(e.clientX - (dragStart.x + pan.x), e.clientY - (dragStart.y + pan.y));
      if (moved < 5) {
        // Registered as a click!
        handleClick(e);
      }
    }
    setIsDragging(false);
  };

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    const coords = screenToCoords(clickX, clickY, canvas.clientWidth, canvas.clientHeight);
    if (!coords.inBounds) return;

    // Check if clicked close to a known POI
    const mapSize = Math.min(canvas.clientWidth, canvas.clientHeight) * zoom;
    const offsetX = (canvas.clientWidth - mapSize) / 2 + pan.x;
    const offsetY = (canvas.clientHeight - mapSize) / 2 + pan.y;

    const clickedPoi = pois.find((poi) => {
      const { xNorm, yNorm } = coordsToNormalized(poi.lat, poi.lon);
      const px = offsetX + xNorm * mapSize;
      const py = offsetY + yNorm * mapSize;
      return Math.hypot(clickX - px, clickY - py) < 18;
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
        lat: Number(coords.lat.toFixed(4)),
        lon: Number(coords.lon.toFixed(4)),
        name: `Waypoint (${coords.lat.toFixed(2)}°N, ${coords.lon.toFixed(2)}°E)`,
      });
    }
  };

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
    setZoom((prev) => Math.max(0.8, Math.min(10.0, prev * zoomFactor)));
  };

  // Zoom controls
  const handleZoomIn = () => setZoom((z) => Math.min(10.0, z * 1.3));
  const handleZoomOut = () => setZoom((z) => Math.max(0.8, z / 1.3));
  const handleReset = () => {
    setZoom(1.0);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-[640px] bg-space-950 rounded-lg overflow-hidden border border-space-border select-none"
    >
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-crosshair"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={() => {
          setIsDragging(false);
          setHoverCoords(null);
        }}
        onWheel={handleWheel}
      />

      {/* Aerospace Corner HUD Brackets */}
      <div className="hud-reticle-corner top-2 left-2 border-t-2 border-l-2" />
      <div className="hud-reticle-corner top-2 right-2 border-t-2 border-r-2" />
      <div className="hud-reticle-corner bottom-2 left-2 border-b-2 border-l-2" />
      <div className="hud-reticle-corner bottom-2 right-2 border-b-2 border-r-2" />

      {/* Top Left: Regional HUD Bar */}
      <div className="absolute top-3 left-4 bg-space-900/80 backdrop-blur-md px-3 py-1.5 rounded border border-space-border text-xs flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-ares-cyan font-mono font-semibold">
          <Compass className="w-3.5 h-3.5 animate-spin" style={{ animationDuration: '20s' }} />
          <span>{region.name.toUpperCase()} GRID</span>
        </div>
        <span className="text-slate-500">|</span>
        <span className="text-slate-400 font-mono text-[11px]">
          OPTICAL MAG: <strong className="text-white">{zoom.toFixed(2)}x</strong>
        </span>
      </div>

      {/* Top Right: Live Cursor Crosshair Coordinates */}
      <div className="absolute top-3 right-4 bg-space-900/80 backdrop-blur-md px-3 py-1.5 rounded border border-space-border text-xs flex items-center gap-2">
        <Crosshair className="w-3.5 h-3.5 text-ares-green" />
        <span className="text-slate-400 font-mono text-[11px]">
          CURSOR:
          {hoverCoords ? (
            <span className="text-ares-green font-bold ml-1.5">
              {hoverCoords.lat.toFixed(3)}°N, {hoverCoords.lon.toFixed(3)}°E
            </span>
          ) : (
            <span className="text-slate-500 ml-1.5">TRACKING...</span>
          )}
        </span>
      </div>

      {/* Bottom Right: Tactical Map Controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-1.5 bg-space-900/80 backdrop-blur-md p-1.5 rounded border border-space-border">
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          className="p-1.5 hover:bg-space-750 text-slate-300 hover:text-ares-cyan rounded transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          className="p-1.5 hover:bg-space-750 text-slate-300 hover:text-ares-cyan rounded transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={handleReset}
          title="Reset View"
          className="p-1.5 hover:bg-space-750 text-slate-300 hover:text-ares-amber rounded transition-colors border-t border-space-border/60 pt-1.5"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Bottom Left: Spatial Scale Indicator */}
      <div className="absolute bottom-4 left-4 bg-space-900/80 backdrop-blur-md px-3 py-1.5 rounded border border-space-border text-[11px] font-mono text-slate-300">
        <div className="flex items-center gap-2">
          <span>SCALE:</span>
          <div className="h-1.5 w-16 bg-ares-cyan/40 border border-ares-cyan" />
          <span className="text-ares-cyan">~{(300 / zoom).toFixed(0)} KM</span>
        </div>
      </div>
    </div>
  );
};

