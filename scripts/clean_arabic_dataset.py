import os
import json
from PIL import Image


DATASET_PATH = (
    "/kaggle/input/datasets/"
    "humansintheloop/arabic-documents-ocr-dataset/"
    "Documents/Documents"
)


# ==============================
# JSON validation
# ==============================

bad_json = []
valid_json = 0

for root, dirs, files in os.walk(DATASET_PATH):

    for file in files:

        if file.endswith(".json"):

            json_path = os.path.join(root, file)

            try:
                with open(
                    json_path,
                    "r",
                    encoding="utf-8"
                ) as f:
                    json.load(f)

                valid_json += 1

            except Exception:
                bad_json.append(json_path)


# ==============================
# Image validation
# ==============================

bad_images = []
valid_images = 0

for root, dirs, files in os.walk(DATASET_PATH):

    for file in files:

        if file.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):

            img_path = os.path.join(root, file)

            try:
                img = Image.open(img_path)
                img.verify()

                valid_images += 1

            except Exception:
                bad_images.append(img_path)


# ==============================
# Report
# ==============================

print("Arabic Documents OCR Dataset")
print("=============================")

print("Valid JSON:", valid_json)
print("Bad JSON:", len(bad_json))

print("Valid images:", valid_images)
print("Bad images:", len(bad_images))