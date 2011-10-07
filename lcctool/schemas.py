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

std_xml_namespaces = {
    # standards based namespaces we will be working with
    "soap":  "http://www.w3.org/2003/05/soap-envelope",
    "wsen":  "http://schemas.xmlsoap.org/ws/2004/09/enumeration",
    "wsman": "http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd",
    "wsa":   "http://schemas.xmlsoap.org/ws/2004/08/addressing",
    "xsi":   "http://www.w3.org/2001/XMLSchema-instance",

    # configuration namespaces
    'raid_attr': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_RAIDAttribute",
    'idrac_attr':"http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardAttribute",
    'nic_attr':  "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICAttribute",
    'bios_enum': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSEnumeration",
    'bios_str':  "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSString",
    'bios_int':  "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSinteger",

    # service namespaces
    'bios_srv': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSService",
    'nic_srv':  "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICService",
    'idrac_srv':"http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardService",
    'raid_srv': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_RAIDService",
    'lc_srv': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService",

    # lifecycle controller misc
    'lc_job': "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob",
    }

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

# cant trace this one as it gets called during CLI option setup
def get_subsystems():
    return dell_schema_list.keys()


