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

def scan():
  scanner = ZshScanner()
  return scanner.scan()

CMD_PATTERN = re.compile(r'^(\s*)\|(\s*)')

def rewrite(cmd):
  out = []
  for line in cmd.split('\n'):
    if not line:
      continue
    m = CMD_PATTERN.match(line)
    if m:
      out.append('%szsh.pysh.run(%s, globals(), locals(),'
                 'alias_map=zsh.alias_map)' % (
          m.group(1), `line[m.end(0):]`))
    else:
      out.append(line)
  return '\n'.join(out)

def command():
  cmd = scan().strip()
  cmd = rewrite(cmd)
  if not cmd:
    return None
  else:
    return cmd


class AliasMap(object):
  def __contains__(self, key):
    result = zsh.native.pyzsh_lookupalias(key)
    return result is not None

  def __getitem__(self, key):
    return (zsh.native.pyzsh_lookupalias(key),
            zsh.native.pyzsh_isaliasglobal(key) != 0)

alias_map = AliasMap()

class pyzsh_cd(object):
  def process(self, args, input):
    zsh.native.pyzsh_execbuiltin('cd', map(str, args))
    return ()

zsh.pysh.register_pycmd('cd', pyzsh_cd())
