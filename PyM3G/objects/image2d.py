"""Image2D Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, const2str
from PyM3G.objects.object3d import Object3D


class Image2D(Object3D):
    """
    A two-dimensional image that can be used as a texture, background or sprite image
    """
    
    ALPHA = 96
    LUMINANCE = 97
    LUMINANCE_ALPHA = 98
    RGB = 99
    RGBA = 100

    HAS_REFS = False

    def __init__(self, format = LUMINANCE, mutable = False, w = 1, h = 1, palette = [], pixels = [127]):
        super().__init__()
        self.image_format = format
        self.is_mutable: bool = mutable
        self.width: int = w
        self.height: int = h
        self.palette: list[int] = palette
        self.pixels: list[int] = pixels

    def __str__(self):
        return obj2str(
            "Image2D",
            [
                ("Format", const2str(self.image_format) + " (%d)" % self.image_format),
                ("Is Mutable", self.is_mutable),
                ("Size", "{} x {}".format(self.width, self.height)),
                ("Palette", "Array of {} items".format(len(self.palette))),
                ("Pixels", "Array of {} items".format(len(self.pixels))),
            ],
        ) + super(Image2D, self).inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        (self.image_format, self.is_mutable, self.width, self.height) = unpack(
            "<B?II", reader.read(10)
        )
        if not self.is_mutable:
            pal = unpack("<I", reader.read(4))[0]
            for _ in range(pal):
                self.palette.append(unpack("<B", reader.read(1))[0])
            pxl = unpack("<I", reader.read(4))[0]
            for _ in range(pxl):
                self.pixels.append(unpack("<B", reader.read(1))[0])

    def update_ref(self, objects):
        super().update_ref(objects)

    def write(self, writer):
        super().write(writer)
        writer.write(pack("<B?II", self.image_format, self.is_mutable, self.width, self.height))
        if not self.is_mutable:
            writer.write(pack("<I", len(self.palette)))
            for color in self.palette:
                writer.write(pack("<B", color))
            writer.write(pack("<I", len(self.pixels)))
            for pixel in self.pixels:
                writer.write(pack("<B", pixel))