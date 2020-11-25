from typing import List

from clang import cindex

from .base import CursorAdapter, Printable, common_index


class ClassBase(CursorAdapter):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        p = CursorAdapter.create(cursor.semantic_parent)
        self.parent = p if isinstance(p, ClassBase) else None

    def stringify(self, ns: List[str]) -> str:
        if self.parent:
            return self.parent.stringify(ns)
        return ''

    def stringify_as_typename(self, ns: List[str]) -> str:
        res = ""
        if self.parent:
            res = self.parent.stringify_as_typename(ns)
            res += "::" + self.cursor.spelling
        else:
            full_name_path = self.full_name_path
            idx = common_index(full_name_path, ns)
            res = "::".join(full_name_path[idx:])
        return res



@CursorAdapter.adapt(cindex.CursorKind.CLASS_DECL)
class ClassDecl(ClassBase):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)


@CursorAdapter.adapt(cindex.CursorKind.STRUCT_DECL)
class StructDecl(ClassBase):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)


@CursorAdapter.adapt(cindex.CursorKind.CLASS_TEMPLATE)
class ClassTemplate(ClassBase):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.template_arguments = []
        for x in cursor.get_children():
            param = CursorAdapter.create(x)
            if param is not None:
                self.template_arguments.append(param)

    def stringify(self, ns: List[str]) -> str:
        res = super().stringify(ns)
        args = ",".join([x.stringify(ns) for x in self.template_arguments])
        res += f'\ntemplate<{args}>'
        return res

    def stringify_as_typename(self, ns: List[str]) -> str:
        res = super().stringify_as_typename(ns)
        args = ",".join([x.stringify_as_typename(ns) for x in self.template_arguments])
        res += f'<{args}>'
        return res
