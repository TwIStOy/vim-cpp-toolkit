from clang import cindex


def print_cursor_recursive(cursor: cindex.Cursor, prefix=None):
  prefix = prefix if prefix is not None else ''
  print(f'{prefix}type={cursor.type.spelling}, '
        f'kind={cursor.kind.name}, spelling={cursor.spelling}')
  for c in cursor.get_children():
    print_cursor_recursive(c, prefix + '  ')


def print_cursor_up_recursive(cursor: cindex.Cursor, prefix=''):
  print(f'{prefix}type={cursor.type.spelling}, '
        f'kind={cursor.kind.name}, spelling={cursor.spelling}')
  if cursor.kind != cindex.CursorKind.TRANSLATION_UNIT:
    print_cursor_up_recursive(cursor.semantic_parent, prefix + '  ')


def print_cindex_type(tp: cindex.Type, prefix=None):
  prefix = prefix if prefix is not None else ''
  next_prefix = prefix + '  '
  print(f'{prefix}=== DUMP TYPE ST ===')
  print(f'{prefix}Spelling: {tp.spelling}')
  print(f'{prefix}Kind: {tp.kind}')
  print(f'{prefix}Canonical: {tp.get_canonical().spelling}')
  print(f'{prefix}Typedef: {tp.get_typedef_name()}')
  if tp.kind == cindex.TypeKind.ELABORATED:
    print(f'{prefix}=== NAMED TYPE ===')
    print_cindex_type(tp.get_named_type(), next_prefix)
  if (tp.kind == cindex.TypeKind.TYPEDEF or
      tp.kind == cindex.TypeKind.UNEXPOSED or
      tp.kind == cindex.TypeKind.RECORD):
    print(f'{prefix}=== DEF UP ===')
    print_cursor_up_recursive(tp.get_declaration(), next_prefix)
  qualifiers = []
  if tp.is_const_qualified():
    qualifiers.append('const')
  if tp.is_volatile_qualified():
    qualifiers.append('volatile')
  if tp.is_restrict_qualified():
    qualifiers.append('restrict')
  if qualifiers:
    print(f'{prefix}Qualifiers: [{",".join(qualifiers)}]')
  if tp.get_num_template_arguments() > 0:
    print(f'{prefix}=== template arguments ===')
    for i in range(tp.get_num_template_arguments()):
      sub = tp.get_template_argument_type(i)
      print_cindex_type(sub, next_prefix)

  _kinds = [
    cindex.TypeKind.POINTER,
    cindex.TypeKind.LVALUEREFERENCE,
    cindex.TypeKind.RVALUEREFERENCE,
  ]
  if tp.kind in _kinds:
    print(f'{prefix}=== CUSTOM ===')
  if tp.kind == cindex.TypeKind.POINTER:
    print(f'{prefix}Pointee:')
    print_cindex_type(tp.get_pointee(), next_prefix)
  if tp.kind == cindex.TypeKind.LVALUEREFERENCE:
    print(f'{prefix}LVALUEREFERENCE:')
    print_cindex_type(tp.get_pointee(), next_prefix)
  if tp.kind == cindex.TypeKind.RVALUEREFERENCE:
    print(f'{prefix}RVALUEREFERENCE:')
    print_cindex_type(tp.get_pointee(), next_prefix)
  # if tp.kind in _kinds:
  #   print(f'{prefix}^^^ CUSTOM ^^^')

  # print(f'{prefix}^^^ DUMP TYPE ED ^^^')
