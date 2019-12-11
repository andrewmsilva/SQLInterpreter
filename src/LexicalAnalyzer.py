from src.FiniteAutomaton import FiniteAutomaton

class LexicalAnalyzer(FiniteAutomaton):
    # Settings
    __SEPARATORS   = [' ', '\n', '\t']
    # Files
    _SEPARATORS_FILE = 'separators.txt'
    
    def __init__(self):
        super().__init__()
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
        is_string = False
        for column in range(len(string)):
            char = string[column]
            # Making the transition if the char is not a separator
            if char not in self.__SEPARATORS:
                token += char
                state = self.makeTransition(state, char)
            # Handling the readed token
            elif token != '':
                # Raising lexical error if the token state is either not final or a error state
                if not self.isFinal(state) or state == error_state:
                    print('Lexical error in column %d'%column)
                # Appending token to the output tape if it is recognized
                else:
                    output += ' ' + token
                    symbol_table.append({
                        'column': column,
                        'state': state,
                        'label': token
                    })
                # Reseting token and state
                token = ''
                state = initial_state
            # Handling a possible token-separator
            if char in self.__SEPARATORS:
                separator_state = self.makeTransition(initial_state, char)
                if self.isFinal(separator_state) and separator_state != error_state:
                    output += ' ' + char
                    symbol_table.append({
                        'column': column,
                        'state': separator_state,
                        'label': char
                    })

        return output, symbol_table