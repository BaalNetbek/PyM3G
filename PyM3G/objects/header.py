"""Header Class"""

from struct import unpack, pack
from PyM3G.util import obj2str
from PyM3G.objects.object import ObjectM3G

class Header(ObjectM3G):
    """
    Header contains metadata about the file
    """

    HAS_REFS = False

    def __init__(self, ver: list[int] | tuple[int, int] = (1,0), extern_refs: bool = False, tot_size: int = 0, uncompressed_size: int = 0,auth_text: str = "", ):
        self.version: list[int] = ver
        self.has_external_references: bool = extern_refs
        self.total_file_size: int = 0
        self.approximate_content_size: int = 0
        self.authoring_field: str = auth_text

    def __str__(self):
        return obj2str(
            "Header",
            [
                ("Version", "%d.%d" % (self.version[0], self.version[1])),
                ("Has external references", self.has_external_references),
                ("Total file size", self.total_file_size),
                ("Approximate content size", self.approximate_content_size),
                ("Authoring field text", ("\n%s" % self.authoring_field) if self.authoring_field != "" else ""),
            ],
        )

    def read(self, reader, objects=None):
        """Read header from file stream"""
        self.version = unpack("<BB", reader.read(2))
        (
            self.has_external_references,
            self.total_file_size,
            self.approximate_content_size,
        ) = unpack("<?II", reader.read(9))
        self.authoring_field = reader.read().rstrip(b"\x00").decode("utf-8")

    def update_ref(self, objects):
        pass
    
    def write(self, writer):
        """
        If file structure was changed sizes has to be updated manually!
        Write header to file stream.
        """
        writer.write(pack("<BB", *self.version))
        writer.write(pack("<?II", self.has_external_references, self.total_file_size, self.approximate_content_size))
        writer.write(self.authoring_field.encode("utf-8") + b"\x00")