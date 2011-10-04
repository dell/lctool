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
# Version: 1.0


DESCRIPTION
===========

This directory contains scripts to get all RAID attributes from iDRAC and saves
the information in an INI formatted file in the form of Name=Value pair.
The INI file can also be used as input to set the RAID attributes on a iDRAC.  

PREREQUISITES
=============

The following are required to run the scripts:

(1) wsmancli - This is a command line tool that sends systems management commands
               using the Web Services for Management standard protocol. Refer to
               http://www.dmtf.org/standards/wsman. The tool is part of the 
               openwsman opensource project. For download and information, refer to
               http://sourceforge.net/projects/openwsman.
			   
(2) python - The scripts are written to run on Python version 2.7. You may run 
             into problems if using older versions. In addition, the module
             xml.dom.minidom is also required. 
			 
             If python not already installed:
             Download python from http://www.python.org/download and choose
             version 2.7 or later. Extract the package and run "configure" 
             then "make" and "make install"

             It will also need the iniparse package
             Download the latest version from:
                 http://code.google.com/p/iniparse/downloads/list
             and then Run:
                 python setup.py install  in the iniparse directory
			 
             If xml.dom.minidom is not already installed:
             Refer to http://docs.python.org/library/xml.dom.minidom.html
	 
TO RUN
======

Get the RAID attributes, run
   . ./pullRAID.sh
or
   ./pullRAID.sh
	
The script will ask you for required information. Upon success, the script
outputs the information in an INI file named with the IP address of the
iDRAC. The INI file contains the list of all NIC attributes in the iDRAC.

The script internally calls a python script. Consequently, you may call
the python script directly as:
   python pullraid.py <IPADDRESS> <USERNAME> <USERPASSWORD> raid


Set the RAID attributes, run
   . ./pushRAID.sh now
or
   ./pushRAID.sh now
	
The script will ask you for required information. Upon success, the script
sets the attributes defined in an INI file, reports any errors related to
setting those attributes, creates a targeted config job and then  provides 
updates on the status of the job that is created and exits when the job is
completed. 

The script internally calls a python script. Consequently, you may call
the python script directly as:
   python pushattr.py <IPADDRESS> <USERNAME> <USERPASSWORD> <INIFILE> raid Now
	
# =============================================================================
# End of content
# =============================================================================
