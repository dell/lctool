#!/usr/bin/python
# #############################################################################
#
# Copyright (c) 2011, Dell Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Dell, Inc. nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL Dell, Inc. BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
#
# #############################################################################
# Filename: pullraid.py
# Version: 1.0
# Authors: Sharad Naik
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:coding=latin-1:

import sys, os
from os import system, popen3
from xml.dom.minidom import parse
import xml.dom.minidom

# =============================================================================
class CNARunner:
    '''
    Transforms lists of tests into lists of results.
    '''
    def __init__(self, idracIp, idracUser, idracPass, attrSet):
        '''
        Takes a list of strings, which includes the iDrac ip, username, password and attribute type.
        '''
        self.idracIp = idracIp
        self.idracUser = idracUser
        self.idracPass = idracPass
        self.settings  = attrSet
        self.run()
 
    def run(self):

      # Check for ini filename and remove it if it exists

      fileName = self.idracIp + "_" + self.settings + ".ini"
      fileStat = os.path.exists(fileName)
      if (fileStat == True):
        os.remove(fileName)

      # Create the log file

      logFile = self.idracIp + "_" + self.settings + ".log"
      logfd = open(logFile, 'wb')

      # Build a order list with the Ordered XML file

      print "\n Building the Order Attributes Template File..."
      if (self.settings == 'raid'):
        order_file = "RAID0.01.xml"

      fname = self.buildOrder(self.idracIp, self.settings, order_file)

      logfd.write("Order template file used: " + order_file + "\n\n")

      # Read the Ordered File so it can be used for sorting
      orderAttr = self.read_orderxml(fname)

      # Get the RAID attributes
      print "\n Getting the Attributes ...."

      if (self.settings == 'raid'):
        command = "wsman enumerate http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_RAIDAttribute -h " + self.idracIp +" -P 443 -u " + self.idracUser + " -p " + self.idracPass + " -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -O virtList1.xml"
        tmpList = self.runCommand(command)
        logfd.write( "Command:" + command + "\n\n")
        self.buildIni(self.idracIp, self.settings, orderAttr)
      else:
        print "Option Not Valid. Use raid\n"

      logfd.close()

    # Create the ini style file for RAID attributes by parsing the XML file from wsman

    def buildIni(self, idracIp, settings, orderAttr):

      raidlevel_offset = 7          # Hardcoded offset may change in future
      supportDisk_offset = 2        # Hardcoded offset may change in future
      iniDict = {}
      DOMTree = xml.dom.minidom.parse("virtList1.xml")
      root_elem = DOMTree.documentElement

      attrlist = root_elem.getElementsByTagNameNS('*', 'AttributeName')
      vallist  = root_elem.getElementsByTagNameNS('*', 'CurrentValue')
      fqdd     = root_elem.getElementsByTagNameNS('*', 'FQDD')

      # Check to see if the XML file is empty
      if len(attrlist) == 0:
         return

      i = 0
      j = 0
      fileName = idracIp + "_" + settings + ".ini"
      fileStat = os.path.exists(fileName)
      ofile = open(fileName, 'ab')
      if (fileStat != True):
        print " Creating the .ini file ...."
        ofile.write("[" + fqdd[0].childNodes[0].data + "]")
        ofile.write('\r\n')
      fqdd_save = fqdd[0].childNodes[0].data
      iniList = []                               # Initialize the list
      for attr in attrlist:
        if fqdd_save != fqdd[i].childNodes[0].data:
           iniList.sort(key=orderAttr.get)       # output to file before next fqdd
           for attr_name in iniList:
             ofile.write(attr_name + " = " + iniDict[attr_name])
             ofile.write('\r\n')
           ofile.write('\r\n')
           ofile.write("[" + fqdd[i].childNodes[0].data + "]")
           ofile.write('\r\n')
           fqdd_save = fqdd[i].childNodes[0].data
           iniList = []                          # Initialize List for new fqdd
           iniDict = {}
        if vallist[j].hasChildNodes() == True:
           iniList.append(attr.childNodes[0].data)
           iniDict[attr.childNodes[0].data] = vallist[j].childNodes[0].data
           if (attr.childNodes[0].data == "RAIDSupportedRAIDLevels"):
              j = j + raidlevel_offset 
           elif (attr.childNodes[0].data == "RAIDSupportedDiskProt"):
              j = j + supportDisk_offset
           else:
              j = j + 1

           i = i + 1

      iniList.sort(key=orderAttr.get)
      for attr in iniList:
         ofile.write(attr + " = " + iniDict[attr])
         ofile.write('\r\n')

      ofile.close()

      if (fileStat != True):
        print " File Created: " + fileName 
        print " Adding Attributes to the file..."
      
    # Take the XML which has the ordering of Attributes and extract the order
    def buildOrder(self, idracIp, settings, order_file):

      DOMTree = xml.dom.minidom.parse(order_file)
      root_elem = DOMTree.documentElement
      attrlist = root_elem.getElementsByTagName('AttributeName')
      vallist  = root_elem.getElementsByTagName('DisplayOrder')

      i = 0
      fileName = idracIp + "_" + settings + "order.xml"
      ofile = open(fileName, 'wb')
      for attr in attrlist:
        if vallist[i].hasChildNodes() == True:
           ofile.write(vallist[i].childNodes[0].data + " " + attr.childNodes[0].data)
           ofile.write('\r\n')
        i = i + 1

      ofile.close()
      return fileName

    # Read the  ordered attributes in a dictionary which can then be used as key for sorting
    def read_orderxml(self, filename):
      orderDict = {}
      for line in open(filename):
          line = line.strip()
          if not line: continue
          fields = line.split(" ")
          name = fields[1]
          orderDict[name] = int(fields[0])
      return orderDict

    def runCommand(self, command):
        '''
        Executes command and returns a dictionary.
        '''
        tmpStr = ""
        commandOutList = []
        (fin, fout, ferr) = os.popen3(command, "t")
        fin.close()
        commandOutList.append(command)
        tmpStr = self.smoosh(fout.read())
        commandOutList.append(tmpStr.split('\n'))
        commandOutList.append(ferr.read())
        return commandOutList
        
    def smoosh(self, thing):  # message the output of a command
        '''
        >>> print Shell().smoosh("blah")  #  leave normal strings alone
        blah
        >>> print Shell().smoosh("blah\\n")  # strip trailing blanklines
        blah
        >>> print Shell().smoosh(["blah\\n"])  # if thing is one item list, return the item (smooshed)
        blah
        '''
        if type([]) == type(thing):  # if return is a list of one item, return just the item.
            newthing = []
            for l in thing:
                if '\n' == l[-1:]:
                    newthing.append(l[:-1])
                else:
                    newthing.append(l)
            thing = newthing
                    
            if 1 == len(thing):
                thing = thing[0]
        if type("") == type(thing):  # if return is a string with a newline, strip newline.
            if '\n' == thing[-1:]:
                thing = thing[:-1]
        return thing

# =============================================================================
# Main Program, gets the input values and calls the routine in the main class
if __name__ == '__main__':
  bRunCNA = True
  try:
    idracIp = sys.argv[1]
    idracUser = sys.argv[2]
    idracPass = sys.argv[3]
    attrSet = sys.argv[4]
  except IndexError: #This error happens if you do not specify a file
    print "USAGE: pullraid.py <IPADDRESS> <USERNAME> <USERPASSWORD> raid"
    print "For example: python pullraid.py 192.168.0.111 admin admin123 raid"
    bRunCNA = False
  if bRunCNA == True:
    CNARunner(idracIp, idracUser, idracPass, attrSet)

# =============================================================================
# End of code
# =============================================================================
