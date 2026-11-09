import type { Language } from '../core/types'
import { getDict } from '../i18n'

interface Props {
  lang: Language
  lastFetched: Date | null
}

export function OfflineBanner({ lang, lastFetched }: Props) {
  const dict = getDict(lang)
  const timeStr = lastFetched
    ? lastFetched.toLocaleString(lang === 'en' ? 'en-US' : lang === 'sk' ? 'sk-SK' : 'cs-CZ', {
        day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit'
      })
    : '?'

  return (
    <div style={{
      position: 'absolute', top: 0, left: 0, right: 0,
      background: '#23232F', color: '#B9B6CC',
      fontSize: 13, padding: '8px 16px',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 200, borderBottom: '1px solid #2E2D3C'
    }}>
      {dict.offline} {timeStr}
    </div>
  )
}
