import os
import sys
from StringIO import StringIO

import zsh.native
from zsh.native import hgetc

def scan():
  w = StringIO()
  while True:
    c = hgetc()
    if c == ord('\n') or zsh.native.cvar.lexstop:
      break
    w.write(chr(c))
  return w.getvalue()

def run():
  os.system(scan())
