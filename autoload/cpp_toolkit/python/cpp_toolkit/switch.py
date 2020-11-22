import os.path
from itertools import product
from typing import Optional

from .cpp_project import project_root
from .utils import *


def _has_sub_directory(path, sub_directory):
  parts = full_split_path(path)
  if isinstance(sub_directory, str):
    sub_directory = [sub_directory]
  multi_parts = [parts[i:] for i in range(len(sub_directory))]
  for part in zip(*multi_parts):
    if compare_iterable(part, sub_directory):
      return True
  return False


def _replace_sub_directory(path, sub_directory, new_sub_directory):
  assert _has_sub_directory(path, sub_directory)
  if isinstance(sub_directory, str):
    sub_directory = [sub_directory]
  if isinstance(new_sub_directory, str):
    new_sub_directory = [new_sub_directory]
  parts = full_split_path(path)
  multi_parts = list(zip(*[parts[i:] for i in range(len(sub_directory))]))
  res_idx = -1
  for i, part in enumerate(multi_parts):
    if compare_iterable(part, sub_directory):
      res_idx = i
  assert res_idx >= 0
  return os.path.join(
    *(parts[:res_idx] + new_sub_directory + parts[
                                            res_idx + len(sub_directory):])
  )


def corresponding_file() -> Optional[str]:
  import vim
  import json
  current_file = vim.eval('expand("%:p")')
  dirname, filename = os.path.split(current_file)
  root = project_root(dirname, vim_option('cpp_toolkit_project_marker', []))
  basename, ext = os.path.splitext(filename)
  associated_ext = ext_associated().get(ext, None)

  # load switch hints
  project_level_header_folders = []
  project_level_source_folders = []
  switch_hints = os.path.join(root, '.switch_hints')
  if os.path.exists(switch_hints):
    with open(switch_hints, 'r') as fp:
      try:
        project_level_switch_hints = json.load(fp)
        project_level_header_folders = project_level_switch_hints.get(
          'header_folders', [])
        project_level_source_folders = project_level_switch_hints.get(
          'source_folders', [])
      except:
        print('Failed to load project_level switch hints.')

  if associated_ext is None:
    return None

  filename_candidates = [f'{basename}{e}' for e in associated_ext]

  folder_candidates = [dirname]
  if 'h' in ext:
    # header file
    replacer = (
      project_level_header_folders + header_folders(),
      project_level_source_folders + source_folders())
  elif 'c' in ext:
    # source file
    replacer = (
      project_level_source_folders + source_folders(),
      project_level_header_folders + header_folders())

  for src_folder in replacer[0]:
    if _has_sub_directory(dirname, src_folder):
      for dst_folder in replacer[1]:
        folder_candidates.append(_replace_sub_directory(dirname,
                                                        src_folder,
                                                        dst_folder))
  candidates = [
    os.path.join(folder, filename)
    for folder, filename in product(folder_candidates, filename_candidates)
    if os.path.exists(os.path.join(folder, filename))
  ]

  return candidates
