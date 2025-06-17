import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from utils.firebase_utils import save_to_firestore, get_from_firestore, query_firestore, delete_from_firestore

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def save_user(firebase_uid: str, email: str, display_name: Optional[str] = None) -> Optional[str]:
    """
    Save user information to Firestore
    """
    try:
        user_data = {
            'firebase_uid': firebase_uid,
            'email': email,
            'display_name': display_name or "",
            'created_at': datetime.utcnow().isoformat()
        }
        document_id = save_to_firestore('users', user_data, firebase_uid)
        if document_id:
            logger.info(f"[User] Saved: {email}")
            return document_id
        else:
            logger.error(f"[User] Failed to save: {email}")
    except Exception as e:
        logger.exception(f"[User] Exception occurred: {str(e)}")
    return None

def get_user_by_firebase_uid(firebase_uid: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from Firestore by Firebase UID
    """
    try:
        return get_from_firestore('users', firebase_uid)
    except Exception as e:
        logger.exception(f"[User] Error fetching user by UID: {str(e)}")
        return None

def save_resume_analysis(user_id: str, filename: str, resume_text: str, analysis_results: Dict[str, Any]) -> Optional[str]:
    """
    Save resume analysis to Firestore
    """
    try:
        analysis_data = {
            'user_id': user_id,
            'filename': filename,
            'resume_text': resume_text,
            'skills': analysis_results.get('skills', []),
            'education': analysis_results.get('education', []),
            'experience': analysis_results.get('experience', []),
            'suggestions': analysis_results.get('suggestions', []),
            'ats_score': analysis_results.get('ats_score', 0),
            'created_at': datetime.utcnow().isoformat()
        }
        document_id = save_to_firestore('resume_analyses', analysis_data)
        if document_id:
            logger.info(f"[Resume] Analysis saved for: {filename}")
            return document_id
        else:
            logger.error(f"[Resume] Failed to save analysis: {filename}")
    except Exception as e:
        logger.exception(f"[Resume] Exception while saving: {str(e)}")
    return None

def get_user_resume_analyses(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all resume analyses for a user
    """
    try:
        analyses = query_firestore('resume_analyses', 'user_id', '==', user_id)
        return sorted(analyses, key=lambda x: x.get('created_at', ''), reverse=True)
    except Exception as e:
        logger.exception(f"[Resume] Error fetching analyses: {str(e)}")
        return []

def save_job_search(user_id: str, keywords: str, location: str, results_count: int) -> Optional[str]:
    """
    Save job search query to Firestore
    """
    try:
        search_data = {
            'user_id': user_id,
            'keywords': keywords,
            'location': location or '',
            'results_count': results_count,
            'created_at': datetime.utcnow().isoformat()
        }
        document_id = save_to_firestore('job_searches', search_data)
        if document_id:
            logger.info(f"[Job Search] Saved: {keywords} in {location}")
            return document_id
        else:
            logger.error(f"[Job Search] Failed to save: {keywords}")
    except Exception as e:
        logger.exception(f"[Job Search] Exception while saving: {str(e)}")
    return None

def save_job(user_id: str, job_data: Dict[str, Any]) -> Optional[str]:
    """
    Save a job posting to Firestore
    """
    try:
        job_id = job_data.get('job_id')
        if not job_id:
            logger.error("[Job Save] Missing job_id in job_data")
            return None

        document_id = f"{user_id}_{job_id}"
        saved_job_data = {
            'user_id': user_id,
            'job_id': job_id,
            'title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'location': job_data.get('location', ''),
            'description': job_data.get('description', ''),
            'url': job_data.get('url', ''),
            'saved_at': datetime.utcnow().isoformat()
        }
        result_id = save_to_firestore('saved_jobs', saved_job_data, document_id)
        if result_id:
            logger.info(f"[Job Save] Job saved: {saved_job_data['title']}")
            return result_id
        else:
            logger.error(f"[Job Save] Failed to save job: {saved_job_data['title']}")
    except Exception as e:
        logger.exception(f"[Job Save] Exception: {str(e)}")
    return None

def get_saved_jobs(user_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve saved jobs for a user
    """
    try:
        jobs = query_firestore('saved_jobs', 'user_id', '==', user_id, limit=100)
        return sorted(jobs, key=lambda x: x.get('saved_at', ''), reverse=True)
    except Exception as e:
        logger.exception(f"[Saved Jobs] Error fetching saved jobs: {str(e)}")
        return []

def save_chat_message(user_id: str, message: str, is_user_message: bool = True) -> Optional[str]:
    """
    Save a chat message to Firestore
    """
    try:
        message_data = {
            'user_id': user_id,
            'message': message,
            'is_user_message': is_user_message,
            'created_at': datetime.utcnow().isoformat()
        }
        document_id = save_to_firestore('chat_messages', message_data)
        if document_id:
            logger.info(f"[Chat] Message saved by {'User' if is_user_message else 'AI'}")
            return document_id
        else:
            logger.error("[Chat] Failed to save message")
    except Exception as e:
        logger.exception(f"[Chat] Exception while saving message: {str(e)}")
    return None

def get_chat_history(user_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve chat history for a user
    """
    try:
        messages = query_firestore('chat_messages', 'user_id', '==', user_id, limit=100)
        return sorted(messages, key=lambda x: x.get('created_at', ''))
    except Exception as e:
        logger.exception(f"[Chat] Error fetching chat history: {str(e)}")
        return []
