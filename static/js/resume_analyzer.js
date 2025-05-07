// Resume Analyzer JavaScript

let resumeFile = null;
let analysisResults = null;
let extractedSkills = [];

document.addEventListener('DOMContentLoaded', function() {
    // Initialize file upload area
    initializeFileUpload();
    
    // Initialize form submission
    initializeAnalyzeForm();
});

// Initialize file upload area
function initializeFileUpload() {
    const uploadArea = document.getElementById('resume-upload-area');
    const fileInput = document.getElementById('resume-file');
    const fileInfo = document.getElementById('file-info');
    
    if (!uploadArea || !fileInput) return;
    
    // Handle click on upload area
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Handle drag over
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('border-primary');
    });
    
    // Handle drag leave
    uploadArea.addEventListener('dragleave', function() {
        uploadArea.classList.remove('border-primary');
    });
    
    // Handle drop
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('border-primary');
        
        if (e.dataTransfer.files.length) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });
    
    // Handle file selection via input
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length) {
            handleFileSelection(fileInput.files[0]);
        }
    });
    
    // Function to handle file selection
    function handleFileSelection(file) {
        // Check if file is PDF or DOC/DOCX
        const fileType = file.type;
        if (fileType !== 'application/pdf' && 
            fileType !== 'application/msword' && 
            fileType !== 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
            showToast('Error', 'Please upload a PDF or Word document');
            return;
        }
        
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showToast('Error', 'File size must be less than 5MB');
            return;
        }
        
        // Update UI with file info
        resumeFile = file;
        fileInfo.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-file-earmark-text me-2 fs-4"></i>
                <div>
                    <div class="fw-bold">${file.name}</div>
                    <div class="text-muted small">${formatFileSize(file.size)}</div>
                </div>
                <button type="button" class="btn-close ms-3" id="remove-file" aria-label="Remove file"></button>
            </div>
        `;
        
        // Show file info and analyze button
        fileInfo.classList.remove('d-none');
        document.getElementById('analyze-button').disabled = false;
        
        // Add event listener to remove button
        document.getElementById('remove-file').addEventListener('click', function(e) {
            e.stopPropagation();
            removeFile();
        });
    }
    
    // Function to remove selected file
    function removeFile() {
        resumeFile = null;
        fileInput.value = '';
        fileInfo.classList.add('d-none');
        document.getElementById('analyze-button').disabled = true;
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + ' bytes';
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(1) + ' KB';
        } else {
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
    }
}

// Initialize analyze form
function initializeAnalyzeForm() {
    const analyzeForm = document.getElementById('analyze-form');
    const resultsContainer = document.getElementById('results-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    if (!analyzeForm) return;
    
    analyzeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!resumeFile) {
            showToast('Error', 'Please upload a resume');
            return;
        }
        
        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        resultsContainer.classList.add('d-none');
        
        // Create form data
        const formData = new FormData();
        formData.append('resume', resumeFile);
        
        // Make API request
        fetch('/api/analyze-resume', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Store analysis results
            analysisResults = data;
            extractedSkills = data.skills || [];
            
            // Hide loading indicator
            loadingIndicator.classList.add('d-none');
            
            // Display results
            displayResults(data);
            
            // Show results container
            resultsContainer.classList.remove('d-none');
        })
        .catch(error => {
            // Hide loading indicator
            loadingIndicator.classList.add('d-none');
            
            // Show error message
            showToast('Error', error.message);
        });
    });
}

// Display analysis results
function displayResults(data) {
    const resultsContainer = document.getElementById('results-container');
    if (!resultsContainer) return;
    
    // Create ATS score visualization
    const atsScore = data.ats_score || 0;
    const scoreColor = getScoreColor(atsScore);
    
    // Update ATS score display
    document.getElementById('ats-score-value').textContent = atsScore;
    document.getElementById('ats-score-circle').style.strokeDashoffset = (440 - (440 * atsScore / 100)).toString();
    document.getElementById('ats-score-circle').style.stroke = scoreColor;
    
    // Update skills list
    const skillsList = document.getElementById('skills-list');
    skillsList.innerHTML = '';
    
    if (data.skills && data.skills.length > 0) {
        data.skills.forEach(skill => {
            const skillItem = document.createElement('span');
            skillItem.className = 'badge bg-primary me-2 mb-2';
            skillItem.textContent = skill;
            skillsList.appendChild(skillItem);
        });
    } else {
        skillsList.innerHTML = '<p class="text-muted">No skills detected</p>';
    }
    
    // Update education list
    const educationList = document.getElementById('education-list');
    educationList.innerHTML = '';
    
    if (data.education && data.education.length > 0) {
        data.education.forEach(edu => {
            const eduItem = document.createElement('div');
            eduItem.className = 'mb-2';
            eduItem.innerHTML = `<strong>${edu.degree || 'Degree'}</strong> - ${edu.institution || 'Institution'} ${edu.year ? `(${edu.year})` : ''}`;
            educationList.appendChild(eduItem);
        });
    } else {
        educationList.innerHTML = '<p class="text-muted">No education details detected</p>';
    }
    
    // Update experience list
    const experienceList = document.getElementById('experience-list');
    experienceList.innerHTML = '';
    
    if (data.experience && data.experience.length > 0) {
        data.experience.forEach(exp => {
            const expItem = document.createElement('div');
            expItem.className = 'mb-3';
            expItem.innerHTML = `
                <div><strong>${exp.title || 'Position'}</strong> at ${exp.company || 'Company'}</div>
                <div class="text-muted small">${exp.duration || ''}</div>
                <div>${exp.description || ''}</div>
            `;
            experienceList.appendChild(expItem);
        });
    } else {
        experienceList.innerHTML = '<p class="text-muted">No experience details detected</p>';
    }
    
    // Update suggestions
    const suggestionsList = document.getElementById('suggestions-list');
    suggestionsList.innerHTML = '';
    
    if (data.suggestions && data.suggestions.length > 0) {
        data.suggestions.forEach(suggestion => {
            const suggestionItem = document.createElement('li');
            suggestionItem.className = 'mb-2';
            suggestionItem.textContent = suggestion;
            suggestionsList.appendChild(suggestionItem);
        });
    } else {
        suggestionsList.innerHTML = '<p class="text-muted">No suggestions available</p>';
    }
    
    // Update the search for jobs section with extracted skills
    const skillsKeywordsInput = document.getElementById('skills-keywords');
    if (skillsKeywordsInput && extractedSkills.length > 0) {
        skillsKeywordsInput.value = extractedSkills.slice(0, 5).join(', ');
    }
    
    // Show the job recommendation section if it exists
    const jobRecommendationSection = document.getElementById('job-recommendation-section');
    if (jobRecommendationSection) {
        jobRecommendationSection.classList.remove('d-none');
    }
}

// Get color based on score
function getScoreColor(score) {
    if (score >= 80) {
        return '#28a745'; // Green
    } else if (score >= 60) {
        return '#17a2b8'; // Blue
    } else if (score >= 40) {
        return '#ffc107'; // Yellow
    } else {
        return '#dc3545'; // Red
    }
}

// Search for jobs based on resume skills
function searchJobsFromResume() {
    const skillsKeywordsInput = document.getElementById('skills-keywords');
    const locationInput = document.getElementById('location-input');
    
    if (!skillsKeywordsInput || !locationInput) return;
    
    const keywords = skillsKeywordsInput.value.trim();
    const location = locationInput.value.trim();
    
    if (!keywords) {
        showToast('Error', 'Please enter skills or keywords');
        return;
    }
    
    // Redirect to job recommender page with parameters
    window.location.href = `/job-recommender?keywords=${encodeURIComponent(keywords)}&location=${encodeURIComponent(location)}`;
}
