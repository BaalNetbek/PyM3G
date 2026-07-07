from struct import pack, unpack
from pym3g.objects import *
from pym3g.objects.object import ObjectM3G

import zlib
from io import BytesIO

_type2class = {
    0: Header,
    1: AnimationController,
    2: AnimationTrack,
    3: Appearance,
    4: Background,
    5: Camera,
    6: CompositingMode,
    7: Fog,
    8: PolygonMode,
    9: Group,
    10: Image2D,
    11: TriangleStripArray,
    12: Light,
    13: Material,
    14: Mesh,
    15: MorphingMesh,
    16: SkinnedMesh,
    17: Texture2D,
    18: Sprite,
    19: KeyframeSequence,
    20: VertexArray,
    21: VertexBuffer,
    22: World,
    100: Submesh,
    255: ExternalReference,
}

_class2type = {cls: t for t, cls in _type2class.items()}
class Section:
    """
    Class for r/w .m3g file sections. Stores objects in binary format.
    """

    UNCOMPRESSED = 0
    ZLIB = 1
    _comprEnum2str = {
        0: "UNCOMPRESSED", 
        1: "ZLIB",    
    }

    def __init__(self, objects: list[ObjectM3G]|ObjectM3G = None, compression = UNCOMPRESSED, logger = None):
        self.compression_scheme: int = 0 
        self.total_section_size: int = 0
        self.uncompressed_size: int = 0
        self.objects_bytes: bytes = b''
        self.checksum: int = 0
        self.log = logger
        self.objects_offset: int = None
        if objects:
            self.set_objects(objects, compression)
        else:
            self.objects: list[ObjectM3G] = []

    def getCompressionScheme(self):
        return self.compression_scheme
    
    def setCompressionScheme(self, scheme):
        if scheme is None:
            return
        if scheme not in (Section.ZLIB, Section.UNCOMPRESSED):
            raise ValueError("Error, set_objects(): invalid arg compression value: {}.".format(scheme))
        self.compression_scheme = scheme
    
    def getSize(self):
        return len(self.objects_bytes)+13
    
    def getObjectsSize(self):
        return len(self.objects_bytes) 

    def set_objects(self, objects: list[ObjectM3G]|ObjectM3G, compression = UNCOMPRESSED):
        self.setCompressionScheme(compression)
        if type(objects) == list:
            self.objects = objects
        else:
            self.objects = [objects]
        self.updateFields()

    def read(self, file, before_objects):
        header = file.read(9)
        if header == b"":
            self.file_size = file.tell()
            self.log_info("Reached end of file @%s", hex(self.file_size))
            return b""
        self.log_info("Section @%s", hex(file.tell() - 9))

        self.compression_scheme, self.total_section_size, self.uncompressed_size = unpack("<BII", header)
        if self.compression_scheme not in (Section.ZLIB, Section.UNCOMPRESSED):
            raise ValueError("Unknown compression scheme: %d"%self.compression_scheme)
        self.log_info("Compression: %s", Section._comprEnum2str[self.compression_scheme])
        self.log_info("Total length: %s", hex(self.total_section_size))
        self.log_info("Uncompressed length: %s", hex(self.uncompressed_size))

        self.objects_offset = file.tell()
        self.objects_bytes = file.read(self.total_section_size-13)
        self.checksum = unpack("<I", file.read(4))[0]
        chksum_verify = zlib.adler32(header + self.objects_bytes)
        if self.checksum != chksum_verify:
            self.log_error("Checksums do not match, file '%s' may be corrupt"%file.name)
        else:    
            self.log_info("Checksum validated successfully")
        if self.compression_scheme == Section.ZLIB:
            self.read_objects(zlib.decompress(self.objects_bytes), before_objects)
        elif self.compression_scheme == Section.UNCOMPRESSED:
            self.read_objects(self.objects_bytes, before_objects, self.objects_offset)
        else:
            raise ValueError("WTF? Unknown compression scheme: %d"%self.compression_scheme)
       
        return self.objects_bytes

    def read_objects(self, data, before_objects, offset = None):
        """Reads all objects from a section"""
        with BytesIO(data) as rdr:
            while True:
                if offset == None:
                    obj_off = None
                else:
                    obj_off = offset + rdr.tell()
                object_header = rdr.read(5)
                if object_header == b"":
                    break
                object_type, size = unpack("<BI", object_header)
                if object_type == _class2type[ExternalReference]:
                    ext_ref = self.parse_object(object_type, rdr.read(size), before_objects, obj_off)
                    exr = self.parse_external_ref(ext_ref)
                    self.objects.append(exr)
                    before_objects.append(exr)
                else:
                    ob = self.parse_object(object_type, rdr.read(size), before_objects, obj_off)
                    self.objects.append(ob)
                    before_objects.append(ob)


    def parse_object(self, objtype, data, before_objects = None, offset = None):
        """Parse an object out of a uncompressed binary data chunk"""
        with BytesIO(data) as rdr:
            if objtype in _type2class:
                obj = _type2class.get(objtype)()
            else:
                obj = None
                if offset == None:
                    self.log_error("Invalid object type(%d) found", objtype)
                else:
                    self.log_error("Invalid object type(%d) found @%s", objtype, hex(offset))
                return None
            
            if offset == None:
                self.log_info(
                    "Found [bold cyan]%s[/] object",
                    obj.__class__.__name__, 
                    extra={"markup": True},
                )
            else:
                self.log_info(
                    "Found [bold cyan]%s[/] object @%s",
                    obj.__class__.__name__, hex(offset),
                    extra={"markup": True},
                )
            obj.read(rdr, before_objects)
            bytes_unread = len(rdr.read())
            if obj is None and bytes_unread > 0:
                self.log_error("%d bytes left unread", bytes_unread)
        return obj
            
    def updateFields(self):
        objects_writer = BytesIO()
        for o in self.objects:
            # docs page 261
            tmp_object = BytesIO() 
            o.write(tmp_object)
            objects_writer.write(pack(
                "<BI", 
                _class2type[o.__class__], 	# ObjectType
                tmp_object.tell()			            # Length
                )) 		
            objects_writer.write(tmp_object.getvalue()) # Data
        self.objects_bytes = objects_writer.getvalue()
        self.uncompressed_size = self.getObjectsSize()
        if self.compression_scheme == Section.ZLIB:
            self.objects_bytes = zlib.compress(self.objects_bytes)
        self.total_section_size = self.getSize()
        self.checksum = zlib.adler32(
            pack("<bII", self.compression_scheme, self.total_section_size, self.uncompressed_size) + self.objects_bytes
        )
        
    def write(self, file, update = True):
        if (update):
            self.updateFields()
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
        
    def log_info(self, msg: str, *args,  **kwargs):
        try: 
            self.log.info(msg % args if args else msg,  **kwargs)
            return True
        except AttributeError:
            return False

    def log_error(self, msg: str, *args,  **kwargs):
        try: 
            self.log.error(msg % args if args else msg,  **kwargs)
            return True
        except AttributeError:
            return False