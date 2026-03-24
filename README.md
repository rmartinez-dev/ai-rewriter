# book-rewriter

Convierte un libro `.epub` de inglés antiguo a inglés moderno (nivel B1/B2)
usando **Ollama + Llama 3.2 3B** completamente local, sin internet ni costo.

---

## Requisitos

- Python 3.10 o superior
- [Ollama](https://ollama.com) instalado y corriendo
- Modelo `llama3.2:3b` descargado

---

## Instalación

```bash
# 1. Clona o descarga el proyecto
cd book-rewriter

# 2. Crea entorno virtual (recomendado)
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Asegúrate de tener el modelo en Ollama
ollama pull llama3.2:3b
```

---

## Uso

### Uso básico

```bash
python rewriter.py input/mi_libro.epub
```

El resultado se guarda en `output/mi_libro_modern.txt`

### Opciones disponibles

```bash
python rewriter.py input/mi_libro.epub --output mi_carpeta/
python rewriter.py input/mi_libro.epub --chunk-size 200
python rewriter.py input/mi_libro.epub --model llama3.1:8b
```

| Opción | Default | Descripción |
|---|---|---|
| `--output` | `output/` | Carpeta donde guardar el resultado |
| `--chunk-size` | `300` | Palabras por fragmento enviado al modelo |
| `--model` | `llama3.2:3b` | Modelo Ollama a usar |

---

## Estructura del proyecto

```
book-rewriter/
├── rewriter.py          ← script principal
├── requirements.txt     ← dependencias Python
├── README.md
├── input/               ← pon aquí tus archivos .epub
├── output/              ← aquí aparece el .txt reescrito
└── logs/                ← logs de cada ejecución
```

---

## Estimación de tiempo (i7-10700T, 16GB RAM, sin GPU)

| Tamaño del libro | Chunks aprox. | Tiempo estimado |
|---|---|---|
| Novela corta (50k palabras) | ~170 | 2–4 horas |
| Novela estándar (100k palabras) | ~334 | 4–8 horas |
| Libro largo (200k palabras) | ~667 | 8–15 horas |

> Tip: puedes dejar corriendo de noche. El script guarda progreso en logs/.

---

## Solución de problemas

**"Ollama no está corriendo"**
```bash
ollama serve
```

**"Model not found"**
```bash
ollama pull llama3.2:3b
```

**El resultado tiene texto extraño o mezcla idiomas**
→ Reduce el chunk-size: `--chunk-size 150`

**El proceso es muy lento**
→ Cierra otras aplicaciones para liberar RAM.
→ Considera usar la API de Claude como alternativa (~$5 USD por libro).
