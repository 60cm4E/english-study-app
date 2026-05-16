// MultiChoice.js — 객관식 선택 문제 (2~5지선다)
class MultiChoiceQuiz extends QuizBase {
  renderQuestion() {
    this._removeReportButton();
    this.answered = false;
    const q = this.questions[this.current];
    const shuffled = this.shuffle([...q.opts]);

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">📝 알맞은 것 고르기</div>
        <div class="q-text">${q.q}</div>
      </div>
      <div class="options-list">
        ${shuffled.map((o, i) => `
          <button class="option-btn" data-val="${o}" onclick="currentQuiz._check(this,'${o.replace(/'/g, "\\'")}')">
            <span class="option-label">${String.fromCharCode(65 + i)}</span><span>${o}</span>
          </button>
        `).join('')}
      </div>
    `;
  }

  _check(btn, val) {
    if (this.answered) return;
    const q = this.questions[this.current];
    // Support multi-answer: "hope, to learn"
    const correct = this.normalize(val) === this.normalize(q.a) ||
                    val === q.a;
    this.container.querySelectorAll('.option-btn').forEach(b => {
      b.style.pointerEvents = 'none';
      if (b.dataset.val === q.a || this.normalize(b.dataset.val) === this.normalize(q.a))
        b.classList.add('correct');
      else if (b === btn && !correct) b.classList.add('wrong');
    });
    this.showFeedback(correct, q.exp, q.a);
  }
}
