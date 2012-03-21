import os
import parser
import re
import sys
from StringIO import StringIO

import zsh.native
from zsh.native import hgetc
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
      c = chr(hgetc())
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
      out.append('%szsh.pysh.run(%s, globals(), locals())' % (
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
