// QuizBase — 공통 베이스 클래스 (모든 모듈이 상속)
class QuizBase {
  constructor(container, questions, progressKey, title) {
    this.container = container;
    this.questions = questions;
    this.progressKey = progressKey;
    this.title = title || '';
    this.current = 0;
    this.score = 0;
    this.answered = false;
    this.startTime = Date.now();
  }

  start() {
    this.current = 0;
    this.score = 0;
    this.startTime = Date.now();
    this.renderQuestion();
  }

  // ── 공통 헤더 ──
  renderHeader() {
    const pct = (this.current / this.questions.length) * 100;
    return `
      <div class="quiz-header">
        <span class="quiz-progress">${this.current + 1} / ${this.questions.length}</span>
        <span class="quiz-score">✅ ${this.score}점</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
    `;
  }

  // ── 피드백 표시 ──
  showFeedback(isCorrect, explanation, correctAnswer) {
    this.answered = true;
    if (isCorrect) this.score++;

    const fb = document.createElement('div');
    fb.className = `feedback ${isCorrect ? 'correct' : 'wrong'} anim-slide`;
    fb.innerHTML = `
      <span class="fb-icon">${isCorrect ? '🎉' : '😅'}</span>
      <strong>${isCorrect ? '정답이에요!' : `오답 — 정답: ${correctAnswer}`}</strong>
      ${explanation ? `<span class="fb-exp">💡 ${explanation}</span>` : ''}
    `;
    this.container.appendChild(fb);

    // XP micro animation
    if (isCorrect) {
      const xpPop = document.createElement('div');
      xpPop.className = 'xp-popup';
      xpPop.textContent = '+10 XP';
      this.container.appendChild(xpPop);
      setTimeout(() => xpPop.remove(), 1200);
    }

    this._addNextButton();
    this._addReportButton();
  }

  // ── 다음 문제 버튼 ──
  _addNextButton() {
    const btn = document.createElement('button');
    btn.className = 'btn-primary btn-block mt-md anim-fade';
    btn.textContent = this.current < this.questions.length - 1 ? '다음 문제 →' : '결과 보기 🏆';
    btn.onclick = () => {
      this.current++;
      if (this.current < this.questions.length) this.renderQuestion();
      else this.showResult();
    };
    this.container.appendChild(btn);
  }

  // ── 오류 신고 버튼 ──
  _addReportButton() {
    this._removeReportButton();
    const q = this.questions[this.current] || {};
    const btn = document.createElement('button');
    btn.className = 'report-btn';
    btn.title = '문제 오류 신고';
    btn.textContent = '⚠️';
    btn.onclick = () => showReportModal(this.progressKey, this.current, JSON.stringify(q).slice(0, 80));
    document.body.appendChild(btn);
    this._reportBtn = btn;
  }

  _removeReportButton() {
    if (this._reportBtn) { this._reportBtn.remove(); this._reportBtn = null; }
    document.querySelectorAll('.report-btn').forEach(b => b.remove());
  }

  // ── 결과 화면 ──
  showResult() {
    this._removeReportButton();
    const pct = Math.round((this.score / this.questions.length) * 100);
    const elapsed = Math.round((Date.now() - this.startTime) / 1000);
    const xpEarned = this.score * 10;
    Storage.addXP(xpEarned);
    Storage.updateStreak();
    Storage.setProgress(this.progressKey, { completed: this.questions.length, total: this.questions.length, score: pct });
    if (currentUser) Storage.syncToCloud(currentUser.uid);

    const emoji = pct >= 100 ? '🏆' : pct >= 80 ? '🌟' : pct >= 50 ? '👍' : '💪';
    const msg = pct >= 100 ? '완벽해요!' : pct >= 80 ? '훌륭해요!' : pct >= 50 ? '잘했어요!' : '다시 도전해봐요!';
    const mins = Math.floor(elapsed / 60);
    const secs = elapsed % 60;

    this.container.innerHTML = `
      <div class="result-card card anim-pop">
        <div class="result-emoji">${emoji}</div>
        <div class="result-score">${pct}%</div>
        <div class="result-label">${this.score} / ${this.questions.length} 정답 — ${msg}</div>
        <div class="result-time">⏱ ${mins > 0 ? mins + '분 ' : ''}${secs}초</div>
        <div class="result-xp">+${xpEarned} XP 획득! ⚡</div>
        <div class="result-actions">
          <button class="btn-outline" onclick="history.back()">← 돌아가기</button>
          <button class="btn-primary" onclick="location.reload()">다시 풀기 🔄</button>
        </div>
      </div>
    `;
  }

  // ── 유틸 ──
  shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  normalize(s) {
    return (s || '').toLowerCase().replace(/[^a-z0-9가-힣]/g, '').trim();
  }

  // Override in subclasses
  renderQuestion() { throw new Error('Override renderQuestion()'); }
}

// ── 오류 신고 모달 (공통) ──
function showReportModal(progressKey, qIndex, qPreview) {
  document.querySelectorAll('.report-modal').forEach(m => m.remove());
  const modal = document.createElement('div');
  modal.className = 'report-modal';
  modal.innerHTML = `
    <div class="report-modal-content anim-pop">
      <h3>⚠️ 문제 오류 신고</h3>
      <p style="color:var(--c-text-dim);font-size:0.85rem;margin-top:8px;">
        위치: ${progressKey} — #${qIndex + 1}
      </p>
      <textarea class="report-textarea" placeholder="어떤 오류가 있는지 설명해주세요..." id="report-text"></textarea>
      <div style="display:flex;gap:8px;margin-top:16px;">
        <button class="btn-outline" style="flex:1" onclick="this.closest('.report-modal').remove()">취소</button>
        <button class="btn-primary" style="flex:1" onclick="submitReport('${progressKey}',${qIndex})">제출</button>
      </div>
    </div>
  `;
  modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
  document.body.appendChild(modal);
}

function submitReport(pk, qi) {
  const text = document.getElementById('report-text')?.value?.trim();
  if (!text) return alert('내용을 입력해주세요.');
  if (isFirebaseReady()) {
    firebaseDB.collection('reports').add({
      userId: currentUser?.uid || 'anon', progressKey: pk, questionIndex: qi,
      message: text, status: 'open', createdAt: firebase.firestore.FieldValue.serverTimestamp()
    });
  }
  const r = JSON.parse(localStorage.getItem('eng-reports') || '[]');
  r.push({ pk, qi, text, date: new Date().toISOString() });
  localStorage.setItem('eng-reports', JSON.stringify(r));
  document.querySelector('.report-modal')?.remove();
  alert('신고가 접수되었습니다. 감사합니다! 🙏');
}
