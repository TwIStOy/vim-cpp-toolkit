command! -bar -nargs=0 LeaderfHeaderFiles call cpp_toolkit#leaderf#start_expl()

call g:LfRegisterSelf("HeaderFiles", "navigate the cpp headers")

let s:extension = {
            \   "name": "headerFiles",
            \   "help": "navigate the cpp headers",
            \   "registerFunc": "cpp_toolkit#leaderf#register",
            \   "arguments": [
            \   ]
            \ }

call g:LfRegisterPythonExtension(s:extension.name, s:extension)

