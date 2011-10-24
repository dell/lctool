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
moduleDebugLog = getLog(prefix="debug.")

basic_wsman_cmd = ["wsman", "-P", "443", "-V", "-v", "-c", "dummy.cert", "-j", "utf-8", "-y", "basic", "-o", "-m", "512"]

# more wsman commands we need to implement
"wsman invoke -a GetRSStatus http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_LCService,SystemName=DCIM:ComputerSystem,Name=DCIM:LCService"
"wsman invoke -a CreateTargetedConfigJob http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_%(jobservice)s?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_%(jobservice)s,SystemName=DCIM:ComputerSystem,Name=DCIM:%(jobservice)s -J %(f_name)s"
"wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=%(job_id)s"
"wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=%(job_id)s"

class OpenWSManCLI(lcctool.BaseWsman):
    def __init__(self, host, *args, **kargs):
        super(OpenWSManCLI, self).__init__(host, *args, **kargs)

        self.client = pywsman.Client( "https://%(user)s:%(pass)s@%(host)s:%(port)s/wsman" %
            {'user': self.get_user(), 'pass': self.get_password(), 'host': self.get_host(), 'port': 443})

        self.debug = kargs.get("debug", False)

        assert self.client is not None
        # required transport characteristics to talk to drac
        self.client.transport().set_auth_method(pywsman.BASIC_AUTH_STR) # Windows winrm needs this
        # we can implement verification later (need to save certs and pass them in
        self.client.transport().set_verify_peer(False)
        self.client.transport().set_verify_host(False)

        self.options = pywsman.ClientOptions()
        assert self.options is not None

        # for debugging
        if self.debug:
            self.options.set_dump_request()

        self._identify_result = self.client.identify( self.options )
        if self.debug:
            moduleDebugLog.info("Identify: \n%s" % self._identify_result)


    # generates <Items> element from each schema call, sequentially
    @traceLog()
    def enumerate(self, schema, filter=None):
        filt = pywsman.Filter()
        #self.options.set_flags(pywsman.FLAG_ENUMERATION_OPTIMIZATION)
        doc = self.client.enumerate(self.options, filt, schema)
        root=doc.root()
        context = doc.context()
        moduleDebugLog.info("enumerate(schema='%s')" % schema)
        moduleDebugLog.info("enumerate result xml: \n%s" % doc.body().string())

        while 1:
            xml_out = etree.fromstring(doc.body().string())
            #print "got some xml: %s" % etree.tostring(xml_out)
            for item_list in  xml_out.iter("{%(wsen)s}Items" % schemas.std_xml_namespaces):
                #print "Got item_list: %s" % item_list
                for item in list(item_list):
                    #print "Got item: %s" % item
                    yield wscim.cim_instance_from_wsxml(self, item)

            if not context:
                break

            doc = self.client.pull(self.options, filt, schema, context)
            moduleDebugLog.info("enumerate result xml: \n%s" % doc.body().string())
            context = doc.context()
            if self.client.response_code() not in [200, 400, 500]:
                break

    @traceLog()
    def invoke(self, schema, method, xml_input_etree):
        doc = self.client.invoke(self.options, schema, method, etree.tostring(xml_input_etree))
        xml_out = etree.fromstring(doc.body().string())
        if self.client.response_code() not in [200, 400, 500]:
            raise Exception("invalid response code from server: %s" % self.client.response_code())
        return xml_out
