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

import lcctool
import wscim
import schemas
from stdcli.trace_decorator import traceLog, getLog
import wscim_classes
from wscim_classes import *

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

# the purpose of this module is to provide definitions for all the
# Dell-specific cim classes.


# Dell-specfic mixin class that implements some standard methods that are
# useful for setting bios/nic/drac/raid settings. Also, all the dell classes
# have the "FQDD" property.
class DCIM_Mixin(object):
    _property_list  = {"FQDD": "string"}

    @traceLog()
    def get_service_uri(self):
        # cache the uri
        if not self.associated_service_class.get("uri", None):
            self.associated_service_class["uri"] = lcctool.get_service_uri(self.wsman, self.associated_service_class["name"]._ns)
        method = self.associated_service_class["set_method"]
        multi_method = self.associated_service_class["multi_set_method"]
        uri = self.associated_service_class["uri"]
        return {'uri': uri, 'ns': self.associated_service_class["name"]._ns, 'set_method': method, 'multi_set_method': multi_method}

    @traceLog()
    def get_name(self):
        name = self["attributename"]
        if self.has_key("groupid") and self["groupid"]:
            name = self["groupid"] + "#" + name
        return name

    @traceLog()
    def deserialize_ini(self, ini):
        retval = False
        if ini.has_section(self["fqdd"]) and ini.has_option(self["fqdd"], self.get_name()):
            newval = ini.get(self["fqdd"], self.get_name())
            if newval != self["currentvalue"]:
                moduleVerboseLog.debug("setPending: [%s] %s = %s" % (self["fqdd"], self.get_name(), newval))
                self.update_existing({'PendingValue': newval})
                retval = True
            else:
                moduleVerboseLog.debug("Option has not changed: [%s] %s" % (self["fqdd"], self.get_name()))
        else:
            moduleVerboseLog.debug("could not find new section/option: [%s] %s" % (self["fqdd"], self.get_name()))

        return retval

    @traceLog()
    def serialize_ini(self, ini):
        name = self.get_name()
        for sec in ("main", self["fqdd"]):
            if not ini.has_section(sec):
                ini.add_section(sec)

        if self.has_key("isreadonly") and self["isreadonly"].lower() == "true":
            name = "#readonly#  %s" % name

        value = self["currentvalue"]
        if value is None:
            value = ''

        ini.set(self["fqdd"], name, value)



class DCIM_BIOSService(CIM_Service):
    _ns = schemas.std_xml_namespaces['bios_srv']
    _methods = {
        "SetAttribute": {
            'input': {
                "Target": "string",
                "AttributeName": "string",
                "AttributeValue": "string",
            },
            'output': {
                "SetResult": "string",
                "RebootRequired": "string",
                "MessageID": "string",
                "Message": "string",
                "MessageArguments": "string",
            }
         },

        "SetAttributes": {
            'input': {
                "Target": "string",
                "AttributeName": "string",  # array
                "AttributeValue": "string",  # array
            },
            'output': {
                "SetResult": "string",  # array
                "RebootRequired": "string",  # array
                "MessageID": "string",  # array
                "Message": "string",  # array
                "MessageArguments": "string",  # array
            }
        },
        "CreateTargetedConfigJob": {
            'input': {
                "Target": "string",
                "RebootJobType": "uint16",
                "ScheduledStartTime": "string",  # array
                "UntilTime": "string",  # array
            },
            'output': {
                'Job': None,
                "MessageID": "string",  # array
                "Message": "string",  # array
                "MessageArguments": "string",  # array
            }
        },
        "DeletePendingConfiguration": {
            'input': {
                "Target": "string",
            },
            'output': {
                "MessageID": "string",  # array
                "Message": "string",  # array
                "MessageArguments": "string",  # array
            }
        },
        "ChangePassword": {
            'input': {
                "Target": "string",
                "PasswordType": "uint16",
                "OldPassword": "string",
                "NewPassword": "string",
            },
            'output': {
                "MessageID": "string",  # array
                "Message": "string",  # array
                "MessageArguments": "string",  # array
            }
        },
    }
class DCIM_RAIDService(CIM_Service):
    _ns = schemas.std_xml_namespaces['raid_srv']
class DCIM_NICService(CIM_Service):
    _ns = schemas.std_xml_namespaces['nic_srv']
class DCIM_iDRACCardService(CIM_Service):
    _ns = schemas.std_xml_namespaces['idrac_srv']


class DCIM_BIOSAttribute(CIM_BIOSAttribute, DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['bios_attr']
    associated_service_class = {'name': DCIM_BIOSService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
class DCIM_BIOSString(CIM_BIOSString, DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['bios_str']
    associated_service_class = {'name': DCIM_BIOSService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
class DCIM_BIOSinteger(CIM_BIOSInteger, DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['bios_int']
    associated_service_class = {'name': DCIM_BIOSService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
class DCIM_BIOSEnumeration(CIM_BIOSEnumeration, DCIM_Mixin):
    _ns = schemas.std_xml_namespaces['bios_enum']
    associated_service_class = {'name': DCIM_BIOSService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}

class DCIM_RAIDAttribute(CIM_BIOSAttribute, DCIM_Mixin):
    associated_service_class = {'name': DCIM_RAIDService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
    _ns = schemas.std_xml_namespaces['raid_attr']
class DCIM_RAIDString(CIM_BIOSString, DCIM_Mixin):
    associated_service_class = {'name': DCIM_RAIDService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
    _ns = schemas.std_xml_namespaces['raid_str']
class DCIM_RAIDInteger(CIM_BIOSInteger, DCIM_Mixin):
    associated_service_class = {'name': DCIM_RAIDService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
    _ns = schemas.std_xml_namespaces['raid_int']
class DCIM_RAIDEnumeration(CIM_BIOSEnumeration, DCIM_Mixin):
    associated_service_class = {'name': DCIM_RAIDService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
    _ns = schemas.std_xml_namespaces['raid_enum']

class DCIM_NICAttribute(CIM_BIOSAttribute, DCIM_Mixin):
    associated_service_class = {'name': DCIM_NICService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
    _ns = schemas.std_xml_namespaces['nic_attr']
class DCIM_NICString(CIM_BIOSString, DCIM_Mixin):
    associated_service_class = {'name': DCIM_NICService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
    _ns = schemas.std_xml_namespaces['nic_str']
class DCIM_NICInteger(CIM_BIOSInteger, DCIM_Mixin):
    associated_service_class = {'name': DCIM_NICService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
    _ns = schemas.std_xml_namespaces['nic_int']
class DCIM_NICEnumeration(CIM_BIOSEnumeration, DCIM_Mixin):
    associated_service_class = {'name': DCIM_NICService, 'set_method': 'SetAttribute', 'multi_set_method': 'SetAttributes'}
    _ns = schemas.std_xml_namespaces['nic_enum']

class DCIM_iDRACCardAttribute(CIM_BIOSAttribute, DCIM_Mixin):
    associated_service_class = {'name': DCIM_iDRACCardService, 'set_method': 'ApplyAttributes', 'multi_set_method': 'ApplyAttributes'}
    _property_list  = {"GroupID": "string"}
    _ns = schemas.std_xml_namespaces['idrac_attr']
class DCIM_iDRACCardString(CIM_BIOSString, DCIM_Mixin):
    associated_service_class = {'name': DCIM_iDRACCardService, 'set_method': 'ApplyAttributes', 'multi_set_method': 'ApplyAttributes'}
    _property_list  = {"GroupID": "string"}
    _ns = schemas.std_xml_namespaces['idrac_str']
class DCIM_iDRACCardInteger(CIM_BIOSInteger, DCIM_Mixin):
    associated_service_class = {'name': DCIM_iDRACCardService, 'set_method': 'ApplyAttributes', 'multi_set_method': 'ApplyAttributes'}
    _property_list  = {"GroupID": "string"}
    _ns = schemas.std_xml_namespaces['idrac_int']
class DCIM_iDRACCardEnumeration(CIM_BIOSEnumeration, DCIM_Mixin):
    associated_service_class = {'name': DCIM_iDRACCardService, 'set_method': 'ApplyAttributes', 'multi_set_method': 'ApplyAttributes'}
    _property_list  = {"GroupID": "string"}
    _ns = schemas.std_xml_namespaces['idrac_enum']


class DCIM_LifecycleJob(CIM_ConcreteJob):
    _property_list  = { "JobStartTime": 'string', "JobUntilTime": 'string', "Message": 'string', "MessageID": 'string', }
    _ns = schemas.std_xml_namespaces['lc_job']

