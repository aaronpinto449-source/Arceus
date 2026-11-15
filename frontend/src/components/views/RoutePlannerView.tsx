import React, { useState } from 'react';
import { Region, PointOfInterest } from '../../types';
import { Navigation, Compass, Info } from 'lucide-react';

interface RoutePlannerViewProps {
  region: Region;
  pois: PointOfInterest[];
}

export const RoutePlannerView: React.FC<RoutePlannerViewProps> = ({ region, pois }) => {
  const [startPoi, setStartPoi] = useState<string>(pois[0]?.name || 'Landing Site');
  const [destPoi, setDestPoi] = useState<string>(pois[1]?.name || 'Scientific Target');
  const [vehicle, setVehicle] = useState<string>('pcr');
  const [priority, setPriority] = useState<string>('balanced');

  return (
    <div className="space-y-6">
      {/* Simulation Notice Banner */}
      <div className="p-4 rounded-lg bg-space-900 border-l-4 border-ares-amber border-y border-r border-space-border text-xs text-slate-300 leading-relaxed shadow-lg">
        <div className="flex items-center gap-2 mb-1 text-ares-amber font-bold font-mono">
          <Info className="w-4 h-4" />
          <span>EXPEDITION PLANNING ENGINE (PHASE 4 FOUNDATION)</span>
        </div>
        <div>
          This module defines mission parameters and waypoint nodes. Algorithmic pathfinding (A* graph search over synthetic terrain cost grids)
          and dynamic astronaut life-support consumption models are scheduled for subsequent milestones.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Mission Expedition Configuration */}
        <div className="aerospace-panel p-5 space-y-4">
          <div className="hud-label text-ares-coral flex items-center gap-2">
            <Compass className="w-4 h-4" />
            <span>EXPEDITION CONFIGURATION</span>
          </div>

          <div>
            <label className="text-xs font-mono text-slate-300 block mb-1.5">
              DEPARTURE POINT (START WAYPOINT)
            </label>
            <select
              value={startPoi}
              onChange={(e) => setStartPoi(e.target.value)}
              className="w-full bg-space-950 border border-space-border rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-ares-coral cursor-pointer"
            >
              {pois.map((p) => (
                <option key={p.id} value={p.name}>
                  {p.name} ({p.type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-mono text-slate-300 block mb-1.5">
              TARGET DESTINATION (END WAYPOINT)
            </label>
            <select
              value={destPoi}
              onChange={(e) => setDestPoi(e.target.value)}
              className="w-full bg-space-950 border border-space-border rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-ares-coral cursor-pointer"
            >
              {pois.map((p) => (
                <option key={p.id} value={p.name}>
                  {p.name} ({p.type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-mono text-slate-300 block mb-1.5">
              SURFACE VEHICLE CONFIGURATION
            </label>
            <select
              value={vehicle}
              onChange={(e) => setVehicle(e.target.value)}
              className="w-full bg-space-950 border border-space-border rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-ares-cyan cursor-pointer"
            >
              <option value="pcr">Pressurized Crew Rover (PCR-1) — 12 km/h</option>
              <option value="luv">Lightweight Unpressurized Scout (LUV) — 18 km/h</option>
              <option value="hch">Heavy Cargo & Habitat Hauler (HCH) — 6 km/h</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-mono text-slate-300 block mb-1.5">
              TRAVERSAL PRIORITY
            </label>
            <div className="space-y-1.5 font-mono text-xs">
              {[
                { id: 'balanced', label: 'Balanced (Optimal Energy & Moderate Slope)' },
                { id: 'safety', label: 'Minimum Slope (Conservative Safety First)' },
                { id: 'direct', label: 'Direct Traversal (Distance Minimization)' },
              ].map((opt) => (
                <label
                  key={opt.id}
                  className="flex items-center gap-2 p-2 rounded bg-space-950/60 border border-space-border cursor-pointer hover:bg-space-850"
                >
                  <input
                    type="radio"
                    name="priority"
                    value={opt.id}
                    checked={priority === opt.id}
                    onChange={(e) => setPriority(e.target.value)}
                    className="text-ares-coral focus:ring-0"
                  />
                  <span className="text-slate-300 text-[11px]">{opt.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Right 2 Columns: Route Staging & Telemetry Preview */}
        <div className="lg:col-span-2 space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="aerospace-panel p-4">
              <div className="hud-label text-slate-400">EXPEDITION STATUS</div>
              <div className="text-lg hud-value text-ares-amber mt-1">CONFIGURED</div>
              <div className="text-[10px] font-mono text-slate-400 mt-1">Ready for A* solver</div>
            </div>

            <div className="aerospace-panel p-4">
              <div className="hud-label text-slate-400">DEPARTURE</div>
              <div className="text-sm hud-value text-white mt-1 truncate">{startPoi}</div>
              <div className="text-[10px] font-mono text-slate-400 mt-1">{region.name}</div>
            </div>

            <div className="aerospace-panel p-4">
              <div className="hud-label text-slate-400">DESTINATION</div>
              <div className="text-sm hud-value text-ares-cyan mt-1 truncate">{destPoi}</div>
              <div className="text-[10px] font-mono text-slate-400 mt-1">Target waypoint</div>
            </div>

            <div className="aerospace-panel p-4">
              <div className="hud-label text-slate-400">ROUTER ENGINE</div>
              <div className="text-lg hud-value text-ares-coral mt-1">PHASE 4</div>
              <div className="text-[10px] font-mono text-slate-400 mt-1">NetworkX graph solver</div>
            </div>
          </div>

          <div className="aerospace-panel p-6 space-y-4">
            <h3 className="text-sm font-bold font-mono text-slate-200 flex items-center gap-2">
              <Navigation className="w-4 h-4 text-ares-coral" />
              TERRAIN-AWARE ROUTE PLANNING ARCHITECTURE
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed font-mono">
              In Phase 4, ARES will evaluate surface traversability by transforming the regional MOLA basemap into a weighted grid graph.
              Each grid edge will incorporate:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono">
              <div className="p-3 rounded bg-space-950 border border-space-border space-y-1">
                <span className="text-ares-cyan font-bold block">1. SLOPE PENALTY</span>
                <span className="text-slate-400 text-[11px]">
                  Costs scale exponentially as incline approaches rover wheel slippage thresholds (~15°–20°).
                </span>
              </div>
              <div className="p-3 rounded bg-space-950 border border-space-border space-y-1">
                <span className="text-ares-amber font-bold block">2. REGOLITH RISKS</span>
                <span className="text-slate-400 text-[11px]">
                  Identified eolian sand dunes and boulder fields receive high traversal impedance to avoid entrapment.
                </span>
              </div>
              <div className="p-3 rounded bg-space-950 border border-space-border space-y-1">
                <span className="text-ares-green font-bold block">3. POWER & TIME</span>
                <span className="text-slate-400 text-[11px]">
                  Calculates watt-hour consumption and sol sunlight windows along safe bedrock corridors.
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
