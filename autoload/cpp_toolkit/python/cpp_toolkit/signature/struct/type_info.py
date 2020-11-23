from clang import cindex


_reference_or_pointer_type = {
  cindex.TypeKind.POINTER: '*',
  cindex.TypeKind.LVALUEREFERENCE: '&',
  cindex.TypeKind.RVALUEREFERENCE: '&&',
}


# if tp is this kind, find its full path via get_declaration()
_actual_decl_kinds = [
  cindex.TypeKind.TYPEDEF_DECL,
  cindex.TypeKind.TYPEDEF,
  cindex.TypeKind.UNEXPOSED.
  cindex.TypeKind.RECORD,
]


class TypeInfo(object):
  def __init__(self, tp: cindex.Type):
    self.tp = tp
    self.pointee = None
    self.actual_decl = None

    if self.tp.kind == cindex.TypeKind.ELABORATED:
      self.actual_decl = TypeInfo(self.tp.get_named_type())
    elif self.tp.kind in _reference_or_pointer_type:
      self.pointee = (TypeInfo(self.tp.get_pointee()),
                      _reference_or_pointer_type[self.tp.kind])
    elif self.tp.kind in _actual_decl_kinds:
      self.decl_cursor: cindex.Cursor = self.tp.get_declaration()
      self.parent = self.decl_cursor.semantic_parent
    else:
      assert False

  @staticmethod
  def _full_qualified_name(cursor: cindex.Cursor):
    if cursor is None:
      return []
    elif cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
      return []
    else:
      tmp = TypeInfo._full_qualified_name(cursor.semantic_parent) + [
        cursor.spelling
      ]
      return [x for x in tmp if x]


