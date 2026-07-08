"""Utility functions"""

_constants = {
    2: "ANTIALIAS",
    4: "DITHER",
    8: "TRUE_COLOR",
    16: "OVERWRITE",
    32: "BORDER",
    33: "REPEAT",
    48: "GENERIC",
    49: "PARALLEL",
    50: "PERSPECTIVE",
    64: "ALPHA",
    65: "ALPHA_ADD",
    66: "MODULATE",
    67: "MODULATE_X2",
    68: "REPLACE",
    80: "EXPONENTIAL",
    81: "LINEAR",
    96: "ALPHA",
    97: "LUMINANCE",
    98: "LUMINANCE_ALPHA",
    99: "RGB",
    100: "RGBA",
    125: "NONSTANDARD_IMAGE", # non standard
    128: "AMBIENT",
    129: "DIRECTIONAL",
    130: "OMNI",
    131: "SPOT",
    144: "NONE",
    145: "ORIGIN",
    146: "X_AXIS",
    147: "Y_AXIS",
    148: "Z_AXIS",
    160: "CULL_BACK",
    161: "CULL_FRONT",
    162: "CULL_NONE",
    164: "SHADE_FLAT",
    165: "SHADE_SMOOTH",
    168: "WINDING_CCW",
    169: "WINDING_CW",
    176: "LINEAR",
    177: "SLERP",
    178: "SPLINE",
    179: "SQUAD",
    180: "STEP",
    192: "CONSTANT",
    193: "LOOP",
    208: "FILTER_BASE_LEVEL",
    209: "FILTER_LINEAR",
    210: "FILTER_NEAREST",
    224: "FUNC_ADD",
    225: "FUNC_BLEND",
    226: "FUNC_DECAL",
    227: "FUNC_MODULATE",
    228: "FUNC_REPLACE",
    240: "WRAP_CLAMP",
    241: "WRAP_REPEAT",
    256: "ALPHA",
    257: "AMBIENT_COLOR",
    258: "COLOR",
    259: "CROP",
    260: "DENSITY",
    261: "DIFFUSE_COLOR",
    262: "EMISSIVE_COLOR",
    263: "FAR_DISTANCE",
    264: "FIELD_OF_VIEW",
    265: "INTENSITY",
    266: "MORPH_WEIGHTS",
    267: "NEAR_DISTANCE",
    268: "ORIENTATION",
    269: "PICKABILITY",
    270: "SCALE",
    271: "SHININESS",
    272: "SPECULAR_COLOR",
    273: "SPOT_ANGLE",
    274: "SPOT_EXPONENT",
    275: "TRANSLATION",
    276: "VISIBILITY",
    1024: "AMBIENT",
    2048: "DIFFUSE",
    4096: "EMISSIVE",
    8192: "SPECULAR",
}

def obj2str(obtype, values):
    """Build a string representation of an object"""
    outstr = obtype+":\n"
    for item in values:
        outstr += "\t"+str(item[0])+": "+str(item[1])+"\n"
    return outstr


def const2str(const_id):
    """Return a string representing a constant value"""
    return _constants.get(const_id)


def deref_from_file(this: object, attr_name: str, attr_type: type, idx: int, objects: list):
    """Sets a reference from the objects list by index"""
    if objects is None:
        print("deref_from_file() failed with arg objects being None")
        return
    if objects is []:
        return
    val = None
    if not isinstance(idx, (list, tuple)):
        idx = (idx,)
    else:
        val = []
    for ix in idx:
        if ix > len(objects):
            raise IndexError("IndexError: Tried to derefence {} with ObjectIndex = {} from objects list of {} elemnts".format(attr_name, ix, len(objects)))
        if ix == 0:
            val = None
        else:
            if ix - 1 == len(objects):
                ref = this
            else:
                ref = objects[ix - 1]
            if not isinstance(ref, attr_type):
                raise TypeError("Expected {}, got {} in object {}".format(attr_type.__name__, type(ref).__name__, ix))
            if isinstance(val, list):
                val.append(ref)
            else:
                val = ref
    setattr(this, attr_name, val)

def verify_ref(this: object, this_idx: int, child_idx: list[int]):
    for ci in child_idx:
            if ci >= this_idx:
                raise(IndexError("{}.update_ref() ERROR: Child of object with idx {} has child {} serialized after itself.".format(type(this).__name__, this_idx, ci)))
            
def fishlabs_deobfuscate(data):
    """
    From j2me-preservation/MascotCapsule
    https://github.com/j2me-preservation/MascotCapsule/blob/master/tools/fishlabs_obfuscation.py
    """
    length = len(data)
    data = bytearray(data)
    if length < 100:
        var5 = 10 + length % 10
    elif length < 200:
        var5 = 50 + length % 20
    elif length < 300:
        var5 = 80 + length % 20
    else:
        var5 = 100 + length % 50
    for i in range(var5):
        var7 = data[i]
        data[i] = data[length - i - 1]
        data[length - i - 1] = var7
    return bytes(data)