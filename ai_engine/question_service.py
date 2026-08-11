import logging
import random

from applicants.models import Application

from .extractor import extract_skills
from .models import InterviewQuestion
from .question_bank import QUESTION_BANK

logger = logging.getLogger(__name__)


def generate_interview_questions(application_id):
    """
    Generate AI interview questions based on the candidate's
    resume analysis and the job description.
    """

    logger.info(
        "Starting interview question generation. application_id=%s",
        application_id,
    )

    application = Application.objects.select_related(
        "resume",
        "job",
        "candidate",
    ).get(id=application_id)

    parsed = application.resume.parsed_data or {}

    matched_skills = parsed.get("matched_skills", [])

    job_skills = (
        extract_skills(application.job.description)
        if application.job.description
        else []
    )

    skills_to_generate = matched_skills or job_skills

    logger.info(
        "Generating questions for skills: %s",
        skills_to_generate,
    )

    InterviewQuestion.objects.filter(
        application=application,
    ).delete()

    generated_questions = []

    for skill in skills_to_generate:

        if skill not in QUESTION_BANK:

            logger.warning(
                "Question bank not found for skill '%s'",
                skill,
            )

            continue

        questions = QUESTION_BANK[skill]

        selected_questions = random.sample(
            questions,
            min(3, len(questions)),
        )

        logger.info(
            "Selected %d questions for %s",
            len(selected_questions),
            skill,
        )

        for question_data in selected_questions:

            question = InterviewQuestion.objects.create(
                application=application,
                skill=skill,
                question=question_data["question"],
                difficulty=question_data["difficulty"],
            )

            generated_questions.append(question)

    logger.info(
        "Generated %d interview questions.",
        len(generated_questions),
    )

    return generated_questions