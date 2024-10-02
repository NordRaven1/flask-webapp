from typing import Union

from PIL import Image


class CoverImage:
    def __init__(self, image: Image):
        self.image = image

    def _to_rgb(self):
        return self.image.getdata()

    def __eq__(self, other):
        return isinstance(other, type(self)) and self._to_rgb() == other._to_rgb()

    @staticmethod
    def create(image: Image) -> Union['CoverImage', None]:
        if image is None:
            return None
        return CoverImage(image)
