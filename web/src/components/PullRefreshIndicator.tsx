interface Props {
  pullDist: number
  isRefreshing: boolean
}

export function PullRefreshIndicator({ pullDist, isRefreshing }: Props) {
  if (pullDist <= 0 && !isRefreshing) return null
  return (
    <>
      <style>{`@keyframes ptr-spin { to { transform: rotate(360deg) } }`}</style>
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, zIndex: 20,
        display: 'flex', justifyContent: 'center', pointerEvents: 'none',
        transform: pullDist > 0 ? `translateY(${Math.min(pullDist * 0.6, 60) - 44}px)` : 'translateY(16px)',
        transition: pullDist > 0 ? 'none' : 'transform 200ms',
      }}>
        <div style={{
          width: 36, height: 36, borderRadius: 18,
          background: '#2A2838', border: '1px solid #3A3848',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
          animation: isRefreshing ? 'ptr-spin 0.7s linear infinite' : 'none',
        }}>
          <svg
            width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke={pullDist >= 70 || isRefreshing ? '#FF4D8D' : '#B9B6CC'}
            strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
            style={{ transform: isRefreshing ? 'none' : `rotate(${Math.round(pullDist / 120 * 360)}deg)` }}
          >
            <path d="M20 8a8 8 0 1 0 .5 5" />
            <polyline points="20 2 20 8 14 8" />
          </svg>
        </div>
      </div>
    </>
  )
}
