from unittest.mock import MagicMock, patch

from django.test import TestCase

from ai_engine.question_service import generate_interview_questions


class GenerateInterviewQuestionsTests(TestCase):

    @patch("ai_engine.question_service.random.sample")
    @patch("ai_engine.question_service.InterviewQuestion.objects.create")
    @patch("ai_engine.question_service.InterviewQuestion.objects.filter")
    @patch("ai_engine.question_service.extract_skills")
    @patch("ai_engine.question_service.calculate_match_score")
    @patch("ai_engine.question_service.Application.objects.get")
    def test_generate_questions_using_matched_skills(
        self,
        mock_application,
        mock_match_score,
        mock_extract_skills,
        mock_filter,
        mock_create,
        mock_sample,
    ):
        application = MagicMock()
        application.resume.file.path = "resume.pdf"
        application.job.description = "Java Spring Boot"

        mock_application.return_value = application

        mock_match_score.return_value = {
            "matched_skills": ["Java"],
        }

        mock_extract_skills.return_value = [
            "Java",
            "Spring Boot",
        ]

        mock_filter.return_value.delete.return_value = (0, {})

        mock_sample.return_value = [
            "Explain JVM",
            "Explain OOP",
        ]

        mock_create.side_effect = (
            lambda **kwargs: MagicMock(**kwargs)
        )

        questions = generate_interview_questions(1)

        self.assertEqual(len(questions), 2)

        mock_match_score.assert_called_once()

        mock_create.assert_called()

    @patch("ai_engine.question_service.random.sample")
    @patch("ai_engine.question_service.InterviewQuestion.objects.create")
    @patch("ai_engine.question_service.InterviewQuestion.objects.filter")
    @patch("ai_engine.question_service.extract_skills")
    @patch("ai_engine.question_service.calculate_match_score")
    @patch("ai_engine.question_service.Application.objects.get")
    def test_generate_questions_using_job_skills_when_no_match(
        self,
        mock_application,
        mock_match_score,
        mock_extract_skills,
        mock_filter,
        mock_create,
        mock_sample,
    ):
        application = MagicMock()
        application.resume.file.path = "resume.pdf"
        application.job.description = "Java Spring Boot"

        mock_application.return_value = application

        mock_match_score.return_value = {
            "matched_skills": [],
        }

        mock_extract_skills.return_value = [
            "Java",
            "Spring Boot",
        ]

        mock_filter.return_value.delete.return_value = (0, {})

        mock_sample.return_value = [
            "Question 1",
        ]

        mock_create.side_effect = (
            lambda **kwargs: MagicMock(**kwargs)
        )

        questions = generate_interview_questions(1)

        self.assertGreater(len(questions), 0)

    @patch("ai_engine.question_service.InterviewQuestion.objects.filter")
    @patch("ai_engine.question_service.extract_skills")
    @patch("ai_engine.question_service.calculate_match_score")
    @patch("ai_engine.question_service.Application.objects.get")
    def test_unknown_skill_generates_no_questions(
        self,
        mock_application,
        mock_match_score,
        mock_extract_skills,
        mock_filter,
    ):
        application = MagicMock()
        application.resume.file.path = "resume.pdf"
        application.job.description = "Unknown Skill"

        mock_application.return_value = application

        mock_match_score.return_value = {
            "matched_skills": [],
        }

        mock_extract_skills.return_value = [
            "Unknown Skill",
        ]

        mock_filter.return_value.delete.return_value = (0, {})

        questions = generate_interview_questions(1)

        self.assertEqual(questions, [])