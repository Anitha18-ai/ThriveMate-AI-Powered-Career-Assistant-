import os
import logging
import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variables to store Firebase instances
firebase_app = None
firebase_storage = None
firebase_db = None

# Flag to indicate if we should try to use Firebase
try:
    import firebase_admin
    from firebase_admin import credentials, storage, firestore
    from firebase_admin.exceptions import FirebaseError
    FIREBASE_AVAILABLE = True
except ImportError:
    logger.warning("Firebase admin SDK not available. Firebase features will be disabled.")
    FIREBASE_AVAILABLE = False

def init_firebase():
    """
    Initialize Firebase Admin SDK
    
    Returns:
        Tuple of (firebase_app, storage_client, firestore_client)
    """
    global firebase_app, firebase_storage, firebase_db
    
    # If already initialized, return existing instances
    if firebase_app:
        return firebase_app, firebase_storage, firebase_db
    
    # Check if Firebase is available
    if not FIREBASE_AVAILABLE:
        logger.warning("Firebase SDK is not available. Skipping initialization.")
        return None, None, None
    
    # For the Replit environment, we'll disable full Firebase admin functionality
    # and just return placeholders for the client-side Firebase setup
    logger.info("Firebase server functionality is disabled in this environment.")
    logger.info("Client-side Firebase authentication will still be available.")
    
    # Return None for all Firebase components
    return None, None, None

def upload_file_to_storage(file_data, file_path):
    """
    Upload a file to Firebase Storage
    
    Args:
        file_data: File data to upload
        file_path: Path in Firebase Storage where the file should be stored
        
    Returns:
        Download URL for the uploaded file
    """
    global firebase_storage
    
    if not firebase_storage:
        logger.error("Firebase Storage not initialized")
        return None
    
    try:
        # Create a blob object
        blob = firebase_storage.blob(file_path)
        
        # Upload file
        blob.upload_from_string(file_data)
        
        # Make the file publicly accessible
        blob.make_public()
        
        # Get the download URL
        download_url = blob.public_url
        
        logger.info(f"File uploaded to Firebase Storage: {file_path}")
        return download_url
        
    except Exception as e:
        logger.exception(f"Error uploading file to Firebase Storage: {str(e)}")
        return None

def save_to_firestore(collection, document_data, document_id=None):
    """
    Save a document to Firestore
    
    Args:
        collection: Collection name
        document_data: Data to save
        document_id: Optional document ID (if None, a new ID will be generated)
        
    Returns:
        Document ID
    """
    global firebase_db
    
    if not firebase_db:
        logger.error("Firestore not initialized")
        return None
    
    try:
        # Get collection reference
        collection_ref = firebase_db.collection(collection)
        
        # Add or set document
        if document_id:
            doc_ref = collection_ref.document(document_id)
            doc_ref.set(document_data)
        else:
            doc_ref = collection_ref.add(document_data)[1]
            document_id = doc_ref.id
        
        logger.info(f"Document saved to Firestore: {collection}/{document_id}")
        return document_id
        
    except Exception as e:
        logger.exception(f"Error saving to Firestore: {str(e)}")
        return None

def get_from_firestore(collection, document_id):
    """
    Get a document from Firestore
    
    Args:
        collection: Collection name
        document_id: Document ID
        
    Returns:
        Document data
    """
    global firebase_db
    
    if not firebase_db:
        logger.error("Firestore not initialized")
        return None
    
    try:
        # Get document reference
        doc_ref = firebase_db.collection(collection).document(document_id)
        
        # Get document
        doc = doc_ref.get()
        
        # Return document data if it exists
        if doc.exists:
            return doc.to_dict()
        else:
            logger.warning(f"Document not found: {collection}/{document_id}")
            return None
        
    except Exception as e:
        logger.exception(f"Error getting document from Firestore: {str(e)}")
        return None

def query_firestore(collection, field, operator, value, limit=10):
    """
    Query documents from Firestore
    
    Args:
        collection: Collection name
        field: Field to filter on
        operator: Operator to use (==, >, <, etc.)
        value: Value to compare against
        limit: Maximum number of documents to return
        
    Returns:
        List of document data
    """
    global firebase_db
    
    if not firebase_db:
        logger.error("Firestore not initialized")
        return []
    
    try:
        # Query collection
        query = firebase_db.collection(collection).where(field, operator, value).limit(limit)
        
        # Get documents
        docs = query.stream()
        
        # Return document data
        return [doc.to_dict() for doc in docs]
        
    except Exception as e:
        logger.exception(f"Error querying Firestore: {str(e)}")
        return []

def delete_from_firestore(collection, document_id):
    """
    Delete a document from Firestore
    
    Args:
        collection: Collection name
        document_id: Document ID
        
    Returns:
        True if successful, False otherwise
    """
    global firebase_db
    
    if not firebase_db:
        logger.error("Firestore not initialized")
        return False
    
    try:
        # Delete document
        firebase_db.collection(collection).document(document_id).delete()
        
        logger.info(f"Document deleted from Firestore: {collection}/{document_id}")
        return True
        
    except Exception as e:
        logger.exception(f"Error deleting document from Firestore: {str(e)}")
        return False
