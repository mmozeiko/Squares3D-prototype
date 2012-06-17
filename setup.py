from distutils.core import setup
import py2exe
import sys

if len(sys.argv) == 1:
  sys.argv.append("py2exe")
  sys.argv.append("-q")

  game = {"description" : "Game",
          "script" : "main.py",
##          "icon_resources" : [(1, "icon.ico")],
          "dest_base" : "squares"} # exe faila nosaukums
  setup(options = {"py2exe": {"compressed": 1,
                   "optimize": 2,
                   "ascii": 1,
                   "bundle_files": 2,
                   "dll_excludes": ["OpenAL32.dll"]}},
        zipfile = "library.zip",
        console = [game],
##        windows = [game],
##        data_files=[(r"C:\Python24\Lib\site-packages\PIL\PngImagePlugin.py")]
        )

##[00:14:01] <bubu>  "bundle_files": 1
##[00:14:05] <bubu> tas ir jaapamaina
##[00:14:09] <bubu> un zipfile = None
##[00:14:19] <bubu> var arii bunde_files : 2 atstaat
##[00:14:23] <bubu> bet zipfile = None
##[00:14:32] <bubu> bundle_files kontrolee to .dll ielikshanu exee
##[00:14:35] <bubu> zipfile - to zipfailu

##[00:46:03] <bubu> options = {"py2exe": { "dll_excludes": ["OpenAL32.dll"]}},
