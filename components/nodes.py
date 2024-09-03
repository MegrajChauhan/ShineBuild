from enum import Enum

class NodeKind(Enum):
    COMMAND_SOURCE = 1
    COMMAND_HEADER = 2
    COMMAND_OUTPUT = 3
    COMMAND_NAME = 4
    COMMAND_FINAL = 5
    VARIABLE = 6
    COMMAND_FOREACH = 7

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
        self.kind = NodeKind.COMMAND_HEADER

class NodeOutput(NodeBase):
    def __init__(self, dir):
        super().__init__(NodeKind.COMMAND_OUTPUT)
        self.dir = dir
    
    def get_output_dir(self):
        return self.dir

class NodeName(NodeOutput):
    def __init__(self, name):
        super().__init__(name)
        self.kind = NodeKind.COMMAND_NAME
    
    def get_name(self):
        return self.get_output_dir()

class NodeFinal(NodeBase):
    def __init__(self, grp_name, exe):
        super().__init__(NodeKind.COMMAND_FINAL)
        self.grp = grp_name
        self.exe = exe
    
    def get_grp(self):
        return self.grp
   
    def get_exe(self):
        return self.exe

# During parsing, expressions are nothing but a list of tokens
# It is okay for them to not make sense
# To this parser, everything after '=' is part of the expression until the new line
# It is the expression parser's job to make sense of those tokens
class Expression:
    def __init__(self, toks) -> None:
        self.tok_list = toks
    
    def add(self, tok):
        self.tok_list.append(tok)

class NodeVariable(NodeBase):
    def __init__(self, name, expr: Expression):
        super().__init__(NodeKind.VARIABLE)
        self.expr = expr
        self.name = name
    
    def get_expr(self):
        return self.expr

class NodeForEach(NodeBase):
    def __init__(self, var_name, collecting_var, expr):
        super().__init__(NodeKind.COMMAND_FOREACH)
        self.var_name = var_name
        self.collecting_var = collecting_var
        self.expr = expr

class Node:
    def __init__(self, n):
        self.node = n
    
    def get(self):
        return self.node
