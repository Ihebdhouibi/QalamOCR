from pathlib import Path
import json

try:
    import fitz  # type: ignore[import]
except ImportError as exc:
    raise ImportError(
        "The PyMuPDF package is required. Install it with 'pip install pymupdf'."
    ) from exc


# =====================================
# Yarmouk OCR Dataset paths
# =====================================

PDF_PATH = Path(
    "/kaggle/input/datasets/eyadwin/yarmouk-ocr-dataset/"
    "Training/Training/Scanned/training/training"
)

TXT_PATH = Path(
    "/kaggle/input/datasets/eyadwin/yarmouk-ocr-dataset/"
    "Training/Training/OCR/text/text"
)


# =====================================
# PDF validation
# =====================================

valid_pdf = 0
bad_pdf = []


for pdf in PDF_PATH.glob("*.pdf"):

    try:
        doc = fitz.open(pdf)
        doc.close()

        valid_pdf += 1

    except Exception:
        bad_pdf.append(pdf.name)


print("Valid PDF:", valid_pdf)
print("Bad PDF:", len(bad_pdf))


# =====================================
# Text validation
# =====================================

valid_txt = 0
empty_txt = []


for txt in TXT_PATH.glob("*.txt"):

    content = txt.read_text(
        encoding="utf-8",
        errors="ignore"
    ).strip()

    if content:
        valid_txt += 1
    else:
        empty_txt.append(txt.name)


print("Valid text files:", valid_txt)
print("Empty text files:", len(empty_txt))


# =====================================
# PDF ↔ Text consistency
# =====================================

pdf_ids = {
    p.stem
    for p in PDF_PATH.glob("*.pdf")
}

txt_ids = {
    t.stem
    for t in TXT_PATH.glob("*.txt")
}


pdf_without_text = pdf_ids - txt_ids
text_without_pdf = txt_ids - pdf_ids


print(
    "PDF without text:",
    len(pdf_without_text)
)

print(
    "Text without PDF:",
    len(text_without_pdf)
)


# =====================================
# Cleaning / validation report
# =====================================

report = {

    "dataset": "Yarmouk OCR Dataset",

    "subset": "Training",

    "validation": {

        "pdf_checked": valid_pdf,

        "valid_pdf": valid_pdf,

        "bad_pdf": len(bad_pdf),

        "text_files_checked": (
            valid_txt + len(empty_txt)
        ),

        "valid_text_files": valid_txt,

        "empty_text_files": len(empty_txt),

        "pdf_without_text": len(
            pdf_without_text
        ),

        "text_without_pdf": len(
            text_without_pdf
        )
    }
}


# =====================================
# Save report
# =====================================

OUTPUT_REPORT = Path(
    "Yarmouk_cleaning_report.json"
)


with open(
    OUTPUT_REPORT,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        report,
        f,
        ensure_ascii=False,
        indent=4
    )


print(
    "Yarmouk report saved:",
    OUTPUT_REPORT
)