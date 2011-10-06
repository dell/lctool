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
import tempfile
import ConfigParser

from stdcli.trace_decorator import traceLog, getLog
from stdcli.pycompat import call_output

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

#The ultra-compatible way to import lxml
# yes. it is gross.
try:
  from lxml import etree
  moduleVerboseLog.debug("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    moduleVerboseLog.debug("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      moduleVerboseLog.debug("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        moduleVerboseLog.debug("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          moduleVerboseLog.debug("running with ElementTree")
        except ImportError:
          moduleVerboseLog.debug("Failed to import ElementTree from any known place")
          raise

try:
    register_namespace = etree.register_namespace
except AttributeError:
    def register_namespace(prefix, uri):
        etree._namespace_map[uri] = prefix


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

std_xml_namespaces = {
    "soap":  "http://www.w3.org/2003/05/soap-envelope",
    "wsen":  "http://schemas.xmlsoap.org/ws/2004/09/enumeration",
    "wsman": "http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd",
    "xsi":   "http://www.w3.org/2001/XMLSchema-instance",

    'raid_attr': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_RAIDAttribute",
    'idrac_attr':"http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardAttribute",
    'nic_attr':  "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICAttribute",
    'bios_enum': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSEnumeration",
    'bios_str':  "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSString",
    'bios_int':  "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSinteger",

    'bios_srv': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSService",
    'nic_srv':  "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICService",
    'idrac_srv':"http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardService",
    'raid_srv': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_RAIDService",
    'lc_srv': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",

    'lc_job': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob",
    }

def get_subsystems():
    return dell_schema_list.keys()

dell_schema_list = {
    "bios":  [ std_xml_namespaces["bios_enum"], std_xml_namespaces["bios_str"], std_xml_namespaces["bios_int"], ],
    'nic': [ std_xml_namespaces["nic_attr"] ],
    'idrac': [ std_xml_namespaces["idrac_attr"] ],
    'raid': [ std_xml_namespaces["raid_attr"] ],
    }

_urlpart = "%(ns)s?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_%(service)sService,SystemName=DCIM:ComputerSystem,Name=DCIM:%(service)sService"

service_names = {
    'bios':  {"set_elem": "SetAttributes",   "ns": std_xml_namespaces['bios_srv'], "invoke_url": _urlpart % {"service": "BIOS", "ns": std_xml_namespaces['bios_srv']},},
    'nic':   {"set_elem": "SetAttributes",   "ns": std_xml_namespaces['nic_srv'],  "invoke_url": _urlpart % {"service": "NIC", "ns": std_xml_namespaces['nic_srv']},},
    'idrac': {"set_elem": "ApplyAttributes", "ns": std_xml_namespaces['idrac_srv'],"invoke_url": _urlpart % {"service": "iDRACCard", "ns": std_xml_namespaces['idrac_srv']},},
    'raid':  {"set_elem": "SetAttributes",   "ns": std_xml_namespaces['raid_srv'], "invoke_url": _urlpart % {"service": "RAID", "ns": std_xml_namespaces['raid_srv']},},
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
        opts = { "-h": self._get_host, "-u": self._get_user, "-p": self._get_password }
        self.wsman_cmd = copy.copy(basic_wsman_cmd)
        for k,v in opts.items():
            if v() is not None:
                self.wsman_cmd.extend([k,v()])

    def _get_host(self):
        return self.host.get("host", None)

    def _get_user(self):
        return self.host.get("user", None)

    def _get_password(self):
        return self.host.get("password", None)

    def enumerate(self, schema_list, filter=None):
        for schema in schema_list:
            moduleLog.info("retrieving info for schema: %s" % schema)
            yield call_output( self.wsman_cmd + ["enumerate", schema], raise_exc=False )

    def invoke(self, schema, cmd, input_xml, *args, **kargs):
        wsman_cmd = copy.copy(self.wsman_cmd)
        if input_xml:
            fd, fn = tempfile.mkstemp(suffix=".xml")
            os.write(fd, etree.tostring(input_xml))
            os.close(fd)
            wsman_cmd.extend(["-J", fn])

        wsman_cmd.extend(["invoke", "-a", cmd, schema])
        print "REPR: %s" % wsman_cmd
        print "JOIN: %s" % " ".join(wsman_cmd)

#        if input_xml:
#            os.unlink(fn)


    def get(self, schema_list, *args, **kargs):
        pass


class MockWsman(Wsman):
    def makesafe(self, pth):
        p = re.compile( '[^a-zA-Z0-9]')
        return p.sub( '_', pth)

    def enumerate(self, schema_list):
        for schema in schema_list:
            xml_file = open(os.path.join(test_data_dir, self.makesafe(self._get_host()), self.makesafe(schema)), "r")
            xml_str = xml_file.read()
            xml_file.close()
            yield xml_str

    def invoke(self, *args, **kargs):
        pass

    def get(self, *args, **kargs):
        pass

@traceLog()
def commit_settings(host, setting):
    pass

@traceLog()
def settings_from_ini(host, ini):
    wsman = wsman_factory(host)
    for section in ini.sections():
        if not ini.has_option("main", section):
            continue
        moduleLog.info("processing %s" % section)
        subsys = ini.get("main", section)
        ns = service_names[subsys]["ns"]
        set_elem = service_names[subsys]["set_elem"]
        root = etree.Element("{%s}%s_INPUT" % (ns, set_elem))
        for opt in ini.options(section):
            etree.SubElement(root, "{%s}Target" % ns).text = section
            etree.SubElement(root, "{%s}AttributeName" % ns).text = opt
            etree.SubElement(root, "{%s}AttributeValue" % ns).text = ini.get(section, opt)

        wsman.invoke(service_names[subsys]["invoke_url"], set_elem, input_xml=root)


@traceLog()
def stuff_xml_into_ini(host, ini, setting):
    # run each wsman command in turn, and add the info to the INI object
    schema_list = dell_schema_list[setting]
    wsman = wsman_factory(host)
    for wsman_xml in wsman.enumerate(schema_list):
        add_options_to_ini(ini, wsman_xml, setting)


# Create the ini file for BIOS or NIC by parsing the XML file from wsman
@traceLog()
def add_options_to_ini(ini, wsman_xml, setting):
    root = etree.fromstring(wsman_xml)
    section_list = {}

    # iterate over all <Items> sub elements, we dont know what their names are
    for item_list in  root.iter("{%(wsman)s}Items" % std_xml_namespaces):
      for elem in list(item_list):
        ns = elem.tag.split("}")[0][1:]
        name = elem.find("{%s}AttributeName" % ns).text
        fqdd = elem.find("{%s}FQDD" % ns).text
        value = elem.find("{%s}CurrentValue" % ns).text

        moduleVerboseLog.info("Processing element: %s" % name)

        # something peculiar to idrac
        grpid = elem.find('{%s}GroupID' % ns)
        if grpid is not None:
            name = grpid.text + "#" + name

        section_list[fqdd] = None
        if not ini.has_section(fqdd):
            ini.add_section(fqdd)
        ini.set(fqdd, name, value)

    for section in section_list.keys():
        ini.set("main", section, setting)

