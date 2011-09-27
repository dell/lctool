# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0
# Copyright (c) 2011, Dell Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Dell, Inc. nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Dell, Inc. BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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



