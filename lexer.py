import ply.lex as lex

tokens = [
    'ID', 'NUMBER', 'ASSIGN', 'SEMI',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'GT', 'LT', 'GE', 'LE', 'EQ', 'NE',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE'
] + ['INT', 'FLOAT', 'IF', 'RETURN']

reserved = {
    'int': 'INT',
    'float': 'FLOAT',
    'if': 'IF',
    'return': 'RETURN'
}

t_ASSIGN = r'='
t_SEMI = r';'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_GT = r'>'
t_LT = r'<'
t_GE = r'>='
t_LE = r'<='
t_EQ = r'=='
t_NE = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_ignore = ' \t'

def t_ID(t):
    r'[A-Za-z_]\w*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()
