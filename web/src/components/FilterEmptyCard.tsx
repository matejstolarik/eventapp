import { pressClass } from '../core/motion'
/** Empty result of the filter (design 7b, task 075): a quiet card above the
 * bottom bar with "Najbližšie: <day> ›" (when a later day has results) and
 * "Zrušiť filter". Same surface as the update card (#2A2838, radius 20). */
export function FilterEmptyCard({ text, nearestLabel, onNearest, clearLabel, onClear }: {
  text: string
  nearestLabel: string | null
  onNearest: () => void
  clearLabel: string
  onClear: () => void
}) {
  const btn: React.CSSProperties = {
    height: 36, padding: '0 14px', borderRadius: 18, border: 0, cursor: 'pointer',
    fontFamily: "'Outfit', sans-serif", fontSize: 14, fontWeight: 600, whiteSpace: 'nowrap',
  }
  return (
    <div data-testid="filter-empty" style={{
      position: 'fixed', left: 16, right: 16, bottom: 112, zIndex: 25,
      background: '#2A2838', borderRadius: 20, padding: '14px 16px',
      boxShadow: '0 4px 16px rgba(0,0,0,0.5)', fontFamily: "'Outfit', sans-serif",
      display: 'flex', flexDirection: 'column', gap: 12,
    }}>
      <p style={{ margin: 0, fontSize: 14, fontWeight: 500, color: '#F4F2FF' }}>{text}</p>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {nearestLabel && (
          <button className={pressClass()} style={{ ...btn, background: '#F4F2FF', color: '#111118' }} onClick={onNearest}>{nearestLabel} ›</button>
        )}
        <button className={pressClass()} style={{ ...btn, background: '#3A3A50', color: '#F4F2FF' }} onClick={onClear}>{clearLabel}</button>
      </div>
    </div>
  )
}
