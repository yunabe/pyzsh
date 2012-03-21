%{
#include "zsh.mdh"
%}

int lexstop;
int errflag;
int isfirstln;
int curindentwidth;

int hgetc(void);
void closedumps(void);
void cmdpush(int cmdtok);
void cmdpop(void);
