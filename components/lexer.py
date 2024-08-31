import os
import pathlib as _pl
import logmsg as log
from enum import Enum

class TokenType(Enum):
    IDENTIFIER = 1
    OPEN_PAREN = 2
    CLOSE_PAREN = 3
    EQUALS_TO = 4 # ==
    ASSIGN = 5    # =
    DOT = 6
    PLUS_EQUAL = 7 # +=
    OPEN_CURLY = 8
    CLOSE_CURLY = 9

class Token:
    def _init_(self, type: TokenType, val: str):
        self.type = type
        self.val = val

class Lexer:
    def _init_(self,_path):
        log._FPATH_ = _path
        self.path = _path
        self.col = 0
        self.line = 0
        self.content = None
        self.offset = 0
        self.confirm_inp_file() # if this returns then it is okay
    
    def curr(self):
        return self.content[self.offset]
    
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
        self.col += 1
        self.offset += 1
        if self.curr() == '\n':
            self.line += 1
            self.col = 0
    
    def peek(self, _peek_by):
        return self.content[self.offset + _peek_by] if (self.offset + _peek_by) < len(self.content) else '\0'

    def next_token(self):
        tok = Token()
        



