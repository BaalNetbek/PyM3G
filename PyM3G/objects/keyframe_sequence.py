"""Keyframe Sequence Class"""

from struct import unpack, pack
from pym3g.util import obj2str, const2str
from pym3g.objects.object3d import Object3D


class KeyframeSequence(Object3D):
    """
    Encapsulates animation data as a sequence of time-stamped, vector-valued keyframes
    """

    CONSTANT = 192
    LINEAR = 176
    LOOP = 193
    SLERP = 177
    SPLINE = 178
    SQUAD = 179
    STEP = 180

    HAS_REFS = False
    
    def __init__(self):
        super().__init__()
        self.interpolation: int  = None
        self.repeat_mode: int  = None
        self.encoding: int  = None
        self.duration: int  = None
        self.valid_range_first: int  = None
        self.valid_range_last: int  = None
        self.component_count: int  = None
        self.keyframe_count: int = None
        self.time: list[int] = []
        self.vector_value: list[list] = []
        self.vector_bias: list[float] = []
        self.vector_scale: list[float] = []

    def __str__(self):
        return obj2str(
            "KeyframeSequence",
            [
                ("Interpolation", const2str(self.interpolation) + " (%d)" % self.interpolation),
                ("Repeat Mode", const2str(self.repeat_mode) + " (%d)" % self.repeat_mode),
                ("Encoding", self.encoding),
                ("Duration", self.duration),
                ("Valid Range First", self.valid_range_first),
                ("Valid Range Last", self.valid_range_last),
                ("Component Count", self.component_count),
                ("Keyframe Count", self.keyframe_count),
                ("Time", "Array of %d items"%len(self.time)),
                ("Vector Value", "Array of %d items"%len(self.vector_value)),
                ("Vector Bias", "Array of %d items"%len(self.vector_bias)),
                ("Vector Scale", "Array of %d items"%len(self.vector_scale)),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        (
            self.interpolation,
            self.repeat_mode,
            self.encoding,
            self.duration,
            self.valid_range_first,
            self.valid_range_last,
            self.component_count,
            self.keyframe_count,
        ) = unpack("<3B5I", reader.read(23))
        if self.encoding == 0:
            for _ in range(self.keyframe_count):
                self.time.append(unpack("<I", reader.read(4))[0])
                self.vector_value.append(
                    unpack(
                        "<%df"%self.component_count,
                        reader.read(4 * self.component_count),
                    )
                )
        elif self.encoding == 1:
            self.vector_bias = unpack(
                "<%df"%self.component_count, reader.read(4 * self.component_count)
            )
            self.vector_scale = unpack(
                "<%df"%self.component_count, reader.read(4 * self.component_count)
            )
            for _ in range(self.keyframe_count):
                self.time.append(unpack("<I", reader.read(4))[0])
                self.vector_value.append(
                    unpack(
                        "<%dB"%self.component_count,
                        reader.read(self.component_count),
                    )
                )
        elif self.encoding == 2:
            self.vector_bias = unpack(
                "<%df"%self.component_count, reader.read(4 * self.component_count)
            )
            self.vector_scale = unpack(
                "<%df"%self.component_count, reader.read(4 * self.component_count)
            )
            for _ in range(self.keyframe_count):
                self.time.append(unpack("<I",reader.read(4))[0])
                self.vector_value.append(
                    unpack(
                        "<%dH"%self.component_count,
                        reader.read(2 * self.component_count),
                    )
                )

    def update_ref(self, objects):
        super().update_ref(objects)

    def write(self, writer):
        super().write(writer)
        writer.write(pack("<3B5I",
            self.interpolation,
            self.repeat_mode,
            self.encoding,
            self.duration,
            self.valid_range_first,
            self.valid_range_last,
            self.component_count,
            self.keyframe_count,
        ))
        if self.encoding == 0:
            for i in range(self.keyframe_count):
                writer.write(pack("<I", self.time[i]))
                writer.write(
                    pack(
                        "<%df"%self.component_count,
                        *self.vector_value[i],
                    )
                )
        elif self.encoding == 1:
            writer.write(pack("<%df"%self.component_count, *self.vector_bias))
            writer.write(pack("<%df"%self.component_count, *self.vector_scale))

            for i in range(self.keyframe_count):
                writer.write(pack("<I", self.time[i]))
                writer.write(
                    pack(
                        "<%dB"%self.component_count,
                        *self.vector_value[i]
                    )
                )
        elif self.encoding == 2:
            writer.write(pack("<%df"%self.component_count, *self.vector_bias))
            writer.write(pack("<%df"%self.component_count, *self.vector_scale))

            for i in range(self.keyframe_count):
                writer.write(pack("<I", self.time[i]))
                writer.write(
                    pack(
                        "<%dH"%self.component_count,
                        *self.vector_value[i]
                    )
                )