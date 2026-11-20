import { useLayoutEffect, useRef, useState } from 'react'
import { motionOn } from '../core/motion'

/** Text that slides in from below when it changes, the old one leaves upwards
 * (~200 ms, task 081: Akcie count line). The new text is rendered at once. */
export function SlideText({ text }: { text: string }) {
  const [anim, setAnim] = useState<{ old: string | null; n: number }>({ old: null, n: 0 })
  const prev = useRef(text)
  useLayoutEffect(() => {
    if (prev.current === text) return
    const old = prev.current
    prev.current = text
    if (!motionOn('countSlide')) return
    setAnim(a => ({ old, n: a.n + 1 }))
    const id = setTimeout(() => setAnim(a => ({ ...a, old: null })), 220)
    return () => clearTimeout(id)
  }, [text])
  return (
    <span style={{ position: 'relative', display: 'inline-block', overflow: 'hidden', verticalAlign: 'bottom', whiteSpace: 'nowrap' }}>
      {anim.old !== null && <span key={`o${anim.n}`} className="m-count-out" aria-hidden="true">{anim.old}</span>}
      <span key={anim.n} className={anim.n > 0 ? 'm-count-in' : undefined}>{text}</span>
    </span>
  )
}
