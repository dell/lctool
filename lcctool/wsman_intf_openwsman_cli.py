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
import pywsman

from stdcli.trace_decorator import traceLog, getLog
from stdcli.pycompat import call_output
import lcctool
import schemas
etree = schemas.etree
import wscim

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

basic_wsman_cmd = ["wsman", "-P", "443", "-V", "-v", "-c", "dummy.cert", "-j", "utf-8", "-y", "basic", "-o", "-m", "512"]

# more wsman commands we need to implement
"wsman invoke -a GetRSStatus http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_LCService,SystemName=DCIM:ComputerSystem,Name=DCIM:LCService"
"wsman invoke -a CreateTargetedConfigJob http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_%(jobservice)s?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_%(jobservice)s,SystemName=DCIM:ComputerSystem,Name=DCIM:%(jobservice)s -J %(f_name)s"
"wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=%(job_id)s"
"wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=%(job_id)s"

class OpenWSManCLI(lcctool.BaseWsman):
    def __init__(self, host, *args, **kargs):
        super(OpenWSManCLI, self).__init__(host, *args, **kargs)

        self.client = pywsman.Client( "https://%(user)s:%(pass)@%(host):%(port)/wsman" %
            {'user': self.get_user(), 'pass': self.get_password(), 'host': self.get_host(), 'port': 443})

        assert client is not None
        # required transport characteristics to talk to drac
        self.client.transport().set_auth_method(BASIC_AUTH_STR) # Windows winrm needs this
        # we can implement verification later (need to save certs and pass them in
        self.client.transport().set_verify_peer(False)
        self.client.transport().set_verify_host(False)

        self.options = pywsman.ClientOptions()
        assert options is not None
        self.options.set_flags(FLAG_ENUMERATION_OPTIMIZATION)

        # for debugging
        self.options.set_dump_request()
        doc = self.client.identify( options )
        print "Document [%s]" % doc


    # generates <Items> element from each schema call, sequentially
    @traceLog()
    def enumerate(self, schema, filter=None):
        filt = pywsman.Filter()
        doc = client.enumerate(options, filt, schema)
        root=doc.root()
        context = doc.context()

        while 1:
            xml_out = etree.fromstring(doc.body().string())
            for item_list in  xml_out.iter("{%(wsman)s}Items" % schemas.std_xml_namespaces):
                for item in list(item_list):
                    yield wscim.cim_instance_from_wsxml(elem)

            if not context:
                break

            doc = client.pull(options, filt, schema, context)
            context = doc.context()
            if client.response_code() not in [200, 400, 500]:
                break


