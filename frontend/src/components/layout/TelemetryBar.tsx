import React from 'react';
import { Region, SelectedTarget } from '../../types';
import { Activity, Target, Compass, Globe } from 'lucide-react';

interface TelemetryBarProps {
  region: Region;
  selectedTarget: SelectedTarget;
}

export const TelemetryBar: React.FC<TelemetryBarProps> = ({ region, selectedTarget }) => {
  const metrics = [
    {
      label: 'MISSION STATUS',
      value: 'ACTIVE',
      sub: 'Prototype environment',
      icon: Activity,
      color: 'text-ares-green',
    },
    {
      label: 'TARGET REGION',
      value: region.name,
      sub: region.diameter ? `Diameter: ${region.diameter}` : 'Exploration sector',
      icon: Globe,
      color: 'text-white',
    },
    {
      label: 'TARGET LATITUDE',
      value: `${selectedTarget.lat.toFixed(3)}° N`,
      sub: 'Planetocentric coordinate',
      icon: Compass,
      color: 'text-ares-cyan',
    },
    {
      label: 'TARGET LONGITUDE',
      value: `${selectedTarget.lon.toFixed(3)}° E`,
      sub: 'East longitude standard',
      icon: Target,
      color: 'text-ares-coral',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {metrics.map((m, idx) => {
        const Icon = m.icon;
        return (
          <div
            key={idx}
            className="aerospace-panel p-4 flex flex-col justify-between hover:border-space-border-bright transition-all"
          >
            <div className="flex items-center justify-between">
              <span className="hud-label">{m.label}</span>
              <Icon className="w-3.5 h-3.5 text-slate-500" />
            </div>
            <div className={`text-xl md:text-2xl hud-value mt-2 ${m.color}`}>{m.value}</div>
            <div className="text-[11px] text-slate-400 font-mono mt-1 truncate">{m.sub}</div>
          </div>
        );
      })}
    </div>
  );
};

