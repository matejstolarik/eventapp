import { formatDayLabel } from '../i18n'
import type { Language } from '../core/types'

interface Props {
  days: string[]
  selectedDay: string
  lang: Language
  now: Date
  onSelect: (day: string) => void
  onClose: () => void
}

export function DaySelector({ days, selectedDay, lang, now, onSelect, onClose }: Props) {
  return (
    <>
      {/* Backdrop */}
      <div
        style={{ position: 'absolute', inset: 0, zIndex: 29, background: 'rgba(0,0,0,0.5)' }}
        onClick={onClose}
      />
      {/* Sheet */}
      <div style={{
        position: 'absolute', left: 0, right: 0, bottom: 0,
        background: '#1C1C27', borderRadius: '28px 28px 0 0',
        zIndex: 30, paddingBottom: 'max(28px, env(safe-area-inset-bottom))',
        maxHeight: '70vh', overflowY: 'auto'
      }}>
        {/* Handle */}
        <div style={{
          width: 40, height: 4, borderRadius: 2, background: '#3A3A50',
          margin: '12px auto 0'
        }} />

        <div style={{ padding: '8px 0 4px' }}>
          {days.map(day => {
            const isSelected = day === selectedDay
            const label = formatDayLabel(day, lang, now)
            return (
              <button
                key={day}
                style={{
                  display: 'block', width: '100%', textAlign: 'left',
                  padding: '14px 24px', border: 'none', background: 'none',
                  fontSize: 17, fontWeight: isSelected ? 700 : 400,
                  color: isSelected ? '#F4F2FF' : '#B9B6CC',
                  cursor: 'pointer', letterSpacing: '-0.01em'
                }}
                onClick={() => onSelect(day)}
              >
                {label}
              </button>
            )
          })}
        </div>
      </div>
    </>
  )
}
