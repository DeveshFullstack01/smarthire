from unittest.mock import MagicMock, patch

from django.test import TestCase

from ai_engine.question_service import generate_interview_questions


class GenerateInterviewQuestionsTests(TestCase):

    # ==========================================================
    # Matched skills should be used
    # ==========================================================

    @patch("ai_engine.question_service.random.sample")
    @patch("ai_engine.question_service.InterviewQuestion.objects.create")
    @patch("ai_engine.question_service.InterviewQuestion.objects.filter")
    @patch("ai_engine.question_service.extract_skills")
    @patch("ai_engine.question_service.Application.objects.select_related")
    def test_generate_questions_using_matched_skills(
        self,
        mock_select_related,
        mock_extract_skills,
        mock_filter,
        mock_create,
        mock_sample,
    ):

        # ------------------------------------------------------
        # Fake Application
        # ------------------------------------------------------

        application = MagicMock()

        application.resume.parsed_data = {
            "matched_skills": ["Java"]
        }

        application.job.description = (
            "Java Spring Boot"
        )

        # ------------------------------------------------------
        # Mock:
        #
        # Application.objects.select_related(...).get(...)
        # ------------------------------------------------------

        mock_select_related.return_value.get.return_value = (
            application
        )

        # ------------------------------------------------------
        # Mock delete()
        # ------------------------------------------------------

        mock_filter.return_value.delete.return_value = (
            0,
            {},
        )

        # ------------------------------------------------------
        # Mock random.sample()
        # ------------------------------------------------------

        mock_sample.return_value = [
            {
                "question": "Explain JVM",
                "difficulty": "Medium",
            },
            {
                "question": "Explain OOP",
                "difficulty": "Easy",
            },
        ]

        # ------------------------------------------------------
        # Mock InterviewQuestion.objects.create()
        # ------------------------------------------------------

        mock_create.side_effect = (
            lambda **kwargs: MagicMock(**kwargs)
        )

        # ------------------------------------------------------
        # Execute
        # ------------------------------------------------------

        questions = generate_interview_questions(1)

        # ------------------------------------------------------
        # Verify
        # ------------------------------------------------------

        self.assertEqual(
            len(questions),
            2,
        )

        # Because matched_skills already exists,
        # extract_skills() should NOT be called.
        mock_extract_skills.assert_called_once_with(
            "Java Spring Boot"
        )

        self.assertEqual(
            mock_create.call_count,
            2,
        )


    # ==========================================================
    # No matched skills:
    # fall back to job description skills
    # ==========================================================

    @patch("ai_engine.question_service.random.sample")
    @patch("ai_engine.question_service.InterviewQuestion.objects.create")
    @patch("ai_engine.question_service.InterviewQuestion.objects.filter")
    @patch("ai_engine.question_service.extract_skills")
    @patch("ai_engine.question_service.Application.objects.select_related")
    def test_generate_questions_using_job_skills_when_no_match(
        self,
        mock_select_related,
        mock_extract_skills,
        mock_filter,
        mock_create,
        mock_sample,
    ):

        # ------------------------------------------------------
        # Fake Application
        # ------------------------------------------------------

        application = MagicMock()

        application.resume.parsed_data = {
            "matched_skills": []
        }

        application.job.description = (
            "Java Spring Boot"
        )

        mock_select_related.return_value.get.return_value = (
            application
        )

        # ------------------------------------------------------
        # Job skills
        # ------------------------------------------------------

        mock_extract_skills.return_value = [
            "Java",
            "Spring Boot",
        ]

        # ------------------------------------------------------
        # Mock delete()
        # ------------------------------------------------------

        mock_filter.return_value.delete.return_value = (
            0,
            {},
        )

        # ------------------------------------------------------
        # Mock questions
        # ------------------------------------------------------

        mock_sample.return_value = [
            {
                "question": "Explain JVM",
                "difficulty": "Medium",
            }
        ]

        mock_create.side_effect = (
            lambda **kwargs: MagicMock(**kwargs)
        )

        # ------------------------------------------------------
        # Execute
        # ------------------------------------------------------

        questions = generate_interview_questions(1)

        # ------------------------------------------------------
        # Verify
        # ------------------------------------------------------

        self.assertGreater(
            len(questions),
            0,
        )

        mock_extract_skills.assert_called_once_with(
            "Java Spring Boot"
        )

        self.assertGreater(
            mock_create.call_count,
            0,
        )


    # ==========================================================
    # Unknown skill:
    # no questions should be generated
    # ==========================================================

    @patch("ai_engine.question_service.random.sample")
    @patch("ai_engine.question_service.InterviewQuestion.objects.create")
    @patch("ai_engine.question_service.InterviewQuestion.objects.filter")
    @patch("ai_engine.question_service.extract_skills")
    @patch("ai_engine.question_service.Application.objects.select_related")
    def test_unknown_skill_generates_no_questions(
        self,
        mock_select_related,
        mock_extract_skills,
        mock_filter,
        mock_create,
        mock_sample,
    ):

        # ------------------------------------------------------
        # Fake Application
        # ------------------------------------------------------

        application = MagicMock()

        application.resume.parsed_data = {
            "matched_skills": []
        }

        application.job.description = (
            "Unknown Skill"
        )

        mock_select_related.return_value.get.return_value = (
            application
        )

        # ------------------------------------------------------
        # Unknown skill returned by extractor
        # ------------------------------------------------------

        mock_extract_skills.return_value = [
            "Unknown Skill"
        ]

        # ------------------------------------------------------
        # Mock delete()
        # ------------------------------------------------------

        mock_filter.return_value.delete.return_value = (
            0,
            {},
        )

        # ------------------------------------------------------
        # Execute
        # ------------------------------------------------------

        questions = generate_interview_questions(1)

        # ------------------------------------------------------
        # Verify
        # ------------------------------------------------------

        self.assertEqual(
            questions,
            [],
        )

        # Unknown skill is not present in QUESTION_BANK,
        # therefore no question should be created.
        mock_create.assert_not_called()

        # random.sample() should also never be called.
        mock_sample.assert_not_called()