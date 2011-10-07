#!/usr/bin/python
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
#

import os
import copy
import tempfile

from stdcli.trace_decorator import traceLog, getLog
from stdcli.pycompat import call_output
import wsman_factory
import schemas
etree = schemas.etree

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

basic_wsman_cmd = ["wsman", "-P", "443", "-V", "-v", "-c", "dummy.cert", "-j", "utf-8", "-y", "basic", "-o", "-m", "512"]

# more wsman commands we need to implement
"wsman invoke -a GetRSStatus http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_LCService,SystemName=DCIM:ComputerSystem,Name=DCIM:LCService"
"wsman invoke -a CreateTargetedConfigJob http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_%(jobservice)s?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_%(jobservice)s,SystemName=DCIM:ComputerSystem,Name=DCIM:%(jobservice)s -J %(f_name)s"
"wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=%(job_id)s"
"wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=%(job_id)s"


class OpenWSManCLI(wsman_factory.BaseWsman):
    def __init__(self, host, *args, **kargs):
        super(OpenWSManCLI, self).__init__(host, *args, **kargs)
        self.host = host
        opts = { "-h": self.get_host, "-u": self.get_user, "-p": self.get_password }
        self.wsman_cmd = copy.copy(basic_wsman_cmd)
        for k,v in opts.items():
            if v() is not None:
                self.wsman_cmd.extend([k,v()])

    @traceLog()
    def enumerate(self, schema_list, filter=None):
        for schema in schema_list:
            moduleLog.info("retrieving info for schema: %s" % schema)
            yield call_output( self.wsman_cmd + ["enumerate", schema], raise_exc=False )

    @traceLog()
    def invoke(self, schema, cmd, input_xml, *args, **kargs):
        wsman_cmd = copy.copy(self.wsman_cmd)
        if input_xml:
            fd, fn = tempfile.mkstemp(suffix=".xml")
            os.write(fd, etree.tostring(input_xml))
            os.close(fd)
            wsman_cmd.extend(["-J", fn])

        try:
            wsman_cmd.extend(["invoke", "-a", cmd, schema])
            return call_output(wsman_cmd, raise_exc=False)
        finally:
            if input_xml:
                os.unlink(fn)

    #@traceLog()
    #def get(self, schema_list, *args, **kargs):
    #    pass

