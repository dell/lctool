import pkg_resources
import ConfigParser
import fnmatch

import lcctool
from stdcli.trace_decorator import traceLog, getLog
from stdcli.plugin import Plugin

moduleVerboseLog = getLog(prefix="verbose.")
moduleVerboseLog.debug("initializing plugin module: %s" % __name__)

_ = lcctool._

class PowerPlugin(Plugin):
    @traceLog()
    def __init__(self, ctx):
        moduleVerboseLog.debug("initializing plugin: %s" % self.__class__.__name__)
        # subparser for dumping config (note this is what plugins should do)
        power_ctl_p = ctx.subparsers.add_parser("power-ctl", help="Control power for a RAC")
        power_ctl_p.add_argument("--on",     action="store_const", const="on", dest="action", help=_("Turn power on"))
        power_ctl_p.add_argument("--off",    action="store_const", const="off", dest="action", help=_("Turn power off"))
        power_ctl_p.add_argument("--cycle",  action="store_const", const="cycle", dest="action", help=_("Cycle power: Turn power off, then on."))
        power_ctl_p.set_defaults(func=self.powerCtl)

    @traceLog()
    def powerCtl(self, ctx):
        action = ctx.args.action
        for host in ctx.raccfg.iterSpecfiedRacs():
            if action is None:
                print _("NO ACTION SPECIFIED!")
            if action == "on":
                print _("Power ON: %s") % host["host"]
            if action == "off":
                print _("Power OFF: %s") % host["host"]
            if action == "cycle":
                print
                print _("Power OFF: %s") % host["host"]
                print _("Power ON: %s") % host["host"]
            


