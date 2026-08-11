import os
import json


unified_samples = []


# =====================================
# Arabic Documents OCR Dataset
# =====================================

arabic_docs_root = "/kaggle/input/datasets/humansintheloop/arabic-documents-ocr-dataset/Documents/Documents"


for root, dirs, files in os.walk(arabic_docs_root):

    if root.endswith("/img"):

        for img in files:

            if img.lower().endswith((".jpg", ".jpeg", ".png")):

                img_path = os.path.join(root, img)

                ann_root = root.replace("/img", "/ann")

                ann_path = os.path.join(
                    ann_root,
                    os.path.splitext(img)[0] + ".json"
                )

                unified_samples.append({
                    "source": "Arabic Documents OCR Dataset",
                    "file": img_path,
                    "annotation": ann_path if os.path.exists(ann_path) else None,
                    "annotation_type": "JSON",
                    "text_available": True if os.path.exists(ann_path) else False
                })


# =====================================
# Yarmouk OCR Dataset
# =====================================

yarmouk_pdf_root = "/kaggle/input/datasets/eyadwin/yarmouk-ocr-dataset/Training/Training/Scanned/training/training"

yarmouk_text_root = "/kaggle/input/datasets/eyadwin/yarmouk-ocr-dataset/Training/Training/OCR/text/text"


for pdf in os.listdir(yarmouk_pdf_root):

    if pdf.endswith(".pdf"):

        txt_file = pdf.replace(".pdf", ".txt")

        txt_path = os.path.join(
            yarmouk_text_root,
            txt_file
        )

        unified_samples.append({

            "source": "Yarmouk OCR Dataset",

            "file": os.path.join(
                yarmouk_pdf_root,
                pdf
            ),

            "annotation": txt_path if os.path.exists(txt_path) else None,

            "annotation_type": "OCR text",

            "text_available": True if os.path.exists(txt_path) else False
        })


# =====================================
# Save Unified Metadata
# =====================================

with open(
    "unified_metadata.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        unified_samples,
        f,
        ensure_ascii=False,
        indent=4
    )


print("Total unified samples:", len(unified_samples))
print("Unified metadata saved")