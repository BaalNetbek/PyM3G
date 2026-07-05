"""World Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, deref_from_file, verify_ref
from PyM3G.objects.group import Group
from PyM3G.objects.background import Background
from PyM3G.objects.camera import Camera

class World(Group):
    """
    A special Group node that is a top-level container for scene graphs
    """

    HAS_REFS = True

    def __init__(self):
        super().__init__()
        self.active_camera_idx: int = None
        self.active_camera: Camera = None
        self.background_idx: int = None
        self.background: Background = None

    def __str__(self):
        return obj2str(
            "World",
            [("Active Camera", self.active_camera_idx), ("Background", self.background_idx)],
        ) + super().inherited_str()
    
    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.active_camera_idx, self.background_idx = unpack("<II", reader.read(8))
        
        deref_from_file(self, "active_camera", Camera, self.active_camera_idx, objects)
        deref_from_file(self, "background", Background, self.background_idx, objects)

    def update_ref(self, objects):
        super().update_ref(objects) 
        self.active_camera_idx = 0
        self.background_idx = 0
        child_idx = []
        this_idx = 0
        for i, o in enumerate(objects):
            if o == self:
                this_idx = i+1
            if o == self.active_camera:
                self.active_camera_idx = i+1
                child_idx.append(i+1)
            if o == self.background:
                self.background_idx = i+1
                child_idx.append(i+1)

        verify_ref(self, this_idx, child_idx)


    def write(self, writer):
        super().write(writer)
        writer.write(
            pack(
                "<II",
                self.active_camera_idx,
                self.background_idx
            )
        )