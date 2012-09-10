import os
import parser
import re
import sys
from StringIO import StringIO

from pysh.converter import Converter, RoughLexer
import pysh.shell.builtin
from pysh.shell.evaluator import Evaluator
from pysh.shell.evaluator import start_global_wait_thread
from pysh.shell.parser import Parser
from pysh.shell.pycmd import pycmd
from pysh.shell.pycmd import IOType
from pysh.shell.tokenizer import Tokenizer

import zsh.native
from zsh.native import hgetc
import zsh.scanner


class ZshReader(object):
  def __init__(self):
    self.__first = True

  def read(self, n):
    assert n == 1
    if zsh.native.cvar.lexstop:
      return ''
    # Special hack to store a command (chline) to history. This hack is
    # much better than setting chwordpos >= 4 (it causes segfault
    # with timing error.) See hend in hist.c.
    # TODO: Reduce calls of hwbegin and hwend.
    zsh.native.hwbegin(0)
    c = chr(hgetc())
    zsh.native.hwend()
    if self.__first:
      # disable print prompt.
      zsh.native.cvar.isfirstln = 0
      zsh.native.cvar.curindentwidth = 0
      self.__first = False
    return c


# TODO: Show more information using cmdpush and cmdpop.
class ZshRoughLexer(RoughLexer):
  def __init__(self):
    RoughLexer.__init__(self, ZshReader())

  def _predict_indent(self, indent):
    zsh.native.cvar.curindentwidth = len(indent)

  def _predict_shellmode(self, prediction):
    zsh.native.cvar.expect_shellmode = 1 if prediction else 0


def scan_and_convert():
  lexer = ZshRoughLexer()
  tokens = []
  for token in lexer:
    indent = token[0]
    if not indent and token[1] == 'python' and is_python_expr(token[2]):
      token = (token[0], token[1], 'print ' + token[2])
    tokens.append(token)
    if not indent and zsh.native.cvar.curindentwidth == 0:
      break
  io = StringIO()
  converter = Converter(tokens, io, run_funcname='zsh.run')
  converter.convert(False)
  return io.getvalue()


def is_python_expr(line):
  try:
    parser.expr(line)
    return True
  except:
    return False


def read_and_rewrite(path):
  try:
    content = file(path, 'r').read()
    lexer = RoughLexer(StringIO(content))
    io = StringIO()
    converter = Converter(lexer, io, run_funcname='zsh.run')
    converter.convert(False)
    return io.getvalue()
  except:
    return None


def command():
  try:
    cmd = scan_and_convert()
  except KeyboardInterrupt:
    cmd = None
  if not cmd:
    return None
  else:
    return cmd


class Evaluator(Evaluator):
  def __after_folk(self, pid):
    if pid == 0:
      zsh.native.pyzsh_child_unblock()


class AliasMap(object):
  def __contains__(self, key):
    result = zsh.native.pyzsh_lookupalias(key)
    return result is not None

  def __getitem__(self, key):
    return (zsh.native.pyzsh_lookupalias(key),
            zsh.native.pyzsh_isaliasglobal(key) != 0)


alias_map = AliasMap()


def run(cmd_str, globals, locals, responses):
  return pysh.shell.runner.run(cmd_str, globals, locals, responses, alias_map)


@pycmd(name='cd', inType=IOType.No, outType=IOType.No)
def pyzsh_cd(args, input, options):
  zsh.native.pyzsh_execbuiltin('cd', map(str, args))
  return ()
