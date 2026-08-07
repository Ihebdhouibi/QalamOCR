import os
import json


unified_samples = []


# ==========================
# Arabic Documents OCR Dataset
# ==========================

arabic_dataset_path = "datasets/arabic_documents"

if os.path.exists(arabic_dataset_path):

    for root, dirs, files in os.walk(arabic_dataset_path):

        for file in files:

            if file.lower().endswith((".jpg", ".jpeg", ".png")):

                unified_samples.append({
                    "id": file,
                    "source": "Arabic Documents OCR Dataset",
                    "file": os.path.join(root, file),
                    "annotation": None,
                    "annotation_type": "image",
                    "text_available": False
                })


# ==========================
# Yarmouk OCR Dataset
# ==========================

yarmouk_path = "datasets/yarmouk"

if os.path.exists(yarmouk_path):

    for root, dirs, files in os.walk(yarmouk_path):

        for file in files:

            if file.lower().endswith((".pdf", ".txt")):

                unified_samples.append({
                    "id": file,
                    "source": "Yarmouk OCR Dataset",
                    "file": os.path.join(root, file),
                    "annotation": None,
                    "annotation_type": "ocr_text",
                    "text_available": file.endswith(".txt")
                })


# ==========================
# Create JSON
# ==========================

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


print("Total samples:", len(unified_samples))
print("unified_metadata.json created")