"""Vertex Buffer Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, deref_from_file
from PyM3G.data.color import Color
from PyM3G.objects.object3d import Object3D
from PyM3G.objects.vertex_array import VertexArray


class VertexBuffer(Object3D):
    """
    VertexBuffer holds references to VertexArrays that contain the positions, colors,
    normals, and texture coordinates for a set of vertices
    """

    def __init__(self):
        super().__init__()
        self.default_color = Color([0xff, 0xff, 0xff, 0xff])
        self.positions_idx = None
        self.positions: VertexArray = None
        self.position_bias = None
        self.position_scale = None
        self.normals_idx = None
        self.normals: VertexArray = None
        self.colors_idx = None
        self.colors: VertexArray = None
        self.texcoord_array_count = None
        self.tex_coords_idx = []
        self.tex_coords: list[VertexArray] = []
        self.tex_coord_bias = []
        self.tex_coord_scale = []

    def __str__(self):
        return obj2str(
            "VertexBuffer",
            [
                ("Default Color", self.default_color),
                ("Positions", self.positions_idx),
                ("Position Bias", self.position_bias),
                ("Position Scale", self.position_scale),
                ("Normals", self.normals_idx),
                ("Colors", self.colors_idx),
                ("Texcoord Array Count", self.texcoord_array_count),
                ("Texcoords", self.tex_coords_idx),
                ("Texcoord Bias", "\n\t" + str(self.tex_coord_bias) + "\n\tresolution:\n\t{}".format([round(1/b, 3) for bs in self.tex_coord_bias for b in bs])),
                ("Texcoord Scale", "{} \n\tresolution {}".format(self.tex_coord_scale, [round(1/s, 3) for s in self.tex_coord_scale])),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.default_color = Color(unpack("<4B", reader.read(4)))
        self.positions_idx = unpack("<I", reader.read(4))[0]
        self.position_bias = unpack("<3f", reader.read(12))
        (
            self.position_scale,
            self.normals_idx,
            self.colors_idx,
            self.texcoord_array_count,
        ) = unpack("<f3I", reader.read(16))
        if self.texcoord_array_count > 0:
            for _ in range(self.texcoord_array_count):
                self.tex_coords_idx.append(unpack("<I", reader.read(4))[0])
                self.tex_coord_bias.append(unpack("<3f", reader.read(12)))
                self.tex_coord_scale.append(unpack("<f", reader.read(4))[0])
                
        deref_from_file(self, "positions", VertexArray, self.positions_idx, objects)
        deref_from_file(self, "normals", VertexArray, self.normals_idx, objects)
        deref_from_file(self, "colors", VertexArray, self.colors_idx, objects)
        deref_from_file(self, "tex_coords", VertexArray, self.tex_coords_idx, objects)    

    def write(self, writer):
        super().write(writer)
        writer.write(pack("<4B", *self.default_color.to_list(4)))
        writer.write(pack("<I", self.positions_idx))
        writer.write(pack("<3f", *self.position_bias))
        writer.write(pack(
            "<f3I",
            self.position_scale, 
            self.normals_idx, 
            self.colors_idx, 
            self.texcoord_array_count
            ))
        if self.texcoord_array_count > 0:
            for i in range(self.texcoord_array_count):
                writer.write(pack("<I", self.tex_coords_idx[i]))
                writer.write(pack("<3f", *self.tex_coord_bias[i]))
                writer.write(pack("<f", self.tex_coord_scale[i]))

    # def get_colors(self):
    #     """
    #     Gets the current color array, or null if per-vertex colors are not set.
    #     """
    #     pass
    # def get_default_color(self):
    #     """
    #     Retrieves the default color of this VertexBuffer.
    #     """
    #     pass
    
    # def get_normals(self):
    #     """
    #     Gets the current normal vector array, or null if normals are not set.
    #     """
    #     pass
