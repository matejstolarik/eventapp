/** Fetches the OpenFreeMap liberty style and transforms it to a dark theme
 * matching the app's color palette. POI icons and noisy labels are removed. */
export async function loadDarkMapStyle(): Promise<object> {
  const resp = await fetch('https://tiles.openfreemap.org/styles/liberty')
  if (!resp.ok) throw new Error('Map style unavailable')
  const style = await resp.json() as { layers: MapLayer[]; [k: string]: unknown }
  return applyDarkTheme(style)
}

interface MapLayer {
  id: string
  type: string
  paint?: Record<string, unknown>
  layout?: Record<string, unknown>
  [k: string]: unknown
}

const COLOR_MAP: [RegExp, string][] = [
  // Background and land
  [/#f8f4f0/gi, '#14141D'],
  [/#f5f1ec/gi, '#14141D'],
  [/#f0ebe4/gi, '#14141D'],
  [/#ede9e4/gi, '#14141D'],
  [/#e8e0d8/gi, '#181822'],
  [/#e0d8d0/gi, '#1C1C27'],
  [/#d8d0c8/gi, '#1C1C27'],
  [/#ccc4bc/gi, '#1C1C27'],
  // Water
  [/#a0c8f0/gi, '#1E2A44'],
  [/#a8d0f8/gi, '#1E2A44'],
  [/#b8d8f8/gi, '#1E2A44'],
  [/#c0d8f8/gi, '#1E2A44'],
  [/#7ab0e0/gi, '#1A2640'],
  [/#6898c8/gi, '#162035'],
  // Parks / greenery
  [/#c8e0b8/gi, '#17261F'],
  [/#d0e8c0/gi, '#17261F'],
  [/#b8d8a8/gi, '#152219'],
  [/#c0d8b0/gi, '#17261F'],
  [/#a8c898/gi, '#112018'],
  // Roads
  [/#f0e8e0/gi, '#22222E'],
  [/#e8e0d8/gi, '#22222E'],
  [/#d8d0c8/gi, '#1A1A25'],
  [/#c0b8b0/gi, '#1E1E2A'],
  [/#b8b0a8/gi, '#1A1A25'],
  [/#f8f8f0/gi, '#22222E'],
  // Buildings
  [/#e0d4c8/gi, '#1C1C28'],
  [/#d8ccc0/gi, '#1C1C28'],
  // Text and boundaries
  [/#987878/gi, '#5A4466'],
  [/#888080/gi, '#4A4460'],
  [/#706868/gi, '#3A3450'],
]

const POI_LAYER_PATTERNS = [
  /poi/i, /shop/i, /restaurant/i, /cafe/i, /hotel/i, /hospital/i,
  /pharmacy/i, /station/i, /icon/i, /symbol/i, /aeroway/i,
  /barrier/i, /pitch/i, /landuse-/i,
]

function isPOILayer(layer: MapLayer): boolean {
  return POI_LAYER_PATTERNS.some(p => p.test(layer.id))
}

function transformColors(str: string): string {
  let result = str
  for (const [from, to] of COLOR_MAP) {
    result = result.replace(from, to)
  }
  return result
}

function applyDarkTheme(style: { layers: MapLayer[]; [k: string]: unknown }): object {
  // Stringify → replace colors → parse back
  let styleStr = JSON.stringify(style)
  styleStr = transformColors(styleStr)
  const dark = JSON.parse(styleStr) as { layers: MapLayer[]; [k: string]: unknown }

  // Remove POI / icon layers, keep road/water/land/label layers
  dark.layers = dark.layers.filter(layer => !isPOILayer(layer))

  return dark
}
