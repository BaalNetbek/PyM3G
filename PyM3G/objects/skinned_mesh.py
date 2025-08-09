"""Skinned Mesh Class"""

from struct import unpack
from PyM3G.util import obj2str
from PyM3G.objects.mesh import Mesh


class SkinnedMesh(Mesh):
    """
    A scene graph node that represents a skeletally animated polygon mesh
    """

    def __init__(self):
        super().__init__()
        self.skeleton = None
        self.transform_reference_count = None
        self.transform_node = []
        self.first_vertex = []
        self.vertex_count = []
        self.weight = []

    def __str__(self):
        return obj2str(
            "SkinnedMesh",
            [
            ("Skeleton", self.skeleton),
            ("Transform Reference Count", self.transform_reference_count),
            ("Transform Node", "Array of {0} items".format(len(self.transform_node))),
            ("First Vertex", "Array of {0} items".format(len(self.first_vertex))),
            ("Vertex Count", "Array of {0} items".format(len(self.vertex_count))),
            ("Weight", "Array of {0} items".format(len(self.weight))),
            ],
        ) + super(SkinnedMesh, self).inherited_str()

    def read(self, reader):
        super().read(reader)
        self.skeleton, self.transform_reference_count = unpack("<II", reader.read(8))
        for _ in range(self.transform_reference_count):
            (transform_node, first_vertex, vertex_count, weight) = unpack(
                "<3Ii", reader.read(16)
            )
            self.transform_node.append(transform_node)
            self.first_vertex.append(first_vertex)
            self.vertex_count.append(vertex_count)
            self.weight.append(weight)
