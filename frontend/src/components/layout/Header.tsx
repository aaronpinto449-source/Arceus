import React from 'react';
import { Rocket, Radio } from 'lucide-react';

interface HeaderProps {
  currentRegionName: string;
}

export const Header: React.FC<HeaderProps> = ({ currentRegionName }) => {
  return (
    <div className="relative mb-6 p-6 rounded-xl border border-space-border bg-gradient-to-r from-space-900 via-space-850 to-[#1e1414] overflow-hidden shadow-2xl">
      {/* Decorative top accent glow */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-ares-cyan via-ares-coral to-transparent" />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono tracking-[0.25em] text-ares-cyan font-bold uppercase">
              PLANETARY EXPLORATION PLATFORM / SOL 001
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-ares-green animate-pulse" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-wider text-white flex items-center gap-3">
            <Rocket className="w-7 h-7 text-ares-coral" />
            ARES MISSION CONTROL
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Astronaut Route Exploration & Survival &nbsp;|&nbsp; 
            <span className="text-slate-300 font-semibold">TEAM ARCEUS</span> &nbsp;|&nbsp; 
            NASA SPACE APPS CHALLENGE 2026
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-space-950/70 border border-space-border px-4 py-2 rounded-lg text-right">
            <div className="text-[10px] font-mono tracking-widest text-slate-400 uppercase">ACTIVE ZONE</div>
            <div className="text-sm font-bold text-ares-green font-mono">{currentRegionName.toUpperCase()}</div>
          </div>
          <div className="bg-space-950/70 border border-space-border px-3.5 py-2 rounded-lg flex items-center gap-2 text-ares-cyan font-mono text-xs">
            <Radio className="w-4 h-4 animate-pulse" />
            <span>LINK ACTIVE</span>
          </div>
        </div>
      </div>
    </div>
  );
};

