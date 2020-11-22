from clang import cindex


def print_cursor_recursive(cursor: cindex.Cursor, prefix=None):
  prefix = prefix if prefix is not None else ''
  print(f'{prefix}type={cursor.type.spelling}, '
        f'kind={cursor.kind.name}, spelling={cursor.spelling}')
  for c in cursor.get_children():
    print_cursor_recursive(c, prefix + '  ')


def print_cursor_up_recursive(cursor: cindex.Cursor):
  print(f'type={cursor.type.spelling}, '
        f'kind={cursor.kind.name}, spelling={cursor.spelling}')
  if cursor.kind != cindex.CursorKind.TRANSLATION_UNIT:
    print_cursor_up_recursive(cursor.semantic_parent)
