// FillBlank — 빈칸 채우기 + 오류 수정
class FillBlankQuiz extends QuizBase {
  renderQuestion() {
    this.removeReportBtn();
    this.answered = false;
    const q = this.questions[this.current];
    const isError = q.type === 'error-correction';

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">${isError ? '🔍 오류 수정' : '✏️ 빈칸 채우기'}</div>
        <div class="q-text">${isError ? this.renderErrorText(q) : this.renderBlankText(q.q)}</div>
      </div>
      ${q.opts ? this.renderOptions(q) : this.renderInput(q)}
    `;
  }

  renderBlankText(text) {
    return text.replace(/___/g, '<span class="blank">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>');
  }

  renderErrorText(q) {
    return `<p style="margin-bottom:8px;color:var(--c-text-dim);font-size:0.85rem;">아래 문장에서 틀린 부분을 고쳐 쓰세요:</p>
      <p>${q.q.replace(q.wrong, `<span class="error-word">${q.wrong}</span>`)}</p>`;
  }

  renderOptions(q) {
    return `<div class="options-list">
      ${q.opts.map((opt, i) => `
        <button class="option-btn" data-val="${opt}" onclick="currentQuiz.checkOption(this, '${opt.replace(/'/g, "\\'")}')">
          <span class="option-label">${String.fromCharCode(65 + i)}</span>
          <span>${opt}</span>
        </button>
      `).join('')}
    </div>`;
  }

  renderInput(q) {
    return `<div class="fill-input-area">
      <input class="fill-input" id="fill-answer" type="text" placeholder="정답을 입력하세요..."
        onkeydown="if(event.key==='Enter')currentQuiz.checkInput()" autocomplete="off" autofocus>
      <button class="fill-submit" onclick="currentQuiz.checkInput()">확인</button>
    </div>`;
  }

  checkOption(btn, selected) {
    if (this.answered) return;
    const q = this.questions[this.current];
    const correct = this.normalize(selected) === this.normalize(q.a);

    // Highlight all options
    this.container.querySelectorAll('.option-btn').forEach(b => {
      b.style.pointerEvents = 'none';
      if (this.normalize(b.dataset.val) === this.normalize(q.a)) b.classList.add('correct');
      else if (b === btn && !correct) b.classList.add('wrong');
    });

    this.showFeedback(correct, q.exp, q.a);
  }

  checkInput() {
    if (this.answered) return;
    const input = document.getElementById('fill-answer');
    const q = this.questions[this.current];
    const userAnswer = input.value.trim();
    if (!userAnswer) return;

    // Support multiple answers separated by comma
    const correctParts = q.a.split(',').map(s => s.trim().toLowerCase());
    const userParts = userAnswer.split(',').map(s => s.trim().toLowerCase());
    const correct = correctParts.every((cp, i) => this.normalize(userParts[i] || '') === this.normalize(cp));

    input.classList.add(correct ? 'correct' : 'wrong');
    input.disabled = true;
    this.showFeedback(correct, q.exp, q.a);
  }

  normalize(s) {
    return (s || '').toLowerCase().replace(/[^a-z0-9가-힣]/g, '').trim();
  }
}
