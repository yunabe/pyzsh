%{
#include "zsh.mdh"

static const char* pyzsh_lookupalias(const char* text) {
  Alias an = (Alias) aliastab->getnode(aliastab, text);
  if (!an) {
    return NULL;
  }
  return an->text;
}

static int pyzsh_isaliasglobal(const char* text) {
  Alias an = (Alias) aliastab->getnode(aliastab, text);
  if (an && (an->node.flags & ALIAS_GLOBAL)) {
    return 1;
  } else {
    return 0;
  }
}
%}

const char* pyzsh_lookupalias(const char* text);
int pyzsh_isaliasglobal(const char* text);

int lexstop;
int errflag;
int isfirstln;
int curindentwidth;

int hgetc(void);
void closedumps(void);
void cmdpush(int cmdtok);
void cmdpop(void);
