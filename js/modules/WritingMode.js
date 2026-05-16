// WritingMode.js — 서술형 직접 타이핑 (칠보중 전용)
class WritingModeQuiz extends QuizBase {
  renderQuestion() {
    this._removeReportButton();
    this.answered = false;
    const q = this.questions[this.current];

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">✍️ 서술형</div>
        <div class="q-text">${q.q}</div>
        ${q.hint ? `<div style="color:var(--c-text-muted);font-size:0.85rem;margin-top:8px;">💡 ${q.hint}</div>` : ''}
        ${q.ko ? `<div style="color:var(--c-warning);font-size:0.9rem;margin-top:8px;">🇰🇷 ${q.ko}</div>` : ''}
      </div>

      <div class="writing-area">
        <textarea class="writing-input" id="wr-input" rows="3" placeholder="영어로 문장을 작성하세요..."
          autocomplete="off" spellcheck="false"></textarea>
        <div class="writing-tools">
          <span class="char-count" id="wr-count">0자</span>
          <button class="btn-primary" onclick="currentQuiz._check()">제출 ✓</button>
        </div>
      </div>
    `;

    const input = document.getElementById('wr-input');
    input.addEventListener('input', () => {
      document.getElementById('wr-count').textContent = input.value.length + '자';
    });
    setTimeout(() => input.focus(), 100);
  }

  _check() {
    if (this.answered) return;
    const textarea = document.getElementById('wr-input');
    const q = this.questions[this.current];
    const userAnswer = textarea.value.trim();
    if (!userAnswer) return;

    // 키워드 매칭 채점 (핵심 단어들이 포함되어 있는지)
    const answer = q.a.toLowerCase();
    const user = userAnswer.toLowerCase();

    // 완전 일치 체크
    const exactMatch = this.normalize(user) === this.normalize(answer);

    // 키워드 체크 (답안의 핵심 단어 중 몇 개가 포함?)
    const keywords = answer.split(/\s+/).filter(w => w.length > 2);
    const matched = keywords.filter(kw => user.includes(kw));
    const keywordPct = keywords.length > 0 ? matched.length / keywords.length : 0;

    const correct = exactMatch || keywordPct >= 0.7;

    textarea.disabled = true;
    textarea.style.borderColor = correct ? 'var(--c-success)' : 'var(--c-danger)';

    // 모범 답안 표시
    const modelDiv = document.createElement('div');
    modelDiv.className = 'writing-model';
    modelDiv.innerHTML = `
      <strong>📋 모범 답안:</strong>
      <p style="color:var(--c-info);margin-top:4px;line-height:1.7;">${q.a}</p>
      ${!exactMatch && correct ? '<p style="color:var(--c-warning);font-size:0.85rem;margin-top:4px;">⚠️ 핵심 키워드 포함으로 정답 처리되었습니다</p>' : ''}
      ${keywordPct < 0.7 && !exactMatch ? `<p style="color:var(--c-text-dim);font-size:0.85rem;margin-top:4px;">키워드 일치율: ${Math.round(keywordPct * 100)}% (${matched.length}/${keywords.length})</p>` : ''}
    `;
    textarea.parentNode.appendChild(modelDiv);

    this.showFeedback(correct, q.exp, q.a);
  }
}
