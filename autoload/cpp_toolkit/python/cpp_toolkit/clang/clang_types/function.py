from typing import List

from clang import cindex

from .base import CursorAdapter, TypeAdapter, common_index


class _FunctionBase(CursorAdapter):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.parent = CursorAdapter.create(cursor.semantic_parent)
        self.arguments = [
            (TypeAdapter.create(x.type), x.spelling)
            for x in cursor.get_arguments()
        ]
        self.result_type = TypeAdapter.create(cursor.result_type)


class _NonTemplateFunction(_FunctionBase):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)

    def stringify(self, ns: List[str]) -> str:
        res = []
        if self.parent is not None:
            res.append(self.parent.stringify(ns))
        if self.result_type is not None:
            res.append(self.result_type.stringify(ns))
        if self.parent is not None:
            func_name = f'{self.parent.stringify_as_typename(ns)}' \
                        f'::{self.cursor.spelling}'
        else:
            name = self.full_name_path
            idx = common_index(name, ns)
            func_name = f'{"::".join(name[idx:])}'
        args = [f'{arg[0].stringify(ns)} {arg[1]}' for arg in self.arguments]
        qualifiers = ''
        if self.cursor.is_const_method():
            qualifiers = ' const'
        args_str = ', '.join(args)
        res.append(f'{func_name}({args_str}){qualifiers} ' + '{')
        res.append('')
        res.append('}')
        res_str = "\n".join(res)
        return res_str.strip()


@CursorAdapter.adapt(cindex.CursorKind.CONSTRUCTOR)
class Constructor(_NonTemplateFunction):
    pass


@CursorAdapter.adapt(cindex.CursorKind.CXX_METHOD)
class CxxMethod(_NonTemplateFunction):
    pass


@CursorAdapter.adapt(cindex.CursorKind.DESTRUCTOR)
class Destructor(_NonTemplateFunction):
    pass


@CursorAdapter.adapt(cindex.CursorKind.FUNCTION_DECL)
class FunctionDecl(_NonTemplateFunction):
    pass


@CursorAdapter.adapt(cindex.CursorKind.FUNCTION_TEMPLATE)
class FunctionTemplate(_FunctionBase):
    def __init__(self, cursor: cindex.Cursor):
        super().__init__(cursor)
        self.template_arguments = [
            CursorAdapter.adapt(c) for c in cursor.get_children()]

    def stringify(self, ns: List[str]) -> str:
        res = []
        if self.parent is not None:
            res.append(self.parent.stringify(ns))
        sub = [c.stringify(ns) for c in self.template_arguments]
        res.append(f'template<{",".join(sub)}>')
        if self.result_type is not None:
            res.append(self.result_type.stringify(ns))
        if self.parent is not None:
            func_name = f'{self.parent.stringify_as_typename(ns)}' \
                        f'::{self.cursor.spelling}'
        else:
            name = self.full_name_path
            idx = common_index(name, ns)
            func_name = f'{"::".join(name[idx:])}'
        args = [f'{arg[0].stringify(ns)} {arg[1]}' for arg in self.arguments]
        qualifiers = ''
        if self.cursor.is_const_method():
            qualifiers = ' const'
        args_str = ', '.join(args)
        res.append(f'{func_name}({args_str}){qualifiers} ' + '{')
        res.append('')
        res.append('}')
        res_str = "\n".join(res)
        return res_str.strip()

