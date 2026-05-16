// Storage — localStorage + Firestore batch sync
const STORAGE_KEY = 'eng-study-data';

const Storage = {
  _data: null,

  init() {
    try {
      this._data = JSON.parse(localStorage.getItem(STORAGE_KEY)) || this._default();
    } catch { this._data = this._default(); }
  },

  _default() {
    return { profile: null, progress: {}, xp: 0, level: 1, streak: 0, lastStudyDate: null };
  },

  save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(this._data));
  },

  get profile() { return this._data.profile; },
  set profile(v) { this._data.profile = v; this.save(); },

  get xp() { return this._data.xp; },
  addXP(n) {
    this._data.xp += n;
    this._data.level = Math.floor(this._data.xp / 100) + 1;
    this.save();
    this._updateXPDisplay();
  },

  get level() { return this._data.level; },
  get streak() { return this._data.streak; },

  updateStreak() {
    const today = new Date().toISOString().slice(0, 10);
    const last = this._data.lastStudyDate;
    if (last === today) return;
    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    this._data.streak = (last === yesterday) ? this._data.streak + 1 : 1;
    this._data.lastStudyDate = today;
    this.save();
  },

  getProgress(key) {
    return this._data.progress[key] || { completed: 0, total: 0, score: 0, answers: {} };
  },

  setProgress(key, data) {
    this._data.progress[key] = { ...this.getProgress(key), ...data };
    this.save();
  },

  getAllProgress() { return this._data.progress; },

  _updateXPDisplay() {
    const el = document.getElementById('xp-count');
    if (el) el.textContent = this._data.xp;
  },

  // Firestore sync
  async syncToCloud(uid) {
    if (!isFirebaseReady() || !uid) return;
    try {
      await firebaseDB.collection('users').doc(uid).set({
        profile: this._data.profile,
        progress: this._data.progress,
        xp: this._data.xp,
        level: this._data.level,
        streak: this._data.streak,
        lastStudyDate: this._data.lastStudyDate,
        updatedAt: firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });
    } catch(e) { console.warn('Sync failed:', e); }
  },

  async syncFromCloud(uid) {
    if (!isFirebaseReady() || !uid) return;
    try {
      const doc = await firebaseDB.collection('users').doc(uid).get();
      if (doc.exists) {
        const cloud = doc.data();
        // 클라우드 데이터가 더 최신이면 사용
        if (cloud.xp >= this._data.xp) {
          this._data = { ...this._default(), ...cloud };
          this.save();
        }
      }
    } catch(e) { console.warn('Cloud fetch failed:', e); }
  }
};

Storage.init();
