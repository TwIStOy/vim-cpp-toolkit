import os
import os.path
from typing import List


def is_project_root(p: str, custom_markers: List[str]) -> bool:
  search_in_order = [os.path.join(p, marker) for marker in custom_markers]
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
