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
        import lcctool, lcctool.wsman
        lcctool.wsman.unit_test_mode = 1
        lcctool.wsman.test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def tearDown(self):
        if globals().get('lcctool'): del(lcctool)
        for k in sys.modules.keys():
            if k.startswith("lcctool"):
                del(sys.modules[k])

    def testNic(self):
        import lcctool, lcctool.wsman
        host = {'host': 'testhost'}
        ini = ConfigParser.ConfigParser()
        ini.optionxform = str # need to be case sensitive
        lcctool.wsman.stuff_xml_into_ini(host, ini, "nic")

        good_ini = ConfigParser.ConfigParser()
        good_ini.optionxform = str # need to be case sensitive
        fh = cStringIO.StringIO(nic_ini_testdata)
        good_ini.readfp(fh)
        fh.close()
        for sec in good_ini.sections():
            for opt in good_ini.options(sec):
                print "check [%s] %s = %s" % (sec, opt, good_ini.get(sec, opt))
                self.assertEquals(good_ini.get(sec, opt), ini.get(sec, opt))


## test data
nic_ini_testdata = """
[NIC.Embedded.4-1]
ChipMdl = BCM5709 C0
MacAddr = 00:24:E8:67:99:1B
VirtMacAddr = 00:24:E8:67:99:1B
IscsiMacAddr = 00:24:E8:67:99:1C
VirtIscsiMacAddr = 00:24:E8:67:99:1C
DhcpVendId = BRCM ISAN
IscsiInitiatorIpAddr = ::
IscsiInitiatorSubnetPrefix = 0
IscsiInitiatorGateway = ::
IscsiInitiatorPrimDns = ::
IscsiInitiatorSecDns = ::
IscsiInitiatorName = iqn.1995-05.com.broadcom.iscsiboot
IscsiInitiatorChapId = 
IscsiInitiatorChapPwd = 
FirstTgtIpAddress = ::
FirstTgtIscsiName = 
FirstTgtChapId = 
FirstTgtChapPwd = 
SecondTgtIpAddress = ::
SecondTgtIscsiName = 
SecondTgtChapId = 
SecondTgtChapPwd = 
SecondaryDeviceMacAddr = 00:00:00:00:00:00
BlnkLeds = 0
LnkUpDelayTime = 0
LunBusyRetryCnt = 0
FirstTgtTcpPort = 3260
FirstTgtBootLun = 0
SecondTgtTcpPort = 3260
SecondTgtBootLun = 0
VLanId = 0
TcpIpViaDHCP = Enabled
IscsiViaDHCP = Enabled
ChapAuthEnable = Disabled
IscsiTgtBoot = Enabled
TcpTimestmp = Disabled
FirstHddTarget = Disabled
IpVer = IPv6
WinHbaBootMode = Disabled
ConnectFirstTgt = Disabled
ConnectSecondTgt = Disabled
LegacyBootProto = PXE
LnkSpeed = AutoNeg
WakeOnLan = Disabled
VLanMode = Disabled
BootRetryCnt = No Retry
UseIndTgtPortal = Disabled
UseIndTgtName = Disabled

[NIC.Embedded.3-1]
ChipMdl = BCM5709 C0
MacAddr = 00:24:E8:67:99:19
VirtMacAddr = 00:24:E8:67:99:19
IscsiMacAddr = 00:24:E8:67:99:1A
VirtIscsiMacAddr = 00:24:E8:67:99:1A
DhcpVendId = BRCM ISAN
IscsiInitiatorIpAddr = 0.0.0.0
IscsiInitiatorSubnet = 0.0.0.0
IscsiInitiatorGateway = 0.0.0.0
IscsiInitiatorPrimDns = 0.0.0.0
IscsiInitiatorSecDns = 0.0.0.0
IscsiInitiatorName = iqn.1995-05.com.broadcom.iscsiboot
IscsiInitiatorChapId = 
IscsiInitiatorChapPwd = 
FirstTgtIpAddress = 0.0.0.0
FirstTgtIscsiName = 
FirstTgtChapId = 
FirstTgtChapPwd = 
SecondTgtIpAddress = 0.0.0.0
SecondTgtIscsiName = 
SecondTgtChapId = 
SecondTgtChapPwd = 
SecondaryDeviceMacAddr = 00:00:00:00:00:00
BlnkLeds = 0
LnkUpDelayTime = 0
LunBusyRetryCnt = 0
FirstTgtTcpPort = 3260
FirstTgtBootLun = 0
SecondTgtTcpPort = 3260
SecondTgtBootLun = 0
VLanId = 0
TcpIpViaDHCP = Enabled
IscsiViaDHCP = Enabled
ChapAuthEnable = Disabled
IscsiTgtBoot = Enabled
TcpTimestmp = Disabled
FirstHddTarget = Disabled
IpVer = IPv4
WinHbaBootMode = Disabled
ConnectFirstTgt = Disabled
ConnectSecondTgt = Disabled
LegacyBootProto = PXE
LnkSpeed = AutoNeg
WakeOnLan = Disabled
VLanMode = Disabled
BootRetryCnt = No Retry
UseIndTgtPortal = Disabled
UseIndTgtName = Disabled

[NIC.Embedded.2-1]
ChipMdl = BCM5709 C0
MacAddr = 00:24:E8:67:99:17
VirtMacAddr = 00:24:E8:67:99:17
IscsiMacAddr = 00:24:E8:67:99:18
VirtIscsiMacAddr = 00:24:E8:67:99:18
DhcpVendId = BRCM ISAN
IscsiInitiatorIpAddr = 172.17.11.4
IscsiInitiatorSubnet = 255.255.0.0
IscsiInitiatorGateway = 172.17.1.150
IscsiInitiatorPrimDns = 172.17.1.150
IscsiInitiatorSecDns = 0.0.0.0
IscsiInitiatorName = iqn.1995-05.com.broadcom.iscsiboot:r710:lom2
IscsiInitiatorChapId = 
IscsiInitiatorChapPwd = 
FirstTgtIpAddress = 172.17.14.81
FirstTgtIscsiName = iqn.1984-05.com.dell:powervault.md3200i.60026b9000348f3c000000004c99cb9d
FirstTgtChapId = 
FirstTgtChapPwd = 
SecondTgtIpAddress = 172.17.14.80
SecondTgtIscsiName = iqn.1984-05.com.dell:powervault.md3200i.60026b9000348f3c000000004c99cb9d
SecondTgtChapId = 
SecondTgtChapPwd = 
SecondaryDeviceMacAddr = 00:00:00:00:00:00
BlnkLeds = 0
LnkUpDelayTime = 0
LunBusyRetryCnt = 0
FirstTgtTcpPort = 3260
FirstTgtBootLun = 0
SecondTgtTcpPort = 3260
SecondTgtBootLun = 0
VLanId = 0
TcpIpViaDHCP = Disabled
IscsiViaDHCP = Disabled
ChapAuthEnable = Disabled
IscsiTgtBoot = Disabled
TcpTimestmp = Disabled
FirstHddTarget = Enabled
IpVer = IPv4
WinHbaBootMode = Disabled
ConnectFirstTgt = Enabled
ConnectSecondTgt = Enabled
LegacyBootProto = iSCSI
LnkSpeed = AutoNeg
WakeOnLan = Disabled
VLanMode = Disabled
BootRetryCnt = No Retry
UseIndTgtPortal = Disabled
UseIndTgtName = Disabled

[NIC.Embedded.1-1]
ChipMdl = BCM5709 C0
MacAddr = 00:24:E8:67:99:15
VirtMacAddr = 00:24:E8:67:99:15
IscsiMacAddr = 00:24:E8:67:99:16
VirtIscsiMacAddr = 00:24:E8:67:99:16
DhcpVendId = BRCM ISAN
IscsiInitiatorIpAddr = 0.0.0.0
IscsiInitiatorSubnet = 0.0.0.0
IscsiInitiatorGateway = 0.0.0.0
IscsiInitiatorPrimDns = 0.0.0.0
IscsiInitiatorSecDns = 0.0.0.0
IscsiInitiatorName = 
IscsiInitiatorChapId = 
IscsiInitiatorChapPwd = 
FirstTgtIpAddress = 0.0.0.0
FirstTgtIscsiName = 
FirstTgtChapId = 
FirstTgtChapPwd = 
SecondTgtIpAddress = 0.0.0.0
SecondTgtIscsiName = 
SecondTgtChapId = 
SecondTgtChapPwd = 
SecondaryDeviceMacAddr = 00:00:00:00:00:00
BlnkLeds = 0
LnkUpDelayTime = 0
LunBusyRetryCnt = 0
FirstTgtTcpPort = 3260
FirstTgtBootLun = 0
SecondTgtTcpPort = 3260
SecondTgtBootLun = 0
VLanId = 0
TcpIpViaDHCP = Enabled
IscsiViaDHCP = Enabled
ChapAuthEnable = Disabled
IscsiTgtBoot = Disabled
TcpTimestmp = Disabled
FirstHddTarget = Disabled
IpVer = IPv4
WinHbaBootMode = Disabled
ConnectFirstTgt = Disabled
ConnectSecondTgt = Disabled
LegacyBootProto = PXE
LnkSpeed = AutoNeg
WakeOnLan = Disabled
VLanMode = Disabled
BootRetryCnt = No Retry
UseIndTgtPortal = Disabled
UseIndTgtName = Disabled
"""


if __name__ == "__main__":
    import test.TestLib
    sys.exit(not test.TestLib.runTests( [TestCase] ))
