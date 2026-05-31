from pathlib import Path


def images_to_pdf(image_paths: list[Path], output_pdf: Path) -> Path:
    from PIL import Image

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    opened = [Image.open(path).convert("RGB") for path in image_paths]
    if not opened:
        raise ValueError("At least one image is required")
    first, rest = opened[0], opened[1:]
    first.save(output_pdf, save_all=True, append_images=rest)
    for image in opened:
        image.close()
    return output_pdf


def pdf_to_images(input_pdf: Path, output_dir: Path, image_format: str = "png") -> list[Path]:
    import fitz

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    document = fitz.open(input_pdf)
    for index, page in enumerate(document, start=1):
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        output = output_dir / f"page-{index:03d}.{image_format}"
        pixmap.save(output)
        paths.append(output)
    document.close()
    return paths


def merge_pdfs(input_pdfs: list[Path], output_pdf: Path) -> Path:
    from pypdf import PdfWriter

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    for path in input_pdfs:
        writer.append(str(path))
    with output_pdf.open("wb") as file:
        writer.write(file)
    return output_pdf


def split_pdf(input_pdf: Path, output_dir: Path) -> list[Path]:
    from pypdf import PdfReader, PdfWriter

    output_dir.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(input_pdf))
    outputs: list[Path] = []
    for index, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        output = output_dir / f"page-{index:03d}.pdf"
        with output.open("wb") as file:
            writer.write(file)
        outputs.append(output)
    return outputs


def extract_pages(input_pdf: Path, output_pdf: Path, pages: list[int]) -> Path:
    from pypdf import PdfReader, PdfWriter

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()
    for page_number in pages:
        writer.add_page(reader.pages[page_number - 1])
    with output_pdf.open("wb") as file:
        writer.write(file)
    return output_pdf


def rotate_pdf(input_pdf: Path, output_pdf: Path, degrees: int = 90) -> Path:
    from pypdf import PdfReader, PdfWriter

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(degrees)
        writer.add_page(page)
    with output_pdf.open("wb") as file:
        writer.write(file)
    return output_pdf


def protect_pdf(input_pdf: Path, output_pdf: Path, password: str) -> Path:
    from pypdf import PdfReader, PdfWriter

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    with output_pdf.open("wb") as file:
        writer.write(file)
    return output_pdf


def unlock_pdf(input_pdf: Path, output_pdf: Path, password: str) -> Path:
    from pypdf import PdfReader, PdfWriter

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(input_pdf))
    if reader.is_encrypted:
        reader.decrypt(password)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with output_pdf.open("wb") as file:
        writer.write(file)
    return output_pdf


def compress_pdf(input_pdf: Path, output_pdf: Path) -> Path:
    import fitz

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    document = fitz.open(input_pdf)
    document.save(output_pdf, garbage=4, deflate=True, clean=True)
    document.close()
    return output_pdf

