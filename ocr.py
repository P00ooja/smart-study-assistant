import pytesseract
from PIL import Image
import re
import os

def extract_text_from_image(image_path):
    try:
        if os.name != "nt":
            pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"

        img = Image.open(image_path)
        img = img.convert("L")

        text = pytesseract.image_to_string(img)

        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        return text.strip(), None

    except Exception as e:
        return None, str(e)