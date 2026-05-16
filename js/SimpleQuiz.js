// SimpleQuiz — T/F + MultiChoice (공통 선택형)
class SimpleQuiz extends QuizBase {
  renderQuestion() {
    this.removeReportBtn();
    this.answered = false;
    const q = this.questions[this.current];

    if (q.type === 'true-false') {
      this.renderTF(q);
    } else {
      this.renderMC(q);
    }
  }

  renderTF(q) {
    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">⭕ 참 / 거짓</div>
        <div class="q-text">${q.q}</div>
      </div>
      <div class="options-list">
        <button class="option-btn" onclick="currentQuiz.checkTF(this, true)">
          <span class="option-label">T</span><span>참 (True)</span>
        </button>
        <button class="option-btn" onclick="currentQuiz.checkTF(this, false)">
          <span class="option-label">F</span><span>거짓 (False)</span>
        </button>
      </div>
    `;
  }

  renderMC(q) {
    const opts = q.opts || [];
    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">📝 알맞은 것 고르기</div>
        <div class="q-text">${q.q}</div>
      </div>
      <div class="options-list">
        ${opts.map((opt, i) => `
          <button class="option-btn" data-val="${opt}" onclick="currentQuiz.checkMC(this, '${opt.replace(/'/g, "\\'")}')">
            <span class="option-label">${String.fromCharCode(65 + i)}</span>
            <span>${opt}</span>
          </button>
        `).join('')}
      </div>
    `;
  }

  checkTF(btn, selected) {
    if (this.answered) return;
    const q = this.questions[this.current];
    const correct = selected === q.a;

    this.container.querySelectorAll('.option-btn').forEach(b => {
      b.style.pointerEvents = 'none';
    });

    const correctLabel = q.a ? 'T' : 'F';
    this.container.querySelectorAll('.option-btn').forEach(b => {
      const label = b.querySelector('.option-label').textContent;
      if ((label === 'T' && q.a) || (label === 'F' && !q.a)) b.classList.add('correct');
      else if (b === btn && !correct) b.classList.add('wrong');
    });

    this.showFeedback(correct, q.exp, q.a ? '참 (True)' : '거짓 (False)');
  }

  checkMC(btn, selected) {
    if (this.answered) return;
    const q = this.questions[this.current];
    const correct = selected === q.a;

    this.container.querySelectorAll('.option-btn').forEach(b => {
      b.style.pointerEvents = 'none';
      if (b.dataset.val === q.a) b.classList.add('correct');
      else if (b === btn && !correct) b.classList.add('wrong');
    });

    this.showFeedback(correct, q.exp, q.a);
  }
}
