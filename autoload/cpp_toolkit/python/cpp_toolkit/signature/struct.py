from typing import List

from clang import cindex


def _remove_common_index(lst: List[str], ns: List[str]) -> (int, List[str]):
  common_index = 0
  for lhs, rhs in zip(lst, ns):
    if lhs == rhs:
      common_index += 1
    else:
      break
  return common_index, lst[common_index:]


class TypeInfo(object):
  _reference_or_pointer_type = [
    cindex.TypeKind.POINTER,
    cindex.TypeKind.LVALUEREFERENCE,
    cindex.TypeKind.RVALUEREFERENCE,
  ]
  def __init__(self, tp: cindex.Type):
    self.tp = tp
    if self.tp.kind in self._reference_or_pointer_type:
      # reference type
      self.pointee = TypeInfo(self.tp.get_pointee())
    else:
      self.pointee = None
      self.full_qualified_name = self._full_qualified_name(tp.get_declaration())
      self.qualifiers = []
      self.alias = self.tp.get_typedef_name()
      if tp.is_const_qualified():
        self.qualifiers.append('const')
      if tp.is_volatile_qualified():
        self.qualifiers.append('volatile')
      if tp.is_restrict_qualified():
        self.qualifiers.append('restrict')
      self.template_arguments = None
      if self.tp.get_num_template_arguments() > 0:
        self.template_arguments = []
        for i in range(self.tp.get_num_template_arguments()):
          self.template_arguments.append(
            TypeInfo(self.tp.get_template_argument_type(i)))

  @staticmethod
  def _full_qualified_name(cursor: cindex.Cursor):
    """
    Split namespaces
    """
    if cursor is None:
      return []
    elif cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
      return []
    else:
      tmp = TypeInfo._full_qualified_name(cursor.semantic_parent) + [
        cursor.spelling
      ]
      return [x for x in tmp if x]

  def stringify(self, ns: List[str]) -> str:
    if self.pointee:
      if self.tp.kind == cindex.TypeKind.POINTER:
        return self.pointee.stringify(ns) + '*'
      if self.tp.kind == cindex.TypeKind.LVALUEREFERENCE:
        return self.pointee.stringify(ns) + '&'
      if self.tp.kind == cindex.TypeKind.RVALUEREFERENCE:
        return self.pointee.stringify(ns) + '&&'
    else:
      if self.full_qualified_name:
        # custom type
        _, printable_name = _remove_common_index(self.full_qualified_name, ns)
        if self.template_arguments:
          parameters = [arg.stringify(ns) for arg in self.template_arguments]
          tpl_parameter = f'<{", ".join(parameters)}>' \
            if self.template_arguments else ''
        else:
          tpl_parameter = ''
        return " ".join(self.qualifiers) + ' ' + "::".join(printable_name) + tpl_parameter
      else:
        # builtin type
        return self.tp.spelling


class TemplateArgumentInfo(object):
  _all_template_arg_kinds = [
    cindex.CursorKind.TEMPLATE_TYPE_PARAMETER,
    cindex.CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
    cindex.CursorKind.TEMPLATE_TEMPLATE_PARAMETER,
  ]

  def __init__(self, cursor: cindex.Cursor):
    assert cursor.kind in self._all_template_arg_kinds
    self.cursor = cursor
    self.children = []
    if self.cursor.kind == cindex.CursorKind.TEMPLATE_TEMPLATE_PARAMETER:
      self.children = [
        TemplateArgumentInfo(c) for c in self.cursor.get_children()
        if c.kind in self._all_template_arg_kinds
      ]

  def stringify(self, ns) -> str:
    if self.cursor.kind == cindex.CursorKind.TEMPLATE_TYPE_PARAMETER:
      return f'typename {self.cursor.spelling}'
    elif self.cursor.kind == cindex.CursorKind.TEMPLATE_NON_TYPE_PARAMETER:
      return f'{TypeInfo(self.cursor.type).stringify(ns)} {self.cursor.spelling}'
    else:
      sub = [c.stringify(ns) for c in self.children]
      return f'template<{", ".join(sub)}> class {self.cursor.spelling}'

  def stringify_as_param(self) -> str:
    if self.cursor.kind == cindex.CursorKind.TEMPLATE_TYPE_PARAMETER:
      return self.cursor.spelling
    elif self.cursor.kind == cindex.CursorKind.TEMPLATE_NON_TYPE_PARAMETER:
      return self.cursor.spelling
    else:
      sub = [c.stringify_as_param() for c in self.children]
      return f'{self.cursor.spelling}<{", ".join(sub)}>'


class ClassInfo(object):
  _all_struct_kinds = [
    cindex.CursorKind.CLASS_DECL,
    cindex.CursorKind.STRUCT_DECL,
    cindex.CursorKind.CLASS_TEMPLATE,
  ]

  def __init__(self, cursor: cindex.Cursor):
    assert cursor.kind in self._all_struct_kinds
    self.cursor = cursor
    self.parent = ClassInfo(cursor.semantic_parent) \
      if cursor.semantic_parent.kind in self._all_struct_kinds else None
    self.name = TypeInfo._full_qualified_name(cursor)
    if cursor.kind == cindex.CursorKind.CLASS_TEMPLATE:
      self.template_arguments = [
        TemplateArgumentInfo(c)
        for c in cursor.get_children()
        if c.kind in TemplateArgumentInfo._all_template_arg_kinds
      ]
    else:
      self.template_arguments = None

  def stringify(self, ns) -> List[str]:
    res = []
    if self.parent:
      res.extend(self.parent.stringify(ns))
    if self.template_arguments is not None:
      tpl_args = [c.stringify(ns) for c in self.template_arguments]
      res.append(f'template<{",".join(tpl_args)}>')
    return res

  def stringify_as_mark(self, ns) -> str:
    res = ""
    if self.parent:
      res = self.parent.stringify_as_mark(ns) + "::"
    else:
      common_idx, name = _remove_common_index(self.name, ns)
      if common_idx == 0:
        res = "::" + '::'.join(name[:-1])
      else:
        res = "::".join(name[:-1])
    res += ("::" if res else '') + self.cursor.spelling
    if self.template_arguments is not None:
      sub = [
        c.stringify_as_param() for c in self.template_arguments
      ]
      res += f'<{", ".join(sub)}>'
    return res


class FunctionInfo(object):
  _all_func_kinds = [
    cindex.CursorKind.CXX_METHOD,
    cindex.CursorKind.FUNCTION_TEMPLATE,
    cindex.CursorKind.FUNCTION_DECL,
    cindex.CursorKind.DESTRUCTOR,
    cindex.CursorKind.CONSTRUCTOR,
  ]

  def __init__(self, cursor: cindex.Cursor):
    assert cursor.kind in self._all_func_kinds
    self.cursor = cursor
    self.full_qualified_name = TypeInfo._full_qualified_name(cursor)
    if cursor.semantic_parent.kind in ClassInfo._all_struct_kinds:
      self.parent = ClassInfo(cursor.semantic_parent)
    else:
      self.parent = None
    self.arguments = [
      (TypeInfo(x.type), x.spelling) for x in cursor.get_arguments()
    ]
    self.result_type = TypeInfo(cursor.result_type)
    if cursor.kind == cindex.CursorKind.FUNCTION_TEMPLATE:
      self.template_arguments = [
        TemplateArgumentInfo(c)
        for c in cursor.get_children()
        if c.kind in TemplateArgumentInfo._all_template_arg_kinds
      ]
    else:
      self.template_arguments = None

  def stringify(self, ns) -> List[str]:
    res = []
    if self.parent is not None:
      res.extend(self.parent.stringify(ns))
    if self.template_arguments is not None:
      sub = [c.stringify(ns) for c in self.template_arguments]
      res.append(f'template<{",".join(sub)}>')
    res.append(self.result_type.stringify(ns))
    if self.parent is not None:
      func_name = f'{self.parent.stringify_as_mark(ns)}::{self.cursor.spelling}'
    else:
      # not a cls method, namespace marker should on function its self
      _, name = _remove_common_index(self.full_qualified_name, ns)
      func_name = f'{"::".join(name)}'
    args = [f'{arg[0].stringify(ns)} {arg[1]}' for arg in self.arguments]
    qualifiers = []
    if self.cursor.is_const_method():
      qualifiers.append(' const')
    res.append(f'{func_name}({",".join(args)})' + "".join(qualifiers) +  ' {')
    res.append('')
    res.append("}")
    return res
