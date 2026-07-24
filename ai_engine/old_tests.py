from django.test import TestCase

from ai_engine.extractor import extract_skills


class ExtractSkillsTest(TestCase):

    def test_extract_multiple_skills(self):
        text = "Java Spring Boot Docker PostgreSQL"

        skills = extract_skills(text)

        self.assertIn("Java", skills)
        self.assertIn("Spring Boot", skills)
        self.assertIn("Docker", skills)
        self.assertIn("PostgreSQL", skills)

    def test_no_skills_found(self):
        text = "I enjoy reading books and playing football."

        skills = extract_skills(text)

        self.assertEqual(skills, [])

    def test_duplicate_skills_removed(self):
        text = "Java Java Java Spring Boot Spring Boot"

        skills = extract_skills(text)

        self.assertEqual(skills.count("Java"), 1)
        self.assertEqual(skills.count("Spring Boot"), 1)