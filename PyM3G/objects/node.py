"""Node Class"""

from struct import unpack, pack
from PyM3G.objects.transformable import Transformable
from PyM3G.util import obj2str



class Node(Transformable):
    """
    An abstract base class for all scene graph nodes
    """

    HAS_REFS = False

    def __init__(self):
        super().__init__()
        self.enable_rendering = True
        self.enable_picking = True
        self.alpha_factor = 1.0
        self.scope = 0xffffffff
        self.has_alignment = None
        self.z_target = None
        self.y_target = None
        self.z_reference = None
        self.y_reference = None

    def __str__(self):
        return obj2str(
            "Node",
            [
                ("Enable Rendering", self.enable_rendering),
                ("Enable Picking", self.enable_picking),
                ("Alpha Factor", self.alpha_factor),
                ("Scope", hex(self.scope)),
                ("Has Alignment", self.has_alignment),
                ("Z Target", self.z_target),
                ("Y Target", self.y_target),
                ("Z Reference", self.z_reference),
                ("Y Reference", self.y_reference),
            ],
        ) + super().inherited_str()
    
    def inherited_str(self):
        if (self.enable_rendering != True
            or self.enable_picking != True
            or self.alpha_factor != 1.0
            or self.scope != -1
            or self.has_alignment != None
            or self.z_target != None
            or self.y_target != None
            or self.z_reference != None
            or self.y_reference != None):
                return "From " + Node.__str__(self)
        return "From Node:\n\tdefault values"

    def read(self, reader, objects=None):
        super().read(reader, objects)
        (
            self.enable_rendering,
            self.enable_picking,
            self.alpha_factor,
            self.scope,
            self.has_alignment,
        ) = unpack("<??BI?", reader.read(8))
        if self.has_alignment:
            (
                self.z_target,
                self.y_target, 
                self.z_reference, 
                self.y_reference
                ) = unpack("<BBII", reader.read(10)
            )
        self.alpha_factor = self.alpha_factor / 255.0

    def update_ref(self, objects):
        super().update_ref(objects)

    def write(self, writer):
        super().write(writer)
        writer.write(pack( # line 79
                "<??BI?", 
                self.enable_rendering,
                self.enable_picking,
                int(self.alpha_factor * 255 + 0.5),
                self.scope,
                self.has_alignment,    
                ))
        if self.has_alignment:
            writer.write(pack(
                "<BBII",
                self.z_target, 
                self.y_target, 
                self.z_reference, 
                self.y_reference
                ))