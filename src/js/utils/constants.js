const CONSTANTS = {
  WS_URL: 'ws://localhost:8000/ws/',
  TIMER_DURATION: 15,
  MAX_COMBO: 5,
  MSG_TYPES: {
    GAME_START: 'game_start',
    GAME_STARTED: 'game_started',
    WORD_SUBMIT: 'word_submit',
    WORD_RESULT: 'word_result',
    LLM_TYPING: 'llm_typing',
    LLM_COMPLETE: 'llm_complete',
    GAME_OVER: 'game_over',
    TIMER_EXPIRED: 'timer_expired',
    ERROR: 'error'
  },
  COLORS: {
    USER: '#4fc3f7',
    AI: '#ff7043',
    SUCCESS: '#66bb6a',
    ERROR: '#ef5350',
    COMBO: '#ffd54f'
  }
};
