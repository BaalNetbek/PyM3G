"""Morphing Mesh Class"""

from struct import unpack
from PyM3G.util import obj2str, deref_from_file
from PyM3G.objects.mesh import Mesh
from PyM3G.objects.vertex_buffer import VertexBuffer


class MorphingMesh(Mesh):
    """
    A scene graph node that represents a vertex morphing polygon mesh
    """

    def __init__(self):
        super().__init__()
        self.morph_target_count: int = None
        self.morph_target_idx: list[int] = []
        self.morph_target: list[VertexBuffer] = []
        self.initial_weight: list[int] = []

    def __str__(self):
        return obj2str(
            "MorphingMesh",
            [
                ("Morph Target Count", self.morph_target_count),
                ("Morph Target", "Array of {0} items".format(len(self.morph_target_idx))),
                ("Initial Weight", "Array of {0} items".format(len(self.initial_weight))),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.morph_target_count = unpack("<I", reader.read(4))
        for _ in range(self.morph_target_count):
            morph_target, initial_weight = unpack("<If", 8)
            self.morph_target_idx.append(morph_target)
            self.initial_weight.append(initial_weight)
        
        deref_from_file(self, "morph_target", VertexBuffer, self.morph_target_idx, objects)

    # TODO write