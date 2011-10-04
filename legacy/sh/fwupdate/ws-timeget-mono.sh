#!/bin/sh
##############################################################################
# Copyright (c) 2011, Dell Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
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
##############################################################################
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

