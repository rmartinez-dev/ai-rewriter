import re
from pathlib import Path

# ── CONFIG ─────────────────────────────────────────────────────────────

INPUT_FILE = Path("book.txt")
OUTPUT_DIR = Path("original")

# ── ROMANO → ENTERO ────────────────────────────────────────────────────

ROMAN_MAP = {
    'I': 1, 'V': 5, 'X': 10,
    'L': 50, 'C': 100,
    'D': 500, 'M': 1000
}

def roman_to_int(roman: str) -> int:
    total = 0
    prev = 0
    for char in reversed(roman):
        value = ROMAN_MAP.get(char, 0)
        if value < prev:
            total -= value
        else:
            total += value
        prev = value
    return total

# ── MAIN ───────────────────────────────────────────────────────────────

def main():
    if not INPUT_FILE.exists():
        print("❌ No existe book.txt")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    text = INPUT_FILE.read_text(encoding="utf-8")

    # Detecta capítulos tipo: CHAPTER I, CHAPTER II...
    pattern = re.compile(r"(CHAPTER\s+([IVXLCDM]+))", re.IGNORECASE)

    matches = list(pattern.finditer(text))

    if not matches:
        print("❌ No se encontraron capítulos")
        return

    print(f"📚 Capítulos encontrados: {len(matches)}")

    for i, match in enumerate(matches):
        start = match.start()

        # Fin del capítulo = inicio del siguiente o fin del texto
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        chapter_text = text[start:end].strip()

        roman = match.group(2).upper()
        number = roman_to_int(roman)

        filename = OUTPUT_DIR / f"chapter_{number}.txt"
        filename.write_text(chapter_text, encoding="utf-8")

        print(f"✅ Guardado: {filename}")

if __name__ == "__main__":
    main()