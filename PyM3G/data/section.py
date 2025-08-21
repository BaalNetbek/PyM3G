from struct import pack, unpack
from PyM3G.objects.object import Object

import zlib
from io import BytesIO

class Section:
    _const2str = {
        0: "UNCOMPRESSED", 
        1: "ZLIB",    
    }
    UNCOMPRESSED = 0
    ZLIB = 1
    def __init__(self, logger = None):
        self.compression_scheme: int = 0 
        self.total_section_size: int = 0
        self.uncompressed_size: int = 0
        self.objects_bytes: bytes = b''
        self.checksum: int = 0
        self.log = logger

    def getCompressionScheme(self):
        return self.compression_scheme
    
    def getSize(self):
        return len(self.objects_bytes)+13
    
    def set_objects(self, objects: list[Object], compression = None):
        from PyM3G.reader import M3GReader
        if compression not in (Section.ZLIB, Section.UNCOMPRESSED, None):
            raise ValueError("Error, set_objects(): invalid arg compression value: {}.".format(compression))
        if compression != None:
            self.compression_scheme = compression

        objects_writer = BytesIO()
        for o in objects:
            # docs page 261
            tmp_object = BytesIO() 
            o.write(tmp_object)
            objects_writer.write(pack(
                "<BI", 
                M3GReader._class2type[o.__class__], 	# ObjectType
                tmp_object.tell()			            # Length
                )) 		
            objects_writer.write(tmp_object.getvalue()) # Data
        self.objects_bytes = objects_writer.getvalue()
        self.uncompressed_size == self.getSize()
        if self.compression_scheme == Section.ZLIB:
            self.objects_bytes = zlib.compress(self.objects_bytes)
        self.total_section_size == self.getSize()
        self.checksum = zlib.adler32(
            pack("<bII", self.compression_scheme, self.total_section_size, self.uncompressed_size) + self.objects_bytes
        )

    def read(self, file):
        header = file.read(9)
        if header == b"":
            self.file_size = file.tell()
            self.log_info("Reached end of file @ %d", self.file_size)
            return b""
        self.log_info("Section @ %d", file.tell() - 9)

        self.compression_scheme, self.total_section_size, self.uncompressed_size = unpack("<BII", header)

        self.log_info("Compression: %s", Section._const2str[self.compression_scheme])
        self.log_info("Total length: %d", self.total_section_size)
        self.log_info("Uncompressed length: %d", self.uncompressed_size)

        self.objects_bytes = file.read(self.total_section_size-13)
        self.checksum = unpack("<I", file.read(4))[0]
        chksum_verify = zlib.adler32(header + self.objects_bytes)
        if self.checksum != chksum_verify:
            self.log_error("Checksums do not match, file '%s' may be corrupt"%file.name)
        else:    
            self.log_info("Checksum validated successfully")
        # if self.checksum != chksum_verify:
        #     raise ValueError("Section checksum validation failed computed: %d, read: %d"%(chksum_verify, self.checksum))
        return self.objects_bytes
            
    def write(self, file):
        file.write(pack("<bII", self.compression_scheme, self.total_section_size, self.uncompressed_size))
        file.write(self.objects_bytes)
        file.write(pack("<I", self.checksum))

    def decompress(self, force: bool = False):
        if self.compression_scheme == Section.ZLIB or force:
            self.objects_bytes = zlib.decompress(self.objects_bytes)
            self.total_section_size = self.getSize()
            self.compression_scheme = Section.UNCOMPRESSED
            self.checksum = zlib.adler32(pack("<BII", self.compression_scheme, self.total_section_size, self.uncompressed_size) + self.objects_bytes)

    def compress(self, force: bool = False):
        if self.compression_scheme == Section.UNCOMPRESSED or force:
            self.objects_bytes = zlib.compress(self.objects_bytes)
            self.total_section_size = self.getSize()
            self.compression_scheme = Section.ZLIB
            self.checksum = zlib.adler32(pack("<BII", self.compression_scheme, self.total_section_size, self.uncompressed_size) + self.objects_bytes)

    def set_compression(self, compression):
        if compression == Section.ZLIB:
            self.compress()
        elif compression == Section.UNCOMPRESSED:
            self.decompress()
        else:
            raise ValueError("Error, set_compression(): invalid arg compression value: {}.".format(compression))
        
    def log_info(self, msg: str, *args):
        try: 
            self.log.info(msg % args if args else msg)
            return True
        except AttributeError:
            return False

    def log_error(self, msg: str, *args):
        try: 
            self.log.error(msg % args if args else msg)
            return True
        except AttributeError:
            return False