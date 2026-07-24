from ai_engine.parser import extract_text_from_pdf
from ai_engine.services import calculate_match_score


resume = extract_text_from_pdf("sample_resume.pdf")


job_description = """
Looking for a Java Developer.

Skills Required:

Java
Spring Boot
Docker
Kubernetes
AWS
PostgreSQL
Kafka
Microservices
Git
"""


result = calculate_match_score(
    resume,
    job_description,
)

print()

print("Match Score:", result["score"], "%")

print()

print("Matched Skills")

for skill in result["matched"]:
    print("-", skill)

print()

print("Missing Skills")

for skill in result["missing"]:
    print("-", skill)