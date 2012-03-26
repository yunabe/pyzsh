import sys
from StringIO import StringIO


class Scanner(object):
  def __init__(self):
    self.writer = None
    self.indent_stack = []

  def push_indent(self, indent):
    while self.indent_stack and self.indent_stack[-1] >= indent:
      self.indent_stack.pop()
    self.indent_stack.append(indent)
    self.expectIndent(indent)

  def pop_indent(self):
    if self.indent_stack:
      self.indent_stack.pop()
    self.expectIndent(self.indent_stack[-1] if self.indent_stack else 0)

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
        elif c != '\n':
          first = False

      if c == ':':
        c = self.getc()
        if c == '\n':
          self.push_indent(indent + 2)
          first = True
          indent = 0
          inblock = True
      elif c == '\n':
        if inblock:
          if first:
            self.pop_indent()
          else:
            self.push_indent(indent)
            
        if inblock and indent > 0:
          first = True
          indent = 0
        else:
          break
