class ObjectIndex:
    
    def __init__ (self, obj_idx=None, abs_idx = None):
        if (obj_idx != None and obj_idx >= 0 and abs_idx == None):
            self.object_index = obj_idx
            if obj_idx > 0:
                self.absolute_index = obj_idx - 1
            else:
                self.absolute_index = None
        elif (abs_idx != None and abs_idx >= 0 and obj_idx == None):
           self.absolute_index = abs_idx
           self.object_index = abs_idx + 1
        elif (abs_idx != None and obj_idx != None and abs_idx >= 0 and abs_idx +1 == obj_idx):
            self.absolute_index = abs_idx
            self.object_index = obj_idx
        else:
            raise Exception("ObjectIndex.__init__() invalid arguments obj_idx: {}, abs_idx: {}.".format(obj_idx, abs_idx))
        
    def __str__(self):
        if self.absolute_index == None or self.absolute_index < 0 or self.object_index == None or self.object_index < 1:
            return "NULL_REFERENCE"
        else:
            return str(self.object_index)
        
    