import pathlib as _pl
from . import logmsg as log
from enum import Enum

opers = "(){=}+."

class TokenType(Enum):
    NEW_LINE = 0
    IDENTIFIER = 1
    OPEN_PAREN = 2
    CLOSE_PAREN = 3
    EQUALS_TO = 4 # ==
    ASSIGN = 5    # =
    DOT = 6
    OPEN_CURLY = 8
    CLOSE_CURLY = 9
    PLUS = 10
    SOURCE = 11
    HEADER = 12
    OUTPUT = 13
    NAME = 14
    FINAL = 15
    IF = 16
    LEN = 17
    TRUE = 18
    FALSE  = 19
    NULL = 20
    FOREACH = 21
    ELSE = 23
    GROUP = 24
    PROGRAM = 25
    FLAGS = 26
    TYPE = 27
    STATIC = 28
    SHARED = 29
    FOR = 30
    ECHO = 31
    

oper_iden = {
    '=': TokenType.ASSIGN,
    '==': TokenType.EQUALS_TO,
    '+': TokenType.PLUS,
    '(': TokenType.OPEN_PAREN,
    ')': TokenType.CLOSE_PAREN,
    '{': TokenType.OPEN_CURLY,
    '}': TokenType.CLOSE_CURLY,
    '.': TokenType.DOT
    }

key_iden = {
    'source': TokenType.SOURCE,
    'header': TokenType.HEADER,
    'output' : TokenType.OUTPUT,
    'name': TokenType.NAME,
    'final': TokenType.FINAL,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'len' : TokenType.LEN,
    'foreach': TokenType.FOREACH,
    'for': TokenType.FOR,
    'echo': TokenType.ECHO,
    'group': TokenType.GROUP,
    'program': TokenType.PROGRAM,
    'flags': TokenType.FLAGS,
    'type': TokenType.TYPE,
    'static': TokenType.STATIC,
    'shared': TokenType.SHARED,
    "NULL": TokenType.NULL
}

class Token:
    def __init__(self, type: TokenType, line, col_st, val: str = None, ):
        self.type = type
        self.val = val
        self.line = line
        self.col = col_st

class Lexer:
    def __init__(self,_path):
        log._FPATH_ = _path
        self.path = _path
        self.col = 0
        self.line = 1
        self.content = None
        self.offset = 0
        self.token_list = []
        self.confirm_inp_file() # if this returns then it is okay
        self.content += '\0'
        self.curr = self.content[self.offset]
        self.length = len(self.content)
    
    def confirm_inp_file(self):
        _p = _pl.Path(self.path)
        if not _p.exists():
            log._note_(f"The file {self.path} doesn't exist.")
            exit(log.FILE_NOT_EXISTS)
        if _p.is_dir():
            log._note_(f"The file {self.path} is not a file but a directory")
            exit(log.FILE_A_DIR)
        self.content = _p.read_text()
    
    def next(self):
        if self.curr == '\n':
            self.line += 1
            self.col = 0
        else:
            self.col += 1
        self.offset += 1
        if self.offset >= self.length:
            return
        self.curr = self.content[self.offset]
    
    def peek(self, _peek_by):
        return self.content[self.offset + _peek_by] if (self.offset + _peek_by) < len(self.content) else '\0'

    # identify the token and then add
    def identify_key(self, value):
        if key_iden.get(value) != None:
            return key_iden[value]
        else:
            return TokenType.IDENTIFIER

    # To make things easier, we will just lex everything at once
    def lex_all(self):
        length = len(self.content)
        while self.offset < length:
            line = self.line
            col = self.col
            if self.curr == '\0':
                break
            if self.curr in opers:
                _token = self.curr
                self.next()
                if self.curr in opers:
                    match _token:
                        case '+':
                            if self.curr == '=':
                                _token += self.curr
                                self.next()
                        case '=':
                            if self.curr == '=':
                                _token += self.curr
                                self.next()
                self.token_list.append(Token(oper_iden[_token], line, col))
            elif self.curr == '@':
                while self.curr != '\n' and self.offset < length:
                    self.next()
            elif self.curr in " \n\t\r\f":
                while self.curr in " \n\t\r\f":
                    if self.curr == '\n':
                        self.token_list.append(Token(TokenType.NEW_LINE, line, col))
                    self.next()                        
            else:
                _tok = self.curr
                self.next()
                while self.curr not in " \n\t\r\f" and self.offset < length and self.curr not in opers:
                    _tok += self.curr
                    self.next()
                _type = self.identify_key(_tok)
                self.token_list.append(Token(_type, line, col, _tok if _type == TokenType.IDENTIFIER else None))
                
                
            
        



