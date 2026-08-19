import argparse
import json
import os

from PIL import Image


def main():
    parser = argparse.ArgumentParser(
        description="Validate Arabic Documents OCR Dataset"
    )
    parser.add_argument(
        "--dataset-root",
        required=True,
        help="Path to the Arabic Documents OCR Dataset/Documents/Documents directory",
    )
    args = parser.parse_args()

    dataset_path = args.dataset_root

    bad_json = []
    valid_json = 0

    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith(".json"):
                json_path = os.path.join(root, file)

                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        json.load(f)

                    valid_json += 1

                except (OSError, json.JSONDecodeError):
                    bad_json.append(json_path)

    bad_images = []
    valid_images = 0

    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                img_path = os.path.join(root, file)

                try:
                    img = Image.open(img_path)
                    img.verify()

                    valid_images += 1

                except (OSError, SyntaxError):
                    bad_images.append(img_path)

    print("Arabic Documents OCR Dataset")
    print("=============================")
    print("Valid JSON:", valid_json)
    print("Bad JSON:", len(bad_json))
    print("Valid images:", valid_images)
    print("Bad images:", len(bad_images))


if __name__ == "__main__":
    main()
