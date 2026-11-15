import type { NavigationPage, InterfaceMode, Region, PointOfInterest, SelectedTarget, MissionTelemetry } from '../types';
import { INITIAL_REGIONS } from '../data/regions';
import { api } from '../services/api';

class MissionStore {
  activePage = $state<NavigationPage>('Mission Overview');
  activeRegionId = $state<string>('gale-crater');
  interfaceMode = $state<InterfaceMode>('desktop');
  selectedTarget = $state<SelectedTarget | null>(null);
  selectedPoi = $state<PointOfInterest | null>(null);
  regions = $state<Region[]>(INITIAL_REGIONS);
  backendConnected = $state<boolean>(false);
  sidebarOpen = $state<boolean>(true);
  rightDrawerOpen = $state<boolean>(false);
  activeModal = $state<string | null>(null);

  telemetry = $state<MissionTelemetry>({
    sol: '001',
    commDelay: '14m 22s',
    systemStatus: 'NOMINAL',
    powerGrid: '98.4%',
    surfaceTemp: '-63°C',
    atmosphericPressure: '610 Pa'
  });

  currentRegion = $derived<Region>(
    this.regions.find(r => r.id === this.activeRegionId) || this.regions[0]
  );

  currentPois = $derived<PointOfInterest[]>(
    this.currentRegion.pois || []
  );

  constructor() {
    this.init();
  }

  async init() {
    try {
      const health = await api.checkHealth();
      if (health.status === 'OK' || health.status === 'NOMINAL') {
        this.backendConnected = true;
        const fetchedRegions = await api.getRegions();
        if (fetchedRegions && fetchedRegions.length > 0) {
          this.regions = fetchedRegions;
        }
      }
    } catch {
      this.backendConnected = false;
    }
  }

  setActivePage(page: NavigationPage) {
    this.activePage = page;
  }

  setActiveRegion(regionId: string) {
    this.activeRegionId = regionId;
    this.selectedTarget = null;
    this.selectedPoi = null;
  }

  setInterfaceMode(mode: InterfaceMode) {
    this.interfaceMode = mode;
    // In tablet field mode, sidebar defaults to compact / minimal navigation
    if (mode === 'field') {
      this.sidebarOpen = false;
    } else {
      this.sidebarOpen = true;
    }
  }

  toggleInterfaceMode() {
    this.setInterfaceMode(this.interfaceMode === 'desktop' ? 'field' : 'desktop');
  }

  selectTarget(target: SelectedTarget | null) {
    this.selectedTarget = target;
    if (target) {
      this.rightDrawerOpen = true;
    }
  }

  selectPoi(poi: PointOfInterest | null) {
    this.selectedPoi = poi;
    if (poi) {
      this.selectedTarget = {
        lat: poi.lat,
        lon: poi.lon,
        name: poi.name,
        type: poi.type,
        source: poi.source_reference
      };
      this.rightDrawerOpen = true;
    }
  }

  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  }

  toggleRightDrawer() {
    this.rightDrawerOpen = !this.rightDrawerOpen;
  }

  setRightDrawer(open: boolean) {
    this.rightDrawerOpen = open;
  }

  openModal(modalId: string) {
    this.activeModal = modalId;
  }

  closeModal() {
    this.activeModal = null;
  }
}

export const mission = new MissionStore();
