import os.path
from .cpp_project import *
import vim
import sys
import subprocess
import os


def macos_active_toolchain():
  if sys.platform == 'darwin':
    res = subprocess.run(['xcode-select', '-p'], stdout=subprocess.PIPE)
    toolchains_path = os.path.join(
      res.stdout.decode('utf-8').strip(), 'Toolchains')
    res = []
    for folder in os.listdir(toolchains_path):
      if os.path.isdir(os.path.join(toolchains_path, folder)):
        res.append(
          os.path.join(toolchains_path, folder, 'usr', 'include', 'c++', 'v1'))
    return res
  return []


def vim_option(option_name, default_value):
  if int(vim.eval(f'exists("g:{option_name}")')) == 1:
    return vim.eval(f'get(g:, "{option_name}")')
  return default_value


def current_file():
  return vim.eval('expand("%:p")')


def current_project_root():
  dirname, _ = os.path.split(current_file())
  root = project_root(dirname, vim_option('cpp_toolkit_project_marker', []))
  return root


def current_line():
  return int(vim.eval('line(".")'))


def current_column():
  return int(vim.eval('col(".")'))


def ext_associated():
  custom = vim_option('cpp_toolkit_custom_associated', {})
  assert custom is not None
  assert isinstance(custom, dict)
  builtin = {
    '.c': ['.h', '.hh', '.hpp', '.hxx'],
    '.cpp': ['.hpp', '.hxx', '.hh', '.h'],
    '.cc': ['.hh', '.hxx', '.hpp', '.h'],
    '.cxx': ['.hxx', '.hpp', '.hh', '.h'],
    '.h': ['.c', '.cxx', '.cpp', '.cc'],
    '.hh': ['.cc', '.cxx', '.cpp', '.c'],
    '.hpp': ['.cpp', '.cc', '.hxx', '.c'],
    '.hxx': ['.cxx', '.cc', '.hpp', '.c'],
  }
  builtin.update(custom)
  return builtin


def header_folders():
  custom = vim_option('cpp_toolkit_header_folders', [])
  assert custom is not None
  assert isinstance(custom, list)
  builtin = [
    'include',
    ['..', 'include'],
    'inc',
  ]
  custom.extend(builtin)
  return custom


def source_folders():
  custom = vim_option('cpp_toolkit_source_folders', [])
  assert custom is not None
  assert isinstance(custom, list)
  builtin = [
    'src',
    'source',
    'srcs',
    'sources',
  ]
  custom.extend(builtin)
  return custom


def header_extensions():
  custom = vim_option('cpp_toolkit_header_extension', [])
  assert custom is not None
  assert isinstance(custom, list)
  builtin = [
    'h', 'hpp', 'hh', 'hxx'
  ]
  custom.extend(builtin)
  return list(set(custom))


def full_split_path(p: str) -> List[str]:
  first = os.path.normpath(p)
  res = []
  while True:
    first, second = os.path.split(first)
    if second:
      res.append(second)
    elif first:
      res.append(first)
      break
  res.reverse()
  return res


def compare_iterable(lhs, rhs):
  from itertools import zip_longest, tee
  sentinel = object()
  return all(a == b for a, b in zip_longest(lhs, rhs, fillvalue=sentinel))


def get_unsaved_buffer():
  res = []
  for b in vim.buffers:
    if b.options['modified']:
      res.append([
        b.name,
        '\n'.join(b)
      ])
  return res


# vim:sw=2 ts=2
