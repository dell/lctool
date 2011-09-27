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

import sys, os
from os import system, popen3
from xml.dom.minidom import parse
import xml.dom.minidom

from stdcli.trace_decorator import traceLog, getLog
from stdcli.pycompat import call_output

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

basic_wsman_cmd = ["wsman", "enumerate", "-P", "443", "-V", "-v", "-c", "dummy.cert", "-j", "utf-8", "-y", "basic", "-o", "-m", "512"]
# info for when we get around to porting nic and idrac
#'nic': ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICAttribute"] 
#'idrac': ["http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardAttribute"]

# =============================================================================
class CNARunner:
    '''
    Transforms lists of tests into lists of results.
    '''
    @traceLog()
    def __init__(self, drachost, output_ini_file, order_xml, attr, wsman_cmds):
        '''
        Takes a list of strings, which includes the iDrac ip, username, password and attribute type.
        '''
        # Read the Ordered File so it can be used for sorting
        orderAttr = self.buildOrder(order_xml)
        del(order_xml) # free up memory
  
        # Get the BIOS or NIC attributes
        moduleLog.info("Getting the Attributes")

        basic_wsman_cmd.extend(["-h", drachost["host"],"-u", drachost["user"], "-p", drachost["password"],])
        for wsman_cmd in wsman_cmds:
            wsman_xml = call_output( basic_wsman_cmd + [wsman_cmd], raise_exc=False )
            self.buildIni(output_ini_file, attr, orderAttr, wsman_xml)
            

    # Create the ini file for BIOS or NIC by parsing the XML file from wsman
    @traceLog()
    def buildIni(self, output_ini_file, settings, orderAttr, wsman_xml):

      iniDict = {}
      DOMTree = xml.dom.minidom.parseString(wsman_xml)
      root_elem = DOMTree.documentElement

      if (settings == 'idrac'):
        grpid = root_elem.getElementsByTagNameNS('*', 'GroupID')

      attrlist = root_elem.getElementsByTagNameNS('*', 'AttributeName')
      vallist  = root_elem.getElementsByTagNameNS('*', 'CurrentValue')
      fqdd     = root_elem.getElementsByTagNameNS('*', 'FQDD')

      # Check to see if the XML file is empty
      if len(attrlist) == 0:
         return

      i = 0
      fileStat = os.path.exists(output_ini_file)
      ofile = open(output_ini_file, 'a')
      if (fileStat != True):
        ofile.write("[%s]\n" % fqdd[0].childNodes[0].data )
      fqdd_save = fqdd[0].childNodes[0].data
      iniList = []                               # Initialize the list
      for attr in attrlist:
        if fqdd_save != fqdd[i].childNodes[0].data:
           iniList.sort(key=orderAttr.get)       # output to file before next fqdd
           for attr_name in iniList:
             ofile.write("%s = %s\n" % (attr_name, iniDict[attr_name]))
           ofile.write('\n')
           ofile.write("[%s]\n" % fqdd[i].childNodes[0].data)
           fqdd_save = fqdd[i].childNodes[0].data
           iniList = []                          # Initialize List for new fqdd
           iniDict = {}
        if vallist[i].hasChildNodes() == True:
           if (settings == "idrac"):
             idracattr = grpid[i].childNodes[0].data + "#" + attr.childNodes[0].data
             iniList.append(idracattr)
             iniDict[idracattr] = vallist[i].childNodes[0].data
           else:
             iniList.append(attr.childNodes[0].data)
             iniDict[attr.childNodes[0].data] = vallist[i].childNodes[0].data
        i = i + 1

      iniList.sort(key=orderAttr.get)
      for attr in iniList:
         ofile.write("%s = %s\n" % (attr, iniDict[attr]))

      ofile.close()

    # Take the XML which has the ordering of Attributes and extract the order
    @traceLog()
    def buildOrder(self, order_xml):

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
