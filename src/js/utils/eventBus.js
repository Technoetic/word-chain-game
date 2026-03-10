class EventBus {
  constructor() {
    this._listeners = {};
  }

  on(event, handler) {
    if (!this._listeners[event]) {
      this._listeners[event] = [];
    }
    this._listeners[event].push(handler);
  }

  off(event, handler) {
    if (!this._listeners[event]) {
      return;
    }
    const index = this._listeners[event].indexOf(handler);
    if (index > -1) {
      this._listeners[event].splice(index, 1);
    }
  }

  emit(event, data) {
    if (!this._listeners[event]) {
      return;
    }
    this._listeners[event].forEach(handler => {
      handler(data);
    });
  }
}
