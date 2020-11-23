let g:cpp_toolkit_py = get(g:, 'cpp_toolkit_py', 'py3')
let g:cpp_toolkit_pyeval = get(g: , 'cpp_toolkit_pyeval','py3eval')

" prepare python environment, add current path into sys.path
exec g:cpp_toolkit_py "import vim, sys, os, re, os.path"
exec g:cpp_toolkit_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:cpp_toolkit_py "sys.path.insert(0, os.path.join(cwd, 'cpp_toolkit', 'python'))"
exec g:cpp_toolkit_py "import cpp_toolkit.signature.clang as cl"

function! cpp_toolkit#corresponding_file()
  exec g:cpp_toolkit_py "import cpp_toolkit.switch as switch"
  return call(g:cpp_toolkit_pyeval, ["switch.corresponding_file()"])
endfunction

function! cpp_toolkit#mark_current_function_decl()
  if &modified
    echo 'Please save first!'
  else
    exec g:cpp_toolkit_py "cl.mark_current_function()"
  endif
endfunction

function! cpp_toolkit#generate_function_define_here()
  if &modified
    echo 'Please save first!'
  else
    exec g:cpp_toolkit_py "cl.generate_here()"
  endif
endfunction

