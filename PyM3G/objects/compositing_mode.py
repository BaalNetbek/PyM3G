"""Compositing Mode Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, const2str
from PyM3G.objects.object3d import Object3D


class CompositingMode(Object3D):
    """
    An Appearance component encapsulating per-pixel compositing attributes
    """
    ALPHA = 64
    ALPHA_ADD = 65
    MODULATE = 66
    MODULATE_X2 = 67
    REPLACE = 68

    HAS_REFS = False

    def __init__(self):
        super().__init__()
        self.depth_test_enabled: bool = True
        self.depth_write_enabled: bool = True
        self.color_write_enabled: bool = True
        self.alpha_write_enabled: bool = True
        self.blending: int = CompositingMode.REPLACE
        self.alpha_threshold: float = 0.0
        self.depth_offset_factor: float = 0.0
        self.depth_offset_units: float = 0.0

    def __str__(self):
        return obj2str(
            "CompositingMode",
            [
                ("Depth Test Enabled", self.depth_test_enabled),
                ("Depth Write Enabled", self.depth_write_enabled),
                ("Color Write Enabled", self.color_write_enabled),
                ("Alpha Write Enabled", self.alpha_write_enabled),
                ("Blending", const2str(self.blending) + " (%d)" % self.blending),
                ("Alpha Threshold", self.alpha_threshold),
                ("Depth Offset Factor", self.depth_offset_factor),
                ("Depth Offset Units", self.depth_offset_units),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        (
            self.depth_test_enabled,
            self.depth_write_enabled,
            self.color_write_enabled,
            self.alpha_write_enabled,
            self.blending,
            self.alpha_threshold,
            self.depth_offset_factor,
            self.depth_offset_units,
        ) = unpack("<4?BBff", reader.read(14))

    def update_ref(self, objects):
        super().update_ref(objects)    

    def write(self, writer):
        super().write(writer)
        writer.write(
            pack(
                "<4?BBff",
                self.depth_test_enabled,
                self.depth_write_enabled,
                self.color_write_enabled,
                self.alpha_write_enabled,
                self.blending,
                self.alpha_threshold,
                self.depth_offset_factor,
                self.depth_offset_units,
            )
        )
