from distutils.core import setup
import py2exe
import sys
sys.setrecursionlimit(5000)
#setup(options = {"dll_excludes": "MSVCP90.dll"},console=['C:\\Users\\abhi\\Documents\\projects\\test\\nse\\bin\\get_futures.py'])
setup(console=['C:\\Users\\abhi\\Documents\\projects\\test\\nse\\bin\\get_futures.py'])