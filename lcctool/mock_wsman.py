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
import wsman_factory

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")


class MockWsman(wsman_factory.BaseWsman):
    def __init__(self, test_data_dir, *args, **kargs):
        self.test_data_dir = test_data_dir
        super(MockWsman, self).__init__(*args, **kargs)

    def makesafe(self, pth):
        p = re.compile( '[^a-zA-Z0-9]')
        return p.sub( '_', pth)

    @traceLog()
    def enumerate(self, schema_list):
        for schema in schema_list:
            xml_file = open(os.path.join(self.test_data_dir, self.makesafe(self.get_host()), self.makesafe(schema)), "r")
            xml_str = xml_file.read()
            xml_file.close()
            yield xml_str

    @traceLog()
    def invoke(self, schema, cmd, input_xml, *args, **kargs):
        # probably ought to have some sort of callback registered so that unit test framework can inspect the input_xml
        xml_file = open(os.path.join(self.test_data_dir, self.makesafe(self.get_host()), cmd + "_" + self.makesafe(schema)), "r")
        xml_str = xml_file.read()
        xml_file.close()
        return xml_str

    @traceLog()
    def get(self, *args, **kargs):
        pass
