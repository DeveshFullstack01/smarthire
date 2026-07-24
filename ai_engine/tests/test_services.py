from unittest.mock import patch

from django.test import TestCase

from ai_engine.services import calculate_match_score


class CalculateMatchScoreTests(TestCase):

    @patch("ai_engine.services.extract_text_from_pdf")
    @patch("ai_engine.services.extract_skills")
    def test_full_match_score(
        self,
        mock_extract_skills,
        mock_extract_text,
    ):
        mock_extract_text.return_value = (
            "Java Spring Boot Docker PostgreSQL"
        )

        mock_extract_skills.side_effect = [
            ["Java", "Spring Boot", "Docker", "PostgreSQL"],
            ["Java", "Spring Boot", "Docker", "PostgreSQL"],
        ]

        result = calculate_match_score(
            "resume.pdf",
            "Job Description",
        )

        self.assertEqual(result["score"], 100.0)
        self.assertEqual(
            len(result["matched_skills"]),
            4,
        )
        self.assertEqual(
            len(result["missing_skills"]),
            0,
        )

    @patch("ai_engine.services.extract_text_from_pdf")
    @patch("ai_engine.services.extract_skills")
    def test_partial_match_score(
        self,
        mock_extract_skills,
        mock_extract_text,
    ):
        mock_extract_text.return_value = "Java Docker"

        mock_extract_skills.side_effect = [
            ["Java", "Docker"],
            [
                "Java",
                "Spring Boot",
                "Docker",
                "PostgreSQL",
            ],
        ]

        result = calculate_match_score(
            "resume.pdf",
            "Job Description",
        )

        self.assertEqual(result["score"], 50.0)

        self.assertEqual(
            result["matched_skills"],
            ["Java", "Docker"],
        )

        self.assertEqual(
            result["missing_skills"],
            ["Spring Boot", "PostgreSQL"],
        )

    @patch("ai_engine.services.extract_text_from_pdf")
    @patch("ai_engine.services.extract_skills")
    def test_no_job_skills(
        self,
        mock_extract_skills,
        mock_extract_text,
    ):
        mock_extract_text.return_value = "Java"

        mock_extract_skills.side_effect = [
            ["Java"],
            [],
        ]

        result = calculate_match_score(
            "resume.pdf",
            "",
        )

        self.assertEqual(result["score"], 0)
        self.assertEqual(
            result["matched_skills"],
            [],
        )
        self.assertEqual(
            result["missing_skills"],
            [],
        )

    @patch("ai_engine.services.extract_text_from_pdf")
    @patch("ai_engine.services.extract_skills")
    def test_no_matching_skills(
        self,
        mock_extract_skills,
        mock_extract_text,
    ):
        mock_extract_text.return_value = "Python"

        mock_extract_skills.side_effect = [
            ["Python"],
            ["Java", "Spring Boot"],
        ]

        result = calculate_match_score(
            "resume.pdf",
            "Job Description",
        )

        self.assertEqual(result["score"], 0.0)

        self.assertEqual(
            result["matched_skills"],
            [],
        )

        self.assertEqual(
            result["missing_skills"],
            ["Java", "Spring Boot"],
        )