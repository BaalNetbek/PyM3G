"""Mesh Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, deref_from_file, verify_ref
from PyM3G.objects.node import Node
from PyM3G.objects.vertex_buffer import VertexBuffer
from PyM3G.objects.appearance import Appearance 
from PyM3G.objects.triangle_strip_array import TriangleStripArray 

class Mesh(Node):
    """
    A scene graph node that represents a 3D object defined as a polygonal surface.
    Contains indices of objects in the scene building the mesh.
    """

    HAS_REFS = True

    def __init__(self):
        super().__init__()
        self.vertex_buffer_idx: int = None
        self.vertex_buffer: VertexBuffer = None
        self.submesh_count: int = None
        self.index_buffer_idx: list[int] = []
        self.index_buffer: list[TriangleStripArray] = []
        self.appearance_idx: list[int] = []
        self.appearance: list[Appearance] = []

    def __str__(self):
        return obj2str(
            "Mesh",
            [
                ("Vertex Buffer", self.vertex_buffer_idx),
                ("Submesh Count", self.submesh_count),
                ("Index Buffer", self.index_buffer_idx),
                ("Appearance", self.appearance_idx),
            ],
        ) + super().inherited_str()
    
    def inherited_str(self):
        if (self.vertex_buffer_idx != None
            or self.submesh_count != None
            or self.index_buffer_idx != []
            or self.appearance_idx != []):
                return "From " + Mesh.__str__(self)
        return "From Mesh:\n\tdefault values"

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.vertex_buffer_idx, self.submesh_count = unpack("<II", reader.read(8))
        for _ in range(self.submesh_count):
            self.index_buffer_idx.append(unpack("<I", reader.read(4))[0])
            self.appearance_idx.append(unpack("<I", reader.read(4))[0])
     
        deref_from_file(self, "vertex_buffer", VertexBuffer, self.vertex_buffer_idx, objects)
        deref_from_file(self, "index_buffer", TriangleStripArray, self.index_buffer_idx, objects)
        deref_from_file(self, "appearance", Appearance, self.appearance_idx, objects)

    def update_ref(self, objects):
        super().update_ref(objects)
        self.vertex_buffer_idx = 0
        self.index_buffer_idx = []
        self.appearance_idx = []
        child_idx = []
        this_idx = 0
        for i, o in enumerate(objects):
            if o == self:
                this_idx = i+1
            if o == self.vertex_buffer:
                self.vertex_buffer_idx = i+1
                child_idx.append(i+1)   
            for a in self.appearance:
                if o == a:
                    self.appearance_idx.append(i+1)
                    child_idx.append(i+1)   
            for ib in self.index_buffer:
                if o == ib:
                    self.index_buffer_idx.append(i+1)
                    child_idx.append(i+1)   
        verify_ref(self, this_idx, child_idx)

    def write(self, writer):
        super().write(writer)
        writer.write(pack("<II", self.vertex_buffer_idx, self.submesh_count))
        for i in range(self.submesh_count):
            writer.write(pack("<I", self.index_buffer_idx[i]))
            writer.write(pack("<I", self.appearance_idx[i]))

    # def update_references(self, objects):
    #     """Updates references from m3g file extracted objects list."""
    #     vb = objects[self.vertex_buffer_idx-1]
    #     if not isinstance(vb, VertexBuffer):
    #         raise TypeError("Expected VertexBuffer, got {}".format(type(vb).__name__))
    #     self.vertex_buffer = vb
    #     for ibi in self.index_buffer_idx:
    #         ib = objects[ibi - 1]
    #         if not isinstance(ib, TriangleStripArray):
    #             raise TypeError("Expected {}, got {}".format(TriangleStripArray.__name__, type(vb).__name__))
    #         self.index_buffer.append(ib)
    # @staticmethod
    # def update_reference(field, field_type, idx, objects):
    #     if not isinstance([idx], (list, tuple)):
    #         idx = (idx,)
    #         field = None
    #     else:
    #         field = []
    #     for ix in idx:
    #         ref = objects[ix - 1]
    #         if not isinstance(ref, field_type):
    #             raise TypeError("Expected {}, got {}".format(field_type.__name__, type(ref).__name__))
    #         if field == []:
    #             field.append(ref)
    #         else:
    #             field = ref


    # def get_appearance(self, index: int) -> Appearance:    
    #     """
    #     Gets the current Appearance of the specified submesh.
    #     """
    #     if index < 0 or index >= self.submesh_count:
    #         raise IndexError("Index out of range")
    #     return self.appearance[index]

    # def get_index_buffer(self, index: int):
    #     """
    #     Retrieves the submesh at the given index.
    #     """
    #     if index < 0 or index >= self.submesh_count:
    #         raise IndexError("Index out of range")
    #     return self.index_buffer[index]
    
    # def get_submesh_count(self) -> int:
    #     """
    #     Gets the number of submeshes in this Mesh.
    #     """
    #     return self.submesh_count
    
    # def get_vertex_buffer(self) -> VertexBuffer:
    #     """
    #     Gets the vertex buffer of this Mesh. 
    #     """
    #     return self.vertex_buffer

    # def set_appearance(self, index: int, appearance: Appearance):
    #     """
    #     Sets the Appearance for the specified submesh.
    #     """
    #     if index < 0 or index >= self.submesh_count:
    #         raise IndexError("Index out of range")
    #     self.appearance[index] = appearance