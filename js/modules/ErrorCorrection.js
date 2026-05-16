// ErrorCorrection.js — 오류 찾기 & 수정
class ErrorCorrectionQuiz extends QuizBase {
  renderQuestion() {
    this._removeReportButton();
    this.answered = false;
    const q = this.questions[this.current];

    // 문장에서 틀린 단어를 하이라이트
    const markedSentence = q.q.replace(
      q.wrong,
      `<span class="error-word" id="err-word">${q.wrong}</span>`
    );

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">🔍 오류 수정</div>
        <p style="color:var(--c-text-dim);font-size:0.85rem;margin-bottom:12px;">밑줄 친 부분을 올바르게 고쳐 쓰세요</p>
        <div class="q-text" style="font-size:1.15rem;line-height:2;">${markedSentence}</div>
      </div>

      <div class="error-input-area">
        <div class="error-arrow">
          <span class="error-from">${q.wrong}</span>
          <span style="color:var(--c-text-muted);">→</span>
          <input class="error-input" id="err-input" type="text" placeholder="올바른 답을 입력..."
            autocomplete="off" autofocus onkeydown="if(event.key==='Enter')currentQuiz._check()">
        </div>
        <button class="btn-primary btn-block mt-sm" onclick="currentQuiz._check()">확인 ✓</button>
      </div>
    `;

    setTimeout(() => document.getElementById('err-input')?.focus(), 100);
  }

  _check() {
    if (this.answered) return;
    const input = document.getElementById('err-input');
    const q = this.questions[this.current];
    if (!input.value.trim()) return;

    const correct = this.normalize(input.value.trim()) === this.normalize(q.a);

    input.classList.add(correct ? 'correct' : 'wrong');
    input.disabled = true;

    // 원래 단어에 취소선 + 정답 표시
    const errWord = document.getElementById('err-word');
    if (errWord) {
      errWord.classList.add('corrected');
      const fix = document.createElement('span');
      fix.style.cssText = 'color:var(--c-success);font-weight:700;margin-left:8px;';
      fix.textContent = q.a;
      errWord.parentNode.insertBefore(fix, errWord.nextSibling);
    }

    this.showFeedback(correct, q.exp, `${q.wrong} → ${q.a}`);
  }
}
