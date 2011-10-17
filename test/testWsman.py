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
"""
"""

from __future__ import generators

import os
import sys
import unittest
import cStringIO
import ConfigParser

class TestCase(unittest.TestCase):
    def setUp(self):
        import lcctool
        lcctool.unit_test_mode = 1
        lcctool.test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def tearDown(self):
        if globals().get('lcctool'): del(lcctool)
        for k in sys.modules.keys():
            if k.startswith("lcctool"):
                del(sys.modules[k])

    def testFactory(self):
        import lcctool.cim
        from lcctool.schemas import etree

        test_xml_str = """\
        <n1:DCIM_BIOSinteger 
                xmlns:n1="http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSinteger"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                >
          <n1:AttributeName>AcPwrRcvryUserDelay</n1:AttributeName>
          <n1:CurrentValue>30</n1:CurrentValue>
          <n1:DefaultValue xsi:nil="true"/>
          <n1:FQDD>BIOS.Setup.1-1</n1:FQDD>
          <n1:InstanceID>BIOS.Setup.1-1:AcPwrRcvryUserDelay</n1:InstanceID>
          <n1:IsReadOnly>true</n1:IsReadOnly>
          <n1:LowerBound>30</n1:LowerBound>
          <n1:PendingValue xsi:nil="true"/>
          <n1:UpperBound>240</n1:UpperBound>
        </n1:DCIM_BIOSinteger>"""
        
        xml = etree.fromstring(test_xml_str)
         
        i = lcctool.cim.single_attribute_from_xml_factory(xml)

        #self.assertEquals( i['namespace'], 'http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSinteger' )
        self.assertEquals( i['AttributeName'], 'AcPwrRcvryUserDelay' )
        self.assertEquals( i['CurrentValue'], '30' )
        self.assertEquals( i['DefaultValue'], None )
        self.assertEquals( i['FQDD'], 'BIOS.Setup.1-1' )
        self.assertEquals( i['InstanceID'], 'BIOS.Setup.1-1:AcPwrRcvryUserDelay' )
        self.assertEquals( i['IsReadOnly'], 'true')
        self.assertEquals( i['LowerBound'], 30 )
        self.assertEquals( i['PendingValue'], None )
        self.assertEquals( i['UpperBound'], 240 )
