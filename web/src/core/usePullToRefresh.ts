import { useState, useEffect, useRef } from 'react'

const THRESHOLD = 70
const MAX_PULL = 120

export function usePullToRefresh(
  scrollRef: React.RefObject<HTMLDivElement | null>,
  onRefresh: (() => Promise<void>) | undefined
) {
  const [pullDist, setPullDist] = useState(0)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [refreshError, setRefreshError] = useState(false)
  const startYRef = useRef(0)
  const isPullingRef = useRef(false)
  const pullDistRef = useRef(0)
  const isRefreshingRef = useRef(false)

  useEffect(() => {
    isRefreshingRef.current = isRefreshing
  }, [isRefreshing])

  useEffect(() => {
    const el = scrollRef.current
    if (!el || !onRefresh) return

    function onTouchStart(e: TouchEvent) {
      if (el!.scrollTop > 2) return
      startYRef.current = e.touches[0]!.clientY
      isPullingRef.current = false
    }

    function onTouchMove(e: TouchEvent) {
      if (isRefreshingRef.current) return
      if (el!.scrollTop > 2) { pullDistRef.current = 0; setPullDist(0); return }
      const dy = e.touches[0]!.clientY - startYRef.current
      if (dy <= 0) { pullDistRef.current = 0; setPullDist(0); return }
      isPullingRef.current = true
      e.preventDefault()
      pullDistRef.current = Math.min(dy, MAX_PULL)
      setPullDist(pullDistRef.current)
    }

    function onTouchEnd() {
      if (!isPullingRef.current) return
      isPullingRef.current = false
      const dist = pullDistRef.current
      pullDistRef.current = 0
      setPullDist(0)
      if (dist >= THRESHOLD) {
        setIsRefreshing(true)
        onRefresh!()
          .catch(() => {
            setRefreshError(true)
            setTimeout(() => setRefreshError(false), 2500)
          })
          .finally(() => setIsRefreshing(false))
      }
    }

    el.addEventListener('touchstart', onTouchStart, { passive: true })
    el.addEventListener('touchmove', onTouchMove, { passive: false })
    el.addEventListener('touchend', onTouchEnd, { passive: true })
    return () => {
      el.removeEventListener('touchstart', onTouchStart)
      el.removeEventListener('touchmove', onTouchMove)
      el.removeEventListener('touchend', onTouchEnd)
    }
  }, [scrollRef, onRefresh])

  return { pullDist, isRefreshing, refreshError }
}
