export const MAP_MIN_ZOOM = 10

/** Palette for variant A (the only supported variant). */
const PALETTE = {
  bg:          '#1E1E2A',
  water:       '#1D3352',
  park:        '#1C2E24',
  building:    '#252532',
  roadMinor:   '#34344A',
  roadMajor:   '#4A4A66',
  roadHighway: '#5E5E7E',
  text:        '#B4B0CC',
}

interface MapLayer {
  id: string
  type: string
  source?: string
  'source-layer'?: string
  minzoom?: number
  maxzoom?: number
  filter?: unknown[]
  paint?: Record<string, unknown>
  layout?: Record<string, unknown>
}

function buildLayers(src: string): MapLayer[] {
  const p = PALETTE
  const halo = p.bg

  return [
    // === Fill: land, parks, landcover ===
    { id: 'bg', type: 'background',
      paint: { 'background-color': p.bg } },
    { id: 'park', type: 'fill', source: src, 'source-layer': 'park',
      paint: { 'fill-color': p.park } },
    { id: 'landcover', type: 'fill', source: src, 'source-layer': 'landcover',
      filter: ['match', ['get', 'class'],
        ['grass', 'wood', 'forest', 'scrub', 'farmland'], true, false],
      paint: { 'fill-color': p.park, 'fill-opacity': 0.55 } },
    { id: 'landuse', type: 'fill', source: src, 'source-layer': 'landuse',
      paint: { 'fill-color': p.bg, 'fill-opacity': 0.4 } },

    // === Water (drawn AFTER landcover so it always shows over wetland) ===
    { id: 'water', type: 'fill', source: src, 'source-layer': 'water',
      paint: { 'fill-color': p.water } },
    { id: 'waterway', type: 'line', source: src, 'source-layer': 'waterway',
      paint: {
        'line-color': p.water,
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1, 14, 3],
      } },

    // === Buildings ===
    { id: 'building', type: 'fill', source: src, 'source-layer': 'building', minzoom: 14,
      paint: { 'fill-color': p.building, 'fill-outline-color': p.bg } },

    // === Roads: minor ===
    { id: 'road-path', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['path', 'track', 'pedestrian'], true, false],
      paint: { 'line-color': p.roadMinor,
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.5, 16, 1.5] } },
    { id: 'road-service', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['==', ['get', 'class'], 'service'],
      paint: { 'line-color': p.roadMinor,
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.8, 16, 2.5] } },
    { id: 'road-minor', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['minor', 'street', 'street_limited'], true, false],
      paint: { 'line-color': p.roadMinor,
        'line-width': ['interpolate', ['linear'], ['zoom'], 12, 1.2, 15, 4] } },

    // === Roads: secondary/tertiary ===
    { id: 'road-secondary', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['secondary', 'tertiary'], true, false],
      paint: { 'line-color': p.roadMajor,
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.5, 14, 5.5, 16, 9] } },

    // === Roads: primary/trunk/motorway ===
    { id: 'road-major', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['primary', 'trunk'], true, false],
      paint: { 'line-color': p.roadHighway,
        'line-width': ['interpolate', ['linear'], ['zoom'], 8, 1.5, 12, 4, 16, 10] } },
    { id: 'road-highway', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['==', ['get', 'class'], 'motorway'],
      paint: { 'line-color': p.roadHighway,
        'line-width': ['interpolate', ['linear'], ['zoom'], 6, 2, 12, 5, 16, 11] } },

    // === Transit (rail/metro lines) ===
    { id: 'transit-rail', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['rail', 'transit'], true, false],
      paint: { 'line-color': p.roadMajor, 'line-width': 1.5,
        'line-dasharray': [4, 2] } },

    // === Water labels ===
    { id: 'water-label-point', type: 'symbol', source: src, 'source-layer': 'water_name',
      filter: ['match', ['geometry-type'], ['Point', 'MultiPoint'], true, false],
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Italic'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 10, 11, 14, 14],
        'text-max-width': 10,
      },
      paint: { 'text-color': '#5A6E8A', 'text-halo-color': halo, 'text-halo-width': 1.5 } },
    { id: 'water-label-line', type: 'symbol', source: src, 'source-layer': 'water_name',
      filter: ['match', ['geometry-type'], ['LineString', 'MultiLineString'], true, false],
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Italic'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 10, 11, 14, 14],
        'symbol-placement': 'line',
        'symbol-spacing': 350,
      },
      paint: { 'text-color': '#5A6E8A', 'text-halo-color': halo, 'text-halo-width': 1.5 } },

    // === Place: islands ===
    { id: 'place-island', type: 'symbol', source: src, 'source-layer': 'place',
      filter: ['==', ['get', 'class'], 'island'],
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 15, 13],
        'text-max-width': 8,
      },
      paint: { 'text-color': p.text, 'text-halo-color': halo, 'text-halo-width': 1.5 } },

    // === Place: neighbourhoods ===
    { id: 'place-neighbourhood', type: 'symbol', source: src, 'source-layer': 'place',
      filter: ['match', ['get', 'class'],
        ['neighbourhood', 'suburb', 'quarter', 'city_block'], true, false],
      minzoom: 11,
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 11, 10, 15, 13],
        'text-max-width': 6,
        'text-transform': 'uppercase',
        'text-letter-spacing': 0.1,
      },
      paint: { 'text-color': p.text, 'text-halo-color': halo, 'text-halo-width': 1.5 } },

    // === Place: cities/towns ===
    { id: 'place-town', type: 'symbol', source: src, 'source-layer': 'place',
      filter: ['match', ['get', 'class'], ['city', 'town'], true, false],
      maxzoom: 13,
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Bold'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 8, 12, 12, 16],
      },
      paint: { 'text-color': p.text, 'text-halo-color': halo, 'text-halo-width': 2 } },

    // === Road labels ===
    { id: 'road-label-minor', type: 'symbol', source: src, 'source-layer': 'transportation_name',
      filter: ['match', ['get', 'class'],
        ['minor', 'service', 'track', 'path', 'street', 'street_limited'], true, false],
      minzoom: 15,
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': 10,
        'symbol-placement': 'line',
        'text-max-angle': 30,
        'text-rotation-alignment': 'map',
      },
      paint: { 'text-color': p.text, 'text-halo-color': halo, 'text-halo-width': 1.5 } },
    { id: 'road-label-major', type: 'symbol', source: src, 'source-layer': 'transportation_name',
      filter: ['match', ['get', 'class'],
        ['primary', 'secondary', 'tertiary', 'trunk', 'motorway'], true, false],
      minzoom: 13,
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': 11,
        'symbol-placement': 'line',
        'text-max-angle': 30,
        'text-rotation-alignment': 'map',
      },
      paint: { 'text-color': p.text, 'text-halo-color': halo, 'text-halo-width': 1.5 } },

    // === Metro/rail/subway stations: from zoom 13 ===
    // Liberty sprite uses underscore names (railway_metro, railway) without size suffix.
    { id: 'poi-metro', type: 'symbol', source: src, 'source-layer': 'poi',
      filter: ['match', ['get', 'class'],
        ['rail', 'railway', 'subway', 'station', 'train_station'], true, false],
      minzoom: 13,
      layout: {
        'icon-image': ['coalesce',
          ['image', 'railway_metro'], ['image', 'railway_metro_11'],
          ['image', 'railway'],       ['image', 'railway_11'],
          ['image', 'railway_light'], ['image', 'railway_light_11'],
        ],
        'icon-size': 0.75,
        'icon-allow-overlap': false,
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': 10,
        'text-anchor': 'top',
        'text-offset': [0, 0.7],
        'text-optional': true,
      },
      paint: {
        'icon-color': '#B9B6CC',
        'icon-opacity': 0.85,
        'text-color': '#8E8AA6',
        'text-halo-color': halo,
        'text-halo-width': 1.5,
      } },

    // === Culture POIs: theatre, museum, attraction (from sprite), from zoom 14 ===
    // Liberty sprite uses underscore names without size suffix (theatre, museum_11).
    { id: 'poi-culture', type: 'symbol', source: src, 'source-layer': 'poi',
      filter: ['match', ['get', 'class'], ['theatre', 'theater', 'museum', 'attraction', 'monument'], true, false],
      minzoom: 14,
      layout: {
        'icon-image': [
          'match', ['get', 'class'],
          'theatre',    ['coalesce', ['image', 'theatre'],    ['image', 'theatre_11']    ],
          'theater',    ['coalesce', ['image', 'theatre'],    ['image', 'theatre_11']    ],
          'museum',     ['coalesce', ['image', 'museum'],     ['image', 'museum_11']     ],
          'monument',   ['coalesce', ['image', 'monument'],   ['image', 'monument_11'],  ['image', 'attraction'], ['image', 'attraction_11'] ],
          /* attraction */ ['coalesce', ['image', 'attraction'], ['image', 'attraction_11'], ['image', 'monument'] ],
        ],
        'icon-size': 0.7,
        'icon-allow-overlap': false,
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': 10,
        'text-anchor': 'top',
        'text-offset': [0, 0.7],
        'text-optional': true,
        'text-max-width': 8,
      },
      paint: {
        'icon-color': '#8E8AA6',
        'icon-opacity': 0.8,
        'text-color': '#8E8AA6',
        'text-halo-color': halo,
        'text-halo-width': 1.5,
      } },
  ]
}

/**
 * Fetches the OpenFreeMap liberty style to reuse its sources / sprite / glyphs,
 * then replaces all layers with our dark style.
 *
 * Root cause of the green Vltava issue (task 025): landcover/wetland was drawn
 * AFTER the water layer, so wetland polygons overlapped and coloured water green.
 * Fix: landcover is now drawn BEFORE water layers (see layer order above).
 */
export async function loadMapStyle(): Promise<object> {
  const resp = await fetch('https://tiles.openfreemap.org/styles/liberty')
  if (!resp.ok) throw new Error('Map style unavailable')
  const style = await resp.json() as {
    sources: Record<string, { type: string }>
    layers: unknown[]
    [k: string]: unknown
  }

  const srcId = Object.keys(style.sources).find(id => style.sources[id].type === 'vector') ?? 'openmaptiles'

  return {
    version: 8,
    name: 'eventapp-dark',
    sources: style.sources,
    sprite: style.sprite,
    glyphs: style.glyphs,
    layers: buildLayers(srcId),
  }
}

/** Kept for backwards compatibility. */
export async function loadDarkMapStyle(): Promise<object> {
  return loadMapStyle()
}
