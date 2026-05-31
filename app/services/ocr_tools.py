from pathlib import Path


def image_to_text(image_path: Path, languages: str = "eng") -> str:
    import pytesseract
    from PIL import Image

    with Image.open(image_path) as image:
        return pytesseract.image_to_string(image, lang=languages).strip()


def pdf_to_text(pdf_path: Path) -> str:
    import fitz

    chunks: list[str] = []
    document = fitz.open(pdf_path)
    for page in document:
        chunks.append(page.get_text())
    document.close()
    return "\n".join(chunks).strip()

