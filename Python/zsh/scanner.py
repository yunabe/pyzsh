import re
import sys
from StringIO import StringIO


INDENT_PATTERN = re.compile(r'^(\s*)')
BLOCK_START_PATTERN = re.compile(r'^.*:\s*(#.*)?$')
EMPTY_LINE_PATTERN = re.compile(r'^(>?\s*)(#.*)?$')


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

  def expectShellMode(self, expectation):
    pass

  def scanLine(self):
    line = StringIO()
    while True:
      c = self.getc()
      if c == '\n':
        break
      line.write(c)
    return line.getvalue()

  def __scan(self):
    self.expectIndent(0)  # reset indent position
    inblock = False
    while True:
      line = self.scanLine()
      indent = INDENT_PATTERN.match(line).end()
      line = line[indent:]
      m = BLOCK_START_PATTERN.match(line)
      if m:
        self.push_indent(indent + 2)
        inblock = True
        continue

      is_empty = EMPTY_LINE_PATTERN.match(line)
      if not is_empty or not inblock:
        # don't change mode if line is in block and empty.
        self.expectShellMode(line.startswith('>'))
      if not inblock or indent == 0:
        break
      if is_empty:
        self.pop_indent()
      else:
        self.push_indent(indent)
