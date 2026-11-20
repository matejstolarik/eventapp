import { pressClass } from '../core/motion'
import { useEffect, useState } from 'react'
import { useRegisterSW } from 'virtual:pwa-register/react'
import type { Language } from '../core/types'
import { getDict } from '../i18n'

const CHECK_INTERVAL_MS = 60 * 60 * 1000

// Debug switch for screenshots/tests: ?dbg=update shows the card without a real new version.
const DEBUG_FORCE = typeof window !== 'undefined'
  && new URLSearchParams(window.location.search).get('dbg') === 'update'

interface Props {
  lang: Language
  /** False on overlay pages (event, venue) without the bottom nav, and while a
   *  bottom panel (map event panel) occupies the same spot. */
  visible: boolean
}

/**
 * Card above the bottom nav that offers to reload into a new app version
 * (task 055). The service worker is checked on start, on every return to the
 * app (visibilitychange -> visible) and every hour.
 */
export function UpdatePrompt({ lang, visible }: Props) {
  const {
    needRefresh: [needRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegisteredSW(swUrl, registration) {
      if (!registration) return
      const check = async () => {
        if (registration.installing || !navigator.onLine) return
        try {
          // Skip the check when the SW script itself is unreachable (offline/flaky).
          const res = await fetch(swUrl, { cache: 'no-store', headers: { 'cache-control': 'no-cache' } })
          if (res.status === 200) await registration.update()
        } catch {
          // Network error: try again on the next trigger.
        }
      }
      check()
      setInterval(check, CHECK_INTERVAL_MS)
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') check()
      })
    },
  })

  const [dismissed, setDismissed] = useState(false)

  // A dismissed card comes back on the next return to the app.
  useEffect(() => {
    function onVisibility() {
      if (document.visibilityState === 'visible') setDismissed(false)
    }
    document.addEventListener('visibilitychange', onVisibility)
    return () => document.removeEventListener('visibilitychange', onVisibility)
  }, [])

  const show = (needRefresh || DEBUG_FORCE) && !dismissed && visible
  if (!show) return null

  const dict = getDict(lang)

  return (
    <div
      role="status"
      style={{
        position: 'absolute', left: 16, right: 16, bottom: 28 + 72 + 12,
        // Above page content and map controls (20-30), below the bottom nav (100) and sheets (101+).
        zIndex: 40,
        background: '#2A2838', color: '#F4F2FF',
        borderRadius: 20, padding: '8px 8px 8px 16px',
        display: 'flex', alignItems: 'center', gap: 8,
        boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
      }}
    >
      <span style={{ flex: 1, fontSize: 14, fontWeight: 600 }}>{dict.update.available}</span>
      <button
        onClick={() => { updateServiceWorker(true) }}
        className={pressClass()}
        style={{
          background: '#FF4D8D', color: '#1A0710', border: 'none',
          borderRadius: 16, padding: '8px 14px', fontSize: 14, fontWeight: 700,
          fontFamily: 'inherit', cursor: 'pointer', whiteSpace: 'nowrap',
        }}
      >
        {dict.update.button}
      </button>
      <button
        onClick={() => setDismissed(true)}
        aria-label={dict.update.close}
        style={{
          width: 28, height: 28, borderRadius: 14, border: 'none',
          background: 'transparent', color: '#B9B6CC', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0,
        }}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}
