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
#
# #############################################################################
# Filename: pullattr.py
# Version: 1.0
# Authors: Sharad Naik

import os
import sys
import copy
import xml.dom.minidom
import ConfigParser

from stdcli.trace_decorator import traceLog, getLog
from stdcli.pycompat import call_output

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

basic_wsman_cmd = ["wsman", "enumerate", "-P", "443", "-V", "-v", "-c", "dummy.cert", "-j", "utf-8", "-y", "basic", "-o", "-m", "512"]

@traceLog()
def CNARunner(drachost, ini, attr, wsman_cmds):
    '''
    Takes a list of strings, which includes the iDrac ip, username, password and attribute type.
    '''
    # add basic authentication options to wsman command line
    wsman_cmd = copy.copy(basic_wsman_cmd)
    wsman_cmd.extend(["-h", drachost["host"],"-u", drachost["user"], "-p", drachost["password"],])

    # run each wsman command in turn, and add the info to the INI object
    for cmd in wsman_cmds:
        wsman_xml = call_output( wsman_cmd + [cmd], raise_exc=False )
        add_options_to_ini(ini, attr, wsman_xml)
    

# Create the ini file for BIOS or NIC by parsing the XML file from wsman
@traceLog()
def add_options_to_ini(ini, settings, wsman_xml):
    iniDict = {}
    DOMTree = xml.dom.minidom.parseString(wsman_xml)
    item_list = DOMTree.documentElement.getElementsByTagNameNS('*', 'Items')[0]
    element_node_type = xml.dom.minidom.Node.ELEMENT_NODE

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
            value = value + "#" + getNodeText(grpid[0])

        if not ini.has_section(fqdd):
            ini.add_section(fqdd)
        ini.set(fqdd, name, value)

# Take the XML which has the ordering of Attributes and extract the order
@traceLog()
def get_display_order(order_xml):
  DOMTree = xml.dom.minidom.parseString(order_xml)
  root_elem = DOMTree.documentElement
  attrlist = root_elem.getElementsByTagName('AttributeName')
  vallist  = root_elem.getElementsByTagName('DisplayOrder')
  orderDict = {}

  i = 0
  for attr in attrlist:
    if vallist[i].hasChildNodes() == True:
       orderDict[attr.childNodes[0].data] = int(vallist[i].childNodes[0].data)
    i = i + 1

  return orderDict



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

