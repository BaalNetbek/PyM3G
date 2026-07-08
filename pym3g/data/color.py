class Color:
    
    def __init__ (self, color: list[int] = None):
        if len(color) == 4:
            self.rgb = list(color[:3])
            self.a = color[3]
        elif len(color) == 3:
            self.rgb = color
            self.a = None 
        else:
            self.rgb = None
            self.a = None
            raise ValueError("Color must have 3 (RGB) or 4 elements (RGBA).")
        
    def supports_true_color(self) -> bool:
        """Return True if ANSI colors are supported (Linux, Git Bash, Windows Terminal)."""
        import os
        import platform
        system = platform.system()
        if system == "Linux":
            return True
        if "MSYSTEM" in os.environ:  
            return True
        return False

    def __str__(self):
        if self.rgb is None:
            return "Not initialized" 
        return ("R:%d G:%d B:%d "% (self.rgb[0], self.rgb[1], self.rgb[2])  +
                (("A:%d "%self.a) if self.a is not None else "") +
                # print the color in linux termial
                ("\033[48;2;{0};{1};{2}m".format(*self.rgb[:3]) + "  \033[0m") if self.supports_true_color() else "{0}, {1}, {2}".format(*self.rgb[:3]))
    
    def to_list(self, len=3):
        """ Takes argument len=3 for returning RGB and len=4 for RGBA """
        if self.rgb == None:
            raise Exception("Reading Color.rgb that is None")        
        if len == 4:
            if self.a != None:
                return list(self.rgb + [self.a,])
            return list(self.rgb + [255,]) 
        if len == 3:
            return list(self.rgb)
        raise Exception("Color.to_list(): Invalid argument len = {}. Expected 4 or 3 (default)".format(len))  