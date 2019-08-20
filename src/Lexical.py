from src.FiniteAutomaton import FiniteAutomaton

def Analyze(file):
    # Testing
    FA = FiniteAutomaton(save=False)
    FA.Show()

    initial_state = FA.GetInitialState()
    error_state = FA.GetErrorState()
    while True:
        token = input('enter a token: ')
        state = initial_state
        for char in token:
            state = FA.MakeTransition(state, char)

        if state == error_state or not FA.IsFinal(state):
            print('Lexical error! State:', state)
        else:
            print('Correct! State:', state)