"""
Contains base classes for objects
"""
from struct import unpack, pack


class Object3D:
    """
    An abstract base class for all objects that can be part of a 3D
    world
    """

    def __init__(self):
        self.user_id = 0
        self.animation_tracks = []
        self.user_parameters = {}

    def read(self, reader):
        """Read object data from an input stream"""
        self.user_id, at_count = unpack("<II", reader.read(8))
        if at_count > 0:
            for _ in range(at_count):
                self.animation_tracks.append(unpack("<I", reader.read(4))[0])
        up_count = unpack("<I", reader.read(4))[0]
        if up_count > 0:
            for _ in range(up_count):
                pid, psz = unpack("<II", reader.read(8))
                self.user_parameters[pid] = reader.read(psz)

    def write(self, writer):
        """Write object data to an output stream"""
        writer.write(pack("<II", self.user_id, len(self.animation_tracks)))
        if len(self.animation_tracks) > 0:
            for track in self.animation_tracks:
                writer.write(pack("<I", track))
        writer.write(pack("<I", len(self.user_parameters)))
        if len(self.user_parameters) > 0:
            for pid, pval in self.user_parameters.items():
                writer.write(pack("<II", pid, len(pval)))
                writer.write(pval)


class Transformable(Object3D):
    """
    An abstract base class for Node and Texture2D, defining common methods
    for manipulating node and texture transformations
    """

    def __init__(self):
        super().__init__()
        self.has_component_transform = None
        self.translation = (0, 0, 0)
        self.scale = (1, 1, 1)
        self.orientation_angle = 0
        self.orientation_axis = None
        self.has_general_transform = None
        self.transform = None

    def read(self, reader):
        super().read(reader)
        self.has_component_transform = unpack("<?", reader.read(1))[0]
        if self.has_component_transform:
            self.translation = unpack("<3f", reader.read(12))
            self.scale = unpack("<3f", reader.read(12))
            self.orientation_angle = unpack("<f", reader.read(4))[0]
            self.orientation_axis = unpack("<3f", reader.read(12))
        self.has_general_transform = unpack("<?", reader.read(1))[0]
        if self.has_general_transform:
            self.transform = unpack("<16f", reader.read(64))


class Node(Transformable):
    """
    An abstract base class for all scene graph nodes
    """

    def __init__(self):
        super().__init__()
        self.enable_rendering = True
        self.enable_picking = True
        self.alpha_factor = 1.0
        self.scope = -1
        self.has_alignment = None
        self.z_target = None
        self.y_target = None
        self.z_reference = None
        self.y_reference = None

    def read(self, reader):
        super().read(reader)
        (
            self.enable_rendering,
            self.enable_picking,
            self.alpha_factor,
            self.scope,
            self.has_alignment,
        ) = unpack("<??BI?", reader.read(8))
        if self.has_alignment:
            (self.z_target, self.y_target, self.z_reference, self.y_reference) = unpack(
                "<BBII", reader.read(10)
            )
        self.alpha_factor = self.alpha_factor / 255.0
