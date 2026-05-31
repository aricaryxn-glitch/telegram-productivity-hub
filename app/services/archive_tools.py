from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def zip_files(input_paths: list[Path], output_zip: Path) -> Path:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_zip, "w", compression=ZIP_DEFLATED) as archive:
        for path in input_paths:
            archive.write(path, arcname=path.name)
    return output_zip


def unzip_file(zip_path: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path) as archive:
        archive.extractall(output_dir)
        return [output_dir / name for name in archive.namelist()]

