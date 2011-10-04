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

OPTS="${WSOPTS} -o -N root/dcim -M epr -O ${RESPONSEFILE}"
$WSCOLORCMD; echo wsman enumerate http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_TimeService $OPTS
$WSCOLORREQ;      wsman enumerate http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_TimeService $OPTS >>${WSLOG}
$WSCOLORRSP; cat ${RESPONSEFILE} >>${WSLOG}

ResourceURI=$(xml_grep 'wsman:ResourceURI' ${RESPONSEFILE} --text_only)
Name=$(xml_grep '*[@Name="Name"]' ${RESPONSEFILE} --text_only)
SystemCreationClassName=$(xml_grep '*[@Name="SystemCreationClassName"]' ${RESPONSEFILE} --text_only)
CreationClassName=$(xml_grep '*[@Name="CreationClassName"]' ${RESPONSEFILE} --text_only)
SystemName=$(xml_grep '*[@Name="SystemName"]' ${RESPONSEFILE} --text_only)

OPTS="${WSOPTS} -o -N root/dcim -M epr -O ${RESPONSEFILE}.1"
$WSCOLORCMD; echo wsman enumerate http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_SPComputerSystem $OPTS
$WSCOLORREQ;      wsman enumerate http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_SPComputerSystem $OPTS >>${WSLOG}
$WSCOLORRSP; cat ${RESPONSEFILE}.1 >>${WSLOG}

RefParam=`xml_grep 'wsa:ReferenceParameters' ${RESPONSEFILE}.1 | sed '1d' | sed '1d' | sed '1d' | sed '$d' | sed '$d'`
URI=$(echo ${ResourceURI} | sed 's/\//\\\//g' )
cat <<EOF | sed "s/AAAAA/${URI}/" >request.xml
<p:ManageTime_INPUT xmlns:p="AAAAA">
  <p:GetRequest>true</p:GetRequest>
  <p:ManagedElement xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd">
    <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
EOF
echo ${RefParam} >>request.xml
cat <<EOF >>request.xml
  </p:ManagedElement>
</p:ManageTime_INPUT>
EOF

OPTS="${WSOPTS} -N root/dcim -O ${RESPONSEFILE}.2"
$WSCOLORCMD; echo wsman invoke -a ManageTime "${ResourceURI}?CreationClassName=${CreationClassName},Name=${Name},SystemCreationClassName=${SystemCreationClassName},SystemName=${SystemName}" $OPTS -J request.xml 
$WSCOLORREQ;      wsman invoke -a ManageTime "${ResourceURI}?CreationClassName=${CreationClassName},Name=${Name},SystemCreationClassName=${SystemCreationClassName},SystemName=${SystemName}" $OPTS -J request.xml >>${WSLOG}
fDisplayResult ${RESPONSEFILE}.2
$WSCOLORWRN; echo "NOTE: the response is saved to file ${RESPONSEFILE}.2"
$WSCOLORNORM

