/**
 * WordHistory UI Component
 * Displays word exchange history between player and LLM
 */
class WordHistory {
  constructor(containerSelector = '.word-history') {
    this.container = document.querySelector(containerSelector);
    this.items = [];
  }

  addUserWord(word) {
    const item = this._createWordItem(word, true);
    this.container.appendChild(item);
    this.items.push(item);
    this.scrollToBottom();
  }

  addRejectedWord(word, reason) {
    const item = document.createElement('div');
    item.className = 'word-item word-item--user word-item--rejected';

    const speaker = document.createElement('div');
    speaker.className = 'word-item__speaker';
    speaker.textContent = '나';

    const content = document.createElement('div');
    content.className = 'word-item__content';

    const wordEl = document.createElement('div');
    wordEl.className = 'word-item__word';
    wordEl.textContent = word;

    const meta = document.createElement('div');
    meta.className = 'word-item__meta';

    const badge = document.createElement('span');
    badge.className = 'word-item__dict-badge word-item__dict-badge--fail';
    badge.textContent = reason || '표준국어대사전에 없는 단어';
    meta.appendChild(badge);

    content.appendChild(wordEl);
    content.appendChild(meta);
    item.appendChild(speaker);
    item.appendChild(content);

    this.container.appendChild(item);
    this.items.push(item);
    this.scrollToBottom();

    setTimeout(() => {
      item.classList.add('word-item--fade-out');
      setTimeout(() => item.remove(), 400);
    }, 2500);
  }

  startLLMTyping() {
    const item = this._createWordItem('', false);
    item.classList.add('word-item--typing');
    const wordEl = item.querySelector('.word-item__word');
    const cursor = document.createElement('span');
    cursor.className = 'word-history__cursor';
    cursor.textContent = '|';
    wordEl.appendChild(cursor);
    this.container.appendChild(item);
    this.items.push(item);
    this.scrollToBottom();
  }

  addLLMTypingChar(char) {
    if (this.items.length === 0) return;

    const lastItem = this.items[this.items.length - 1];
    const wordEl = lastItem.querySelector('.word-item__word');
    const cursor = wordEl.querySelector('.word-history__cursor');

    if (cursor) {
      cursor.remove();
    }

    const charSpan = document.createElement('span');
    charSpan.textContent = char;
    wordEl.appendChild(charSpan);

    const newCursor = document.createElement('span');
    newCursor.className = 'word-history__cursor';
    newCursor.textContent = '|';
    wordEl.appendChild(newCursor);

    this.scrollToBottom();
  }

  finalizeLLMWord(word) {
    if (this.items.length === 0) return;

    const lastItem = this.items[this.items.length - 1];
    lastItem.classList.remove('word-item--typing');
    const cursor = lastItem.querySelector('.word-history__cursor');

    if (cursor) {
      cursor.remove();
    }

    const meta = lastItem.querySelector('.word-item__meta');
    if (meta && !meta.querySelector('.word-item__dict-badge')) {
      const badge = document.createElement('span');
      badge.className = 'word-item__dict-badge';
      badge.textContent = '국립국어원 확인';
      badge.title = '국립국어원 한국어기초사전에서 검증된 단어입니다';
      meta.appendChild(badge);
    }
  }

  startAIReaction() {
    const item = document.createElement('div');
    item.className = 'word-item word-item--ai word-item--reaction';

    const speaker = document.createElement('div');
    speaker.className = 'word-item__speaker';
    speaker.textContent = 'AI';

    const content = document.createElement('div');
    content.className = 'word-item__content';

    const textEl = document.createElement('div');
    textEl.className = 'word-item__reaction-text';

    content.appendChild(textEl);
    item.appendChild(speaker);
    item.appendChild(content);

    this.container.appendChild(item);
    this.items.push(item);
    this._reactionEl = textEl;
    this.scrollToBottom();
  }

  addAIReactionChar(char) {
    if (this._reactionEl) {
      this._reactionEl.textContent += char;
      this.scrollToBottom();
    }
  }

  finalizeAIReaction() {
    this._reactionEl = null;
  }

  removeLastTyping() {
    if (this.items.length === 0) return;
    const lastItem = this.items[this.items.length - 1];
    if (lastItem.classList.contains('word-item--typing')) {
      lastItem.remove();
      this.items.pop();
    }
  }

  scrollToBottom() {
    this.container.scrollTop = this.container.scrollHeight;
  }

  clear() {
    this.container.innerHTML = '';
    this.items = [];
  }

  _createWordItem(word, isUser) {
    const item = document.createElement('div');
    item.className = `word-item ${isUser ? 'word-item--user' : 'word-item--ai'}`;

    const speaker = document.createElement('div');
    speaker.className = 'word-item__speaker';
    speaker.textContent = isUser ? '나' : 'AI';

    const content = document.createElement('div');
    content.className = 'word-item__content';

    const wordEl = document.createElement('div');
    wordEl.className = 'word-item__word';
    wordEl.textContent = word;

    const meta = document.createElement('div');
    meta.className = 'word-item__meta';

    if (isUser) {
      const badge = document.createElement('span');
      badge.className = 'word-item__dict-badge';
      badge.textContent = '국립국어원 확인';
      badge.title = '국립국어원 한국어기초사전에서 검증된 단어입니다';
      meta.appendChild(badge);
    }

    content.appendChild(wordEl);
    content.appendChild(meta);

    item.appendChild(speaker);
    item.appendChild(content);

    return item;
  }
}
