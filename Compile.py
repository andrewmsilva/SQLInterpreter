from src.LexicalAnalyzer import LexicalAnalyzer

symbol_table = LexicalAnalyzer('the.game')
if symbol_table is None:
    print('\nAborted!')