export type MapVariant = 'a' | 'b' | 'c'

interface Palette {
  bg: string
  water: string
  park: string
  building: string
  roadMinor: string
  roadMajor: string
  roadHighway: string
  text: string
}

/** Three basemap palettes. Colors per task 025 spec, fine-tuned for readability. */
const PALETTES: Record<MapVariant, Palette> = {
  a: {
    bg:         '#1E1E2A',
    water:      '#1D3352',
    park:       '#1C2E24',
    building:   '#252532',
    roadMinor:  '#34344A',
    roadMajor:  '#4A4A66',
    roadHighway:'#5E5E7E',
    text:       '#B4B0CC',
  },
  b: {
    bg:         '#1B2230',
    water:      '#0E1828',
    park:       '#1A2A2A',
    building:   '#222B3A',
    roadMinor:  '#2D3A4F',
    roadMajor:  '#3F5070',
    roadHighway:'#526688',
    text:       '#A4B3CC',
  },
  c: {
    bg:         '#2A2A36',
    water:      '#22406A',
    park:       '#26392C',
    building:   '#32323F',
    roadMinor:  '#45455A',
    roadMajor:  '#5C5C78',
    roadHighway:'#727294',
    text:       '#D0CCE2',
  },
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

function buildLayers(src: string, p: Palette): MapLayer[] {
  const halo = p.bg  // text halo uses background colour for maximum contrast
  return [
    // === Fill ===
    { id: 'bg', type: 'background',
      paint: { 'background-color': p.bg } },
    { id: 'water', type: 'fill', source: src, 'source-layer': 'water',
      paint: { 'fill-color': p.water } },
    { id: 'waterway', type: 'line', source: src, 'source-layer': 'waterway',
      paint: { 'line-color': p.water,
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1, 14, 3] } },
    { id: 'park', type: 'fill', source: src, 'source-layer': 'park',
      paint: { 'fill-color': p.park } },
    { id: 'landcover', type: 'fill', source: src, 'source-layer': 'landcover',
      filter: ['match', ['get', 'class'],
        ['grass', 'wood', 'forest', 'scrub', 'wetland', 'farmland'], true, false],
      paint: { 'fill-color': p.park, 'fill-opacity': 0.55 } },
    { id: 'landuse', type: 'fill', source: src, 'source-layer': 'landuse',
      paint: { 'fill-color': p.bg, 'fill-opacity': 0.4 } },
    { id: 'building', type: 'fill', source: src, 'source-layer': 'building', minzoom: 14,
      paint: { 'fill-color': p.building, 'fill-outline-color': p.bg } },

    // === Roads – minor (service, track, path) ===
    { id: 'road-path', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['path', 'track', 'pedestrian'], true, false],
      paint: { 'line-color': p.roadMinor,
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.5, 16, 1.5] } },
    { id: 'road-service', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['==', ['get', 'class'], 'service'],
      paint: { 'line-color': p.roadMinor,
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.8, 16, 2.5] } },

    // === Roads – minor (residential / minor) ===
    { id: 'road-minor', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['minor', 'street', 'street_limited'], true, false],
      paint: { 'line-color': p.roadMinor,
        'line-width': ['interpolate', ['linear'], ['zoom'], 12, 1.2, 15, 4] } },

    // === Roads – secondary / tertiary ===
    { id: 'road-secondary', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['secondary', 'tertiary'], true, false],
      paint: { 'line-color': p.roadMajor,
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.5, 14, 5.5, 16, 9] } },

    // === Roads – primary / trunk ===
    { id: 'road-major', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['primary', 'trunk'], true, false],
      paint: { 'line-color': p.roadHighway,
        'line-width': ['interpolate', ['linear'], ['zoom'], 8, 1.5, 12, 4, 16, 10] } },

    // === Roads – motorway ===
    { id: 'road-highway', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['==', ['get', 'class'], 'motorway'],
      paint: { 'line-color': p.roadHighway,
        'line-width': ['interpolate', ['linear'], ['zoom'], 6, 2, 12, 5, 16, 11] } },

    // === Transit lines (rail, subway) ===
    { id: 'transit-rail', type: 'line', source: src, 'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['rail', 'transit'], true, false],
      paint: { 'line-color': p.roadMajor, 'line-width': 1.5,
        'line-dasharray': [4, 2] } },

    // === Water labels – points (lakes) ===
    { id: 'water-label-point', type: 'symbol', source: src, 'source-layer': 'water_name',
      filter: ['match', ['geometry-type'], ['Point', 'MultiPoint'], true, false],
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Italic'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 10, 11, 14, 14],
        'text-max-width': 10,
      },
      paint: { 'text-color': '#5A6E8A', 'text-halo-color': halo, 'text-halo-width': 1.5 } },

    // === Water labels – lines (rivers, Vltava) ===
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

    // === Place: neighbourhoods / suburbs / quarters (from zoom 11) ===
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

    // === Place: cities / towns ===
    { id: 'place-town', type: 'symbol', source: src, 'source-layer': 'place',
      filter: ['match', ['get', 'class'], ['city', 'town'], true, false],
      maxzoom: 13,
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Bold'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 8, 12, 12, 16],
      },
      paint: { 'text-color': p.text, 'text-halo-color': halo, 'text-halo-width': 2 } },

    // === Road labels – minor streets (from zoom 15) ===
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

    // === Road labels – major roads (from zoom 13) ===
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

    // === Metro / rail stations: dot ===
    { id: 'metro-dot', type: 'circle', source: src, 'source-layer': 'poi',
      filter: ['==', ['get', 'class'], 'rail'],
      minzoom: 12,
      paint: {
        'circle-color': p.roadMajor,
        'circle-radius': 4,
        'circle-stroke-color': p.text,
        'circle-stroke-width': 1.2,
      } },

    // === Metro / rail stations: label ===
    { id: 'metro-label', type: 'symbol', source: src, 'source-layer': 'poi',
      filter: ['==', ['get', 'class'], 'rail'],
      minzoom: 12,
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': 10,
        'text-anchor': 'top',
        'text-offset': [0, 0.6],
      },
      paint: { 'text-color': p.text, 'text-halo-color': halo, 'text-halo-width': 1.5 } },
  ]
}

/**
 * Fetches the OpenFreeMap liberty style to reuse its sources / sprite / glyphs,
 * then replaces all layers with a hand-built dark style in the requested variant.
 *
 * Root cause of missing labels in 024: source-layer names were from the Protomaps
 * schema (roads, buildings, places, roads_labels, transit_stops) but OpenFreeMap uses
 * the OpenMapTiles schema (transportation, building, place, transportation_name, poi).
 * Attribute names were also wrong: pmap:kind → class.
 */
export async function loadMapStyle(variant: MapVariant = 'a'): Promise<object> {
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
    name: `eventapp-${variant}`,
    sources: style.sources,
    sprite: style.sprite,
    glyphs: style.glyphs,
    layers: buildLayers(srcId, PALETTES[variant]),
  }
}

/** Kept for backwards compatibility – loads variant A. */
export async function loadDarkMapStyle(): Promise<object> {
  return loadMapStyle('a')
}
