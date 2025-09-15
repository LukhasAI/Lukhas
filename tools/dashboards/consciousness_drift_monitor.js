// Consciousness Drift Monitor widget
// ΛTAG: affect_delta
// Provides real-time visualization of affect_delta metrics.

export function initializeConsciousnessDriftMonitor(endpoint) {
  const display = document.getElementById('affect-delta');
  if (!display) {
    console.error('Affect delta display element not found');
    return;
  }

  const socket = new WebSocket(endpoint);
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const value = data.affect_delta;
    display.textContent = value;
    const driftScore = Math.abs(value); // ΛTAG: driftScore
    // ΛTAG: affect_delta
    console.log('[ConsciousnessDriftMonitor] affect_delta', value, 'driftScore', driftScore);
  };
  socket.onerror = (err) => {
    console.error('Affect delta socket error', err);
  };
  // TODO: handle socket reconnection logic
}
