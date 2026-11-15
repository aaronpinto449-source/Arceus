import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-12 py-6 border-t border-space-border text-center text-xs font-mono text-slate-500 tracking-wider">
      <div className="flex flex-col md:flex-row items-center justify-between gap-3 text-[11px]">
        <div>
          ARES &nbsp;|&nbsp; TEAM ARCEUS &nbsp;|&nbsp; NASA SPACE APPS CHALLENGE 2026
        </div>
        <div className="text-slate-400">
          PROTOTYPE ENVIRONMENT — NOT CERTIFIED FOR HUMAN MISSION NAVIGATION
        </div>
        <div className="text-ares-cyan/80">
          DATA SOURCE: NASA MGS MOLA MEG256
        </div>
      </div>
    </footer>
  );
};

