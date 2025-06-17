from flask import Blueprint, request, jsonify
import os
import requests
import logging
from typing import Dict, List, Any
import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

job_recommender_bp = Blueprint('job_recommender', __name__)

# -------------------- ROUTE --------------------
@job_recommender_bp.route('/recommend_jobs', methods=['POST'])
def recommend_jobs():
    data = request.get_json()
    keywords = data.get('keywords', '')
    location = data.get('location', '')
    
    logger.info(f"Received job recommendation request: keywords={keywords}, location={location}")
    
    results = search_jobs(keywords, location)
    return jsonify(results)

# -------------------- API FUNCTIONS --------------------

def get_api_key() -> str:
    return os.environ.get('JSEARCH_API_KEY', config.JSEARCH_API_KEY)

def search_jobs(keywords: str, location: str = '', page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    logger.debug(f"Searching jobs with keywords='{keywords}', location='{location}', page={page}")
    api_key = get_api_key()
    if not api_key:
        logger.error("JSearch API key not found")
        return {"error": "API key not configured", "jobs": [], "total_jobs": 0}

    url = config.JSEARCH_API_URL
    params = {
        "query": keywords,
        "page": str(page),
        "num_pages": "1",
        "page_size": str(page_size)
    }
    if location:
        params["location"] = location

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            logger.error(f"JSearch API request failed: {data.get('message', 'Unknown error')}")
            return {"error": data.get("message", "API request failed"), "jobs": [], "total_jobs": 0}

        jobs_data = data.get("data", [])
        processed_jobs = process_job_listings(jobs_data)
        total_jobs = data.get("total_jobs", len(processed_jobs))

        return {"jobs": processed_jobs, "total_jobs": total_jobs}

    except requests.exceptions.RequestException as e:
        logger.exception("Error fetching job listings")
        return {"error": str(e), "jobs": [], "total_jobs": 0}

def process_job_listings(raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    processed_jobs = []
    for job in raw_jobs:
        processed_job = {
            "id": job.get("job_id", ""),
            "title": job.get("job_title", ""),
            "company": job.get("employer_name", ""),
            "company_logo": job.get("employer_logo", ""),
            "location": f"{job.get('job_city', '')}, {job.get('job_country', '')}",
            "description": job.get("job_description", ""),
            "date": job.get("job_posted_at_datetime_utc", ""),
            "url": job.get("job_apply_link") or job.get("job_google_link", "")
        }
        if job.get("job_min_salary"):
            processed_job["salary_min"] = job["job_min_salary"]
        if job.get("job_max_salary"):
            processed_job["salary_max"] = job["job_max_salary"]
        if job.get("job_salary_period"):
            processed_job["salary_period"] = job["job_salary_period"]
        if job.get("job_employment_type"):
            processed_job["employment_type"] = job["job_employment_type"]
        processed_jobs.append(processed_job)
    return processed_jobs

# Optional: function if you plan to use it
def get_job_details(job_id: str) -> Dict[str, Any]:
    api_key = get_api_key()
    if not api_key:
        logger.error("JSearch API key not found")
        return {"error": "API key not configured"}

    url = "https://jsearch.p.rapidapi.com/job-details"
    params = {"job_id": job_id}
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "OK":
            logger.error(f"Failed to fetch job details: {data.get('message', 'Unknown error')}")
            return {"error": data.get("message", "API request failed")}
        job_details = data.get("data", [{}])[0]
        return {"job": job_details}
    except requests.exceptions.RequestException as e:
        logger.exception("Error fetching job details")
        return {"error": str(e)}

# Export for register_routes
job_recommendation_route = job_recommender_bp