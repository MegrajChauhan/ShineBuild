from enum import Enum

class NodeKind(Enum):
    COMMAND_SOURCE = 1

class NodeBase:
    def __init__(self, kind: NodeKind):
        self.kind = kind
        
    def get_kind(self):
        return self.kind

class NodeSource(NodeBase):
    def __init__(self, dirs):
        super().__init__(NodeKind.COMMAND_SOURCE)
        self.dirs = dirs
    
    def get_dirs(self):
        return self.dirs

class NodeHeader(NodeSource):
    def __init__(self, dirs):
        super().__init__(dirs)    

class Node:
    def __init__(self, n):
        self.node = n
    
    def get(self):
        return self.node
