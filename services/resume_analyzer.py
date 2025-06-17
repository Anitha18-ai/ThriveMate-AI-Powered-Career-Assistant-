# services/resume_analyzer.py

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any, List
import re

resume_analysis_route = Blueprint('resume_analysis_route', __name__)
logger = logging.getLogger(__name__)

@resume_analysis_route.route('/api/analyze-resume', methods=['POST'])
def analyze_resume_api():
    try:
        data = request.get_json()
        resume_text = data.get('text', '')

        if not resume_text:
            return jsonify({'error': 'Resume text is missing'}), 400

        analysis_results = analyze_resume(resume_text)
        ats_score = calculate_ats_score(analysis_results)

        return jsonify({
            'analysis': analysis_results,
            'ats_score': ats_score
        })

    except Exception as e:
        logger.exception("Error analyzing resume")
        return jsonify({'error': str(e)}), 500


# --- Resume Analysis Logic Functions (no changes made) ---

def analyze_resume(text: str) -> Dict[str, Any]:
    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience(text)
    suggestions = generate_suggestions(text, skills, education, experience)
    
    return {
        'skills': skills,
        'education': education,
        'experience': experience,
        'suggestions': suggestions
    }

def extract_skills(text: str) -> List[str]:
    skill_keywords = [
        'python', 'javascript', 'typescript', 'java', 'c\\+\\+', 'c#', 'react', 'angular', 
        'vue', 'node', 'express', 'django', 'flask', 'sql', 'nosql', 'mongodb',
        'postgresql', 'mysql', 'aws', 'azure', 'gcp', 'docker', 'kubernetes',
        'git', 'agile', 'scrum', 'project management', 'leadership', 'communication',
        'html', 'css', 'bootstrap', 'tailwind', 'jquery', 'php', 'laravel', 'symfony',
        'ruby', 'rails', 'go', 'rust', 'swift', 'kotlin', 'tensorflow', 'pytorch',
        'machine learning', 'artificial intelligence', 'data science', 'big data',
        'hadoop', 'spark', 'tableau', 'power bi', 'excel', 'word', 'powerpoint',
        'photoshop', 'illustrator', 'figma', 'sketch', 'ui/ux', 'seo', 'digital marketing'
    ]
    pattern = '|'.join(r'\b' + skill + r'\b' for skill in skill_keywords)
    found_skills = list(set(re.findall(pattern, text.lower())))
    return [skill.capitalize() for skill in found_skills]

def extract_education(text: str) -> List[Dict[str, str]]:
    education_list = []
    degree_pattern = r'\b(Bachelor|Master|PhD|BSc|MSc|BA|MA|MBA|B\.A\.|M\.A\.|B\.S\.|M\.S\.)[s]?\b|\b(Bachelor|Master)\'s\b'
    degrees = re.findall(degree_pattern, text)
    flattened_degrees = [d[0] if d[0] else d[1] for d in degrees if d[0] or d[1]]
    university_pattern = r'\b(University|College|Institute|School)( of)? [A-Z][a-zA-Z]+\b'
    universities = re.findall(university_pattern, text)
    university_names = [' '.join(u).strip() for u in universities]
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)

    for i, degree in enumerate(flattened_degrees):
        education_entry = {
            'degree': degree,
            'institution': university_names[i] if i < len(university_names) else 'Unknown Institution',
            'year': years[i] if i < len(years) else 'Unknown Year'
        }
        education_list.append(education_entry)

    if not education_list and university_names:
        for i, institution in enumerate(university_names):
            education_entry = {
                'degree': 'Degree not specified',
                'institution': institution,
                'year': years[i] if i < len(years) else 'Unknown Year'
            }
            education_list.append(education_entry)

    return education_list

def extract_experience(text: str) -> List[Dict[str, str]]:
    experience_list = []
    title_pattern = r'\b(Software Engineer|Developer|Senior Developer|Manager|Director|Coordinator|Specialist|Analyst|Designer|Programmer|Architect|Lead|Consultant|Associate|Assistant|Administrator|Executive|Officer)\b'
    job_titles = re.findall(title_pattern, text)
    company_pattern = r'\b[A-Z][a-zA-Z]+ (Inc|LLC|Ltd|Company|Corp|Corporation)\b|\b[A-Z][a-zA-Z]+ Technologies\b|\b[A-Z][a-zA-Z]+ Solutions\b|\b[A-Z][a-zA-Z]+ Systems\b'
    companies = re.findall(company_pattern, text)
    date_pattern = r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* [\d]{4}\s*(-|to|–|—)\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* [\d]{4}\b|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* [\d]{4}\s*(-|to|–|—)\s*[Pp]resent\b|\b[\d]{4}\s*(-|to|–|—)\s*[\d]{4}\b|\b[\d]{4}\s*(-|to|–|—)\s*[Pp]resent\b'
    dates = re.findall(date_pattern, text)
    paragraphs = re.split(r'\n\s*\n', text)

    for i, title in enumerate(job_titles):
        description = ""
        for paragraph in paragraphs:
            if title in paragraph:
                description = paragraph.replace(title, "").strip()
                break
        experience_entry = {
            'title': title,
            'company': companies[i] if i < len(companies) else 'Unknown Company',
            'period': dates[i] if i < len(dates) else 'Unknown Period',
            'description': description if description else 'No detailed description available'
        }
        experience_list.append(experience_entry)

    return experience_list

def generate_suggestions(text: str, skills: List[str], education: List[Dict[str, str]], experience: List[Dict[str, str]]) -> List[str]:
    suggestions = []

    if len(text) < 2000:
        suggestions.append("Your resume seems short. Consider adding more details about your experience and skills.")
    if len(skills) < 5:
        suggestions.append("Try adding more specific skills relevant to your target position.")
    if not education:
        suggestions.append("Add your educational background with degrees and institutions.")
    if not experience:
        suggestions.append("Add your work experience with job titles, companies, and responsibilities.")
    elif len(experience) < 2:
        suggestions.append("Consider adding more details about your past work experiences.")
    
    important_sections = ['skill', 'experience', 'education', 'project', 'certification', 'publication']
    missing_sections = [section for section in important_sections if section not in text.lower()]
    if missing_sections:
        suggestions.append(f"Consider adding dedicated sections for: {', '.join(missing_sections).title()}")
    
    suggestions.append("Quantify your achievements with numbers where possible (e.g., 'Increased revenue by 15%').")
    suggestions.append("Customize your resume for each job application by matching keywords from the job description.")
    suggestions.append("Use strong action verbs at the beginning of bullet points (e.g., 'Led', 'Developed', 'Achieved').")
    
    return suggestions

def calculate_ats_score(analysis_results: Dict[str, Any]) -> int:
    score = 60
    skills_count = len(analysis_results.get('skills', []))
    if skills_count >= 10:
        score += 15
    elif skills_count >= 5:
        score += 10
    elif skills_count > 0:
        score += 5

    if analysis_results.get('education', []):
        score += 10

    experience_count = len(analysis_results.get('experience', []))
    if experience_count >= 3:
        score += 15
    elif experience_count >= 1:
        score += 10

    if not analysis_results.get('skills', []):
        score -= 10
    if not analysis_results.get('education', []):
        score -= 5
    if not analysis_results.get('experience', []):
        score -= 10

    return min(max(score, 0), 100)