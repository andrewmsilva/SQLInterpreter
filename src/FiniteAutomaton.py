import pickle

class FiniteAutomaton(object):
    # Default settings
    __INITIAL_STATE   = 0
    __ERROR_STATE     = -1
    __RESERVED_STATES = [__ERROR_STATE]
    __ALPHABET        = []
    __STATES_COUNT    = 0
    __FA              = {}
    # Folders
    __INPUTS_FOLDER  = "set"
    __RESULTS_FOLDER = "bin"
    # Files
    __TOKENS_FILE     = "tokens.txt"
    __GRAMMATICS_FILE = "grammatics.txt"
    __RESULTS_FILE    = "finite_automaton.bin"

    def __init__(self):
        # Trying to load an already created Finite Automaton
        if not self.__Load():
            # Creating error_state
            self.__CreateState(self.__ERROR_STATE, True)
            # Mapping transitions
            self.__MapTokens()
            self.__MapGrammatics()
            # Handling with erros
            self.__RemoveEpslonTransitions()
            self.__Determinize()
            #self.__RemoveUnreachebleStates()
            #self.__RemoveDeadStates()
            # Saving to file
            #self.__Save()

    def __Load(self):
        try:
            file = open(self.__RESULTS_FOLDER+'/'+self.__RESULTS_FILE, 'rb')
            self.__FA = pickle.load(file)
            file.close()
            return True
        except:
            return False
    
    def __Save(self):
        file = open(self.__RESULTS_FOLDER+'/'+self.__RESULTS_FILE, 'wb')
        pickle.dump(self.__FA, file)
        file.close()
    
    def __GetAvailableState(self, state=None):
        if state is None:
            state = self.__STATES_COUNT-1
        else:
            state += 1
        while state in self.__RESERVED_STATES:
            state += 1
        return state

    def __CreateState(self, state, final=False, parents=[]):
        # Checking if the state already exists in the FA
        if not state in self.__FA:
            self.__FA[state] = {'final': final, 'parents': parents}
            self.__STATES_COUNT += 1
            for char in self.__ALPHABET:
                self.__FA[state][char] = self.__ERROR_STATE
        elif not self.__FA[state]['final']:
            self.__FA[state]['final'] = final

    def __AppendCharacter(self, char):
        # Checking if the character already exists in the ALPHABET
        if not char in self.__ALPHABET:
            self.__ALPHABET.append(char)
            for state in self.__FA:
                self.__FA[state][char] = self.__ERROR_STATE

    def __CreateTransition(self, state, char, next_state):
        # Checking if the next_state already exists in the FA for the state and character
        if self.__FA[state][char] == self.__ERROR_STATE:
            self.__FA[state][char] = next_state
        elif self.__FA[state][char] != next_state:
            if type(self.__FA[state][char]) is list:
                if next_state not in self.__FA[state][char]:
                    self.__FA[state][char].append(next_state)
            else:
                self.__FA[state][char] = [self.__FA[state][char], next_state]
    
    def __MapTokens(self):
        try:
            file = open(self.__INPUTS_FOLDER+'/'+self.__TOKENS_FILE, 'r')
            for token in file:
                # Settings
                token        = token.replace('\n', '')
                token_length = len(token)
                # Building token states
                state = self.__INITIAL_STATE
                for i in range(token_length):
                    char = token[i]
                    # Appending character to the alphabet
                    self.__AppendCharacter(char)
                    # Creating state if does not exists
                    self.__CreateState(state)
                    # Getting an availabe next_state
                    next_state = self.__GetAvailableState(state)
                    # Creating next_state if does not exists
                    if i < token_length-1:
                        self.__CreateState(next_state)
                    else:
                        self.__CreateState(next_state, True)
                        self.__RESERVED_STATES.append(next_state)
                    # Creating the transition
                    self.__CreateTransition(state, char, next_state)
                    # Updating state
                    state = next_state
        except:
            # Doing nothing if the file with tokens does not exists
            pass
    
    def __MapGrammatics(self):
        try:
            file = open(self.__INPUTS_FOLDER+'/'+self.__GRAMMATICS_FILE, 'r')
            for grammatic in file:
                # Splitting state and its productions
                grammatic = grammatic.replace('\n', '')
                state, productions = grammatic.split('::=')
                productions = productions.split('|')
                state = int(state.replace('<', '').replace('>', ''))

                self.__CreateState(state)
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
                    self.__AppendCharacter(char)
                    # Checking if this production is final
                    if next_state:
                        next_state = int(next_state.replace('<', '').replace('>', ''))
                        self.__CreateState(next_state)
                        self.__CreateTransition(state, char, next_state)
                    else:
                        self.__FA[state]['final'] = True
        except:
            # Doing nothing if the file with tokens does not exists
            pass

    def __MergeStates(self, state, next_state):
        # Checking if the next_state is a final state
        if self.__FA[next_state]['final']:
            self.__FA[state]['final'] = True
        # Merging states for each character
        for char in self.__ALPHABET:
            states = self.__FA[next_state][char]
            if type(states) is list:
                for s in states:
                    self.__CreateTransition(state, char, s)
            else:
                self.__CreateTransition(state, char, states)

    def __CheckEpslon(self, state):
        if type(self.__FA[state]['']) is list:
            for next_state in self.__FA[state]['']:
                self.__CheckEpslon(next_state)
                self.__MergeStates(state, next_state)
                self.__FA[state][''] = None

    def __RemoveEpslonTransitions(self):
        if '' in self.__ALPHABET:
            for state in self.__FA:
                self.__CheckEpslon(state)
                del self.__FA[state]['']
            self.__ALPHABET.remove('')

    def __DeterminizeState(self, state):
        for char in self.__ALPHABET:
            # Verifying if this transition is not determinized
            next_states = self.__FA[state][char]
            if type(next_states) is list:
                for s in next_states:
                    # Removing states already included
                    if s in self.__FA[state]['parents']:
                        try:
                            next_states.remove(s)
                        except:
                            pass
                # Verifying if this transition keep not determinized
                if len(next_states) > 1:
                    # Creating a new_state with all transitions
                    new_state = self.__GetAvailableState()
                    self.__CreateState(new_state, parents=next_states)
                    for next_state in next_states:
                        self.__MergeStates(new_state, next_state)
                    # Updating the transition with the new_state
                    self.__FA[state][char] = new_state
                    # Determinizing the new_state
                    self.__DeterminizeState(new_state)
                # If there is only one state in this transition, this is already determinized
                elif len(next_states) == 1:
                    self.__FA[state][char] = next_states[0]

    def __Determinize(self):
        FA = self.__FA.copy()
        for state in FA:
            self.__DeterminizeState(state)
    
    """''' Methods of 5th step '''
    def __GetReachebleStates(self, initial_state=__INITIAL_STATE):
        reacheble = [initial_state]
        verified = []
        # Verifying all reacheble states
        for state in reacheble:
            for char in self.__FA[state]:
                next_state = self.__FA[state][char]
                if char != self.__IS_FINAL and next_state and not state in verified and not next_state in reacheble:
                    reacheble.append(next_state)
            if not state in verified:
                verified.append(state)
        return reacheble
    
    def __RemoveUnreacheble(self):
        reacheble = self.__GetReachebleStates()
        # Removing unreacheble states
        for state in self.__FA.copy():
            if not state in reacheble:
                del self.__FA[state]
    
    def __RemoveDead(self):
        # Getting all final states
        for state in self.__FA.copy():
            if not self.__FA[state][self.__IS_FINAL]:
                reacheble = self.__GetReachebleStates(state)
                dead = True
                for next_state in reacheble:
                    if dead and self.__FA[next_state][self.__IS_FINAL]:
                        dead = False
                if dead:
                    print(state, ' is dead!')
                    del self.__FA[state]
        
    ''' Methods of 6th step '''
    def __MapErrorState(self):
        self.__AddState(self.__ERROR_STATE, True)
        for state in self.__FA:
            for char in self.__FA[state]:
                if not self.__FA[state][char] and char != self.__IS_FINAL:
                    self.__FA[state][char] = self.__ERROR_STATE"""

    ''' Methods for test '''
    def Show(self):
        for state, value in self.__FA.items():
            print(state, '->', value, '\n')
    
    def GetInitialState(self):
        return self.__INITIAL_STATE
    
    def GetErrorState(self):
        return self.__ERROR_STATE
    
    def MakeTransition(self, state, char):
        try:
            return self.__FA[state][char]
        except:
            return self.__ERROR_STATE
    
    def IsFinal(self, state):
        return self.__FA[state]['final']