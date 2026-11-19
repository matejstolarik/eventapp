import { SparkleIcon } from './EventRow'

/** Chip "✦ Pre teba" of the Akcie bar (design 4); also shown, inert, in the onboarding (task 079). */
export function chipStyle(active: boolean): React.CSSProperties {
  return {
    height: 40, padding: '0 14px', borderRadius: 20, border: 0,
    background: active ? '#FF4D8D' : '#23232F', color: active ? '#1A0710' : '#B9B6CC',
    fontFamily: 'Outfit,sans-serif', fontSize: 14, fontWeight: 500,
    display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap', flex: 'none', cursor: 'pointer',
  }
}

export function ForYouChip({ active, label, onClick, inert = false }: {
  active: boolean; label: string; onClick?: () => void; inert?: boolean
}) {
  return (
    <button style={{ ...chipStyle(active), ...(inert ? { cursor: 'default', pointerEvents: 'none' } : null) }}
      onClick={onClick} tabIndex={inert ? -1 : undefined} aria-hidden={inert || undefined}>
      <SparkleIcon size={16} color={active ? '#1A0710' : '#B9B6CC'} />{label}
    </button>
  )
}
