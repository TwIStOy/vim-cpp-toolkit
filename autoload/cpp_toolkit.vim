let g:cpp_toolkit_py = 'py3 '

" prepare python environment, add current path into sys.path
exec g:cpp_toolkit_py "import vim, sys, os, re, os.path"
exec g:cpp_toolkit_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:cpp_toolkit_py "sys.path.insert(0, os.path.join(cwd, 'cpp_toolkit', 'python'))"

function! cpp_toolkit#corresponding_file()
  " let g:cpp_toolkit_header_folders = [['include', 'khala']]

  exec g:cpp_toolkit_py "import cpp_toolkit.switch as switch"
  exec g:cpp_toolkit_py "print(switch.corresponding_file())"
endfunction

