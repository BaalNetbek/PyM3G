"""
Module for reading JSR 184 m3g files
"""

from io import BytesIO
from struct import unpack, pack
import zlib
import logging

from PyM3G.util import fishlabs_deobfuscate
from PyM3G.data.section import Section
from PyM3G.objects import *

_M3G_SIG = b"\xAB\x4A\x53\x52\x31\x38\x34\xBB\x0D\x0A\x1A\x0A"
"""«JSR184»"""
_IM_M3G_SIG = b"\xAB\x49\x4D\x2D\x4D\x33\x47\xBB\x0D\x0A\x1A\x0A" 
"""«IM-M3G»"""
_IM2M3G_SIG = b"\xAB\x49\x4D\x32\x4D\x33\x47\xBB\x0D\x0A\x1A\x0A" 
"""«IM2M3G»"""

_BAD_SIG = 0
_M3G = 1 
_IM_M3G = 2 
_IM2M3G = 3
class M3GReader:
    """
    Reader for JSR 184 M3G data files
    """

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

    log = None



    def __init__(self, path, log_handler = logging.StreamHandler(), log_level=logging.ERROR):
        logging.basicConfig(
            level=logging.NOTSET,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[log_handler],
        )
        self.log = logging.getLogger("m3g")
        self.log.setLevel(log_level)

        # self.status = M3GStatus.FAILED
        self.objects = []
        self.sections_lens = []
        self.sect_cnt = 0
        self.file = open(path, "rb")
        if not self.file:
            self.log.error("Could not open file %s", path)
            return
        self.version = self.verify_signature()
        if self.version == _BAD_SIG:
            self.log.error("Invalid M3G file %s", path)
            self.file.close()
            return
        self.read_sections()
        self.log.info("Read sections with lenghts: "+ str([s[1]-s[0] for s in self.sections_lens]) + " - " + str(self.sections_lens[self.sect_cnt-1][1]) + " objects total.")
        self.file.close()
        # self.status = M3GStatus.SUCCESS

    def verify_signature(self):
        """Verify header bytes to make sure this is a valid m3g file"""
        magic = self.file.read(12)
        if magic == _M3G_SIG:
            return _M3G
        if magic == _IM_M3G_SIG:
            self.log.error("IronMonkey M3G signature detected")
            return _IM_M3G
        if magic == _IM2M3G_SIG:
            self.log.error("IronMonkey M3G 2 signature detected")
            return _IM2M3G
        self.file.seek(-12,2)
        if self.file.read(12) == _M3G_SIG[::-1]:
            from io import BytesIO
            self.file.seek(0)
            data = self.file.read()
            self.file = BytesIO(fishlabs_deobfuscate(data))
            if self.file.read(12) == _M3G_SIG:
                self.log.info("Fishlabs obfuscation detected")
                return _M3G
        return _BAD_SIG

    def parse_object(self, objtype, data, before_objects = None):
        """Parse an object out of a binary data chunk"""
        rdr = BytesIO(data)
        if objtype in self._type2class:
            obj = self._type2class.get(objtype)()
        else:
            obj = None
            self.log.error("Invalid object type(%d) found", objtype)
            rdr.close()
            return None
        self.log.info(
            "Found [bold cyan]%s[/] object",
            obj.__class__.__name__,
            extra={"markup": True},
        )
        obj.read(rdr, before_objects)

        bytes_unread = len(rdr.read())
        if obj is None and bytes_unread > 0:
            self.log.warning("%d bytes left unread", bytes_unread)
        rdr.close()
        return obj

    def read_objects(self, data):
        """Reads all objects from a section"""
        rdr = BytesIO(data)
        while True:
            object_header = rdr.read(5)
            if object_header == b"":
                break
            object_type, size = unpack("<BI", object_header)
            if object_type == self._class2type[ExternalReference]:
                ext_ref = self.parse_object(object_type, rdr.read(size), self.objects)                
                self.objects.append(self.parse_external_ref(ext_ref))
            else:
                self.objects.append(self.parse_object(object_type, rdr.read(size), self.objects))
            
        rdr.close()

    def read_sections(self):
        """Reads all sections from a file"""
        while True:
            section = Section(self.log)

            if section.read(self.file) == b'':
                if self.objects[0].total_file_size == section.file_size:
                    self.log.info(
                        "File size matches size declared in [bold cyan]Header[/]",
                        extra={"markup": True}
                    )
                else:
                    self.log.error(
                        "File size (%d Bytes) doesn't match size declared in [bold cyan]Header[/]: %d Bytes",
                        section.file_size, self.objects[0].total_file_size,extra={"markup": True}
                    )
                break
            self.sections_lens.append([len(self.objects)])

            if section.compression_scheme == Section.ZLIB:
                self.read_objects(zlib.decompress(section.objects_bytes))
            elif section.compression_scheme == Section.UNCOMPRESSED:
                self.read_objects(section.objects_bytes)
            else:
                self.log.error("Unknown Compression Scheme.")
                return            

            self.sections_lens[self.sect_cnt].append(len(self.objects))
            self.sect_cnt+=1

    def get_object(self, obj_id):
        """Returns an object by id"""
        return self.objects[obj_id - 1]

    def parse_external_ref(self, ext_ref: ExternalReference) -> Image2D:
        try:
            from PIL import Image
            from os import path
            path.join(path.dirname(self.file.name), ext_ref.uri)
            img = Image.open(path)
            mode_map = {
                "L": Image2D.LUMINANCE,
                "LA": Image2D.LUMINANCE_ALPHA,
                "RGB": Image2D.RGB,
                "RGBA": Image2D.RGBA,
                "A": Image2D.ALPHA,
            }
            if img.mode not in mode_map:
                raise ValueError(f"Unsupported image mode: {img.mode}")
            image2d = Image2D()
            image2d.format = mode_map[img.mode]
            image2d.is_mutable = False
            image2d.width, image2d.height = img.size
            image2d.palette = [] 
            image2d.pixels = list(img.tobytes())
            return image2d
        except Exception as e:
            self.log.error("Failed loading external image: %s" %ext_ref.uri)
            return Image2D()