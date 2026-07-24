from pathlib import Path

from django.test import TestCase

from ai_engine.parser import extract_text_from_pdf


class ParserTests(TestCase):

    def test_invalid_pdf_path_raises_exception(self):
        with self.assertRaises(FileNotFoundError):
            extract_text_from_pdf("does_not_exist.pdf")

    def test_returns_string(self):
        """
        Verify the function returns a string for a valid PDF.
        """

        sample_pdf = Path(__file__).parent / "sample_resume.pdf"

        if sample_pdf.exists():
            text = extract_text_from_pdf(sample_pdf)

            self.assertIsInstance(text, str)