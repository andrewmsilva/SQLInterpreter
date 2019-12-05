from src.LexicalAnalyzer import LexicalAnalyzer

lexical_analyzer = LexicalAnalyzer()

def interpret(query):
    output, symbol_table = lexical_analyzer.analyze(query)
    print(output)
    for symbol in symbol_table:
      print(symbol)