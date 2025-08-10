"""Material Class"""

from struct import unpack, pack
from PyM3G.util import obj2str
from PyM3G.data.color import Color
from PyM3G.objects.object3d import Object3D


class Material(Object3D):
    """
    An Appearance component encapsulating material attributes for lighting computations
    """

    def __init__(self):
        super().__init__()
        self.ambient_color = Color([0.2, 0.2, 0.2, 0.0])
        self.diffuse_color = Color([0.8, 0.8, 0.8, 1.0])
        self.emissive_color = Color([0.0, 0.0, 0.0, 0.0])
        self.specular_color = Color([0.0, 0.0, 0.0, 0.0])
        self.shininess = 0.0
        self.vertex_color_tracking_enabled = False

    def __str__(self):
        return obj2str(
            "Material",
            [
                ("Ambient Color", self.ambient_color),
                ("Diffuse Color", self.diffuse_color),
                ("Emissive Color", self.emissive_color),
                ("Specular Color", self.specular_color),
                ("Shininess", self.shininess),
                ("Vertex Color Tracking Enabled", self.vertex_color_tracking_enabled),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.ambient_color = Color(unpack("<3B", reader.read(3)))
        self.diffuse_color = Color(unpack("<4B", reader.read(4)))
        self.emissive_color = Color(unpack("<3B", reader.read(3)))
        self.specular_color = Color(unpack("<3B", reader.read(3)))
        (self.shininess, self.vertex_color_tracking_enabled) = unpack(
            "<f?", reader.read(5)
        )

    def write(self, writer):
        super().write(writer)
        writer.write(pack("<3B", *self.ambient_color.to_list(3)))
        writer.write(pack("<4B", *self.diffuse_color.to_list(4)))
        writer.write(pack("<3B", *self.emissive_color.to_list(3)))
        writer.write(pack("<3B", *self.specular_color.to_list(3)))
        writer.write(pack("<f?", self.shininess, self.vertex_color_tracking_enabled))