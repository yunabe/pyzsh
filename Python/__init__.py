import os
import parser
import re
import sys
from StringIO import StringIO

import zsh.native
from zsh.native import hgetc
import zsh.pysh
import zsh.scanner


# TODO: Show more information using cmdpush and cmdpop.
class ZshScanner(zsh.scanner.Scanner):
  def __init__(self):
    super(ZshScanner, self).__init__()
    self.first = True

  def read(self):
    if zsh.native.cvar.lexstop:
      raise StopIteration()
    else:
      # Special hack to store a command (chline) to history. This hack is
      # much better than setting chwordpos >= 4 (it causes segfault
      # with timing error.) See hend in hist.c.
      # TODO: Reduce calls of hwbegin and hwend.
      zsh.native.hwbegin(0)
      c = chr(hgetc())
      zsh.native.hwend()
      if self.first:
        # disable print prompt.
        zsh.native.cvar.isfirstln = 0
        zsh.native.cvar.curindentwidth = 0
        self.first = False
      return c

  def expectIndent(self, indent):
    zsh.native.cvar.curindentwidth = indent

  def expectShellMode(self, expectation):
    zsh.native.cvar.expect_shellmode = 1 if expectation else 0

def scan():
  scanner = ZshScanner()
  return scanner.scan()

CMD_PATTERN = re.compile(r'^(\s*)>(\s*)')
INDENT_PATTERN = re.compile(r'^(\s*)')

def is_python_expr(line):
  try:
    parser.expr(line)
    return True
  except:
    return False

def rewrite(cmd, interactive):
  out = []
  for line in cmd.split('\n'):
    if not line:
      continue
    m = CMD_PATTERN.match(line)
    if m:
      body = line[m.end(0):]
      if body:
        out.append('%szsh.run(%s, globals(), locals())' % (
            m.group(1), `body`))
    else:
      indent = INDENT_PATTERN.match(line).group(0)
      line = line[len(indent):]
      if interactive and is_python_expr(line):
        # print expr if intaractive is True.
        formatter = '%sprint %s'
      else:
        formatter = '%s%s'
      out.append(formatter % (indent, line))
  return '\n'.join(out)

def read_and_rewrite(path):
  try:
    return rewrite(file(path, 'r').read(), False)
  except:
    return None

def command():
  cmd = scan().strip()
  cmd = rewrite(cmd, True)
  if not cmd:
    return None
  else:
    return cmd


class Evaluator(zsh.pysh.Evaluator):
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


def run(cmd_str, globals, locals):
  tok = zsh.pysh.Tokenizer(cmd_str, alias_map=alias_map)
  parser = zsh.pysh.Parser(tok)
  evaluator = Evaluator(parser)
  evaluator.execute(globals, locals)
  return evaluator.rc()


class pyzsh_cd(object):
  def process(self, args, input):
    zsh.native.pyzsh_execbuiltin('cd', map(str, args))
    return ()

zsh.pysh.register_pycmd('cd', pyzsh_cd())
