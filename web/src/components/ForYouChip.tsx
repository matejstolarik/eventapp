import { SparkleIcon } from './EventRow'
import { pressClass } from '../core/motion'
import { useChangeKey } from '../core/useMotion'

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
  // Task 081: the sparkle twinkles once when Pre teba is turned on
  const twinkle = useChangeKey(active, 'forYouSparkle', (prev, next) => !prev && next && !inert)
  return (
    <button className={inert ? undefined : pressClass()}
      style={{ ...chipStyle(active), ...(inert ? { cursor: 'default', pointerEvents: 'none' } : null) }}
      onClick={onClick} tabIndex={inert ? -1 : undefined} aria-hidden={inert || undefined}>
      <span key={twinkle} className={twinkle > 0 ? 'm-twinkle' : undefined} style={{ display: 'inline-flex' }}>
        <SparkleIcon size={16} color={active ? '#1A0710' : '#B9B6CC'} />
      </span>{label}
    </button>
  )
}
