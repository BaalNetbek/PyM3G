"""Submesh Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, deref_from_file, verify_ref
from PyM3G.objects.object3d import Object3D
from PyM3G.objects.appearance import Appearance 
from PyM3G.objects.triangle_strip_array import TriangleStripArray 

class Submesh(Object3D):
    """
    Non standard object from EA's IM M3G implementation
    """
    def __init__(self):
        super().__init__()
        self.index_buffer_idx: int = None
        self.index_buffer: TriangleStripArray = None
        self.appearance_idx: int = None
        self.appearance: Appearance = None
    
    def __str__(self):
        return obj2str(
            "Mesh",
            [
                ("Index Buffer", self.index_buffer_idx),
                ("Appearance", self.appearance_idx),
            ],
        ) + super().inherited_str()
    
    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.index_buffer_idx, self.appearance_idx = unpack("<II", reader.read(8))
        deref_from_file(self, "index_buffer", TriangleStripArray, self.index_buffer_idx, objects)
        deref_from_file(self, "appearance", Appearance, self.appearance_idx, objects)

    def update_ref(self, objects):
        super().update_ref(objects)
        self.index_buffer_idx = 0
        self.appearance_idx = 0
        child_idx = []
        this_idx = 0
        for i, o in enumerate(objects):
            if o == self:
                this_idx = i+1
            if o == self.index_buffer:
                self.index_buffer_idxappearance_idx = i+1
                child_idx.append(i+1) 
            if o == self.appearance:
                self.appearance_idx = i+1
                child_idx.append(i+1)
        verify_ref(self, this_idx, child_idx)