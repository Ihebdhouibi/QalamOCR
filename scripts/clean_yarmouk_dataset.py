import argparse
import json
from pathlib import Path

import fitz


def main():
    parser = argparse.ArgumentParser(description="Validate Yarmouk OCR Dataset")
    parser.add_argument(
        "--pdf-root",
        required=True,
        help="Path to the Yarmouk scanned PDF directory",
    )
    parser.add_argument(
        "--text-root",
        required=True,
        help="Path to the Yarmouk OCR text directory",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf_root)
    txt_path = Path(args.text_root)

    valid_pdf = 0
    bad_pdf = []

    for pdf in pdf_path.glob("*.pdf"):
        try:
            doc = fitz.open(pdf)
            doc.close()
            valid_pdf += 1

        except (OSError, RuntimeError):
            bad_pdf.append(pdf.name)

    valid_txt = 0
    empty_txt = []

    for txt in txt_path.glob("*.txt"):
        try:
            content = txt.read_text(
                encoding="utf-8",
                errors="ignore",
            ).strip()

            if content:
                valid_txt += 1
            else:
                empty_txt.append(txt.name)

        except OSError:
            empty_txt.append(txt.name)

    pdf_ids = {pdf.stem for pdf in pdf_path.glob("*.pdf")}
    txt_ids = {txt.stem for txt in txt_path.glob("*.txt")}

    pdf_without_text = pdf_ids - txt_ids
    text_without_pdf = txt_ids - pdf_ids

    report = {
        "dataset": "Yarmouk OCR Dataset",
        "subset": "Training",
        "validation": {
            "pdf_checked": len(pdf_ids),
            "valid_pdf": valid_pdf,
            "bad_pdf": len(bad_pdf),
            "text_files_checked": len(txt_ids),
            "valid_text_files": valid_txt,
            "empty_text_files": len(empty_txt),
            "pdf_without_text": len(pdf_without_text),
            "text_without_pdf": len(text_without_pdf),
        },
    }

    report_path = Path("reports/yarmouk_cleaning_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8") as f:
        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=4,
        )

    print("Yarmouk OCR Dataset")
    print("====================")
    print("Valid PDF:", valid_pdf)
    print("Bad PDF:", len(bad_pdf))
    print("Valid text files:", valid_txt)
    print("Empty text files:", len(empty_txt))
    print("PDF without text:", len(pdf_without_text))
    print("Text without PDF:", len(text_without_pdf))
    print("Yarmouk report saved:", report_path)


if __name__ == "__main__":
    main()
