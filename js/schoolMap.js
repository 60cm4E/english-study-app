// School-Textbook Mapping
const SCHOOL_MAP = {
  chilbo:    { name: '칠보중', emoji: '🏫', examType: 'writing', grades: { 1: 'donga-yoon-22-g1', 2: 'donga-yoon-22', 3: 'donga-lee-15' }},
  homae:     { name: '호매실중', emoji: '🎓', examType: 'mixed', grades: { 1: 'ybm-park-22-g1', 2: 'ybm-park-22', 3: 'donga-yoon-15' }},
  neungsil:  { name: '능실중', emoji: '📖', examType: 'mixed', grades: { 1: 'donga-yoon-22-g1', 2: 'donga-yoon-22', 3: 'neungyul-kim-15' }},
  sangchon:  { name: '상촌중', emoji: '✏️', examType: 'mixed', grades: { 1: 'donga-yoon-22-g1', 2: 'donga-yoon-22', 3: 'donga-yoon-15' }}
};

const TEXTBOOK_NAMES = {
  'donga-yoon-22-g1': '동아(윤정미) 22개정 중1',
  'donga-yoon-22': '동아(윤정미) 22개정',
  'ybm-park-22-g1': 'YBM(박준언) 22개정 중1',
  'ybm-park-22': 'YBM(박준언) 22개정',
  'donga-lee-15': '동아(이병민) 15개정',
  'donga-yoon-15': '동아(윤정미) 15개정',
  'neungyul-kim-15': '능률(김성곤) 15개정'
};

// 현재 사용 가능한 레슨 (추후 동적 관리)
const AVAILABLE_LESSONS = {
  'donga-yoon-22-g1': [1, 2, 3, 4, 5, 6, 7, 8],
  'donga-yoon-22': [1, 2, 3],
  'ybm-park-22-g1': [1, 2, 3, 4, 5, 6, 7, 8],
  'ybm-park-22': [1, 2, 3],
  'donga-lee-15': [1, 2, 3, 4, 5, 6, 7, 8],
  'donga-yoon-15': [1, 2, 3, 4, 5, 6, 7, 8],
  'neungyul-kim-15': [1, 2, 3, 4, 5, 6, 7]
};

function getTextbook(schoolId, grade) {
  return SCHOOL_MAP[schoolId]?.grades[grade] || null;
}

function getTextbookName(textbookId) {
  return TEXTBOOK_NAMES[textbookId] || textbookId;
}

function getAvailableLessons(textbookId) {
  return AVAILABLE_LESSONS[textbookId] || [];
}
