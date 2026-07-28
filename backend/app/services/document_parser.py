"""
Document parser service.

Extracts raw text from uploaded complaint documents.
Supports PDF (pypdf), images (pytesseract + Pillow), and plain text / email.
"""
import io
import re
from typing import Optional

from pypdf import PdfReader
from PIL import Image
import pytesseract


# ─── PDF ──────────────────────────────────────────────────────────────────────

async def extract_text_from_pdf(content: bytes) -> str:
    """
    Extract plain text from a PDF binary using pypdf.

    Iterates every page and concatenates extracted text.
    Returns an empty string if the PDF contains no extractable text
    (e.g. scanned-only PDFs — those should be uploaded as images instead).
    """
    reader = PdfReader(io.BytesIO(content))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    raw = "\n\n".join(pages)
    return _clean_text(raw)


# ─── Image / OCR ──────────────────────────────────────────────────────────────

async def extract_text_from_image(content: bytes) -> str:
    """
    Extract plain text from an image binary using pytesseract OCR.

    Requires the system tesseract binary (tesseract-ocr package).
    Converts the image to RGB before passing to tesseract to handle
    PNG transparency and TIFF multi-channel images.
    """
    image = Image.open(io.BytesIO(content)).convert("RGB")
    raw: str = pytesseract.image_to_string(image, lang="eng")
    return _clean_text(raw)


# ─── Plain text / Email ───────────────────────────────────────────────────────

def clean_email_text(raw: str) -> str:
    """
    Strip common email headers (From:, To:, Subject:, Date:, Cc:, etc.)
    and return the cleaned body text.
    """
    header_pattern = re.compile(
        r"^(From|To|Cc|Bcc|Subject|Date|Reply-To|Message-ID|"
        r"Content-Type|MIME-Version|X-[\w-]+)\s*:.*$",
        re.MULTILINE | re.IGNORECASE,
    )
    stripped = header_pattern.sub("", raw)
    return _clean_text(stripped)


# ─── Dispatcher ───────────────────────────────────────────────────────────────

async def extract_text(
    input_type: str,
    file_content: Optional[bytes] = None,
    raw_text: Optional[str] = None,
) -> str:
    """
    Route extraction to the correct parser based on input_type.

    Args:
        input_type:   "pdf" | "image" | "email" | "text"
        file_content: binary bytes for pdf / image uploads
        raw_text:     plain string for email / text inputs

    Returns:
        Cleaned extracted text string.

    Raises:
        ValueError: if required arguments are missing for the given input_type.
    """
    if input_type == "pdf":
        if not file_content:
            raise ValueError("file_content is required for PDF extraction.")
        return await extract_text_from_pdf(file_content)

    if input_type == "image":
        if not file_content:
            raise ValueError("file_content is required for image OCR.")
        return await extract_text_from_image(file_content)

    if input_type == "email":
        if not raw_text:
            raise ValueError("raw_text is required for email extraction.")
        return clean_email_text(raw_text)

    if input_type == "text":
        if not raw_text:
            raise ValueError("raw_text is required for text extraction.")
        return _clean_text(raw_text)

    raise ValueError(f"Unsupported input_type: '{input_type}'")


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """
    Normalise whitespace:
    - collapse multiple blank lines into one
    - strip leading/trailing whitespace per line
    - strip overall leading/trailing whitespace
    """
    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace on each line
    lines = [line.rstrip() for line in text.split("\n")]
    # Collapse 3+ consecutive blank lines into two
    cleaned: list[str] = []
    blank_count = 0
    for line in lines:
        if line == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)
    return "\n".join(cleaned).strip()
