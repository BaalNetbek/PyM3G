from struct import pack, unpack
import zlib

class Section:
    UNCOMPRESSED = 0
    ZLIB = 1
    def __init__(self):
        self.compression_scheme = 0 
        self.total_section_size = 0
        self.uncompressed_size = 0
        self.objects = r''
        self.checksum = 0

    def getCompressionScheme(self):
        return self.compression_scheme
    
    def getSize(self):
        return len(self.objects)+13
    
    def read(self, file):
        header = file.read(9)
        if header == b"":
            return
        self.compression_scheme, self.total_section_size, self.uncompressed_size = unpack("<BII", header)
        self.objects = file.read(self.total_section_size-13)
        self.checksum = unpack("<I", file.read(4))[0]

    def write(self, file):
        file.write(pack("<bII", self.compression_scheme, self.total_section_size, self.uncompressed_size))
        file.write(self.objects)
        file.write(pack("<I", self.checksum))

    def decompress(self):
        if self.compression_scheme == Section.ZLIB:
            self.objects = zlib.decompress(self.objects)
            self.total_section_size = self.getSize()
            self.compression_scheme = Section.UNCOMPRESSED
            self.checksum = zlib.adler32(pack("<BII", self.compression_scheme, self.total_section_size, self.uncompressed_size) + self.objects)

    def compress(self):
        if self.compression_scheme == Section.UNCOMPRESSED:
            self.objects = zlib.compress(self.objects)
            self.total_section_size = self.getSize()
            self.compression_scheme = Section.ZLIB
            self.checksum = zlib.adler32(pack("<BII", self.compression_scheme, self.total_section_size, self.uncompressed_size) + self.objects)