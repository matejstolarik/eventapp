import { useEffect, useState } from 'react'
import { getForYouPrefs, PREFERENCES_EVENT } from './store'
import type { ForYouPrefs } from './search'

/** Current Pre teba preferences; updates when favourites or preferences change (task 079). */
export function useForYouPrefs(): ForYouPrefs {
  const [prefs, setPrefs] = useState<ForYouPrefs>(getForYouPrefs)
  useEffect(() => {
    const on = () => setPrefs(getForYouPrefs())
    window.addEventListener(PREFERENCES_EVENT, on)
    return () => window.removeEventListener(PREFERENCES_EVENT, on)
  }, [])
  return prefs
}
