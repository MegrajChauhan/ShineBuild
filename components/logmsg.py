_FPATH_ = None

def _log_(msg, line):
    print(f"{_FPATH_}: In line {line}: {msg}")

def _note_(msg):
    print(f"Note: {msg}")
    
# Return value interpretation
FILE_NOT_EXISTS = 1
FILE_A_DIR = 2
UNKNOWN_TOK = 3
SYNTAX_ERROR = 4