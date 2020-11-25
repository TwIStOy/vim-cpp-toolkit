from clang import cindex

from .base import TypeAdapter, common_index
from typing import List


class _CanResolveFullNamePath(TypeAdapter):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)

    @property
    def full_name_path(self) -> List[str]:
        res = []
        cursor: cindex.Cursor = self.tp.get_declaration()

        while cursor.kind != cindex.CursorKind.TRANSLATION_UNIT:
            res.append(cursor.spelling)
            cursor = cursor.semantic_parent
        res.reverse()
        return res


@TypeAdapter.adapt(
    cindex.TypeKind.VOID,
    cindex.TypeKind.BOOL,
    cindex.TypeKind.CHAR_U,
    cindex.TypeKind.UCHAR,
    cindex.TypeKind.CHAR16,
    cindex.TypeKind.CHAR32,
    cindex.TypeKind.USHORT,
    cindex.TypeKind.UINT,
    cindex.TypeKind.ULONG,
    cindex.TypeKind.ULONGLONG,
    cindex.TypeKind.UINT128,
    cindex.TypeKind.CHAR_S,
    cindex.TypeKind.SCHAR,
    cindex.TypeKind.WCHAR,
    cindex.TypeKind.SHORT,
    cindex.TypeKind.INT,
    cindex.TypeKind.LONG,
    cindex.TypeKind.LONGLONG,
    cindex.TypeKind.INT128,
    cindex.TypeKind.FLOAT,
    cindex.TypeKind.DOUBLE,
    cindex.TypeKind.LONGDOUBLE,
    cindex.TypeKind.NULLPTR,
)
class BuiltinType(TypeAdapter):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)

    def stringify(self, ns: List[str]) -> str:
        return f'{self.qualifiers}{self.tp.spelling}'


@TypeAdapter.adapt(cindex.TypeKind.RECORD)
class Record(_CanResolveFullNamePath):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)

    def stringify(self, ns: List[str]) -> str:
        full_name_path = self.full_name_path
        idx = common_index(full_name_path, ns)
        return self.qualifiers + "::".join(full_name_path[idx:])


@TypeAdapter.adapt(cindex.TypeKind.TYPEDEF)
class Typedef(Record):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)



@TypeAdapter.adapt(cindex.TypeKind.ENUM)
class Enum(Record):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)

