#!/bin/sh
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
# Version 1.0

. sourceme-uenv

OPTS="${WSOPTS} -N root/dcim -O ${RESPONSEFILE}"
## Mapping for RebootJobType
## 1 = PowerCycle
## 2 = Graceful Reboot without forced shutdown
## 3 = Graceful Reboot with forced shutdown
$WSCOLORCMD; echo wsman invoke -a CreateRebootJob "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService?CreationClassName=DCIM_SoftwareInstallationService,SystemCreationClassName=DCIM_ComputerSystem,SystemName=IDRAC:ID,Name=SoftwareUpdate" -k RebootJobType="1" -k RebootStartTime="TIME_NOW" $OPTS
$WSCOLORREQ;      wsman invoke -a CreateRebootJob "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService?CreationClassName=DCIM_SoftwareInstallationService,SystemCreationClassName=DCIM_ComputerSystem,SystemName=IDRAC:ID,Name=SoftwareUpdate" -k RebootJobType="1" -k RebootStartTime="TIME_NOW" $OPTS >>${WSLOG}
fDisplayResult ${RESPONSEFILE}
$WSCOLORWRN; echo "NOTE: the response is saved to file ${RESPONSEFILE}"
$WSCOLORNORM

