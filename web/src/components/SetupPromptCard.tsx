/** Card above the bottom nav in the style of the update card (task 055): text,
 * pink action button and a small close cross. Task 079: Pre teba without preferences. */
export function SetupPromptCard({ text, button, closeLabel, onAction, onClose }: {
  text: string
  button: string
  closeLabel: string
  onAction: () => void
  onClose: () => void
}) {
  return (
    <div role="status" data-testid="setup-prompt" style={{
      position: 'fixed', left: 16, right: 16, bottom: 28 + 72 + 12, zIndex: 40,
      background: '#2A2838', color: '#F4F2FF',
      borderRadius: 20, padding: '8px 8px 8px 16px',
      display: 'flex', alignItems: 'center', gap: 8,
      boxShadow: '0 4px 20px rgba(0,0,0,0.5)', fontFamily: "'Outfit', sans-serif",
    }}>
      <span style={{ flex: 1, fontSize: 14, fontWeight: 600, lineHeight: 1.3 }}>{text}</span>
      <button onClick={onAction} style={{
        background: '#FF4D8D', color: '#1A0710', border: 'none',
        borderRadius: 16, padding: '8px 14px', fontSize: 14, fontWeight: 700,
        fontFamily: 'inherit', cursor: 'pointer', whiteSpace: 'nowrap',
      }}>{button}</button>
      <button onClick={onClose} aria-label={closeLabel} style={{
        width: 28, height: 28, borderRadius: 14, border: 'none', flex: 'none',
        background: 'transparent', color: '#B9B6CC', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0,
      }}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}
