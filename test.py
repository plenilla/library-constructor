class Debugger:
  def __init__(self):
    self.value = False


def calculate(a, b):
  result = a + b
  return result

def main():
  d = Debugger()
  x = 5
  y = 1
  total = calculate(x, y)
  print(total)
  
  
if __name__ == "__main__":
  main()