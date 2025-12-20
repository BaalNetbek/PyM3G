"""Background Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, const2str, deref_from_file, verify_ref
from PyM3G.objects.object3d import Object3D
from PyM3G.objects.image2d import Image2D
from PyM3G.data.color import Color


class Background(Object3D):
    """
    Defines whether and how to clear the viewport
    """

    HAS_REFS = True

    def __init__(self):
        super().__init__()
        self.background_color = Color([0, 0, 0, 0])
        self.background_image_idx = None
        self.background_image: Image2D = None
        self.background_image_mode_x = 32
        self.background_image_mode_y = 32
        self.crop_x = None
        self.crop_y = None
        self.crop_width = None
        self.crop_height = None
        self.depth_clear_enabled = True
        self.color_clear_enabled = True

    def __str__(self):
        return obj2str(
            "Background",
            [
                ("Color", self.background_color),
                ("Image", self.background_image_idx),
                ("Image Mode X", const2str(self.background_image_mode_x) + " (%d)" % self.background_image_mode_x),
                ("Image Mode Y", const2str(self.background_image_mode_y) + " (%d)" % self.background_image_mode_y),
                ("Crop X", self.crop_x),
                ("Crop Y", self.crop_y),
                ("Crop Width", self.crop_width),
                ("Crop Height", self.crop_height),
                ("Depth Clear Enabled", self.depth_clear_enabled),
                ("Color Clear Enabled", self.color_clear_enabled),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.background_color = Color(unpack("<4B", reader.read(4)))
        (
            self.background_image_idx,
            self.background_image_mode_x,
            self.background_image_mode_y,
            self.crop_x,
            self.crop_y,
            self.crop_width,
            self.crop_height,
            self.depth_clear_enabled,
            self.color_clear_enabled,
        ) = unpack("<IBB4I??", reader.read(24))

        deref_from_file(self, "background_image", Image2D, self.background_image_idx, objects)

    def update_ref(self, objects):
        super().update_ref(objects)
        self.background_image_idx = 0
        child_idx = []
        this_idx = 0
        for i, o in enumerate(objects):
            if o == self:
                this_idx = i+1
            if o == self.background_image:
                self.background_image_idx = i+1
                child_idx.append(i+1)   
        verify_ref(self, this_idx, child_idx)

    def write(self, writer):
        super().write(writer)
        writer.write(pack("<4B", *self.background_color.to_list(4)))
        writer.write(
            pack(
                "<IBB4I??",
                self.background_image_idx,
                self.background_image_mode_x,
                self.background_image_mode_y,
                self.crop_x,
                self.crop_y,
                self.crop_width,
                self.crop_height,
                self.depth_clear_enabled,
                self.color_clear_enabled,
            )
        )
