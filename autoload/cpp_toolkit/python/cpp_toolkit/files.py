from .utils import *
from .cpp_project import *
from .logger import getLogger
import itertools
import subprocess


_include_hints = '.include_hints'
logger =  getLogger(__name__)


def filter_header_files(pwd: str) -> List[str]:
    root = project_root(pwd, [_include_hints])
    if root is None:
        root = project_root(pwd)

    logger.info(f'Use root {root}')

    # load .include_hints
    directories = []
    if os.path.exists(os.path.join(root, _include_hints)):
        with open(os.path.join(root, _include_hints)) as fp:
            for line in fp.readlines():
                directories.append(os.path.join(root, line.strip()))
    else:
        directories = [root]

    logger.info(f'filter headers in directories: {directories}')

    directories = list(set([os.path.normpath(p) for p in directories]))
    result = []
    for directory in directories:
        ext_args = [['-e', header] for header in header_extensions()]
        ext_args = list(itertools.chain(*ext_args))
        cmd = ['fd', '-LI'] + ext_args + ['--base-directory', directory]
        logger.info(f'filter headers cmd: {cmd}')
        exec_res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            encoding='utf-8'
        )
        result.extend([
            x.strip() for x in exec_res.stdout.split('\n') if x.strip()
        ])
    return list(set(result))


