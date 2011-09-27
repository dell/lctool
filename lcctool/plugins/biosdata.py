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

import os
import pkg_resources

import lcctool
from stdcli.trace_decorator import traceLog, getLog
from stdcli.plugin import Plugin

import lcctool.pullattr

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
        print "in biosdatactl!"

        order_xml = pkg_resources.resource_string("lcctool","BIOS0.01.xml")
        bios_wsman_cmds = [ "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSEnumeration",
                "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSString",
                "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSinteger",]

        for host in ctx.raccfg.iterSpecfiedRacs():
            print "  for host: %s" % host["host"]
            outfile = host["host"] + "_bios.ini"
            if os.path.exists(outfile):
                os.remove(outfile)
            lcctool.pullattr.CNARunner(host, outfile, order_xml, "bios", bios_wsman_cmds)



