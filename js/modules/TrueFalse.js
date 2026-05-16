// TrueFalse.js — 참/거짓 판별 (스와이프 지원)
class TrueFalseQuiz extends QuizBase {
  renderQuestion() {
    this._removeReportButton();
    this.answered = false;
    const q = this.questions[this.current];

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade" id="tf-card">
        <div class="q-label">⭕ 참 / 거짓</div>
        <div class="q-text" style="font-size:1.1rem;line-height:1.8;">${q.q}</div>
      </div>
      <div class="tf-buttons">
        <button class="tf-btn tf-true" onclick="currentQuiz._check(true)">
          <span class="tf-icon">⭕</span>
          <span>참 (True)</span>
        </button>
        <button class="tf-btn tf-false" onclick="currentQuiz._check(false)">
          <span class="tf-icon">❌</span>
          <span>거짓 (False)</span>
        </button>
      </div>
    `;

    // 스와이프: 오른쪽=True, 왼쪽=False
    let startX = 0;
    const card = document.getElementById('tf-card');
    card.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
    card.addEventListener('touchend', e => {
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 60) this._check(dx > 0);
    }, { passive: true });
  }

  _check(val) {
    if (this.answered) return;
    const q = this.questions[this.current];
    const correct = val === q.a;

    this.container.querySelectorAll('.tf-btn').forEach(b => b.style.pointerEvents = 'none');
    const trueBtn = this.container.querySelector('.tf-true');
    const falseBtn = this.container.querySelector('.tf-false');

    if (q.a === true) trueBtn.classList.add('tf-correct');
    else falseBtn.classList.add('tf-correct');

    if (!correct) {
      (val ? trueBtn : falseBtn).classList.add('tf-wrong');
    }

    this.showFeedback(correct, q.exp, q.a ? '참 (True)' : '거짓 (False)');
  }
}
