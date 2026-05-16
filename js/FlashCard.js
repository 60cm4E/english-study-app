// FlashCard — 단어 카드 뒤집기 학습
class FlashCardModule {
  constructor(container, words, progressKey) {
    this.container = container;
    this.words = this.shuffle([...words]);
    this.progressKey = progressKey;
    this.current = 0;
    this.known = 0;
    this.unknown = [];
    this.flipped = false;
  }

  shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  start() { this.render(); }

  render() {
    if (this.current >= this.words.length) { this.showResult(); return; }
    const w = this.words[this.current];
    this.flipped = false;

    this.container.innerHTML = `
      <div class="page-header">
        <h1>🔤 단어 학습</h1>
        <p>카드를 탭하여 뜻을 확인하세요</p>
      </div>
      <div class="fc-counter">${this.current + 1} / ${this.words.length} · ✅ ${this.known}개 알아요</div>
      <div class="progress-bar"><div class="progress-fill" style="width:${(this.current/this.words.length)*100}%"></div></div>
      <div class="flashcard-container mt-lg">
        <div class="flashcard" id="fc-card">
          <div class="flashcard-face flashcard-front">
            <div class="fc-word">${w.en}</div>
            ${w.pos ? `<div class="fc-pos">${w.pos}</div>` : ''}
            <div class="fc-hint">👆 탭하여 뜻 보기</div>
          </div>
          <div class="flashcard-face flashcard-back">
            <div class="fc-meaning">${w.ko}</div>
            ${w.ex ? `<div class="fc-example">"${w.ex}"</div>` : ''}
          </div>
        </div>
      </div>
      <div class="fc-actions mt-lg" id="fc-actions" style="display:none">
        <button class="fc-btn-dunno" id="fc-dunno">😅 모르겠어요</button>
        <button class="fc-btn-know" id="fc-know">😊 알아요!</button>
      </div>
      <div class="fc-swipe-hint">카드를 탭한 후 알아요/모르겠어요를 선택하세요</div>
    `;

    document.getElementById('fc-card').onclick = () => this.flip();
    document.getElementById('fc-know').onclick = () => this.next(true);
    document.getElementById('fc-dunno').onclick = () => this.next(false);
  }

  flip() {
    if (this.flipped) return;
    this.flipped = true;
    document.getElementById('fc-card').classList.add('flipped');
    document.getElementById('fc-actions').style.display = 'flex';
  }

  next(isKnown) {
    if (isKnown) {
      this.known++;
    } else {
      this.unknown.push(this.words[this.current]);
    }
    this.current++;
    this.render();
  }

  showResult() {
    const pct = Math.round((this.known / this.words.length) * 100);
    const xp = this.known * 5;
    Storage.addXP(xp);
    Storage.updateStreak();
    Storage.setProgress(this.progressKey, { completed: this.words.length, total: this.words.length, score: pct });
    if (currentUser) Storage.syncToCloud(currentUser.uid);

    let emoji = '🏆', msg = '완벽해요!';
    if (pct < 50) { emoji = '💪'; msg = '다시 도전해봐요!'; }
    else if (pct < 80) { emoji = '👍'; msg = '잘했어요!'; }
    else if (pct < 100) { emoji = '🌟'; msg = '거의 다 외웠어요!'; }

    this.container.innerHTML = `
      <div class="result-card card anim-pop">
        <div class="result-emoji">${emoji}</div>
        <div class="result-score">${pct}%</div>
        <div class="result-label">${this.known} / ${this.words.length} 단어 — ${msg}</div>
        <div class="result-xp">+${xp} XP ⚡</div>
        ${this.unknown.length > 0 ? `
          <div style="margin-top:24px;text-align:left;">
            <strong style="color:var(--c-danger);">📝 다시 복습할 단어:</strong>
            <ul style="margin-top:8px;color:var(--c-text-dim);font-size:0.9rem;list-style:none;padding:0;">
              ${this.unknown.map(w => `<li style="padding:4px 0;">• <strong>${w.en}</strong> — ${w.ko}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
        <div class="result-actions">
          <button class="btn-outline" onclick="history.back()">← 돌아가기</button>
          ${this.unknown.length > 0 ? `<button class="btn-primary" id="retry-unknown">틀린 단어만 다시 🔄</button>` : ''}
        </div>
      </div>
    `;

    if (this.unknown.length > 0) {
      document.getElementById('retry-unknown').onclick = () => {
        this.words = this.shuffle([...this.unknown]);
        this.current = 0; this.known = 0; this.unknown = [];
        this.render();
      };
    }
  }
}
