import React from 'react';
import { 
  NavigationPage, 
  Region 
} from '../../types';
import { 
  LayoutDashboard, 
  Radar, 
  Navigation, 
  Layers, 
  AlertTriangle, 
  Microscope,
  MapPin,
  Cpu
} from 'lucide-react';

interface SidebarProps {
  currentPage: NavigationPage;
  onSelectPage: (page: NavigationPage) => void;
  regions: Region[];
  selectedRegionId: string;
  onSelectRegion: (regionId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onSelectPage,
  regions,
  selectedRegionId,
  onSelectRegion,
}) => {
  const navItems: { label: NavigationPage; icon: React.FC<{ className?: string }> }[] = [
    { label: 'Mission Overview', icon: LayoutDashboard },
    { label: 'Mars Explorer', icon: Radar },
    { label: 'Route Planner', icon: Navigation },
    { label: 'Terrain Intelligence', icon: Layers },
    { label: 'Hazard Analysis', icon: AlertTriangle },
    { label: 'Science Discovery', icon: Microscope },
  ];

  return (
    <aside className="w-64 min-h-screen bg-space-900 border-r border-space-border flex flex-col justify-between p-4 flex-shrink-0">
      <div>
        {/* Brand Header */}
        <div className="pt-2 pb-6 border-b border-space-border/60">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-extrabold tracking-widest text-white">🚀 ARES</span>
          </div>
          <div className="text-[10px] font-mono tracking-widest text-slate-400 mt-0.5">
            MISSION CONTROL SYSTEM
          </div>
        </div>

        {/* Navigation Menu */}
        <div className="mt-6">
          <div className="hud-label px-2 mb-2.5">MISSION MODULES</div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.label;
              return (
                <button
                  key={item.label}
                  onClick={() => onSelectPage(item.label)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-space-800 text-white border-l-2 border-ares-coral font-semibold shadow-inner'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-space-850'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-ares-coral' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Exploration Zone Selector */}
        <div className="mt-8 pt-6 border-t border-space-border/60">
          <div className="hud-label px-2 mb-2 flex items-center gap-1.5">
            <MapPin className="w-3 h-3 text-ares-cyan" />
            <span>EXPLORATION ZONE</span>
          </div>
          <select
            value={selectedRegionId}
            onChange={(e) => onSelectRegion(e.target.value)}
            className="w-full bg-space-950 border border-space-border rounded-lg px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-ares-cyan cursor-pointer"
          >
            {regions.map((reg) => (
              <option key={reg.id} value={reg.id}>
                {reg.name} ({reg.lat > 0 ? `+${reg.lat}` : reg.lat}°, {reg.lon}°)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Telemetry / Status Footer */}
      <div className="pt-4 border-t border-space-border/60 text-[11px] font-mono space-y-2 text-slate-400">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1.5 text-ares-green font-semibold">
            <span className="w-2 h-2 rounded-full bg-ares-green animate-pulse" />
            OPERATIONAL
          </span>
          <span className="text-[10px] bg-space-950 px-1.5 py-0.5 rounded border border-space-border">
            API v1.0
          </span>
        </div>
        <div className="text-[10px] text-slate-500 pt-1">
          <div>CHALLENGE: NASA SPACE APPS 2026</div>
          <div className="flex items-center gap-1 text-slate-400 font-semibold mt-0.5">
            <Cpu className="w-3 h-3 text-ares-cyan" />
            TEAM ARCEUS
          </div>
        </div>
      </div>
    </aside>
  );
};

