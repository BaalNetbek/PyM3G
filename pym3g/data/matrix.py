class Matrix:
    def __init__(self, elements = None):
        if len(elements) == 16 and type(elements) in (list, tuple):
            self.elements = list(elements)
        elif (type(elements) == type(Matrix)):
            # it's ugly but not important
            self.elements = list(elements.elements)
        elif elements is None:
            self = Matrix.identity()
        else:
            raise ValueError("Matrix must have 16 elements.")
        
    def __str__(self):
        return ('[\n' 
                + '\t' + str(self.elements[0:4]) + ',\n' 
                + '\t' + str(self.elements[4:8]) + ',\n' 
                + '\t' + str(self.elements[8:12]) + ',\n' 
                + '\t' + str(self.elements[12:16]) +
                ']')
        
    @staticmethod
    def identity():
        return Matrix((
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
            ))
    @staticmethod
    def identity_tuple(self):
        return ((
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ))
    