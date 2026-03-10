class WebSocketClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl || CONFIG.WS_URL;
    this.socket = null;
    this.isConnected = false;
    this._handlers = {};
    this._reconnectAttempts = 0;
    this._maxReconnect = CONFIG.RECONNECT_MAX || 5;
    this._reconnectDelay = CONFIG.RECONNECT_DELAY || 1000;
    this._sessionId = null;
  }

  connect(sessionId) {
    this._sessionId = sessionId || this._generateSessionId();

    return new Promise((resolve, reject) => {
      try {
        this.socket = new WebSocket(this.baseUrl + this._sessionId);

        this.socket.onopen = () => {
          this.isConnected = true;
          this._reconnectAttempts = 0;
          resolve();
        };

        this.socket.onclose = () => {
          this.isConnected = false;
          if (this._onCloseCallback) {
            this._onCloseCallback();
          }
          this._reconnect();
        };

        this.socket.onerror = (error) => {
          if (this._onErrorCallback) {
            this._onErrorCallback(error);
          }
          if (!this.isConnected) {
            reject(error);
          }
        };

        this.socket.onmessage = (event) => {
          this._handleMessage(event);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  send(type, data = {}) {
    if (!this.isConnected) {
      return;
    }

    const message = {
      type,
      ...data
    };

    this.socket.send(JSON.stringify(message));
  }

  on(type, handler) {
    if (!this._handlers[type]) {
      this._handlers[type] = [];
    }

    this._handlers[type].push(handler);
  }

  off(type, handler) {
    if (!this._handlers[type]) {
      return;
    }

    const index = this._handlers[type].indexOf(handler);
    if (index > -1) {
      this._handlers[type].splice(index, 1);
    }
  }

  onError(callback) {
    this._onErrorCallback = callback;
  }

  onClose(callback) {
    this._onCloseCallback = callback;
  }

  close() {
    this._maxReconnect = 0;
    if (this.socket) {
      this.socket.close();
    }
  }

  _handleMessage(event) {
    try {
      const message = JSON.parse(event.data);

      if (this._handlers[message.type]) {
        this._handlers[message.type].forEach((handler) => {
          handler(message);
        });
      }
    } catch (error) {
      console.error('Failed to parse message:', error);
    }
  }

  async _reconnect() {
    if (this._reconnectAttempts >= this._maxReconnect) {
      if (this._handlers['connection_failed']) {
        this._handlers['connection_failed'].forEach((handler) => {
          handler();
        });
      }
      return;
    }

    this._reconnectAttempts++;
    const delay = this._reconnectDelay * Math.pow(2, this._reconnectAttempts - 1);

    await new Promise((resolve) => setTimeout(resolve, delay));

    try {
      await this.connect(this._sessionId);
    } catch (error) {
      console.error('Reconnection failed:', error);
      this._reconnect();
    }
  }

  _generateSessionId() {
    const chars = '0123456789abcdef';
    let sessionId = '';

    for (let i = 0; i < 8; i++) {
      sessionId += chars.charAt(Math.floor(Math.random() * chars.length));
    }

    return sessionId;
  }
}
