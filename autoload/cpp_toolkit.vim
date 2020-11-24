let g:cpp_toolkit_py = get(g:, 'cpp_toolkit_py', 'py3')
let g:cpp_toolkit_pyeval = get(g: , 'cpp_toolkit_pyeval','py3eval')

" prepare python environment, add current path into sys.path
exec g:cpp_toolkit_py "import vim, sys, os, re, os.path"
exec g:cpp_toolkit_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:cpp_toolkit_py "sys.path.insert(0, os.path.join(cwd, 'cpp_toolkit', 'python'))"

exec g:cpp_toolkit_py "import cpp_toolkit.signature as signature"

function! s:setup_environment()
  if get(s:, 'cpp_toolkit_py_setup', 0)
    return
  endif
  let s:cpp_toolkit_py_setup = 1
  exec g:cpp_toolkit_py "import cpp_toolkit.switch as switch"
  exec g:cpp_toolkit_py "import cpp_toolkit.signature as signature"
  exec g:cpp_toolkit_py "import cpp_toolkit.logger as logger"
  exec g:cpp_toolkit_py "logger.setup('DEBUG', '/tmp/cpp-toolkit.log')"
endfunction

function! cpp_toolkit#corresponding_file()
  call s:setup_environment()

  return call(g:cpp_toolkit_pyeval, ["switch.corresponding_file()"])
endfunction

function! cpp_toolkit#mark_current_function_decl()
  call s:setup_environment()

  exec g:cpp_toolkit_py "signature.mark_current()"
endfunction

function! cpp_toolkit#generate_function_define_here()
  call s:setup_environment()

  exec g:cpp_toolkit_py "signature.generate_here()"
endfunction

