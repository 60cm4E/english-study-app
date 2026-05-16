// FlashCard.js — 3D 카드 뒤집기 + 스와이프 + 반복학습
class FlashCardModule {
  constructor(container, words, progressKey) {
    this.container = container;
    this.allWords = [...words];
    this.words = this.shuffle([...words]);
    this.progressKey = progressKey;
    this.current = 0;
    this.known = 0;
    this.unknown = [];
    this.flipped = false;
    this.round = 1;
    this.touchStartX = 0;
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
      <div class="page-header"><h1>🔤 단어 학습</h1>
        <p>카드를 탭/스와이프하여 학습하세요${this.round > 1 ? ` (${this.round}라운드 - 복습)` : ''}</p>
      </div>
      <div class="fc-counter">${this.current + 1} / ${this.words.length} · ✅ ${this.known}개 알아요</div>
      <div class="progress-bar"><div class="progress-fill" style="width:${(this.current / this.words.length) * 100}%"></div></div>

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

      <div class="fc-actions mt-lg" id="fc-actions" style="visibility:hidden">
        <button class="fc-btn-dunno" id="fc-dunno">😅 모르겠어요</button>
        <button class="fc-btn-know" id="fc-know">😊 알아요!</button>
      </div>
      <div class="fc-swipe-hint">← 모르겠어요 | 알아요 →</div>
    `;

    const card = document.getElementById('fc-card');
    card.onclick = () => this.flip();

    // 스와이프 지원
    card.addEventListener('touchstart', e => { this.touchStartX = e.touches[0].clientX; }, { passive: true });
    card.addEventListener('touchend', e => {
      const dx = e.changedTouches[0].clientX - this.touchStartX;
      if (!this.flipped) { this.flip(); return; }
      if (Math.abs(dx) > 60) this.next(dx > 0);
    }, { passive: true });

    document.getElementById('fc-know').onclick = () => this.next(true);
    document.getElementById('fc-dunno').onclick = () => this.next(false);
  }

  flip() {
    if (this.flipped) return;
    this.flipped = true;
    document.getElementById('fc-card').classList.add('flipped');
    document.getElementById('fc-actions').style.visibility = 'visible';
  }

  next(isKnown) {
    const card = document.getElementById('fc-card');
    card.style.transition = 'transform 0.3s, opacity 0.3s';
    card.style.transform = isKnown ? 'translateX(120%) rotateY(180deg)' : 'translateX(-120%) rotateY(180deg)';
    card.style.opacity = '0';

    if (isKnown) this.known++;
    else this.unknown.push(this.words[this.current]);

    setTimeout(() => { this.current++; this.render(); }, 250);
  }

  showResult() {
    const pct = Math.round((this.known / this.words.length) * 100);
    const xp = this.known * 5;
    Storage.addXP(xp);
    Storage.updateStreak();
    Storage.setProgress(this.progressKey, { completed: this.words.length, total: this.words.length, score: pct });
    if (currentUser) Storage.syncToCloud(currentUser.uid);

    const emoji = pct >= 100 ? '🏆' : pct >= 80 ? '🌟' : pct >= 50 ? '👍' : '💪';

    this.container.innerHTML = `
      <div class="result-card card anim-pop">
        <div class="result-emoji">${emoji}</div>
        <div class="result-score">${pct}%</div>
        <div class="result-label">${this.known} / ${this.words.length} 단어${this.round > 1 ? ` (${this.round}라운드)` : ''}</div>
        <div class="result-xp">+${xp} XP ⚡</div>
        ${this.unknown.length > 0 ? `
          <div class="wrong-words-list">
            <strong>📝 다시 복습할 단어 (${this.unknown.length}개):</strong>
            <ul>${this.unknown.map(w => `<li><strong>${w.en}</strong> — ${w.ko}</li>`).join('')}</ul>
          </div>
        ` : ''}
        <div class="result-actions">
          <button class="btn-outline" onclick="history.back()">← 돌아가기</button>
          ${this.unknown.length > 0 ? `<button class="btn-primary" id="retry-wrong">틀린 단어만 복습 🔄</button>` : ''}
          <button class="btn-outline" onclick="startSpellingFromFlash()">스펠링 퀴즈로 →</button>
        </div>
      </div>
    `;

    if (this.unknown.length > 0) {
      document.getElementById('retry-wrong').onclick = () => {
        this.words = this.shuffle([...this.unknown]);
        this.current = 0; this.known = 0; this.unknown = [];
        this.round++;
        this.render();
      };
    }

    // Global function for spelling transition
    window.startSpellingFromFlash = () => {
      const el = document.getElementById('content');
      currentQuiz = new SpellingQuiz(el, this.allWords.slice(0, 15), this.progressKey.replace('/vocab', '/spelling'), '🔤 스펠링 퀴즈');
      currentQuiz.start();
    };
  }
}
