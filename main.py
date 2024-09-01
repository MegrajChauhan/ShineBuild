"""
It has been a long time since I last used Python for a project so this Build System will be written in Python
SB = Shine Build
I just randomly chose the name based on the lyrics I heard just now.
Song- Belong Together by Mark Ambor
"""

"""
 The way that the entire system works is like an interpreter.
 The script is parsed and converted into nodes which are then tranversed
 to get that specific thing done
"""

from components import lexer

l = lexer.Lexer("test/test.sb")
l.lex_all()

for t in l.token_list:
    print(f"{t.type} {t.val} {t.line} {t.col}")