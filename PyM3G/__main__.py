"""
Dumps all data from the specified m3g file when the module is called directly
"""

from sys import argv
from rich import console
from PyM3G.reader import M3GReader

c = console.Console()

m3g = M3GReader(argv[1], "DEBUG")
idx = 0
for obj in m3g.objects:
    c.print("({0}) {1}".format(idx+1, obj))
    idx = idx + 1
