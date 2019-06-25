class FiniteAutomaton(object):
    # Presets
    __INITIAL_STATE = '<S>'
    __ERROR_STATE   = '<error>'
    __FIRST_STATE   = '<A>'
    __IS_FINAL      = 'final'
    __UNION         = '¬'
    __ALPHABET      = []
    __FA            = {}

    def __init__(self, file):
        # 1th and 2nd steps: read file with tokens and regular 
        # grammatics to build a non-deterministic finite automaton
        self.__BuildByFile(file)

        # 3rd step: remove epslon transitions
        self.__RemoveEpslon()

        # 4th step: determinize finite automaton
        self.__Determinize()

        # 5th step: remove unreacheble and dead states
        self.__RemoveUnreacheble()

        # 6th step: map unmapped transitions with a error state
        self.__MapErrorState()

    ''' Methods of 1th and 2nd steps '''
    
    def __BuildByFile(self, file):
        try:
            file = open(file, 'r')
        except:
            return None
    
        for line in file:
            length = len(line)
            if length > 6 and line[0] == '<' and '>' in line:
                self.__IsGrammarRule(line)
            else:
                self.__IsToken(line)

    def __AddState(self, state, final=False):
        # Checking if the current_state already exists in the FA
        if not state in self.__FA:
            self.__FA[state] = {self.__IS_FINAL: final}
            for char in self.__ALPHABET:
                self.__FA[state][char] = None

    def __AddChar(self, char):
        # Checking if the character already exists in the ALPHABET
        if not char in self.__ALPHABET:
            self.__ALPHABET.append(char)
            for state in self.__FA:
                if state != self.__IS_FINAL:
                    self.__FA[state][char] = None

    def __AddNextState(self, current_state, char, next_state):
        # Checking if the next_state already exists in the FA for the current_state and character
        if not self.__FA[current_state][char]:
            self.__FA[current_state][char] = [next_state]
        elif  not next_state in self.__FA[current_state][char]:
            self.__FA[current_state][char].append(next_state)
            try:
                self.__FA[current_state][char].remove(ERROR_STATE)
            except:
                pass

    def __IsToken(self, string):
        # Settings
        string        = string[:len(string)-1]
        length        = len(string)
        current_state = self.__INITIAL_STATE
        next_state    = self.__FIRST_STATE
        final_state   = '<'+string+'>'
        # Building token states
        self.__AddState(final_state, True)
        for i in range(0, len(string)):
            char  = string[i]
            # Checking if this is the last character
            if i == length-1:
                next_state = final_state
            # Adding state, char and next_state
            self.__AddState(current_state)
            self.__AddChar(char)
            self.__AddNextState(current_state, char, next_state)
            # Updating current_state
            current_state = next_state
            # Updating next_state
            if next_state != final_state:
                while next_state == self.__INITIAL_STATE or next_state == self.__ERROR_STATE or current_state == next_state:
                    for j in range(len(next_state)-2, -1, -1):
                        if next_state[j] == 'Z':
                            next_state = next_state[:j]+'A'+next_state[j+1:]
                        elif j == 0:
                            next_state = next_state[j]+'A'+next_state[j+1:]
                        else:
                            next_state = next_state[:j]+chr(ord(next_state[j]) + 1)+next_state[j+1:]
                            break

    def __IsGrammarRule(self, string):
        string = string[:len(string)-1]
        state, productions = string.split('::=')
        productions = productions.split('|')

        self.__AddState(state)
        for p in productions:
            char = ''
            next_state = None
            is_char = True
            for c in p:
                if c == '<' and is_char:
                    next_state = c
                    is_char = False
                elif c == '>' and not is_char:
                    next_state += c
                    is_char = True
                elif not is_char:
                    next_state += c
                else:
                    char = c
            self.__AddChar(char)
            # Checking if this production is final
            if next_state:
                self.__AddNextState(state, char, next_state)
            else:
                self.__FA[state][self.__IS_FINAL] = True
    
    ''' Methods of 3rd step '''
    def __MergeStates(self, state, next_state):
        # Checking if the next_state is a final state
        if self.__FA[next_state][self.__IS_FINAL]:
            self.__FA[state][self.__IS_FINAL] = True
        # Merging next_states for each character
        for char in self.__FA[next_state]:
            if self.__FA[next_state][char] and char != self.__IS_FINAL:
                for next_next_state in self.__FA[next_state][char]:
                    if isinstance(self.__FA[state][char], list):
                        if not next_next_state in self.__FA[state][char]:
                            self.__FA[state][char].append(next_next_state)
                    elif self.__FA[state][char] and next_next_state and self.__FA[state][char] != next_next_state:
                        self.__FA[state][char] = [self.__FA[state][char], next_next_state]
                    elif next_next_state:
                        self.__FA[state][char] = next_next_state
                    else:
                        continue                        

                    if self.__UNION in next_next_state:
                        states = next_next_state[1:len(next_next_state)-1].split(self.__UNION)
                        for s in states:
                            try:
                                self.__FA[state][char].remove('<'+s+'>')
                            except:
                                pass

    def __CheckEpslon(self, state):
        if '' in self.__FA[state] and isinstance(self.__FA[state][''], list):
            for next_state in self.__FA[state]['']:
                self.__CheckEpslon(next_state)
                self.__MergeStates(state, next_state)
                self.__FA[state][''] = None

    def __RemoveEpslon(self):
        for state in self.__FA:
            self.__CheckEpslon(state)
            try:
                del self.__FA[state]['']
            except:
                pass

    ''' Methods of 4th step '''
    def __DeterminizeState(self, state):
        for char in self.__FA[state]:
            if char != self.__IS_FINAL:
                # Verifying if this state is a united_state and which states it's associated with
                next_states = self.__FA[state][char]
                if isinstance(next_states, str) or not next_states: continue
                for next_state in next_states:
                    if self.__UNION in next_state:
                        states = next_state[1:len(next_state)-1].split(self.__UNION)
                        for s in states:
                            try:
                                next_states.remove('<'+s+'>')
                            except:
                                pass
                
                # Verifying if there more then 1 next_states
                if len(next_states) > 1:
                    united_states = '<'
                    for i in range(0, len(next_states)):
                        next_state = self.__FA[state][char][i]
                        united_states += next_state[1:len(next_state)-1]
                        if i < len(self.__FA[state][char])-1:
                            united_states += self.__UNION
                    united_states += '>'
                    self.__AddState(united_states, final=False)
                    for next_state in next_states:
                        self.__MergeStates(united_states, next_state)
                    self.__FA[state][char] = united_states
                    self.__DeterminizeState(united_states)
                elif len(next_states) == 1:
                    self.__FA[state][char] = next_states[0]

    def __Determinize(self):
        FA = self.__FA.copy()
        for state in FA:
            self.__DeterminizeState(state)
    
    ''' Methods of 5th step '''
    def __RemoveUnreacheble(self):
        reacheble = [self.__INITIAL_STATE]
        verified = []
        # Verifying all reacheble states
        for state in reacheble:
            for char in self.__FA[state]:
                next_state = self.__FA[state][char]
                if char != self.__IS_FINAL and next_state and not state in verified and not next_state in reacheble:
                    reacheble.append(next_state)
            if not state in verified:
                verified.append(state)
        # Removing unreacheble states
        for state in self.__FA.copy():
            if not state in reacheble:
                del self.__FA[state]
    
    def __RemoveDead(self):
        dead = []
        verified = []
        # Getting all final states
        for state in self.__FA:
            if not state[self.__IS_FINAL] and not state in dead:
                dead.append(state)
        # To be continued
            
    ''' Methods of 6th step '''
    def __MapErrorState(self):
        self.__AddState(self.__ERROR_STATE, True)
        for state in self.__FA:
            for char in self.__FA[state]:
                if not self.__FA[state][char] and char != self.__IS_FINAL:
                    self.__FA[state][char] = self.__ERROR_STATE

    ''' Methods for test '''
    def Show(self):
        for state, value in self.__FA.items():
            print(state, '->', value, '\n')
    
    def CheckToken(self, token):
        state = self.__INITIAL_STATE
        for char in token:
            try:
                state = self.__FA[state][char]
            except:
                return self.__ERROR_STATE
        return state


# Testing
FA = FiniteAutomaton('tokens.txt')
FA.Show()
while True:
    token = input('enter a token: ')
    state = FA.CheckToken(token)
    print('state:', state)