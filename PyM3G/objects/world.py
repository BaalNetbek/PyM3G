"""World Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, deref_from_file
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

    # TODO upadate_ref

    def update_ref(self, objects):
        raise(Exception("%s.update_ref() not implemented" % type(self).__name__))
        super().update_ref(objects) 


    def write(self, writer):
        super().write(writer)
        writer.write(
            pack(
                "<II",
                self.active_camera_idx,
                self.background_idx
            )
        )