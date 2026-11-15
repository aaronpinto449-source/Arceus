import React from 'react';
import { Region } from '../../types';
import { Layers, Info } from 'lucide-react';

interface TerrainViewProps {
  region: Region;
}

export const TerrainView: React.FC<TerrainViewProps> = ({ region }) => {
  const elevationBands = [
    {
      color: 'bg-[#3b2d6a]',
      label: 'VIOLET / DARK BLUE',
      desc: 'Deep Basins & Depressions',
      range: '< -4,000 m',
      example: 'Impact basin floors, deep crater interiors (Hellas, Gale crater floor)',
    },
    {
      color: 'bg-[#29788f]',
      label: 'CYAN / LIGHT BLUE',
      desc: 'Lowland Plains',
      range: '-4,000 to -1,500 m',
      example: 'Vast northern plains (Vastitas Borealis), ancient depositional surfaces',
    },
    {
      color: 'bg-[#4da851]',
      label: 'GREEN / YELLOW',
      desc: 'Martian Datum Plains',
      range: '-1,500 to +2,000 m',
      example: 'Equatorial terrain, delta surfaces, average planetary datum reference',
    },
    {
      color: 'bg-[#c75e2e]',
      label: 'ORANGE / RED',
      desc: 'Highlands & Volcanic Aprons',
      range: '+2,000 to +8,000 m',
      example: 'Southern cratered highlands, volcanic shield aprons',
    },
    {
      color: 'bg-[#f4ebe6]',
      label: 'WHITE / LIGHT PINK',
      desc: 'Volcanic Summits',
      range: '+8,000 to +21,000 m+',
      example: 'Massive peaks of Tharsis (Olympus, Ascraeus, Pavonis Mons)',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Geodetic Notice Banner */}
      <div className="p-4 rounded-lg bg-space-900 border-l-4 border-ares-cyan border-y border-r border-space-border text-xs text-slate-300 leading-relaxed shadow-lg">
        <div className="flex items-center gap-2 mb-1 text-ares-cyan font-bold font-mono">
          <Info className="w-4 h-4" />
          <span>MARTIAN GEODETIC DATUM STANDARD</span>
        </div>
        <div>
          Unlike Earth, Mars has no sea level. Topographic elevations are officially defined relative to an equipotential surface 
          (the Martian &quot;areoid&quot;) where the average atmospheric pressure is <strong>610 Pascals</strong> (the triple point of water).
          MOLA color tiles depict relative elevation bands qualitatively.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Color Palette Elevation Key */}
        <div className="aerospace-panel p-5 space-y-3">
          <div className="hud-label text-slate-200 flex items-center gap-2">
            <Layers className="w-4 h-4 text-ares-cyan" />
            <span>MOLA ELEVATION PALETTE KEY</span>
          </div>

          <div className="space-y-2.5 mt-3">
            {elevationBands.map((band, idx) => (
              <div
                key={idx}
                className="p-3 rounded bg-space-950 border border-space-border flex items-start gap-3 text-xs font-mono"
              >
                <div className={`w-4 h-4 rounded-sm flex-shrink-0 mt-0.5 border border-white/20 ${band.color}`} />
                <div className="flex-1">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-white">{band.label}</span>
                    <span className="text-ares-green font-semibold">{band.range}</span>
                  </div>
                  <div className="text-ares-amber text-[11px] font-semibold mt-0.5">{band.desc}</div>
                  <div className="text-slate-400 text-[10px] mt-1">{band.example}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Regional Topographic Profile */}
        <div className="space-y-4">
          <div className="aerospace-panel p-5">
            <div className="hud-label text-ares-green">SECTOR ELEVATION SPAN</div>
            <div className="text-xl hud-value text-white mt-1">{region.elevation_approx}</div>
            <p className="text-xs text-slate-300 mt-2 font-mono leading-relaxed">{region.elevation_summary}</p>
          </div>

          <div className="aerospace-panel p-5">
            <div className="hud-label text-slate-300">REGIONAL MORPHOLOGY</div>
            <p className="text-xs text-slate-200 mt-2 leading-relaxed font-mono">{region.geology}</p>
          </div>

          <div className="aerospace-panel p-5 text-xs font-mono space-y-2">
            <div className="hud-label text-ares-coral">SURFACE TRAVERSABILITY CLASSIFICATION</div>
            <div className="space-y-2 text-slate-300 pt-1">
              <p>
                ● <strong className="text-white">Pavement Bedrock:</strong> High mechanical traction, minimal wheel sinkage. Optimal for traverse speed.
              </p>
              <p>
                ● <strong className="text-white">Sedimentary Terraces:</strong> Moderate slope challenges, step scarps. Requires path winding.
              </p>
              <p>
                ● <strong className="text-white">Active Ripple Fields:</strong> Unconsolidated fine basaltic grains. High slip hazard; designated as caution zones.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

