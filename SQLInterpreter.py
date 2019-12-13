from src.Lexer import Lexer

lexical_analyzer = Lexer()

def interpret(query):
    output, symbol_table = lexical_analyzer.analyze(query)
    print(output)
    for symbol in symbol_table:
      print(symbol)