from pathlib import Path


def convert_image(input_path: Path, output_path: Path, format_name: str) -> Path:
    from PIL import Image

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as image:
        image.convert("RGB").save(output_path, format=format_name.upper())
    return output_path


def compress_image(input_path: Path, output_path: Path, quality: int = 75) -> Path:
    from PIL import Image

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as image:
        image.save(output_path, optimize=True, quality=quality)
    return output_path


def resize_image(input_path: Path, output_path: Path, width: int, height: int) -> Path:
    from PIL import Image

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as image:
        image.resize((width, height)).save(output_path)
    return output_path


def crop_image(input_path: Path, output_path: Path, left: int, top: int, right: int, bottom: int) -> Path:
    from PIL import Image

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path) as image:
        image.crop((left, top, right, bottom)).save(output_path)
    return output_path


def watermark_image(input_path: Path, output_path: Path, text: str) -> Path:
    from PIL import Image, ImageDraw

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(input_path).convert("RGBA") as image:
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        margin = 20
        draw.text((margin, image.height - 40), text, fill=(255, 255, 255, 180))
        Image.alpha_composite(image, overlay).convert("RGB").save(output_path)
    return output_path

