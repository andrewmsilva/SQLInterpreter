import pickle

class FSM():
    # Default settings
    __INITIAL_STATE   = 0
    __ERROR_STATE     = -1
    __ALPHABET        = []
    __NEXT_NEW_STATE  = 0
    __FSM              = {}
    # Folders
    _INPUTS_FOLDER  = "set"
    _RESULTS_FOLDER = "bin"
    # Files
    __TOKENS_FILE     = "tokens.txt"
    __GRAMMATICS_FILE = "grammatics.txt"
    __RESULTS_FILE    = "FSM.bin"

    def __init__(self, save=True):
        # Trying to load an already created Finite Automaton
        if not self.__load():
            # Mapping transitions
            self.__mapGrammatics()
            self.__mapTokens()
            # Handling with erros
            self.__removeEpslonTransitions()
            self.__determinize()
            # Removing useless
            self.__removeUnreachebleStates()
            self.__removeDeadStates()
            # Mapping error state
            self.__mapErrorState()
            # Saving to file
            if save:
                self.__save()

    def __load(self):
        try:
            file = open(self._RESULTS_FOLDER+'/'+self.__RESULTS_FILE, 'rb')
            self.__FSM = pickle.load(file)
            file.close()
            return True
        except:
            return False
    
    def __save(self):
        file = open(self._RESULTS_FOLDER+'/'+self.__RESULTS_FILE, 'wb')
        pickle.dump(self.__FSM, file)
        file.close()
    
    def __getAvailableState(self, state=None):
        if state is None:
            state = self.__NEXT_NEW_STATE
        else:
            state += 1
        try:
            while self.__FSM[state]['final']:
                state += 1
        except:
            pass
        return state

    def __createState(self, state, final=False, parents=[]):
        # Checking if the state already exists in the FSM
        if not state in self.__FSM:
            self.__FSM[state] = {'final': final, 'parents': parents}
            self.__NEXT_NEW_STATE += 1
            for char in self.__ALPHABET:
                self.__FSM[state][char] = []
        elif not self.__FSM[state]['final']:
            self.__FSM[state]['final'] = final

    def __appendCharacter(self, char):
        # Checking if the character already exists in the ALPHABET
        if not char in self.__ALPHABET:
            self.__ALPHABET.append(char)
            for state in self.__FSM:
                self.__FSM[state][char] = []

    def __createTransition(self, state, char, next_state):
        # Checking if the next_state already exists in the FSM for the state and character
        if type(self.__FSM[state][char]) == list:
            if next_state not in self.__FSM[state][char]:
                self.__FSM[state][char].append(next_state)
    
    def __mapTokens(self):
        try:
            file = open(self._INPUTS_FOLDER+'/'+self.__TOKENS_FILE, 'r')
            for token in file:
                # Settings
                token        = token.replace('\n', '')
                token_length = len(token)
                # Building token states
                state = self.__INITIAL_STATE
                for i in range(token_length):
                    char = token[i]
                    # Appending character to the alphabet
                    self.__appendCharacter(char)
                    # Creating state if does not exists
                    self.__createState(state)
                    # Creating next_state if does not exists
                    next_state = None
                    if i < token_length-1:
                        next_state = self.__getAvailableState(state)
                        self.__createState(next_state)
                    else:
                        next_state = self.__getAvailableState()
                        self.__createState(next_state, True)
                    # Creating the transition
                    self.__createTransition(state, char, next_state)
                    # Updating state
                    state = next_state
        except:
            # Doing nothing if the file with tokens does not exists
            pass
    
    def __mapGrammatics(self):
        try:
            file = open(self._INPUTS_FOLDER+'/'+self.__GRAMMATICS_FILE, 'r')
            for grammatic in file:
                # Splitting state and its productions
                grammatic = grammatic.replace('\n', '')
                state, productions = grammatic.split('::=')
                productions = productions.split('|')
                state = int(state.replace('<', '').replace('>', ''))

                self.__createState(state)
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
                    self.__appendCharacter(char)
                    # Checking if this production is final
                    if next_state:
                        next_state = int(next_state.replace('<', '').replace('>', ''))
                        self.__createState(next_state)
                        self.__createTransition(state, char, next_state)
                    else:
                        self.__FSM[state]['final'] = True
        except:
            # Doing nothing if the file with tokens does not exists
            pass

    def __mergeStates(self, state, next_state):
        # Checking if the next_state is a final state
        if self.__FSM[next_state]['final']:
            self.__FSM[state]['final'] = True
        # Merging states for each character
        for char in self.__ALPHABET:
            states = self.__FSM[next_state][char]
            if type(states) is list:
                for s in states:
                    self.__createTransition(state, char, s)
            elif type(states) is int:
                self.__createTransition(state, char, states)


    def __checkEpslon(self, state):
        for next_state in self.__FSM[state]['']:
            self.__checkEpslon(next_state)
            self.__mergeStates(state, next_state)
            self.__FSM[state][''] = []

    def __removeEpslonTransitions(self):
        if '' in self.__ALPHABET:
            for state in self.__FSM:
                self.__checkEpslon(state)
                del self.__FSM[state]['']
            self.__ALPHABET.remove('')
    
    def __getStateByParents(self, parents):
        for state in self.__FSM:
            if self.__FSM[state]['parents'] == parents:
                return state

    def __determinizeState(self, state):
        for char in self.__ALPHABET:
            # Verifying if this transition is not determinized
            next_states = self.__FSM[state][char]
            if type(next_states) == list:
                if len(next_states) == 1:
                    self.__FSM[state][char] = next_states[0]
                elif len(next_states) == 0:
                    self.__FSM[state][char] = None
                else:
                    next_states = next_states.copy()
                    # Removing states already included
                    for parent in self.__FSM[state]['parents']:
                        if parent in next_states:
                            next_states.remove(parent)
                    # If the transition has only one state, keep this one
                    if len(next_states) == 1:
                        self.__FSM[state][char] = next_states[0]
                    elif len(next_states) == 0 and self.__FSM[state][char] == self.__FSM[state]['parents']:
                        self.__FSM[state][char] = state
                    # Determinizing state
                    else:
                        # Getting the parents states
                        parents = []
                        for next_state in next_states:
                            if next_state not in parents:
                                parents.append(next_state)
                        # Getting a state with these parents
                        new_state = self.__getStateByParents(parents)
                        if new_state is not None:
                            self.__FSM[state][char] = new_state
                        # Creating a new_state with all transitions
                        else:
                            new_state = self.__getAvailableState()
                            self.__FSM[state][char] = new_state
                            self.__createState(new_state, parents=parents)
                            for next_state in next_states:
                                self.__mergeStates(new_state, next_state)
                            # Determinizing the new_state
                            self.__determinizeState(new_state)

    def __determinize(self):
        FSM = self.__FSM.copy()
        for state in FSM:
            self.__determinizeState(state)
    
    def __getReachebleStates(self, initial_state=__INITIAL_STATE):
        reacheble = [initial_state]
        verified = []
        # Verifying all reacheble states
        for state in reacheble:
            for char in self.__ALPHABET:
                next_state = self.__FSM[state][char]
                if next_state and not state in verified and not next_state in reacheble:
                    reacheble.append(next_state)
            if not state in verified:
                verified.append(state)
        return reacheble
    
    def __removeUnreachebleStates(self):
        reacheble = self.__getReachebleStates()
        # Removing unreacheble states
        for state in self.__FSM.copy():
            if not state in reacheble:
                del self.__FSM[state]
    
    def __removeDeadStates(self):
        # Getting all final states
        for state in self.__FSM.copy():
            if not self.__FSM[state]['final']:
                reacheble = self.__getReachebleStates(state)
                dead = True
                for next_state in reacheble:
                    if dead and self.__FSM[next_state]['final']:
                        dead = False
                if dead:
                    print(state, ' is dead!')
                    del self.__FSM[state]
    
    def __mapErrorState(self):
        self.__createState(self.__ERROR_STATE, final=True)
        for state in self.__FSM:
            for char in self.__ALPHABET:
                if self.__FSM[state][char] is None or type(self.__FSM[state][char]) == list:
                    self.__FSM[state][char] = self.__ERROR_STATE

    def show(self):
        for state, value in self.__FSM.items():
            print(state, '->', value, '\n')
    
    def getInitialState(self):
        return self.__INITIAL_STATE
    
    def getErrorState(self):
        return self.__ERROR_STATE
    
    def makeTransition(self, state, char):
        try:
            return self.__FSM[state][char]
        except KeyError:
            return self.__ERROR_STATE
    
    def isFinal(self, state):
        try:
            is_final = self.__FSM[state]['final']
        except KeyError:
            is_final = False
        return is_final