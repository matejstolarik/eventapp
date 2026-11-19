import type maplibregl from 'maplibre-gl'
import type { Language } from '../core/types'
import { getDict } from '../i18n'
import { IconChevronDown, IconLocation } from '../icons'
import { FilterButton } from '../components/FilterButton'
import { AllFavsToggle } from '../components/AllFavsToggle'

interface TopBarProps {
  lang: Language
  selectedDayLabel: string
  showFavorites: boolean
  toggleRef: React.RefObject<HTMLDivElement>
  toggleWidth: number
  onDaySelectorOpen: () => void
  onFavoritesChange: (val: boolean) => void
  onFilterClick: () => void
  filterBadge: number
}

export function MapTopBar({
  lang, selectedDayLabel, showFavorites, toggleRef, toggleWidth,
  onDaySelectorOpen, onFavoritesChange, onFilterClick, filterBadge,
}: TopBarProps) {
  const dict = getDict(lang)
  const togglePad = toggleWidth < 160 ? '0 6px' : toggleWidth < 200 ? '0 8px' : '0 14px'
  const toggleFontSize = toggleWidth < 140 ? 13 : 14

  return (
    <div style={{
      position: 'absolute', top: 56, left: 16, right: 16,
      display: 'grid', gridTemplateColumns: 'auto 1fr 44px',
      alignItems: 'center', gap: 8, zIndex: 20,
    }}>
      <button
        style={{
          height: 44, padding: '0 14px', borderRadius: 22,
          background: '#F4F2FF', color: '#111118',
          fontSize: 15, fontWeight: 600,
          display: 'flex', alignItems: 'center', gap: 6,
          border: 'none', cursor: 'pointer',
          whiteSpace: 'nowrap',
        }}
        onClick={onDaySelectorOpen}
        aria-label={dict.map.daySelector}
      >
        {selectedDayLabel}
        <IconChevronDown size={16} color="#111118" />
      </button>

      <AllFavsToggle
        containerRef={toggleRef}
        showFavorites={showFavorites}
        onChange={onFavoritesChange}
        allLabel={dict.map.all}
        favLabel={dict.map.favorites}
        fontSize={toggleFontSize}
        padding={togglePad}
        style={{ flex: 1, minWidth: 0 }}
      />

      <FilterButton badge={filterBadge} label={dict.map.filter} onClick={onFilterClick} />
    </div>
  )
}

interface CompassProps {
  bearing: number
  lang: Language
  mapRef: React.MutableRefObject<maplibregl.Map | null>
}

export function MapCompass({ bearing, lang, mapRef }: CompassProps) {
  const dict = getDict(lang)
  if (bearing === 0) return null
  return (
    <button
      style={{
        position: 'absolute', right: 16, bottom: 192,
        width: 44, height: 44, borderRadius: 22,
        background: '#F4F2FF',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.4)', zIndex: 20,
        border: 0,
      }}
      onClick={() => mapRef.current?.easeTo({ bearing: 0, duration: 400 })}
      aria-label={dict.map.compassLabel}
    >
      <svg width="26" height="26" viewBox="0 0 24 24" aria-hidden="true"
        style={{ transform: `rotate(${-bearing}deg)`, transition: 'transform 100ms' }}>
        <path d="M12 2l4 10h-8z" fill="#FF4D8D" />
        <path d="M12 22l-4-10h8z" fill="#5D5677" />
        <circle cx="12" cy="12" r="1.6" fill="#111118" />
      </svg>
    </button>
  )
}

interface LocationButtonProps {
  lang: Language
  locationLoading: boolean
  onClick: () => void
}

export function MapLocationButton({ lang, locationLoading, onClick }: LocationButtonProps) {
  const dict = getDict(lang)
  return (
    <button
      style={{
        position: 'absolute', right: 16, bottom: 132,
        width: 52, height: 52, borderRadius: 26,
        background: '#F4F2FF', color: '#111118',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 2px 12px rgba(0,0,0,0.4)', zIndex: 20,
        border: 'none', cursor: 'pointer',
        opacity: locationLoading ? 0.6 : 1,
      }}
      onClick={onClick}
      aria-label={dict.map.myLocation}
    >
      <IconLocation size={22} color="#111118" />
    </button>
  )
}

interface AttributionProps {
  showAttribution: boolean
  onToggle: () => void
}

export function MapAttribution({ showAttribution, onToggle }: AttributionProps) {
  return (
    <button
      style={{
        position: 'absolute', left: 16, bottom: 108,
        height: 28, padding: '0 10px', borderRadius: 14,
        background: 'rgba(28,28,39,0.90)', color: '#B9B6CC',
        border: '1px solid #2E2D3C',
        fontSize: 12, fontWeight: showAttribution ? 400 : 700,
        display: 'flex', alignItems: 'center', gap: 6, zIndex: 20,
        whiteSpace: 'nowrap', cursor: 'pointer',
      }}
      onClick={onToggle}
      aria-label="Autorstvo mapy"
    >
      {showAttribution ? '© OpenStreetMap prispievatelia | OpenFreeMap' : 'i'}
    </button>
  )
}

interface ArrowButtonsProps {
  prevVenue: { id: string; lng: number; lat: number } | null
  nextVenue: { id: string; lng: number; lat: number } | null
  leftCount: number
  rightCount: number
  onPrev: () => void
  onNext: () => void
}

function arrowBtnStyle(enabled: boolean): React.CSSProperties {
  return {
    position: 'absolute', bottom: 310,
    width: 40, height: 40, borderRadius: 20,
    background: enabled ? '#F4F2FF' : '#2A2838',
    color: enabled ? '#111118' : '#5D5677',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    boxShadow: enabled ? '0 4px 12px rgba(0,0,0,0.45)' : 'none',
    zIndex: 25,
    border: 'none',
    cursor: enabled ? 'pointer' : 'default',
    opacity: enabled ? 1 : 0.5,
  }
}

export function MapArrowButtons({ prevVenue, nextVenue, leftCount, rightCount, onPrev, onNext }: ArrowButtonsProps) {
  return (
    <>
      <button
        style={{ ...arrowBtnStyle(!!prevVenue), left: 16 }}
        onClick={onPrev}
        disabled={!prevVenue}
        aria-label="Predošlé miesto"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M15 6l-6 6 6 6" />
        </svg>
        {leftCount > 0 && (
          <span style={{
            position: 'absolute', top: -4, right: -4,
            minWidth: 18, height: 18, borderRadius: 9,
            background: '#111118', color: '#F4F2FF',
            fontSize: 11, fontWeight: 700, lineHeight: '18px',
            textAlign: 'center', padding: '0 4px',
            pointerEvents: 'none',
          }}>{leftCount}</span>
        )}
      </button>
      <button
        style={{ ...arrowBtnStyle(!!nextVenue), right: 16 }}
        onClick={onNext}
        disabled={!nextVenue}
        aria-label="Ďalšie miesto"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M9 6l6 6-6 6" />
        </svg>
        {rightCount > 0 && (
          <span style={{
            position: 'absolute', top: -4, left: -4,
            minWidth: 18, height: 18, borderRadius: 9,
            background: '#111118', color: '#F4F2FF',
            fontSize: 11, fontWeight: 700, lineHeight: '18px',
            textAlign: 'center', padding: '0 4px',
            pointerEvents: 'none',
          }}>{rightCount}</span>
        )}
      </button>
    </>
  )
}
