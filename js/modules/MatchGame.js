// MatchGame.js — 영단어 ↔ 한글 뜻 매칭 게임
class MatchGame {
  constructor(container, words, progressKey) {
    this.container = container;
    this.progressKey = progressKey;
    this.pairs = words.slice(0, 8); // 8쌍 = 16카드
    this.selected = [];
    this.matched = 0;
    this.attempts = 0;
    this.startTime = Date.now();
  }

  start() {
    // 영어 카드 + 한글 카드 섞기
    const cards = [];
    this.pairs.forEach((w, i) => {
      cards.push({ id: i, type: 'en', text: w.en, pairId: i });
      cards.push({ id: i, type: 'ko', text: w.ko, pairId: i });
    });
    this.cards = this.shuffle(cards);
    this.render();
  }

  shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  render() {
    this.container.innerHTML = `
      <div class="page-header"><h1>🎮 매칭 게임</h1>
        <p>같은 뜻의 영어-한글 카드를 맞추세요!</p>
      </div>
      <div class="match-stats">
        <span>✅ ${this.matched}/${this.pairs.length}</span>
        <span>🔄 ${this.attempts}회</span>
      </div>
      <div class="match-grid" id="match-grid">
        ${this.cards.map((c, i) => `
          <button class="match-card ${c.matched ? 'match-done' : ''}" data-idx="${i}"
            onclick="currentQuiz._tap(${i})" ${c.matched ? 'disabled' : ''}>
            <span class="match-card-inner">
              <span class="match-card-front">?</span>
              <span class="match-card-back ${c.type === 'en' ? 'match-en' : 'match-ko'}">${c.text}</span>
            </span>
          </button>
        `).join('')}
      </div>
    `;
  }

  _tap(idx) {
    if (this.cards[idx].matched) return;
    const card = this.container.querySelectorAll('.match-card')[idx];

    // 이미 2장 선택됨 → 무시
    if (this.selected.length >= 2) return;
    // 같은 카드 재탭 → 무시
    if (this.selected.some(s => s.idx === idx)) return;

    card.classList.add('match-flipped');
    this.selected.push({ idx, card, data: this.cards[idx] });

    if (this.selected.length === 2) {
      this.attempts++;
      const [a, b] = this.selected;

      if (a.data.pairId === b.data.pairId && a.data.type !== b.data.type) {
        // 매칭 성공!
        setTimeout(() => {
          a.card.classList.add('match-done');
          b.card.classList.add('match-done');
          this.cards[a.idx].matched = true;
          this.cards[b.idx].matched = true;
          this.matched++;
          this.selected = [];
          this._updateStats();
          if (this.matched === this.pairs.length) this._finish();
        }, 500);
      } else {
        // 매칭 실패
        setTimeout(() => {
          a.card.classList.remove('match-flipped');
          b.card.classList.remove('match-flipped');
          a.card.classList.add('anim-shake');
          b.card.classList.add('anim-shake');
          setTimeout(() => {
            a.card.classList.remove('anim-shake');
            b.card.classList.remove('anim-shake');
          }, 400);
          this.selected = [];
          this._updateStats();
        }, 800);
      }
    }
  }

  _updateStats() {
    const stats = this.container.querySelector('.match-stats');
    if (stats) stats.innerHTML = `<span>✅ ${this.matched}/${this.pairs.length}</span><span>🔄 ${this.attempts}회</span>`;
  }

  _finish() {
    const elapsed = Math.round((Date.now() - this.startTime) / 1000);
    const efficiency = Math.max(0, 100 - (this.attempts - this.pairs.length) * 5);
    const xp = Math.round(efficiency * 0.5);
    Storage.addXP(xp);
    Storage.updateStreak();
    Storage.setProgress(this.progressKey, { completed: this.pairs.length, total: this.pairs.length, score: efficiency });

    setTimeout(() => {
      this.container.innerHTML = `
        <div class="result-card card anim-pop">
          <div class="result-emoji">🎮</div>
          <div class="result-score">${efficiency}%</div>
          <div class="result-label">${this.attempts}번 만에 ${this.pairs.length}쌍 완성!</div>
          <div class="result-time">⏱ ${Math.floor(elapsed/60) > 0 ? Math.floor(elapsed/60)+'분 ' : ''}${elapsed%60}초</div>
          <div class="result-xp">+${xp} XP ⚡</div>
          <div class="result-actions">
            <button class="btn-outline" onclick="history.back()">← 돌아가기</button>
            <button class="btn-primary" onclick="location.reload()">다시 하기 🔄</button>
          </div>
        </div>
      `;
    }, 600);
  }
}
