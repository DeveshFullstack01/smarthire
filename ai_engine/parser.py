import logging

import pdfplumber

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    """

    logger.info("Starting PDF text extraction.")

    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        logger.debug(
            "PDF opened successfully with %d pages.",
            len(pdf.pages),
        )

        for index, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)
                logger.debug(
                    "Extracted text from page %d.",
                    index,
                )
            else:
                logger.debug(
                    "No text found on page %d.",
                    index,
                )

    extracted_text = "\n".join(pages)

    logger.info(
        "PDF text extraction completed. Extracted %d characters.",
        len(extracted_text),
    )

    return extracted_text