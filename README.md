# Book-rewriter

Convierte capítulos `.txt` de inglés antiguo a inglés moderno (nivel B1/B2)
usando **Ollama** completamente local, sin internet ni costo, y los empaqueta en un `.epub`.

---

## Requisitos

- Python 3.10 o superior
- [Ollama](https://ollama.com) instalado y corriendo
- Modelo configurado en `rewriter.py` (por defecto `gpt-oss:120b-cloud`)

---

## Instalación

```bash
# 1. Clona o descarga el proyecto
cd ai-transcription

# 2. Crea entorno virtual (recomendado)
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 3. Instala dependencias
pip install -r requirements.txt
```

---

## Flujo de trabajo

### Paso 1 — Reescribir capítulos

Coloca los archivos `chapter_1.txt`, `chapter_2.txt`, etc. en la carpeta `original/` y ejecuta:

```bash
python rewriter.py
```

Los archivos reescritos se guardan en `output/` con el nombre `chapter_N_modern.txt`.

- Si un archivo ya existe en `output/`, se omite automáticamente (reanudable).
- Configura las opciones editando las constantes al inicio de `rewriter.py`:

| Variable | Default | Descripción |
|---|---|---|
| `MODEL` | `gpt-oss:120b-cloud` | Modelo Ollama a usar |
| `CHUNK_SIZE` | `300` | Palabras por fragmento enviado al modelo |
| `START_FROM` | `1` | Capítulo desde el que empezar |
| `BATCH_SIZE` | `None` | Límite de capítulos a procesar (`None` = todos) |
| `MAX_CHUNKS` | `None` | Límite de chunks por archivo (útil para testing) |
| `DELAY_BETWEEN` | `0.5` | Segundos de espera entre llamadas al modelo |

### Paso 2 — Generar el EPUB

Una vez procesados los capítulos, ejecuta:

```bash
python unificar_capitulos.py
```

Lee los `chapter_*.txt` de `output/` y genera `book.epub`.

Configura título, autor y portada al inicio de `unificar_capitulos.py`:

| Variable | Descripción |
|---|---|
| `BOOK_TITLE` | Título del libro |
| `BOOK_AUTHOR` | Autor |
| `COVER_IMAGE` | Ruta a la imagen de portada (`.png` o `.jpg`), o `None` para omitir |

---

## Estructura del proyecto

```
ai-transcription/
├── rewriter.py            ← paso 1: reescribe capítulos TXT
├── unificar_capitulos.py  ← paso 2: ensambla el EPUB
├── requirements.txt
├── README.md
├── original/              ← pon aquí los chapter_*.txt originales
├── output/                ← capítulos reescritos (input para el EPUB)
└── assets/
    └── cover.png          ← portada opcional
```

---

## Solución de problemas

**"Ollama no está corriendo"**
```bash
ollama serve
```

**"Model not found"**
```bash
ollama pull <nombre-del-modelo>
```

**El resultado mezcla idiomas o tiene texto extraño**
→ Reduce `CHUNK_SIZE` a `150` en `rewriter.py`.

**El proceso es muy lento**
→ Cierra otras aplicaciones para liberar RAM.
