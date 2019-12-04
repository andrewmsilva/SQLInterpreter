import SQLInterpreter as SQLI

while True:
    query = input('>>> ')
    SQLI.interpret(query)