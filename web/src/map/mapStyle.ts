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

function buildDarkLayers(src: string): MapLayer[] {
  return [
    // === Fill ===
    { id: 'bg', type: 'background', paint: { 'background-color': '#191923' } },
    { id: 'earth', type: 'fill', source: src, 'source-layer': 'earth',
      paint: { 'fill-color': '#191923' } },
    { id: 'water', type: 'fill', source: src, 'source-layer': 'water',
      paint: { 'fill-color': '#1D3352' } },
    { id: 'natural', type: 'fill', source: src, 'source-layer': 'natural',
      filter: ['match', ['get', 'pmap:kind'],
        ['park', 'national_park', 'forest', 'grass', 'scrub', 'wetland', 'farmland'], true, false],
      paint: { 'fill-color': '#1B2A22' } },
    { id: 'landuse', type: 'fill', source: src, 'source-layer': 'landuse',
      paint: { 'fill-color': '#1D1D27', 'fill-opacity': 0.4 } },
    { id: 'buildings', type: 'fill', source: src, 'source-layer': 'buildings', minzoom: 14,
      paint: { 'fill-color': '#21212D', 'fill-outline-color': '#1A1A28' } },

    // === Roads ===
    { id: 'road-path', type: 'line', source: src, 'source-layer': 'roads',
      filter: ['match', ['get', 'pmap:kind'], ['path', 'track', 'pedestrian'], true, false],
      paint: { 'line-color': '#252535',
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.6, 16, 1.5] } },
    { id: 'road-service', type: 'line', source: src, 'source-layer': 'roads',
      filter: ['==', ['get', 'pmap:kind'], 'service'],
      paint: { 'line-color': '#252535',
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.8, 16, 2] } },
    { id: 'road-minor', type: 'line', source: src, 'source-layer': 'roads',
      filter: ['==', ['get', 'pmap:kind'], 'minor_road'],
      paint: { 'line-color': '#2C2C3B',
        'line-width': ['interpolate', ['linear'], ['zoom'], 12, 1, 15, 3] } },
    { id: 'road-medium', type: 'line', source: src, 'source-layer': 'roads',
      filter: ['==', ['get', 'pmap:kind'], 'medium_road'],
      paint: { 'line-color': '#3D3D52',
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1, 14, 4, 16, 6] } },
    { id: 'road-major', type: 'line', source: src, 'source-layer': 'roads',
      filter: ['==', ['get', 'pmap:kind'], 'major_road'],
      paint: { 'line-color': '#4A4A63',
        'line-width': ['interpolate', ['linear'], ['zoom'], 8, 1, 12, 3, 16, 7] } },
    { id: 'road-highway', type: 'line', source: src, 'source-layer': 'roads',
      filter: ['==', ['get', 'pmap:kind'], 'highway'],
      paint: { 'line-color': '#4A4A63',
        'line-width': ['interpolate', ['linear'], ['zoom'], 6, 1.5, 12, 4, 16, 9] } },

    // === Transit ===
    { id: 'transit-rail', type: 'line', source: src, 'source-layer': 'transit',
      filter: ['match', ['get', 'pmap:kind'], ['rail', 'subway', 'light_rail'], true, false],
      paint: { 'line-color': '#33334A', 'line-width': 1.5,
        'line-dasharray': [4, 2] } },
    { id: 'transit-tram', type: 'line', source: src, 'source-layer': 'transit',
      filter: ['==', ['get', 'pmap:kind'], 'tram'],
      paint: { 'line-color': '#2D2D44', 'line-width': 1 } },

    // === Labels ===
    { id: 'water-label', type: 'symbol', source: src, 'source-layer': 'water_labels',
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Italic'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 10, 11, 14, 14],
        'text-max-width': 10,
      },
      paint: { 'text-color': '#5A6E8A', 'text-halo-color': '#111118', 'text-halo-width': 1.5 } },

    { id: 'natural-label', type: 'symbol', source: src, 'source-layer': 'natural_labels',
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 15, 13],
        'text-max-width': 8,
      },
      paint: { 'text-color': '#6B8A6B', 'text-halo-color': '#111118', 'text-halo-width': 1.5 } },

    { id: 'place-neighbourhood', type: 'symbol', source: src, 'source-layer': 'places',
      filter: ['match', ['get', 'pmap:kind'],
        ['neighbourhood', 'suburb', 'quarter', 'city_block'], true, false],
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 12, 9, 15, 12],
        'text-max-width': 6,
        'text-transform': 'uppercase',
        'text-letter-spacing': 0.1,
      },
      paint: { 'text-color': '#8E8AA6', 'text-halo-color': '#111118', 'text-halo-width': 1.5 } },

    { id: 'place-town', type: 'symbol', source: src, 'source-layer': 'places',
      filter: ['match', ['get', 'pmap:kind'], ['city', 'town'], true, false],
      maxzoom: 13,
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Bold'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 8, 12, 12, 16],
      },
      paint: { 'text-color': '#B9B6CC', 'text-halo-color': '#111118', 'text-halo-width': 2 } },

    { id: 'road-label', type: 'symbol', source: src, 'source-layer': 'roads_labels',
      minzoom: 14,
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': 11,
        'symbol-placement': 'line',
        'text-max-angle': 30,
      },
      paint: { 'text-color': '#8E8AA6', 'text-halo-color': '#111118', 'text-halo-width': 1.5 } },

    { id: 'metro-dot', type: 'circle', source: src, 'source-layer': 'transit_stops',
      filter: ['match', ['get', 'pmap:kind'],
        ['station', 'subway_entrance', 'stop'], true, false],
      minzoom: 12,
      paint: {
        'circle-color': '#3A3A58',
        'circle-radius': 4,
        'circle-stroke-color': '#5A5A78',
        'circle-stroke-width': 1,
      } },

    { id: 'metro-label', type: 'symbol', source: src, 'source-layer': 'transit_stops',
      filter: ['match', ['get', 'pmap:kind'],
        ['station', 'subway_entrance', 'stop'], true, false],
      minzoom: 12,
      layout: {
        'text-field': ['coalesce', ['get', 'name:cs'], ['get', 'name']],
        'text-font': ['Noto Sans Regular'],
        'text-size': 10,
        'text-anchor': 'top',
        'text-offset': [0, 0.6],
      },
      paint: { 'text-color': '#8E8AA6', 'text-halo-color': '#111118', 'text-halo-width': 1.5 } },
  ]
}

/** Fetches the OpenFreeMap liberty style to reuse its sources/sprite/glyphs,
 * then replaces the layers with a hand-built dark style. */
export async function loadDarkMapStyle(): Promise<object> {
  const resp = await fetch('https://tiles.openfreemap.org/styles/liberty')
  if (!resp.ok) throw new Error('Map style unavailable')
  const style = await resp.json() as {
    sources: Record<string, { type: string }>
    layers: unknown[]
    [k: string]: unknown
  }

  // Find the vector tile source ID (usually 'openmaptiles')
  const srcId = Object.keys(style.sources).find(id => style.sources[id].type === 'vector') ?? 'openmaptiles'

  return {
    version: 8,
    name: 'eventapp-dark',
    sources: style.sources,
    sprite: style.sprite,
    glyphs: style.glyphs,
    layers: buildDarkLayers(srcId),
  }
}
