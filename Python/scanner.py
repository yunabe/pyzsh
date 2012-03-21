import sys
from StringIO import StringIO


class Scanner(object):
  def __init__(self):
    self.writer = None

  def read(self):
    return sys.stdin.read(1)

  def getc(self):
    c = self.read()
    if not c:
      raise StopIteration()
    self.writer.write(c)
    return c

  def scan(self):
    self.writer = StringIO()
    try:
      self.__scan()
    except StopIteration:
      pass
    return self.writer.getvalue()

  def expectIndent(self):
      pass

  def __scan(self):
    first = True
    indent = 0
    inblock = False
    while True:
      c = self.getc()
      if first:
        if c == ' ':
          indent += 1
        else:
          first = False

      if c == ':':
        c = self.getc()
        if c == '\n':
          self.expectIndent(indent + 2)
          first = True
          indent = 0
          inblock = True
      elif c == '\n':
        self.expectIndent(indent if inblock else 0)
        if inblock and indent > 0:
          first = True
          indent = 0
        else:
          break
