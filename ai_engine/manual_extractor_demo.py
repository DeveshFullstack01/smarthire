from  ai_engine.parser import extract_text_from_pdf
from  ai_engine.extractor import extract_skills


pdf_path = "sample_resume.pdf"

text = extract_text_from_pdf(pdf_path)

skills = extract_skills(text)

print("\nDetected Skills:\n")

for skill in skills:
    print(skill)