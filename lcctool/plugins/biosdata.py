# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0
import lcctool
from stdcli.trace_decorator import traceLog, getLog
from stdcli.plugin import Plugin

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")
moduleVerboseLog.debug("loading plugin module: %s" % __name__)

_ = lcctool._

class BiosData(Plugin):
    @traceLog()
    def __init__(self, ctx):
        moduleVerboseLog.debug("initializing plugin: %s" % self.__class__.__name__)
        biosdata_ctl_p = ctx.subparsers.add_parser("get-bios", help="")
        biosdata_ctl_p.set_defaults(func=self.biosdataCtl)

    @traceLog()
    def biosdataCtl(self, ctx):
        print "HI THERE!"

