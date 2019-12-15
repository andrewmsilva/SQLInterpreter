from src.Lexer import Lexer
from src.Parser import Parser

lexer = Lexer()
parser = Parser()

def interpret(query):
    output, symbol_table = lexer.analyze(query)
    parser.parse(output)
    