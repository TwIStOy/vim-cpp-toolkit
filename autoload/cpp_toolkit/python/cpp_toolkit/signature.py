import logging

import vim
from clang import cindex

from .clang.clang_types import CursorAdapter, TypeAdapter
from .clang.indexer import ClangIndexer
from .utils import *


def _current_clang_indexer() -> ClangIndexer:
    root = current_project_root()
    return ClangIndexer.create(root)


_clang_path = None
def _node_under_cursor():
    global _clang_path
    if _clang_path is None:
        _clang_path = vim_option('cpp_toolkit_clang_library', None)
    if _clang_path is not None:
        ClangIndexer.SetLibraryPath(_clang_path)

    tu = _current_clang_indexer().parse_file(current_file(),
                                             get_unsaved_buffer())

    line, col = current_line(), current_column()
    filename = current_file()

    return cindex.Cursor.from_location(tu, cindex.SourceLocation.from_position(
      tu, cindex.File.from_name(tu, filename), line, col
    ))


_current_marked_function = None


_func_kinds = [
    cindex.CursorKind.CONSTRUCTOR,
    cindex.CursorKind.CXX_METHOD,
    cindex.CursorKind.DESTRUCTOR,
    cindex.CursorKind.FUNCTION_DECL,
    cindex.CursorKind.FUNCTION_TEMPLATE,
]

_class_kinds = [
    cindex.CursorKind.CLASS_DECL,
    cindex.CursorKind.STRUCT_DECL,
    cindex.CursorKind.CLASS_TEMPLATE,
]

def mark_current():
    global _current_marked_function
    cursor: cindex.Cursor = _node_under_cursor()
    kind: cindex.CursorKind = cursor.kind

    if cursor.kind in _func_kinds:
        _current_marked_function = CursorAdapter.create(cursor)
        assert _current_marked_function is not None
    elif cursor.kind in _class_kinds:
        _current_marked_function = [
            CursorAdapter.create(c)
            for c in cursor.get_children()
            if c.kind in _func_kinds
        ]
    else:
        print('Current position is not supported decl! It\'s', kind)


def _current_namespace():
    cursor = _node_under_cursor()

    res = []
    while (cursor is not None and
           cursor.kind != cindex.CursorKind.TRANSLATION_UNIT):
        if cursor.kind == cindex.CursorKind.NAMESPACE:
            res.append(cursor.spelling)
        cursor = cursor.semantic_parent

    res.reverse()
    return res


def generate_here():
    global _current_marked_function
    if _current_marked_function is not None:
        ns = _current_namespace()
    else:
        print('Please mark function first!')
        return
    print("Generate function define in ns:", ns)
    if not isinstance(_current_marked_function, list):
        buf = _current_marked_function.stringify(ns).split('\n')
        line_count = len(buf)
    else:
        buf = [x.stringify(ns) for x in _current_marked_function]
        buf = "\n\n".join(buf)
        buf = buf.split('\n')
        line_count = 1

    cur = current_line()
    vim.current.buffer.append(buf, cur)
    vim.command(f'call cursor({cur + line_count - 1}, 0)')
