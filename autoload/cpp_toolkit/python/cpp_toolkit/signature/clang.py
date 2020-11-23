from ..utils import *
import vim
import logging
import os.path
import os
import sys
from .struct import *
from .skeleton import *

logger = logging.getLogger("cpp-toolkit.clang")


# initialize clang environment
class ClangIndexer(object):
  def __init__(self, root):
    self.clang_lib = vim_option('cpp_toolkit_clang_library', None)
    if self.clang_lib is None:
      print('You must setup clang!')
    if sys.platform == 'darwin':
      cindex.Config.set_library_file(
        os.path.join(self.clang_lib, 'lib', 'libclang.dylib'))
    else:
      cindex.Config.set_library_file(
        os.path.join(self.clang_lib, 'lib', 'libclang.so'))

    self.compile_database = cindex.CompilationDatabase.fromDirectory(root)
    self.indexer = cindex.Index.create()

  def parse_file(self, filename):
    try:
      file_args = self._get_args_from_compile_database(filename)
      tu = self.indexer.parse(filename, file_args)
      return tu
    except cindex.CompilationDatabaseError:
      print(f"Could not load compilation flags for {filename}")
      return None

  def parse_current(self):
    return self.parse_file(vim.eval('expand("%:p")'))

  def _get_args_from_compile_database(self, filename):
    res = []
    ret = self.compile_database.getCompileCommands(filename)
    _basename = os.path.basename(filename)
    assert isinstance(ret, cindex.CompileCommands)
    logger.info(f'Read compile_database for: {filename}')
    if ret:
      for cmds in ret:
        cwd = cmds.directory
        skip = 0
        last = ''
        for arg in cmds.arguments:
          assert isinstance(arg, str)
          if skip:
            skip = 0
            if len(arg) == 0 or arg[0] != '-':
              continue
          if arg == '-o' or arg == '-c':
            skip = 1
            continue

          if arg != '-I' and arg.startswith('-I'):
            include_path = arg[2:]
            if not os.path.isabs(include_path):
              include_path = os.path.normpath(os.path.join(cwd, include_path))
            res.append(f'-I{include_path}')
          elif arg != '-isystem' and arg.startswith('-isystem'):
            include_path = arg[8:]
            if not os.path.isabs(include_path):
              include_path = os.path.normpath(os.path.join(cwd, include_path))
            res.append(f'-isystem{include_path}')
          elif _basename in arg:
            continue
          else:
            # if last added switch was standalone include then we need to append
            # path to it
            if last == '-I' or last == '-isystem':
              include_path = arg
              if not os.path.isabs(include_path):
                include_path = os.path.normpath(os.path.join(cwd, include_path))
              res[len(res) - 1] += include_path
              last = ''
            else:
              res.append(arg)
              last = arg
    else:
      print(
        f'Could not find compile flags for {filename} in compilation database')
    res.extend(
      [f'-isystem{x}' for x in self._clang_include_path()]
    )
    res.extend(
      [f'-isystem{x}' for x in macos_active_toolchain()]
    )
    return res

  def _clang_include_path(self):
    p = os.path.join(self.clang_lib, 'lib', 'clang')
    res = []
    for f in os.listdir(p):
      if os.path.isdir(os.path.join(p, f)):
        res.append(os.path.join(p, f))
    return [
      os.path.join(x, 'include')
      for x in res
    ]


_cached_indexer = {}


def current_clang_indexer() -> ClangIndexer:
  root = current_project_root()
  global _cached_indexer
  if root in _cached_indexer:
    return _cached_indexer[root]
  _cached_indexer[root] = ClangIndexer(root)
  return _cached_indexer[root]


def node_under_cursor() -> cindex.Cursor:
  tu = current_clang_indexer().parse_current()
  line, col = current_line(), current_column()
  filename = current_file()

  return cindex.Cursor.from_location(tu, cindex.SourceLocation.from_position(
    tu, cindex.File.from_name(tu, filename), line, col
  ))


_current_marked_function = None


def mark_current_function():
  cursor = node_under_cursor()
  kind: cindex.CursorKind = cursor.kind

  if kind not in FunctionInfo._all_func_kinds:
    print('Current position is not a function decl! It\'s', kind)
    return

  global _current_marked_function
  _current_marked_function = FunctionInfo(cursor)


def current_namespace():
  cursor = node_under_cursor()

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
    ns = current_namespace()
    print("Generate function define in ns:", ns)
    buf = _current_marked_function.stringify(ns)
    line_count = len(buf)
    cur = current_line()
    vim.current.buffer.append(buf, cur)
    vim.command(f'call cursor({cur + line_count - 1}, 0)')
