from pathlib import Path
from tempfile import mkdtemp
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.config import get_settings
from app.services import ai_tools, archive_tools, image_tools, ocr_tools, pdf_tools


router = APIRouter(prefix="/tools", tags=["tools"])


def _workdir() -> Path:
    return Path(mkdtemp(dir=get_settings().storage_dir))


async def _save_upload(upload: UploadFile, directory: Path) -> Path:
    suffix = Path(upload.filename or "upload.bin").suffix or ".bin"
    path = directory / f"input{suffix}"
    data = await upload.read()
    path.write_bytes(data)
    return path


async def _save_uploads(files: list[UploadFile], directory: Path) -> list[Path]:
    paths: list[Path] = []
    for index, upload in enumerate(files, start=1):
        suffix = Path(upload.filename or f"upload-{index}.bin").suffix or ".bin"
        path = directory / f"input-{index}{suffix}"
        path.write_bytes(await upload.read())
        paths.append(path)
    return paths


def _download(path: Path, media_type: str = "application/octet-stream") -> FileResponse:
    return FileResponse(path, media_type=media_type, filename=path.name)


@router.post("/pdf/image-to-pdf")
async def image_to_pdf(files: Annotated[list[UploadFile], File(...)]) -> FileResponse:
    root = _workdir()
    inputs = await _save_uploads(files, root)
    output = pdf_tools.images_to_pdf(inputs, root / "images.pdf")
    return _download(output, "application/pdf")


@router.post("/pdf/to-images")
async def pdf_to_images(file: Annotated[UploadFile, File(...)], image_format: Annotated[str, Form()] = "png") -> FileResponse:
    root = _workdir()
    input_pdf = await _save_upload(file, root)
    images = pdf_tools.pdf_to_images(input_pdf, root / "images", image_format)
    archive = archive_tools.zip_files(images, root / "images.zip")
    return _download(archive, "application/zip")


@router.post("/pdf/merge")
async def merge_pdfs(files: Annotated[list[UploadFile], File(...)]) -> FileResponse:
    root = _workdir()
    inputs = await _save_uploads(files, root)
    output = pdf_tools.merge_pdfs(inputs, root / "merged.pdf")
    return _download(output, "application/pdf")


@router.post("/pdf/split")
async def split_pdf(file: Annotated[UploadFile, File(...)]) -> FileResponse:
    root = _workdir()
    input_pdf = await _save_upload(file, root)
    pages = pdf_tools.split_pdf(input_pdf, root / "pages")
    archive = archive_tools.zip_files(pages, root / "split-pages.zip")
    return _download(archive, "application/zip")


@router.post("/pdf/compress")
async def compress_pdf(file: Annotated[UploadFile, File(...)]) -> FileResponse:
    root = _workdir()
    input_pdf = await _save_upload(file, root)
    output = pdf_tools.compress_pdf(input_pdf, root / "compressed.pdf")
    return _download(output, "application/pdf")


@router.post("/pdf/protect")
async def protect_pdf(file: Annotated[UploadFile, File(...)], password: Annotated[str, Form(...)]) -> FileResponse:
    root = _workdir()
    input_pdf = await _save_upload(file, root)
    output = pdf_tools.protect_pdf(input_pdf, root / "protected.pdf", password)
    return _download(output, "application/pdf")


@router.post("/pdf/unlock")
async def unlock_pdf(file: Annotated[UploadFile, File(...)], password: Annotated[str, Form(...)]) -> FileResponse:
    root = _workdir()
    input_pdf = await _save_upload(file, root)
    output = pdf_tools.unlock_pdf(input_pdf, root / "unlocked.pdf", password)
    return _download(output, "application/pdf")


@router.post("/pdf/rotate")
async def rotate_pdf(file: Annotated[UploadFile, File(...)], degrees: Annotated[int, Form()] = 90) -> FileResponse:
    root = _workdir()
    input_pdf = await _save_upload(file, root)
    output = pdf_tools.rotate_pdf(input_pdf, root / "rotated.pdf", degrees)
    return _download(output, "application/pdf")


@router.post("/pdf/extract")
async def extract_pages(file: Annotated[UploadFile, File(...)], pages: Annotated[str, Form(...)]) -> FileResponse:
    page_numbers = [int(value.strip()) for value in pages.split(",") if value.strip()]
    root = _workdir()
    input_pdf = await _save_upload(file, root)
    output = pdf_tools.extract_pages(input_pdf, root / "extracted.pdf", page_numbers)
    return _download(output, "application/pdf")


@router.post("/image/convert")
async def convert_image(file: Annotated[UploadFile, File(...)], format_name: Annotated[str, Form()] = "png") -> FileResponse:
    root = _workdir()
    input_image = await _save_upload(file, root)
    output = image_tools.convert_image(input_image, root / f"converted.{format_name.lower()}", format_name)
    return _download(output, f"image/{format_name.lower()}")


@router.post("/image/compress")
async def compress_image(file: Annotated[UploadFile, File(...)], quality: Annotated[int, Form()] = 75) -> FileResponse:
    root = _workdir()
    input_image = await _save_upload(file, root)
    output = image_tools.compress_image(input_image, root / f"compressed{input_image.suffix}", quality)
    return _download(output)


@router.post("/image/resize")
async def resize_image(
    file: Annotated[UploadFile, File(...)],
    width: Annotated[int, Form(...)],
    height: Annotated[int, Form(...)],
) -> FileResponse:
    root = _workdir()
    input_image = await _save_upload(file, root)
    output = image_tools.resize_image(input_image, root / f"resized{input_image.suffix}", width, height)
    return _download(output)


@router.post("/image/crop")
async def crop_image(
    file: Annotated[UploadFile, File(...)],
    left: Annotated[int, Form(...)],
    top: Annotated[int, Form(...)],
    right: Annotated[int, Form(...)],
    bottom: Annotated[int, Form(...)],
) -> FileResponse:
    root = _workdir()
    input_image = await _save_upload(file, root)
    output = image_tools.crop_image(input_image, root / f"cropped{input_image.suffix}", left, top, right, bottom)
    return _download(output)


@router.post("/image/watermark")
async def watermark_image(file: Annotated[UploadFile, File(...)], text: Annotated[str, Form(...)]) -> FileResponse:
    root = _workdir()
    input_image = await _save_upload(file, root)
    output = image_tools.watermark_image(input_image, root / f"watermarked{input_image.suffix}", text)
    return _download(output)


@router.post("/archive/zip")
async def zip_uploads(files: Annotated[list[UploadFile], File(...)]) -> FileResponse:
    root = _workdir()
    inputs = await _save_uploads(files, root)
    output = archive_tools.zip_files(inputs, root / "bundle.zip")
    return _download(output, "application/zip")


@router.post("/archive/unzip")
async def unzip_upload(file: Annotated[UploadFile, File(...)]) -> FileResponse:
    root = _workdir()
    zip_path = await _save_upload(file, root)
    extracted = archive_tools.unzip_file(zip_path, root / "extracted")
    output = archive_tools.zip_files(extracted, root / "extracted-bundle.zip")
    return _download(output, "application/zip")


@router.post("/ocr/image-to-text")
async def ocr_image(file: Annotated[UploadFile, File(...)], languages: Annotated[str | None, Form()] = None) -> JSONResponse:
    root = _workdir()
    input_image = await _save_upload(file, root)
    text = ocr_tools.image_to_text(input_image, languages or get_settings().ocr_languages)
    return JSONResponse({"text": text})


@router.post("/ocr/pdf-to-text")
async def ocr_pdf(file: Annotated[UploadFile, File(...)]) -> JSONResponse:
    root = _workdir()
    input_pdf = await _save_upload(file, root)
    text = ocr_tools.pdf_to_text(input_pdf)
    return JSONResponse({"text": text})


@router.post("/ai/summarize")
async def summarize(text: Annotated[str, Form(...)]) -> JSONResponse:
    return JSONResponse({"summary": await ai_tools.summarize_text(text)})


@router.post("/ai/quiz")
async def quiz(text: Annotated[str, Form(...)]) -> JSONResponse:
    return JSONResponse({"quiz": await ai_tools.generate_quiz(text)})


@router.post("/ai/simplify")
async def simplify(text: Annotated[str, Form(...)]) -> JSONResponse:
    return JSONResponse({"notes": await ai_tools.simplify_notes(text)})


@router.post("/ai/flashcards")
async def flashcards(text: Annotated[str, Form(...)]) -> JSONResponse:
    return JSONResponse({"flashcards": await ai_tools.generate_flashcards(text)})


@router.post("/ai/interview")
async def interview(cv_text: Annotated[str, Form(...)]) -> JSONResponse:
    return JSONResponse({"questions": await ai_tools.interview_questions(cv_text)})


@router.post("/ai/translate")
async def translate(text: Annotated[str, Form(...)], target_language: Annotated[str, Form(...)]) -> JSONResponse:
    return JSONResponse({"translation": await ai_tools.translate_text(text, target_language)})


@router.post("/resume/ats-score")
async def ats_score(
    resume_text: Annotated[str, Form(...)],
    job_description: Annotated[str, Form()] = "",
) -> JSONResponse:
    return JSONResponse({"ats_review": await ai_tools.ats_score(resume_text, job_description)})


@router.post("/resume/improve")
async def resume_improve(resume_text: Annotated[str, Form(...)]) -> JSONResponse:
    return JSONResponse({"resume": await ai_tools.improve_resume(resume_text)})


@router.post("/resume/cover-letter")
async def resume_cover_letter(
    resume_text: Annotated[str, Form(...)],
    job_description: Annotated[str, Form()] = "",
) -> JSONResponse:
    return JSONResponse({"cover_letter": await ai_tools.cover_letter(resume_text, job_description)})


@router.post("/resume/linkedin")
async def resume_linkedin(resume_text: Annotated[str, Form(...)]) -> JSONResponse:
    return JSONResponse({"linkedin": await ai_tools.linkedin_profile(resume_text)})


@router.get("/catalog")
def catalog() -> dict:
    return {
        "pdf": ["image-to-pdf", "to-images", "merge", "split", "compress", "protect", "unlock", "rotate", "extract"],
        "image": ["convert", "compress", "resize", "crop", "watermark"],
        "archive": ["zip", "unzip"],
        "ocr": ["image-to-text", "pdf-to-text"],
        "ai": ["summarize", "quiz", "simplify", "flashcards", "interview", "translate"],
        "resume": ["ats-score", "improve", "cover-letter", "linkedin"],
    }
