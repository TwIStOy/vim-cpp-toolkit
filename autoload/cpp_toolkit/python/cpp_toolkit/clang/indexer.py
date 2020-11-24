import os
import os.path
import sys
from typing import List

import clang
from clang import cindex

_clang_library = None



def _clang_include_path():
    assert _clang_library is not None
    p = os.path.join(_clang_library, 'lib', 'clang')
    res = []
    for f in os.listdir(p):
        if os.path.isdir(os.path.join(p, f)):
            res.append(os.path.join(p, f))
    return [ os.path.join(x, 'include') for x in res ]



class ClangIndexer(object):
    _clang_indexers = {}

    @staticmethod
    def create(root: str) -> 'ClangIndexer':
        res = ClangIndexer._clang_indexers.get(root, None)
        if res is not None:
            return res
        res = ClangIndexer(root)
        ClangIndexer._clang_indexers[root] = res
        return res

    @staticmethod
    def SetLibraryPath(path: str):
        global _clang_library
        _clang_library = path

    def __init__(self, root: str):
        if _clang_library is None:
            raise RuntimeError('Must setup libclang first!');
        if sys.platform == 'dawrin':
            cindex.Config.set_library_file(
                os.path.join(_clang_library, 'lib', 'libclang.dylib')
            )
        else:
            cindex.Config.set_library_file(
                os.path.join(_clang_library, 'lib', 'libclang.so')
            )

        self.cdb: cindex.CompilationDatabase = cindex.CompilationDatabase.fromDirectory(root)
        self.indexer = cindex.Index.create()
        self._tu = {}

    def parse_file(self, filename: str, unsaved_buffer) -> cindex.TranslationUnit:
        try:
            tu = self._tu.get(filename, None)
            if tu is not None:
                tu.reparse(unsaved_buffer)
            else:
                file_args = self._simplify_args_from_database(filename)
                tu = self.indexer.parse(filename, file_args, unsaved_buffer)
                self._tu[filename] = tu
            return self._tu[filename]
        except Exception as e:
            print(f'Cound not parse file: {e}')
            return None


    def _simplify_args_from_database(self, filename: str) -> List[str]:
        res = []
        ret = self.cdb.getCompileCommands(filename)
        _basename = os.path.basename(filename)
        assert isinstance(ret, cindex.CompileCommands)
        if not ret:
            print(f'Cound not find compile flags for {filename} in cdb.')
            return res
        for cmds in ret:
            assert isinstance(cmds, cindex.CompileCommand)
            cmds: cindex.CompileCommand = cmds
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
        # TODO(hawtian): extend include path in macos
        res.extend([f'-isystem{x}' for x in  _clang_include_path()])
        return res

