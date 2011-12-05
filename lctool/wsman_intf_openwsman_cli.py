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
import lctool
import schemas
etree = schemas.etree
import wscim

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")
moduleDebugLog = getLog(prefix="debug.")

class OpenWSManCLI(lctool.BaseWsman):
    def __init__(self, host, *args, **kargs):
        super(OpenWSManCLI, self).__init__(host, *args, **kargs)
        self.avail_debug_flags.extend([
                'verbose_requests',
                'print_input_xml',
                'print_request_xml',
                'print_identify',
                ])

        if kargs.get("use_wsman_cli", True):
            self.init_wsmancli(host, *args, **kargs)
            self.invoke = self._invoke_wsmancli
            self.enumerate = self._enumerate_wsmancli
            self.get_instance_id = self._get_instance_id_wsmancli
        else:
            self.init_pywsman(host, *args, **kargs)
            self.invoke = self._invoke_pywsman
            self.enumerate = self._enumerate_pywsman

    def init_wsmancli(self, host, *args, **kargs):
        self.wsman_cmd = ["wsman", "-P", "443", "-V", "-v", "-c", "dummy.cert", "-j", "utf-8", "-y", "basic", "-o", "-m", "512"]
        self.host = host
        opts = { "-h": self.get_host, "-u": self.get_user, "-p": self.get_password }
        for k,v in opts.items():
            if v() is not None:
                self.wsman_cmd.extend([k,v()])
        if self.debug_flag('verbose_requests'):
            self.wsman_cmd.append("--debug=6")
            moduleDebugLog.info("wsman basic cli: %s" % " ".join(self.wsman_cmd))

    @traceLog()
    def _retry_wsmancli(self, cmd, retries=3):
        # sometimes wsman cli will just fail for no discernable reason. Retry a reasonable number of times
        xml_out = None
        retries = retries
        while 1:
            try:
                s = call_output( cmd, raise_exc=False )
                return etree.fromstring(s)
            except Exception:
                retries = retries - 1
                if retries == 0:
                    raise

    @traceLog()
    def _enumerate_wsmancli(self, schema, filter=None):
        moduleDebugLog.info("retrieving info for schema: %s" % schema)
        xml_out = self._retry_wsmancli(self.wsman_cmd + ["enumerate", schema])
        for item_list in  xml_out.iter("{%(wsman)s}Items" % schemas.std_xml_namespaces):
            for item in list(item_list):
                yield wscim.cim_instance_from_wsxml(self, item)

    @traceLog()
    def _invoke_wsmancli(self, schema, method, xml_input_etree):
        wsman_cmd = self.wsman_cmd[:]
        if xml_input_etree:
            fd, fn = tempfile.mkstemp(suffix=".xml")
            os.write(fd, etree.tostring(xml_input_etree))
            os.close(fd)
            wsman_cmd.extend(["-J", fn])
            if self.debug_flag('print_input_xml'):
                moduleDebugLog.info("invoke input xml: \n%s" %  etree.tostring(xml_input_etree))

        try:
            wsman_cmd.extend(["invoke", "-a", method, schema])
            xml_out = self._retry_wsmancli(wsman_cmd)
            for body_elements in xml_out.iter("{%(soap)s}Body" % schemas.std_xml_namespaces):
                return list(body_elements)[0]
        finally:
            if xml_input_etree:
                os.unlink(fn)

    @traceLog()
    def _get_instance_id_wsmancli(self, schema, instance_id):
        wsman_cmd = self.wsman_cmd[:]

        wsman_cmd.extend(["get", "%s?InstanceID=%s" % (schema, instance_id)])
        xml_out = self._retry_wsmancli(wsman_cmd)
        for body_elements in xml_out.iter("{%(soap)s}Body" % schemas.std_xml_namespaces):
            for item in list(body_elements):
                yield wscim.cim_instance_from_wsxml(self, item)


    def init_pywsman(self, host, *args, **kargs):
        self.client = pywsman.Client( "https://%(user)s:%(pass)s@%(host)s:%(port)s/wsman" %
            {'user': self.get_user(), 'pass': self.get_password(), 'host': self.get_host(), 'port': 443})

        assert self.client is not None
        # required transport characteristics to talk to drac
        self.client.transport().set_auth_method(pywsman.BASIC_AUTH_STR) # Windows winrm needs this
        # we can implement verification later (need to save certs and pass them in
        self.client.transport().set_verify_peer(False)
        self.client.transport().set_verify_host(False)

        self.options = pywsman.ClientOptions()
        assert self.options is not None

        # for debugging
        if self.debug_flag('print_request_xml'):
            self.options.set_dump_request()

        self._identify_result = self.client.identify( self.options )
        if self.debug_flag('print_identify'):
            moduleDebugLog.info("Identify: \n%s" % self._identify_result)

    @traceLog()
    def _enumerate_pywsman(self, schema, filter=None):
        # THIS API SUCKS! Dont use it. There is no way that I can tell to do
        # the OPTIMIZATION that wsman cli does to pull multiple records at
        # once. That makes this api painfully, painfully slow.
        filt = pywsman.Filter()
        #self.options.set_flags(pywsman.FLAG_ENUMERATION_OPTIMIZATION)
        doc = self.client.enumerate(self.options, filt, schema)
        root=doc.root()
        context = doc.context()

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
    def _invoke_pywsman(self, schema, method, xml_input_etree):
        ## THIS DOES NOT YET WORK!! (we can't create an xmldoc to pass into
        ## this method due to inadequacies in the python xml API
        #doc = self.client.invoke(self.options, schema, method, etree.tostring(xml_input_etree))
        doc = self.client.invoke(self.options, schema, method)
        xml_out = etree.fromstring(doc.body().string())
        if self.client.response_code() not in [200, 400, 500]:
            raise Exception("invalid response code from server: %s" % self.client.response_code())
        for body_elements in xml_out.iter("{%(soap)s}Body" % schemas.std_xml_namespaces):
            return list(body_elements)[0]


