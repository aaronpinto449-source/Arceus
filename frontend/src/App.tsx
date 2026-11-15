import React, { useState, useEffect } from 'react';
import { NavigationPage, Region, PointOfInterest, SelectedTarget } from './types';
import { api } from './services/api';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { TelemetryBar } from './components/layout/TelemetryBar';
import { Footer } from './components/layout/Footer';
import { OverviewView } from './components/views/OverviewView';
import { ExplorerView } from './components/views/ExplorerView';
import { RoutePlannerView } from './components/views/RoutePlannerView';
import { TerrainView } from './components/views/TerrainView';
import { HazardsView } from './components/views/HazardsView';
import { ScienceView } from './components/views/ScienceView';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<NavigationPage>('Mission Overview');
  const [regions, setRegions] = useState<Region[]>([]);
  const [selectedRegionId, setSelectedRegionId] = useState<string>('gale-crater');
  const [currentRegion, setCurrentRegion] = useState<Region | null>(null);
  const [pois, setPois] = useState<PointOfInterest[]>([]);
  const [selectedTarget, setSelectedTarget] = useState<SelectedTarget>({
    lat: -4.59,
    lon: 137.44,
    name: 'Bradbury Landing',
  });
  const [loading, setLoading] = useState<boolean>(true);

  // Initial load: Fetch regions list
  useEffect(() => {
    async function init() {
      try {
        const data = await api.getRegions();
        setRegions(data);
        if (data.length > 0) {
          const initialRegion = data[0];
          setSelectedRegionId(initialRegion.id);
        }
      } catch (err) {
        console.error('Failed to load regions from API:', err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  // When selected region changes, fetch full region profile and POIs
  useEffect(() => {
    if (!selectedRegionId) return;

    async function loadRegionData() {
      try {
        const [regData, poiData] = await Promise.all([
          api.getRegion(selectedRegionId),
          api.getRegionPOIs(selectedRegionId),
        ]);
        setCurrentRegion(regData);
        setPois(poiData);

        // Update default target to region's primary POI
        if (poiData.length > 0) {
          setSelectedTarget({
            lat: poiData[0].lat,
            lon: poiData[0].lon,
            name: poiData[0].name,
            type: poiData[0].type,
            source: poiData[0].source_reference,
          });
        } else {
          setSelectedTarget({
            lat: regData.lat,
            lon: regData.lon,
            name: `${regData.name} Datum Center`,
          });
        }
      } catch (err) {
        console.error(`Failed to load region data for ${selectedRegionId}:`, err);
      }
    }

    loadRegionData();
  }, [selectedRegionId]);

  if (loading || !currentRegion) {
    return (
      <div className="min-h-screen bg-space-950 flex flex-col items-center justify-center font-mono text-ares-cyan gap-3">
        <div className="w-10 h-10 border-2 border-ares-cyan border-t-transparent rounded-full animate-spin" />
        <span className="text-xs tracking-widest uppercase">INITIALIZING ARES MISSION CONTROL INTERFACE...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-space-950 text-slate-200">
      {/* Aerospace Navigation Sidebar */}
      <Sidebar
        currentPage={currentPage}
        onSelectPage={setCurrentPage}
        regions={regions}
        selectedRegionId={selectedRegionId}
        onSelectRegion={setSelectedRegionId}
      />

      {/* Main Mission Control Console */}
      <main className="flex-1 p-6 max-w-7xl mx-auto overflow-y-auto">
        <Header currentRegionName={currentRegion.name} />

        <TelemetryBar
          region={currentRegion}
          selectedTarget={selectedTarget}
        />

        {/* View Router */}
        {currentPage === 'Mission Overview' && (
          <OverviewView region={currentRegion} />
        )}

        {currentPage === 'Mars Explorer' && (
          <ExplorerView
            region={currentRegion}
            pois={pois}
            selectedTarget={selectedTarget}
            onSelectTarget={setSelectedTarget}
          />
        )}

        {currentPage === 'Route Planner' && (
          <RoutePlannerView
            region={currentRegion}
            pois={pois}
          />
        )}

        {currentPage === 'Terrain Intelligence' && (
          <TerrainView region={currentRegion} />
        )}

        {currentPage === 'Hazard Analysis' && (
          <HazardsView region={currentRegion} />
        )}

        {currentPage === 'Science Discovery' && (
          <ScienceView
            region={currentRegion}
            pois={pois}
          />
        )}

        <Footer />
      </main>
    </div>
  );
};

