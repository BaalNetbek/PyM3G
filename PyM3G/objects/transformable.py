"""Transformable Class"""

from struct import unpack
from PyM3G.objects.object3d import Object3D
from PyM3G.util import obj2str


class Transformable(Object3D):
    """
    An abstract base class for Node and Texture2D, defining common methods
    for manipulating node and texture transformations
    """

    def __init__(self):
        super().__init__()
        self.has_component_transform = None
        self.translation = (0, 0, 0)
        self.scale = (1, 1, 1)
        self.orientation_angle = 0
        self.orientation_axis = None
        self.has_general_transform = None
        self.matrix = (1.0, 0, 0, 0,
                       0, 1.0, 0, 0,
                       0, 0, 1.0, 0,
                       0, 0, 0, 1.0)

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
            or self.matrix != (1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0)
            ):
                return "From: " + Transformable.__str__(self)
        return "From: Transformable: default values"
    
        return ""
    def read(self, reader):
        super().read(reader)
        self.has_component_transform = unpack("<?", reader.read(1))[0]
        if self.has_component_transform:
            self.translation = unpack("<3f", reader.read(12))
            self.scale = unpack("<3f", reader.read(12))
            self.orientation_angle = unpack("<f", reader.read(4))[0]
            self.orientation_axis = unpack("<3f", reader.read(12))
        self.has_general_transform = unpack("<?", reader.read(1))[0]
        if self.has_general_transform:
            self.matrix = unpack("<16f", reader.read(64))
