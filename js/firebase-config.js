// Firebase Configuration
// TODO: 실제 Firebase 프로젝트 설정으로 교체 필요
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Firebase 초기화 (설정이 유효할 때만)
let firebaseApp = null;
let firebaseAuth = null;
let firebaseDB = null;

try {
  if (firebaseConfig.apiKey !== "YOUR_API_KEY") {
    firebaseApp = firebase.initializeApp(firebaseConfig);
    firebaseAuth = firebase.auth();
    firebaseDB = firebase.firestore();
  }
} catch(e) {
  console.warn('Firebase not configured. Running in offline mode.');
}

function isFirebaseReady() {
  return firebaseApp !== null;
}
