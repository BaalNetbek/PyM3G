"""Morphing Mesh Class"""

from struct import unpack, pack
from pym3g.util import obj2str, deref_from_file, verify_ref
from pym3g.objects.mesh import Mesh
from pym3g.objects.vertex_buffer import VertexBuffer


class MorphingMesh(Mesh):
    """
    A scene graph node that represents a vertex morphing polygon mesh
    """

    HAS_REFS = True

    def __init__(self):
        super().__init__()
        self.morph_targets_count: int = None
        self.morph_targets_idx: list[int] = []
        self.morph_targets: list[VertexBuffer] = []
        self.initial_weights: list[int] = []

    def __str__(self):
        return obj2str(
            "MorphingMesh",
            [
                ("Morph Target Count", self.morph_targets_count),
                ("Morph Target", "Array of {0} items".format(len(self.morph_targets_idx))),
                ("Initial Weight", "Array of {0} items".format(len(self.initial_weights))),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        self.morph_targets_count = unpack("<I", reader.read(4))
        for _ in range(self.morph_targets_count):
            morph_target, initial_weight = unpack("<If", 8)
            self.morph_targets_idx.append(morph_target)
            self.initial_weights.append(initial_weight)
        
        deref_from_file(self, "morph_target", VertexBuffer, self.morph_targets_idx, objects)

    def update_ref(self, objects):
            super().update_ref(objects) 
            self.morph_targets_idx = []
            child_idx = []
            this_idx = 0
            
            obj_to_idx = {o: i + 1 for i, o in enumerate(objects)}
            if self in obj_to_idx:
                this_idx = obj_to_idx[self]
            
            for mt in self.morph_targets:
                if mt in obj_to_idx:
                    idx = obj_to_idx[mt]
                    self.morph_targets_idx.append(idx)
                    child_idx.append(idx)
                else:
                    self.morph_targets_idx.append(0)
                    
            verify_ref(self, this_idx, child_idx)


    def write(self, writer):
        lengths = {
            len(f) for f in (
                self.morph_targets, self.morph_targets_idx,
                self.initial_weights
            )
        }
        if ({self.morph_targets_count} != lengths):
            print("Warning: MorphingMesh.write(): morph_targets_count mismatches object's data.")
            if len(lengths) == 1:
                new_count = list(lengths)[0]
                print("Updated morph_targets_count: {}->{}".format(self.morph_targets_count, new_count))
                self.morph_targets_count = new_count
            else:
                print("Error: MorphingMesh.write(): morphing targets data arrays' lengths mismatch:")
                print("\tlen(self.morph_targets){}".format(len(self.morph_targets)))
                print("\tlen(self.morph_targets_idx){}".format(len(self.morph_targets_idx)))
                print("\tlen(self.initial_weights){}".format(len(self.initial_weights)))

        super().write(writer)
        writer.write(pack("<I", self.morph_targets_count))
        for i in range(self.morph_targets_count):
            writer.write(
                pack("<If", 
                    self.morph_targets_idx[i],
                    self.initial_weights[i]
                )
            )
      