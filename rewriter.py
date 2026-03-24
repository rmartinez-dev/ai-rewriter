"""
book-rewriter · batch TXT → inglés moderno (multi-archivos)
"""

import re
import sys
import time
import logging
from pathlib import Path

import ollama

# ── CONFIG ────────────────────────────────────────────────────────────────────

MODEL = "gpt-oss:120b-cloud" # gpt-oss:120b-cloud llama3.2:3b
CHUNK_SIZE = 300
MAX_CHUNKS = None   # 🔥 None = todo, o número para testing
DELAY_BETWEEN = 0.5

INPUT_DIR = Path("original")   # carpeta con chapter_*.txt
OUTPUT_DIR = Path("output")

BATCH_SIZE = None   # 🔥 None = todos
START_FROM = 1    # capítulo inicial

PROMPT_TEMPLATE = """\
Rewrite the following passage in clear modern English for a B1/B2 level reader.
Rules:
- Replace archaic or obsolete words with modern equivalents
- Break very long sentences into shorter ones
- Keep the original meaning, narrative voice and tone
- Do NOT add explanations, summaries or commentary
- Output ONLY the rewritten text, nothing else

Text:
{text}"""

# ── LOGGER ────────────────────────────────────────────────────────────────────

def setup_logger():
    logger = logging.getLogger("rewriter")

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                            datefmt="%H:%M:%S")

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(ch)
    return logger

# ── OBTENER ARCHIVOS ──────────────────────────────────────────────────────────

def get_chapter_files():
    files = list(INPUT_DIR.glob("chapter_*.txt"))

    def extract_number(f):
        match = re.search(r"chapter_(\d+)", f.stem)
        return int(match.group(1)) if match else 0

    files.sort(key=extract_number)

    # desde capítulo específico
    files = [f for f in files if extract_number(f) >= START_FROM]

    # limitar batch
    if BATCH_SIZE:
        files = files[:BATCH_SIZE]

    return files

# ── TXT ───────────────────────────────────────────────────────────────────────

def extract_txt(txt_path: Path):
    text = txt_path.read_text(encoding="utf-8")

    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    parts = re.split(r"(CHAPTER\s+\w+.*)", text, flags=re.IGNORECASE)

    chapters = []

    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            title = parts[i].strip()
            body  = parts[i+1].strip()
            chapters.append({"title": title, "text": body})
    else:
        chapters.append({"title": "FULL TEXT", "text": text})

    return chapters

# ── CHUNKS ────────────────────────────────────────────────────────────────────

def split_into_chunks(text, max_words=CHUNK_SIZE):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current, count = [], [], 0

    for para in paragraphs:
        words = len(para.split())
        if count + words > max_words and current:
            chunks.append("\n\n".join(current))
            current, count = [], 0
        current.append(para)
        count += words

    if current:
        chunks.append("\n\n".join(current))

    return chunks

# ── OLLAMA ────────────────────────────────────────────────────────────────────

def rewrite_chunk(text, logger, retries=3):
    prompt = PROMPT_TEMPLATE.format(text=text)

    for attempt in range(1, retries + 1):
        try:
            response = ollama.generate(model=MODEL, prompt=prompt)
            return response["response"].strip()
        except Exception as e:
            logger.warning(f"Intento {attempt} fallido: {e}")
            time.sleep(2 * attempt)

    logger.error("Fallback → texto original")
    return text

# ── PROGRESS ──────────────────────────────────────────────────────────────────

def progress(current, total, label=""):
    pct = current / total * 100
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    print(f"\r[{bar}] {pct:5.1f}%  {label[:50]:<50}", end="", flush=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    logger = setup_logger()

    if not INPUT_DIR.exists():
        print(f"❌ No existe la carpeta: {INPUT_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    try:
        ollama.list()
    except:
        print("❌ Ollama no está corriendo (usa: ollama serve)")
        sys.exit(1)

    files = get_chapter_files()

    if not files:
        print("❌ No hay archivos para procesar")
        return

    logger.info(f"Archivos a procesar: {len(files)}\n")

    for file in files:
        output_file = OUTPUT_DIR / f"{file.stem}_modern.txt"

        # 🔥 SKIP si ya existe
        if output_file.exists():
            logger.info(f"⏭️  Saltando (ya existe): {file.name}")
            continue

        logger.info(f"\n📘 Procesando: {file.name}")

        chapters = extract_txt(file)

        all_chunks = []
        for ch_idx, chapter in enumerate(chapters):
            for chunk in split_into_chunks(chapter["text"]):
                all_chunks.append({
                    "chapter_idx": ch_idx,
                    "title": chapter["title"],
                    "text": chunk
                })

        total = min(len(all_chunks), MAX_CHUNKS) if MAX_CHUNKS else len(all_chunks)

        rewritten_by_chapter = {}

        for i, chunk in enumerate(all_chunks):
            if MAX_CHUNKS is not None and i >= MAX_CHUNKS:
                break

            label = f"{file.stem} | chunk {i+1}"
            progress(i + 1, total, label)

            rewritten = rewrite_chunk(chunk["text"], logger)

            rewritten_by_chapter.setdefault(chunk["chapter_idx"], []).append(rewritten)

            time.sleep(DELAY_BETWEEN)

        print()

        lines = []

        for ch_idx in sorted(rewritten_by_chapter):
            lines.append("\n\n".join(rewritten_by_chapter[ch_idx]))

        output_file.write_text("\n\n".join(lines), encoding="utf-8")

        logger.info(f"✅ Guardado: {output_file}")

# ── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()