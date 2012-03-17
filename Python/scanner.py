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

  def __scan(self):
    first = True
    indent = False
    inblock = False
    while True:
      c = self.getc()
      if first:
        first = False
        if c == ' ':
          indent = True

      if c == ':':
        c = self.getc()
        if c == '\n':
          first = True
          indent = False
          inblock = True
      elif c == '\n':
        if inblock and indent:
          first = True
          indent = False
        else:
          break
