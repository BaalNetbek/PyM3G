"""Polygon Mode Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, const2str
from PyM3G.objects.object3d import Object3D


class PolygonMode(Object3D):
    """
    An Appearance component encapsulating polygon-level attributes
    """

    def __init__(self):
        super().__init__()
        self.culling = 160
        self.shading = 165
        self.winding = 168
        self.two_sided_lighting_enabled = False
        self.local_camera_lighting_enabled = False
        self.perspective_correction_enabled = False

    def __str__(self):
        return obj2str(
            "PolygonMode",
            [
                ("Culling", const2str(self.culling) + " (%d)" % self.culling),
                ("Shading", const2str(self.shading) + " (%d)" % self.shading),
                ("Winding", const2str(self.winding) + " (%d)" % self.winding),
                ("Two Sided Lighting Enabled", self.two_sided_lighting_enabled),
                ("Local Camera Lighting Enabled", self.local_camera_lighting_enabled),
                ("Perspective Correction Enabled", self.perspective_correction_enabled),
            ],
        ) + super().inherited_str()

    def read(self, reader):
        super().read(reader)
        (
            self.culling,
            self.shading,
            self.winding,
            self.two_sided_lighting_enabled,
            self.local_camera_lighting_enabled,
            self.perspective_correction_enabled,
        ) = unpack("<3B3?", reader.read(6))

    def write(self, writer):
        super().write(writer)
        writer.write(
            pack(
                "<3B3?",
                self.culling,
                self.shading,
                self.winding,
                self.two_sided_lighting_enabled,
                self.local_camera_lighting_enabled,
                self.perspective_correction_enabled,
            )
        )