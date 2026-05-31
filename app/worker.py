from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.db import SessionLocal
from app.models import ConversionJob, JobStatus
from app.services import archive_tools, image_tools, pdf_tools


def run_job(job_id: int) -> None:
    with SessionLocal() as db:
        job = db.scalar(select(ConversionJob).where(ConversionJob.id == job_id))
        if not job:
            return
        job.status = JobStatus.processing.value
        db.commit()
        try:
            output = _execute(job)
            job.output_path = str(output) if output else None
            job.status = JobStatus.completed.value
            job.completed_at = datetime.now(timezone.utc)
        except Exception as exc:
            job.status = JobStatus.failed.value
            job.error = str(exc)
        db.commit()


def _execute(job: ConversionJob) -> Path | None:
    if not job.input_path:
        raise ValueError("input_path is required")
    input_path = Path(job.input_path)
    output_dir = input_path.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if job.feature == "split_pdf":
        archive = output_dir / "split-pages.zip"
        pages = pdf_tools.split_pdf(input_path, output_dir / "pages")
        return archive_tools.zip_files(pages, archive)
    if job.feature == "pdf_to_images":
        archive = output_dir / "images.zip"
        images = pdf_tools.pdf_to_images(input_path, output_dir / "images")
        return archive_tools.zip_files(images, archive)
    if job.feature == "compress_pdf":
        return pdf_tools.compress_pdf(input_path, output_dir / "compressed.pdf")
    if job.feature == "convert_image":
        return image_tools.convert_image(input_path, output_dir / "converted.png", "png")
    if job.feature == "compress_image":
        return image_tools.compress_image(input_path, output_dir / input_path.name)

    raise ValueError(f"Unsupported worker feature: {job.feature}")

