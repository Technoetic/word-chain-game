const CONFIG = {
  WS_URL: (() => {
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${location.host}/ws/`;
  })(),
  TIMER_DURATION: 30,
  RECONNECT_MAX: 5,
  RECONNECT_DELAY: 1000
};
