import base64
import io
from typing import Union

from werkzeug.datastructures import FileStorage
from PIL import Image as PILImage

from webapp.images.CoverImage import CoverImage


def image_to_bytes(image: PILImage) -> Union[bytes, None]:
    if image:
        byte_stream = io.BytesIO()
        image.save(byte_stream, "PNG")
        return byte_stream.getvalue()
    return None


def image_from_bytes(image_bytes: Union[bytes, None]) -> Union[PILImage.Image, None]:
    if image_bytes is None:
        return None
    return PILImage.open(io.BytesIO(image_bytes))


def load_image(image_form_data: FileStorage) -> Union[PILImage.Image, None]:
    if image_form_data:
        image_bytes = image_form_data.read()
        return PILImage.open(io.BytesIO(image_bytes))
    return None


def dump_image(image: CoverImage) -> Union[str, None]:
    if image:
        buffer = io.BytesIO()
        image.image.save(buffer, "PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    return None
