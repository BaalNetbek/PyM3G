class color:
    def __init__ (self, color: list[int]):
        if len(color) == 4:
            self.rgb = color[:3]
            self.a = color[3]
        elif len(color) == 3:
            self.rgb = color 
        else:
            self.rgb = None
            raise ValueError("Color must have 3 (RGB) or 4 elements (RGBA).")
