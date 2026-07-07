"""
Module for reading JSR 184 m3g files
"""

from io import BytesIO
from struct import unpack, pack
import logging

from PyM3G.util import fishlabs_deobfuscate
from PyM3G.data.section import Section
from PyM3G.objects import *
from PyM3G.objects.object import ObjectM3G

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
class M3GFile:
    """
    Reader, writer class for JSR 184 M3G data files
    """
    def __init__(self, path="", log_level=logging.ERROR):

        self.log = logging.getLogger("m3g")
        self.log.setLevel(log_level)

        self.objects = []
        self.sections = []
        self.file = None
        self.version = None

        if path != "":
            self.read(path)

    def get_object(self, obj_id):
        """Returns an object by id"""
        return self.objects[obj_id - 1]
    
    def read(self, path):
        try:
            with open(path, "rb") as file:
                self.file = file        
                self.version = self._verify_signature()
                if self.version == _BAD_SIG:
                    self.log.error("Invalid M3G file %s", path)
                    return [], []
                self.read_sections()
        except OSError as e:
            self.log.error(str(e))
            return [], []

        sections_lens = [*[len(s.objects) for s in self.sections]]
        self.log.info("Read sections with lenghts: "+ str(sections_lens) + " - " + str(sum(sections_lens)) + " objects total.")
        return self.sections, self.objects

    def _verify_signature(self):
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

    def read_sections(self):
        """Reads all sections from a file"""
        while True:
            section = Section(logger = self.log)
            if section.read(self.file, self.objects) == b'':
                if self.objects[0].total_file_size == section.file_size:
                    self.log.info(
                        "File size matches size declared in [bold cyan]Header[/]",
                        extra={"markup": True}
                    )
                else:
                    self.log.error(
                        "File size (%s Bytes) doesn't match size declared in [bold cyan]Header[/]: %s Bytes",
                        hex(section.file_size), hex(self.objects[0].total_file_size), extra={"markup": True}
                    )
                break
            self.sections.append(section)

    def set_sections(self, sections: list[Section], compression):
        sections = list(sections)
        header_sect = sections[0]
        header = header_sect.objects[0]
        if len(header_sect.objects) != 1 or type(header) != Header:
            raise ValueError("First section must have only Header object.")
        if header.has_external_references and any(not isinstance(o, ExternalReference) for o in sections[1].objects):  
            raise ValueError("External reference section doesn't exclusively containt external refs.")
        self.objects = [o for s in sections for o in s.objects]
        for o in self.objects:
            o.update_ref(self.objects) 

        sects = []
        size = len(_M3G_SIG)
        with BytesIO() as temp:
            temp.write(_M3G_SIG)
            header_sect = sections[0]
            sects.append(header_sect)
            header_sect.write(temp, Section.UNCOMPRESSED)
            size += header_sect.getSize()
            for s in sections[1:]:
                sects.append(s)
                s.write(temp, compression)
                size += s.getSize()
            self.sections = sects
            header.total_file_size = temp.tell()
            header.approximate_content_size = size
            temp.seek(len(_M3G_SIG))
            header_sect.write(temp, update=True)
            return temp.getvalue()

    def set_objects(self, objects: list[ObjectM3G], compression):
        n_heads = sum(isinstance(o, Header) for o in objects)
        n_erefs = sum(isinstance(o, ExternalReference) for o in objects)
        n_data = len(objects) - n_heads - n_erefs

        objects = list(objects)
        if n_heads == 0:
            objects = [Header()] + objects
        elif n_heads > 1:
            raise ValueError("Too many Header objects in the list")
        elif not isinstance(objects[0], Header): # n_heads == 1    
            self.log.warning("Header is not the first object in the list. Moving the Header to the begging.")
            head_pos = next((i for i, o in enumerate(objects) if isinstance(o, Header)), None)
            objects[0:0] = [objects.pop(head_pos)] # move it to [0]
        header = objects[0]
        
        if n_erefs > 0:
            if not all(isinstance(o, ExternalReference) for o in objects[1:1 + n_erefs]): 
                erefs = [o for o in objects if isinstance(o, ExternalReference)]
                data = [o for o in objects if not isinstance(o, ExternalReference)]
                objects[:] = [header] + erefs + data
        for o in objects:
            o.update_ref(objects) 

        sects = []
        size = len(_M3G_SIG)
        with BytesIO() as temp:
            temp.write(_M3G_SIG)
            header_sect = Section(header, Section.UNCOMPRESSED)
            sects.append(header_sect)
            header_sect.write(temp)
            size += header_sect.getSize()
            if n_erefs > 0:
                eref_sect = Section(objects[1:1+n_erefs])
                sects.append(eref_sect)
                eref_sect.write(temp)
                size += eref_sect.getSize()
            if n_data > 0:
                data_sect = Section(objects[1+n_erefs:])
                data_sect.write(temp)
                sects.append(data_sect)
                size += data_sect.getSize()
            self.sections = sects

            header.total_file_size = temp.tell()
            header.approximate_content_size = size
            temp.seek(len(_M3G_SIG))
            header_sect.write(temp, update=True)
            return temp.getvalue()
        
    def write(self, path, sect_or_obj, compression = None):
        write_bytes = b""
        if not isinstance(sect_or_obj, list):
            raise TypeError("Section obj must be a list")
        if all(isinstance(o, ObjectM3G) for o in sect_or_obj):
            objects = sect_or_obj
            write_bytes = self.set_objects(objects, compression)
        elif all(isinstance(s, Section) for s in sect_or_obj): 
            sections = sect_or_obj
            write_bytes = self.set_sections(sections, compression)
        else:
            raise TypeError("sect_or_obj must be list of exclusively Section or Object instances")
            
        with open(path, "wb") as f:
            if write_bytes:
                f.write(write_bytes)
                return
            f.write(_M3G_SIG)
            for s in self.sections:
                s.write(f)