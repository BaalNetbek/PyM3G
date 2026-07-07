"""Triangle Strip Array Class"""

from struct import unpack, pack
from pym3g.util import obj2str
from pym3g.objects.object3d import Object3D


class TriangleStripArray(Object3D):
    """
    TriangleStripArray defines an array of triangle strips
    """
    
    HAS_REFS = False

    def __init__(self):
        super().__init__()
        self.encoding: int = None
        self.start_index: int = None
        self.indices: list[int] = []
        self.strip_lengths: list[int] = []

    def __str__(self):
        return obj2str(
            "TriangleStripArray",
            [
                ("Encoding", self.encoding),
                ("Start Index", self.start_index),
                ("Indices", "Array of {0} items".format(len(self.indices))),
                ("Strip Lengths", "Array of {0} items".format(len(self.strip_lengths))),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.start_index = 0
        self.encoding = unpack("<B", reader.read(1))[0]
        if self.encoding == 0:
            self.start_index = unpack("<I", reader.read(4))[0]
        elif self.encoding == 1:
            self.start_index = unpack("<B", reader.read(1))[0]
        elif self.encoding == 2:
            self.start_index = unpack("<H", reader.read(2))[0]
        elif self.encoding == 128:
            icount = unpack("<I", reader.read(4))[0]
            for _ in range(icount):
                self.indices.append(unpack("<I", reader.read(4))[0])
        elif self.encoding == 129:
            icount = unpack("<I", reader.read(4))[0]
            for _ in range(icount):
                self.indices.append(unpack("<B", reader.read(1))[0])
        elif self.encoding == 130:
            icount = unpack("<I", reader.read(4))[0]
            for _ in range(icount):
                self.indices.append(unpack("<H", reader.read(2))[0])
        scount = unpack("<I", reader.read(4))[0]
        for _ in range(scount):
            self.strip_lengths.append(unpack("<I", reader.read(4))[0])

    def update_ref(self, objects):
        super().update_ref(objects)

    def write(self, writer):
        super().write(writer)
        writer.write(pack("<B", self.encoding))
        if self.encoding == 0:
            writer.write(pack("<I", self.start_index))
        elif self.encoding == 1:
            writer.write(pack("<B", self.start_index))
        elif self.encoding == 2:
            writer.write(pack("<H", self.start_index))
        elif self.encoding == 128:
            writer.write(pack("<I", len(self.indices)))
            for index in self.indices:
                writer.write(pack("<I", index))
        elif self.encoding == 129:
            writer.write(pack("<I", len(self.indices)))
            for index in self.indices:
                writer.write(pack("<B", index))
        elif self.encoding == 130:
            writer.write(pack("<I", len(self.indices)))
            for index in self.indices:
                writer.write(pack("<H", index))
        writer.write(pack("<I", len(self.strip_lengths)))
        for length in self.strip_lengths:
            writer.write(pack("<I", length))