#! /bin/sh
#  The "Section x.y.z" below, refers to the section in the Lifecycle_Controller_1_5_Web_Services_Interface_Guide_for_linux.pdf 
#  Security options -v & -V are inserted in every WSMAN command for convenience.
#
#  User command line input uses the following format:
#
#  sh scriptfilename.sh IPADDRESS USERNAME PASSWORD
#
#  [1] Replace IPADDRESS with the actual IP address using the format "aa.bb.cc.dd"  
#  [2] Replace USERNAME with the actual user name to logon to the target system
#  [3] Replace PASSWORD with the actual password to logon to the target system

#
#  BEGINNING OF SCRIPT EXECUTION
#

# --Check for correct number of command line parameters
if [ $# -eq 3 ]
then
  break #continue to script below
else
  echo Usage: sh scriptfilename.sh IPADDRESS USERNAME PASSWORD
  exit 0
fi

IPADDRESS=$1
USERNAME=$2
PASSWORD=$3

#  --Section 11.3.2	Unpack Selected Drivers and Attach to Host OS as USB Device
#
#  --Display command to screen

echo wsman invoke -a UnpackAndAttach "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_OSDeploymentService?CreationClassName=DCIM_OSDeploymentService,Name=DCIM:OSDeploymentService,SystemCreationClassName=DCIM_ComputerSystem,SystemName=DCIM:ComputerSystem" -h $IPADDRESS -V -v -c dummy.cert -P 443 -u $USERNAME -p $PASSWORD -k OSName="<INSERT APPLICABLE VALUE>" -k ExposeDuration="00000000002200.000000:000" -j utf-8 -y basic

#  --Run command

wsman invoke -a UnpackAndAttach "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_OSDeploymentService?CreationClassName=DCIM_OSDeploymentService,Name=DCIM:OSDeploymentService,SystemCreationClassName=DCIM_ComputerSystem,SystemName=DCIM:ComputerSystem" -h $IPADDRESS -V -v -c dummy.cert -P 443 -u $USERNAME -p $PASSWORD -k OSName="<INSERT APPLICABLE VALUE>" -k ExposeDuration="00000000002200.000000:000" -j utf-8 -y basic

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
