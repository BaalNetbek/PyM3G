"""Skinned Mesh Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, deref_from_file, verify_ref
from PyM3G.objects.mesh import Mesh
from PyM3G.objects.group import Group
from PyM3G.objects.transformable import Transformable

class SkinnedMesh(Mesh):
    """
    A scene graph node that represents a skeletally animated polygon mesh
    """

    HAS_REFS = True
    
    def __init__(self):
        super().__init__()
        self.skeleton_idx = None
        self.skeleton: Group = None
        self.transform_reference_count = None
        self.transform_nodes = []
        self.transform_nodes_idx = []
        self.first_vertex = []
        self.vertex_count = []
        self.weight = []

    def __str__(self):
        return obj2str(
            "SkinnedMesh",
            [
            ("Skeleton", self.skeleton_idx),
            ("Transform Reference Count", self.transform_reference_count),
            ("Transform Node", "Array of {0} items".format(len(self.transform_nodes))),
            ("First Vertex", "Array of {0} items".format(len(self.first_vertex))),
            ("Vertex Count", "Array of {0} items".format(len(self.vertex_count))),
            ("Weight", "Array of {0} items".format(len(self.weight))),
            ],
        ) + super(SkinnedMesh, self).inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.skeleton_idx, self.transform_reference_count = unpack("<II", reader.read(8))
        for _ in range(self.transform_reference_count):
            (transform_nodes_idx, first_vertex, vertex_count, weight) = unpack(
                "<3Ii", reader.read(16)
            )
            self.transform_nodes_idx.append(transform_nodes_idx)
            self.first_vertex.append(first_vertex)
            self.vertex_count.append(vertex_count)
            self.weight.append(weight)
        deref_from_file(self, "skeleton", Group, self.skeleton_idx, objects)
        deref_from_file(self, "transform_nodes", Transformable, self.transform_nodes_idx, objects)

    def update_ref(self, objects):
            super().update_ref(objects) 
            self.transform_nodes_idx = []
            self.skeleton_idx = 0
            child_idx = []
            this_idx = 0
            
            # No, not I came up with this a-intelligent optimization
            obj_to_idx = {o: i + 1 for i, o in enumerate(objects)}
            if self in obj_to_idx:
                this_idx = obj_to_idx[self]

            if self.skeleton and self.skeleton in obj_to_idx:
                self.skeleton_idx = obj_to_idx[self.skeleton]
                child_idx.append(self.skeleton_idx)
                
            # Iterate through transform_nodes to preserve matching order of arrays. 
            # This may couse trouble, but seems fine. TODO test, maybe add dataclass transformNode properties.
            for tn in self.transform_nodes:
                if tn in obj_to_idx:
                    idx = obj_to_idx[tn]
                    self.transform_nodes_idx.append(idx)
                    child_idx.append(idx)
                else:
                    self.transform_nodes_idx.append(0)
                    
            verify_ref(self, this_idx, child_idx)


    def write(self, writer):
        lengths = {
            len(f) for f in (
                self.transform_nodes, self.transform_nodes_idx,
                self.first_vertex, self.vertex_count, self.weight
            )
        }
        if ({self.transform_reference_count} != lengths):
            print("Warning: SkinnedMesh.write(): transform_reference_count mismatches object's data.")
            if len(lengths) == 1:
                new_count = list(lengths)[0]
                print("Updated transform_reference_count: {}->{}".format(self.transform_reference_count, new_count))
                self.transform_reference_count = new_count
            else:
                print("Error: SkinnedMesh.write(): transform ref. data arrays' lengths mismatch:")
                print("\tlen(self.transform_nodes){}".format(len(self.transform_nodes)))
                print("\tlen(self.transform_nodes_idx){}".format(len(self.transform_nodes_idx)))
                print("\tlen(self.first_vertex){}".format(len(self.first_vertex)))
                print("\tlen(self.vertex_count){}".format(len(self.vertex_count)))
                print("\tlen(self.weight){}".format(len(self.weight)))
            
        #raise(Exception("%s.write() not implemented" % type(self).__name__))
        super().write(writer)
        writer.write(pack("<I", self.skeleton_idx))
        writer.write(pack("<I", self.transform_reference_count))
        for i in range(self.transform_reference_count):
            writer.write(pack("<I", self.transform_nodes_idx[i]))
            writer.write(pack("<I", self.first_vertex[i]))
            writer.write(pack("<I", self.vertex_count[i]))
            writer.write(pack("<i", self.weight[i]))
      