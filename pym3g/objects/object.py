"""Object Class"""


class ObjectM3G:
    """
    Abstract parent class to all M3G objects
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