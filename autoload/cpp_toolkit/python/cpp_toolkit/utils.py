import os
import os.path
from typing import List


def vim_option(option_name, default_value):
    import vim
    if int(vim.eval(f'exists("g:{option_name}")')) == 1:
        return vim.eval(f'get(g:, "{option_name}")')
    return default_value


def ext_associated():
    custom = vim_option('cpp_toolkit_custom_associated', {})
    assert custom is not None
    assert isinstance(custom, dict)
    builtin = {
        '.c': ['.h', '.hh', '.hpp', '.hxx'],
        '.cpp': ['.hpp', '.hxx', '.hh', '.h'],
        '.cc':  ['.hh', 'hxx', '.hpp', '.h'],
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


