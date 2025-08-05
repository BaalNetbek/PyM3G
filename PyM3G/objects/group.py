"""Group Class"""

from struct import unpack, pack
from PyM3G.util import obj2str
from PyM3G.objects.node import Node


class Group(Node):
    """
    A scene graph node that stores an unordered set of nodes as its children
    """

    def __init__(self):
        super().__init__()
        self.children = []

    def __str__(self):
        return obj2str("Group", [("Children", self.children)]) + super().inherited_str()
    
    def inherited_str(self):
        if self.children != []:
            return "From: " + Group.__str__(self)
        return "From: Group:\n\tdefault values"

    def read(self, reader):
        super().read(reader)
        count = unpack("<I", reader.read(4))[0]
        for _ in range(count):
            self.children.append(unpack("<I", reader.read(4))[0])

    def write(self, writer):
        super().write(writer)
        writer.write(pack("<I", len(self.children)))
        for child in self.children:
            writer.write(pack("<I", child))
