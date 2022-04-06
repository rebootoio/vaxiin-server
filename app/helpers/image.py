import base64
import pytesseract
from PIL import Image


def encode_image(image):
    return base64.b64encode(image).decode('ascii')


def decode_image(image):
    return base64.b64decode(image.encode('ascii'))


def get_ocr_text(image):
    return pytesseract.image_to_string(Image.open(image))
