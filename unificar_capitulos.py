from pathlib import Path
import re
from ebooklib import epub

# ── CONFIG ─────────────────────────────────────────────────────────────

INPUT_DIR = Path("output")   # donde están los chapter_*.txt (modern)
OUTPUT_FILE = "book.epub"

BOOK_TITLE = "The Adventures of Tom Sawyer"
BOOK_AUTHOR = "Mark Twain"
COVER_IMAGE = Path("assets/cover.png")   # ruta a la imagen de portada (jpg/png), o None para omitir

# ── UTIL ───────────────────────────────────────────────────────────────

def extract_number(file):
    match = re.search(r"chapter_(\d+)", file.stem)
    return int(match.group(1)) if match else 0

# ── MAIN ───────────────────────────────────────────────────────────────

def main():
    files = list(INPUT_DIR.glob("chapter_*.txt"))

    if not files:
        print("❌ No se encontraron archivos chapter_*.txt")
        return

    # Ordenar capítulos
    files.sort(key=extract_number)

    print(f"📚 Capítulos encontrados: {len(files)}")

    # Crear libro
    book = epub.EpubBook()

    book.set_identifier("id123456")
    book.set_title(BOOK_TITLE)
    book.set_language("en")
    book.add_author(BOOK_AUTHOR)

    if COVER_IMAGE and COVER_IMAGE.exists():
        cover_data = COVER_IMAGE.read_bytes()
        media_type = "image/png" if COVER_IMAGE.suffix.lower() == ".png" else "image/jpeg"
        book.set_cover(COVER_IMAGE.name, cover_data)
        cover_item = book.get_item_with_id("cover-image")
        if cover_item:
            cover_item.media_type = media_type
        print(f"🖼️  Portada añadida: {COVER_IMAGE}")
    elif COVER_IMAGE:
        print(f"⚠️  Portada no encontrada: {COVER_IMAGE}")

    chapters = []

    for file in files:
        number = extract_number(file)
        text = file.read_text(encoding="utf-8")

        # Convertir texto a HTML simple
        html_content = ""
        for para in text.split("\n\n"):
            html_content += f"<p>{para}</p>"

        chapter = epub.EpubHtml(
            title=f"Chapter {number}",
            file_name=f"chap_{number}.xhtml",
            lang="en"
        )

        chapter.content = f"<h1>Chapter {number}</h1>{html_content}"

        book.add_item(chapter)
        chapters.append(chapter)

        print(f"✅ Añadido: Chapter {number}")

    # ── TOC y spine ────────────────────────────────────────────────────

    book.toc = chapters
    book.spine = ["nav"] + chapters

    # Archivos necesarios
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Estilo básico
    style = "body { font-family: serif; } h1 { text-align: center; }"
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )
    book.add_item(nav_css)

    # ── GUARDAR ────────────────────────────────────────────────────────

    epub.write_epub(OUTPUT_FILE, book)

    print(f"\n📘 EPUB creado: {OUTPUT_FILE}")

# ── RUN ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()