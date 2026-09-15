from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def png(name="image.png"):
    """A tiny valid PNG upload for image-field tests."""
    buf = BytesIO()
    Image.new("RGB", (4, 4), "white").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")
