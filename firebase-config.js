// TODO: Replace with your actual Firebase project config
const firebaseConfig = {
  apiKey: "AIzaSyBCghm5U6rJpJi-pqMAlFjqlst1IOLQRps",
  authDomain: "audiototext-ff04f.firebaseapp.com",
  projectId: "audiototext-ff04f",
  storageBucket: "audiototext-ff04f.firebasestorage.app",
  messagingSenderId: "805660366216",
  appId: "1:805660366216:web:86e978c602c8c4f9c1d63d",
  measurementId: "G-ZBQVC10CEP"
};

const app = firebase.apps.length > 0 ? firebase.app() : firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// Make functions available globally so non-module scripts can easily access them
window.firebaseAuth = auth;
window.firebaseDb = db;
window.onAuthStateChanged = (authObj, cb) => authObj.onAuthStateChanged(cb);

window.signUpUser = async (email, password) => {
    const userCredential = await auth.createUserWithEmailAndPassword(email, password);
    const user = userCredential.user;
    
    // Create initial user doc
    await db.collection("users").doc(user.uid).set({
        email: user.email,
        createdAt: new Date().toISOString()
    });
    return userCredential;
};

window.loginUser = async (email, password) => {
    return auth.signInWithEmailAndPassword(email, password);
};

window.logoutUser = async () => {
    return auth.signOut();
};

window.loginWithGithub = async () => {
    const provider = new firebase.auth.GithubAuthProvider();
    try {
        const result = await auth.signInWithPopup(provider);
        const user = result.user;
        
        // Ensure user document exists in firestore
        const userDoc = await db.collection("users").doc(user.uid).get();
        if (!userDoc.exists) {
            await db.collection("users").doc(user.uid).set({
                email: user.email || (user.providerData && user.providerData.length > 0 ? user.providerData[0].email : ""),
                createdAt: new Date().toISOString()
            });
        }
        return result;
    } catch (error) {
        throw error;
    }
};

window.saveTranscriptionHistory = async (audioName, transcript) => {
    const user = auth.currentUser;
    if (!user) return; // Only save if logged in

    const historyRef = db.collection("users").doc(user.uid).collection("history");
    await historyRef.add({
        audioName: audioName,
        transcript: transcript,
        createdAt: new Date().toISOString(),
        timestamp: Date.now() // For easier sorting
    });

    // Cleanup logic: Keep only 3 latest records
    const snapshot = await historyRef.orderBy("timestamp", "desc").get();
    
    if (snapshot.size > 3) {
        // We have more than 3, delete the rest
        const docs = snapshot.docs;
        for (let i = 3; i < docs.length; i++) {
            await historyRef.doc(docs[i].id).delete();
        }
    }
};

window.getTranscriptionHistory = async () => {
    const user = auth.currentUser;
    if (!user) return [];

    const historyRef = db.collection("users").doc(user.uid).collection("history");
    const snapshot = await historyRef.orderBy("timestamp", "desc").limit(3).get();
    
    return snapshot.docs.map(doc => doc.data());
};
