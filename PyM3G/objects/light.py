"""Light Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, const2str
from PyM3G.data.color import Color
from PyM3G.objects.node import Node


class Light(Node):
    """
    A scene graph node that represents different kinds of light sources
    """
    AMBIENT = 128
    DIRECTIONAL = 129
    OMNI = 130
    SPOT = 131

    HAS_REFS = False

    def __init__(self):
        super().__init__()
        self.attenuation_constant = 1.0
        self.attenuation_linear = 1.0
        self.attenuation_quadratic = 1.0
        self.color = Color([0, 0, 0, 0])
        self.mode = Light.DIRECTIONAL
        self.intensity = 1.0
        self.spot_angle = 45
        self.spot_exponent = 0.0

    def __str__(self):
        return obj2str(
            "Light",
            [
                ("Attenuation Constant", self.attenuation_constant),
                ("Attenuation Linear", self.attenuation_linear),
                ("Attenuation Quadratic", self.attenuation_quadratic),
                ("Color", self.color),
                ("Mode", const2str(self.mode) + " (%d)" % self.mode),
                ("Intensity", self.intensity),
                ("Spot Angle", self.spot_angle),
                ("Spot Exponent", self.spot_exponent),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        (
            self.attenuation_constant,
            self.attenuation_linear,
            self.attenuation_quadratic,
        ) = unpack("<3f", reader.read(12))
        self.color = Color(unpack("<3f", reader.read(12)))
        (self.intensity, self.spot_angle, self.spot_exponent) = unpack(
            "<3f", reader.read(12)
        )

    #TODO upadate_ref

    def write(self, writer):
        super().write(writer)
        writer.write(pack(
            "<3f",
            self.attenuation_constant,
            self.attenuation_linear,
            self.attenuation_quadratic,
        ))
        writer.write(pack("<3f", *self.color.to_list(3)))
        writer.write(pack(
            "<3f",
            self.intensity,
            self.spot_angle,
            self.spot_exponent
        ))

