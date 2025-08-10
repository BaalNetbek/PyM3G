"""Texture2D Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, const2str, deref_from_file
from PyM3G.data.color import Color
from PyM3G.objects.transformable import Transformable
from PyM3G.objects.image2d import Image2D

class Texture2D(Transformable):
    """
    An Appearance component encapsulating a two-dimensional texture image and a set of
    attributes specifying how the image is to be applied on submeshes
    """

    FILTER_BASE_LEVEL = 208
    FILTER_LINEAR = 209
    FILTER_NEAREST = 210
    FUNC_ADD = 224
    FUNC_BLEND = 225
    FUNC_DECAL = 226
    FUNC_MODULATE = 227
    FUNC_REPLACE = 228
    WRAP_CLAMP = 240
    WRAP_REPEAT = 241

    def __init__(self):
        super().__init__()
        self.image_idx: int = None
        self.image: Image2D = None
        self.blend_color = Color([0.0, 0.0, 0.0])
        self.blending = Texture2D.FUNC_MODULATE
        self.wrapping_s = Texture2D.WRAP_REPEAT
        self.wrapping_t = Texture2D.WRAP_REPEAT
        self.level_filter = Texture2D.FILTER_BASE_LEVEL
        self.image_filter = Texture2D.FILTER_NEAREST

    def __str__(self):
        return obj2str(
            "Texture2D",
            [
                ("Image", self.image_idx),
                ("Blend Color", self.blend_color),
                ("Blending", const2str(self.blending) + " (%d)" % self.blending),
                ("Wrapping S", const2str(self.wrapping_s) + " (%d)" % self.wrapping_s),
                ("Wrapping T", const2str(self.wrapping_t) + " (%d)" % self.wrapping_t),
                ("Level Filter", const2str(self.level_filter) + " (%d)" % self.level_filter),
                ("Image Filter", const2str(self.image_filter) + " (%d)" % self.image_filter),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.image_idx = unpack("<I", reader.read(4))[0]
        self.blend_color = Color(unpack("<3B", reader.read(3)))
        (
            self.blending,
            self.wrapping_s,
            self.wrapping_t,
            self.level_filter,
            self.image_filter,
        ) = unpack("<5B", reader.read(5))
        
        deref_from_file(self, "image", Image2D, self.image_idx, objects)
    
    def write(self, writer):
        super().write(writer)
        writer.write(pack("<I", self.image_idx))
        writer.write(pack("<3B", *self.blend_color.to_list(3)))
        writer.write(pack(
            "<5B",
            self.blending,
            self.wrapping_s,
            self.wrapping_t,
            self.level_filter,
            self.image_filter
        ))