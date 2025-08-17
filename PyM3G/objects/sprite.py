"""Sprite Class"""

from struct import unpack
from PyM3G.util import obj2str, deref_from_file
from PyM3G.objects.node import Node
from PyM3G.objects.image2d import Image2D
from PyM3G.objects.appearance import Appearance

class Sprite(Node):
    """
    A scene graph node that represents a 2-dimensional image with a 3D position
    """

    def __init__(self):
        super().__init__()
        self.image_idx = None
        self.image: Image2D = None
        self.appearance_idx = None
        self.appearance: Appearance = None
        self.is_scaled = None
        self.crop_x = None
        self.crop_y = None
        self.crop_width = None
        self.crop_height = None

    def __str__(self):
        return obj2str(
            "Sprite",
            [
                ("Image", self.image_idx),
                ("Appearance", self.appearance_idx),
                ("Is Scaled", self.is_scaled),
                ("Crop X", self.crop_x),
                ("Crop Y", self.crop_y),
                ("Crop Width", self.crop_width),
                ("Crop Height", self.crop_height),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        (
            self.image_idx,
            self.appearance_idx,
            self.is_scaled,
            self.crop_x,
            self.crop_y,
            self.crop_width,
            self.crop_height,
        ) = unpack("<II?4i", reader.read(25))
        
        deref_from_file(self, "image", Image2D, self.image_idx, objects)
        deref_from_file(self, "appearance", Appearance, self.appearance_idx, objects)
    # TODO write, upadate_ref
    