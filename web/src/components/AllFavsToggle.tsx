import { IconHeart } from '../icons'

interface ToggleProps {
  showFavorites: boolean
  onChange: (v: boolean) => void
  allLabel: string
  favLabel: string
  /** Optional: ref forwarded to the container div (used by MapPage for size measurement) */
  containerRef?: React.RefObject<HTMLDivElement>
  /** Optional: font size (default 14). MapPage shrinks it when space is tight. */
  fontSize?: number
  padding?: string
  style?: React.CSSProperties
}

export function AllFavsToggle({
  showFavorites, onChange, allLabel, favLabel,
  containerRef, fontSize = 14, padding = '0 20px', style,
}: ToggleProps) {
  return (
    <div
      ref={containerRef}
      style={{
        display: 'inline-flex', height: 44, borderRadius: 22,
        background: '#23232F', alignItems: 'center', minWidth: 0,
        ...style,
      }}
      role="group"
      aria-label={`${allLabel} / ${favLabel}`}
    >
      {/* All */}
      <button
        onClick={() => onChange(false)}
        style={{
          flex: 1, height: 44, borderRadius: 22,
          background: !showFavorites ? '#F4F2FF' : 'transparent',
          color: !showFavorites ? '#111118' : '#B9B6CC',
          fontSize, fontWeight: !showFavorites ? 600 : 500,
          padding,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          border: 'none', cursor: 'pointer',
          whiteSpace: 'nowrap',
          fontFamily: "'Outfit', sans-serif",
          WebkitTapHighlightColor: 'transparent',
          transition: 'background 160ms, color 160ms',
        } as React.CSSProperties}
      >
        {allLabel}
      </button>
      {/* Favorites */}
      <button
        onClick={() => onChange(true)}
        style={{
          flex: 1, height: 44, borderRadius: 22,
          background: showFavorites ? '#FF4D8D' : 'transparent',
          color: showFavorites ? '#1A0710' : '#B9B6CC',
          fontSize, fontWeight: showFavorites ? 600 : 500,
          padding,
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5,
          border: 'none', cursor: 'pointer',
          whiteSpace: 'nowrap',
          fontFamily: "'Outfit', sans-serif",
          WebkitTapHighlightColor: 'transparent',
          transition: 'background 160ms, color 160ms',
        } as React.CSSProperties}
      >
        <IconHeart size={14} color={showFavorites ? '#111118' : '#B9B6CC'} filled={showFavorites} />
        {favLabel}
      </button>
    </div>
  )
}
