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
import sys
import copy
import xml.dom.minidom
import ConfigParser

from stdcli.trace_decorator import traceLog, getLog
from stdcli.pycompat import call_output

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

basic_wsman_cmd = ["wsman", "-P", "443", "-V", "-v", "-c", "dummy.cert", "-j", "utf-8", "-y", "basic", "-o", "-m", "512"]

# more wsman commands we need to implement
"wsman invoke -a ApplyAttributes http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_%(service)sService?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_%(service)sService,SystemName=DCIM:ComputerSystem,Name=DCIM:%(service)sService -J %(f_name)s"

"wsman invoke -a SetAttributes http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_%(service)sService?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_%(service)sService,SystemName=DCIM:ComputerSystem,Name=DCIM:%(service)sService -J %(f_name)s"

"wsman invoke -a GetRSStatus http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_LCService,SystemName=DCIM:ComputerSystem,Name=DCIM:LCService"

"wsman invoke -a CreateTargetedConfigJob http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_%(jobservice)s?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_%(jobservice)s,SystemName=DCIM:ComputerSystem,Name=DCIM:%(jobservice)s -J %(f_name)s"

"wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=%(job_id)s"

"wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=%(job_id)s"

unit_test_mode = False
test_data_dir = ""

def get_subsystems():
    return dell_schema_list.keys()

dell_schema_list = {
    "bios":  [ "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSEnumeration",
        "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSString",
        "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSinteger",],
    'nic': ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICAttribute"],
    'idrac': ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardAttribute"],
    'raid': ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_RAIDAttribute"],
    }

order_files = {
    'bios': "BIOS0.01.xml",
    'idrac':"IDRAC0.01.xml",
    'nic':  "NIC0.01.xml",
    'raid':  "NIC0.01.xml",
    }

service_names = {
    'bios':  ["BIOS", "BIOSService"],
    'nic':   ["NIC",  "NICService"],
    'idrac': ["iDRACCard", "iDRACCardService"],
    'raid': ["RAID", "RAIDService"],
    }

@traceLog()
def wsman_factory(*args, **kargs):
    if not unit_test_mode:
        return Wsman(*args, **kargs)
    else:
        return MockWsman(*args, **kargs)

class Wsman(object):
    def __init__(self, host):
        self.host = host
        opts = { "-h": self.get_host, "-u": self.get_user, "-p": self.get_password }
        self.wsman_cmd = copy.copy(basic_wsman_cmd)
        for k,v in opts.items():
            if v() is not None:
                self.wsman_cmd.extend([k,v()])

    def get_host(self):
        return self.host.get("host", None)

    def get_user(self):
        return self.host.get("user", None)

    def get_password(self):
        return self.host.get("password", None)

    def get_xml_for_schema(self, schema_list):
        for schema in schema_list:
            moduleLog.info("retrieving info for schema: %s" % schema)
            yield call_output( self.wsman_cmd + ["enumerate", schema], raise_exc=False )

class MockWsman(Wsman):
    def makesafe(self, pth):
        p = re.compile( '[^a-zA-Z0-9]')
        return p.sub( '_', pth)

    def get_xml_for_schema(self, schema_list):
        for schema in schema_list:
            xml_file = open(os.path.join(test_data_dir, self.makesafe(self.get_host()), self.makesafe(schema)), "r")
            xml_str = xml_file.read()
            xml_file.close()
            yield xml_str

@traceLog()
def settings_from_ini(host, ini):
    pass

@traceLog()
def commit_settings(host, setting):
    pass

@traceLog()
def stuff_xml_into_ini(host, ini, setting):
    # run each wsman command in turn, and add the info to the INI object
    schema_list = dell_schema_list[setting]
    wsman = wsman_factory(host)
    if not ini.has_section("breadcrumbs"):
        ini.add_section("breadcrumbs")
    for wsman_xml in wsman.get_xml_for_schema(schema_list):
        add_options_to_ini(ini, wsman_xml, setting)


# Create the ini file for BIOS or NIC by parsing the XML file from wsman
@traceLog()
def add_options_to_ini(ini, wsman_xml, setting):
    iniDict = {}
    DOMTree = xml.dom.minidom.parseString(wsman_xml)
    item_list = DOMTree.documentElement.getElementsByTagNameNS('*', 'Items')[0]
    element_node_type = xml.dom.minidom.Node.ELEMENT_NODE

    section_list = {}

    # iterate over all <Items> sub elements, we dont know what their names are
    for elem in [ e for e in item_list.childNodes if e.nodeType == element_node_type]:
        name  = getNodeText(elem.getElementsByTagNameNS('*', 'AttributeName')[0])
        fqdd  = getNodeText(elem.getElementsByTagNameNS('*', 'FQDD')[0])
        value = getNodeText(elem.getElementsByTagNameNS('*', 'CurrentValue')[0])
        moduleVerboseLog.info("Processing element: %s" % name)

        # something peculiar to idrac, no idea what at this point
        # just emulating old behaviour for now
        grpid = elem.getElementsByTagNameNS('*', 'GroupID')
        if grpid:
            name = getNodeText(grpid[0]) + "#" + name

        section_list[fqdd] = None
        if not ini.has_section(fqdd):
            ini.add_section(fqdd)
        ini.set(fqdd, name, value)
        for section in section_list.keys():
            ini.set("breadcrumbs", section, setting)







# HELPER FUNCTIONS FOR PARSING XML BELOW
def getText(nodelist):
    rc = ""
    if nodelist is not None:
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
    return rc

def getNodeText( node, *args ):
    rc = ""
    node = getNodeElement(node, *args)
    if node is not None:
        rc = getText( node.childNodes )
    return rc

def getNodeElement( node, *args ):
    if len(args) == 0:
        return node

    if node is not None:
        for search in node.childNodes:
            if isinstance(args[0], types.StringTypes):
                if search.nodeName == args[0]:
                    candidate = getNodeElement( search, *args[1:] )
                    if candidate is not None:
                        return candidate
            else:
                if search.nodeName == args[0][0]:
                    attrHash = args[0][1]
                    found = 1
                    for (key, value) in attrHash.items():
                        if search.getAttribute( key ) != value:
                            found = 0
                    if found:
                        candidate = getNodeElement( search, *args[1:] )
                        if candidate is not None:
                            return candidate

