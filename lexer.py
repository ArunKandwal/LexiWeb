# lexer.py

import re

# Define token patterns
TOKEN_SPECIFICATION = [
    ('NUMBER',   r'\d+(\.\d*)?'),         # Integer or decimal number
    ('ASSIGN',   r'='),                   # Assignment operator
    ('END',      r';'),                   # Statement terminator
    ('ID',       r'[A-Za-z_]\w*'),        # Identifiers
    ('OP',       r'[+\-*/]'),             # Arithmetic operators
    ('NEWLINE',  r'\n'),                  # Line endings
    ('SKIP',     r'[ \t]+'),              # Skip spaces and tabs
    ('MISMATCH', r'.'),                   # Any other character
]

# Define keywords
KEYWORDS = {'int', 'float', 'char', 'if', 'else', 'while', 'return'}

# Symbol table
symbol_table = {}

def tokenize(code):
    tokens = []
    line_num = 1
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'ID':
            if value in KEYWORDS:
                kind = 'KEYWORD'
            else:
                kind = 'ID'
                symbol_table[value] = {'type': 'identifier', 'line': line_num}
        elif kind == 'NEWLINE':
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character {value!r} on line {line_num}')
        tokens.append((kind, value))
    return tokens
