import clang
from clang import cindex
from .type_info import TypeInfo

class Param(object):
  def __init__(self, cursor: cindex.Cursor):
    assert cursor.kind == cindex.CursorKind.PARM_DECL

  def stringify(self, ns: List[str]) -> str:
    pass



# vim: sw=2 ts=2

