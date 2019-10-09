from src.FiniteAutomaton import FiniteAutomaton

class LexicalAnalyzer(FiniteAutomaton):
    # Settings
    __SEPARATORS   = [' ', '\n', '\t']
    __SYMBOL_TABLE = [] # List of dicts, each one with line, indentation_level, final_state and label
    __OUTPUT_TAPE = '$'
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
        # Getting important states
        initial_state = self.GetInitialState()
        error_state = self.GetErrorState()
        # Initializing
        token = ''
        state = initial_state
        line_count = 0
        # Reading lines
        for line in self.__SOURCE_CODE:
            line_count += 1
            identate = True
            identation = 0
            # Reading chars
            for char in line:
                # Getting identation
                if char != '\t':
                    identate = False
                elif identate:
                    identation += 1
                # Making the transition if the char is not a separator
                if char not in self.__SEPARATORS:
                    token += char
                    state = self.MakeTransition(state, char)
                # Handling the readed token
                elif token != '':
                    # Changing to error state if the token state is not final
                    if not self.IsFinal(state):
                        state = error_state
                    # Appending token to the output tape if it is recognized
                    else:
                        self.__OUTPUT_TAPE += token
                    # Appending token to the symbol table
                    self.__SYMBOL_TABLE.append({
                        'line': line_count,
                        'identation': identation,
                        'state': state,
                        'label': token
                    })
                    # Showing error message if necessary
                    if state == error_state:
                        print('Lexical error: "%s" in line %d:%d' %(token, line_count, i))
                    # Reseting token and state
                    token = ''
                    state = initial_state
        
        # Printing result
        print(self.__OUTPUT_TAPE)
        for line in self.__SYMBOL_TABLE:
            print(line)