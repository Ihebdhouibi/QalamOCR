import argparse
import json
import os


def main():
    parser = argparse.ArgumentParser(description="Unify Arabic OCR datasets metadata")
    parser.add_argument(
        "--arabic-docs-root",
        required=True,
        help="Path to the Arabic Documents OCR Dataset/Documents/Documents directory",
    )
    parser.add_argument(
        "--yarmouk-pdf-root",
        required=True,
        help="Path to the Yarmouk OCR Dataset scanned PDFs directory",
    )
    parser.add_argument(
        "--yarmouk-text-root",
        required=True,
        help="Path to the Yarmouk OCR Dataset OCR text directory",
    )
    parser.add_argument(
        "--output",
        default="unified_metadata.json",
        help="Output path for unified metadata JSON",
    )

    args = parser.parse_args()

    unified_samples = []

    # =====================================
    # Arabic Documents OCR Dataset
    # =====================================

    arabic_docs_root = args.arabic_docs_root

    for root, dirs, files in os.walk(arabic_docs_root):
        if root.endswith(("/img", "\\img")):
            for img in files:
                if img.lower().endswith((".jpg", ".jpeg", ".png")):
                    img_path = os.path.join(root, img)

                    ann_root = root.replace("/img", "/ann").replace("\\img", "\\ann")

                    ann_path = os.path.join(
                        ann_root,
                        os.path.splitext(img)[0] + ".json",
                    )

                    unified_samples.append(
                        {
                            "source": "Arabic Documents OCR Dataset",
                            "file": img_path,
                            "annotation": (
                                ann_path if os.path.exists(ann_path) else None
                            ),
                            "annotation_type": "JSON",
                            "text_available": bool(os.path.exists(ann_path)),
                        }
                    )

    # =====================================
    # Yarmouk OCR Dataset
    # =====================================

    yarmouk_pdf_root = args.yarmouk_pdf_root
    yarmouk_text_root = args.yarmouk_text_root

    for pdf in os.listdir(yarmouk_pdf_root):
        if pdf.endswith(".pdf"):
            txt_file = pdf.replace(".pdf", ".txt")

            txt_path = os.path.join(yarmouk_text_root, txt_file)

            unified_samples.append(
                {
                    "source": "Yarmouk OCR Dataset",
                    "file": os.path.join(yarmouk_pdf_root, pdf),
                    "annotation": (txt_path if os.path.exists(txt_path) else None),
                    "annotation_type": "OCR text",
                    "text_available": bool(os.path.exists(txt_path)),
                }
            )

    # =====================================
    # Save Unified Metadata
    # =====================================

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(
            unified_samples,
            f,
            ensure_ascii=False,
            indent=4,
        )

    print("Total unified samples:", len(unified_samples))
    print("Unified metadata saved")


if __name__ == "__main__":
    main()
