import React from 'react';
import { Region } from '../../types';
import { AlertTriangle, ShieldCheck, Info } from 'lucide-react';

interface HazardsViewProps {
  region: Region;
}

export const HazardsView: React.FC<HazardsViewProps> = ({ region }) => {
  const hazards = [
    {
      title: 'SLOPE INCLINE & WHEEL SLIP',
      severity: 'Critical on Loose Regolith',
      sub: 'Kinematic Suspension Limits',
      desc: 'On bedrock, rovers can ascend moderate slopes safely. However, on loose regolith (sand dunes), wheel slip exceeds 80% on slopes as low as 12°–15°, creating severe motor stall and immobilization risks.',
    },
    {
      title: 'EOLIAN SAND TRAPS & MEGARIPPLES',
      severity: 'Severe Immobilization Hazard',
      sub: 'Soil Shear Strength',
      desc: 'Fine-grained basaltic dust and sulfate-rich sands (such as the deposit that permanently entrapped NASA\'s Spirit rover at "Troy" in 2009) present negligible bearing capacity, risking wheel sinkage.',
    },
    {
      title: 'DUST STORMS & OPTICAL OPACITY (TAU)',
      severity: 'Power & Sensor Degradation',
      sub: 'Atmospheric Dynamics',
      desc: 'Martian dust storms drastically elevate atmospheric optical depth (tau). This curtails solar array power generation and severely degrades autonomous stereo hazard cameras.',
    },
    {
      title: 'THERMAL CYCLING & SOLAR RADIATION',
      severity: 'Subsystem Stress',
      sub: 'Space Environment',
      desc: 'Diurnal temperature swings from -90°C at night to +10°C at midday induce thermal fatigue on welds and electronics. Lack of an intrinsic global magnetic field exposes crews and electronics to cosmic rays.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Engineering Fact Banner */}
      <div className="p-4 rounded-lg bg-space-900 border-l-4 border-ares-coral border-y border-r border-space-border text-xs text-slate-300 leading-relaxed shadow-lg">
        <div className="flex items-center gap-2 mb-1 text-ares-coral font-bold font-mono">
          <Info className="w-4 h-4" />
          <span>ROVER KINEMATICS & SOIL MECHANICS PRINCIPLES</span>
        </div>
        <div>
          There is <strong>no single universal slope safety limit</strong> on Mars. Safe traversal angles depend on chassis suspension (e.g. NASA&apos;s 6-wheel rocker-bogie), wheel diameter, and soil shear strength. While NASA rovers possess static stability beyond 40° on firm bedrock, mission flight rules typically restrict autonomous driving to slopes below <strong>15°–20°</strong> to prevent uncontrollable wheel slip.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Hazard Profiles */}
        <div className="space-y-3">
          <div className="hud-label text-slate-200 flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-ares-coral" />
            <span>MARTIAN ENVIRONMENTAL HAZARDS</span>
          </div>

          {hazards.map((hz, idx) => (
            <div key={idx} className="aerospace-panel p-4 space-y-1 text-xs font-mono">
              <div className="flex justify-between items-start">
                <span className="font-bold text-white text-sm">{hz.title}</span>
                <span className="text-[10px] text-ares-coral font-bold bg-ares-coral/10 px-2 py-0.5 rounded border border-ares-coral/30">
                  {hz.sub}
                </span>
              </div>
              <div className="text-ares-amber text-[11px] font-semibold">{hz.severity}</div>
              <p className="text-slate-400 text-[11px] leading-relaxed pt-1">{hz.desc}</p>
            </div>
          ))}
        </div>

        {/* Right Column: Sector Protocols & Mitigation */}
        <div className="space-y-4">
          <div className="aerospace-panel p-5">
            <div className="hud-label text-ares-green flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" />
              <span>SECTOR SAFETY CORRIDOR STATUS</span>
            </div>
            <div className="text-xl hud-value text-ares-green mt-2">MONITORED</div>
            <div className="text-xs font-mono text-slate-300 mt-1">
              Active Zone: {region.name} ({region.lat}° N, {region.lon}° E)
            </div>
          </div>

          <div className="aerospace-panel p-5 text-xs font-mono space-y-2.5">
            <div className="hud-label text-slate-300">EXPLORATION SAFETY PROTOCOLS</div>
            <div className="space-y-2 text-slate-300 pt-1">
              <p>
                ● <strong className="text-white">Autonomous Drive Threshold:</strong> Flight rules cap automatic drive steps when slopes exceed 15°.
              </p>
              <p>
                ● <strong className="text-white">Visual Odometry:</strong> Rover compares successive camera frames to detect wheel slippage before getting stuck.
              </p>
              <p>
                ● <strong className="text-white">Ventifact Avoidance:</strong> Sharp, wind-sculpted rocks are actively avoided to preserve aluminum wheel treads.
              </p>
              <p>
                ● <strong className="text-white">Solar Margin:</strong> Minimum 30% battery reserve required before entering shaded crater wall areas.
              </p>
            </div>
          </div>

          <div className="aerospace-panel p-5 text-xs font-mono">
            <div className="hud-label text-ares-cyan mb-2">PHASE 4 ROUTE SOLVER INTEGRATION</div>
            <p className="text-slate-400 leading-relaxed text-[11px]">
              In Phase 4, these parameters will directly inform our pathfinding cost function: slopes, identified dune ripples, and obstacle clusters will receive high traversal cost penalties, automatically guiding routes through gentler bedrock corridors.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

