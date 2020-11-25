from typing import List

from clang import cindex

from .base import TypeAdapter


@TypeAdapter.adapt(cindex.TypeKind.ELABORATED)
class Elaborated(TypeAdapter):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)
        self.named_type = TypeAdapter.create(self.tp.get_named_type())

    def stringify(self, ns: List[str]) -> str:
        if self.tp.get_named_type().kind == cindex.TypeKind.UNEXPOSED:
            return self.tp.spelling
        return self.qualifiers + self.named_type.stringify(ns)


@TypeAdapter.adapt(cindex.TypeKind.UNEXPOSED)
class Unexposed(TypeAdapter):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)

    def stringify(self, ns: List[str]) -> str:
        return self.tp.spelling


