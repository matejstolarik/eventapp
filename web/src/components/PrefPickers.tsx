import { useState } from 'react'
import type { Language, Venue } from '../core/types'
import { getDict, tagLabel } from '../i18n'
import { typeIconSvg } from '../map/markers'
import { EVENT_TYPE_COLOR, EVENT_TYPE_DARK, CULTURE_SUBTYPES, subtypeIconKey, type EventIconKey } from '../core/eventType'
import type { FilterType } from '../core/filter'
import { MAX_PREF_GENRES, toggleFavorite, type Preferences } from '../core/store'
import { togglePrefType, togglePrefSubtype, togglePrefGenre, canToggleTypeOff } from '../core/preferences'
import { normalizeText } from '../core/search'
import { IconHeart } from '../icons'
import { heartPop } from '../core/motion'
import { VenuePhoto } from '../pages/PlacesPage'

// Task 079 (design.md 7c): the three preference pickers shared by the onboarding
// and My account → Event preferences.

export const PREF_TYPE_ORDER: FilterType[] = ['concert', 'dj', 'party', 'culture']
const TYPE_ICON: Record<FilterType, EventIconKey> = { concert: 'concert', party: 'party', dj: 'dj', culture: 'culture' }
const PINK = '#FF4D8D'

function SvgIcon({ k, color, bg, size }: { k: EventIconKey; color: string; bg: string; size: number }) {
  return <span style={{ display: 'flex', width: size, height: size, lineHeight: 0, flex: 'none' }}
    dangerouslySetInnerHTML={{ __html: typeIconSvg(k, color, size, bg) }} />
}

/** Round type icon in its colour (welcome row, type cards). */
export function TypeCircle({ type, size = 36, bg = '#1C1C27', filled = false }: { type: FilterType; size?: number; bg?: string; filled?: boolean }) {
  const color = EVENT_TYPE_COLOR[type]
  return (
    <span style={{
      width: size, height: size, borderRadius: size / 2, boxSizing: 'border-box', flex: 'none',
      border: `1.5px solid ${color}`, background: filled ? color : 'transparent',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <SvgIcon k={TYPE_ICON[type]} color={filled ? EVENT_TYPE_DARK[type] : color} bg={filled ? color : bg} size={Math.round(size * 0.55)} />
    </span>
  )
}

/** White search field like Miesta (search without diacritics). */
export function PlaceSearch({ value, placeholder, onChange }: { value: string; placeholder: string; onChange: (v: string) => void }) {
  return (
    <label style={{
      display: 'flex', alignItems: 'center', gap: 8, height: 44, borderRadius: 22, background: '#F4F2FF',
      padding: '0 16px', boxSizing: 'border-box', flex: 'none',
    }}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5D5677" strokeWidth="2.2" strokeLinecap="round">
        <circle cx="11" cy="11" r="7" /><path d="M16.5 16.5l4 4" />
      </svg>
      <input type="search" placeholder={placeholder} value={value} onChange={e => onChange(e.target.value)}
        style={{ flex: 1, minWidth: 0, border: 'none', outline: 'none', background: 'transparent', fontSize: 16, color: '#111118', fontFamily: "'Outfit', sans-serif" }} />
    </label>
  )
}

/** Active venues alphabetically, filtered by the search text. */
export function placesFor(venues: Venue[], query: string): Venue[] {
  const q = normalizeText(query.trim())
  return venues.filter(v => v.active)
    .sort((a, b) => a.name.localeCompare(b.name, 'cs'))
    .filter(v => !q || normalizeText(v.name).includes(q))
}

/** Compact venue rows (~44 px): photo, name, heart = the app's favourite. */
export function PlacesList({ venues, favorites }: { venues: Venue[]; favorites: Set<string> }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {venues.map(v => {
        const fav = favorites.has(v.id)
        return (
          <button key={v.id} data-testid={`pref-place-${v.id}`} aria-pressed={fav}
            onClick={e => { const on = toggleFavorite(v.id); if (on) heartPop(e.currentTarget.querySelector('[data-heart]')) }}
            style={{
              display: 'flex', alignItems: 'center', gap: 12, height: 44, padding: 0, border: 0,
              background: 'transparent', color: '#F4F2FF', cursor: 'pointer', textAlign: 'left',
              WebkitTapHighlightColor: 'transparent', outline: 'none', fontFamily: "'Outfit', sans-serif",
            }}>
            <VenuePhoto venue={v} size={32} radius={16} />
            <span style={{ flex: 1, minWidth: 0, fontSize: 15, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{v.name}</span>
            <span data-heart style={{ padding: '0 4px', display: 'flex' }}>
              <IconHeart size={20} color={fav ? PINK : '#5D5677'} filled={fav} />
            </span>
          </button>
        )
      })}
    </div>
  )
}

/** Neutral chip of the pickers; selected = app pink. */
function PrefChip({ label, on, disabled = false, icon, onClick, testId }: {
  label: string; on: boolean; disabled?: boolean; icon?: EventIconKey; onClick: () => void; testId?: string
}) {
  const bg = on ? PINK : '#2A2838'
  return (
    <button onClick={onClick} disabled={disabled} aria-pressed={on} data-testid={testId} style={{
      height: 34, padding: icon ? '0 13px 0 10px' : '0 13px', borderRadius: 17, border: 0,
      background: bg, color: on ? '#1A0710' : '#E4DEFF', fontWeight: on ? 700 : 500,
      opacity: disabled ? 0.4 : 1, cursor: disabled ? 'default' : 'pointer',
      outline: 'none', WebkitTapHighlightColor: 'transparent',
      fontFamily: "'Outfit', sans-serif", fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap',
    }}>
      {icon && <SvgIcon k={icon} color={on ? '#1A0710' : EVENT_TYPE_COLOR.culture} bg={bg} size={16} />}
      {label}
    </button>
  )
}

export function reducedMotion(): boolean {
  try { return window.matchMedia('(prefers-reduced-motion: reduce)').matches } catch { return false }
}

/** Type cards one under another; culture expands its subtype chips (~250 ms).
 * keepOne (Event preferences, task 091): the last selected type cannot be removed –
 * a tap on it shakes the card (like Next in the onboarding, task 080) and keeps it. */
export function TypesPicker({ lang, prefs, onChange, keepOne = false }: { lang: Language; prefs: Preferences; onChange: (p: Preferences) => void; keepOne?: boolean }) {
  const t = getDict(lang).filter
  const [reduced] = useState(reducedMotion)
  const [shake, setShake] = useState<{ type: FilterType; n: number } | null>(null)
  function tap(type: FilterType) {
    if (keepOne && !canToggleTypeOff(prefs, type)) {
      setShake(s => ({ type, n: (s?.type === type ? s.n : 0) + 1 }))
      try { navigator.vibrate?.(30) } catch { /* not supported */ }
      return
    }
    setShake(null)
    onChange(togglePrefType(prefs, type))
  }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <style>{`@keyframes prefShake { 0%, 100% { transform: translateZ(0) } 20% { transform: translateX(-8px) } 40% { transform: translateX(7px) } 60% { transform: translateX(-5px) } 80% { transform: translateX(3px) } }`}</style>
      {PREF_TYPE_ORDER.map(type => {
        const on = prefs.types.includes(type)
        const culture = type === 'culture'
        const shakeN = shake?.type === type ? shake.n : 0
        return (
          <div key={shakeN > 0 ? `${type}-${shakeN}` : type} data-testid={`pref-type-${type}`} data-on={on || undefined}
            data-shake={shakeN > 0 ? shakeN : undefined} style={{
            animation: shakeN > 0 && !reduced ? 'prefShake 300ms ease-in-out' : undefined,
            // Task 080: the outline is an inset ring on the card's own layer (no 1.5 px
            // border), so a deselected card repaints fully, without a pink remnant.
            borderRadius: 16, background: '#1C1C27', boxShadow: `inset 0 0 0 1.5px ${on ? PINK : '#2E2D3C'}`,
            transform: 'translateZ(0)', overflow: 'hidden',
          }}>
            <button aria-pressed={on} onClick={() => tap(type)} style={{
              width: '100%', display: 'flex', alignItems: culture ? 'center' : 'flex-start', gap: 12, padding: '12px 14px',
              border: 0, background: 'transparent', color: '#F4F2FF', textAlign: 'left', cursor: 'pointer',
              fontFamily: "'Outfit', sans-serif", WebkitTapHighlightColor: 'transparent', outline: 'none',
            }}>
              <TypeCircle type={type} size={32} />
              <span style={{ flex: 1, minWidth: 0 }}>
                <b style={{ display: 'block', fontSize: 15, fontWeight: 700, color: EVENT_TYPE_COLOR[type] }}>{t.types[type]}</b>
                {!culture && <span style={{ display: 'block', marginTop: 2, fontSize: 13, lineHeight: 1.35, color: '#B9B6CC' }}>{t.typeHelp[type]}</span>}
              </span>
              <span aria-hidden="true" style={{
                width: 22, height: 22, borderRadius: 11, boxSizing: 'border-box', flex: 'none', alignSelf: 'center',
                border: on ? 0 : '2px solid #5D5677', background: on ? PINK : 'transparent',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                {on && <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#1A0710" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12l5 5 9-10" /></svg>}
              </span>
            </button>
            {culture && (
              <div data-testid="pref-subtypes" style={{
                display: 'grid', gridTemplateRows: on ? '1fr' : '0fr', opacity: on ? 1 : 0,
                visibility: on ? 'visible' : 'hidden',
                transition: reduced ? 'none' : on ? 'grid-template-rows 250ms cubic-bezier(.2,.8,.2,1), opacity 250ms' : 'grid-template-rows 250ms cubic-bezier(.2,.8,.2,1), opacity 250ms, visibility 0s 250ms',
              }}>
                <div style={{ overflow: 'hidden', minHeight: 0 }}>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, padding: '0 14px 14px' }}>
                    {CULTURE_SUBTYPES.map(s => (
                      <PrefChip key={s} label={tagLabel(s, lang)} on={prefs.subtypes.includes(s)} icon={subtypeIconKey(s)}
                        testId={`pref-subtype-${s}`}
                        onClick={() => { if (on) onChange(togglePrefSubtype(prefs, s)) }} />
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

/** "n/5" badge on the genres title row: grey at 0, pink from 1. */
export function GenreCounter({ n }: { n: number }) {
  return (
    <span data-testid="pref-genre-count" style={{
      height: 24, padding: '0 10px', borderRadius: 12, flex: 'none',
      background: n > 0 ? PINK : '#2A2838', color: n > 0 ? '#1A0710' : '#B9B6CC',
      fontFamily: "'Outfit', sans-serif", fontSize: 13, fontWeight: 700, display: 'inline-flex', alignItems: 'center',
    }}>{n}/{MAX_PREF_GENRES}</span>
  )
}

/** Umbrella music genre chips; after 5 picks the rest are dimmed and disabled. */
export function GenresPicker({ lang, genres, prefs, onChange }: { lang: Language; genres: string[]; prefs: Preferences; onChange: (p: Preferences) => void }) {
  const full = prefs.genres.length >= MAX_PREF_GENRES
  const shown = [...genres, ...prefs.genres.filter(g => !genres.includes(g))]
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
      {shown.map(g => {
        const on = prefs.genres.includes(g)
        return <PrefChip key={g} label={tagLabel(g, lang)} on={on} disabled={full && !on} testId={`pref-genre-${g}`}
          onClick={() => onChange(togglePrefGenre(prefs, g))} />
      })}
    </div>
  )
}
