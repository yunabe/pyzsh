import os
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
        self.first = False
      return c

def scan():
  scanner = ZshScanner()
  return scanner.scan()

def run():
  cmd = scan()
  if cmd.startswith(':'):
    print eval(cmd[1:])
  else:
    os.system(cmd)
  sys.stderr.flush()
  sys.stdout.flush()
