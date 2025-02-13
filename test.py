import sys
import os
import traceback
import time
import subprocess

# Import everything from interpreter and lexer
from interpreter import *
from lexer import *

with open("code.at", "r") as f:
    lexer = Lexer(f.read())
    f.close()



tokens = lexer.tokenize()
print(tokens, end="\n\n\n")

inter = Interpreter()
inter.interpret(tokens)