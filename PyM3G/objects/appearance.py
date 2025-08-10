"""Appearance Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, deref_from_file
from PyM3G.objects.object3d import Object3D
from PyM3G.objects.compositing_mode import CompositingMode
from PyM3G.objects.fog import Fog
from PyM3G.objects.polygon_mode import PolygonMode
from PyM3G.objects.material import Material
from PyM3G.objects.texture2d import Texture2D


class Appearance(Object3D):
    """
    A set of component objects that define the rendering attributes of a Mesh or
    Sprite3D
    """

    def __init__(self):
        super().__init__()
        self.layer = 0
        self.compositing_mode_idx = None
        self.compositing_mode: PolygonMode = None
        self.fog = None
        self.polygon_mode_idx = None
        self.polygon_mode: PolygonMode = None
        self.material_idx = None
        self.material: Material = None
        self.textures_idx = []
        self.textures: list[Texture2D] = []

    def __str__(self):
        return obj2str(
            "Appearance",
            [
                ("Layer", self.layer),
                ("Compositing Mode", self.compositing_mode_idx),
                ("Fog", self.fog),
                ("Polygon Mode", self.polygon_mode_idx),
                ("Material", self.material_idx),
                ("Textures", self.textures_idx),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.textures_idx = []
        (
            self.layer,
            self.compositing_mode_idx,
            self.fog,
            self.polygon_mode_idx,
            self.material_idx,
            texcount,
        ) = unpack("<B5I", reader.read(21))
        for _ in range(texcount):
            self.textures_idx.append(unpack("<I", reader.read(4))[0])
        
        deref_from_file(self, "compositing_mode", CompositingMode, self.compositing_mode_idx, objects)
        deref_from_file(self, "polygon_mode", PolygonMode, self.polygon_mode_idx, objects)
        deref_from_file(self, "material", Material, self.material_idx, objects)
        deref_from_file(self, "textures", Texture2D, self.textures_idx, objects)
        

    def write(self, writer):
        super().write(writer)
        writer.write(
            pack(
                "<B5I",
                self.layer,
                self.compositing_mode_idx,
                self.fog,
                self.polygon_mode_idx,
                self.material_idx,
                len(self.textures_idx),
            )
        )
        for tex in self.textures_idx:
            writer.write(pack("<I", tex))