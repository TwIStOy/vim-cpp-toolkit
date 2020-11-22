from typing import List

from clang import cindex
from clang.cindex import CursorKind

from .struct import TypeInfo
from .debug import *




class Skeleton(object):
  _all_func_kinds = [
    CursorKind.CXX_METHOD,
    CursorKind.FUNCTION_TEMPLATE,
    CursorKind.FUNCTION_DECL,
  ]

  _all_template_arg_kinds = [
    CursorKind.TEMPLATE_TYPE_PARAMETER,
    CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
    CursorKind.TEMPLATE_TEMPLATE_PARAMETER,
  ]

  _all_struct_kinds = [
    CursorKind.CLASS_DECL,
    CursorKind.STRUCT_DECL,
    CursorKind.CLASS_TEMPLATE,
  ]

  def __init__(self, cursor: cindex.Cursor, ns):
    assert cursor.kind in Skeleton._all_func_kinds
    self.ns = ns
    if cursor.semantic_parent.kind in Skeleton._all_struct_kinds:
      cls_cursor: cindex.Cursor = cursor.semantic_parent
      print_cursor_recursive(cls_cursor)
      # method
      self.cls = {
        'template': Skeleton._tpl_args(cls_cursor, ns),
        'name': TypeInfo._full_qualified_name(cls_cursor),
        'params': Skeleton._tpl_param(cls_cursor)
      }
    else:
      self.cls = None
    self.template_arguments = self._tpl_args(cursor, ns)
    self.arguments = [TypeInfo(x.type) for x in cursor.get_arguments()]
    self.result = TypeInfo(cursor.result_type)

    print(self.cls)
    print(self.template_arguments)
    print(self.arguments)
    print(self.result)

  @staticmethod
  def _tpl_args(cursor: cindex.Cursor, ns):
    return [
      Skeleton._generate_tpl(sub, ns)
      for sub in cursor.get_children()
      if sub.kind in Skeleton._all_template_arg_kinds
    ]

  @staticmethod
  def _tpl_param(cursor: cindex.Cursor):
    return [
      Skeleton._generate_param(sub)
      for sub in cursor.get_children()
      if sub.kind in Skeleton._all_template_arg_kinds
    ]

  def generate(self) -> str:
    result_lines = []

    if self.cls is not None:
      tpl = 'template<{}>'
      result_lines.append(tpl.format(", ".join(self.cls['template'])))

    if self.template_arguments:
      tpl = 'template<{}>'
      result_lines.append(tpl.format(", ".join(self.template_arguments)))

    result_lines.append(str(self.result))
    if self.cls:
      typename = '::'.join(self.cls['name'])
      tpl = f"<{', '.join(self.cls['params'])}>" if self.cls["params"] else ""
      result_lines.append(f'::{typename}{tpl}')

    return '\n'.join(result_lines)

  @staticmethod
  def _generate_tpl_TEMPLATE_TYPE_PARAMETER(cursor: cindex.Cursor, ns):
    return f'template {cursor.spelling}'

  @staticmethod
  def _generate_param_TEMPLATE_TYPE_PARAMETER(cursor: cindex.Cursor):
    return cursor.spelling

  @staticmethod
  def _generate_tpl_TEMPLATE_NON_TYPE_PARAMETER(cursor: cindex.Cursor, ns):
    return f'{TypeInfo(cursor.type).stringify(ns)} {cursor.spelling}'

  @staticmethod
  def _generate_param_TEMPLATE_NON_TYPE_PARAMETER(cursor: cindex.Cursor):
    return cursor.spelling

  @staticmethod
  def _generate_tpl_TEMPLATE_TEMPLATE_PARAMETER(cursor: cindex.Cursor, ns):
    sub = [Skeleton._generate_tpl(c, ns) for c in cursor.get_children()]
    return f"template<{','.join(sub)}> class {cursor.spelling}"

  @staticmethod
  def _generate_param_TEMPLATE_TEMPLATE_PARAMETER(cursor: cindex.Cursor):
    sub = [Skeleton._generate_param(c) for c in cursor.get_children()]
    return f'{cursor.spelling}<{",".join(sub)}>'

  @staticmethod
  def _generate_tpl(cursor: cindex.Cursor, ns: List[str]) -> str:
    def _dummy(*args, **kwargs):
      return ""

    return getattr(Skeleton,
                   f'_generate_tpl_{cursor.kind.name}')(cursor, ns)
  @staticmethod
  def _generate_param(cursor: cindex.Cursor) -> str:
    def _dummy(*args, **kwargs):
      return "FUCK!"

    return getattr(Skeleton,
                   f'_generate_param_{cursor.kind.name}')(cursor)
