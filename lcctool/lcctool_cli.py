import stdcli.cli_main

main = stdcli.cli_main.main

import lctool
__VERSION__=lctool.__VERSION__

stdcli.cli_main.__VERSION__ = __VERSION__
stdcli.cli_main.moduleName = "lctool"
