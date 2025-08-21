"""External Reference Class"""

from PyM3G.util import obj2str
from PyM3G.objects.object import Object

class ExternalReference(Object):
    """
    Used for including external files (textures or other scenes)
    """

    def __init__(self):
        self.uri = None

    def __str__(self):
        return obj2str("External Reference", [("URI", self.uri)])

    def read(self, reader, objects=None):
        """Read external reference string from file stream"""
        self.uri = reader.read().rstrip(b"\x00").decode("utf-8")

    def write(self, writer):
        writer.write(self.uri.encode("utf-8") + b"\x00")