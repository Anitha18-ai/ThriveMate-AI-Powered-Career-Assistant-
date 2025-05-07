// Job Recommender JavaScript

let currentPage = 1;
const pageSize = 10;
let totalJobs = 0;
let currentKeywords = '';
let currentLocation = '';
let isLoading = false;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize search form
    initializeSearchForm();
    
    // Check URL parameters for search
    checkUrlParameters();
    
    // Initialize pagination
    initializePagination();
});

// Initialize search form
function initializeSearchForm() {
    const searchForm = document.getElementById('job-search-form');
    
    if (!searchForm) return;
    
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const keywordsInput = document.getElementById('keywords-input');
        const locationInput = document.getElementById('location-input');
        
        if (!keywordsInput) return;
        
        const keywords = keywordsInput.value.trim();
        const location = locationInput ? locationInput.value.trim() : '';
        
        if (!keywords) {
            showToast('Error', 'Please enter job title, skills, or keywords');
            return;
        }
        
        // Reset to first page
        currentPage = 1;
        
        // Search jobs
        searchJobs(keywords, location);
    });
}

// Check URL parameters for search terms
function checkUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const keywords = urlParams.get('keywords');
    const location = urlParams.get('location');
    
    if (keywords) {
        const keywordsInput = document.getElementById('keywords-input');
        if (keywordsInput) {
            keywordsInput.value = keywords;
        }
        
        if (location) {
            const locationInput = document.getElementById('location-input');
            if (locationInput) {
                locationInput.value = location;
            }
        }
        
        // Search jobs with URL parameters
        searchJobs(keywords, location || '');
    }
}

// Initialize pagination controls
function initializePagination() {
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    
    if (!prevPageBtn || !nextPageBtn) return;
    
    prevPageBtn.addEventListener('click', function() {
        if (currentPage > 1 && !isLoading) {
            currentPage--;
            searchJobs(currentKeywords, currentLocation);
        }
    });
    
    nextPageBtn.addEventListener('click', function() {
        if (currentPage * pageSize < totalJobs && !isLoading) {
            currentPage++;
            searchJobs(currentKeywords, currentLocation);
        }
    });
}

// Search for jobs
function searchJobs(keywords, location) {
    // Update current search parameters
    currentKeywords = keywords;
    currentLocation = location;
    
    // Show loading indicator
    const loadingIndicator = document.getElementById('jobs-loading');
    const resultsContainer = document.getElementById('jobs-results');
    const noResultsMessage = document.getElementById('no-jobs-found');
    
    if (loadingIndicator) loadingIndicator.classList.remove('d-none');
    if (resultsContainer) resultsContainer.classList.add('d-none');
    if (noResultsMessage) noResultsMessage.classList.add('d-none');
    
    isLoading = true;
    
    // Make API request
    fetch('/api/search-jobs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            keywords: keywords,
            location: location,
            page: currentPage,
            page_size: pageSize
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading indicator
        if (loadingIndicator) loadingIndicator.classList.add('d-none');
        isLoading = false;
        
        // Store total jobs count
        totalJobs = data.total_jobs || 0;
        
        // Update pagination info
        updatePagination();
        
        // Display results
        displayJobs(data.jobs || []);
        
        // Show no results message if needed
        if (data.jobs && data.jobs.length === 0) {
            if (noResultsMessage) noResultsMessage.classList.remove('d-none');
        } else {
            if (resultsContainer) resultsContainer.classList.remove('d-none');
        }
        
        // Update search summary
        updateSearchSummary(data.total_jobs || 0);
    })
    .catch(error => {
        // Hide loading indicator
        if (loadingIndicator) loadingIndicator.classList.add('d-none');
        isLoading = false;
        
        // Show error message
        showToast('Error', error.message);
    });
}

// Display job results
function displayJobs(jobs) {
    const jobsList = document.getElementById('jobs-list');
    if (!jobsList) return;
    
    // Clear previous results
    jobsList.innerHTML = '';
    
    // Add job cards
    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.className = 'card job-card mb-3';
        
        // Format date 
        const publishedDate = job.date ? formatRelativeTime(job.date) : '';
        
        // Format salary
        let salaryText = 'Salary not specified';
        if (job.salary_min && job.salary_max) {
            salaryText = `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`;
            if (job.salary_period) {
                salaryText += ` per ${job.salary_period}`;
            }
        }
        
        jobCard.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title">${job.title || 'Untitled Position'}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">${job.company || 'Unknown Company'}</h6>
                    </div>
                    ${job.company_logo ? `<img src="${job.company_logo}" alt="${job.company}" class="company-logo" style="max-width: 60px; max-height: 60px;">` : ''}
                </div>
                <div class="mb-3">
                    <i class="bi bi-geo-alt me-1"></i> ${job.location || 'Location not specified'}
                </div>
                <div class="mb-3">
                    <i class="bi bi-cash me-1"></i> ${salaryText}
                </div>
                <p class="card-text job-description">${job.description ? truncateText(job.description, 200) : 'No description available'}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        <i class="bi bi-clock me-1"></i> ${publishedDate}
                    </small>
                    <a href="${job.url || '#'}" target="_blank" class="btn btn-primary btn-sm">View Job</a>
                </div>
            </div>
        `;
        
        jobsList.appendChild(jobCard);
    });
}

// Update pagination controls
function updatePagination() {
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const currentPageSpan = document.getElementById('current-page');
    const totalPagesSpan = document.getElementById('total-pages');
    
    if (!prevPageBtn || !nextPageBtn || !currentPageSpan || !totalPagesSpan) return;
    
    // Calculate total pages
    const totalPages = Math.ceil(totalJobs / pageSize) || 1;
    
    // Update current page and total pages
    currentPageSpan.textContent = currentPage;
    totalPagesSpan.textContent = totalPages;
    
    // Update button states
    prevPageBtn.disabled = currentPage <= 1;
    nextPageBtn.disabled = currentPage >= totalPages;
}

// Update search summary
function updateSearchSummary(totalJobs) {
    const searchSummary = document.getElementById('search-summary');
    if (!searchSummary) return;
    
    const startItem = (currentPage - 1) * pageSize + 1;
    const endItem = Math.min(currentPage * pageSize, totalJobs);
    
    if (totalJobs > 0) {
        searchSummary.innerHTML = `
            Showing jobs <strong>${startItem}-${endItem}</strong> of <strong>${totalJobs}</strong> 
            for <strong>${currentKeywords}</strong>
            ${currentLocation ? ` in <strong>${currentLocation}</strong>` : ''}
        `;
    } else {
        searchSummary.innerHTML = `
            No jobs found for <strong>${currentKeywords}</strong>
            ${currentLocation ? ` in <strong>${currentLocation}</strong>` : ''}
        `;
    }
}

// Helper function to truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}
