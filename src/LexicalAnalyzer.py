from src.FiniteAutomaton import FiniteAutomaton

class LexicalAnalyzer(FiniteAutomaton):
    # Settings
    __SEPARATORS   = [' ', '\n', '\t']
    __SYMBOL_TABLE = [] # List of dicts, each one with line, indentation_level, final_state and label
    __SOURCE_CODE  = None
    # Files
    _SEPARATORS_FILE = 'separators.txt'
    
    def __init__(self, source_code):
        super().__init__(False)
        # Load dependencies
        self.__LoadSeparators()
        if not self.__LoadSourceCode(source_code):
            return None
        # Analyze source code
        try:
            self.__Analyze()
            return self.__SYMBOL_TABLE
        except Exception as e:
            print(e)
            return None

    def __LoadSeparators(self):
        try:
            file = open(self._INPUTS_FOLDER+'/'+self._SEPARATORS_FILE, 'r')
            for separator in file:
                separator = separator.replace('\n', '')
                self.__SEPARATORS.append(separator)
            file.close()
        except:
            pass
    
    def __LoadSourceCode(self, source_code):
        try:
            self.__SOURCE_CODE = open(source_code, 'r')
            return True
        except:
            return False

    def __Analyze(self):
        """
            OVERWRITE THE CODE BELOW WITH THE TRUE LEXICAL ANALYZER,
            WICH NEED TO READ EACH LINE AND EACH CHAR OF self.__SOURCE_CODE
            AND BUILD THE SYMBOL TABLE
        """
        initial_state = self.GetInitialState()
        error_state = self.GetErrorState()
        while True:
            token = input('enter a token: ')
            state = initial_state
            for char in token:
                state = self.MakeTransition(state, char)

            if state == error_state or not self.IsFinal(state):
                print('Lexical error! State:', state)
            else:
                print('Correct! State:', state)