// SentenceBuilder.js — 한글 문장 보고 영어 문장 조합 (키워드 힌트)
class SentenceBuilder extends QuizBase {
  renderQuestion() {
    this._removeReportButton();
    this.answered = false;
    const q = this.questions[this.current];

    // 정답 문장에서 키워드 추출하여 힌트로 제공
    const words = q.a.split(/\s+/);
    const hintWords = words.filter((_, i) => i % 3 === 0); // 3단어마다 1개 힌트

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">🏗️ 문장 만들기</div>
        <div class="q-text" style="text-align:center;">
          <div style="font-size:1.2rem;color:var(--c-warning);line-height:1.8;">${q.ko || q.q}</div>
        </div>
      </div>

      <div class="sb-hints">
        <span style="color:var(--c-text-muted);font-size:0.8rem;">💡 힌트 단어:</span>
        ${hintWords.map(w => `<span class="sb-hint-word">${w}</span>`).join('')}
      </div>

      <div class="writing-area">
        <textarea class="writing-input" id="sb-input" rows="2" placeholder="영어 문장을 작성하세요..."
          autocomplete="off" spellcheck="false"
          onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();currentQuiz._check()}"></textarea>
        <div class="writing-tools">
          <button class="btn-outline btn-sm" onclick="currentQuiz._moreHint()">힌트 더 보기</button>
          <button class="btn-primary" onclick="currentQuiz._check()">확인 ✓</button>
        </div>
      </div>
    `;

    this._hintLevel = 0;
    this._allWords = words;
    setTimeout(() => document.getElementById('sb-input')?.focus(), 100);
  }

  _moreHint() {
    this._hintLevel++;
    const showCount = Math.min(this._hintLevel + 2, this._allWords.length);
    const hints = this._allWords.slice(0, showCount);
    const hintsEl = this.container.querySelector('.sb-hints');
    hintsEl.innerHTML = `
      <span style="color:var(--c-text-muted);font-size:0.8rem;">💡 힌트 (${showCount}/${this._allWords.length}):</span>
      ${hints.map(w => `<span class="sb-hint-word">${w}</span>`).join('')}
      ${showCount < this._allWords.length ? ' ...' : ''}
    `;
  }

  _check() {
    if (this.answered) return;
    const textarea = document.getElementById('sb-input');
    const q = this.questions[this.current];
    if (!textarea.value.trim()) return;

    const user = textarea.value.trim().toLowerCase().replace(/[^a-z0-9\s']/g, '').replace(/\s+/g, ' ');
    const answer = q.a.toLowerCase().replace(/[^a-z0-9\s']/g, '').replace(/\s+/g, ' ');
    const correct = user === answer;

    textarea.disabled = true;
    textarea.style.borderColor = correct ? 'var(--c-success)' : 'var(--c-danger)';

    // Word-by-word diff 표시
    const userWords = textarea.value.trim().split(/\s+/);
    const answerWords = q.a.split(/\s+/);
    const diffHtml = answerWords.map((w, i) => {
      const uw = (userWords[i] || '').toLowerCase().replace(/[^a-z0-9']/g, '');
      const aw = w.toLowerCase().replace(/[^a-z0-9']/g, '');
      if (uw === aw) return `<span style="color:var(--c-success)">${w}</span>`;
      return `<span style="color:var(--c-danger);text-decoration:underline">${w}</span>`;
    }).join(' ');

    const diffDiv = document.createElement('div');
    diffDiv.className = 'writing-model';
    diffDiv.innerHTML = `<strong>정답:</strong> <span style="line-height:2">${diffHtml}</span>`;
    textarea.parentNode.appendChild(diffDiv);

    this.showFeedback(correct, q.exp, q.a);
  }
}
