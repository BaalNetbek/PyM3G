"""Fog Class"""

from struct import unpack
from PyM3G.util import obj2str, const2str
from PyM3G.objects.object3d import Object3D
from PyM3G.data.color import Color


class Fog(Object3D):
    """
    An Appearance component encapsulating attributes for fogging
    """
    
    EXPONENTIAL = 80
    LINEAR = 81

    def __init__(self):
        super().__init__()
        self.color = Color([0,0,0])
        self.mode = Fog.LINEAR
        self.density: float = 1.0
        self.near: float = 0.0
        self.far: float = 1.0

    def __str__(self):
        return obj2str(
            "Fog",
            [
                ("Color", self.color),
                ("Mode", const2str(self.mode) + " (%d)" % self.mode),
                ("Density", self.density),
                ("Near", self.near),
                ("Far", self.far),
            ],
        ) + super().inherited_str()
    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.color = Color(unpack("<3B", reader.read(3)))
        self.mode = unpack("<B", reader.read(1))[0]
        if self.mode == 80:
            self.density = unpack("<f", reader.read(4))[0]
        elif self.mode == 81:
            (self.near, self.far) = unpack("<2f", reader.read(8))

    # TODO write

    def update_ref(self, objects):
        super().update_ref(objects) 

    def write(self, writer):
        raise(Exception("%s.write() not implemented" % type(self).__name__))
        super().write(writer)