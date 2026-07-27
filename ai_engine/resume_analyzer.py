"""
Enhanced resume analysis.

Extends the basic skill extractor to pull structured data from resume
text: contact details, education, experience hints, and certifications.
Everything is best-effort regex/heuristics — no external AI service — so
it stays fast, free, and offline. Results are shaped for JSON storage in
Resume.parsed_data.
"""

import re

from .extractor import KNOWN_SKILLS, extract_skills


def _clean_line(line):
    """Strip PDF artifacts like (cid:NNN) glyphs and bullet characters."""
    line = re.sub(r"\(cid:\d+\)", "", line)
    line = line.lstrip("\u2022\u25cf\u25aa\u2023\u2043-*\u2219 \t")
    return line.strip()

# --------------------------------------------------
# Contact details
# --------------------------------------------------

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(
    r"(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}"
    r"|\+?\d{10,13})"
)
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w-]+", re.I)
GITHUB_RE = re.compile(r"github\.com/[\w-]+", re.I)


def extract_contact(text):
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    linkedin = LINKEDIN_RE.search(text)
    github = GITHUB_RE.search(text)

    return {
        "email": email.group(0) if email else "",
        "phone": phone.group(0).strip() if phone else "",
        "linkedin": linkedin.group(0) if linkedin else "",
        "github": github.group(0) if github else "",
    }


# --------------------------------------------------
# Education
# --------------------------------------------------

DEGREE_KEYWORDS = [
    "PhD", "Doctorate", "M.Tech", "MTech", "M.E", "MSc", "M.Sc", "MBA",
    "MCA", "Master", "B.Tech", "BTech", "B.E", "BSc", "B.Sc", "BCA",
    "Bachelor", "Diploma",
]


def extract_education(text):
    """Return lines that look like they name a degree."""
    found = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Skip lines that are clearly certifications, so titles like
        # "Certified Scrum Master" don't match the degree keyword "Master".
        if re.search(r"\bcert-?(?:ified|ificate|ification)\b", stripped, re.I):
            continue
        for kw in DEGREE_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", stripped, re.I):
                found.append(stripped[:120])
                break
    # de-dupe while keeping order
    seen = set()
    unique = []
    for item in found:
        low = item.lower()
        if low not in seen:
            seen.add(low)
            unique.append(item)
    return unique[:5]


# --------------------------------------------------
# Certifications
# --------------------------------------------------

CERT_KEYWORDS = [
    "Certified", "Certification", "Certificate", "AWS Certified",
    "Azure", "PMP", "Scrum", "OCP", "CKA", "CKAD",
]


def extract_certifications(text):
    found = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        for kw in CERT_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", stripped, re.I):
                found.append(stripped[:120])
                break
    seen = set()
    unique = []
    for item in found:
        low = item.lower()
        if low not in seen:
            seen.add(low)
            unique.append(item)
    return unique[:5]


# --------------------------------------------------
# Experience (years)
# --------------------------------------------------

YEARS_RE = re.compile(
    r"(\d{1,2})\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience)?",
    re.I,
)


def extract_years_of_experience(text):
    """Highest 'N years' figure mentioned, or None."""
    matches = YEARS_RE.findall(text)
    numbers = [int(m) for m in matches if m.isdigit()]
    return max(numbers) if numbers else None


# --------------------------------------------------
# Top-level analyzer
# --------------------------------------------------

def analyze_resume(text, job_description=""):
    """
    Produce a full structured analysis of a resume.

    If job_description is given, also compute the skill match and
    recommend the missing skills the candidate should add.
    """
    resume_skills = extract_skills(text)

    analysis = {
        "contact": extract_contact(text),
        "skills": resume_skills,
        "education": extract_education(text),
        "certifications": extract_certifications(text),
        "years_of_experience": extract_years_of_experience(text),
    }

    if job_description:
        job_skills = extract_skills(job_description)
        matched = [s for s in job_skills if s in resume_skills]
        missing = [s for s in job_skills if s not in resume_skills]

        score = (
            round(len(matched) / len(job_skills) * 100, 2)
            if job_skills else 0
        )

        analysis["score"] = score
        analysis["matched_skills"] = matched
        analysis["missing_skills"] = missing
        analysis["recommendations"] = _build_recommendations(score, missing)

    return analysis


def _build_recommendations(score, missing_skills):
    """Human-readable suggestions based on the match result."""
    recs = []

    if score >= 80:
        recs.append("Strong match. Your profile aligns well with this role.")
    elif score >= 50:
        recs.append("Moderate match. Highlighting a few skills could help.")
    else:
        recs.append("Low match. Consider building the skills below.")

    if missing_skills:
        preview = ", ".join(missing_skills[:5])
        recs.append(f"Add or gain experience in: {preview}.")

    return recs