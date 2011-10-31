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
import re

from stdcli.trace_decorator import traceLog, getLog
import lcctool
import schemas
import wscim
etree = schemas.etree

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

@traceLog()
def _makesafe(*args):
    p = re.compile( '[^a-zA-Z0-9]')
    return p.sub( '_', "_".join(args))

class MockWsman(lcctool.BaseWsman):
    def __init__(self, test_data_dir, *args, **kargs):
        self.test_data_dir = test_data_dir
        super(MockWsman, self).__init__(*args, **kargs)

    @traceLog()
    def _mkpath(self, *args):
        return os.path.join(self.test_data_dir, _makesafe(self.get_host()), _makesafe(*args))

    @traceLog()
    def _open_ro(self, *args):
        return open(self._mkpath(*args), "r")

    @traceLog()
    def enumerate(self, schema):
        xml_file = self._open_ro("enumerate_%s" % schema)
        xml_out = etree.fromstring(xml_file.read())
        xml_file.close()
        for item_list in  xml_out.iter("{%(wsman)s}Items" % schemas.std_xml_namespaces):
            for item in list(item_list):
                yield wscim.cim_instance_from_wsxml(self, item)

    @traceLog()
    def invoke(self, schema, method, xml_input_etree):
#        if xml_input_etree:
#            fd, fn = tempfile.mkstemp(suffix=".xml")
#            os.write(fd, etree.tostring(xml_input_etree))
#            os.close(fd)
        xml_file = self._open_ro("invoke_%s_%s" % (schema, method))
        xml_out = etree.fromstring(xml_file.read())
        xml_file.close()
        for body_elements in xml_out.iter("{%(soap)s}Body" % schemas.std_xml_namespaces):
            return list(body_elements)[0]
