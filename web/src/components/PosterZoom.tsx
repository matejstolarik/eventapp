// Task 072: full-screen poster with pinch zoom (up to 4x), double tap 1x / 2.5x
// at the tap point and pan when zoomed. The image never leaves the screen edges.
// Plain pointer events, no library.
import { useEffect, useRef, type PointerEvent as RPointerEvent } from 'react'

const MAX_SCALE = 4
const TAP_SCALE = 2.5
const DOUBLE_TAP_MS = 300
const TAP_SLOP = 10

interface Pt { x: number; y: number }

export function PosterZoom({ src, alt }: { src: string; alt: string }) {
  const boxRef = useRef<HTMLDivElement>(null)
  const imgRef = useRef<HTMLImageElement>(null)
  const st = useRef({ s: 1, tx: 0, ty: 0, dw: 0, dh: 0, W: 0, H: 0 })
  const pointers = useRef(new Map<number, Pt>())
  const gesture = useRef<{ s0: number; tx0: number; ty0: number; d0: number; m0: Pt; moved: boolean; start: Pt } | null>(null)
  const lastTap = useRef<{ t: number; p: Pt } | null>(null)

  function apply(animate: boolean) {
    const img = imgRef.current
    if (!img) return
    const { s, tx, ty } = st.current
    img.style.transition = animate ? 'transform 200ms ease-out' : 'none'
    img.style.transform = `translate(${tx}px, ${ty}px) scale(${s})`
  }

  function clamp() {
    const c = st.current
    const mx = Math.max(0, (c.dw * c.s - c.W) / 2)
    const my = Math.max(0, (c.dh * c.s - c.H) / 2)
    c.tx = Math.min(mx, Math.max(-mx, c.tx))
    c.ty = Math.min(my, Math.max(-my, c.ty))
  }

  // contain size of the image in the box (the 1x view)
  function layout() {
    const box = boxRef.current, img = imgRef.current
    if (!box || !img || !img.naturalWidth) return
    const c = st.current
    c.W = box.clientWidth; c.H = box.clientHeight
    const r = img.naturalWidth / img.naturalHeight
    c.dw = Math.min(c.W, c.H * r); c.dh = c.dw / r
    img.style.width = `${c.dw}px`; img.style.height = `${c.dh}px`
    clamp(); apply(false)
  }

  useEffect(() => {
    window.addEventListener('resize', layout)
    return () => window.removeEventListener('resize', layout)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  /** pointer position relative to the box centre */
  function rel(e: RPointerEvent): Pt {
    const r = boxRef.current!.getBoundingClientRect()
    return { x: e.clientX - r.left - r.width / 2, y: e.clientY - r.top - r.height / 2 }
  }

  function startGesture() {
    const pts = [...pointers.current.values()]
    const c = st.current
    const m0 = pts.length >= 2 ? { x: (pts[0].x + pts[1].x) / 2, y: (pts[0].y + pts[1].y) / 2 } : pts[0]
    const d0 = pts.length >= 2 ? Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y) : 0
    const prev = gesture.current
    gesture.current = { s0: c.s, tx0: c.tx, ty0: c.ty, d0, m0, moved: prev?.moved ?? false, start: prev?.start ?? m0 }
  }

  /** zoom to scale s keeping the image point under p in place */
  function zoomAt(p: Pt, s: number, s0: number, tx0: number, ty0: number) {
    const c = st.current
    c.s = Math.min(MAX_SCALE, Math.max(1, s))
    c.tx = p.x - (p.x - tx0) * c.s / s0
    c.ty = p.y - (p.y - ty0) * c.s / s0
  }

  function onPointerDown(e: RPointerEvent) {
    e.currentTarget.setPointerCapture(e.pointerId)
    if (pointers.current.size === 0) gesture.current = null
    pointers.current.set(e.pointerId, rel(e))
    if (pointers.current.size >= 2 && gesture.current) gesture.current.moved = true
    startGesture()
  }

  function onPointerMove(e: RPointerEvent) {
    if (!pointers.current.has(e.pointerId) || !gesture.current) return
    const p = rel(e)
    pointers.current.set(e.pointerId, p)
    const g = gesture.current
    const pts = [...pointers.current.values()]
    if (Math.hypot(p.x - g.start.x, p.y - g.start.y) > TAP_SLOP) g.moved = true
    const c = st.current
    if (pts.length >= 2 && g.d0 > 0) {
      const m = { x: (pts[0].x + pts[1].x) / 2, y: (pts[0].y + pts[1].y) / 2 }
      const d = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y)
      zoomAt(g.m0, g.s0 * d / g.d0, g.s0, g.tx0, g.ty0)
      c.tx += m.x - g.m0.x; c.ty += m.y - g.m0.y
    } else if (pts.length === 1 && c.s > 1) {
      c.tx = g.tx0 + p.x - g.m0.x; c.ty = g.ty0 + p.y - g.m0.y
    } else return
    clamp(); apply(false)
  }

  function onPointerUp(e: RPointerEvent) {
    if (!pointers.current.has(e.pointerId)) return
    const p = rel(e)
    pointers.current.delete(e.pointerId)
    const g = gesture.current
    if (pointers.current.size > 0) { startGesture(); return }
    if (!g || g.moved || e.type === 'pointercancel') { lastTap.current = null; return }
    const now = e.timeStamp
    const prev = lastTap.current
    if (prev && now - prev.t < DOUBLE_TAP_MS && Math.hypot(p.x - prev.p.x, p.y - prev.p.y) < 40) {
      lastTap.current = null
      const c = st.current
      if (c.s > 1) { c.s = 1; c.tx = 0; c.ty = 0 }
      else zoomAt(p, TAP_SCALE, c.s, c.tx, c.ty)
      clamp(); apply(true)
    } else {
      lastTap.current = { t: now, p }
    }
  }

  return (
    <div
      ref={boxRef}
      style={{ position: 'absolute', inset: 0, overflow: 'hidden', touchAction: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      onPointerDown={onPointerDown} onPointerMove={onPointerMove}
      onPointerUp={onPointerUp} onPointerCancel={onPointerUp}
    >
      <img
        ref={imgRef} src={src} alt={alt} draggable={false} onLoad={layout}
        style={{ flex: 'none', maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', transformOrigin: 'center', userSelect: 'none', WebkitUserSelect: 'none' }}
      />
    </div>
  )
}
