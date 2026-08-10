export function connect(onSnapshot, onStatus) {
  const scheme = location.protocol === 'https:' ? 'wss' : 'ws';
  let socket;
  let retry;

  const open = () => {
    onStatus?.('connecting');
    socket = new WebSocket(`${scheme}://${location.host}/ws`);
    socket.onopen = () => onStatus?.('live');
    socket.onmessage = event => onSnapshot(JSON.parse(event.data));
    socket.onerror = () => socket.close();
    socket.onclose = () => {
      onStatus?.('offline');
      clearTimeout(retry);
      retry = setTimeout(open, 1500);
    };
  };

  open();
  return () => { clearTimeout(retry); socket?.close(); };
}
