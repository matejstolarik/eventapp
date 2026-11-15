export const PIN_CSS = `
@keyframes pinpulse {
  0%   { transform: scale(1); opacity: 0.9; }
  70%  { transform: scale(1.9); opacity: 0; }
  100% { transform: scale(1.9); opacity: 0; }
}
@keyframes pin-appear {
  from { opacity: 0; transform: scale(0.82); }
  to   { opacity: 1; transform: scale(1); }
}
@keyframes pin-disappear {
  from { opacity: 1; transform: scale(1); }
  to   { opacity: 0; transform: scale(0.82); }
}
@keyframes card-slide-up {
  from { transform: translateY(100%); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

.pin-inner {
  position: relative;
  width: 50px;
  height: 64px;
  transform: translateX(var(--pin-dx, 0px)) scale(1);
  transform-origin: 50% 100%;
  transition: transform 220ms ease-out, opacity 220ms ease-out;
}
.pin-selected .pin-inner {
  transform: translateX(var(--pin-dx, 0px)) scale(1.22);
}
@media (prefers-reduced-motion: reduce) {
  .pin-inner { transition: none; }
}

.pin-glow {
  position: absolute;
  left: -8px; top: -8px;
  width: 66px; height: 66px;
  border-radius: 33px;
  opacity: 0;
  transition: opacity 220ms ease-out;
  pointer-events: none;
  z-index: 0;
}
.pin-selected .pin-glow { opacity: 1; }
@media (prefers-reduced-motion: reduce) {
  .pin-glow { transition: none; }
}

.pin-live-ring {
  position: absolute;
  left: 3px; top: 3px;
  width: 44px; height: 44px;
  border-radius: 22px;
  border: 2px solid var(--pc, #fff);
  animation: pinpulse 1.6s ease-out infinite;
  transform-origin: center;
  z-index: 0;
  pointer-events: none;
}
@media (prefers-reduced-motion: reduce) {
  .pin-live-ring {
    animation: none;
    opacity: 0.5;
    border-width: 4px;
  }
}

.pin-svg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.pin-circle {
  position: absolute;
  left: 7px; top: 7px;
  width: 36px; height: 36px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.pin-badge-heart {
  position: absolute;
  top: -2px; right: -4px;
  width: 20px; height: 20px;
  border-radius: 10px;
  background: #F4F2FF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.4);
  z-index: 3;
}

.pin-badge-count {
  position: absolute;
  top: -2px; left: -6px;
  height: 20px; min-width: 20px;
  padding: 0 5px;
  box-sizing: border-box;
  border-radius: 10px;
  background: #111118;
  color: #F4F2FF;
  border: 1.5px solid #F4F2FF;
  font-size: 11px; font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: Outfit, sans-serif;
  z-index: 3;
}

.pin-name {
  position: absolute;
  left: 50%;
  top: 68px;
  transform: translateX(-50%);
  white-space: nowrap;
  font-family: 'Outfit', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #E4E2EE;
  text-shadow: 0 0 3px #111118, 0 0 3px #111118, 0 1px 2px #111118;
  letter-spacing: 0.01em;
  pointer-events: none;
  display: none;
  z-index: 4;
}
.pin-selected .pin-name {
  display: block !important;
  font-size: 13px !important;
  font-weight: 800 !important;
  color: #FFFFFF !important;
  left: 50% !important;
  right: auto !important;
  transform: translateX(-50%) !important;
  text-align: center !important;
}
.map-zoom-13 .pin-name {
  display: block;
}

/* Combined pair label — maplibregl.Marker element, moves with the map */
.pin-combined-name {
  white-space: nowrap;
  font-family: 'Outfit', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #E4E2EE;
  text-shadow: 0 0 3px #111118, 0 0 3px #111118, 0 1px 2px #111118;
  letter-spacing: 0.01em;
  pointer-events: none;
  display: none;
  z-index: 10;
}
.map-zoom-13 .pin-combined-name.is-active {
  display: block;
}

.pin-new .pin-inner {
  animation: pin-appear 180ms ease-out both;
}
.pin-leaving .pin-inner {
  animation: pin-disappear 180ms ease-in both;
  pointer-events: none;
}
@media (prefers-reduced-motion: reduce) {
  .pin-new .pin-inner { animation: none; }
  .pin-leaving .pin-inner { animation: none; opacity: 0; }
}

.event-panel-enter {
  animation: card-slide-up 150ms ease-out both;
}
@media (prefers-reduced-motion: reduce) {
  .event-panel-enter { animation: none; }
}
`
