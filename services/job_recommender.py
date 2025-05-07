import os
import requests
import logging
from typing import Dict, List, Any
import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def search_jobs(keywords: str, location: str = '', page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    Search for jobs using the JSearch API
    
    Args:
        keywords: Job title, skills, or keywords to search for
        location: Location for the job search (optional)
        page: Page number for pagination
        page_size: Number of results per page
        
    Returns:
        Dictionary containing job listings and metadata
    """
    logger.debug(f"Searching jobs with keywords: {keywords}, location: {location}, page: {page}")
    
    # Get API key from environment variables
    api_key = os.environ.get('JSEARCH_API_KEY', config.JSEARCH_API_KEY)
    
    if not api_key:
        logger.error("JSearch API key not found")
        return {
            "error": "API key not configured",
            "jobs": [],
            "total_jobs": 0
        }
    
    # Prepare request parameters
    url = config.JSEARCH_API_URL
    querystring = {
        "query": keywords,
        "page": str(page),
        "num_pages": "1",
        "page_size": str(page_size)
    }
    
    # Add location if provided
    if location:
        querystring["location"] = location
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    try:
        # Make the API request
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse response data
        data = response.json()
        
        # Check if request was successful
        if data.get("status") != "OK":
            logger.error(f"API request failed: {data.get('message', 'Unknown error')}")
            return {
                "error": data.get("message", "API request failed"),
                "jobs": [],
                "total_jobs": 0
            }
        
        # Extract job listings
        raw_jobs = data.get("data", [])
        processed_jobs = process_job_listings(raw_jobs)
        
        # Get total jobs count (estimate based on API response)
        total_jobs = data.get("total_jobs", len(processed_jobs))
        
        return {
            "jobs": processed_jobs,
            "total_jobs": total_jobs
        }
        
    except requests.exceptions.RequestException as e:
        logger.exception(f"Error fetching job listings: {str(e)}")
        return {
            "error": str(e),
            "jobs": [],
            "total_jobs": 0
        }

def process_job_listings(raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process raw job listings from API response into a clean format
    
    Args:
        raw_jobs: List of job listings from the API
        
    Returns:
        List of processed job listings
    """
    processed_jobs = []
    
    for job in raw_jobs:
        job_data = job.get("job_id", {})
        
        # Extract relevant fields
        processed_job = {
            "id": job_data.get("id", ""),
            "title": job_data.get("title", ""),
            "company": job_data.get("company_name", ""),
            "company_logo": job_data.get("company_logo", ""),
            "location": job_data.get("location", ""),
            "description": job_data.get("description", ""),
            "date": job_data.get("posted_at", ""),
            "url": job_data.get("job_apply_link", "") or job_data.get("job_link", "")
        }
        
        # Extract salary information if available
        if "salary_min" in job_data and job_data["salary_min"] is not None:
            processed_job["salary_min"] = job_data["salary_min"]
        
        if "salary_max" in job_data and job_data["salary_max"] is not None:
            processed_job["salary_max"] = job_data["salary_max"]
        
        if "salary_period" in job_data and job_data["salary_period"] is not None:
            processed_job["salary_period"] = job_data["salary_period"]
            
        # Extract employment type if available
        if "job_employment_type" in job_data and job_data["job_employment_type"] is not None:
            processed_job["employment_type"] = job_data["job_employment_type"]
        
        processed_jobs.append(processed_job)
    
    return processed_jobs

def get_job_details(job_id: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific job
    
    Args:
        job_id: The ID of the job to retrieve details for
        
    Returns:
        Dictionary containing detailed job information
    """
    # Get API key from environment variables
    api_key = os.environ.get('JSEARCH_API_KEY', config.JSEARCH_API_KEY)
    
    if not api_key:
        logger.error("JSearch API key not found")
        return {"error": "API key not configured"}
    
    # Prepare request parameters
    url = "https://jsearch.p.rapidapi.com/job-details"
    querystring = {"job_id": job_id}
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    try:
        # Make the API request
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse response data
        data = response.json()
        
        # Check if request was successful
        if data.get("status") != "OK":
            logger.error(f"API request failed: {data.get('message', 'Unknown error')}")
            return {"error": data.get("message", "API request failed")}
        
        # Extract job details
        job_details = data.get("data", [{}])[0]
        
        return {"job": job_details}
        
    except requests.exceptions.RequestException as e:
        logger.exception(f"Error fetching job details: {str(e)}")
        return {"error": str(e)}
