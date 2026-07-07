"""
Dumps all data from the specified m3g file when the module is called directly
"""

from sys import argv
import logging
from rich import console
from rich.logging import RichHandler
from PyM3G.file import M3GFile

logging.basicConfig(
    level=logging.NOTSET,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
m3g = M3GFile(argv[1], log_level=logging.DEBUG)
c = console.Console()

for i, obj in enumerate(m3g.objects, 1):
    c.print("({0}) {1}".format(i, obj))

