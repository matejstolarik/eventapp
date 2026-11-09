import type { Language } from '../core/types'
import { getDict } from '../i18n'

interface Props { lang: Language; title: string }

export function ComingSoon({ lang, title }: Props) {
  const dict = getDict(lang)
  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 12
    }}>
      <p style={{ fontSize: 28, fontFamily: "'Bricolage Grotesque', sans-serif", fontWeight: 700 }}>
        {title}
      </p>
      <p style={{ fontSize: 17, color: '#B9B6CC' }}>{dict.comingSoon}</p>
    </div>
  )
}
