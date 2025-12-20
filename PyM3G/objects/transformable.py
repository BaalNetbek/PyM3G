"""Transformable Class"""

from struct import unpack, pack
from PyM3G.objects.object3d import Object3D
from PyM3G.util import obj2str
from PyM3G.data.matrix import Matrix


class Transformable(Object3D):
    """
    An abstract base class for Node and Texture2D, defining common methods
    for manipulating node and texture transformations
    """

    HAS_REFS = False

    def __init__(self):
        super().__init__()
        self.has_component_transform = None
        self.translation = (0, 0, 0)
        self.scale = (1, 1, 1)
        self.orientation_angle = 0
        self.orientation_axis = (0,0,1)
        self.has_general_transform = None
        self.matrix = Matrix.identity()

    def __str__(self):
        return obj2str(
            "Transformable",
            [
                #("Has Component Transform", self.has_component_transform),
                ("Translation", self.translation),
                ("Scale", self.scale),
                ("Orientation Angle", self.orientation_angle),
                ("Orientation Axis", self.orientation_axis),
                #("Has General Transform", self.has_general_transform),
                ("Transform", self.matrix),
            ],
        ) + super().inherited_str()
    
    def inherited_str(self):
        if (self.has_component_transform != None
            or self.translation != (0, 0, 0)
            or self.scale != (1, 1, 1)
            or self.orientation_angle != 0
            or self.orientation_axis != None
            or self.has_general_transform != None
            or self.matrix != Matrix.identity()
            ):
                return "From " + Transformable.__str__(self)
        return "From Transformable: default values"    
    
    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.has_component_transform = unpack("<?", reader.read(1))[0]
        if self.has_component_transform:
            self.translation = unpack("<3f", reader.read(12))
            self.scale = unpack("<3f", reader.read(12))
            self.orientation_angle = unpack("<f", reader.read(4))[0]
            self.orientation_axis = unpack("<3f", reader.read(12))
        self.has_general_transform = unpack("<?", reader.read(1))[0]
        if self.has_general_transform:
            self.matrix = Matrix(unpack("<16f", reader.read(64)))

    def update_ref(self, objects):
        super().update_ref(objects)

    def write(self, writer):
        super().write(writer)
        writer.write(pack("<?", self.has_component_transform))
        if (self.has_component_transform and self.translation is not None 
            and self.scale is not None and self.orientation_axis is not None):
            writer.write(pack("<3f", *self.translation))
            writer.write(pack("<3f", *self.scale))
            writer.write(pack("<f", self.orientation_angle))
            writer.write(pack("<3f", *self.orientation_axis))
        writer.write(pack("<?", self.has_general_transform))
        if self.has_general_transform and self.matrix:
            writer.write(pack("<16f", *self.matrix.elements))