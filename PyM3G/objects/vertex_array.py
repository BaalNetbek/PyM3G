"""Vertex Array Class"""

from struct import unpack, pack
from PyM3G.util import obj2str
from PyM3G.objects.object3d import Object3D


class VertexArray(Object3D):
    """
    An array of integer vectors representing vertex positions, normals, colors or
    texture coordinates
    """
    HAS_REFS = False

    def __init__(self, numVertices: int = None, numComponents: int = None, componentSize: int  = None, vertices: list = []):
        super().__init__()
        self.component_size: int = componentSize 
        """1-byte, 2-int16"""
        self.component_count: int = numComponents
        self.encoding: int = 0
        self.vertex_count: int = numVertices
        self.vertices: list = vertices

    def __str__(self):
        return obj2str(
            "VertexArray",
            [
                ("Component Size", self.component_size),
                ("Component Count", self.component_count),
                ("Encoding", self.encoding),
                ("Vertex Count", self.vertex_count),
                ("Vertices", "Array of %d items"%len(self.vertices)), # ", ".join(str(v) for v in self.vertices
            ],
        ) + super().inherited_str()
    
    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.vertices = []
        (
            self.component_size,
            self.component_count,
            self.encoding,
            self.vertex_count,
        ) = unpack("<3BH", reader.read(5))
        if self.component_size == 1:
            c_t = "b"
            c_s = 1
        elif self.component_size == 2:
            c_t = "h"
            c_s = 2
        elif self.component_size == 4:
            c_t = "f"
            c_s = 4
        # else:
        # log.error("Error reading vertex array")
        if self.encoding == 0:
            print(f"r vcount: {self.vertex_count}")
            self.vertices = unpack(
                        "<" + str(self.component_count * self.vertex_count) + c_t,
                        reader.read(self.component_count * self.vertex_count * c_s),
                    )
            
            # for _ in range(self.vertex_count):
            #     self.vertices.append(
            #         unpack(
            #             "<" + str(self.component_count) + c_t,
            #             reader.read(self.component_count * c_s),
            #         )
            #     )
        elif self.encoding == 1:
            delta = (0, 0, 0, 0)
            for _ in range(self.vertex_count):
                vtx = unpack(
                    "<" + str(self.component_count) + c_t,
                    reader.read(self.component_count * c_s),
                )
                if self.component_count == 2:
                    tvtx = (delta[0] + vtx[0], delta[1] + vtx[1])
                elif self.component_count == 3:
                    tvtx = (delta[0] + vtx[0], delta[1] + vtx[1], delta[2] + vtx[2])
                elif self.component_count == 4:
                    tvtx = (
                        delta[0] + vtx[0],
                        delta[1] + vtx[1],
                        delta[2] + vtx[2],
                        delta[3] + vtx[3],
                    )
                #self.vertices.append(tvtx)
                self.vertices.extend(tvtx)
                delta = tvtx

    def update_ref(self, objects):
        super().update_ref(objects)

    def write(self, writer):
        super().write(writer)
        if type(self.vertices[0]) == list:
            vert_element = 1
        else:
            vert_element = self.component_count

        vCount = len(self.vertices)/vert_element
        if (vCount != self.vertex_count):
            if (vCount % 1 == 0):
                print("Warning: VertexArray.write(): vertex_count != len(vertices). vertex_count updated.\n")
                self.vertex_count = vCount//vert_element
        writer.write(pack(
            "<3BH", 
            self.component_size, 
            self.component_count, 
            self.encoding, 
            self.vertex_count
            ))
        if self.component_size == 1:
            c_t = "b"
        elif self.component_size == 2:
            c_t = "h"
        elif self.component_size == 4:
            c_t = "f"
        # else:
        # log.error("Error writing vertex array")
        
        if self.encoding == 0:
            if type(self.vertices[0]) == list:
                for vtx in self.vertices:
                    writer.write(pack(
                        "<" + str(self.component_count) + c_t,
                        *vtx
                    ))
            else:
                writer.write(pack(
                        "<" + str(self.component_count*self.vertex_count) + c_t,
                        *self.vertices
                    ))
                # for i in range(0, len(self.vertices), self.component_count):
                #     writer.write(pack(
                #         "<" + str(self.component_count) + c_t,
                #         *self.vertices[i:i+self.component_count]
                #     ))
        elif self.encoding == 1:
            def sub(a:list, b:list):
                return tuple(x - y for x, y in zip(a, b))
            


            if type(self.vertices[0]) == list:
                for i in range(len(self.vertices)):
                    if i == 0:
                        vtx = self.vertices[i]
                    else:
                        vtx = sub(self.vertices[i], self.vertices[i-1])
                    writer.write(pack(
                        "<" + str(self.component_count) + c_t,
                        *vtx
                    ))
            else:
                for i in range(0, len(self.vertices), self.component_count):
                    if i == 0:
                        vtx = self.vertices[i:i+self.component_count]
                    else:
                        vtx = sub(
                            self.vertices[i:i+self.component_count],
                            self.vertices[i-self.component_count:i]
                        )
                    writer.write(pack(
                        "<" + str(self.component_count) + c_t,
                        *self.vertices[i:i+self.component_count]
                    ))

    def setFlat(self, vals:list|tuple, comp_size: int, comp_cnt: int, firstVtx: int = None, numVtx: int = None, scale = 1):    
        """
        Initializes VertexArray from flat array.
        """ 
        def clamp(v):
            max = (1 << (comp_size * 8 - 1)) - 1
            min = -(1 << (comp_size * 8 - 1))
            if v < min:
                print("Warning: VertexArray.setAny(): clamping {} to {}".format(v, min))
                v = min
            if v > max:
                print("Warning: VertexArray.setAny(): clamping {} to {}".format(v, max))
                v = max
            return round(v)
        

        if isinstance(vals[0], (list, tuple)):
            flat = []
            for v in vals:
                flat.extend(v)
        else:
            flat = vals
            
        self.component_size = comp_size
        self.component_count = comp_cnt
        self.vertices = []
        self.vertex_count = len(flat)//comp_cnt
        #self.vertices = vals
        #return
        start_vtx = 0 if firstVtx == None else firstVtx
        stop_vtx = start_vtx + len(flat) if numVtx == None else numVtx
        self.vertices = [*(clamp(v*scale) for v in flat[start_vtx * self.component_count:stop_vtx * self.component_count])]
        # for i in range(start_vtx * self.component_count,
        #                stop_vtx * self.component_count,
        #                ):#self.component_count):
        #     #print(vals[i:i+self.component_count])  
        #     self.vertices += [*(clamp(v*scale) for v in vals[i:i+self.component_count])]
