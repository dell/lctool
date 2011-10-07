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


from stdcli.trace_decorator import traceLog, getLog

from lcctool import wsman_factory
import schemas

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

etree = schemas.etree

@traceLog()
def commit_settings(host, target, setting, reboot=False):
    wsman = wsman_factory(host)
    ns = schemas.service_names[setting]["ns"]
    job_in = "CreateTargetedConfigJob"
    root = etree.Element("{%s}%s_INPUT" % (ns, job_in))
    etree.SubElement(root, "{%s}Target" % ns).text = target
    if reboot:
        etree.SubElement(root, "{%s}RebootJobType" % ns).text = "1"
    etree.SubElement(root, "{%s}ScheduledStartTime" % ns).text = "TIME_NOW"
    etree.SubElement(root, "{%s}UntilTime" % ns).text = "20121111111111"
    ret_xml = wsman.invoke(schemas.service_names[setting]["invoke_url"], job_in, input_xml=root)
    return ret_xml


@traceLog()
def settings_from_ini(host, ini):
    wsman = wsman_factory(host)
    instance_ids = []
    for section in ini.sections():
        if not ini.has_option("main", section):
            continue
        moduleLog.info("processing %s" % section)
        subsys = ini.get("main", section)
        ns = schemas.service_names[subsys]["ns"]
        set_elem = schemas.service_names[subsys]["set_elem"]
        root = etree.Element("{%s}%s_INPUT" % (ns, set_elem))
        for opt in ini.options(section):
            etree.SubElement(root, "{%s}Target" % ns).text = section
            etree.SubElement(root, "{%s}AttributeName" % ns).text = opt
            etree.SubElement(root, "{%s}AttributeValue" % ns).text = ini.get(section, opt)

        ret_xml = wsman.invoke(schemas.service_names[subsys]["invoke_url"], set_elem, input_xml=root)
        instance_ids.extend(parse_instance_ids(ret_xml))
        yield instance_ids, ret_xml


@traceLog()
def parse_instance_ids(xml):
    # schemas.std_xml_namespaces["wsa"]
    ids = []
    for selector in  xml.iter("{%(wsman)s}Selector" % schemas.std_xml_namespaces):
        if selector.get("Name", None) == "InstanceID":
            ids.append(selector.text)
    return ids

@traceLog()
def stuff_xml_into_ini(host, ini, subsys):
    # run each wsman command in turn, and add the info to the INI object
    wsman = wsman_factory(host)
    schema_list = schemas.dell_schema_list[subsys]
    for item_list in wsman.enumerate(schema_list):
        item_list.attrib["lcctool_subsys"] = subsys
        add_options_to_ini(ini, item_list, subsys)
        yield item_list


# Create the ini file for BIOS or NIC by parsing the XML file from wsman
@traceLog()
def add_options_to_ini(ini, item_list, subsys):
    section_list = {}

    for elem in list(item_list):
        subsys = item_list.attrib["lcctool_subsys"]
        ns = elem.tag.split("}")[0][1:]
        name = elem.find("{%s}AttributeName" % ns).text
        fqdd = elem.find("{%s}FQDD" % ns).text
        value = elem.find("{%s}CurrentValue" % ns).text
        if value is None:
            value = ""

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
        ini.set("main", section, subsys)
