class vector3D:
    def __init__(self, xyz):
        if len(xyz) != 3:
            raise ValueError("Vector3D has to be initialized with 3 elements list.")
        self.xyz = xyz