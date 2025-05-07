import re
import spacy
import logging
from typing import Dict, List, Any
import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load spaCy model - use a small English pipeline
logger.debug("Loading spaCy model...")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("en_core_web_sm not found, using a blank model instead")
    # Create a blank English model
    nlp = spacy.blank("en")
    logger.info("Blank English model loaded successfully")

def analyze_resume(text: str) -> Dict[str, Any]:
    """
    Analyze resume text and extract key information
    
    Args:
        text: The text content of the resume
        
    Returns:
        Dictionary containing extracted information and analysis
    """
    logger.debug("Starting resume analysis")
    
    # Process the text with spaCy
    doc = nlp(text)
    
    # Extract key information
    skills = extract_skills(doc, text)
    education = extract_education(doc, text)
    experience = extract_experience(doc, text)
    suggestions = generate_suggestions(doc, text, skills, education, experience)
    
    # Combine results
    analysis_results = {
        "skills": skills,
        "education": education,
        "experience": experience,
        "suggestions": suggestions
    }
    
    logger.debug("Resume analysis completed")
    return analysis_results

def extract_skills(doc, text: str) -> List[str]:
    """Extract skills from resume text"""
    skills = []
    
    # Use the skill keywords from config
    for skill in config.SKILL_KEYWORDS:
        # Case insensitive search for each skill
        pattern = re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE)
        if pattern.search(text):
            # Capitalize appropriately
            if skill.lower() in ["html", "css", "sql", "api", "aws", "gcp", "ui", "ux"]:
                skills.append(skill.upper())
            else:
                skills.append(skill.title())
    
    # Additionally, look for technical terms that might be skills
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT"]:
            # Check if the entity might be a programming language, framework, or tool
            potential_skill = ent.text.strip()
            # Avoid duplicates and ensure it's not just a common word
            if (potential_skill.lower() not in [s.lower() for s in skills] and 
                len(potential_skill) > 2 and
                potential_skill.lower() not in ["the", "and", "for", "with"]):
                skills.append(potential_skill)
    
    # Remove duplicates while preserving order
    unique_skills = []
    for skill in skills:
        if skill.lower() not in [s.lower() for s in unique_skills]:
            unique_skills.append(skill)
    
    return unique_skills

def extract_education(doc, text: str) -> List[Dict[str, str]]:
    """Extract education information from resume text"""
    education = []
    
    # Look for education-related keywords
    education_keywords = ["degree", "bachelor", "master", "phd", "diploma", "certificate", 
                         "university", "college", "school", "institute", "academy"]
    
    # Find sentences containing education keywords
    education_sentences = []
    for sent in doc.sents:
        sent_text = sent.text.lower()
        if any(keyword in sent_text for keyword in education_keywords):
            education_sentences.append(sent.text)
    
    # Extract education details from these sentences
    for sent in education_sentences:
        # Extract degree
        degree_pattern = re.compile(r'(bachelor|master|phd|doctor|diploma|certificate)s?(\sof\s|\sin\s)?(\w+)?', re.IGNORECASE)
        degree_match = degree_pattern.search(sent)
        degree = degree_match.group(0) if degree_match else ""
        
        # Extract institution
        institution_pattern = re.compile(r'(university|college|institute|school) of [\w\s]+|[\w\s]+ (university|college|institute|school)', re.IGNORECASE)
        institution_match = institution_pattern.search(sent)
        institution = institution_match.group(0) if institution_match else ""
        
        # Extract year
        year_pattern = re.compile(r'\b(19|20)\d{2}\b')
        year_match = year_pattern.search(sent)
        year = year_match.group(0) if year_match else ""
        
        # If we found at least a degree or institution, add it
        if degree or institution:
            education.append({
                "degree": degree,
                "institution": institution,
                "year": year
            })
    
    # If no education found using the pattern matching, try to extract it from the text
    if not education:
        # Look for education section
        education_section_pattern = re.compile(r'education.*?(?=employment|experience|skills|$)', re.IGNORECASE | re.DOTALL)
        education_section_match = education_section_pattern.search(text)
        
        if education_section_match:
            education_section = education_section_match.group(0)
            
            # Look for lines that might contain institution names
            lines = education_section.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ["university", "college", "school", "institute"]):
                    # Extract year
                    year_pattern = re.compile(r'\b(19|20)\d{2}\b')
                    year_match = year_pattern.search(line)
                    year = year_match.group(0) if year_match else ""
                    
                    education.append({
                        "degree": "",
                        "institution": line.strip(),
                        "year": year
                    })
    
    return education

def extract_experience(doc, text: str) -> List[Dict[str, str]]:
    """Extract work experience information from resume text"""
    experience = []
    
    # Look for experience/employment section
    experience_section_pattern = re.compile(r'(experience|employment|work history).*?(?=education|skills|projects|$)', re.IGNORECASE | re.DOTALL)
    experience_section_match = experience_section_pattern.search(text)
    
    if experience_section_match:
        experience_section = experience_section_match.group(0)
        
        # Split into paragraphs (each likely representing a position)
        paragraphs = re.split(r'\n\s*\n', experience_section)
        
        for paragraph in paragraphs[1:]:  # Skip the heading
            if len(paragraph.strip()) < 10:  # Skip very short paragraphs
                continue
                
            # Extract job title (look for capitalized words or words followed by at/with)
            title_pattern = re.compile(r'([A-Z][a-z]+ [A-Z][a-z]+|[A-Z][a-z]+\s+\w+)\s+(at|with|for|,|\-|–)', re.IGNORECASE)
            title_match = title_pattern.search(paragraph)
            title = title_match.group(1) if title_match else ""
            
            # Extract company name
            company_pattern = re.compile(r'(at|with|for)\s+([A-Za-z0-9\s&]+)', re.IGNORECASE)
            company_match = company_pattern.search(paragraph)
            company = company_match.group(2).strip() if company_match else ""
            
            # Extract dates/duration
            duration_pattern = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|20\d{2})\s*(-|to|–|–|−)\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|20\d{2}|Present|present|Current|current)', re.IGNORECASE)
            duration_match = duration_pattern.search(paragraph)
            duration = duration_match.group(0) if duration_match else ""
            
            # Extract description (use the rest of the paragraph)
            description = paragraph.strip()
            
            # If we found at least a title or company, add it
            if title or company:
                experience.append({
                    "title": title,
                    "company": company,
                    "duration": duration,
                    "description": description
                })
    
    # If no experience was extracted, try a different approach
    if not experience:
        # Look for lines that might be job titles
        for sent in doc.sents:
            sent_text = sent.text.strip()
            
            # Check if this looks like a job title line
            if re.search(r'(engineer|manager|developer|analyst|designer|consultant|specialist)', sent_text, re.IGNORECASE):
                # Extract company name (following "at" or "with")
                company_pattern = re.compile(r'(at|with)\s+([A-Za-z0-9\s&]+)', re.IGNORECASE)
                company_match = company_pattern.search(sent_text)
                company = company_match.group(2).strip() if company_match else ""
                
                experience.append({
                    "title": sent_text,
                    "company": company,
                    "duration": "",
                    "description": ""
                })
    
    return experience

def generate_suggestions(doc, text: str, skills: List[str], education: List[Dict[str, str]], experience: List[Dict[str, str]]) -> List[str]:
    """Generate improvement suggestions for the resume"""
    suggestions = []
    
    # Check if skills section is robust
    if len(skills) < 5:
        suggestions.append("Add more specific skills relevant to your target industry")
    
    # Check if education details are complete
    for edu in education:
        if not edu.get("degree"):
            suggestions.append("Specify your degree/qualification in your education section")
        if not edu.get("year"):
            suggestions.append("Include graduation year for each education entry")
    
    # Check if experience descriptions use action verbs
    action_verbs = ["achieved", "improved", "launched", "developed", "created", "implemented", 
                    "led", "managed", "increased", "reduced", "negotiated", "organized"]
    
    has_action_verbs = False
    for exp in experience:
        desc = exp.get("description", "").lower()
        if any(verb in desc for verb in action_verbs):
            has_action_verbs = True
            break
    
    if not has_action_verbs:
        suggestions.append("Use strong action verbs to describe your achievements (e.g., 'increased', 'implemented', 'developed')")
    
    # Check if experience includes quantifiable achievements
    has_numbers = False
    for exp in experience:
        desc = exp.get("description", "")
        if re.search(r'\d+%|\$\d+|\d+ [a-z]+', desc):
            has_numbers = True
            break
    
    if not has_numbers:
        suggestions.append("Include quantifiable achievements with specific numbers (e.g., 'increased sales by 20%')")
    
    # Check if content is too dense or sparse
    words_per_line = len(text.split()) / (text.count('\n') + 1)
    if words_per_line > 20:
        suggestions.append("Break up long paragraphs with bullet points for better readability")
    
    # Check for contact information
    has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
    has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
    
    if not has_email:
        suggestions.append("Add a professional email address to your contact information")
    if not has_phone:
        suggestions.append("Include a phone number in your contact information")
    
    # Check for LinkedIn profile
    has_linkedin = bool(re.search(r'linkedin\.com/in/|linkedin:|\blinkedin\b', text, re.IGNORECASE))
    if not has_linkedin:
        suggestions.append("Add your LinkedIn profile URL to strengthen your online presence")
    
    # Check if resume length seems appropriate (rough estimate)
    word_count = len(text.split())
    if word_count < 300:
        suggestions.append("Your resume appears to be on the short side. Consider adding more details about your experience and achievements")
    elif word_count > 800:
        suggestions.append("Your resume may be too lengthy. Consider focusing on the most relevant experience for your target position")
    
    return suggestions

def calculate_ats_score(analysis_results: Dict[str, Any]) -> int:
    """
    Calculate an ATS compatibility score based on the resume analysis
    
    Args:
        analysis_results: The results from the resume analysis
        
    Returns:
        Score from 0-100 representing ATS compatibility
    """
    score = 0
    
    # Score based on skills (0-25 points)
    skills = analysis_results.get("skills", [])
    if skills:
        skills_score = min(len(skills) * 2, 25)
        score += skills_score
    
    # Score based on education (0-15 points)
    education = analysis_results.get("education", [])
    if education:
        education_score = min(len(education) * 5, 15)
        for edu in education:
            if not edu.get("degree") or not edu.get("institution"):
                education_score -= 2
        score += max(education_score, 0)
    
    # Score based on experience (0-35 points)
    experience = analysis_results.get("experience", [])
    if experience:
        experience_score = min(len(experience) * 7, 35)
        for exp in experience:
            if not exp.get("title") or not exp.get("company"):
                experience_score -= 3
            if not exp.get("description") or len(exp.get("description", "")) < 50:
                experience_score -= 3
        score += max(experience_score, 0)
    
    # Score based on suggestion count (0-25 points)
    # More suggestions means lower score
    suggestions = analysis_results.get("suggestions", [])
    suggestions_penalty = min(len(suggestions) * 5, 25)
    suggestion_score = 25 - suggestions_penalty
    score += suggestion_score
    
    # Ensure score is between 0 and 100
    score = max(0, min(score, 100))
    
    return score
