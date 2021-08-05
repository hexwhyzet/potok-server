from io import BytesIO

import cv2
import numpy as np
import pytesseract
from PIL import Image

from .config import Config

config = Config()

pytesseract.pytesseract.tesseract_cmd = config['tesseract_path']

QUALITY = 75


def resize_and_compress(picture_bytes, extension, max_side_size):
    extension = 'JPEG' if extension.lower() == 'jpg' else extension.upper()
    pil_picture = Image.open(BytesIO(picture_bytes))
    new_picture_bytes = BytesIO()
    picture_was_resized = pil_picture.size[0] > max_side_size or pil_picture.size[1] > max_side_size
    pil_picture.thumbnail((max_side_size, max_side_size), Image.LANCZOS)
    pil_picture.save(new_picture_bytes,
                     format=extension,
                     quality=QUALITY,
                     optimize=True)
    new_picture_bytes.seek(0)
    return new_picture_bytes, pil_picture.size[0], pil_picture.size[1], picture_was_resized


def recognize_text(picture_bytes):
    cv_picture = cv2.imdecode(np.asarray(bytearray(picture_bytes), np.uint8), cv2.IMREAD_COLOR)
    result = pytesseract.image_to_string(cv_picture).strip()
    ban_list = {
        "|": "I",
    }
    for forbidden_pattern, replacement_pattern in ban_list.items():
        result.replace(forbidden_pattern, replacement_pattern)
    return result
