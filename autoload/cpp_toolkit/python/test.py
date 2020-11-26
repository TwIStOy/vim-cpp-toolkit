import os
import os.path

import clang
from clang import cindex

import sys
from cpp_toolkit.cpp_project import project_root

print(project_root(
  '/home/s3101/agora/ddd/media_build/media_server_ddd/ddd', ['.include_hints']))

