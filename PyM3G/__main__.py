"""
Dumps all data from the specified m3g file when the module is called directly
"""

from sys import argv
from rich import console
from PyM3G.reader import M3GReader

c = console.Console()

m3g = M3GReader(r"C:\Users\Ismail\Desktop\GALAXY_ON_FIRE\GOF2 JAVA\gof2m3g\3d_planet.m3g", "WARNING")
idx = 0
for obj in m3g.objects:
    c.print(f"({idx}) {obj}")
    idx = idx + 1
