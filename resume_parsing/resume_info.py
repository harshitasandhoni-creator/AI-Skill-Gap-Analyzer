import os
import re
import json
import fitz  # PyMuPDF
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize

# Ensure NLTK punkt is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text from a PDF resume file using PyMuPDF."""
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("Only PDF files are supported.")
    
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


def extract_name(text: str) -> str:
    """
    Extracts the candidate's name from the very top lines of the resume 
    (before contact info or section headers).
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return "Unknown Candidate"

    # Common words that are never part of a person's name at the top
    skip_words = {"resume", "curriculum", "vitae", "cv", "profile", "contact", "email", "phone"}

    # Inspect the first 2-3 lines where names typically reside
    for line in lines[:3]:
        # Clean out phone numbers, emails, or symbols
        clean_line = re.sub(r'\S+@\S+', '', line)
        clean_line = re.sub(r'[\d\+\-\(\)\s]{7,}', '', clean_line).strip()
        
        if not clean_line:
            continue
            
        words = clean_line.split()
        if 1 <= len(words) <= 4 and all(w.isalpha() for w in words):
            if words[0].lower() not in skip_words:
                return clean_line.title()

    return lines[0].title() if lines else "Unknown Candidate"


def extract_skills_strictly(text: str) -> list:
    """
    Strictly extracts skills ONLY from the dedicated 'SKILLS' section of the resume,
    preventing bleeding into experience, education, or achievements.
    """
    found_skills = []
    
    # Regex to capture text starting from 'SKILLS' (or variations) up until the next section header
    # Common headers in resumes: HOBBIES, LANGUAGES, PROFILE, EDUCATION, EXPERIENCE, WORK HISTORY, SUMMARY
    pattern = r'(?:SKILLS|CORE COMPETENCIES|AREAS OF EXPERTISE|KEY SKILLS)[:\s]*(.*?)(?=\n\s*(?:[-•]*\s*)?(?:HOBBIES|LANGUAGES|PROFILE|EDUCATION|EXPERIENCE|WORK HISTORY|SUMMARY|ACHIEVEMENTS|PROJECTS)|\Z)'
    
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        skills_block = match.group(1).strip()
        
        # Split by bullet points, newlines, or semicolons
        raw_items = re.split(r'[\n•;]+', skills_block)
        
        for item in raw_items:
            clean_item = item.strip()
            # Clean up unwanted trailing/leading characters or bullet symbols
            clean_item = re.sub(r'^[\•\-\*\s]+', '', clean_item).strip()
            
            # Validate that it's a legitimate skill phrase (not empty or too long like a sentence)
            if clean_item and len(clean_item) > 2 and len(clean_item.split()) <= 6:
                # Exclude lines that accidentally matched section header spillover
                if not any(header in clean_item.upper() for header in ["HOBBIES", "LANGUAGES", "PROFILE", "EDUCATION"]):
                    found_skills.append(clean_item)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(found_skills))


def parse_resume(pdf_path: str) -> dict:
    """Main pipeline to extract name and strict skills from resume PDF."""
    if not os.path.exists(pdf_path):
        return {"error": f"File not found: {pdf_path}", "candidate_name": None, "skills": []}

    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text:
        return {"error": "Could not extract text from PDF.", "candidate_name": None, "skills": []}

    candidate_name = extract_name(raw_text)
    candidate_skills = extract_skills_strictly(raw_text)

    return {
        "candidate_name": candidate_name,
        "skills": candidate_skills,
        "total_skills_count": len(candidate_skills)
    }


# ==========================================
# LOCAL TESTING BLOCK
# ==========================================
if __name__ == "__main__":
    test_pdf = "C:/Users/HARSHITA/AI-Skill-Gap-Analysis/data/kupdf.net_btech-freshers-resume.pdf"  # Testing with Robert Cooper's security guard resume
    
    if os.path.exists(test_pdf):
        result = parse_resume(test_pdf)
        print("--- Corrected Parsed Output ---")
        print(json.dumps(result, indent=4))
    else:
        print(f"File {test_pdf} not found.")