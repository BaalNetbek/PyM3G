"""Group Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, deref_from_file
from PyM3G.objects.node import Node


class Group(Node):
    """
    A scene graph node that stores an unordered set of nodes as its children
    """

    def __init__(self):
        super().__init__()
        self.children_idx: list[int] = []
        self.children: list[Node] = []

    def __str__(self):
        return obj2str("Group", [("Children", self.children_idx)]) + super().inherited_str()
    
    def inherited_str(self):
        if self.children_idx != []:
            return "From: " + Group.__str__(self)
        return "From: Group:\n\tdefault values"

    def read(self, reader, objects=None):
        super().read(reader, objects)
        count = unpack("<I", reader.read(4))[0]
        for _ in range(count):
            self.children_idx.append(unpack("<I", reader.read(4))[0])
        
        deref_from_file(self, "children", Node, self.children_idx, objects)
        
    def write(self, writer):
        super().write(writer)
        writer.write(pack("<I", len(self.children_idx)))
        for child in self.children_idx:
            writer.write(pack("<I", child))
