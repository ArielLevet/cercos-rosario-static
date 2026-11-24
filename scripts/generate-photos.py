"""Convierte los originales a WebP (ampliada + miniatura) y actualiza las galerías HTML.

Para cada categoría lee originals/<carpeta>/, escribe img/<carpeta>/ y reemplaza el bloque
entre <!-- fotos:inicio --> y <!-- fotos:fin --> de la página correspondiente.
Los epígrafes se toman de scripts/captions.json (clave = nombre del archivo sin extensión).
"""

from html import escape
from io import BytesIO
from pathlib import Path
import json
import re
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Falta Pillow. Instalalo con: python -m pip install -r scripts/requirements.txt")

ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "originals"
OUTPUT = ROOT / "img"
CAPTIONS = ROOT / "scripts" / "captions.json"

# carpeta -> página HTML que muestra la galería
CATEGORIES = {
    "cercos": "cercos-perimetrales.html",
    "portones": "portones-puertas.html",
    "construccion": "construccion-general.html",
}

FULL_MAX_SIDE = 1920
THUMB_MAX_WIDTH = 800
QUALITY = 80
FORMATS = {".jpg", ".jpeg", ".png", ".webp"}
START, END = "<!-- fotos:inicio", "<!-- fotos:fin -->"


def natural_key(path: Path):
    return [int(p) if p.isdigit() else p.casefold() for p in re.split(r"(\d+)", path.name)]


def encode(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="WEBP", quality=QUALITY, method=6)
    return buffer.getvalue()


def make_versions(source: Path, full: Path, thumb: Path) -> tuple[int, int]:
    """Crea las versiones que falten. Devuelve el tamaño (ancho, alto) de la miniatura."""
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original)
        image = image.convert("RGBA" if image.has_transparency_data else "RGB")
    if not full.exists():
        big = image.copy()
        big.thumbnail((FULL_MAX_SIDE, FULL_MAX_SIDE), Image.Resampling.LANCZOS)
        data = encode(big)
        full.write_bytes(data)
        print(f"  Creada {full.name} ({big.width}x{big.height}, {len(data) / 1024:.0f} KB)")
        if len(data) > 500 * 1024:
            print("    Supera 500 KB; se conserva calidad 80 para revisión visual.")
    if not thumb.exists():
        small = image.copy()
        if small.width > THUMB_MAX_WIDTH:
            height = max(1, round(small.height * THUMB_MAX_WIDTH / small.width))
            small = small.resize((THUMB_MAX_WIDTH, height), Image.Resampling.LANCZOS)
        data = encode(small)
        thumb.write_bytes(data)
        print(f"  Creada {thumb.name} ({small.width}x{small.height}, {len(data) / 1024:.0f} KB)")
    with Image.open(thumb) as t:
        return t.size


def figure(folder: str, stem: str, number: int, caption: str, size: tuple[int, int]) -> str:
    alt = escape(caption, quote=True)
    return (
        "        <figure>\n"
        f'          <a href="img/{folder}/{stem}.webp" data-lightbox>\n'
        f'            <img src="img/{folder}/{stem}_thumb.webp" alt="{alt}" width="{size[0]}" height="{size[1]}" loading="lazy">\n'
        "          </a>\n"
        f"          <figcaption><span>{number}</span>{escape(caption)}</figcaption>\n"
        "        </figure>\n"
    )


def update_page(page: Path, figures: str) -> None:
    text = page.read_text(encoding="utf-8")
    start = text.find(START)
    end = text.find(END)
    if start < 0 or end < 0 or end < start:
        sys.exit(f"Faltan los marcadores de fotos en {page.name}")
    start_line_end = text.index("\n", start) + 1
    end_line_start = text.rfind("\n", 0, end) + 1
    new = text[:start_line_end] + figures + text[end_line_start:]
    if new != text:
        page.write_text(new, encoding="utf-8", newline="\n")
        print(f"  Actualizada {page.name}")


def main() -> int:
    captions = json.loads(CAPTIONS.read_text(encoding="utf-8")) if CAPTIONS.exists() else {}
    errors = 0
    for folder, page_name in CATEGORIES.items():
        source_dir = ORIGINALS / folder
        if not source_dir.is_dir():
            print(f"No existe {source_dir}", file=sys.stderr)
            errors += 1
            continue
        print(f"[{folder}]")
        files = sorted((p for p in source_dir.iterdir() if p.is_file() and p.suffix.lower() in FORMATS),
                       key=natural_key)
        stems = [p.stem.casefold() for p in files]
        if len(stems) != len(set(stems)):
            print(f"Nombres base repetidos en {source_dir}", file=sys.stderr)
            errors += 1
            continue
        out_dir = OUTPUT / folder
        out_dir.mkdir(parents=True, exist_ok=True)
        folder_captions = captions.get(folder, {})
        blocks = []
        for source in files:
            full = out_dir / f"{source.stem}.webp"
            thumb = out_dir / f"{source.stem}_thumb.webp"
            try:
                size = make_versions(source, full, thumb)
            except (OSError, ValueError, Image.DecompressionBombError) as error:
                print(f"  Error en {source.name}: {error}", file=sys.stderr)
                errors += 1
                continue
            caption = folder_captions.get(source.stem)
            if caption is None:
                print(f"  Sin epígrafe para '{source.stem}' (agregalo a scripts/captions.json)")
                caption = ""
            blocks.append((source.stem, caption, size))
        figures = "".join(figure(folder, s, n, c, sz) for n, (s, c, sz) in enumerate(blocks, 1))
        update_page(ROOT / page_name, figures)
        print(f"  {len(blocks)} fotos")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
