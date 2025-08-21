"""Object Class"""


class Object:
    """
    Abstract parent class to all objects
    """

    def __init__(self):
        pass

    def __str__(self):
        return ""
    
    def read(self, reader, objects):
        pass

    def update_ref(self, objects):
        pass

    def write(self, writer):
        pass