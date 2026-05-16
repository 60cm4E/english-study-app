// App — SPA Router + Page Rendering (10 모듈 버전)
let currentQuiz = null;

// ============================================
// Router
// ============================================
function navigate(path) { location.hash = path; }
function getRoute() { return location.hash.slice(1) || 'home'; }

window.addEventListener('hashchange', () => routePage());
window.addEventListener('load', () => routePage());

function routePage() {
  const route = getRoute();
  const content = document.getElementById('content');
  const backBtn = document.getElementById('nav-back');
  const navTitle = document.getElementById('nav-title');

  document.querySelectorAll('.report-btn').forEach(b => b.remove());
  currentQuiz = null;

  backBtn.classList.toggle('hidden', route === 'home');

  const patterns = [
    [/^home$/, () => { navTitle.textContent = '📚 영어 자기학습'; renderHome(content); }],
    [/^select-school$/, () => { navTitle.textContent = '학교 선택'; renderSchoolSelect(content); }],
    [/^lessons$/, () => { navTitle.textContent = '단원 목록'; renderLessons(content); }],
    [/^study\/(.+)\/(\d+)$/, (m) => { navTitle.textContent = `Lesson ${m[2]}`; renderLessonDashboard(content, m[1], +m[2]); }],
    [/^quiz\/(.+)\/(\d+)\/(.+)$/, (m) => { navTitle.textContent = m[3]; launchModule(content, m[1], +m[2], m[3]); }],
  ];

  for (const [re, fn] of patterns) {
    const m = route.match(re);
    if (m) { fn(m); return; }
  }
  content.innerHTML = '<div class="text-center mt-xl"><h2>페이지를 찾을 수 없습니다</h2><button class="btn-primary mt-md" onclick="navigate(\'home\')">홈으로</button></div>';
}

// ============================================
// Home
// ============================================
function renderHome(el) {
  if (currentUser) { navigate(Storage.profile?.school ? 'lessons' : 'select-school'); return; }
  el.innerHTML = `
    <div class="login-hero anim-fade">
      <div class="hero-emoji">📚</div>
      <h1>영어 자기학습</h1>
      <p>중학교 영어 교과서를 인터랙티브하게 학습하세요!<br>단어, 의사소통, 리딩, 문법을 단계별로 마스터!</p>
      <button class="google-btn" onclick="handleLogin()">
        <svg viewBox="0 0 24 24" width="20"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
        Google로 시작하기
      </button>
      <p style="color:var(--c-text-muted);font-size:0.8rem;margin-top:16px;">Google 계정으로 로그인하면 진도가 자동 저장됩니다</p>
    </div>`;
}

// ============================================
// School Select
// ============================================
function renderSchoolSelect(el) {
  el.innerHTML = `
    <div class="page-header anim-fade"><h1>🏫 학교와 학년을 선택하세요</h1><p>선택한 정보에 맞는 교과서로 학습합니다</p></div>
    <div class="card-grid stagger">
      ${Object.entries(SCHOOL_MAP).map(([id, s]) => `
        <div class="school-card" data-school="${id}">
          <div class="school-emoji">${s.emoji}</div>
          <div class="school-name">${s.name}</div>
          <div class="school-sub">${s.examType === 'writing' ? '서술형 10문제' : '객관식20+서술형2'}</div>
          <div class="grade-pills">
            <button class="grade-pill" onclick="selectSchool('${id}',2)">2학년</button>
            <button class="grade-pill" onclick="selectSchool('${id}',3)">3학년</button>
          </div>
        </div>
      `).join('')}
    </div>`;
}

function selectSchool(schoolId, grade) {
  const p = Storage.profile || {};
  p.school = schoolId; p.grade = grade; p.textbook = getTextbook(schoolId, grade);
  Storage.profile = p;
  navigate('lessons');
}

// ============================================
// Lessons
// ============================================
function renderLessons(el) {
  const p = Storage.profile;
  if (!p?.textbook) { navigate('select-school'); return; }
  const school = SCHOOL_MAP[p.school];
  const lessons = getAvailableLessons(p.textbook);

  el.innerHTML = `
    <div class="page-header anim-fade">
      <h1>${school.emoji} ${school.name} ${p.grade}학년</h1>
      <p>${getTextbookName(p.textbook)}</p>
      <button class="btn-outline btn-sm mt-sm" onclick="navigate('select-school')">학교/학년 변경</button>
    </div>
    <div class="flex flex-col gap-md stagger">
      ${lessons.length ? lessons.map(l => {
        const prog = getOverallProgress(`${p.textbook}/lesson${l}`);
        return `<div class="lesson-card" onclick="navigate('study/${p.textbook}/${l}')">
          <div class="lesson-num">${l}</div>
          <div class="lesson-info">
            <div class="lesson-title">Lesson ${l}</div>
            <div class="lesson-progress">${prog > 0 ? `진도 ${prog}%` : '시작하기'}</div>
            <div class="progress-bar"><div class="progress-fill" style="width:${prog}%"></div></div>
          </div>
        </div>`;
      }).join('') : `<div class="card text-center" style="padding:48px;">
        <div style="font-size:3rem;margin-bottom:16px;">📝</div>
        <h3>아직 등록된 단원이 없습니다</h3>
        <p style="color:var(--c-text-dim);margin-top:8px;">시험범위가 확정되면 단원이 추가됩니다</p>
      </div>`}
    </div>`;
}

function getOverallProgress(key) {
  const parts = ['flashcard','spelling','fill-blank','multi-choice','true-false','word-order','error-correction','writing','match','sentence'];
  let total = 0, count = 0;
  parts.forEach(p => {
    const pr = Storage.getProgress(`${key}/${p}`);
    if (pr.score > 0) { total += pr.score; count++; }
  });
  return count > 0 ? Math.round(total / count) : 0;
}

// ============================================
// Lesson Dashboard — 10개 모듈 전부 표시
// ============================================
function renderLessonDashboard(el, textbook, lesson) {
  const key = `${textbook}/lesson${lesson}`;

  const modules = [
    { id: 'flashcard',         icon: '🔤', title: '단어 카드',     desc: '카드 뒤집기로 단어 암기',       color: '--c-vocab' },
    { id: 'spelling',          icon: '✍️', title: '스펠링 퀴즈',  desc: '한글 뜻 보고 영어 타이핑',      color: '--c-vocab' },
    { id: 'match',             icon: '🎮', title: '매칭 게임',     desc: '영어↔한글 카드 짝 맞추기',     color: '--c-vocab' },
    { id: 'fill-blank',        icon: '✏️', title: '빈칸 채우기',  desc: '빈칸에 알맞은 단어 넣기',       color: '--c-comm' },
    { id: 'multi-choice',      icon: '📝', title: '객관식',       desc: '알맞은 답 고르기',              color: '--c-comm' },
    { id: 'true-false',        icon: '⭕', title: '참/거짓',      desc: '내용 일치 여부 판단',           color: '--c-reading' },
    { id: 'word-order',        icon: '🔀', title: '어순 배열',    desc: '단어를 올바른 순서로 배열',      color: '--c-grammar' },
    { id: 'error-correction',  icon: '🔍', title: '오류 수정',    desc: '틀린 부분 찾아 고치기',         color: '--c-grammar' },
    { id: 'sentence',          icon: '🏗️', title: '문장 만들기',  desc: '한글 보고 영어 문장 작성',      color: '--c-grammar' },
    { id: 'writing',           icon: '📄', title: '서술형',       desc: '직접 영작하기 (칠보중 모드)',    color: '--c-accent2' },
  ];

  el.innerHTML = `
    <div class="page-header anim-fade">
      <h1>Lesson ${lesson}</h1>
      <p>${getTextbookName(textbook)}</p>
    </div>

    <h3 style="color:var(--c-vocab);margin-bottom:8px;">🔤 단어 학습</h3>
    <div class="card-grid stagger mb-md">
      ${modules.slice(0, 3).map(m => moduleCard(key, textbook, lesson, m)).join('')}
    </div>

    <h3 style="color:var(--c-comm);margin:24px 0 8px;">💬 의사소통 · 리딩</h3>
    <div class="card-grid stagger mb-md">
      ${modules.slice(3, 6).map(m => moduleCard(key, textbook, lesson, m)).join('')}
    </div>

    <h3 style="color:var(--c-grammar);margin:24px 0 8px;">📝 문법 · 영작</h3>
    <div class="card-grid stagger">
      ${modules.slice(6).map(m => moduleCard(key, textbook, lesson, m)).join('')}
    </div>
  `;
}

function moduleCard(key, tb, lesson, m) {
  const prog = Storage.getProgress(`${key}/${m.id}`);
  return `<div class="part-card" onclick="navigate('quiz/${tb}/${lesson}/${m.id}')">
    <div class="part-icon">${m.icon}</div>
    <div class="part-title">${m.title}</div>
    <div class="part-desc">${m.desc}</div>
    <div class="progress-bar mt-sm"><div class="progress-fill" style="width:${prog.score||0}%"></div></div>
    <div class="progress-text"><span>${prog.score ? prog.score+'%' : '시작 전'}</span></div>
  </div>`;
}

// ============================================
// Module Launcher — 각 모듈별 전용 인스턴스 생성
// ============================================
async function launchModule(el, textbook, lesson, moduleId) {
  el.innerHTML = '<div class="text-center mt-xl"><div style="font-size:2rem">⏳</div><p>로딩 중...</p></div>';

  const content = await loadContent(textbook, lesson);
  const wordtest = await loadWordTest(textbook, lesson);
  const pKey = `${textbook}/lesson${lesson}/${moduleId}`;

  if (!content && !wordtest) {
    el.innerHTML = '<div class="text-center mt-xl"><h2>콘텐츠 없음</h2><button class="btn-primary mt-md" onclick="history.back()">돌아가기</button></div>';
    return;
  }

  switch (moduleId) {
    case 'flashcard':
      if (wordtest?.words) { currentQuiz = new FlashCardModule(el, wordtest.words.slice(0, 20), pKey); currentQuiz.start(); }
      break;

    case 'spelling':
      if (wordtest?.words) { currentQuiz = new SpellingQuiz(el, wordtest.words.slice(0, 15), pKey, '🔤 스펠링 퀴즈'); currentQuiz.start(); }
      break;

    case 'match':
      if (wordtest?.words) { currentQuiz = new MatchGame(el, wordtest.words.slice(0, 8), pKey); currentQuiz.start(); }
      break;

    case 'fill-blank': {
      const qs = gatherByType(content, ['fill-blank']);
      if (qs.length) { currentQuiz = new FillBlankQuiz(el, qs, pKey, '✏️ 빈칸 채우기'); currentQuiz.start(); }
      else noQuestions(el);
      break;
    }

    case 'multi-choice': {
      const qs = gatherByType(content, ['multi-choice']);
      if (qs.length) { currentQuiz = new MultiChoiceQuiz(el, qs, pKey, '📝 객관식'); currentQuiz.start(); }
      else noQuestions(el);
      break;
    }

    case 'true-false': {
      const qs = gatherByType(content, ['true-false']);
      if (qs.length) { currentQuiz = new TrueFalseQuiz(el, qs, pKey, '⭕ 참/거짓'); currentQuiz.start(); }
      else noQuestions(el);
      break;
    }

    case 'word-order': {
      const qs = gatherByType(content, ['word-order']);
      if (qs.length) { currentQuiz = new WordOrderQuiz(el, qs, pKey, '🔀 어순 배열'); currentQuiz.start(); }
      else noQuestions(el);
      break;
    }

    case 'error-correction': {
      const qs = gatherByType(content, ['error-correction']);
      if (qs.length) { currentQuiz = new ErrorCorrectionQuiz(el, qs, pKey, '🔍 오류 수정'); currentQuiz.start(); }
      else noQuestions(el);
      break;
    }

    case 'sentence': {
      const qs = buildSentenceQuestions(content);
      if (qs.length) { currentQuiz = new SentenceBuilder(el, qs, pKey, '🏗️ 문장 만들기'); currentQuiz.start(); }
      else noQuestions(el);
      break;
    }

    case 'writing': {
      const qs = buildWritingQuestions(content);
      if (qs.length) { currentQuiz = new WritingModeQuiz(el, qs, pKey, '📄 서술형'); currentQuiz.start(); }
      else noQuestions(el);
      break;
    }

    default:
      el.innerHTML = '<div class="text-center mt-xl"><h2>알 수 없는 모듈</h2></div>';
  }
}

// ============================================
// Data Gathering Helpers
// ============================================
function gatherByType(content, types) {
  if (!content) return [];
  const all = [];
  ['communication', 'reading', 'grammar'].forEach(section => {
    const exercises = content[section]?.exercises;
    if (exercises) all.push(...exercises.filter(e => types.includes(e.type)));
  });
  return shuffle(all);
}

function buildSentenceQuestions(content) {
  if (!content) return [];
  const qs = [];
  // From reading passages — 한글 → 영어
  if (content.reading?.passages) {
    content.reading.passages.forEach(p => {
      if (p.en && p.ko) {
        // 본문에서 핵심 문장 추출 (1~2문장씩)
        const sentences = p.en.split(/(?<=[.!?])\s+/).filter(s => s.length > 10 && s.length < 80);
        const koSentences = p.ko.split(/(?<=[.!?다])\s+/);
        sentences.slice(0, 2).forEach((en, i) => {
          qs.push({ q: koSentences[i] || p.ko.slice(0, 50), ko: koSentences[i], a: en });
        });
      }
    });
  }
  // From grammar examples
  if (content.grammar?.points) {
    content.grammar.points.forEach(pt => {
      pt.examples?.forEach(ex => {
        if (ex.en && ex.ko) qs.push({ q: ex.ko, ko: ex.ko, a: ex.en });
      });
    });
  }
  return shuffle(qs).slice(0, 10);
}

function buildWritingQuestions(content) {
  if (!content) return [];
  const qs = [];
  if (content.communication?.keyExpressions) {
    content.communication.keyExpressions.forEach(e => {
      qs.push({ q: `다음을 영어로 써보세요: "${e.ko}"`, ko: e.ko, a: e.en, hint: e.category });
    });
  }
  if (content.reading?.passages) {
    content.reading.passages.slice(0, 3).forEach(p => {
      const sentences = p.en.split(/(?<=[.!?])\s+/).filter(s => s.length > 15 && s.length < 60);
      const koSentences = p.ko.split(/(?<=[.!?다])\s+/);
      sentences.slice(0, 1).forEach((en, i) => {
        qs.push({ q: `다음을 영어로 써보세요: "${koSentences[i] || ''}"`, ko: koSentences[i], a: en });
      });
    });
  }
  return shuffle(qs).slice(0, 8);
}

function noQuestions(el) {
  el.innerHTML = '<div class="text-center mt-xl"><div style="font-size:2rem">📭</div><h3>이 유형의 문제가 아직 없습니다</h3><button class="btn-primary mt-md" onclick="history.back()">돌아가기</button></div>';
}

// ============================================
// Utils
// ============================================
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
