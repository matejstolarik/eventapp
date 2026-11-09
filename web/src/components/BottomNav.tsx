import type { Language } from '../core/types'
import { getDict } from '../i18n'
import { IconMap, IconList, IconBuilding, IconPerson } from '../icons'

export type Tab = 'map' | 'events' | 'places' | 'account'

interface Props {
  active: Tab
  lang: Language
  onChange: (tab: Tab) => void
}

export function BottomNav({ active, lang, onChange }: Props) {
  const dict = getDict(lang)

  const tabs: { id: Tab; label: string; Icon: React.FC<{ size?: number; color?: string }> }[] = [
    { id: 'map', label: dict.nav.map, Icon: IconMap },
    { id: 'events', label: dict.nav.events, Icon: IconList },
    { id: 'places', label: dict.nav.places, Icon: IconBuilding },
    { id: 'account', label: dict.nav.account, Icon: IconPerson }
  ]

  return (
    <nav
      style={{
        position: 'absolute', left: 16, right: 16, bottom: 28,
        height: 72, borderRadius: 36, background: '#1C1C27',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 10px', zIndex: 100,
        boxShadow: '0 4px 24px rgba(0,0,0,0.4)'
      }}
      aria-label="Hlavná navigácia"
    >
      {tabs.map(({ id, label, Icon }) => {
        const isActive = active === id
        return (
          <button
            key={id}
            style={{
              height: 52, borderRadius: 26,
              ...(isActive
                ? { padding: '0 20px', background: '#FF4D8D', color: '#1A0710' }
                : { width: 52, color: '#B9B6CC' }),
              display: 'flex', alignItems: 'center',
              justifyContent: 'center', gap: isActive ? 8 : 0,
              fontSize: 15, fontWeight: 600,
              transition: 'all 0.2s'
            }}
            onClick={() => onChange(id)}
            aria-current={isActive ? 'page' : undefined}
            aria-label={label}
          >
            <Icon size={isActive ? 20 : 22} color={isActive ? '#1A0710' : '#B9B6CC'} />
            {isActive && <span>{label}</span>}
          </button>
        )
      })}
    </nav>
  )
}
