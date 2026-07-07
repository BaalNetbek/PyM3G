"""Sprite Class"""

from struct import unpack, pack
from pym3g.util import obj2str, deref_from_file, verify_ref
from pym3g.objects.node import Node
from pym3g.objects.image2d import Image2D
from pym3g.objects.appearance import Appearance

class Sprite(Node):
    """
    A scene graph node that represents a 2-dimensional image with a 3D position
    """

    HAS_REFS = True

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

    def update_ref(self, objects):
        super().update_ref(objects) 
        self.appearance_idx = 0
        self.image_idx = 0
        child_idx = []
        this_idx = 0
        for i, o in enumerate(objects):
            if o == self:
                this_idx = i+1
            if o == self.appearance:
                self.appearance_idx = i+1
                child_idx.append(i+1)
            if o == self.image:
                self.image_idx = i+1
                child_idx.append(i+1)

        verify_ref(self, this_idx, child_idx)

    def write(self, writer):
        super().write(writer)
        writer.write(
            pack("<II?iiii", 
                self.image_idx, 
                self.appearance_idx,
                self.is_scaled,
                self.crop_x,
                self.crop_y,
                self.crop_width,
                self.crop_height
            )
        )

    