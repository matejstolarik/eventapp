import { describe, it, expect } from 'vitest'
import { decidePairLabel, COMBINE_MIN_H_OVERLAP, COMBINE_MIN_V_OVERLAP } from './pairLabel'

function rect(left: number, top: number, width: number, height: number) {
  return { left, top, right: left + width, bottom: top + height, width, height }
}

describe('decidePairLabel', () => {
  // Name height ~15px, same row (vOverlap = 100% = fine)
  const lngA = { lng: 14.40, lat: 50.09 }
  const lngB = { lng: 14.42, lat: 50.09 }

  it(`1px touch → both (hOverlap < ${COMBINE_MIN_H_OVERLAP * 100}%)`, () => {
    const rA = rect(0, 100, 100, 15)
    const rB = rect(99, 100, 100, 15) // hOverlap = 1px = 1%
    const result = decidePairLabel(rA, rB, { x: 50, y: 100 }, { x: 149, y: 100 }, lngA, lngB)
    expect(result.action).toBe('both')
  })

  it(`20% horizontal overlap → both (below ${COMBINE_MIN_H_OVERLAP * 100}% threshold)`, () => {
    const rA = rect(0, 100, 100, 15)
    const rB = rect(80, 100, 100, 15) // hOverlap = 20px = 20%
    const result = decidePairLabel(rA, rB, { x: 50, y: 100 }, { x: 130, y: 100 }, lngA, lngB)
    expect(result.action).toBe('both')
  })

  it('60% horizontal overlap side by side → combine west·east', () => {
    const rA = rect(0, 100, 100, 15)
    const rB = rect(40, 100, 100, 15) // hOverlap = 60px = 60%, vOverlap = 100%
    const ptA = { x: 50, y: 100 }
    const ptB = { x: 90, y: 101 } // |dx|=40 ≥ |dy|=1 → west-east
    const llA = { lng: 14.40, lat: 50.09 }
    const llB = { lng: 14.42, lat: 50.09 }
    const result = decidePairLabel(rA, rB, ptA, ptB, llA, llB)
    expect(result.action).toBe('combine')
    if (result.action === 'combine') {
      expect(result.order).toBe('west-east')
      expect(result.midLng).toBeCloseTo((llA.lng + llB.lng) / 2)
      // ptA.y < ptB.y → ptB is lower → lowerLat = llB.lat
      expect(result.lowerLat).toBe(llB.lat)
    }
  })

  it('60% vertical overlap stacked → combine north·south, label below lower pin', () => {
    const rA = rect(0, 100, 100, 15)
    const rB = rect(0, 106, 100, 15) // vOverlap = 9px = 60%, hOverlap = 100%
    const ptA = { x: 50, y: 100 } // A higher (north, smaller y)
    const ptB = { x: 50, y: 110 } // B lower (south, larger y) |dy|=10 > |dx|=0
    const llA = { lng: 14.41, lat: 50.10 }
    const llB = { lng: 14.41, lat: 50.09 }
    const result = decidePairLabel(rA, rB, ptA, ptB, llA, llB)
    expect(result.action).toBe('combine')
    if (result.action === 'combine') {
      expect(result.order).toBe('north-south')
      // ptB.y > ptA.y → B is lower → lowerLat = llB.lat
      expect(result.lowerLat).toBe(llB.lat)
      expect(result.midLng).toBeCloseTo((llA.lng + llB.lng) / 2)
    }
  })

  it(`${COMBINE_MIN_H_OVERLAP * 100}% and ${COMBINE_MIN_V_OVERLAP * 100}% thresholds are exclusive (just below → both)`, () => {
    // Just below 30% h overlap
    const rA = rect(0, 100, 100, 15)
    const rB = rect(71, 100, 100, 15) // hOverlap = 29px = 29%
    const result = decidePairLabel(rA, rB, { x: 50, y: 100 }, { x: 121, y: 100 }, lngA, lngB)
    expect(result.action).toBe('both')
  })
})
