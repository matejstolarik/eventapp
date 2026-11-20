import { pressClass } from '../core/motion'
/** Pre teba switched on without any preferences (design 7c, task 080): a card in
 * the middle of the empty list, in the style of the filter's empty card
 * (FilterEmptyCard: #2A2838, radius 20), with a pink "Nastaviť" → Event preferences. */
export function ForYouSetupCard({ text, button, onSetUp }: { text: string; button: string; onSetUp: () => void }) {
  return (
    <div data-testid="for-you-setup" style={{
      width: '100%', boxSizing: 'border-box',
      background: '#2A2838', borderRadius: 20, padding: '14px 16px',
      boxShadow: '0 4px 16px rgba(0,0,0,0.5)', fontFamily: "'Outfit', sans-serif",
      display: 'flex', flexDirection: 'column', gap: 12,
    }}>
      <p style={{ margin: 0, fontSize: 14, fontWeight: 500, color: '#F4F2FF' }}>{text}</p>
      <div style={{ display: 'flex' }}>
        <button data-testid="for-you-setup-btn" onClick={onSetUp} className={pressClass()} style={{
          height: 36, padding: '0 14px', borderRadius: 18, border: 0, cursor: 'pointer',
          fontFamily: "'Outfit', sans-serif", fontSize: 14, fontWeight: 700, whiteSpace: 'nowrap',
          background: '#FF4D8D', color: '#1A0710',
        }}>{button}</button>
      </div>
    </div>
  )
}
