from . import symtable as st
from . import lexer
from . import logmsg as log
from enum import Enum
from . import nodes

def die(msg, line, ret):
    log._log_(msg, line)
    exit(ret)

class Parser:
    def __init__(self, _l: lexer.Lexer) -> None:
        _l.lex_all()
        self.nodes = []
        self.tokens: list[lexer.Token] = _l.token_list
        self.ind = -1
        self.length = len(self.tokens)
        self.append_to_last = False # For Nodes such as foreach
            
    def next(self):
        self.ind+=1
        if self.ind >= self.length:
            return None
        return self.tokens[self.ind]
    
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
                
            curr = self.next()
            
    
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
        pass