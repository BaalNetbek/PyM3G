"""Mesh Class"""

from struct import unpack
from PyM3G.util import obj2str
from PyM3G.objects.node import Node
from PyM3G.objects.vertex_buffer import VertexBuffer
from PyM3G.objects.appearance import Appearance  

class Mesh(Node):
    """
    A scene graph node that represents a 3D object defined as a polygonal surface.
    """

    def __init__(self):
        super().__init__()
        self.vertex_buffer: VertexBuffer = None
        self.submesh_count: int = None
        self.index_buffer = []
        self.appearance: Appearance = []

    def __str__(self):
        return obj2str(
            "Mesh",
            [
                ("Vertex Buffer", self.vertex_buffer),
                ("Submesh Count", self.submesh_count),
                ("Index Buffer", self.index_buffer),
                ("Appearance", self.appearance),
            ],
        ) + super().inherited_str()
    
    def inherited_str(self):
        if (self.vertex_buffer != None
            or self.submesh_count != None
            or self.index_buffer != []
            or self.appearance != []):
                return "From: " + Mesh.__str__(self)
        return "From: Mesh:\n\tdefault values"

    def read(self, reader):
        super().read(reader)
        self.vertex_buffer, self.submesh_count = unpack("<II", reader.read(8))
        for _ in range(self.submesh_count):
            self.index_buffer.append(unpack("<I", reader.read(4))[0])
            self.appearance.append(unpack("<I", reader.read(4))[0])

    def get_appearance(self, index: int) -> Appearance:    
        """
        Gets the current Appearance of the specified submesh.
        """
        if index < 0 or index >= self.submesh_count:
            raise IndexError("Index out of range")
        return self.appearance[index]

    def get_index_buffer(self, index: int):
        """
        Retrieves the submesh at the given index.
        """
        if index < 0 or index >= self.submesh_count:
            raise IndexError("Index out of range")
        return self.index_buffer[index]
    
    def get_submesh_count(self) -> int:
        """
        Gets the number of submeshes in this Mesh.
        """
        return self.submesh_count
    
    def get_vertex_buffer(self) -> VertexBuffer:
        """
        Gets the vertex buffer of this Mesh. 
        """
        return self.vertex_buffer

    def set_appearance(self, index: int, appearance: Appearance):
        """
        Sets the Appearance for the specified submesh.
        """
        if index < 0 or index >= self.submesh_count:
            raise IndexError("Index out of range")
        self.appearance[index] = appearance