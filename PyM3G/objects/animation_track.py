"""Animation Track Class"""

from struct import unpack, pack
from PyM3G.util import obj2str, const2str, deref_from_file
from PyM3G.objects.object3d import Object3D
from PyM3G.objects.keyframe_sequence import KeyframeSequence
from PyM3G.objects.animation_controller import AnimationController


class AnimationTrack(Object3D):
    """
    Associates a KeyframeSequence with an AnimationController and an animatable
    property
    """
    # Properties (page 32 in documentation)
    ALPHA = 256
    AMBIENT_COLOR = 257
    COLOR = 258
    CROP = 259
    DENSITY = 260
    DIFFUSE_COLOR = 261
    EMISSIVE_COLOR = 262
    FAR_DISTANCE = 263
    FIELD_OF_VIEW = 264
    INTENSITY = 265
    MORPH_WEIGHTS = 266
    NEAR_DISTANCE = 267
    ORIENTATION = 268
    PICKABILITY = 269
    SCALE = 270
    SHININESS = 271
    SPECULAR_COLOR = 272
    SPOT_ANGLE = 273
    SPOT_EXPONENT = 274
    TRANSLATION = 275
    VISIBILITY = 276

    HAS_REFS = True

    def __init__(self):
        super().__init__()
        self.keyframe_sequence_idx = None
        self.keyframe_sequence: KeyframeSequence = None
        self.animation_controller_idx = None
        self.animation_controller: AnimationController = None
        self.property_id = None

    def __str__(self):
        return obj2str(
            "AnimationTrack",
            [
                ("Keyframe Sequence", self.keyframe_sequence_idx),
                ("Animation Controller", self.animation_controller_idx),
                ("Property ID", const2str(self.property_id) + " (%d)" % self.property_id),
            ],
        ) + super().inherited_str()

    def read(self, reader, objects=None):
        super().read(reader, objects)
        (self.keyframe_sequence_idx, self.animation_controller_idx, self.property_id) = unpack(
            "<3I", reader.read(12)
        )
        
        deref_from_file(self, "keyframe_sequence", KeyframeSequence, self.keyframe_sequence_idx, objects)
        deref_from_file(self, "animation_controller", AnimationController, self.animation_controller_idx, objects)
    #TODO upadate_ref

    def write(self, writer):
        super().write(writer)
        writer.write(pack(
            "<3I", 
            self.keyframe_sequence_idx, 
            self.animation_controller_idx, 
            self.property_id
            ))