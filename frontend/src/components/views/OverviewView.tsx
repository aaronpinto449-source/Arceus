import React from 'react';
import { Region } from '../../types';
import { api } from '../../services/api';
import { Radar, Navigation, Layers, Microscope, CheckCircle2, Clock } from 'lucide-react';

interface OverviewViewProps {
  region: Region;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ region }) => {
  const mapUrl = api.getRegionMapUrl(region.id, 1024);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Surface Intelligence */}
        <div className="lg:col-span-2 aerospace-panel p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-mono tracking-wider text-slate-200 font-bold flex items-center gap-2">
              <Radar className="w-4 h-4 text-ares-cyan" />
              MARS SURFACE INTELLIGENCE — {region.name.toUpperCase()}
            </h2>
            <span className="text-[10px] font-mono text-ares-green">MOLA ELEVATION BASEMAP</span>
          </div>

          <div className="relative aspect-square max-h-[520px] mx-auto rounded-lg overflow-hidden border border-space-border bg-space-950">
            <img
              src={mapUrl}
              alt={`MOLA tile for ${region.name}`}
              className="w-full h-full object-cover"
            />
            <div className="absolute bottom-2 left-2 right-2 bg-space-950/80 backdrop-blur-md px-3 py-1.5 rounded text-[11px] font-mono text-slate-300 border border-space-border/60 flex justify-between">
              <span>LAT: {region.bounds.lat_min}° to {region.bounds.lat_max}° N</span>
              <span>LON: {region.bounds.lon_min}° to {region.bounds.lon_max}° E</span>
            </div>
          </div>

          <div className="text-[11px] font-mono text-slate-400">
            Source: NASA Mars Global Surveyor / Arizona State University MOLA dataset. Rendered elevation imagery.
          </div>
        </div>

        {/* Right Col: Mission Intelligence & System Modules */}
        <div className="space-y-4">
          <div className="aerospace-panel p-5">
            <div className="hud-label text-slate-400">EXPLORATION TARGET</div>
            <div className="text-xl hud-value text-white mt-1">{region.name}</div>
            <p className="text-xs text-slate-300 mt-2 leading-relaxed">{region.description}</p>
          </div>

          <div className="aerospace-panel p-5">
            <div className="hud-label text-ares-cyan">SCIENTIFIC OBJECTIVE</div>
            <p className="text-xs text-slate-200 mt-2 leading-relaxed font-medium">{region.objective}</p>
          </div>

          <div className="aerospace-panel p-5 font-mono text-xs space-y-2.5">
            <div className="hud-label text-slate-400 mb-2">SYSTEM MODULE STATUS</div>
            <div className="flex items-center gap-2 text-ares-green">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>React Mission Control Shell Operational</span>
            </div>
            <div className="flex items-center gap-2 text-ares-green">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>FastAPI Backend Gateway Connected</span>
            </div>
            <div className="flex items-center gap-2 text-ares-green">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Mars Explorer Interactive Canvas Ready</span>
            </div>
            <div className="flex items-center gap-2 text-ares-amber">
              <Clock className="w-3.5 h-3.5" />
              <span>A* Autonomous Route Engine (Phase 4)</span>
            </div>
            <div className="flex items-center gap-2 text-ares-amber">
              <Clock className="w-3.5 h-3.5" />
              <span>Astronaut Life Support Telemetry (Phase 5)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Exploration Systems 3-Column Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-space-border">
        <div className="aerospace-panel p-5">
          <Navigation className="w-6 h-6 text-ares-coral mb-2" />
          <h3 className="text-sm font-bold text-white mb-1">ROUTE PLANNER</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Configure expedition waypoints and terrain-aware surface traversal routes across Martian craters.
          </p>
        </div>

        <div className="aerospace-panel p-5">
          <Layers className="w-6 h-6 text-ares-cyan mb-2" />
          <h3 className="text-sm font-bold text-white mb-1">TERRAIN INTELLIGENCE</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Analyze topographic elevation relief, slope constraints, and Martian datum reference standards.
          </p>
        </div>

        <div className="aerospace-panel p-5">
          <Microscope className="w-6 h-6 text-ares-green mb-2" />
          <h3 className="text-sm font-bold text-white mb-1">SCIENCE DISCOVERY</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Catalog verified NASA scientific exploration sites, sedimentary mudstones, and astrobiological targets.
          </p>
        </div>
      </div>
    </div>
  );
};

