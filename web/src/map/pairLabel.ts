export const COMBINE_MIN_H_OVERLAP = 0.30
export const COMBINE_MIN_V_OVERLAP = 0.50

export interface Rect {
  left: number; right: number; top: number; bottom: number; width: number; height: number
}
export interface Point { x: number; y: number }
export interface LngLat { lng: number; lat: number }

export type PairDecision =
  | { action: 'both' }
  | { action: 'combine'; order: 'west-east' | 'north-south'; midLng: number; lowerLat: number }

/** Decide whether two overlapping pair-name rects should merge into one label.
 *  Combine only when horizontal overlap ≥ 30 % of shorter name AND vertical ≥ 50 %.
 *  Returns the combined label's midpoint lng and the lower pin's lat. */
export function decidePairLabel(
  rA: Rect, rB: Rect,
  ptA: Point, ptB: Point,
  llA: LngLat, llB: LngLat,
): PairDecision {
  const hOverlap = Math.min(rA.right, rB.right) - Math.max(rA.left, rB.left)
  const vOverlap = Math.min(rA.bottom, rB.bottom) - Math.max(rA.top, rB.top)
  if (hOverlap <= 0 || vOverlap <= 0) return { action: 'both' }
  const minWidth = Math.min(rA.width, rB.width)
  const minHeight = Math.min(rA.height, rB.height)
  if (hOverlap / minWidth < COMBINE_MIN_H_OVERLAP || vOverlap / minHeight < COMBINE_MIN_V_OVERLAP) {
    return { action: 'both' }
  }
  const dx = ptB.x - ptA.x
  const dy = ptB.y - ptA.y
  const order: 'west-east' | 'north-south' = Math.abs(dx) >= Math.abs(dy) ? 'west-east' : 'north-south'
  const midLng = (llA.lng + llB.lng) / 2
  const lowerLat = ptA.y >= ptB.y ? llA.lat : llB.lat
  return { action: 'combine', order, midLng, lowerLat }
}
