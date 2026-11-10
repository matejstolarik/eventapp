import { useState, useCallback } from 'react'
import type { EventsData, Language, Venue, EventType } from '../core/types'
import { getDict } from '../i18n'
import { isFavorite, toggleFavorite } from '../core/store'
import { IconHeart, EventTypeIcon } from '../icons'
import { EVENT_TYPE_COLOR, EVENT_TYPE_DARK } from '../core/eventType'

interface Props {
  data: EventsData
  lang: Language
  onVenueOpen: (venueId: string) => void
  showFavoritesInit?: boolean
}

function normalize(s: string) {
  return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
}

function venueEventType(venue: Venue): EventType {
  const t = venue.type
  if (t.some(x => x.includes('dance'))) return 'dj'
  if (t.some(x => x.includes('concert') || x.includes('jazz'))) return 'concert'
  if (t.some(x => x === 'culture-center' || x === 'cafe' || x === 'cinema' || x === 'culture')) return 'culture'
  return 'dj'
}

interface VenuePhotoProps { venue: Venue; size: number; radius: number }
function VenuePhoto({ venue, size, radius }: VenuePhotoProps) {
  const [err, setErr] = useState(false)
  const et = venueEventType(venue)
  const bg = EVENT_TYPE_COLOR[et]
  const fg = EVENT_TYPE_DARK[et]

  if (!venue.image_url || err) {
    return (
      <div style={{
        width: size, height: size, borderRadius: radius, background: bg,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
      }}>
        <EventTypeIcon type={et} size={Math.round(size * 0.45)} color={fg} />
      </div>
    )
  }
  return (
    <img
      src={venue.image_url}
      alt={venue.name}
      onError={() => setErr(true)}
      style={{
        width: size, height: size, borderRadius: radius,
        objectFit: 'cover', flexShrink: 0, display: 'block'
      }}
    />
  )
}

export function PlacesPage({ data, lang, onVenueOpen, showFavoritesInit = false }: Props) {
  const dict = getDict(lang)
  const [query, setQuery] = useState('')
  const [showFavorites, setShowFavorites] = useState(showFavoritesInit)
  const [, forceUpdate] = useState(0)

  const handleToggleFav = useCallback((e: React.MouseEvent, venueId: string) => {
    e.stopPropagation()
    toggleFavorite(venueId)
    forceUpdate(n => n + 1)
  }, [])

  const q = normalize(query.trim())

  const sorted = [...data.venues]
    .filter(v => v.active)
    .sort((a, b) => a.name.localeCompare(b.name, 'cs'))

  const filtered = sorted.filter(v => {
    if (q && !normalize(v.name).includes(q)) return false
    if (showFavorites && !isFavorite(v.id)) return false
    return true
  })

  const noFavs = showFavorites && !q && sorted.filter(v => isFavorite(v.id)).length === 0
  const noSearch = q.length > 0 && filtered.length === 0

  return (
    <div style={{
      position: 'absolute', inset: 0, overflowY: 'auto',
      background: '#111118', display: 'flex', flexDirection: 'column'
    }}>
      {/* Header */}
      <div style={{ padding: '56px 16px 12px', flexShrink: 0 }}>
        <h1 style={{
          fontFamily: "'Bricolage Grotesque', sans-serif",
          fontSize: 28, fontWeight: 700, letterSpacing: '-0.02em',
          margin: '0 0 16px', color: '#F4F2FF'
        }}>
          {dict.places.title}
        </h1>

        {/* Search */}
        <label style={{
          display: 'flex', alignItems: 'center', gap: 8,
          height: 52, borderRadius: 26, background: '#F4F2FF',
          padding: '0 18px', marginBottom: 12
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5D5677" strokeWidth="2.2" strokeLinecap="round">
            <circle cx="11" cy="11" r="7" /><path d="M16.5 16.5l4 4" />
          </svg>
          <input
            type="search"
            placeholder={dict.places.search}
            value={query}
            onChange={e => setQuery(e.target.value)}
            style={{
              flex: 1, border: 'none', outline: 'none', background: 'transparent',
              fontSize: 16, color: '#111118', fontFamily: "'Outfit', sans-serif"
            }}
          />
        </label>

        {/* All | Favorites toggle */}
        <AllFavsToggle
          showFavorites={showFavorites}
          onChange={setShowFavorites}
          allLabel={dict.map.all}
          favLabel={dict.map.favorites}
        />
      </div>

      {/* List */}
      <div style={{ flex: 1, padding: '4px 0 100px' }}>
        {noFavs && (
          <p style={{ color: '#B9B6CC', fontSize: 14, padding: '32px 24px', textAlign: 'center', lineHeight: 1.5 }}>
            {dict.places.noFavorites}
          </p>
        )}
        {noSearch && (
          <p style={{ color: '#B9B6CC', fontSize: 14, padding: '32px 24px', textAlign: 'center' }}>
            {dict.places.noResults}
          </p>
        )}
        {filtered.map(venue => (
          <VenueRow
            key={venue.id}
            venue={venue}
            isFav={isFavorite(venue.id)}
            onToggleFav={handleToggleFav}
            onOpen={onVenueOpen}
          />
        ))}
      </div>
    </div>
  )
}

interface ToggleProps {
  showFavorites: boolean
  onChange: (v: boolean) => void
  allLabel: string
  favLabel: string
}
export function AllFavsToggle({ showFavorites, onChange, allLabel, favLabel }: ToggleProps) {
  return (
    <div style={{
      display: 'inline-flex', height: 44, borderRadius: 22,
      background: '#23232F', padding: 4, gap: 2
    }}>
      {[false, true].map(isFav => (
        <button
          key={String(isFav)}
          onClick={() => onChange(isFav)}
          style={{
            height: 36, borderRadius: 18, border: 'none', cursor: 'pointer',
            padding: '0 20px',
            background: showFavorites === isFav ? '#F4F2FF' : 'transparent',
            color: showFavorites === isFav ? '#111118' : '#B9B6CC',
            fontSize: 14, fontWeight: 600, fontFamily: "'Outfit', sans-serif",
            transition: 'background 160ms, color 160ms',
            display: 'flex', alignItems: 'center', gap: 6
          }}
        >
          {isFav && (
            <IconHeart size={14} color={showFavorites ? '#FF4D8D' : '#B9B6CC'} filled={showFavorites} />
          )}
          {isFav ? favLabel : allLabel}
        </button>
      ))}
    </div>
  )
}

interface RowProps {
  venue: Venue
  isFav: boolean
  onToggleFav: (e: React.MouseEvent, id: string) => void
  onOpen: (id: string) => void
}
function VenueRow({ venue, isFav, onToggleFav, onOpen }: RowProps) {
  return (
    <div
      onClick={() => onOpen(venue.id)}
      style={{
        display: 'flex', alignItems: 'center', gap: 12,
        padding: '10px 16px', cursor: 'pointer'
      }}
    >
      <VenuePhoto venue={venue} size={56} radius={28} />

      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{
          fontFamily: "'Bricolage Grotesque', sans-serif",
          fontSize: 17, fontWeight: 700, color: '#F4F2FF',
          margin: '0 0 5px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'
        }}>
          {venue.name}
        </p>
        <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
          {venue.character.slice(0, 2).map(tag => (
            <span key={tag} style={{
              height: 24, padding: '0 10px', borderRadius: 12,
              border: '1.5px solid #5D5677', color: '#B9B6CC',
              fontSize: 12, fontWeight: 600,
              display: 'inline-flex', alignItems: 'center'
            }}>
              {tag}
            </span>
          ))}
        </div>
      </div>

      <button
        onClick={e => onToggleFav(e, venue.id)}
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          padding: 8, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}
        aria-label={isFav ? 'Odobrať z obľúbených' : 'Pridať do obľúbených'}
      >
        <IconHeart
          size={20}
          color={isFav ? '#FF4D8D' : '#5D5677'}
          filled={isFav}
        />
      </button>
    </div>
  )
}
