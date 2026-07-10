import os
from pathlib import Path
from typing import Tuple


def read_document(path: str) -> Tuple[str, dict]:
    """Return raw text and metadata. OCR is attempted for images if pytesseract is installed."""
    ext = Path(path).suffix.lower()
    meta = {"source_file": os.path.basename(path), "extension": ext}

    if ext in [".txt", ".csv", ".log"]:
        return Path(path).read_text(errors="ignore"), meta

    if ext == ".pdf":
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            meta["pages"] = len(reader.pages)
            return text, meta
        except Exception as e:
            return f"", {**meta, "error": f"PDF read failed: {e}"}

    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs), meta
        except Exception as e:
            return "", {**meta, "error": f"DOCX read failed: {e}"}

    if ext in [".xlsx", ".xlsm"]:
        try:
            import pandas as pd
            frames = pd.read_excel(path, sheet_name=None, engine="openpyxl")
            text = []
            for sheet, df in frames.items():
                text.append(f"SHEET: {sheet}")
                text.append(df.astype(str).to_csv(index=False))
            return "\n".join(text), meta
        except Exception as e:
            return "", {**meta, "error": f"Excel read failed: {e}"}

    if ext in [".png", ".jpg", ".jpeg", ".tif", ".tiff"]:
        try:
            from PIL import Image
            import pytesseract
            return pytesseract.image_to_string(Image.open(path)), meta
        except Exception as e:
            return "", {**meta, "error": f"OCR failed: {e}"}

    return "", {**meta, "error": "Unsupported file type"}
