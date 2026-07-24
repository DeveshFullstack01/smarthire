import logging

from .extractor import extract_skills
from .parser import extract_text_from_pdf

logger = logging.getLogger(__name__)


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