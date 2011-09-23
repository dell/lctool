# #############################################################################
#
#  (C) 2011 Dell Inc.  All rights reserved.
#
#  THIS SOFTWARE IS DISTRIBUTED IN THE HOPE THAT IT WILL BE USEFUL, BUT IS
#  PROVIDED "AS IS" WITHOUT ANY WARRANTY, EXPRESS, IMPLIED OR OTHERWISE,
#  INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTY OF MERCHANTABILITY OR
#  FITNESS FOR A PARTICULAR PURPOSE OR ANY WARRANTY REGARDING TITLE OR
#  AGAINST INFRINGEMENT.  IN NO EVENT SHALL DELL BE LIABLE FOR ANY DIRECT,
#  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTUTUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
#  IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#
#  This sample script is provided as an example only, and is not warranted
#  in any way by Dell; Dell disclaims any liability in connection therewith.
#  Dell provides no technical support with regard to content herein. For
#  more information on libraries and tools used in this example, refer to
#  applicable documentation
#
# #############################################################################
# Version: 1.0


DESCRIPTION
===========

This directory contains scripts to get all BIOS attributes from iDRAC and saves
the information in an INI formatted file in the form of Name=Value pair. The
INI file can also be used as input to set the BIOS attributes on a iDRAC.  

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
			 
             If xml.dom.minicom is not already installed:
             Refer to http://docs.python.org/library/xml.dom.minidom.html
	 
TO RUN
======

Get the BIOS attributes, run
   . ./getBIOS.sh
or
   ./getBIOS.sh
	
The script will ask you for required information. Upon success, the script
outputs the information in an INI file named with the IP address of the
iDRAC. The INI file contains the list of all BIOS attributes in the iDRAC.

The script internally calls a python script. Consequently, you may call
the python script directly as:
   python pullattr.py <IPADDRESS> <USERNAME> <USERPASSWORD> bios


Set the BIOS attributes, run
   . ./setBIOS.sh
or
   ./setBIOS.sh
	
The script will ask you for required information. Upon success, the script
sets the attributes defined in an INI file, reports any errors related to
setting those attributes, creates a targeted config job and then  provides 
updates on the status of the job that is created and exits when the job is
completed. 

The script internally calls a python script. Consequently, you may call
the python script directly as:
   python pushattr.py <IPADDRESS> <USERNAME> <USERPASSWORD> <INIFILE> bios Now
	
# =============================================================================
# End of content
# =============================================================================
