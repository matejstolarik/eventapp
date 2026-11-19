import { useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import type { Event, Language, Venue } from '../core/types'
import { getDict, tagLabel } from '../i18n'
import { typeIconSvg } from '../map/markers'
import { EVENT_TYPE_COLOR, EVENT_TYPE_DARK, CULTURE_SUBTYPES, subtypeIconKey, type EventIconKey } from '../core/eventType'
import {
  FILTER_TYPES, VENUE_SIZES, DEFAULT_FILTER, filterCounts, availableGenres, availableCharacters,
  availableCultureGenres, cultureGenreName, orderByCount, toggleType, toggleIn, type EventFilter, type FilterItem, type CountMode, type FilterType,
} from '../core/filter'

// Filter panel from the bottom (docs/design.md 7b, 09-filter.html; task 075).

const VISIBLE_GENRES = 12
const ANIM_MS = 220
const TYPE_ICON: Record<FilterType, EventIconKey> = { concert: 'concert', party: 'party', dj: 'dj', culture: 'culture' }

interface Props {
  lang: Language
  /** 'venues' on the map (counts places), 'events' in Akcie */
  mode: CountMode
  /** Current results before the filter (day/period, favourites, Pre teba, Nové, search) */
  items: FilterItem[]
  /** All loaded events and venues: which genre / character chips exist */
  allEvents: Event[]
  venues: Venue[]
  filter: EventFilter
  onChange: (f: EventFilter) => void
  onClose: () => void
}

function prefersReducedMotion(): boolean {
  try { return window.matchMedia('(prefers-reduced-motion: reduce)').matches } catch { return false }
}

function Count({ n, on, dark }: { n: number; on: boolean; dark?: string }) {
  return (
    <span style={{
      minWidth: 18, height: 18, padding: '0 5px', boxSizing: 'border-box', borderRadius: 9,
      background: on ? (dark ?? '#111118') : '#3A3A50', color: on ? '#F4F2FF' : '#E4E2EE',
      fontSize: 11, fontWeight: 700, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginLeft: 2,
    }}>{n}</span>
  )
}

function Icon({ k, color, bg, size = 18 }: { k: EventIconKey; color: string; bg: string; size?: number }) {
  return <span style={{ display: 'flex', width: size, height: size, lineHeight: 0, flex: 'none' }}
    dangerouslySetInnerHTML={{ __html: typeIconSvg(k, color, size, bg) }} />
}

function NeutralChip({ label, n, on, icon, onClick }: {
  label: string; n: number; on: boolean; icon?: EventIconKey; onClick: () => void
}) {
  const bg = on ? '#F4F2FF' : '#2A2838'
  return (
    <button onClick={onClick} aria-pressed={on} style={{
      height: 34, padding: icon ? '0 9px 0 10px' : '0 9px 0 13px', borderRadius: 17,
      background: bg, color: on ? '#111118' : '#E4DEFF', border: `1.5px solid ${bg}`,
      fontWeight: on ? 700 : 500, opacity: n === 0 ? 0.45 : 1,
      fontFamily: "'Outfit', sans-serif", fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 6,
      cursor: 'pointer', whiteSpace: 'nowrap',
    }}>
      {icon && <Icon k={icon} color={on ? '#111118' : EVENT_TYPE_COLOR.culture} bg={bg} size={16} />}
      {label}<Count n={n} on={on} />
    </button>
  )
}

function Section({ title, right, children }: { title: string; right?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', alignItems: 'baseline' }}>
        <p style={{ margin: 0, fontSize: 13, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#8E8AA6' }}>{title}</p>
        {right}
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>{children}</div>
    </div>
  )
}

const HELP_ORDER: FilterType[] = ['concert', 'dj', 'party', 'culture']

/** "?" next to TYP AKCIE (task 077): outline circle, #8E8AA6, text-sized, 44 px tap area. */
function HelpButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button onClick={onClick} aria-label={label} data-testid="filter-type-help" style={{
      width: 44, height: 44, margin: '-15px 0 -15px -8px', padding: 0, border: 0, background: 'transparent',
      display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', alignSelf: 'center',
    }}>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#8E8AA6" strokeWidth="2.2"
        strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10" />
        <path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3" />
        <path d="M12 17h.01" />
      </svg>
    </button>
  )
}

/** Card explaining the event types, above the filter panel (task 077). */
function TypeHelpCard({ lang, reduced, closing, onDismiss }: {
  lang: Language; reduced: boolean; closing: boolean; onDismiss: () => void
}) {
  const t = getDict(lang).filter
  const [shown, setShown] = useState(reduced)
  useEffect(() => {
    if (reduced) return
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setShown(true)))
    return () => cancelAnimationFrame(id)
  }, [reduced])
  const open = shown && !closing
  const tr = (p: string) => reduced ? 'none' : `${p} ${ANIM_MS}ms cubic-bezier(.2,.8,.2,1)`
  return (
    <>
      <div onClick={onDismiss} style={{
        position: 'fixed', inset: 0, zIndex: 103, background: 'rgba(8,8,12,0.5)',
        opacity: open ? 1 : 0, transition: tr('opacity'),
      }} />
      <div role="dialog" aria-label={t.typeHelpLabel} data-testid="filter-type-help-card" style={{
        position: 'fixed', left: 16, right: 16, top: '50%', zIndex: 104, maxWidth: 420, margin: '0 auto',
        maxHeight: 'calc(100% - 48px)', overflowY: 'auto', boxSizing: 'border-box',
        background: '#1C1C27', border: '1px solid #2E2D3C', borderRadius: 16,
        padding: '14px 16px 16px', fontFamily: "'Outfit', sans-serif", color: '#F4F2FF',
        boxShadow: '0 12px 40px rgba(0,0,0,0.5)',
        opacity: open ? 1 : 0,
        transform: open ? 'translate3d(0, -50%, 0) scale(1)' : 'translate3d(0, calc(-50% + 12px), 0) scale(0.97)',
        transition: reduced ? 'none' : `${tr('opacity')}, ${tr('transform')}`,
      }}>
        <div style={{ display: 'flex', justifyContent: 'flex-end', margin: '-8px -10px -6px 0' }}>
          <button onClick={onDismiss} aria-label={t.typeHelpClose} data-testid="filter-type-help-close" style={{
            width: 44, height: 44, padding: 0, border: 0, background: 'transparent', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8E8AA6" strokeWidth="2"
              strokeLinecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
          </button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {HELP_ORDER.map(type => (
            <div key={type} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <span style={{
                width: 32, height: 32, borderRadius: 16, border: `1.5px solid ${EVENT_TYPE_COLOR[type]}`, boxSizing: 'border-box',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 'none',
              }}>
                <Icon k={TYPE_ICON[type]} color={EVENT_TYPE_COLOR[type]} bg="#1C1C27" />
              </span>
              <p style={{ margin: 0, fontSize: 14, lineHeight: 1.4, color: '#E4E2EE' }}>
                <b style={{ fontWeight: 700, color: EVENT_TYPE_COLOR[type] }}>{t.types[type]}</b>
                <br />{t.typeHelp[type]}
              </p>
            </div>
          ))}
        </div>
        <p style={{ margin: '16px 0 0', fontSize: 13, lineHeight: 1.4, fontStyle: 'italic', color: '#8E8AA6' }}>{t.typeHelpNote}</p>
      </div>
    </>
  )
}

export function FilterSheet({ lang, mode, items, allEvents, venues, filter, onChange, onClose }: Props) {
  const dict = getDict(lang)
  const t = dict.filter
  const reduced = useMemo(prefersReducedMotion, [])
  const [shown, setShown] = useState(reduced)
  const [closing, setClosing] = useState(false)
  const [dragY, setDragY] = useState(0)
  const [dragging, setDragging] = useState(false)
  const [genresExpanded, setGenresExpanded] = useState(false)
  const historyPushedRef = useRef(false)
  const [helpVisible, setHelpVisible] = useState(false)
  const [helpClosing, setHelpClosing] = useState(false)
  const helpPushedRef = useRef(false)
  const ignorePopRef = useRef(false)
  const closedRef = useRef(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const dragRef = useRef<{ startY: number; active: boolean; fromHeader: boolean } | null>(null)

  const counts = useMemo(() => filterCounts(items, filter, mode), [items, filter, mode])

  // Chip order by count, fixed when the panel opens (7b: chips do not jump).
  const [order] = useState(() => {
    const c = filterCounts(items, filter, mode)
    return {
      genres: orderByCount(availableGenres(allEvents, [...FILTER_TYPES], filter.genres), c.genres),
      characters: orderByCount(availableCharacters(venues, filter.characters), c.characters),
    }
  })
  const genreSet = useMemo(() => new Set(availableGenres(allEvents, filter.types, filter.genres)), [allEvents, filter.types, filter.genres])
  const genres = order.genres.filter(g => genreSet.has(g))
  const visibleGenres = genresExpanded ? genres
    : genres.filter((g, i) => i < VISIBLE_GENRES || filter.genres.includes(g))

  // Culture genre rows (task 076): one per selected subtype with genres. Each
  // row's order by count is fixed when the row first appears.
  const cultureRows = useMemo(() => availableCultureGenres(allEvents, filter.subtypes, filter.cultureGenres),
    [allEvents, filter.subtypes, filter.cultureGenres])
  const cultureOrderRef = useRef(new Map<string, string[]>())
  function cultureRowKeys(subtype: string, keys: string[]): string[] {
    let order = cultureOrderRef.current.get(subtype)
    if (!order) { order = orderByCount(keys, counts.cultureGenres); cultureOrderRef.current.set(subtype, order) }
    const missing = keys.filter(k => !order!.includes(k))
    if (missing.length) { order = [...order, ...orderByCount(missing, counts.cultureGenres)]; cultureOrderRef.current.set(subtype, order) }
    return order.filter(k => keys.includes(k))
  }

  // Open animation
  useEffect(() => {
    if (reduced) return
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setShown(true)))
    return () => cancelAnimationFrame(id)
  }, [reduced])

  // Lock page scroll behind the panel
  useEffect(() => {
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = prev }
  }, [])

  function finishClose() {
    if (closedRef.current) return
    closedRef.current = true
    if (reduced) { onClose(); return }
    setClosing(true)
    setTimeout(onClose, ANIM_MS)
  }

  // System Back closes the panel. The entry is pushed once (StrictMode runs the
  // effect twice) and removed by requestClose or consumed by Back; the panel is
  // only unmounted through finishClose, so the cleanup does not go back.
  useEffect(() => {
    if (!historyPushedRef.current) {
      history.pushState({ filterSheet: true }, '')
      historyPushedRef.current = true
    }
    function onPopState() {
      if (ignorePopRef.current) { ignorePopRef.current = false; return }
      // Back with the type help card open closes only the card (task 077)
      if (helpPushedRef.current) { helpPushedRef.current = false; hideHelp(); return }
      if (historyPushedRef.current) { historyPushedRef.current = false; finishClose() }
    }
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function openHelp() {
    if (helpVisible) return
    history.pushState({ filterTypeHelp: true }, '')
    helpPushedRef.current = true
    setHelpClosing(false)
    setHelpVisible(true)
  }

  function hideHelp() {
    setHelpClosing(true)
    setTimeout(() => { setHelpVisible(false); setHelpClosing(false) }, reduced ? 0 : ANIM_MS)
  }

  function dismissHelp() {
    if (helpClosing) return
    if (helpPushedRef.current) { helpPushedRef.current = false; ignorePopRef.current = true; history.back() }
    hideHelp()
  }

  function requestClose() {
    if (historyPushedRef.current) { historyPushedRef.current = false; history.back() }
    finishClose()
  }

  // Drag down to close: from the header, or from the content when it is scrolled to the top.
  function onTouchStart(e: React.TouchEvent, fromHeader: boolean) {
    dragRef.current = { startY: e.touches[0]!.clientY, active: false, fromHeader }
  }
  function onTouchMove(e: React.TouchEvent) {
    const d = dragRef.current
    if (!d) return
    const dy = e.touches[0]!.clientY - d.startY
    if (!d.active) {
      const atTop = (scrollRef.current?.scrollTop ?? 0) <= 0
      if (dy > 8 && (d.fromHeader || atTop)) { d.active = true; setDragging(true) }
      else if (Math.abs(dy) > 8) { dragRef.current = null; return }
      else return
    }
    setDragY(Math.max(0, dy))
  }
  function onTouchEnd() {
    const d = dragRef.current
    dragRef.current = null
    if (!d?.active) return
    setDragging(false)
    if (dragY > 90) requestClose()
    else setDragY(0)
  }

  const open = shown && !closing
  const transition = reduced || dragging ? 'none' : `transform ${ANIM_MS}ms cubic-bezier(.2,.8,.2,1)`

  function typeChip(type: FilterType) {
    const on = filter.types.includes(type)
    const color = EVENT_TYPE_COLOR[type]
    const dark = EVENT_TYPE_DARK[type]
    const n = counts.types[type]
    return (
      <button key={type} data-testid={`filter-type-${type}`} aria-pressed={on}
        onClick={() => onChange(toggleType(filter, type))}
        style={{
          height: 40, padding: '0 10px', borderRadius: 20,
          background: on ? color : 'transparent', color: on ? dark : '#F4F2FF', border: `1.5px solid ${color}`,
          opacity: n === 0 ? 0.45 : 1,
          fontFamily: "'Outfit', sans-serif", fontSize: 14, fontWeight: 600,
          display: 'inline-flex', alignItems: 'center', gap: 7, cursor: 'pointer', whiteSpace: 'nowrap',
        }}>
        <Icon k={TYPE_ICON[type]} color={on ? dark : color} bg={on ? color : '#1C1C27'} />
        {t.types[type]}<Count n={n} on={on} dark={dark} />
      </button>
    )
  }

  return createPortal(
    <>
      <div
        onClick={requestClose}
        style={{
          position: 'fixed', inset: 0, zIndex: 101, background: 'rgba(8,8,12,0.6)',
          opacity: open ? 1 : 0, transition: reduced ? 'none' : `opacity ${ANIM_MS}ms`,
        }}
      />
      <section
        role="dialog" aria-label={t.title} data-testid="filter-sheet"
        style={{
          position: 'fixed', left: 0, right: 0, bottom: 0, top: 114, zIndex: 102,
          borderRadius: '28px 28px 0 0', background: '#1C1C27', borderTop: '1px solid #2E2D3C',
          boxSizing: 'border-box', display: 'flex', flexDirection: 'column',
          fontFamily: "'Outfit', sans-serif", color: '#F4F2FF',
          transform: open ? `translate3d(0, ${dragY}px, 0)` : 'translate3d(0, 100%, 0)',
          transition, willChange: 'transform',
        }}
        onTouchMove={onTouchMove} onTouchEnd={onTouchEnd} onTouchCancel={onTouchEnd}
      >
        <div style={{ padding: '10px 16px 0', display: 'flex', flexDirection: 'column', touchAction: 'none' }}
          onTouchStart={e => onTouchStart(e, true)}>
          <span style={{ alignSelf: 'center', width: 40, height: 5, borderRadius: 3, background: '#3A3A50' }} />
          <div style={{ display: 'flex', alignItems: 'center', margin: '14px 0 18px' }}>
            <h2 style={{ margin: 0, fontFamily: "'Bricolage Grotesque', sans-serif", fontSize: 26, fontWeight: 700 }}>{t.title}</h2>
            <button onClick={() => onChange(DEFAULT_FILTER)} style={{
              marginLeft: 'auto', border: 0, background: 'transparent', color: '#B9B6CC', padding: 0,
              fontFamily: "'Outfit', sans-serif", fontSize: 14, fontWeight: 600,
              textDecoration: 'underline', textUnderlineOffset: 3, cursor: 'pointer',
            }}>{t.clearAll}</button>
          </div>
        </div>

        <div ref={scrollRef} data-testid="filter-scroll"
          onTouchStart={e => onTouchStart(e, false)}
          style={{
            flex: 1, minHeight: 0, overflowY: 'auto', overscrollBehavior: 'contain',
            WebkitOverflowScrolling: 'touch', padding: '0 16px 8px',
            display: 'flex', flexDirection: 'column', gap: 22,
          }}>
          <Section title={t.type} right={<HelpButton label={t.typeHelpLabel} onClick={openHelp} />}>
            {FILTER_TYPES.map(typeChip)}
            {filter.types.includes('culture') && (
              <div data-testid="filter-subtypes" style={{
                width: '100%', boxSizing: 'border-box', background: '#22212F', borderRadius: 14,
                padding: 10, display: 'flex', flexWrap: 'wrap', gap: 8,
              }}>
                {CULTURE_SUBTYPES.map(s => (
                  <NeutralChip key={s} label={tagLabel(s, lang)} n={counts.subtypes[s] ?? 0}
                    on={filter.subtypes.includes(s)} icon={subtypeIconKey(s)}
                    onClick={() => onChange({ ...filter, subtypes: toggleIn(filter.subtypes, s) })} />
                ))}
                {cultureRows.map(row => (
                  <div key={row.subtype} data-testid={`filter-culture-genres-${row.subtype}`}
                    style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 8, marginTop: 4 }}>
                    <p style={{ margin: 0, fontSize: 11, fontWeight: 600, color: '#8E8AA6' }}>{tagLabel(row.subtype, lang)}</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {cultureRowKeys(row.subtype, row.keys).map(k => (
                        <NeutralChip key={k} label={tagLabel(cultureGenreName(k), lang)} n={counts.cultureGenres.get(k) ?? 0}
                          on={filter.cultureGenres.includes(k)}
                          onClick={() => onChange({ ...filter, cultureGenres: toggleIn(filter.cultureGenres, k) })} />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Section>

          {genres.length > 0 && (
            <Section title={t.genre} right={!genresExpanded && genres.length > VISIBLE_GENRES ? (
              <button onClick={() => setGenresExpanded(true)} style={{
                marginLeft: 'auto', border: 0, background: 'transparent', padding: 0, cursor: 'pointer',
                fontFamily: "'Outfit', sans-serif", fontSize: 13, color: '#B9B6CC', fontWeight: 500,
              }}>{t.all} ({genres.length}) ›</button>
            ) : undefined}>
              {visibleGenres.map(g => (
                <NeutralChip key={g} label={tagLabel(g, lang)} n={counts.genres.get(g) ?? 0}
                  on={filter.genres.includes(g)}
                  onClick={() => onChange({ ...filter, genres: toggleIn(filter.genres, g) })} />
              ))}
            </Section>
          )}

          {order.characters.length > 0 && (
            <Section title={t.character}>
              {order.characters.map(c => (
                <NeutralChip key={c} label={tagLabel(c, lang)} n={counts.characters.get(c) ?? 0}
                  on={filter.characters.includes(c)}
                  onClick={() => onChange({ ...filter, characters: toggleIn(filter.characters, c) })} />
              ))}
            </Section>
          )}

          <Section title={t.size}>
            <div style={{ height: 40, borderRadius: 20, background: '#23232F', display: 'flex', width: '100%' }}>
              {VENUE_SIZES.map(s => {
                const on = filter.sizes.includes(s)
                const n = counts.sizes[s] ?? 0
                return (
                  <button key={s} aria-pressed={on}
                    onClick={() => onChange({ ...filter, sizes: toggleIn(filter.sizes, s) })}
                    style={{
                      flex: 1, height: 40, borderRadius: 20, border: 0,
                      background: on ? '#F4F2FF' : 'transparent', color: on ? '#111118' : '#B9B6CC',
                      fontWeight: on ? 700 : 500, fontFamily: "'Outfit', sans-serif", fontSize: 14,
                      opacity: n === 0 ? 0.45 : 1, cursor: 'pointer',
                      display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                    }}>
                    {t.sizes[s]}<Count n={n} on={on} />
                  </button>
                )
              })}
            </div>
          </Section>

          <Section title={t.price}>
            <NeutralChip label={t.free} n={counts.free} on={filter.free}
              onClick={() => onChange({ ...filter, free: !filter.free })} />
          </Section>
        </div>

        <div style={{ padding: '14px 16px calc(34px + env(safe-area-inset-bottom))', background: '#1C1C27' }}>
          <button data-testid="filter-show" onClick={requestClose} style={{
            width: '100%', height: 54, borderRadius: 27, border: 0, background: '#FF4D8D', color: '#1A0710',
            fontFamily: "'Outfit', sans-serif", fontSize: 17, fontWeight: 700, cursor: 'pointer',
          }}>{mode === 'venues' ? t.showVenues(counts.total) : t.showEvents(counts.total)}</button>
        </div>
      </section>
      {helpVisible && <TypeHelpCard lang={lang} reduced={reduced} closing={helpClosing} onDismiss={dismissHelp} />}
    </>,
    document.body,
  )
}
