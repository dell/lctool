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
if [ ".$1" = "." ] ; then
   $WSCOLORERR; echo "USAGE: $0 InstanceID"; $WSCOLORNORM; exit 1
fi
cat <<EOF | sed "s/AAAAA/$1/" >request.xml
<p:InstallFromSoftwareIdentity_INPUT xmlns:p="http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService">
  <p:Target xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:w="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd">
    <a:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</a:Address>
    <a:ReferenceParameters>
      <w:ResourceURI>http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_SoftwareIdentity</w:ResourceURI>
      <w:SelectorSet>
        <w:Selector Name="InstanceID">AAAAA</w:Selector>
      </w:SelectorSet>
    </a:ReferenceParameters>
  </p:Target>
</p:InstallFromSoftwareIdentity_INPUT>
EOF

OPTS="${WSOPTS} -N root/dcim -O ${RESPONSEFILE} -M epr -o -m 256"
$WSCOLORCMD; echo wsman enumerate "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService ${OPTS}"
$WSCOLORREQ;      wsman enumerate  http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_SoftwareInstallationService ${OPTS} >>${WSLOG}
$WSCOLORRSP; cat ${RESPONSEFILE} >>${WSLOG}

CreationClassName=$(grep "Name=\"CreationClassName" ${RESPONSEFILE} | xml_grep '*[@Name="CreationClassName"]' - --text_only)
Name=$(grep "Name=\"Name" ${RESPONSEFILE} | xml_grep '*[@Name="Name"]' - --text_only)
SystemCreationClassName=$(grep "Name=\"SystemCreationClassName" ${RESPONSEFILE} | xml_grep '*[@Name="SystemCreationClassName"]' - --text_only)
SystemName=$(grep "Name=\"SystemName" ${RESPONSEFILE} | xml_grep '*[@Name="SystemName"]' - --text_only)
ResourceURI=$(grep "wsman:ResourceURI" ${RESPONSEFILE} | xml_grep "wsman:ResourceURI" - --text_only)

OPTS="${WSOPTS} -N root/dcim -J request.xml -O ${RESPONSEFILE}.1"
$WSCOLORCMD; echo wsman invoke -a InstallFromSoftwareIdentity "${ResourceURI}?CreationClassName=${CreationClassName},SystemCreationClassName=${SystemCreationClassName},SystemName=${SystemName},Name=${Name}" $OPTS
$WSCOLORREQ;      wsman invoke -a InstallFromSoftwareIdentity "${ResourceURI}?CreationClassName=${CreationClassName},SystemCreationClassName=${SystemCreationClassName},SystemName=${SystemName},Name=${Name}" $OPTS >>${WSLOG}
fDisplayResult ${RESPONSEFILE}.1
$WSCOLORWRN; echo "NOTE: the response is saved to file ${RESPONSEFILE}.1"
$WSCOLORNORM

