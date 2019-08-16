from src.FiniteAutomaton import FiniteAutomaton

# Testing
FA = FiniteAutomaton()
FA.Show()

initial_state = FA.GetInitialState()
error_state = FA.GetErrorState()
while True:
    token = input('enter a token: ')
    state = FA.GetInitialState()
    for char in token:
        state = FA.MakeTransition(state, char)

    if not FA.IsFinal(state) or state == error_state:
        print('Lexical error! State:', state)
    else:
        print('Correct! State:', state)