"""Animation Controller Class"""

from struct import unpack, pack
from PyM3G.util import obj2str
from PyM3G.objects.object3d import Object3D


class AnimationController(Object3D):
    """
    Controls the position, speed and weight of an animation sequence
    """

    def __init__(self):
        super().__init__()
        self.speed = 1.0
        self.weight = 1.0
        self.active_interval_start = 0
        self.active_interval_end = 0
        self.reference_sequence_time = 0
        self.reference_world_time = 0

    def __str__(self):
        return obj2str(
            "AnimationController",
            [
                ("Speed", self.speed),
                ("Weight", self.weight),
                ("Active Interval Start", self.active_interval_start),
                ("Active Interval End", self.active_interval_end),
                ("Reference Sequence Time", self.reference_sequence_time),
                ("Reference World Time", self.reference_world_time),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        (
            self.speed,
            self.weight,
            self.active_interval_start,
            self.active_interval_end,
            self.reference_sequence_time,
            self.reference_world_time,
        ) = unpack("<ffIIfI", reader.read(24))
        
    #TODO upadate_ref

    def write(self, writer):
        super().write(writer)
        writer.write(
            pack(
                "<ffIIfI",
                self.speed,
                self.weight,
                self.active_interval_start,
                self.active_interval_end,
                self.reference_sequence_time,
                self.reference_world_time,
            )
        )