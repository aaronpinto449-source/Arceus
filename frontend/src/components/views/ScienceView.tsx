import React from 'react';
import { Region, PointOfInterest } from '../../types';
import { Microscope, Award, Bookmark } from 'lucide-react';

interface ScienceViewProps {
  region: Region;
  pois: PointOfInterest[];
}

export const ScienceView: React.FC<ScienceViewProps> = ({ region, pois }) => {
  return (
    <div className="space-y-6">
      {/* Verified Science Catalog Banner */}
      <div className="p-4 rounded-lg bg-space-900 border-l-4 border-ares-green border-y border-r border-space-border text-xs text-slate-300 leading-relaxed shadow-lg">
        <div className="flex items-center gap-2 mb-1 text-ares-green font-bold font-mono">
          <Award className="w-4 h-4" />
          <span>VERIFIED PLANETARY SCIENCE ARCHIVE (NASA PDS / IAU)</span>
        </div>
        <div>
          The scientific points of interest below represent verified ground targets compiled from NASA mission archives 
          (Curiosity MSL, Perseverance Mars 2020, and MGS/MRO orbital surveys). Coordinates represent true planetocentric locations.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns: Detailed POI Cards */}
        <div className="lg:col-span-2 space-y-4">
          <div className="hud-label text-slate-200 flex items-center gap-2 mb-2">
            <Microscope className="w-4 h-4 text-ares-green" />
            <span>SCIENTIFIC TARGET CATALOG — {region.name.toUpperCase()}</span>
          </div>

          {pois.map((poi) => (
            <div key={poi.id} className="aerospace-panel p-5 space-y-3 font-mono">
              <div className="flex items-center justify-between">
                <span className="text-base font-bold text-white">{poi.name}</span>
                <span className="text-[10px] font-bold text-ares-green bg-ares-green/10 border border-ares-green/30 px-2 py-0.5 rounded">
                  {poi.id}
                </span>
              </div>

              <div className="text-xs text-ares-cyan">
                COORDINATES: {poi.lat.toFixed(4)}° N, {poi.lon.toFixed(4)}° E &nbsp;|&nbsp; TYPE: {poi.type}
              </div>

              <p className="text-xs text-slate-300 leading-relaxed font-sans">{poi.description}</p>

              <div className="pt-2 border-t border-space-border/60 text-xs">
                <span className="text-ares-amber font-semibold">EXPLORATION VALUE: </span>
                <span className="text-slate-300 font-sans">{poi.significance}</span>
              </div>

              {poi.source_reference && (
                <div className="text-[10px] text-slate-400">
                  <Bookmark className="w-3 h-3 inline mr-1 text-slate-400" />
                  Citation: <span className="text-slate-300">{poi.source_reference}</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Right Column: Mission Objectives & Sample Caching */}
        <div className="space-y-4">
          <div className="aerospace-panel p-5">
            <div className="hud-label text-slate-300">PRIMARY GEOLOGICAL GOAL</div>
            <div className="text-base font-bold text-white mt-1">{region.objective}</div>
            <p className="text-xs text-slate-300 mt-2 font-mono leading-relaxed">{region.description}</p>
          </div>

          <div className="aerospace-panel p-5">
            <div className="hud-label text-ares-green">MISSION CONTEXT</div>
            <div className="text-sm font-bold text-ares-green mt-1">{region.mission_context}</div>
            <p className="text-xs text-slate-400 mt-2 font-mono leading-relaxed">
              NASA surface rovers utilize multispectral imaging, alpha-particle X-ray spectrometers (APXS),
              and robotic rock drills at these exact geological formations.
            </p>
          </div>

          <div className="aerospace-panel p-5 text-xs font-mono space-y-2">
            <div className="hud-label text-ares-coral">EXPEDITION SAMPLE CACHING PRIORITIES</div>
            <div className="space-y-2 text-slate-300 pt-1">
              <p>
                ● <strong className="text-white">Igneous Cumulates:</strong> Provide precise radiometric crystallization age dating.
              </p>
              <p>
                ● <strong className="text-white">Fine-grained Mudstones:</strong> Highest preservation potential for ancient organic molecules.
              </p>
              <p>
                ● <strong className="text-white">Hydrated Sulfates & Clays:</strong> Reveal timing and chemistry of ancient surface water desiccation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

