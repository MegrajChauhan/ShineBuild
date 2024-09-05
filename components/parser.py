from . import symtable as st
from . import lexer
from . import logmsg as log
from enum import Enum
from . import nodes

def die(msg, line, ret):
    log._log_(msg, line)
    exit(ret)

class ScopeType(Enum):
    GLOBAL = 1
    FOREACH = 2
    UNNAMED = 3
    IF, = 4
    ELSE = 5
    FOR = 6
    

class Scope:
    def __init__(self, _t: ScopeType, _parent = None):
        self._type = _t
        self.parent: Scope = _parent
        self.children: list[Scope] = []
        self.nodes: list[nodes.Node] = []
    
    def add_child(self, _scope):
        self.children.append(_scope)
    
class Parser:
    def __init__(self, _l:lexer.Lexer):
        _l.lex_all()
        self.scope = Scope(ScopeType.GLOBAL)
        self.nodes: list[nodes.Node]  = []
        self.tokens: list[lexer.Token] = _l.token_list
        self.ind = -1
        self.length = len(self.tokens)

    def next(self):
        self.ind+=1
        if self.ind >= self.length:
            return None
        return self.tokens[self.ind]

    def output(self):
        self.handle_dirs(nodes.NodeOutput)
        n = self.nodes.pop()
        _last: nodes.NodeOutput = n.node
        if len(_last.dir) > 1:
            die("The OUTPUT command cannot take more than one argument.", self.tokens[self.ind].line, log.SYNTAX_ERROR)
        self.nodes.append(n)
    
    def name(self):
        self.handle_dirs(nodes.NodeName)
        n = self.nodes.pop()
        _last: nodes.NodeName = n.node
        if len(_last.dir) > 1:
            die("The NAME command cannot take more than one argument.", self.tokens[self.ind].line, log.SYNTAX_ERROR)
        self.nodes.append(n)
    
    def header(self):
        self.handle_dirs(nodes.NodeHeader)
        
    # handle the source 
    def source(self):
        # The current token is SOURCE
        self.handle_dirs(nodes.NodeSource)
            
    def handle_dirs(self, nodeK):
        tmp =self.tokens[self.ind]
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a parenthesis.", tmp.line,log.SYNTAX_ERROR)
        if curr.type != lexer.TokenType.OPEN_PAREN:
            die("Expected a open parenthesis here.", curr.line, log.SYNTAX_ERROR)
        
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a directory path.", tmp.line,log.SYNTAX_ERROR)
        
        paths = []
        while curr.type != lexer.TokenType.CLOSE_PAREN:
            if curr == None:
                die("Unexpected EOF when expected a directory path.", tmp.line,log.SYNTAX_ERROR)
            if curr.type == lexer.TokenType.NEW_LINE:
                tmp = curr
                curr = self.next()
                continue
            if curr.type != lexer.TokenType.IDENTIFIER:
                die("Expected directory paths here and not keywords.", curr.line, log.SYNTAX_ERROR)
            paths.append(curr.val)
            tmp = curr
            curr = self.next()    
        self.nodes.append(nodes.Node(nodeK(paths)))

    def handle_final(self):
        tmp =self.tokens[self.ind]
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a parenthesis.", tmp.line,log.SYNTAX_ERROR)
        if curr.type != lexer.TokenType.OPEN_PAREN:
            die("Expected a open parenthesis here.", curr.line, log.SYNTAX_ERROR)
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a GROUP NAME.", tmp.line,log.SYNTAX_ERROR)
        
        grp_name = ""
        exe_name = ""
        while curr.type != lexer.TokenType.IDENTIFIER:
            if curr == None:
                die("Unexpected EOF when expected a GROUP NAME.", tmp.line,log.SYNTAX_ERROR)
            if curr.type == lexer.TokenType.NEW_LINE:
                tmp = curr
                curr = self.next()
                continue
            if curr.type != lexer.TokenType.IDENTIFIER:
                die("Expected GROUP NAME here and not keywords.", curr.line, log.SYNTAX_ERROR)
            tmp = curr
            curr = self.next()    
        grp_name = curr.val
        while curr.type != lexer.TokenType.IDENTIFIER:
            if curr == None:
                die("Unexpected EOF when expected a EXE NAME.", tmp.line,log.SYNTAX_ERROR)
            if curr.type == lexer.TokenType.NEW_LINE:
                tmp = curr
                curr = self.next()
                continue
            if curr.type != lexer.TokenType.IDENTIFIER:
                die("Expected EXE NAME here and not keywords.", curr.line, log.SYNTAX_ERROR)
            tmp = curr
            curr = self.next()    
        exe_name = curr.val
        while curr.type != lexer.TokenType.CLOSE_PAREN:
            if curr == None:
                die("Unexpected EOF when expected a CLOSE PARENTHESIS.", tmp.line,log.SYNTAX_ERROR)
            curr = self.next()
        self.nodes.append(nodes.Node(nodes.NodeFinal(grp_name, exe_name)))

    def handle_variables(self):
        tmp = self.tokens[self.ind]
        name_of_var = tmp.val
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a EQUALS.", tmp.line,log.SYNTAX_ERROR)
        if curr.type != lexer.TokenType.ASSIGN:
            die("Expected a '=' operator here.", curr.line, log.SYNTAX_ERROR)
        curr = self.next()
        expr = []
        while curr != None and curr.type != lexer.TokenType.NEW_LINE: 
            expr.append(curr)
            curr = self.next()
        if len(expr) == 0:
            die(f"Variable {name_of_var} has not been initialized.", tmp.line, log.SYNTAX_ERROR)
        self.nodes.append(nodes.Node(nodes.NodeVariable(name_of_var, nodes.Expression(expr))))

    def handle_foreach(self):
        nscope = Scope(ScopeType.FOREACH)
        tmp =self.tokens[self.ind]
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a parenthesis.", tmp.line,log.SYNTAX_ERROR)
        if curr.type != lexer.TokenType.OPEN_PAREN:
            die("Expected a open parenthesis here.", curr.line, log.SYNTAX_ERROR)
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a GROUP NAME.", tmp.line,log.SYNTAX_ERROR)
        
        inp_var = ""
        capture_var = ""
        while curr.type != lexer.TokenType.IDENTIFIER:
            if curr == None:
                die("Unexpected EOF when expected a VARIABLE.", tmp.line,log.SYNTAX_ERROR)
            if curr.type == lexer.TokenType.NEW_LINE:
                tmp = curr
                curr = self.next()
                continue
            if curr.type != lexer.TokenType.IDENTIFIER:
                die("Expected VARIABLE here and not keywords.", curr.line, log.SYNTAX_ERROR)
            tmp = curr
            curr = self.next()    
        inp_var = curr.val
        while curr.type != lexer.TokenType.IDENTIFIER:
            if curr == None:
                die("Unexpected EOF when expected a CAPTURE VARIABLE NAME.", tmp.line,log.SYNTAX_ERROR)
            if curr.type == lexer.TokenType.NEW_LINE:
                tmp = curr
                curr = self.next()
                continue
            if curr.type != lexer.TokenType.IDENTIFIER:
                die("Expected CAPTURE VARIABLE NAME here and not keywords.", curr.line, log.SYNTAX_ERROR)
            tmp = curr
            curr = self.next()    
        capture_var = curr.val
        while curr.type != lexer.TokenType.CLOSE_PAREN:
            if curr == None:
                die("Unexpected EOF when expected a CLOSE PARENTHESIS.", tmp.line,log.SYNTAX_ERROR)
            curr = self.next()
        scope_tmp = self.scope
        # Now to parse the scope itself
        self.handle_scope(nscope)
        self.nodes.append(nodes.Node(nodes.NodeForEach(inp_var, capture_var, nscope)))
        self.scope = scope_tmp

    def handle_for(self):
        nscope = Scope(ScopeType.FOR)
        tmp =self.tokens[self.ind]
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a parenthesis.", tmp.line,log.SYNTAX_ERROR)
        if curr.type != lexer.TokenType.OPEN_PAREN:
            die("Expected a open parenthesis here.", curr.line, log.SYNTAX_ERROR)
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a GROUP NAME.", tmp.line,log.SYNTAX_ERROR)
        
        _from = ""
        _to = ""
        _ind = ""
        while curr.type != lexer.TokenType.IDENTIFIER:
            if curr == None:
                die("Unexpected EOF when expected an INTEGER VALUE.", tmp.line,log.SYNTAX_ERROR)
            if curr.type == lexer.TokenType.NEW_LINE:
                tmp = curr
                curr = self.next()
                continue
            if curr.type != lexer.TokenType.IDENTIFIER:
                die("Expected INTEGER VALUE here and not keywords.", curr.line, log.SYNTAX_ERROR)
            tmp = curr
            curr = self.next()    
        _from = curr.val
        while curr.type != lexer.TokenType.IDENTIFIER:
            if curr == None:
                die("Unexpected EOF when expected a INTEGER VALUE.", tmp.line,log.SYNTAX_ERROR)
            if curr.type == lexer.TokenType.NEW_LINE:
                tmp = curr
                curr = self.next()
                continue
            if curr.type != lexer.TokenType.IDENTIFIER:
                die("Expected INTEGER VALUE here and not keywords.", curr.line, log.SYNTAX_ERROR)
            tmp = curr
            curr = self.next()    
        _to = curr.val
        while curr.type != lexer.TokenType.IDENTIFIER:
            if curr == None:
                die("Unexpected EOF when expected a INDEX VARIABLE.", tmp.line,log.SYNTAX_ERROR)
            if curr.type == lexer.TokenType.NEW_LINE:
                tmp = curr
                curr = self.next()
                continue
            if curr.type != lexer.TokenType.IDENTIFIER:
                die("Expected INDEX VARIABLE here and not keywords.", curr.line, log.SYNTAX_ERROR)
            tmp = curr
            curr = self.next()    
        _ind = curr.val
        while curr.type != lexer.TokenType.CLOSE_PAREN:
            if curr == None:
                die("Unexpected EOF when expected a CLOSE PARENTHESIS.", tmp.line,log.SYNTAX_ERROR)
            curr = self.next()
        scope_tmp = self.scope
        # Now to parse the scope itself
        self.handle_scope(nscope)
        self.nodes.append(nodes.Node(nodes.NodeFor(_from, _to, _ind, nscope)))
        self.scope = scope_tmp
    
    def handle_if(self):
        tmp =self.tokens[self.ind]
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expected a parenthesis.", tmp.line,log.SYNTAX_ERROR)
        if curr.type != lexer.TokenType.OPEN_PAREN:
            die("Expected a open parenthesis here.", curr.line, log.SYNTAX_ERROR)
        curr = self.next()
        if curr == None:
            die("Unexpected EOF when expecting an expression", self.tokens[self.length - 1].line, log.SYNTAX_ERROR)
        expr = []
        while curr != None and curr.type != lexer.TokenType.CLOSE_PAREN: 
            if curr.type == lexer.TokenType.NEW_LINE:
                continue
            expr.append(curr)
            curr = self.next()
        if curr == None:
            die("Unexpected EOF when expecting closing parenthesis.", self.tokens[self.length - 1].line, log.SYNTAX_ERROR)
        curr = self.next()
        scope_tmp = self.scope
        nscope = Scope(ScopeType.IF)
        self.handle_scope(nscope)
        self.nodes.append(nodes.Node(nodes.NodeIf(nodes.Expression(expr), nscope)))
        self.scope = scope_tmp
        
    def handle_else(self):
        scope_tmp = self.scope
        nscope = Scope(ScopeType.ELSE)
        self.handle_scope(nscope)
        self.nodes.append(nodes.Node(nodes.NodeElse(nscope)))
        self.scope = scope_tmp
        
    def handle_scope(self, scope: Scope):
        curr = self.next()
        while True:
            if curr != None and curr.type == lexer.TokenType.NEW_LINE:
                curr = self.next()
                continue
            if curr == None or curr.type != lexer.TokenType.OPEN_CURLY:
                die("Expected a open curly here.", curr.line, log.SYNTAX_ERROR)
            else:
                break
        curr = self.next()
        while True:
            if  curr == None:
                die("Unexpected EOF when the scope wasn't even terminated", self.tokens[self.length - 1].line, log.SYNTAX_ERROR)
            if curr.type == lexer.TokenType.CLOSE_CURLY:
                break
            match curr.type:
                case lexer.TokenType.NEW_LINE:
                    pass
                case lexer.TokenType.SOURCE:
                    self.source()
                case lexer.TokenType.HEADER:
                    self.header()
                case lexer.TokenType.OUTPUT:
                    self.output()
                case lexer.TokenType.NAME:
                    self.name()
                case lexer.TokenType.FINAL:
                    self.handle_final()
                case lexer.TokenType.IDENTIFIER:
                    self.handle_variables()
                case lexer.TokenType.OPEN_CURLY:
                    self.ind -= 1
                    nscope = Scope(ScopeType.UNNAMED)
                    self.handle_scope(nscope)
                    self.nodes.append(nodes.Node(nodes.NodeScope(nscope)))
                case lexer.TokenType.IF:
                    self.handle_if()
                case lexer.TokenType.ELSE:
                    self.handle_else()
            scope.nodes.append(self.nodes.pop())
            curr = self.next()            
        self.next()
    
    def parse(self):
        curr = self.next()
        while curr != None:
            match curr.type:
                case lexer.TokenType.NEW_LINE:
                    pass
                case lexer.TokenType.SOURCE:
                    self.source()
                case lexer.TokenType.HEADER:
                    self.header()
                case lexer.TokenType.OUTPUT:
                    self.output()
                case lexer.TokenType.NAME:
                    self.name()
                case lexer.TokenType.FINAL:
                    self.handle_final()
                case lexer.TokenType.IDENTIFIER:
                    self.handle_variables()
                case lexer.TokenType.FOREACH:
                    self.handle_foreach()
                case lexer.TokenType.OPEN_CURLY:
                    self.ind -= 1
                    scope = Scope(ScopeType.UNNAMED)
                    self.handle_scope(scope)
                    self.nodes.append(nodes.Node(nodes.NodeScope(scope)))
                    self.ind -= 1
                case lexer.TokenType.IF:
                    self.handle_if()
                case lexer.TokenType.ELSE:
                    # This below check right here is to make things easier later on
                    prev: nodes.Node = self.nodes[len(self.nodes) - 1]
                    if prev.get_kind() != nodes.NodeKind.IF:
                        die("An else statement without if is not allowed.", curr.line, log.SYNTAX_ERROR) 
                    self.handle_else()
            curr = self.next()            