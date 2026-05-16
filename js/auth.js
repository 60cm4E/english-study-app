// Auth — Google Login + Profile
let currentUser = null;

async function handleLogin() {
  if (isFirebaseReady()) {
    try {
      const provider = new firebase.auth.GoogleAuthProvider();
      const result = await firebaseAuth.signInWithPopup(provider);
      currentUser = result.user;
      Storage.profile = { uid: currentUser.uid, name: currentUser.displayName, photo: currentUser.photoURL };
      await Storage.syncFromCloud(currentUser.uid);
      updateAuthUI();
      navigate(Storage.profile.school ? 'lessons' : 'select-school');
    } catch(e) { console.error('Login failed:', e); demoLogin(); }
  } else {
    demoLogin();
  }
}

function demoLogin() {
  // Firebase 미설정 시 데모 모드
  currentUser = { uid: 'demo', displayName: '학생', photoURL: '' };
  Storage.profile = { uid: 'demo', name: '학생', photo: '' };
  updateAuthUI();
  navigate(Storage.profile.school ? 'lessons' : 'select-school');
}

async function handleLogout() {
  if (isFirebaseReady() && currentUser) {
    await Storage.syncToCloud(currentUser.uid);
    await firebaseAuth.signOut();
  }
  currentUser = null;
  updateAuthUI();
  navigate('home');
}

function updateAuthUI() {
  const loginBtn = document.getElementById('login-btn');
  const userInfo = document.getElementById('user-info');
  const avatar = document.getElementById('user-avatar');
  const xpDisplay = document.getElementById('xp-display');
  const xpCount = document.getElementById('xp-count');

  if (currentUser) {
    loginBtn.classList.add('hidden');
    userInfo.classList.remove('hidden');
    xpDisplay.classList.remove('hidden');
    avatar.src = currentUser.photoURL || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="%236366f1"/><text x="50" y="65" text-anchor="middle" fill="white" font-size="40">😊</text></svg>';
    xpCount.textContent = Storage.xp;
  } else {
    loginBtn.classList.remove('hidden');
    userInfo.classList.add('hidden');
    xpDisplay.classList.add('hidden');
  }
}

// Auto-login check
if (isFirebaseReady()) {
  firebaseAuth.onAuthStateChanged(user => {
    if (user) {
      currentUser = user;
      Storage.profile = Storage.profile || { uid: user.uid, name: user.displayName, photo: user.photoURL };
      updateAuthUI();
    }
  });
} else if (Storage.profile) {
  currentUser = { uid: Storage.profile.uid, displayName: Storage.profile.name, photoURL: Storage.profile.photo };
  updateAuthUI();
}
