import { useLayoutEffect, useRef } from 'react'
import type { Language } from '../core/types'
import { motionOn, play } from '../core/motion'
import { getDict } from '../i18n'
import { IconMap, IconList, IconBuilding, IconPerson } from '../icons'

export type Tab = 'map' | 'events' | 'places' | 'account'

/** Task 079: Akcie first (design.md 1). */
export const TAB_ORDER: Tab[] = ['events', 'map', 'places', 'account']

interface Props {
  active: Tab
  lang: Language
  onChange: (tab: Tab) => void
}

export function BottomNav({ active, lang, onChange }: Props) {
  const dict = getDict(lang)

  const all: { id: Tab; label: string; Icon: React.FC<{ size?: number; color?: string }> }[] = [
    { id: 'events', label: dict.nav.events, Icon: IconList },
    { id: 'map', label: dict.nav.map, Icon: IconMap },
    { id: 'places', label: dict.nav.places, Icon: IconBuilding },
    { id: 'account', label: dict.nav.account, Icon: IconPerson }
  ]
  const tabs = TAB_ORDER.map(id => all.find(t => t.id === id)!)

  // Task 081: the pink pill is one element behind the buttons; on a tab change it
  // moves with transform only (FLIP: translate + scaleX), the new icon pops.
  // Without motion it is placed at once (same look as before).
  const btnRefs = useRef<Partial<Record<Tab, HTMLButtonElement | null>>>({})
  const iconRefs = useRef<Partial<Record<Tab, HTMLSpanElement | null>>>({})
  const labelRefs = useRef<Partial<Record<Tab, HTMLSpanElement | null>>>({})
  const pillRef = useRef<HTMLDivElement>(null)
  const placedRef = useRef<{ left: number; width: number } | null>(null)
  const activeRef = useRef(active)
  activeRef.current = active

  function placePill(animate: boolean) {
    const pill = pillRef.current
    const btn = btnRefs.current[activeRef.current]
    if (!pill || !btn) return
    const left = btn.offsetLeft
    const width = btn.offsetWidth
    const prev = placedRef.current
    // Same place (e.g. the ResizeObserver firing right after a tab change):
    // leave a running move alone, otherwise it would jump to the end at once.
    if (!animate && prev && prev.left === left && prev.width === width) return
    placedRef.current = { left, width }
    pill.style.width = `${width}px`
    if (animate && prev && width > 0 && (prev.left !== left || prev.width !== width)) {
      pill.style.transition = 'none'
      pill.style.transform = `translate3d(${prev.left}px, 0, 0) scaleX(${prev.width / width})`
      void pill.offsetWidth // commit the start position
      pill.style.transition = 'transform 220ms cubic-bezier(.2,.8,.2,1)'
    } else {
      pill.style.transition = 'none'
    }
    pill.style.transform = `translate3d(${left}px, 0, 0)`
  }

  const firstRef = useRef(true)
  useLayoutEffect(() => {
    const first = firstRef.current
    firstRef.current = false
    const animate = !first && motionOn('navPill')
    placePill(animate)
    if (animate) {
      play('navPill', iconRefs.current[active], [
        { transform: 'scale(1)' }, { transform: 'scale(1.25)' }, { transform: 'scale(1)' },
      ], { duration: 250, easing: 'cubic-bezier(.3,.7,.4,1)' })
      play('navPill', labelRefs.current[active], [{ opacity: 0 }, { opacity: 1 }], { duration: 200, easing: 'ease-out' })
    }
  }, [active]) // eslint-disable-line react-hooks/exhaustive-deps

  // Re-place without animation when sizes change (fonts loaded, rotation)
  useLayoutEffect(() => {
    if (typeof ResizeObserver === 'undefined') return
    const ro = new ResizeObserver(() => placePill(false))
    Object.values(btnRefs.current).forEach(b => { if (b) ro.observe(b) })
    return () => ro.disconnect()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <nav
      style={{
        position: 'absolute', left: 16, right: 16, bottom: 28,
        height: 72, borderRadius: 36, background: '#1C1C27',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 10px', zIndex: 100,
        boxShadow: '0 4px 24px rgba(0,0,0,0.4)'
      }}
      aria-label="Hlavná navigácia"
    >
      <div ref={pillRef} aria-hidden="true" data-testid="nav-pill" style={{
        position: 'absolute', left: 0, top: 10, height: 52, width: 0, borderRadius: 26,
        background: '#FF4D8D', transformOrigin: '0 50%', pointerEvents: 'none', zIndex: 0,
      }} />
      {tabs.map(({ id, label, Icon }) => {
        const isActive = active === id
        return (
          <button
            key={id}
            ref={el => { btnRefs.current[id] = el }}
            style={{
              position: 'relative', zIndex: 1,
              height: 52, borderRadius: 26, background: 'transparent',
              ...(isActive
                ? { padding: '0 20px', color: '#1A0710' }
                : { width: 52, padding: 0, color: '#B9B6CC' }),
              display: 'flex', alignItems: 'center',
              justifyContent: 'center', gap: isActive ? 8 : 0,
              fontSize: 15, fontWeight: 600,
              WebkitTapHighlightColor: 'transparent',
              border: 'none', cursor: 'pointer',
            }}
            onClick={() => onChange(id)}
            aria-current={isActive ? 'page' : undefined}
            aria-label={label}
          >
            <span ref={el => { iconRefs.current[id] = el }} style={{ display: 'flex' }}>
              <Icon size={isActive ? 20 : 22} color={isActive ? '#1A0710' : '#B9B6CC'} />
            </span>
            {isActive && <span ref={el => { labelRefs.current[id] = el }}>{label}</span>}
          </button>
        )
      })}
    </nav>
  )
}
