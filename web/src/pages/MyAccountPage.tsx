import type { EventsData, Language } from '../core/types'
import { getDict } from '../i18n'
import { getGoing, setStoredLanguage } from '../core/store'

interface Props {
  data: EventsData | null
  lang: Language
  onLangChange: (lang: Language) => void
  onEventOpen: (eventId: string) => void
}

export function MyAccountPage({ data, lang, onLangChange, onEventOpen }: Props) {
  const dict = getDict(lang)
  const goingIds = getGoing()
  const now = new Date()
  const todayStr = now.toISOString().slice(0, 10)
  const goingEvents = data
    ? data.events
        .filter(e => goingIds.has(e.id))
        .sort((a, b) => {
          const aEnded = a.date < todayStr || (a.date === todayStr && !!a.end_time && a.end_time < now.toTimeString().slice(0, 5))
          const bEnded = b.date < todayStr || (b.date === todayStr && !!b.end_time && b.end_time < now.toTimeString().slice(0, 5))
          if (aEnded !== bEnded) return aEnded ? 1 : -1
          if (a.date !== b.date) return a.date.localeCompare(b.date)
          if (!a.start_time && !b.start_time) return 0
          if (!a.start_time) return 1
          if (!b.start_time) return -1
          return a.start_time.localeCompare(b.start_time)
        })
    : []
  const venueMap = data ? Object.fromEntries(data.venues.map(v => [v.id, v])) : {}

  function handleLangChange(newLang: Language) {
    setStoredLanguage(newLang)
    onLangChange(newLang)
  }

  const languages: Language[] = ['sk', 'cs', 'en']

  return (
    <div style={{
      position: 'absolute', inset: 0, overflowY: 'auto',
      paddingBottom: 110
    }}>
      <div style={{ padding: '56px 16px 0' }}>
        <h1 style={{
          fontFamily: "'Bricolage Grotesque', sans-serif",
          fontSize: 32, fontWeight: 700, marginBottom: 24
        }}>
          {dict.account.title}
        </h1>

        {/* Going list */}
        <section style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: '#F4F2FF' }}>
            {dict.account.going}
          </h2>
          {goingEvents.length === 0 ? (
            <p style={{ color: '#B9B6CC', fontSize: 15 }}>{dict.account.noGoing}</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {goingEvents.map(event => {
                const venue = venueMap[event.venue_id]
                return (
                  <button
                    key={event.id}
                    style={{
                      display: 'flex', gap: 12, padding: '12px 0',
                      borderBottom: '1px solid #23232F', textAlign: 'left',
                      background: 'none', cursor: 'pointer', color: '#F4F2FF',
                      alignItems: 'center'
                    }}
                    onClick={() => onEventOpen(event.id)}
                  >
                    {event.image_url ? (
                      <img src={event.image_url} alt="" style={{
                        width: 56, height: 56, borderRadius: 12, objectFit: 'cover', flexShrink: 0
                      }} />
                    ) : (
                      <div style={{
                        width: 56, height: 56, borderRadius: 12,
                        background: '#23232F', flexShrink: 0
                      }} />
                    )}
                    <div style={{ minWidth: 0 }}>
                      <p style={{ fontSize: 15, fontWeight: 700, marginBottom: 2, overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                        {event.title}
                      </p>
                      <p style={{ fontSize: 13, color: '#B9B6CC' }}>
                        {venue?.name ?? event.venue_id} · {event.date}
                        {event.start_time ? ` · ${event.start_time}` : ''}
                      </p>
                    </div>
                  </button>
                )
              })}
            </div>
          )}
        </section>

        {/* Language selector */}
        <section>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: '#F4F2FF' }}>
            {dict.account.language}
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {languages.map(l => (
              <button
                key={l}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '14px 0', borderBottom: '1px solid #23232F',
                  background: 'none', cursor: 'pointer',
                  color: l === lang ? '#F4F2FF' : '#B9B6CC',
                  fontSize: 17, fontWeight: l === lang ? 700 : 400
                }}
                onClick={() => handleLangChange(l)}
              >
                {dict.account.languages[l]}
                {l === lang && (
                  <span style={{
                    width: 8, height: 8, borderRadius: 4, background: '#FF4D8D'
                  }} />
                )}
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
