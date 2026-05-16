// FillBlank.js — 빈칸 채우기 (선택형 + 입력형)
class FillBlankQuiz extends QuizBase {
  renderQuestion() {
    this._removeReportButton();
    this.answered = false;
    const q = this.questions[this.current];

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">✏️ 빈칸 채우기</div>
        <div class="q-text">${this._renderBlankText(q.q)}</div>
        ${q.hint ? `<div style="color:var(--c-text-muted);font-size:0.85rem;margin-top:8px;">💡 힌트: ${q.hint}</div>` : ''}
      </div>
      ${q.opts ? this._renderOptions(q) : this._renderInput()}
    `;
    if (!q.opts) setTimeout(() => document.getElementById('fill-answer')?.focus(), 100);
  }

  _renderBlankText(text) {
    return text.replace(/___/g, '<span class="blank">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>')
               .replace(/_([^_]+)_/g, '<span class="blank">$1</span>');
  }

  _renderOptions(q) {
    const shuffled = this.shuffle([...q.opts]);
    return `<div class="options-list">${shuffled.map((o, i) =>
      `<button class="option-btn" data-val="${o}" onclick="currentQuiz._checkOpt(this,'${o.replace(/'/g, "\\'")}')">
        <span class="option-label">${String.fromCharCode(65 + i)}</span><span>${o}</span>
      </button>`
    ).join('')}</div>`;
  }

  _renderInput() {
    return `<div class="fill-input-area">
      <input class="fill-input" id="fill-answer" type="text" placeholder="정답을 입력하세요..."
        onkeydown="if(event.key==='Enter')currentQuiz._checkInput()" autocomplete="off">
      <button class="fill-submit" onclick="currentQuiz._checkInput()">확인</button>
    </div>`;
  }

  _checkOpt(btn, val) {
    if (this.answered) return;
    const q = this.questions[this.current];
    const correct = this.normalize(val) === this.normalize(q.a);
    this.container.querySelectorAll('.option-btn').forEach(b => {
      b.style.pointerEvents = 'none';
      if (this.normalize(b.dataset.val) === this.normalize(q.a)) b.classList.add('correct');
      else if (b === btn && !correct) b.classList.add('wrong');
    });
    this.showFeedback(correct, q.exp, q.a);
  }

  _checkInput() {
    if (this.answered) return;
    const input = document.getElementById('fill-answer');
    const q = this.questions[this.current];
    if (!input.value.trim()) return;
    const parts = q.a.split(',').map(s => s.trim());
    const userParts = input.value.split(',').map(s => s.trim());
    const correct = parts.every((p, i) => this.normalize(userParts[i] || '') === this.normalize(p));
    input.classList.add(correct ? 'correct' : 'wrong');
    input.disabled = true;
    this.showFeedback(correct, q.exp, q.a);
  }
}
