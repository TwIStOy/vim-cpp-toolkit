from typing import List

from clang import cindex

from .base import CursorAdapter, Printable, TypeAdapter


class _TemplateInfoBase(CursorAdapter):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)


@CursorAdapter.adapt(cindex.CursorKind.TEMPLATE_TYPE_PARAMETER)
class TemplateTypeParameter(CursorAdapter):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)

    def stringify(self, ns: List[str]) -> str:
        return f'typename {self.cursor.spelling}'

    def stringify_as_typename(self, ns):
        return self.cursor.spelling


@CursorAdapter.adapt(cindex.CursorKind.TEMPLATE_NON_TYPE_PARAMETER)
class TemplateNoneTypeParameter(CursorAdapter):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.param_type = TypeAdapter.create(self.cursor.type)

    def stringify(self, ns: List[str]) -> str:
        return f'{self.param_type.stringify(ns)} {self.cursor.spelling}'

    def stringify_as_typename(self, ns):
        return self.cursor.spelling


@CursorAdapter.adapt(cindex.CursorKind.TEMPLATE_TEMPLATE_PARAMETER)
class TemplateTemplateParameter(CursorAdapter):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.arguments: List[_TemplateInfoBase] = []
        for c in self.cursor.get_children():
            assert isinstance(c, cindex.Cursor)
            cc: cindex.Cursor = c
            param = CursorAdapter.create(cc)
            if param is not None:
                self.arguments.append(param)

    def stringify(self, ns: List[str]) -> str:
        arg_str = ','.join([
            x.stringify(ns)
            for x in self.arguments
        ])
        return f'template<{arg_str}> class {self.cursor.spelling}'

    def stringify_as_typename(self, ns):
        arguments_stringify = ','.join([
            x.stringify_as_typename(ns)
            for x in self.arguments
        ])
        return f'{self.cursor.spelling}<{arguments_stringify}>'
