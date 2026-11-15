export interface TerrainHazard {
  id: string;
  regionId: string;
  name: string;
  lat: number;
  lon: number;
  type: 'SAND_TRAP' | 'STEEP_SCARP' | 'BOULDER_FIELD' | 'COLLAPSE_VOID';
  severity: 'CRITICAL' | 'WARNING' | 'ADVISORY';
  description: string;
  slopeRisk: string;
}

export const REGIONAL_HAZARDS: Record<string, TerrainHazard[]> = {
  'gale-crater': [
    {
      id: 'HZ-GC-01',
      regionId: 'gale-crater',
      name: 'Bagnold Dunes Eolian Sand Trap',
      lat: -4.68,
      lon: 137.38,
      type: 'SAND_TRAP',
      severity: 'CRITICAL',
      description: 'Active basaltic sand dunes and megaripples with minimal shear strength; severe wheel sinkage and entrapment hazard.',
      slopeRisk: 'Slopes 12°–18° with >80% wheel slip'
    },
    {
      id: 'HZ-GC-02',
      regionId: 'gale-crater',
      name: 'Gediz Vallis Ridge Scarp',
      lat: -4.75,
      lon: 137.35,
      type: 'STEEP_SCARP',
      severity: 'CRITICAL',
      description: 'Precipitous debris-flow boulder ridge with vertical wall segments exceeding rover kinematic climb limits.',
      slopeRisk: 'Slopes >25° exceeding vehicle stability threshold'
    },
    {
      id: 'HZ-GC-03',
      regionId: 'gale-crater',
      name: 'Peace Vallis Alluvial Blockfield',
      lat: -4.48,
      lon: 137.52,
      type: 'BOULDER_FIELD',
      severity: 'WARNING',
      description: 'Fractured conglomerate and perched boulder clusters risking belly-pan strike and wheel puncture.',
      slopeRisk: 'Local micro-topographic gradient variations 10°–16°'
    }
  ],
  'jezero-crater': [
    {
      id: 'HZ-JC-01',
      regionId: 'jezero-crater',
      name: 'South Séítah Megaripple Sand Field',
      lat: 18.41,
      lon: 77.44,
      type: 'SAND_TRAP',
      severity: 'CRITICAL',
      description: 'Low-bearing-capacity olivine-rich sand dunes bypassed by NASA Perseverance during campaign planning.',
      slopeRisk: 'Slopes 10°–15° with high immobilization probability'
    },
    {
      id: 'HZ-JC-02',
      regionId: 'jezero-crater',
      name: 'Western Fan Delta Front Scarp',
      lat: 18.44,
      lon: 77.36,
      type: 'STEEP_SCARP',
      severity: 'CRITICAL',
      description: '60-meter high near-vertical eroded delta front scarp; completely impassable for wheeled vehicles.',
      slopeRisk: 'Cliffs >35° vertical relief'
    },
    {
      id: 'HZ-JC-03',
      regionId: 'jezero-crater',
      name: 'Belva Crater Impact Ejecta Zone',
      lat: 18.52,
      lon: 77.38,
      type: 'BOULDER_FIELD',
      severity: 'WARNING',
      description: 'Dense field of meter-scale impact ejecta boulders exceeding rover ground clearance limits.',
      slopeRisk: 'Crater rim slope 15°–22°'
    }
  ],
  'olympus-mons': [
    {
      id: 'HZ-OM-01',
      regionId: 'olympus-mons',
      name: 'Central Caldera Rim Sheer Precipice',
      lat: 18.90,
      lon: 225.35,
      type: 'STEEP_SCARP',
      severity: 'CRITICAL',
      description: 'Up to 3,000-meter vertical drop into nested summit caldera sinkhole depressions.',
      slopeRisk: 'Sheer vertical drops >45°'
    },
    {
      id: 'HZ-OM-02',
      regionId: 'olympus-mons',
      name: 'Subsurface Lava Tube Skylight Collapse',
      lat: 18.45,
      lon: 226.15,
      type: 'COLLAPSE_VOID',
      severity: 'CRITICAL',
      description: 'Unstable basalt roof collapse pits with hidden overhangs and fracture zones.',
      slopeRisk: 'Abrupt 90° pit margins'
    },
    {
      id: 'HZ-OM-03',
      regionId: 'olympus-mons',
      name: 'Basal Scarp Perimeter Escarpment',
      lat: 17.50,
      lon: 223.50,
      type: 'STEEP_SCARP',
      severity: 'CRITICAL',
      description: 'Giant peripheral escarpment with 6 to 8 km sheer vertical descent to surrounding plains.',
      slopeRisk: 'Extreme escarpment cliff relief'
    }
  ]
};
