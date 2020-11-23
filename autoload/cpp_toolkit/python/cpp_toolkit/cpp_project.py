import os
import os.path
from typing import List
import subprocess
from .utils import *
import itertools


def is_project_root(p: str, custom_markers: List[str]) -> bool:
  search_in_order = [os.path.join(p, marker) for marker in custom_markers]
  if not search_in_order:
    # include hint for leaderf-cppinclude
    search_in_order.append(os.path.join(p, '.include_hints'))
    # cmake project
    search_in_order.append(os.path.join(p, 'CMakeLists.txt'))
    # git repo
    search_in_order.append(os.path.join(p, '.git'))

  for patten in search_in_order:
    if os.path.exists(patten):
      return True
  return False


def project_root(p: str, custom_markers: List[str]) -> str:
  current = p
  while os.path.split(current)[1]:
    if is_project_root(current, custom_markers):
      return current
    current = os.path.split(current)[0]
  return p


def filter_header_files(root: str):
  # load '.include_hints' from root
  directories = [root]
  if os.path.exists(os.path.join(root, '.include_hints')):
    with open(os.path.join(root, '.include_hints'), 'r') as fp:
      for line in fp.readlines():
        directories.append(os.path.join(root, line.strip()))

  directories = list(set([os.path.normpath(p) for p in directories]))
  res = []
  for directory in directories:
    ext_args = [['-e', header] for header in header_extensions()]
    ext_args = list(itertools.chain(*ext_args))
    result = subprocess.run(
      ['fd', '-LI'] + ext_args + ['--base-directory', directory],
      stdout=subprocess.PIPE,
      encoding='utf-8'
    )
    res.extend([x.strip() for x in result.stdout.split('\n') if x.strip()])
  return list(set(res))
