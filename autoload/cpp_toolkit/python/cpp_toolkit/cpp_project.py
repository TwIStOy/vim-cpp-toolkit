import os
import os.path
from typing import List, Optional
import subprocess
import itertools


def is_project_root(p: str, custom_markers: List[str]) -> bool:
  search_in_order = [os.path.join(p, marker) for marker in custom_markers]
  for patten in search_in_order:
    if os.path.exists(patten):
      return True
  return False


_default_project_marker = [
    '.include_hints',
    'CMakeLists.txt',
    '.git',
]

def project_root(p: str,
                 markers: List[str] = _default_project_marker) -> Optional[str]:
  def _resolve_internal(current: str, marker: str) -> Optional[str]:
    if not os.path.split(current)[1]:
      return None
    if is_project_root(current, [marker]):
      return current
    return _resolve_internal(os.path.split(current)[0], marker)

  for marker in markers:
    root = _resolve_internal(p, marker)
    if root is not None:
      return root

  return None


