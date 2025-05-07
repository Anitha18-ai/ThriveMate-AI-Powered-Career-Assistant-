// Firebase Configuration

// Initialize Firebase
function initializeFirebase(apiKey, projectId, appId) {
    // Firebase configuration
    const firebaseConfig = {
        apiKey: apiKey,
        authDomain: `${projectId}.firebaseapp.com`,
        projectId: projectId,
        storageBucket: `${projectId}.appspot.com`,
        messagingSenderId: '',
        appId: appId
    };
    
    // Initialize Firebase
    firebase.initializeApp(firebaseConfig);
    
    // Initialize Firebase services
    const auth = firebase.auth();
    const storage = firebase.storage();
    const db = firebase.firestore();
    
    return { auth, storage, db };
}

// Upload resume to Firebase Storage
function uploadResumeToStorage(file, userId) {
    return new Promise((resolve, reject) => {
        // Check if user is authenticated
        if (!firebase.auth().currentUser) {
            reject(new Error('User is not authenticated'));
            return;
        }
        
        // Create a storage reference
        const storageRef = firebase.storage().ref();
        const resumeRef = storageRef.child(`resumes/${userId}/${Date.now()}_${file.name}`);
        
        // Upload file
        const uploadTask = resumeRef.put(file);
        
        // Monitor upload progress
        uploadTask.on('state_changed', 
            // Progress function
            (snapshot) => {
                const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
                console.log('Upload is ' + progress + '% done');
            }, 
            // Error function
            (error) => {
                reject(error);
            }, 
            // Complete function
            () => {
                // Get download URL
                uploadTask.snapshot.ref.getDownloadURL().then((downloadURL) => {
                    resolve({
                        url: downloadURL,
                        path: resumeRef.fullPath,
                        name: file.name,
                        contentType: file.type,
                        size: file.size
                    });
                });
            }
        );
    });
}

// Save resume analysis to Firestore
function saveResumeAnalysis(userId, resumeData, analysisResults) {
    return new Promise((resolve, reject) => {
        // Check if user is authenticated
        if (!firebase.auth().currentUser) {
            reject(new Error('User is not authenticated'));
            return;
        }
        
        // Create document data
        const docData = {
            userId: userId,
            resumeUrl: resumeData.url,
            resumePath: resumeData.path,
            resumeName: resumeData.name,
            analysisResults: analysisResults,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        };
        
        // Add document to collection
        firebase.firestore().collection('resumeAnalyses')
            .add(docData)
            .then((docRef) => {
                resolve(docRef.id);
            })
            .catch((error) => {
                reject(error);
            });
    });
}

// Get user's resume analyses
function getUserResumeAnalyses(userId) {
    return new Promise((resolve, reject) => {
        // Check if user is authenticated
        if (!firebase.auth().currentUser) {
            reject(new Error('User is not authenticated'));
            return;
        }
        
        // Query documents
        firebase.firestore().collection('resumeAnalyses')
            .where('userId', '==', userId)
            .orderBy('createdAt', 'desc')
            .get()
            .then((querySnapshot) => {
                const analyses = [];
                querySnapshot.forEach((doc) => {
                    const data = doc.data();
                    analyses.push({
                        id: doc.id,
                        ...data,
                        createdAt: data.createdAt ? data.createdAt.toDate() : null
                    });
                });
                resolve(analyses);
            })
            .catch((error) => {
                reject(error);
            });
    });
}

// Save job search to Firestore
function saveJobSearch(userId, searchParams, results) {
    return new Promise((resolve, reject) => {
        // Check if user is authenticated
        if (!firebase.auth().currentUser) {
            reject(new Error('User is not authenticated'));
            return;
        }
        
        // Create document data
        const docData = {
            userId: userId,
            searchParams: searchParams,
            resultCount: results.length,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        };
        
        // Add document to collection
        firebase.firestore().collection('jobSearches')
            .add(docData)
            .then((docRef) => {
                resolve(docRef.id);
            })
            .catch((error) => {
                reject(error);
            });
    });
}
