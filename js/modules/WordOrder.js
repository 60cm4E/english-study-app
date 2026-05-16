// WordOrder.js — 어순 배열 (탭 선택 + 드래그)
class WordOrderQuiz extends QuizBase {
  renderQuestion() {
    this._removeReportButton();
    this.answered = false;
    this._selected = [];
    const q = this.questions[this.current];
    const shuffled = this.shuffle([...q.words]);

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">🔀 어순 배열</div>
        <div class="q-text">단어를 올바른 순서로 탭하세요</div>
      </div>
      <div class="word-answer-area" id="wo-answer">
        <span class="wo-placeholder">여기에 단어가 배열됩니다...</span>
      </div>
      <div class="word-bank" id="wo-bank">
        ${shuffled.map((w, i) => `<button class="word-chip" data-idx="${i}" data-word="${w}"
          onclick="currentQuiz._select(this)">${w}</button>`).join('')}
      </div>
      <div class="wo-controls">
        <button class="btn-outline" style="flex:1" onclick="currentQuiz._reset()">초기화 ↺</button>
        <button class="btn-outline btn-sm" onclick="currentQuiz._undo()">↩ 되돌리기</button>
        <button class="btn-primary" style="flex:1" id="wo-submit" onclick="currentQuiz._check()" disabled>확인 ✓</button>
      </div>
    `;
  }

  _select(btn) {
    if (this.answered) return;
    btn.classList.add('selected');
    this._selected.push({ word: btn.dataset.word, btn });
    const area = document.getElementById('wo-answer');
    if (this._selected.length === 1) area.innerHTML = '';
    area.classList.add('active');

    const placed = document.createElement('span');
    placed.className = 'placed-word anim-pop';
    placed.textContent = btn.dataset.word;
    placed.dataset.idx = this._selected.length - 1;
    placed.onclick = () => this._removePlaced(placed);
    area.appendChild(placed);

    const allDone = [...this.container.querySelectorAll('.word-chip')].every(c => c.classList.contains('selected'));
    document.getElementById('wo-submit').disabled = !allDone;
  }

  _removePlaced(el) {
    if (this.answered) return;
    const idx = parseInt(el.dataset.idx);
    const item = this._selected[idx];
    if (item) item.btn.classList.remove('selected');
    this._selected.splice(idx, 1);
    // Re-render placed words
    const area = document.getElementById('wo-answer');
    area.innerHTML = '';
    if (this._selected.length === 0) {
      area.innerHTML = '<span class="wo-placeholder">여기에 단어가 배열됩니다...</span>';
      area.classList.remove('active');
    } else {
      this._selected.forEach((s, i) => {
        const sp = document.createElement('span');
        sp.className = 'placed-word';
        sp.textContent = s.word;
        sp.dataset.idx = i;
        sp.onclick = () => this._removePlaced(sp);
        area.appendChild(sp);
      });
    }
    document.getElementById('wo-submit').disabled = true;
  }

  _undo() {
    if (this.answered || this._selected.length === 0) return;
    const last = this._selected.pop();
    last.btn.classList.remove('selected');
    const area = document.getElementById('wo-answer');
    if (area.lastChild) area.lastChild.remove();
    if (this._selected.length === 0) {
      area.innerHTML = '<span class="wo-placeholder">여기에 단어가 배열됩니다...</span>';
      area.classList.remove('active');
    }
    document.getElementById('wo-submit').disabled = true;
  }

  _reset() {
    if (this.answered) return;
    this._selected.forEach(s => s.btn.classList.remove('selected'));
    this._selected = [];
    const area = document.getElementById('wo-answer');
    area.innerHTML = '<span class="wo-placeholder">여기에 단어가 배열됩니다...</span>';
    area.classList.remove('active');
    document.getElementById('wo-submit').disabled = true;
  }

  _check() {
    if (this.answered) return;
    const q = this.questions[this.current];
    const ua = this._selected.map(s => s.word).join(' ').toLowerCase().replace(/\s+/g, ' ').trim();
    const ca = q.a.toLowerCase().replace(/\s+/g, ' ').trim();
    const correct = ua === ca;

    const area = document.getElementById('wo-answer');
    area.style.borderColor = correct ? 'var(--c-success)' : 'var(--c-danger)';

    if (!correct) {
      // 정답 표시
      const hint = document.createElement('div');
      hint.style.cssText = 'margin-top:8px;font-size:0.9rem;color:var(--c-text-dim);';
      hint.textContent = `정답: ${q.a}`;
      area.appendChild(hint);
    }

    this.showFeedback(correct, null, q.a);
  }
}
