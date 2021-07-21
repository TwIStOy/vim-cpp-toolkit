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

