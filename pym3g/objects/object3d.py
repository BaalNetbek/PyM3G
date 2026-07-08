"""Object3D Class"""

from struct import unpack, pack
from pym3g.util import obj2str, deref_from_file, verify_ref
from pym3g.objects.object import ObjectM3G

class Object3D(ObjectM3G):
    """
    An abstract base class for all objects that can be part of a 3D world
    """

    HAS_REFS = True

    def __init__(self):
        self.user_id = 0
        self.animation_tracks_idx = []
        self.animation_tracks = []
        self.user_parameters = {}

    def __str__(self):
        return obj2str(
            "Object3D",
            [
                ("User ID", self.user_id),
                ("Animation Tracks", self.animation_tracks_idx),
                ("User Parameters", self.user_parameters),
            ],
        )
    
    def inherited_str(self):
        if (self.user_id != 0
            or self.animation_tracks_idx != []
            or self.user_parameters != {}):
            return "From " + Object3D.__str__(self)
        return "From Object3D: default values\n"

    def read(self, reader, objects=None):
        """Read object data from an input stream"""
        self.user_id, at_count = unpack("<II", reader.read(8))
        if at_count > 0:
            for _ in range(at_count):
                self.animation_tracks_idx.append(unpack("<I", reader.read(4))[0])
        up_count = unpack("<I", reader.read(4))[0]
        if up_count > 0:
            for _ in range(up_count):
                pid, psz = unpack("<II", reader.read(8))
                self.user_parameters[pid] = reader.read(psz)
        
        # importing here to evade import loop
        from pym3g.objects.animation_track import AnimationTrack 
        deref_from_file(self, "animation_tracks", AnimationTrack, self.animation_tracks_idx, objects)

    def update_ref(self, objects):
        self.animation_tracks_idx = []
        child_idx = []
        this_idx = 0
        for i, o in enumerate(objects):
            if o == self:
                this_idx = i+1
            for at in self.animation_tracks:
                if o == at:
                    self.animation_tracks_idx.append(i+1)
                    child_idx.append(i+1)   
        verify_ref(self, this_idx, child_idx)

    def write(self, writer):
        """Write object data to an output stream"""
        writer.write(pack(
            "<II",
            self.user_id, 
            len(self.animation_tracks_idx)
            ))
        if len(self.animation_tracks_idx) > 0:
            for track in self.animation_tracks_idx:
                writer.write(pack("<I", track))
        writer.write(pack("<I", len(self.user_parameters)))
        if len(self.user_parameters) > 0:
            for pid, pval in self.user_parameters.items():
                writer.write(pack("<II", pid, len(pval)))
                writer.write(pval)
