import os.path
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *
from .files import filter_header_files
from .utils import current_file
from .logger import getLogger 


logger = getLogger(__name__)


class HeaderFilesLeaderfExplorer(Explorer):
    def __init__(self):
        super().__init__()

    def getContent(self, *args, **kwargs):
        folder, name = os.path.split(current_file())
        return filter_header_files(folder)

    def getStlCategory(self):
        return "HeaderFiles"

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def isFilePath(self):
        return False

class HeaderFilesExplManager(Manager):
    def __init__(self):
        super().__init__()
        self._match_ids = []

    def _getExplClass(self):
        return HeaderFilesLeaderfExplorer

    def _defineMaps(self):
        lfCmd("nmapclear <buffer>")
        lfCmd('nnoremap <buffer> <silent> q '
              ':exec g:Lf_py "headerFilesExplManager.quit()"<CR>')
        lfCmd('nnoremap <buffer> <silent> i '
              ':exec g:Lf_py "headerFilesExplManager.input()"<CR>')
        lfCmd('nnoremap <buffer> <silent> <F1> '
              ':exec g:Lf_py "headerFilesExplManager.toggleHelp()"<CR>')
        lfCmd('nnoremap <buffer> <silent> <CR> '
              ':exec g:Lf_py "headerFilesExplManager.accept()"<CR>')

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        if line == "":
            return

        lfCmd("call setline(line('.'), '#include \"%s\"')" % line)
        lfCmd("call cursor(line('.'), col('$'))")

    def _cmdExtension(self, cmd):
        return True

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, 1, 2, return the whole line
        """
        return line

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, 1, 2, return 1
        """
        return 0

    def _createHelp(self):
        help = []
        help.append('" i : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" <CR> : accept')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super()._afterEnter()

    def _beforeExit(self):
        super()._beforeExit()

headerFilesExplManager = HeaderFilesExplManager()

