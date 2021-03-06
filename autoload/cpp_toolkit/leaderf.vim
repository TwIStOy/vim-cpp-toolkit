let s:setup = get(s:, 'setup', 0)

function! s:setup_leaderf()
  if s:setup
    return
  endif

  let s:setup = 1

  call leaderf#LfPy("import cpp_toolkit.leaderf as cpp_toolkit_leaderf")
endfunc


function! cpp_toolkit#leaderf#start_expl()
  call cpp_toolkit#setup_environment()
  call s:setup_leaderf()

  call leaderf#LfPy(
        \ "cpp_toolkit_leaderf.headerFilesExplManager.startExplorer('" .
        \ g:Lf_WindowPosition . "')")
endfunction

function! cpp_toolkit#leaderf#register(name)
  call cpp_toolkit#setup_environment()
  call s:setup_leaderf()

  call s:register_internal(a:name)
endfunction

function! s:register_internal(name)
exec g:cpp_toolkit_py "<< EOF"
from leaderf.anyExpl import anyHub
anyHub.addPythonExtension(vim.eval("a:name"),
                          cpp_toolkit_leaderf.headerFilesExplManager)
EOF
endfunction

function cpp_toolkit#leaderf#manager_id()
  call cpp_toolkit#setup_environment()
  call s:setup_leaderf()

  return py3eval("id(cpp_toolkit_leaderf.headerFilesExplManager)")
endfunction

