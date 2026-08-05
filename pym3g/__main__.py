"""
Dumps all data from the specified m3g file when the module is called directly
"""

from sys import argv
import logging
from pym3g.file import M3GFile


try:
    from rich import console
    from rich.logging import RichHandler
    logging.basicConfig(
        level=logging.NOTSET,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    c = console.Console()
    rich_cons = True
except ImportError:
    rich_cons = False
    logging.basicConfig(
        level=logging.NOTSET,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler()],
    )
        
m3g = M3GFile(argv[1], log_level=logging.DEBUG)

for i, obj in enumerate(m3g.objects, 1):
    if rich_cons:
        c.print("({0}) {1}".format(i, obj))
    else:
        print("({0}) {1}".format(i, obj))


