// WordOrder — 어순 배열 (탭하여 순서대로 선택)
class WordOrderQuiz extends QuizBase {
  renderQuestion() {
    this.removeReportBtn();
    this.answered = false;
    this.selectedWords = [];
    const q = this.questions[this.current];
    const shuffled = this.shuffle([...q.words]);

    this.container.innerHTML = `
      ${this.renderHeader()}
      <div class="quiz-question anim-fade">
        <div class="q-label">🔀 어순 배열</div>
        <div class="q-text">아래 단어들을 올바른 순서로 탭하세요</div>
      </div>
      <div class="word-answer-area" id="wo-answer">
        <span style="color:var(--c-text-muted);font-size:0.85rem;">여기에 단어가 배열됩니다...</span>
      </div>
      <div class="word-bank" id="wo-bank">
        ${shuffled.map((w, i) => `<button class="word-chip" data-idx="${i}" data-word="${w}" onclick="currentQuiz.selectWord(this)">${w}</button>`).join('')}
      </div>
      <div style="display:flex;gap:8px;margin-top:16px;">
        <button class="btn-outline" style="flex:1" onclick="currentQuiz.resetWords()">초기화 ↺</button>
        <button class="btn-primary" style="flex:1" id="wo-submit" onclick="currentQuiz.checkOrder()" disabled>확인 ✓</button>
      </div>
    `;
  }

  selectWord(btn) {
    if (this.answered) return;
    btn.classList.add('selected');
    this.selectedWords.push(btn.dataset.word);

    const area = document.getElementById('wo-answer');
    if (this.selectedWords.length === 1) area.innerHTML = '';
    area.classList.add('active');

    const placed = document.createElement('span');
    placed.className = 'placed-word';
    placed.textContent = btn.dataset.word;
    placed.onclick = () => this.removeWord(btn, placed);
    area.appendChild(placed);

    // Enable submit when all words placed
    const allChips = this.container.querySelectorAll('.word-chip');
    const allSelected = [...allChips].every(c => c.classList.contains('selected'));
    document.getElementById('wo-submit').disabled = !allSelected;
  }

  removeWord(chipBtn, placedEl) {
    if (this.answered) return;
    chipBtn.classList.remove('selected');
    this.selectedWords = this.selectedWords.filter(w => w !== chipBtn.dataset.word);
    placedEl.remove();

    const area = document.getElementById('wo-answer');
    if (this.selectedWords.length === 0) {
      area.innerHTML = '<span style="color:var(--c-text-muted);font-size:0.85rem;">여기에 단어가 배열됩니다...</span>';
      area.classList.remove('active');
    }
    document.getElementById('wo-submit').disabled = true;
  }

  resetWords() {
    if (this.answered) return;
    this.selectedWords = [];
    this.container.querySelectorAll('.word-chip').forEach(c => c.classList.remove('selected'));
    const area = document.getElementById('wo-answer');
    area.innerHTML = '<span style="color:var(--c-text-muted);font-size:0.85rem;">여기에 단어가 배열됩니다...</span>';
    area.classList.remove('active');
    document.getElementById('wo-submit').disabled = true;
  }

  checkOrder() {
    if (this.answered) return;
    const q = this.questions[this.current];
    const userAnswer = this.selectedWords.join(' ');
    const correct = userAnswer.toLowerCase().replace(/\s+/g, ' ').trim() ===
                    q.a.toLowerCase().replace(/\s+/g, ' ').trim();

    const area = document.getElementById('wo-answer');
    area.style.borderColor = correct ? 'var(--c-success)' : 'var(--c-danger)';

    this.showFeedback(correct, null, q.a);
  }

  shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }
}
