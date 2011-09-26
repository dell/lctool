# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0
import stdcli.cli_main

main = stdcli.cli_main.main

import lcctool
__VERSION__=lcctool.__VERSION__

stdcli.cli_main.__VERSION__ = __VERSION__
stdcli.cli_main.moduleName = "lcctool"
