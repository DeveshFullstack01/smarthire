import logging
import random

from applicants.models import Application

from .extractor import extract_skills
from .models import InterviewQuestion
from .question_bank import QUESTION_BANK
from .services import calculate_match_score

logger = logging.getLogger(__name__)


def generate_interview_questions(application_id):
    logger.info(
        "Starting interview question generation for application_id=%s",
        application_id,
    )

    application = Application.objects.get(id=application_id)

    result = calculate_match_score(
        application.resume.file.path,
        application.job.description,
    )

    matched_skills = result["matched_skills"]
    job_skills = extract_skills(application.job.description)

    skills_to_generate = matched_skills or job_skills

    logger.debug("Skills selected for generation: %s", skills_to_generate)

    InterviewQuestion.objects.filter(
        application=application,
    ).delete()

    generated_questions = []

    for skill in skills_to_generate:
        logger.debug("Processing skill: %s", skill)

        if skill not in QUESTION_BANK:
            logger.warning(
                "No question bank found for skill: %s",
                skill,
            )
            continue

        questions = QUESTION_BANK[skill]

        logger.debug(
            "Found %d questions for skill '%s'",
            len(questions),
            skill,
        )

        selected_questions = random.sample(
            questions,
            min(3, len(questions)),
        )

        logger.debug(
            "Selected %d questions for skill '%s'",
            len(selected_questions),
            skill,
        )

        for question in selected_questions:
            logger.debug(
                "Creating interview question for skill '%s'",
                skill,
            )

            question_obj = InterviewQuestion.objects.create(
                application=application,
                skill=skill,
                question=question,
                difficulty="Medium",
            )

            generated_questions.append(question_obj)

    logger.info(
        "Generated %d interview questions for application_id=%s",
        len(generated_questions),
        application_id,
    )

    return generated_questions