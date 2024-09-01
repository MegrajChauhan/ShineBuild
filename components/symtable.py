from enum import Enum

class Type(Enum):
    _GLOBAL_ = 0
    _LIST_ = 1
    _STR_ = 2

class Base:
    def __init__(self, _type) -> None:
        self._type = _type
    
    def get_type(self):
        return self._type

class List(Base):
    def __init__(self):
        super().__init__(Type._LIST_)
        self.count = 0
        self.values = []
    
    def append_val(self, val):
        self.count+=1
        self.values.append(val)
    
    def get_len(self):
        return self.count
    
    def get_all_val(self):
        return self.values if self.count != 0 else None

    def get_val(self,ind):
        return self.values[ind] if ind < self.count else None

class Value(Base):
    def __init__(self, val):
        super().__init__(Type._STR_)
        self.value = val # This will only ever be a string
    
    def get_len(self):
        return len(self.value)

    def get_value(self):
        return self.value

class Symtable:
    def __init__(self):
        self.table = {}
    
    def add_variable(self, key, val):
        if self.find(key) != None:
            return
        self.table += {key: val}
    
    def find(self, key):
        return self.table.get(key)
        