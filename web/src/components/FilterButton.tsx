import { IconFilter } from '../icons'
import { pressClass } from '../core/motion'
import { useChangeKey } from '../core/useMotion'

/** Pink round Filter button (map and Akcie bar) with the count of active
 * filters as a white badge in the corner (design 2 / 7b, task 075). */
export function FilterButton({ badge, label, onClick, style }: {
  badge: number
  label: string
  onClick: () => void
  style?: React.CSSProperties
}) {
  // Task 081: the badge bumps when the number changes
  const bump = useChangeKey(badge, 'filterBadge')
  return (
    <button
      className={pressClass()}
      style={{
        position: 'relative', flex: 'none', width: 44, height: 44, borderRadius: 22,
        background: '#FF4D8D', color: '#1A0710',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        border: 'none', cursor: 'pointer', ...style,
      }}
      aria-label={badge > 0 ? `${label} (${badge})` : label}
      onClick={onClick}
    >
      <IconFilter size={20} color="#1A0710" />
      {badge > 0 && (
        <span key={bump} data-testid="filter-badge" className={bump > 0 ? 'm-bump' : undefined} style={{
          position: 'absolute', top: -3, right: -3,
          minWidth: 18, height: 18, padding: '0 5px', boxSizing: 'border-box', borderRadius: 9,
          background: '#F4F2FF', color: '#111118', border: '1.5px solid #111118',
          fontFamily: "'Outfit', sans-serif", fontSize: 11, fontWeight: 700, lineHeight: 1,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>{badge}</span>
      )}
    </button>
  )
}
