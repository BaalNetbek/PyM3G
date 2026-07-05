"""Camera Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, const2str
from PyM3G.objects.node import Node
from PyM3G.data.matrix import Matrix


class Camera(Node):
    """
    A scene graph node that defines the position of the viewer in the scene and the
    projection from 3D to 2D
    """
    GENERIC = 48
    PARALLEL = 49
    PERSPECTIVE = 50

    HAS_REFS = False

    def __init__(self):
        super().__init__()
        self.projection_type = Camera.GENERIC
        self.projection_matrix = Matrix.identity()
        self.fovy: float = None
        self.aspect_ratio: float = None
        self.near: float = None
        self.far: float = None

    def __str__(self):
        return obj2str(
            "Camera",
            [
                ("Projection Type", const2str(self.projection_type) + " (%d)" % self.projection_type),
                ("Projection Matrix", self.projection_matrix),
                ("Fov Y", self.fovy),
                ("Aspect Ratio", self.aspect_ratio),
                ("Near", self.near),
                ("Far", self.far),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.projection_type = unpack("<B", reader.read(1))[0]
        if self.projection_type == Camera.GENERIC:
            self.projection_matrix = Matrix(unpack("<16f", reader.read(64)))
        else:
            (self.fovy, self.aspect_ratio, self.near, self.far) = unpack(
                "<4f", reader.read(16)
            )

    def update_ref(self, objects):
        super().update_ref(objects) 

    def write(self, writer):
        super().write(writer)
        writer.write(pack("B", self.projection_type))
        if self.projection_type == Camera.GENERIC:
            writer.write(pack(
                "<16f", 
                *self.projection_matrix.elements))
        else:
            writer.write(pack(
                "<4f", 
                self.fovy, 
                self.aspect_ratio,
                self.near,
                self.far))