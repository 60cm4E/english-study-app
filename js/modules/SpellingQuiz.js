// SpellingQuiz.js — 한글 뜻 보고 영어 스펠링 타이핑
class SpellingQuiz extends QuizBase {
  renderQuestion() {
    this._removeReportButton();
    this.answered = false;
    const q = this.questions[this.current];
    const hintLetters = q.en.charAt(0) + '_'.repeat(q.en.length - 1);

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">🔤 스펠링 퀴즈</div>
        <div class="q-text" style="text-align:center;">
          <div style="font-size:1.5rem;color:var(--c-warning);margin-bottom:12px;">${q.ko}</div>
          ${q.pos ? `<div style="font-size:0.85rem;color:var(--c-text-muted);">${q.pos}</div>` : ''}
        </div>
      </div>

      <div class="spelling-area">
        <div class="spelling-hint" id="sp-hint">${hintLetters.split('').join(' ')}</div>
        <input class="spelling-input" id="sp-input" type="text" placeholder="영어 단어를 입력하세요..."
          autocomplete="off" autocapitalize="off" spellcheck="false" autofocus
          onkeydown="if(event.key==='Enter')currentQuiz.checkSpelling()">
        <div class="spelling-btns">
          <button class="btn-outline btn-sm" onclick="currentQuiz.showHint()">💡 힌트</button>
          <button class="btn-primary" onclick="currentQuiz.checkSpelling()">확인 ✓</button>
        </div>
      </div>

      ${q.ex ? `<div class="spelling-example">
        <span style="color:var(--c-text-muted);font-size:0.8rem;">예문:</span>
        <p style="font-size:0.9rem;color:var(--c-text-dim);margin-top:4px;font-style:italic;">
          "${q.ex.replace(new RegExp(q.en, 'gi'), '______')}"
        </p>
      </div>` : ''}
    `;

    this._hintLevel = 0;
    setTimeout(() => document.getElementById('sp-input')?.focus(), 100);
  }

  showHint() {
    this._hintLevel++;
    const q = this.questions[this.current];
    const word = q.en;
    const revealed = word.slice(0, Math.min(this._hintLevel + 1, word.length));
    const hidden = '_'.repeat(Math.max(0, word.length - revealed.length));
    document.getElementById('sp-hint').textContent = (revealed + hidden).split('').join(' ');
  }

  checkSpelling() {
    if (this.answered) return;
    const input = document.getElementById('sp-input');
    const q = this.questions[this.current];
    const userAnswer = input.value.trim();
    if (!userAnswer) return;

    // 대소문자 무시, 공백/특수문자 비교용 정규화
    const correct = this.normalize(userAnswer) === this.normalize(q.en);

    input.classList.add(correct ? 'correct' : 'wrong');
    input.disabled = true;

    // 정답 스펠링 표시
    document.getElementById('sp-hint').innerHTML = q.en.split('').map((ch, i) => {
      const userCh = userAnswer[i] || '';
      const match = ch.toLowerCase() === userCh.toLowerCase();
      return `<span style="color:${match ? 'var(--c-success)' : 'var(--c-danger)'}">${ch}</span>`;
    }).join(' ');

    this.showFeedback(correct, null, q.en);
  }
}
