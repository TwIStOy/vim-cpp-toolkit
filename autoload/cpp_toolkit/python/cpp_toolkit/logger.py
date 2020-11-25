import logging
import sys

log_format = '%(asctime)s %(levelname)-8s (%(name)s) %(message)s'

root = logging.getLogger('cpp-toolkit')
root.propagate = False
init = False


def getLogger(name):
    """Get a logger that is a child of the 'root' logger.
    """
    return root.getChild(name)


def setup(level, output_file=None):
    """Setup logging
    """
    global init
    if init:
        return
    init = True

    if output_file:
        formatter = logging.Formatter(log_format)
        handler = logging.FileHandler(filename=output_file)
        handler.setFormatter(formatter)
        root.addHandler(handler)

        level = str(level).upper()
        if level not in ('DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR',
                         'CRITICAL', 'FATAL'):
            level = 'DEBUG'
        root.setLevel(getattr(logging, level))

        try:
            import pkg_resources
            neovim_version = pkg_resources.get_distribution('pynvim').version
        except ImportError:
            neovim_version = 'unknown'

        log = getLogger('logging')
        log.info('--- Cpp-Toolkit Log Start ---')
        log.info(f'pynvim: {neovim_version}')



