import abc
from typing import List

from clang import cindex


class Printable(object):
    @abc.abstractclassmethod
    def stringify(self, ns: List[str]) -> str:
        pass


class CursorAdapter(Printable):
    _reg = {}

    @staticmethod
    def adapt(kind: cindex.CursorKind):
        def wrapper(tp):
            CursorAdapter._reg[kind] = tp
            return tp
        return wrapper

    @staticmethod
    def create(cursor: cindex.Cursor):
        func = CursorAdapter._reg.get(cursor.kind, None)
        if func is None:
            return None
        return func(cursor)

    def __init__(self, cursor: cindex.Cursor):
        assert isinstance(cursor, cindex.Cursor)
        self.cursor = cursor

    @abc.abstractclassmethod
    def stringify_as_typename(self, ns: List[str]) -> str:
        pass

    @property
    def full_name_path(self) -> List[str]:
        cursor = self.cursor
        res = []
        while cursor.kind != cindex.CursorKind.TRANSLATION_UNIT:
            res.append(cursor.spelling)
            cursor = cursor.semantic_parent
        res.reverse()
        return res




class TypeAdapter(Printable):
    _reg = {}

    @staticmethod
    def adapt(*args):
        def wrapper(tp):
            for kind in args:
                TypeAdapter._reg[kind] = tp
            return tp
        return wrapper

    @staticmethod
    def create(tp: cindex.Type):
        func = TypeAdapter._reg.get(tp.kind, None)
        if func is None:
            return None
        return func(tp)

    def __init__(self, tp: cindex.Type):
        assert isinstance(tp, cindex.Type)
        self.tp = tp
        self._qualifiers = []
        if tp.is_const_qualified():
            self._qualifiers.append('const')
        if tp.is_volatile_qualified():
            self._qualifiers.append('volatile')
        if tp.is_restrict_qualified():
            self._qualifiers.append('restrict')

    @property
    def qualifiers(self):
        return ' '.join(self._qualifiers)


def common_index(name_path: List[str], ns: List[str]) -> int:
    _common_index = 0
    for lhs, rhs in zip(name_path, ns):
        if lhs == rhs:
            _common_index += 1
    return _common_index
