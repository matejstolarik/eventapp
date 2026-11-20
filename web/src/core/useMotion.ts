import { useEffect, useRef, useState } from 'react'
import { motionOn, type MotionKey } from './motion'

/** Counter that grows each time `value` changes after mount (and `when(prev, next)`
 * holds) while the animation `key` is on. Use it as a React `key` to replay a CSS
 * animation; 0 = never changed (no animation on first render). Task 081. */
export function useChangeKey<T>(value: T, key: MotionKey, when: (prev: T, next: T) => boolean = () => true): number {
  const [n, setN] = useState(0)
  const prev = useRef(value)
  useEffect(() => {
    if (Object.is(prev.current, value)) return
    const p = prev.current
    prev.current = value
    if (when(p, value) && motionOn(key)) setN(k => k + 1)
  }, [value]) // eslint-disable-line react-hooks/exhaustive-deps
  return n
}
