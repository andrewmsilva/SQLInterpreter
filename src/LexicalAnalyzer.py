from src.FiniteAutomaton import FiniteAutomaton

class LexicalAnalyzer(FiniteAutomaton):
    # Settings
    __SEPARATORS   = [' ', '\n', '\t']
    # Files
    _SEPARATORS_FILE = 'separators.txt'
    
    def __init__(self):
        super().__init__(False)
        self.__loadSeparators()

    def __loadSeparators(self):
        try:
            file = open(self._INPUTS_FOLDER+'/'+self._SEPARATORS_FILE, 'r')
            for separator in file:
                separator = separator.replace('\n', '')
                self.__SEPARATORS.append(separator)
            file.close()
        except:
            pass

    def analyze(self, string):
        # Getting important states
        initial_state = self.getInitialState()
        error_state = self.getErrorState()
        # Initializing
        output = '$'
        symbol_table = []
        if string == '':
            return output, symbol_table
        if string[-1] != '\n':
            string += '\n'
        # Reading chars
        token = ''
        state = initial_state
        for column in range(len(string)):
            char = string[column]
            # Making the transition if the char is not a separator
            if char not in self.__SEPARATORS:
                token += char
                state = self.makeTransition(state, char)
            # Handling the readed token
            elif token != '':
                # Changing to error state if the token state is not final
                if not self.isFinal(state):
                    state = error_state
                # Appending token to the output tape if it is recognized
                else:
                    output += ' ' + token
                # Appending token to the symbol table
                symbol_table.append({
                    'column': column,
                    'state': state,
                    'label': token
                })
                # Showing error message if necessary
                if state == error_state:
                    print('Lexical error in %d from %s'%(column, string))
                # Reseting token and state
                token = ''
                state = initial_state
        return output, symbol_table