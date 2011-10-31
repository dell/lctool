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

import pywbem.cimxml_parse
import pywbem.cim_xml

from stdcli.trace_decorator import traceLog, getLog
moduleVerboseLog = getLog(prefix="verbose")

class TestCase(unittest.TestCase):
    def setUp(self):
        import lcctool
        lcctool.unit_test_mode = 1
        lcctool.test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def tearDown(self):
        pass


    @traceLog()
    def dotestIni(self, subsystems, ini_data_string):
        import lcctool
        import lcctool.wscim_dell_classes
        host = {'host': 'testhost'}

        import lcctool.plugins.config_cli
        ini, xml = lcctool.plugins.config_cli.get_host_config(host, subsystems, output_filename=None, output_format='ini', debug=0)

        # read in known-good INI data
        good_ini = ConfigParser.ConfigParser()
        good_ini.optionxform = str # need to be case sensitive
        fh = cStringIO.StringIO(ini_data_string)
        good_ini.readfp(fh)
        fh.close()

        # check that each entry in good_ini corresponds with ini under test
        for sec in good_ini.sections():
            # GOOD ini has 'extra' sections that may not be there for single-subsystem exports, skip
            if sec == "main": continue
            for opt in good_ini.options(sec):
                #print "check GOOD [%s] %s = %s" % (sec, opt, good_ini.get(sec, opt))
                self.assertEquals(good_ini.get(sec, opt), ini.get(sec, opt))
        # and the reverse, to ensure we dont miss any
        for sec in ini.sections():
            if sec == "main": continue
            for opt in ini.options(sec):
                if opt.startswith("#"): continue
                #print "check SUT  [%s] %s = %s" % (sec, opt, ini.get(sec, opt))
                self.assertEquals(good_ini.get(sec, opt), ini.get(sec, opt))

    def testNic(self):
        self.dotestIni(["nic"], main_ini_testdata + nic_ini_testdata)

    def testIdrac(self):
        self.dotestIni(["idrac"], main_ini_testdata + idrac_ini_testdata)

    def testBios(self):
        self.dotestIni(["bios"], main_ini_testdata + bios_ini_testdata)

    def testCombined(self):
        self.dotestIni(["bios", "idrac", "nic"], main_ini_testdata + bios_ini_testdata + nic_ini_testdata + idrac_ini_testdata)

    def testChangeSettingBios(self):
        import lcctool
        import lcctool.wscim_dell_classes
        host = {'host': 'testhost'}
        ini_str = """\
[main]
host = testhost
BIOS.Setup.1-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSEnumeration', 'http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSString', 'http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSinteger']

[BIOS.Setup.1-1]
SataPortB = Auto
NumLock = Off
"""
        fh = cStringIO.StringIO(ini_str)
        wsman = lcctool.wsman_factory(host)
        import lcctool.plugins.config_cli
        ret = lcctool.plugins.config_cli.stage_config(wsman=wsman, host=host, input_fh=fh, debug=False)
        jobs = []
        for service_ns in ret['service_ns_to_fqdd_map'].keys():
            fqdd_list = dict([ (i, None) for i in ret['service_ns_to_fqdd_map'][service_ns]])
            for res in lcctool.plugins.config_cli.run_method_for_each_fqdd(wsman=wsman, method="CreateTargetedConfigJob",
                                     service_ns=service_ns, fqdd_list=fqdd_list, msg="Committing config for %(fqdd)s",
                                     ScheduledStartTime="TIME_NOW",
                                     UntilTime="20121111111111",   # no idea what that number is....
                                     RebootJobType=1):
                for job_details in lcctool.plugins.config_cli.iter_job_details(res):
                    jobs.append(job_details)
        lcctool.plugins.config_cli.monitor_jobs(wsman, jobs)

    def testFactory(self):
        import lcctool
        import lcctool.wscim_dell_classes
        from lcctool.schemas import etree

        xml = etree.fromstring(test_xml_str_int)
         
        host = {'host': 'testhost'}
        wsman = lcctool.wsman_factory(host)
        i = lcctool.wscim.cim_instance_from_wsxml(wsman, xml)

        self.assertEquals( i['AttributeName'], 'AcPwrRcvryUserDelay' )
        self.assertEquals( i['CurrentValue'], '30' )
        self.assertEquals( i['DefaultValue'], None )
        self.assertEquals( i['FQDD'], 'BIOS.Setup.1-1' )
        self.assertEquals( i['InstanceID'], 'BIOS.Setup.1-1:AcPwrRcvryUserDelay' )
        self.assertEquals( i['IsReadOnly'], 'true')
        self.assertEquals( i['LowerBound'], 30 )
        self.assertEquals( i['PendingValue'], None )
        self.assertEquals( i['UpperBound'], 240 )



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





## test data
main_ini_testdata = """
[main]
BIOS.Setup.1-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSEnumeration', 'http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSString', 'http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSinteger']
iDRAC.Embedded.1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardAttribute']
NIC.Embedded.4-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute']
NIC.Embedded.3-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute']
NIC.Embedded.2-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute']
NIC.Embedded.1-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute']
"""

idrac_ini_testdata = """
[iDRAC.Embedded.1]
NIC.1#DNSRacName = idrac-8HDPBK1
NIC.1#DNSDomainName =
IPv4.1#Address = 10.208.46.138
IPv4.1#Netmask = 255.255.254.0
IPv4.1#Gateway = 10.208.46.1
IPv4.1#DNS1 = 0.0.0.0
IPv4.1#DNS2 = 0.0.0.0
;readonly#  Users.1#UserName = 
Users.2#UserName = root
Users.3#UserName = 
Users.4#UserName = 
Users.5#UserName = 
Users.6#UserName = 
Users.7#UserName = 
Users.8#UserName = 
Users.9#UserName = 
Users.10#UserName = 
Users.11#UserName = 
Users.12#UserName = 
Users.13#UserName = 
Users.14#UserName = 
Users.15#UserName = 
Users.16#UserName = 
;readonly#  Users.1#Password = ******
Users.2#Password = ******
Users.3#Password = ******
Users.4#Password = ******
Users.5#Password = ******
Users.6#Password = ******
Users.7#Password = ******
Users.8#Password = ******
Users.9#Password = ******
Users.10#Password = ******
Users.11#Password = ******
Users.12#Password = ******
Users.13#Password = ******
Users.14#Password = ******
Users.15#Password = ******
Users.16#Password = ******
NIC.1#VLanPriority = 0
NIC.1#VLanID = 1
;readonly#  Users.1#Privilege = 0
Users.2#Privilege = 511
Users.3#Privilege = 0
Users.4#Privilege = 0
Users.5#Privilege = 0
Users.6#Privilege = 0
Users.7#Privilege = 0
Users.8#Privilege = 0
Users.9#Privilege = 0
Users.10#Privilege = 0
Users.11#Privilege = 0
Users.12#Privilege = 0
Users.13#Privilege = 0
Users.14#Privilege = 0
Users.15#Privilege = 0
Users.16#Privilege = 0
NIC.1#Enable = Enabled
NIC.1#Selection = Dedicated
NIC.1#Speed = 100
NIC.1#Autoneg = Enabled
NIC.1#Duplex = Full
NIC.1#DNSRegister = Disabled
NIC.1#DNSDomainNameFromDHCP = Disabled
NIC.1#VLanEnable = Disabled
VirtualMedia.1#Attached = Attached
IPv4.1#Enable = Enabled
IPv4.1#DHCPEnable = Enabled
IPv4.1#DNSFromDHCP = Disabled
;readonly#  Users.1#IpmiLanPrivilege = NoAccess
;readonly#  Users.1#IpmiSerialPrivilege = NoAccess
;readonly#  Users.1#Enable = Disabled
Users.2#IpmiLanPrivilege = Administrator
Users.2#IpmiSerialPrivilege = Administrator
Users.2#Enable = Enabled
Users.3#IpmiLanPrivilege = NoAccess
Users.3#IpmiSerialPrivilege = NoAccess
Users.3#Enable = Disabled
Users.4#IpmiLanPrivilege = NoAccess
Users.4#IpmiSerialPrivilege = NoAccess
Users.4#Enable = Disabled
Users.5#IpmiLanPrivilege = NoAccess
Users.5#IpmiSerialPrivilege = NoAccess
Users.5#Enable = Disabled
Users.6#IpmiLanPrivilege = NoAccess
Users.6#IpmiSerialPrivilege = NoAccess
Users.6#Enable = Disabled
Users.7#IpmiLanPrivilege = NoAccess
Users.7#IpmiSerialPrivilege = NoAccess
Users.7#Enable = Disabled
Users.8#IpmiLanPrivilege = NoAccess
Users.8#IpmiSerialPrivilege = NoAccess
Users.8#Enable = Disabled
Users.9#IpmiLanPrivilege = NoAccess
Users.9#IpmiSerialPrivilege = NoAccess
Users.9#Enable = Disabled
Users.10#IpmiLanPrivilege = NoAccess
Users.10#IpmiSerialPrivilege = NoAccess
Users.10#Enable = Disabled
Users.11#IpmiLanPrivilege = NoAccess
Users.11#IpmiSerialPrivilege = NoAccess
Users.11#Enable = Disabled
Users.12#IpmiLanPrivilege = NoAccess
Users.12#IpmiSerialPrivilege = NoAccess
Users.12#Enable = Disabled
Users.13#IpmiLanPrivilege = NoAccess
Users.13#IpmiSerialPrivilege = NoAccess
Users.13#Enable = Disabled
Users.14#IpmiLanPrivilege = NoAccess
Users.14#IpmiSerialPrivilege = NoAccess
Users.14#Enable = Disabled
Users.15#IpmiLanPrivilege = NoAccess
Users.15#IpmiSerialPrivilege = NoAccess
Users.15#Enable = Disabled
Users.16#IpmiLanPrivilege = NoAccess
Users.16#IpmiSerialPrivilege = NoAccess
Users.16#Enable = Disabled
"""

bios_ini_testdata = """
[BIOS.Setup.1-1]
MemTest = Enabled
MemOpMode = OptimizerMode
NodeInterleave = Disabled
;readonly#  MemVolt = AutoVolt
LogicalProc = Enabled
ProcVirtualization = Enabled
ProcAdjCacheLine = Enabled
ProcHwPrefetcher = Enabled
ProcExecuteDisable = Enabled
ProcCores = All
ProcC1E = Enabled
ProcTurboMode = Enabled
ProcCStates = Enabled
EmbSata = AtaMode
SataPortA = Auto
SataPortB = Off
BootMode = Bios
BootSeqRetry = Disabled
IntegratedRaid = Enabled
UsbPorts = AllOn
InternalUsb = On
;readonly#  InternalSdCard = Off
EmbNic1Nic2 = Enabled
EmbNic1 = EnabledPxe
EmbNic2 = Enabled
EmbNic3Nic4 = Enabled
EmbNic3 = Enabled
EmbNic4 = Enabled
OsWatchdogTimer = Disabled
IoatEngine = Disabled
;readonly#  EmbVideo = Enabled
SriovGlobalEnable = Disabled
SerialComm = OnConRedirCom1
SerialPortAddress = Serial1Com1Serial2Com2
ExtSerialConnector = RemoteAccDevice
FailSafeBaud = 115200
ConTermType = Vt100Vt220
RedirAfterBoot = Enabled
;readonly#  FrontLcd = Advanced
PowerMgmt = OsCtrl
;readonly#  ProcPwrPerf = OsDbpm
;readonly#  FanPwrPerf = MinPwr
;readonly#  MemPwrPerf = MaxPerf
PasswordStatus = Unlocked
TpmSecurity = Off
;readonly#  TpmActivation = NoChange
;readonly#  TpmClear = No
PwrButton = Enabled
NmiButton = Disabled
AcPwrRcvry = Last
AcPwrRcvryDelay = Immediate
NumLock = On
ReportKbdErr = NoReport
ErrPrompt = Disabled
UserLcdStr = 
AssetTag = 
;readonly#  AcPwrRcvryUserDelay = 30
"""

nic_ini_testdata = """
[NIC.Embedded.4-1]
;readonly#  ChipMdl = BCM5709 C0
;readonly#  MacAddr = 00:24:E8:67:99:1B
;readonly#  VirtMacAddr = 00:24:E8:67:99:1B
;readonly#  IscsiMacAddr = 00:24:E8:67:99:1C
;readonly#  VirtIscsiMacAddr = 00:24:E8:67:99:1C
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
;readonly#  VLanId = 0
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
;readonly#  ChipMdl = BCM5709 C0
;readonly#  MacAddr = 00:24:E8:67:99:19
;readonly#  VirtMacAddr = 00:24:E8:67:99:19
;readonly#  IscsiMacAddr = 00:24:E8:67:99:1A
;readonly#  VirtIscsiMacAddr = 00:24:E8:67:99:1A
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
;readonly#  VLanId = 0
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
;readonly#  ChipMdl = BCM5709 C0
;readonly#  MacAddr = 00:24:E8:67:99:17
;readonly#  VirtMacAddr = 00:24:E8:67:99:17
;readonly#  IscsiMacAddr = 00:24:E8:67:99:18
;readonly#  VirtIscsiMacAddr = 00:24:E8:67:99:18
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
;readonly#  VLanId = 0
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
;readonly#  ChipMdl = BCM5709 C0
;readonly#  MacAddr = 00:24:E8:67:99:15
;readonly#  VirtMacAddr = 00:24:E8:67:99:15
;readonly#  IscsiMacAddr = 00:24:E8:67:99:16
;readonly#  VirtIscsiMacAddr = 00:24:E8:67:99:16
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
;readonly#  VLanId = 0
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

