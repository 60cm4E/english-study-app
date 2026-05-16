// Content Loader — JSON 데이터 로드 + 캐시
const ContentCache = {};

async function loadContent(textbookId, lesson) {
  const key = `${textbookId}/lesson${lesson}/content`;
  if (ContentCache[key]) return ContentCache[key];
  try {
    const res = await fetch(`data/${textbookId}/lesson${lesson}/content.json`);
    if (!res.ok) throw new Error('Not found');
    ContentCache[key] = await res.json();
    return ContentCache[key];
  } catch(e) { console.error('Content load failed:', e); return null; }
}

async function loadWordTest(textbookId, lesson) {
  const key = `${textbookId}/lesson${lesson}/wordtest`;
  if (ContentCache[key]) return ContentCache[key];
  try {
    const res = await fetch(`data/${textbookId}/lesson${lesson}/wordtest.json`);
    if (!res.ok) throw new Error('Not found');
    ContentCache[key] = await res.json();
    return ContentCache[key];
  } catch(e) { console.error('WordTest load failed:', e); return null; }
}
