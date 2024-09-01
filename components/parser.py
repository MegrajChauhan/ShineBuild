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
        self.nodes = []
        self.tokens: list[lexer.Token] = _l.token_list
        self.ind = -1
        self.length = len(self.tokens)
            
    def next(self):
        if self.ind >= self.length:
            return None
        self.ind+=1
        return self.tokens[self.ind]
    
    def parse(self):
        curr = self.next()
        while curr != None:
            match curr.type:
                case lexer.TokenType.SOURCE:
                    self.source()
                case lexer.TokenType.HEADER:
                    self.header()
            curr = self.next()
            
    
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
            if curr.type != lexer.TokenType.IDENTIFIER:
                die("Expected directory paths here and not keywords.", curr.line, log.SYNTAX_ERROR)
            paths.append(curr.val)
            tmp = curr
            curr = self.next()    
        self.nodes.append(nodes.Node(nodeK(paths)))
        