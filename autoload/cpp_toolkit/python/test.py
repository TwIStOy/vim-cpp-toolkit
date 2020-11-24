import os
import os.path

import clang
from clang import cindex

import sys
from cpp_toolkit.clang.clang_types import TypeAdapter, CursorAdapter

root = '/home/s3101/agora/ddd/media_build'
libclang = '/home/s3101/llvm/clang+llvm-11.0.0-x86_64-linux-gnu-ubuntu-16.04/lib/libclang.so'


cindex.Config.set_library_file(libclang)
cdb = cindex.CompilationDatabase.fromDirectory(root)

def _clang_include_path():
  return [
      '/home/s3101/llvm/clang+llvm-11.0.0-x86_64-linux-gnu-ubuntu-16.04/lib/clang/11.0.0/include/']

def _get_args_from_compile_database(filename):
  global cdb
  res = []
  ret = cdb.getCompileCommands(filename)
  _basename = os.path.basename(filename)
  assert isinstance(ret, cindex.CompileCommands)
  print(f'Read compile_database for: {filename}')
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
    [f'-isystem{x}' for x in _clang_include_path()]
  )
  return res


def _full_qualified_name(cursor: cindex.Cursor):
  """
  Split namespaces
  """
  if cursor is None:
    return []
  elif cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
    return []
  else:
    tmp = _full_qualified_name(cursor.semantic_parent) + [
      cursor.spelling
    ]
    return [x for x in tmp if x]

filename = '/home/s3101/agora/ddd/media_build/media_server_ddd/ddd/client/client.h'
index = cindex.Index.create()
file_args = _get_args_from_compile_database(filename)
print(file_args)
tu = index.parse(filename, file_args)


cursor = cindex.Cursor.from_location(tu, cindex.SourceLocation.from_position(
    tu, cindex.File.from_name(tu, filename), 84, 16))

print(cursor)

def print_cursor_info(cursor: cindex.Cursor):
  print(f'Cursor: {cursor}, kind={cursor.kind}')



def print_param_decl(cursor: cindex.Cursor):
  assert(cursor.kind == cindex.CursorKind.PARM_DECL)
  for c in cursor.get_children():
    if (c.kind == cindex.CursorKind.TEMPLATE_REF or
        c.kind == cindex.CursorKind.TYPE_REF):
      print("pk,", c.kind)
      print("pc,", c.type)
      print("fd,", _full_qualified_name(c.type.get_declaration()))
      break

print(cursor.kind)
print(CursorAdapter.create(cursor).stringify(['agora', 'ddd']))

# print(CursorAdapter._reg)
# print(TypeAdapter._reg)
for arg in cursor.get_arguments():
  print(f'=== Start: {arg.type.spelling}, {arg.kind}, {arg.type.kind} ===')
  print_cindex_type(arg.type)
  print(f'===  End : {arg.type.spelling} ===')
  print('')

# vim: ts=2 sw=2

