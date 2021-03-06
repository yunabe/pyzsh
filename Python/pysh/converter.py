import StringIO
import sys

from pysh.shell.tokenizer import Tokenizer
from pysh.shell.parser import Assign
from pysh.shell.parser import BinaryOp
from pysh.shell.parser import Parser
from pysh.shell.parser import Process


SIGNATURE = ('# -*- coding: utf-8 -*-\n'
             '# This file was auto-generated by pysh.\n'
             '# Don\'t edit this by hand.\n')


class RoughLexer(object):
  def __init__(self, reader):
    self.reader = reader
    self.c = None
    # Used for indent prediction.
    self.__indent_stack = []

  def __iter__(self):
    return self

  def is_space(self, c):
    return c == ' ' or c == '\t' or c == '\f' or c == '\v'

  def __indent_width(self, indent):
    return sum(map(lambda c: 1 if c == ' ' else 8, indent))

  def __push_indent(self, indent):
    width = self.__indent_width(indent)
    while self.__indent_stack and self.__indent_stack[-1][1] >= width:
      self.__indent_stack.pop()
    self.__indent_stack.append((indent, width))

  def __pop_indent(self):
    if self.__indent_stack:
      self.__indent_stack.pop()

  def __predict_next_indent(self, indent, mode, content):
    if len(content) == 0:
      self.__pop_indent()
    else:
      self.__push_indent(indent)
      if mode == 'python':
        if content.endswith(':'):
          self.__push_indent(indent + ' ' * 4)
        elif (content.startswith('pass') or
              content.startswith('return')):
          self.__pop_indent()

    if self.__indent_stack:
      prediction = self.__indent_stack[-1][0]
    else:
      prediction = ''
    self._predict_indent(prediction)

  def _predict_indent(self, indent):
    pass

  def _predict_shellmode(self, prediction):
    pass

  def read(self):
    self.c = self.reader.read(1)
    return self.c

  def seek_string_literal(self, content):
    first = self.c
    self.read()
    if self.c == first:
      if self.read() != first:
        # empty literal
        content.write(first * 2)
      else:
        content.write(first * 3)
        self.read()
        self.seek_here_document(content, first)
    else:
      content.write(first)
      self.seek_simple_string_literal(content, first)

  def seek_here_document(self, content, quote):
    count = 0
    while True:
      cur = self.c
      self.read()
      if cur == '':
        raise Exception('EOF while scanning here document')
      elif cur == quote:
        content.write(cur)
        count += 1
        if count == 3:
          break
      elif cur == '\\':
        if self.c == '\r' or self.c == '\n':
          self.seek_backslash(content)
        else:
          content.write('\\' + self.c)
          self.read()
      else:
        content.write(cur)
        count = 0

  def seek_simple_string_literal(self, content, quote):
    while True:
      cur = self.c
      self.read()
      if cur == '':
        raise Exception('EOF while scanning string literal')
      elif cur == '\r' or cur == '\n':
        raise Exception('EOL while scanning string literal')
      elif cur == '\\':
        if self.c == '\r' or self.c == '\n':
          self.seek_backslash(content)
        else:
          content.write('\\' + self.c)
          self.read()
      else:
        content.write(cur)
        if cur == quote:
          break

  def seek_backslash(self, writer):
    if self.c == '\n':
      self.read()
    elif self.c == '\r':
      if self.read() == '\n':
        self.read()
    else:
      writer.write('\\')

  def next(self):
    if self.c is None:
      self.c = self.reader.read(1)

    indent_writer = StringIO.StringIO()
    while self.is_space(self.c):
      indent_writer.write(self.c)
      self.read()

    mode = 'python'
    if self.c == '>':
      mode = 'shell'
      while self.is_space(self.read()):
        pass
      
    content = StringIO.StringIO()
    while True:
      if self.c == '':
        break
      elif self.c == '\'' or self.c == '"':
        self.seek_string_literal(content)
      elif self.c == '#':
        while self.c != '\n' and self.c != '':
          self.read()
        self.read() # discard '\n'
        break
      elif self.c == '\r':
        if self.read() == '\n':
          self.c = None  # discard '\n'
        break
      elif self.c == '\n':
        self.c = None  # discard '\n'
        break
      elif self.c == '\\':
        self.read()
        self.seek_backslash(content)
      else:
        content.write(self.c)
        self.read()
    content_value = content.getvalue()
    if self.c == '' and not content_value:
      raise StopIteration()
    else:
      indent = indent_writer.getvalue()
      self._predict_shellmode(mode == 'shell')
      self.__predict_next_indent(indent, mode, content_value)
      return indent, mode, content_value


class Converter(object):
  def __init__(self, lexer, writer, run_funcname='pysh.shell.runner.run'):
    self.lexer = lexer
    self.writer = writer
    self.__fun_func_name = run_funcname

  def extractResponseNames(self, content):
    parser = Parser(Tokenizer(content))
    ast = parser.parse()
    names = []
    self.extractResponseNamesInternal(ast, names)
    return names

  def extractResponseNamesInternal(self, ast, names):
    if not ast or not (isinstance(ast, Process) or
                       isinstance(ast, BinaryOp) or
                       isinstance(ast, Assign)):
      return
    if isinstance(ast, Process):
      for redirect in ast.redirects:
        if redirect[0] == '=>':
          names.append(redirect[1])
      return
    if isinstance(ast, Assign):
      self.extractResponseNamesInternal(ast.cmd, names)
      names.append(ast.name)
      return
    for e in (ast.left, ast.right):
      self.extractResponseNamesInternal(e, names)

  def convert(self, with_signature):
    if with_signature:
      self.writer.write(SIGNATURE)
    self.writer.write('import pysh.shell.runner\n')
    for indent, mode, content in self.lexer:
      self.writer.write(indent)
      if mode == 'python':
        self.writer.write(content)
      elif content:
        names = self.extractResponseNames(content)
        if names:
          self.writer.write(', '.join(names + ['']) + '= ')
        self.writer.write('%s(%s, locals(), globals(), %s)' % (
            self.__fun_func_name, `content`, `names`))
      self.writer.write('\n')


if __name__ == '__main__':
  Converter(RoughLexer(sys.stdin), sys.stdout).convert(True)
