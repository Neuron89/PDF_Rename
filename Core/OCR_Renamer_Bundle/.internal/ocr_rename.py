import os
import re
import pytesseract
from pdf2image import convert_from_path

# CONFIG
pdf_folder = r"PDFs"  # Place your PDFs here
poppler_path = r"poppler/bin"  # Poppler bin path inside the zip
tesseract_path = r"tesseract/tesseract.exe"  # Tesseract inside the zip
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Regex patterns
doc_regex = r"DOCUMENT NO:\s*([A-Z]+[0-9]+)"
item_regex = r"FG ITEM\s*#\s*([A-Z0-9_-]+)"


# Process PDFs
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        full_path = os.path.join(pdf_folder, filename)

        try:
            images = convert_from_path(full_path, poppler_path=poppler_path)
            text = pytesseract.image_to_string(images[0])

            doc_match = re.search(doc_regex, text, re.IGNORECASE)
            item_match = re.search(item_regex, text, re.IGNORECASE)

            if doc_match and item_match:
                doc_num = doc_match.group(1).upper()
                item_num = item_match.group(1)

                new_filename = f"{doc_num}_{item_num}.pdf"
                new_path = os.path.join(pdf_folder, new_filename)

                os.rename(full_path, new_path)
                print(f"Renamed: {filename} → {new_filename}")
            else:
                print(f"[!] Could not extract both fields from: {filename}")

        except Exception as e:
            print(f"[!] Error processing {filename}: {e}")
