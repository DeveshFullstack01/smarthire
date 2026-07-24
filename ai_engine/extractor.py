import re


# Technologies our ATS understands
KNOWN_SKILLS = [
    "Python",
    "Java",
    "Spring Boot",
    "Django",
    "Flask",
    "FastAPI",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Kafka",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Terraform",
    "Jenkins",
    "Git",
    "GitHub",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
    "Oracle",
    "SQL",
    "REST",
    "REST API",
    "Microservices",
    "JUnit",
    "Mockito",
    "Hibernate",
    "JPA",
    "Maven",
    "Gradle",
    "Linux",
]


def extract_skills(text: str) -> list[str]:
    """
    Extract known technical skills from resume text.
    """

    found_skills = []

    lower_text = text.lower()

    for skill in KNOWN_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, lower_text):
            found_skills.append(skill)

    return sorted(set(found_skills))

def test_extract_skills_case_insensitive(self):
    text = "java spring boot docker postgresql"

    skills = extract_skills(text)

    self.assertIn("Java", skills)
    self.assertIn("Spring Boot", skills)
    self.assertIn("Docker", skills)
    self.assertIn("PostgreSQL", skills)