import pickle

class FiniteAutomaton(object):
    # Default settings
    __INITIAL_STATE   = 0
    __ERROR_STATE     = -1
    __ALPHABET        = []
    __NEXT_NEW_STATE  = 0
    __FA              = {}
    # Folders
    __INPUTS_FOLDER  = "set"
    __RESULTS_FOLDER = "bin"
    # Files
    __TOKENS_FILE     = "tokens.txt"
    __GRAMMATICS_FILE = "grammatics.txt"
    __RESULTS_FILE    = "finite_automaton.bin"

    def __init__(self, save=True):
        # Trying to load an already created Finite Automaton
        if not self.__Load():
            # Mapping transitions
            self.__MapGrammatics()
            self.__MapTokens()
            # Handling with erros
            self.__RemoveEpslonTransitions()
            self.__Determinize()
            # Removing useless
            self.__RemoveUnreachebleStates()
            self.__RemoveDeadStates()
            # Mapping error state
            self.__MapErrorState()
            # Saving to file
            if save:
                self.__Save()

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
            state = self.__NEXT_NEW_STATE
        else:
            state += 1
        try:
            while self.__FA[state]['final']:
                state += 1
        except:
            pass
        return state

    def __CreateState(self, state, final=False, parents=[]):
        # Checking if the state already exists in the FA
        if not state in self.__FA:
            self.__FA[state] = {'final': final, 'parents': parents}
            self.__NEXT_NEW_STATE += 1
            for char in self.__ALPHABET:
                self.__FA[state][char] = []
        elif not self.__FA[state]['final']:
            self.__FA[state]['final'] = final

    def __AppendCharacter(self, char):
        # Checking if the character already exists in the ALPHABET
        if not char in self.__ALPHABET:
            self.__ALPHABET.append(char)
            for state in self.__FA:
                self.__FA[state][char] = []

    def __CreateTransition(self, state, char, next_state):
        # Checking if the next_state already exists in the FA for the state and character
        if type(self.__FA[state][char]) == list:
            if next_state not in self.__FA[state][char]:
                self.__FA[state][char].append(next_state)
    
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
                    # Creating next_state if does not exists
                    next_state = None
                    if i < token_length-1:
                        next_state = self.__GetAvailableState(state)
                        self.__CreateState(next_state)
                    else:
                        next_state = self.__GetAvailableState()
                        self.__CreateState(next_state, True)
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
                    # Getting transition and character, if exists
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
            for s in states:
                self.__CreateTransition(state, char, s)

    def __CheckEpslon(self, state):
        for next_state in self.__FA[state]['']:
            self.__CheckEpslon(next_state)
            self.__MergeStates(state, next_state)
            self.__FA[state][''] = []

    def __RemoveEpslonTransitions(self):
        if '' in self.__ALPHABET:
            for state in self.__FA:
                self.__CheckEpslon(state)
                del self.__FA[state]['']
            self.__ALPHABET.remove('')
    
    def __GetStateByParents(self, parents):
        for state in self.__FA:
            if self.__FA[state]['parents'] == parents:
                return state

    def __DeterminizeState(self, state):
        for char in self.__ALPHABET:
            # Verifying if this transition is not determinized
            next_states = self.__FA[state][char]
            if type(next_states) == list:
                if len(next_states) == 1:
                    self.__FA[state][char] = next_states[0]
                elif len(next_states) == 0:
                    self.__FA[state][char] = None
                else:
                    next_states = next_states.copy()
                    # Removing states already included
                    for parent in self.__FA[state]['parents']:
                        if parent in next_states:
                            next_states.remove(parent)
                    # If the transition has only one state, keep this one
                    if len(next_states) == 1:
                        self.__FA[state][char] = next_states[0]
                    elif len(next_states) == 0 and self.__FA[state][char] == self.__FA[state]['parents']:
                        self.__FA[state][char] = state
                    # Determinizing state
                    else:
                        # Getting the parents states
                        parents = []
                        for next_state in next_states:
                            if next_state not in parents:
                                parents.append(next_state)
                        # Getting a state with these parents
                        new_state = self.__GetStateByParents(parents)
                        if new_state is not None:
                            self.__FA[state][char] = new_state
                        # Creating a new_state with all transitions
                        else:
                            new_state = self.__GetAvailableState()
                            self.__FA[state][char] = new_state
                            self.__CreateState(new_state, parents=parents)
                            for next_state in next_states:
                                self.__MergeStates(new_state, next_state)
                            # Determinizing the new_state
                            self.__DeterminizeState(new_state)

    def __Determinize(self):
        FA = self.__FA.copy()
        for state in FA:
            self.__DeterminizeState(state)
    
    def __GetReachebleStates(self, initial_state=__INITIAL_STATE):
        reacheble = [initial_state]
        verified = []
        # Verifying all reacheble states
        for state in reacheble:
            for char in self.__ALPHABET:
                next_state = self.__FA[state][char]
                if next_state and not state in verified and not next_state in reacheble:
                    reacheble.append(next_state)
            if not state in verified:
                verified.append(state)
        return reacheble
    
    def __RemoveUnreachebleStates(self):
        reacheble = self.__GetReachebleStates()
        # Removing unreacheble states
        for state in self.__FA.copy():
            if not state in reacheble:
                del self.__FA[state]
    
    def __RemoveDeadStates(self):
        # Getting all final states
        for state in self.__FA.copy():
            if not self.__FA[state]['final']:
                reacheble = self.__GetReachebleStates(state)
                dead = True
                for next_state in reacheble:
                    if dead and self.__FA[next_state]['final']:
                        dead = False
                if dead:
                    print(state, ' is dead!')
                    del self.__FA[state]
    
    def __MapErrorState(self):
        self.__CreateState(self.__ERROR_STATE, final=True)
        for state in self.__FA:
            for char in self.__ALPHABET:
                if self.__FA[state][char] is None or type(self.__FA[state][char]) == list:
                    self.__FA[state][char] = self.__ERROR_STATE

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
        except KeyError:
            return self.__ERROR_STATE
    
    def IsFinal(self, state):
        try:
            is_final = self.__FA[state]['final']
        except KeyError:
            is_final = False
        return is_final