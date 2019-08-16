from src.FiniteAutomaton import FiniteAutomaton

# Testing
FA = FiniteAutomaton()
FA.Show()
while True:
    token = input('enter a token: ')
    state = FA.CheckToken(token)
    print('state:', state)