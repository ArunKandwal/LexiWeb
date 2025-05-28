import ply.yacc as yacc
from lexer import tokens, lexer

class Node:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []

    def to_graphviz(self, dot=None, parent=None, counter=[0]):
        import graphviz
        if dot is None:
            dot = graphviz.Digraph()
        my_id = str(counter[0])
        counter[0] += 1
        dot.node(my_id, self.name)
        if parent is not None:
            dot.edge(parent, my_id)
        for child in self.children:
            if isinstance(child, Node):
                child.to_graphviz(dot, my_id, counter)
            else:
                child_id = str(counter[0])
                counter[0] += 1
                dot.node(child_id, str(child))
                dot.edge(my_id, child_id)
        return dot

def p_program(p):
    '''program : program statement
               | statement'''
    p[0] = Node("Program", p[1:])

def p_statement_declaration(p):
    '''statement : INT ID SEMI
                 | FLOAT ID SEMI
                 | INT ID ASSIGN expression SEMI
                 | FLOAT ID ASSIGN expression SEMI'''
    if len(p) == 4:
        p[0] = Node("Declaration", [p[1], p[2]])
    else:
        p[0] = Node("DeclarationInit", [p[1], p[2], "=", p[4]])


def p_statement_assignment(p):
    'statement : ID ASSIGN expression SEMI'
    p[0] = Node("Assignment", [p[1], "=", p[3]])

def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN block'
    p[0] = Node("If", [p[3], p[5]])

def p_statement_return(p):
    'statement : RETURN expression SEMI'
    p[0] = Node("Return", [p[2]])

def p_function_definition(p):
    'statement : INT ID LPAREN RPAREN block'
    p[0] = Node("Function", [p[2], p[5]])

def p_block(p):
    'block : LBRACE program RBRACE'
    p[0] = Node("Block", [p[2]])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression GT expression
                  | expression LT expression
                  | expression GE expression
                  | expression LE expression
                  | expression EQ expression
                  | expression NE expression'''
    p[0] = Node(p[2], [p[1], p[3]])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = Node(str(p[1]))

def p_expression_id(p):
    'expression : ID'
    p[0] = Node(p[1])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

def parse(code):
    return parser.parse(code, lexer=lexer)
