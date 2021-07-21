let g:cpp_toolkit_py = get(g:, 'cpp_toolkit_py', 'py3')
let g:cpp_toolkit_pyeval = get(g: , 'cpp_toolkit_pyeval','py3eval')

" prepare python environment, add current path into sys.path
exec g:cpp_toolkit_py "import vim, sys, os, re, os.path"
exec g:cpp_toolkit_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:cpp_toolkit_py "sys.path.insert(0, os.path.join(cwd, 'cpp_toolkit', 'python'))"

exec g:cpp_toolkit_py "import cpp_toolkit.signature as signature"

function! cpp_toolkit#init() abort
  command! -bar -nargs=0 LeaderfHeaderFiles call cpp_toolkit#leaderf#start_expl()

  call g:LfRegisterSelf("HeaderFiles", "navigate the cpp headers")

  let s:extension = {
              \   "name": "headerFiles",
              \   "help": "navigate the cpp headers",
              \   "registerFunc": "cpp_toolkit#leaderf#register",
              \   'manager_id': "cpp_toolkit#leaderf#manager_id",
              \   "arguments": [
              \   ]
              \ }

  call g:LfRegisterPythonExtension(s:extension.name, s:extension)

  command! -bar -nargs=0 CppToolkitCurrentRoot echo cpp_toolkit#project_root()
endfunction

function! cpp_toolkit#setup_environment() abort
  if get(s:, 'cpp_toolkit_py_setup', 0)
    return
  endif
  let s:cpp_toolkit_py_setup = 1
  exec g:cpp_toolkit_py "import cpp_toolkit.switch as switch"
  exec g:cpp_toolkit_py "import cpp_toolkit.signature as signature"
  exec g:cpp_toolkit_py "import cpp_toolkit.logger as logger"
  exec g:cpp_toolkit_py "logger.setup('DEBUG', '/tmp/cpp-toolkit.log')"
endfunction

function! cpp_toolkit#project_root() abort
  exec g:cpp_toolkit_py "import cpp_toolkit.utils"

  return call(g:cpp_toolkit_pyeval, ["cpp_toolkit.utils.current_project_root()"])
endfunction

function! cpp_toolkit#corresponding_file() abort
  call cpp_toolkit#setup_environment()

  return call(g:cpp_toolkit_pyeval, ["switch.corresponding_file()"])
endfunction

function! cpp_toolkit#fast_include_header_file() abort
  call cpp_toolkit#setup_environment()

  return call(g:cpp_toolkit_pyeval, ["switch.fast_include_header_file()"])
endfunction

function! cpp_toolkit#mark_current_function_decl() abort
  call cpp_toolkit#setup_environment()

  exec g:cpp_toolkit_py "signature.mark_current()"
endfunction

function! cpp_toolkit#generate_function_define_here() abort
  call cpp_toolkit#setup_environment()

  exec g:cpp_toolkit_py "signature.generate_here()"
endfunction

" 'let curspr=&spr | set nospr | vsplit | wincmd l | if curspr | set spr | endif'
function! cpp_toolkit#switch_file_here(precmd) abort
  let l:cfile = cpp_toolkit#corresponding_file()

  if len(l:cfile) <= 0
    return
  endif

  let newpath = l:cfile[0]

  if &switchbuf =~ '^use'
    let i = 1
    let bufnum = winbufnr(i)
    while bufnum != -1
      let filename = fnamemodify(bufname(bufnum), ':p')
      if filename == newpath
        execute ':sbuffer ' . filename
      endif
      let i += 1
      let bufnum = winbufnr(i)
    endwhile
  endif

  if newpath != ''
    if strlen(a:precmd) != 0
      execute a:precmd
    endif

    let fname = fnameescape(newpath)
    if (strlen(bufname(fname))) > 0
        execute 'buffer ' . fname
    else
        execute 'edit ' . fname
    endif
  endif
endfunction

