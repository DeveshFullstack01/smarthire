from ai_engine.parser import extract_text_from_pdf

pdf_path = "sample_resume.pdf"

text = extract_text_from_pdf(pdf_path)

print(text)