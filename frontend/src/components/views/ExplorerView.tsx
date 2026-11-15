import React, { useState, useEffect } from 'react';
import { Region, PointOfInterest, SelectedTarget, GroundResolution } from '../../types';
import { MarsCanvas } from '../explorer/MarsCanvas';
import { api } from '../../services/api';
import { MapPin, Info, Crosshair, ArrowRight, ShieldCheck } from 'lucide-react';

interface ExplorerViewProps {
  region: Region;
  pois: PointOfInterest[];
  selectedTarget: SelectedTarget;
  onSelectTarget: (target: SelectedTarget) => void;
}

export const ExplorerView: React.FC<ExplorerViewProps> = ({
  region,
  pois,
  selectedTarget,
  onSelectTarget,
}) => {
  const [resolution, setResolution] = useState<GroundResolution | null>(null);
  const [manualLat, setManualLat] = useState<number>(selectedTarget.lat);
  const [manualLon, setManualLon] = useState<number>(selectedTarget.lon);

  useEffect(() => {
    setManualLat(selectedTarget.lat);
    setManualLon(selectedTarget.lon);

    // Fetch live local resolution for the selected latitude
    api.getSpatialResolution(selectedTarget.lat).then(setResolution).catch(console.error);
  }, [selectedTarget.lat, selectedTarget.lon]);

  const handleManualPin = (e: React.FormEvent) => {
    e.preventDefault();
    onSelectTarget({
      lat: Number(manualLat.toFixed(4)),
      lon: Number(manualLon.toFixed(4)),
      name: `Custom Waypoint (${manualLat.toFixed(2)}°N, ${manualLon.toFixed(2)}°E)`,
    });
  };

  const mapUrl = api.getRegionMapUrl(region.id);

  return (
    <div className="space-y-6">
      {/* Scientific Transparency Alert */}
      <div className="p-4 rounded-lg bg-space-900 border-l-4 border-ares-amber border-y border-r border-space-border text-xs text-slate-300 leading-relaxed shadow-lg">
        <div className="flex items-center gap-2 mb-1 text-ares-amber font-bold font-mono">
          <Info className="w-4 h-4" />
          <span>MOLA TOPOGRAPHIC CARTOGRAPHY CONSOLE</span>
        </div>
        <div>
          This interactive canvas renders NASA&apos;s <strong>Mars Global Surveyor (MGS) MOLA MEG256</strong> dataset (256 pixels/degree). 
          Latitude ground scale is uniform (~231.2 m/px), while physical longitude spacing contracts with the cosine of latitude toward higher elevations. 
          This map provides visual regional elevation cues; numerical rover traversal models are derived algorithmically.
        </div>
      </div>

      {/* Main Grid: Interactive Canvas + Telemetry Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: High-Tech Interactive Canvas */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-mono tracking-wider text-slate-300 font-bold flex items-center gap-2">
              <Crosshair className="w-4 h-4 text-ares-cyan" />
              SURFACE CARTOGRAPHY — {region.name.toUpperCase()}
            </h2>
            <span className="text-[11px] font-mono text-slate-400">
              FRAME: {region.bounds.lat_convention} / {region.bounds.lon_convention}
            </span>
          </div>

          <MarsCanvas
            region={region}
            imageUrl={mapUrl}
            pois={pois}
            selectedTarget={selectedTarget}
            onSelectTarget={onSelectTarget}
          />

          <div className="text-[11px] font-mono text-slate-400 flex items-center justify-between px-1">
            <span>Projection: {region.bounds.projection}</span>
            <span>Prime Meridian: {region.bounds.reference_meridian}</span>
            <span>Resolution: ~231 m/pixel (Equatorial)</span>
          </div>
        </div>

        {/* Right Col: Target Telemetry & Precision Coordinate Inputs */}
        <div className="space-y-4">
          {/* Active Target Details Card */}
          <div className="aerospace-panel p-5">
            <div className="hud-label text-ares-green flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              ACTIVE EXPEDITION TARGET
            </div>
            <div className="text-xl hud-value mt-2 text-white">{selectedTarget.name}</div>

            <div className="mt-3 p-3 rounded bg-space-950 border border-space-border font-mono text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">LATITUDE:</span>
                <span className="text-ares-cyan font-bold">{selectedTarget.lat.toFixed(4)}° N</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">LONGITUDE:</span>
                <span className="text-ares-coral font-bold">{selectedTarget.lon.toFixed(4)}° E</span>
              </div>
              {selectedTarget.type && (
                <div className="flex justify-between pt-1 border-t border-space-border/60">
                  <span className="text-slate-400">CLASSIFICATION:</span>
                  <span className="text-white font-medium">{selectedTarget.type}</span>
                </div>
              )}
            </div>

            {selectedTarget.source && (
              <div className="mt-2.5 text-[10px] text-slate-400 font-mono">
                Source: <span className="text-slate-300">{selectedTarget.source}</span>
              </div>
            )}
          </div>

          {/* Local Spatial Resolution Telemetry */}
          {resolution && (
            <div className="aerospace-panel p-4 text-xs font-mono">
              <div className="hud-label text-ares-cyan mb-2">LOCAL SPATIAL SCALE</div>
              <div className="space-y-1.5 text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-400">Latitude pixel scale:</span>
                  <span className="text-white font-bold">{resolution.meters_per_pixel_lat} m/px</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Longitude pixel scale:</span>
                  <span className="text-white font-bold">{resolution.meters_per_pixel_lon} m/px</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Cosine factor:</span>
                  <span className="text-ares-cyan">{resolution.cos_factor}</span>
                </div>
              </div>
              <p className="mt-2 text-[10px] text-slate-400 border-t border-space-border/60 pt-2 leading-relaxed">
                Longitude grid spacing is compressed by {resolution.longitude_compression_pct}% at this latitude.
              </p>
            </div>
          )}

          {/* Manual Precision Coordinate Entry */}
          <div className="aerospace-panel p-4">
            <div className="hud-label text-slate-300 mb-2">MANUAL COORDINATE PINNING</div>
            <p className="text-[11px] text-slate-400 mb-3">
              Enter target coordinates within regional sector boundaries:
            </p>

            <form onSubmit={handleManualPin} className="space-y-3 font-mono text-xs">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">
                  LATITUDE ({region.bounds.lat_min}° to {region.bounds.lat_max}° N)
                </label>
                <input
                  type="number"
                  step="0.0001"
                  min={region.bounds.lat_min}
                  max={region.bounds.lat_max}
                  value={manualLat}
                  onChange={(e) => setManualLat(parseFloat(e.target.value) || 0)}
                  className="w-full bg-space-950 border border-space-border rounded px-3 py-1.5 text-white focus:outline-none focus:border-ares-coral"
                />
              </div>

              <div>
                <label className="text-[10px] text-slate-400 block mb-1">
                  LONGITUDE ({region.bounds.lon_min}° to {region.bounds.lon_max}° E)
                </label>
                <input
                  type="number"
                  step="0.0001"
                  min={region.bounds.lon_min}
                  max={region.bounds.lon_max}
                  value={manualLon}
                  onChange={(e) => setManualLon(parseFloat(e.target.value) || 0)}
                  className="w-full bg-space-950 border border-space-border rounded px-3 py-1.5 text-white focus:outline-none focus:border-ares-coral"
                />
              </div>

              <button
                type="submit"
                className="w-full mt-2 bg-ares-coral hover:bg-ares-coral/90 text-white font-bold py-2 rounded flex items-center justify-center gap-2 transition-all font-sans text-xs uppercase tracking-wider"
              >
                <MapPin className="w-3.5 h-3.5" />
                Pin Coordinates
              </button>
            </form>
          </div>

          {/* Verified POI Quick-List */}
          <div className="aerospace-panel p-4">
            <div className="hud-label text-slate-300 mb-2.5">SECTOR SCIENTIFIC SITES</div>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {pois.map((poi) => {
                const isSelected = selectedTarget.name === poi.name;
                return (
                  <button
                    key={poi.id}
                    onClick={() =>
                      onSelectTarget({
                        lat: poi.lat,
                        lon: poi.lon,
                        name: poi.name,
                        type: poi.type,
                        source: poi.source_reference,
                      })
                    }
                    className={`w-full text-left p-2 rounded transition-all text-xs font-mono flex items-center justify-between ${
                      isSelected
                        ? 'bg-space-800 border-l-2 border-ares-green text-white font-bold'
                        : 'bg-space-950/60 hover:bg-space-850 text-slate-300'
                    }`}
                  >
                    <div>
                      <div className="truncate font-semibold">{poi.name}</div>
                      <div className="text-[10px] text-slate-400">
                        {poi.lat.toFixed(2)}°N, {poi.lon.toFixed(2)}°E
                      </div>
                    </div>
                    <ArrowRight className={`w-3.5 h-3.5 ${isSelected ? 'text-ares-green' : 'text-slate-500'}`} />
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

