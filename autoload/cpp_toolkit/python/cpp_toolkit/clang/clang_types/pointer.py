from typing import List

from clang import cindex

from .base import *


@TypeAdapter.adapt(cindex.TypeKind.POINTER)
class Pointer(TypeAdapter):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)
        self.pointee = TypeAdapter.create(tp.get_pointee())

    def stringify(self, ns: List[str]) -> str:
        # TODO(hawtian): FUNCTIONPROTO
        #                  void (*)(int)
        return f'{self.qualifiers}{self.pointee.stringify(ns)} *'


@TypeAdapter.adapt(cindex.TypeKind.LVALUEREFERENCE)
class LValueReference(Pointer):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)
        self.pointee = TypeAdapter.create(tp.get_pointee())

    def stringify(self, ns: List[str]) -> str:
        # TODO(hawtian): FUNCTIONPROTO
        #                  void (*)(int)
        return f'{self.qualifiers}{self.pointee.stringify(ns)} &'



@TypeAdapter.adapt(cindex.TypeKind.RVALUEREFERENCE)
class RValueReference(Pointer):
    def __init__(self, tp: cindex.Type):
        super().__init__(tp)
        self.pointee = TypeAdapter.create(tp.get_pointee())

    def stringify(self, ns: List[str]) -> str:
        # TODO(hawtian): FUNCTIONPROTO
        #                  void (*)(int)
        return f'{self.qualifiers}{self.pointee.stringify(ns)} &&'



