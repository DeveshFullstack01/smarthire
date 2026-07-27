import logging

from .extractor import extract_skills
from .parser import extract_text_from_pdf

logger = logging.getLogger(__name__)

def analyze_resume_file(resume_file_path, job_description):
    """
    Full structured analysis of a resume PDF against a job description.

    Wraps the enhanced analyzer with PDF parsing, so callers pass a file
    path (as the upload view already does) and get back the rich dict for
    storage in Resume.parsed_data. Backwards-compatible: still contains
    'score', 'matched_skills', 'missing_skills' like calculate_match_score.
    """
    from .resume_analyzer import analyze_resume

    resume_text = extract_text_from_pdf(resume_file_path)
    return analyze_resume(resume_text, job_description)

def calculate_match_score(
    resume_file_path,
    job_description,
):
    """
    Parse resume PDF and calculate skill match score.
    """

    logger.info("Starting resume match score calculation.")

    resume_text = extract_text_from_pdf(
        resume_file_path,
    )

    resume_skills = extract_skills(
        resume_text,
    )

    job_skills = extract_skills(
        job_description,
    )

    logger.debug(
        "Extracted %d resume skills and %d job skills.",
        len(resume_skills),
        len(job_skills),
    )

    if not job_skills:
        logger.warning(
            "No recognizable skills were found in the job description."
        )

        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
        }

    matched_skills = [
        skill
        for skill in job_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill
        for skill in job_skills
        if skill not in resume_skills
    ]

    score = round(
        len(matched_skills) / len(job_skills) * 100,
        2,
    )

    logger.debug(
        "Matched skills: %d | Missing skills: %d",
        len(matched_skills),
        len(missing_skills),
    )

    logger.info(
        "Resume match score calculated successfully: %.2f%%",
        score,
    )

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }