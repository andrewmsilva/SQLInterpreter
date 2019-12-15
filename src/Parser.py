from pandas import read_csv, notnull

class Parser:
  __SLR = None
  __GLC = None

  __INPUTS_FOLDER = 'set'
  __SLR_CSV = 'SLR.csv'
  __GLC_CSV = 'GLC.csv'

  def __init__(self):
    # Loading SLR
    self.__SLR = read_csv(self.__INPUTS_FOLDER + '/' + self.__SLR_CSV)
    self.__SLR = self.__SLR.where((notnull(self.__SLR)), None)
    # Loading GLC
    glc = read_csv(self.__INPUTS_FOLDER + '/' + self.__GLC_CSV)
    self.__GLC = []
    for row in glc.iterrows():
      rule = row[1][0]
      production = row[1][1].split()
      if production[0] == "''":
        production = []
      self.__GLC.append((rule, len(production)))
  
  def parse(self, output, debug=False):
    # Settings
    output = output.split()
    stack = ['0']
    id = 'id'
    num = 'num'

    if debug == True: print(stack, output)
    result = None
    while result == None:
      state = int(stack[-1])
      token = output[0]
      action = None
      try:
        action = self.__SLR.iloc[state][token]
      except:
        try:
          int(token)
          token = num
        except:
          token = id
      action = str(self.__SLR.iloc[state][token])
      # Stacking
      if action[0] == 's':
        stack.append(token)
        stack.append(action[1:])
        output = output[1:]
      # Reducing
      elif action[0] == 'r':
        production_id = int(action[1:])
        rule, production_len = self.__GLC[production_id]
        if production_len > 0:
          stack = stack[:-production_len*2]
        # Leaping
        stack.append(rule)
        if debug == True: print(stack, output)
        state = int(stack[-2])
        leap = self.__SLR.iloc[state][rule]
        if leap == None:
          result = False
        else:
          stack.append(str(int(leap)))
      elif action == 'acc':
        result = True
      else:
        print('Syntax error')
        result = False
    if debug == True: print(result)
    return result
      
