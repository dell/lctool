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


subUsage()
{
   $WSCOLORERR; cat <<EOF
USAGE: $0 AttrService
The attribute service AttrService may be one of the following:
   power    = Power Supply Inventory
   fan      = Fan Inventory
   memory   = Platform Physical Memory
   cpu      = Platform CPUs
   idrac    = iDRAC Remote Access Card
   pci      = Platform PCI devices
   video    = Platform Video controllers
   vflash   = Physical attributes of virtual flash media
   nic      = NIC Controller Configuration
   system   = System attributes
EOF
   $WSCOLORNORM; exit 1
   $WSCOLORNORM;
}
if [ ".$1" = "." ] ; then
  subUsage
fi
case "$1" in
  power)  Classes="DCIM_PowerSupplyView" ;;
  fan)    Classes="DCIM_FanView" ;;
  memory) Classes="DCIM_MemoryView" ;;
  cpu)    Classes="DCIM_CPUView" ;;
  idrac)  Classes="DCIM_iDRACCARDView" ;;
  pci)    Classes="DCIM_PCIDeviceView" ;;
  video)  Classes="DCIM_VideoView" ;;
  vflash) Classes="DCIM_VFlashView" ;;
  nic)    Classes="DCIM_NICView" ;;
  system) Classes="DCIM_SystemView" ;;

  *)       subUsage ;;
esac

Index=1
Notes=


for Class in ${Classes}; do
  OPTS="${WSOPTS} -o -m 256 -O ${RESPONSEFILE}"
  $WSCOLORCMD; echo wsman enumerate "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/${Class}" $OPTS
  $WSCOLORREQ;      wsman enumerate "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/${Class}" $OPTS >>${WSLOG}
  fDisplayResult ${RESPONSEFILE}
  Notes="$Notes ${RESPONSEFILE}.${Index}"
  Index=$((Index + 1))
done

$WSCOLORWRN; cat <<EOF
NOTE: the response is saved to file ${RESPONSEFILE}
EOF
$WSCOLORNORM

