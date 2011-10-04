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

FIRST=$(echo $1 | awk '{print tolower($0)}')
if [ "${FIRST}" = "-h" -o "${FIRST}" = "--help" ]; then
   $WSCOLORERR; cat <<EOF
USAGE: $0
EOF
   $WSCOLORNORM; exit 1
fi

read -n 15 -p "Enter IP address of the Provisioning Server: ? " temp
[ ! "${temp}." = "." ] && export export_serv=${temp}
temp=
read -p "Enter Auto Discovery Value (off=1, Now=2, NextBoot=3): ? " temp
[ ! "${temp}." = "." ] && export auto_discovery=${temp}

METHOD="ReInitiateDHS"

OPTS="${WSOPTS} -N root/dcim -O ${RESPONSEFILE} -o -m 256 -M epr"
$WSCOLORCMD; echo wsman enumerate "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LCService ${OPTS}"
$WSCOLORREQ;      wsman enumerate  http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LCService ${OPTS} >>${WSLOG}
$WSCOLORRSP; cat ${RESPONSEFILE} >>${WSLOG}

ResourceURI=$(grep "wsman:ResourceURI" ${RESPONSEFILE} | xml_grep "wsman:ResourceURI" - --text_only)
Name=$(xml_grep '*[@Name="Name"]' ${RESPONSEFILE} --text_only)
SystemCreationClassName=$(xml_grep '*[@Name="SystemCreationClassName"]' ${RESPONSEFILE} --text_only)
CreationClassName=$(xml_grep '*[@Name="CreationClassName"]' ${RESPONSEFILE} --text_only)
SystemName=$(xml_grep '*[@Name="SystemName"]' ${RESPONSEFILE} --text_only)

echo "<p:${METHOD}_INPUT xmlns:p=\"${ResourceURI}\">" >request.xml
  echo "   <p:ProvisioningServer>${export_serv}</p:ProvisioningServer>" >>request.xml
  echo "   <p:ResetToFactoryDefaults>TRUE</p:ResetToFactoryDefaults>" >>request.xml
  echo "   <p:PerformAutoDiscovery>${auto_discovery}</p:PerformAutoDiscovery>" >>request.xml
echo "</p:${METHOD}_INPUT>" >>request.xml


OPTS="${WSOPTS} -N root/dcim -J request.xml -O ${RESPONSEFILE}.1"
$WSCOLORCMD; echo wsman invoke -a ${METHOD} "${ResourceURI}?CreationClassName=${CreationClassName},SystemCreationClassName=${SystemCreationClassName},SystemName=${SystemName},Name=${Name}" $OPTS 
$WSCOLORREQ;      wsman invoke -a ${METHOD} "${ResourceURI}?CreationClassName=${CreationClassName},SystemCreationClassName=${SystemCreationClassName},SystemName=${SystemName},Name=${Name}" $OPTS  >>${WSLOG}
fDisplayResult ${RESPONSEFILE}.1

$WSCOLORWRN; cat <<EOF
NOTE: the response is saved to file ${RESPONSEFILE}.1
EOF
$WSCOLORNORM

