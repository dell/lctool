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

"""
lcctool: sample desc here
"""

import pkg_resources
dist = pkg_resources.get_distribution(__name__)
__VERSION__=dist.version

from stdcli.trace_decorator import traceLog, getLog
import stdcli.cli_main
stdcli.cli_main.__VERSION__ = __VERSION__
stdcli.cli_main.moduleName = __name__
main = stdcli.cli_main.main

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

try:
    import gettext
    import sys
    t = gettext.translation(__name__)
    _ = t.ugettext

except:
    def _(str):
        """pass given string as-is"""
        return str

class NotImplementedException(Exception): pass

unit_test_mode = False
test_data_dir = ""

@traceLog()
def wsman_factory(*args, **kargs):
    if unit_test_mode:
        import wsman_intf_mock
        return wsman_intf_mock.MockWsman(test_data_dir, *args, **kargs)

    if sys.platform.startswith("linux"):
        import wsman_intf_openwsman_cli
        return wsman_intf_openwsman_cli.OpenWSManCLI(*args, **kargs)

    if sys.platform.startswith("win"):
        import wsman_intf_windows
        return wsman_intf_windows.WsmanWindows(*args, **kargs)

# Notes:
#  all input xml and all output xml from these functions is defined as etree Element objects or equivalent. NO XML STRINGS!
class BaseWsman(object):
    def __init__(self, host):
        self.host = host

    def get_host(self):
        return self.host.get("host", None)

    def get_user(self):
        return self.host.get("user", None)

    def get_password(self):
        return self.host.get("password", None)

# why are these all here but commented out? Good question. These are all methods in the base openwsman Client class that we should implement in some fashion.
#    @traceLog()
#    def get(self, *args, **kargs):
#        raise NotImplementedException
#
#    @traceLog()
#    def put(self, *args, **kargs):
#        raise NotImplementedException
#
#    @traceLog()
#    def create(self, *args, **kargs):
#        raise NotImplementedException
#
#    @traceLog()
#    def delete(self, *args, **kargs):
#        raise NotImplementedException
#
#    @traceLog()
#    def fragment_get(self, *args, **kargs):
#        raise NotImplementedException
#
#    @traceLog()
#    def fragment_put(self, *args, **kargs):
#        raise NotImplementedException
#
#    @traceLog()
#    def fragment_create(self, *args, **kargs):
#        raise NotImplementedException
#
#    @traceLog()
#    def fragment_delete(self, *args, **kargs):
#        raise NotImplementedException
#
#    @traceLog()
#    def enumerate(self, schema, filter=None):
#        raise NotImplementedException
#
#    @traceLog()
#    def pull(self, schema, filter=None):
#        raise NotImplementedException
#
#    @traceLog()
#    def release(self, schema, filter=None):
#        raise NotImplementedException
#
#    @traceLog()
#    def invoke_method(self, methodname, objname, *args, **kargs):
#        raise NotImplementedException


