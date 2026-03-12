class SpeechRecognitionManager {
  constructor(language = 'ko-KR') {
    this.isListening = false;
    this.isSupported = true;
    this._callbacks = {
      onInterim: null,
      onFinal: null,
      onError: null,
      onStateChange: null
    };

    this._sttSocket = null;
    this._mediaStream = null;
    this._audioContext = null;
    this._processor = null;
    this._analyser = null;
    this._volumeRAF = null;
    this._onVolumeCallback = null;
  }

  async start() {
    if (this.isListening) return;

    try {
      this._mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        }
      });

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      this._sttSocket = new WebSocket(`${protocol}//${host}/ws/stt`);
      this._sttSocket.binaryType = 'arraybuffer';

      this._sttSocket.onopen = () => {
        this._startAudioProcessing();
        this.isListening = true;
        if (this._callbacks.onStateChange) {
          this._callbacks.onStateChange(true);
        }
      };

      this._sttSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'stt_result') {
          if (data.is_final) {
            if (this._callbacks.onFinal) {
              this._callbacks.onFinal(data.transcript);
            }
          } else {
            if (this._callbacks.onInterim) {
              this._callbacks.onInterim(data.transcript);
            }
          }
        } else if (data.type === 'stt_utterance_end') {
          if (this._callbacks.onUtteranceEnd) {
            this._callbacks.onUtteranceEnd();
          }
        } else if (data.type === 'stt_error') {
          if (this._callbacks.onError) {
            this._callbacks.onError(data.message);
          }
        }
      };

      this._sttSocket.onerror = () => {
        console.warn('[STT] connection error, will auto-restart');
        this._cleanup();
        this.isListening = false;
        this._autoRestart();
      };

      this._sttSocket.onclose = () => {
        if (this.isListening) {
          console.warn('[STT] connection closed, will auto-restart');
          this._cleanup();
          this.isListening = false;
          if (this._callbacks.onStateChange) {
            this._callbacks.onStateChange(false);
          }
          this._autoRestart();
        }
      };
    } catch (err) {
      if (this._callbacks.onError) {
        this._callbacks.onError('not-allowed');
      }
    }
  }

  _startAudioProcessing() {
    this._audioContext = new (window.AudioContext || window.webkitAudioContext)({
      sampleRate: 16000
    });

    const source = this._audioContext.createMediaStreamSource(this._mediaStream);
    this._processor = this._audioContext.createScriptProcessor(2048, 1, 1);

    // Volume analyser
    this._analyser = this._audioContext.createAnalyser();
    this._analyser.fftSize = 256;
    this._analyser.smoothingTimeConstant = 0.5;
    source.connect(this._analyser);
    this._startVolumeMonitor();

    this._processor.onaudioprocess = (e) => {
      if (this._sttSocket && this._sttSocket.readyState === WebSocket.OPEN) {
        const float32 = e.inputBuffer.getChannelData(0);
        const int16 = new Int16Array(float32.length);
        for (let i = 0; i < float32.length; i++) {
          const s = Math.max(-1, Math.min(1, float32[i]));
          int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        this._sttSocket.send(int16.buffer);
      }
    };

    source.connect(this._processor);
    this._processor.connect(this._audioContext.destination);
  }

  stop() {
    if (this._restartTimer) {
      clearTimeout(this._restartTimer);
      this._restartTimer = null;
    }
    this._cleanup();
    this.isListening = false;
    if (this._callbacks.onStateChange) {
      this._callbacks.onStateChange(false);
    }
  }

  abort() {
    this.stop();
  }

  _cleanup() {
    if (this._volumeRAF) {
      cancelAnimationFrame(this._volumeRAF);
      this._volumeRAF = null;
    }
    if (this._analyser) {
      this._analyser.disconnect();
      this._analyser = null;
    }
    if (this._onVolumeCallback) {
      this._onVolumeCallback(0);
    }
    if (this._processor) {
      this._processor.disconnect();
      this._processor = null;
    }
    if (this._audioContext) {
      this._audioContext.close().catch(() => {});
      this._audioContext = null;
    }
    if (this._mediaStream) {
      this._mediaStream.getTracks().forEach(t => t.stop());
      this._mediaStream = null;
    }
    if (this._sttSocket && this._sttSocket.readyState === WebSocket.OPEN) {
      this._sttSocket.close();
    }
    this._sttSocket = null;
  }

  _startVolumeMonitor() {
    const dataArray = new Uint8Array(this._analyser.frequencyBinCount);
    const tick = () => {
      if (!this._analyser) return;
      this._analyser.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const avg = sum / dataArray.length;
      const normalized = Math.min(avg / 128, 1);
      if (this._onVolumeCallback) {
        this._onVolumeCallback(normalized);
      }
      this._volumeRAF = requestAnimationFrame(tick);
    };
    this._volumeRAF = requestAnimationFrame(tick);
  }

  onVolume(callback) {
    this._onVolumeCallback = callback;
  }

  onInterim(callback) {
    this._callbacks.onInterim = callback;
  }

  onFinal(callback) {
    this._callbacks.onFinal = callback;
  }

  onError(callback) {
    this._callbacks.onError = callback;
  }

  onStateChange(callback) {
    this._callbacks.onStateChange = callback;
  }

  onUtteranceEnd(callback) {
    this._callbacks.onUtteranceEnd = callback;
  }

  _autoRestart() {
    if (this._restartTimer) return;
    this._restartTimer = setTimeout(() => {
      this._restartTimer = null;
      console.log('[STT] auto-restarting...');
      this.start();
    }, 1000);
  }
}
