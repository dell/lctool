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
        pass

    def testFactory(self):
        import lcctool.wscim
        import lcctool.wscim_classes
        from lcctool.schemas import etree

        xml = etree.fromstring(test_xml_str_int)
         
        i = lcctool.wscim.cim_instance_from_wsxml(xml)

        self.assertEquals( i['AttributeName'], 'AcPwrRcvryUserDelay' )
        self.assertEquals( i['CurrentValue'], '30' )
        self.assertEquals( i['DefaultValue'], None )
        self.assertEquals( i['FQDD'], 'BIOS.Setup.1-1' )
        self.assertEquals( i['InstanceID'], 'BIOS.Setup.1-1:AcPwrRcvryUserDelay' )
        self.assertEquals( i['IsReadOnly'], 'true')
        self.assertEquals( i['LowerBound'], 30 )
        self.assertEquals( i['PendingValue'], None )
        self.assertEquals( i['UpperBound'], 240 )



    def testSerialize(self):
        import lcctool.wscim
        import lcctool.wscim_classes
        from lcctool.schemas import etree

        c = ConfigParser.ConfigParser()
        c.optionxform = str
        xml = etree.fromstring("<Items>" + test_xml_str_enums + test_xml_str_int + "</Items>")
        instancelist = []
        for item_list in xml.iter("Items"):
            for i in lcctool.wscim.parse_wsxml_instance_list(item_list):
                i.serialize_ini(c)
                instancelist.append(i)

        c.write(sys.stdout)
        for i in instancelist:
            print i.tocimxml().toprettyxml()

    def testUnserialize(self):
        import pywbem.cimxml_parse
        c = pywbem.cimxml_parse.parse_any(cim_xml_str)
        

cim_xml_str = """\
<INSTANCE CLASSNAME="DCIM_BIOSInteger"><PROPERTY NAME="CurrentValue" TYPE="string"><VALUE>30</VALUE></PROPERTY><PROPERTY NAME="LowerBound" TYPE="uint64"><VALUE>30</VALUE></PROPERTY><PROPERTY NAME="ScalarIncrement" TYPE="uint32"/><PROPERTY NAME="Description" TYPE="string"/><PROPERTY NAME="FQDD" TYPE="string"><VALUE>BIOS.Setup.1-1</VALUE></PROPERTY><PROPERTY NAME="IsReadOnly" TYPE="string"><VALUE>true</VALUE></PROPERTY><PROPERTY NAME="InstanceID" TYPE="string"><VALUE>BIOS.Setup.1-1:AcPwrRcvryUserDelay</VALUE></PROPERTY><PROPERTY NAME="DefaultValue" TYPE="string"/><PROPERTY NAME="AttributeName" TYPE="string"><VALUE>AcPwrRcvryUserDelay</VALUE></PROPERTY><PROPERTY NAME="ElementName" TYPE="string"/><PROPERTY NAME="UpperBound" TYPE="uint64"><VALUE>240</VALUE></PROPERTY><PROPERTY NAME="Caption" TYPE="string"/><PROPERTY NAME="IsOrderedList" TYPE="string"/><PROPERTY NAME="ProgrammaticUnit" TYPE="string"/><PROPERTY NAME="PendingValue" TYPE="string"/></INSTANCE>"""


test_xml_str_enums = """\
        <n1:DCIM_BIOSEnumeration
                xmlns:n1="http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSEnumeration"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                >
          <n1:AttributeName>NumLock</n1:AttributeName>
          <n1:CurrentValue>On</n1:CurrentValue>
          <n1:DefaultValue xsi:nil="true"/>
          <n1:FQDD>BIOS.Setup.1-1</n1:FQDD>
          <n1:InstanceID>BIOS.Setup.1-1:NumLock</n1:InstanceID>
          <n1:IsReadOnly>false</n1:IsReadOnly>
          <n1:PendingValue xsi:nil="true"/>
          <n1:PossibleValues>On</n1:PossibleValues>
          <n1:PossibleValues>Off</n1:PossibleValues>
        </n1:DCIM_BIOSEnumeration>
        <n1:DCIM_BIOSEnumeration
                xmlns:n1="http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSEnumeration"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                >
          <n1:AttributeName>ReportKbdErr</n1:AttributeName>
          <n1:CurrentValue>NoReport</n1:CurrentValue>
          <n1:DefaultValue xsi:nil="true"/>
          <n1:FQDD>BIOS.Setup.1-1</n1:FQDD>
          <n1:InstanceID>BIOS.Setup.1-1:ReportKbdErr</n1:InstanceID>
          <n1:IsReadOnly>false</n1:IsReadOnly>
          <n1:PendingValue xsi:nil="true"/>
          <n1:PossibleValues>Report</n1:PossibleValues>
          <n1:PossibleValues>NoReport</n1:PossibleValues>
        </n1:DCIM_BIOSEnumeration>
"""
test_xml_str_int = """\
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
        </n1:DCIM_BIOSinteger>
"""
