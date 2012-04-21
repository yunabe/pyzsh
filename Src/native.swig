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

static int pyzsh_execbuiltin(const char* cmd, LinkList args) {
  HashNode hn = (HashNode) builtintab->getnode(builtintab, cmd);
  if (hn) {
    return execbuiltin(args, (Builtin) hn);
  } else {
    return -1;
  }
}

static void pyzsh_child_unblock(void) {
  child_unblock();
}

%}

%typemap(in) LinkList {
  $1 = newlinklist();
  PyObject* iter = PyObject_GetIter($input);
  if (!iter) {
    PyErr_Clear();
  } else {
    PyObject* item;
    while (item = PyIter_Next(iter)) {
      if (PyString_Check(item)) {
        addlinknode($1, PyString_AsString(item));
      }
      Py_DECREF(item);
    }
    Py_DECREF(iter);
  }
}

const char* pyzsh_lookupalias(const char* text);
int pyzsh_isaliasglobal(const char* text);
int pyzsh_execbuiltin(const char* cmd, LinkList args);

int lexstop;
int errflag;
int isfirstln;
int curindentwidth;
int expect_shellmode;

int hgetc(void);
void closedumps(void);
void cmdpush(int cmdtok);
void cmdpop(void);

void hwbegin(int offset);
void hwend(void);

void pyzsh_child_unblock(void);
