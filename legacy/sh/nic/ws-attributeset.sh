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

subUsage()
{
   $WSCOLORERR; cat <<EOF
USAGE: $0 AttrService FQDD AttrName1=AttrValue1 [AttrNameN=AttrValueN]
The attribute service may be one of the following:
   bios    = BIOS attributes
   dracnw  = DRAC NW attributes
   lc      = LC attributes (FQDD not required)
   nic     = NIC attributes
   raid    = RAID attributes
NOTE: First use either ws-attributelist.sh or ws-attributeget.sh to get
the attribute properties. Ensure it is settable by looking at the 
'IsReadOnly' property and look at the possible values you may set in
the 'PossibleValues' property.
EOF
   $WSCOLORNORM; exit 1
}
if [ ".$2" = "." ] ; then
  subUsage
fi
case "$1" in
  bios)    Class="DCIM_BIOSService"; shift; Target=$1; shift ;;
  dracnw)  Class="DCIM_DRACNWService"; shift; Target=$1; shift ;;
  lc)      Class="DCIM_LCService"; shift ;;
  nic)     Class="DCIM_NICService"; shift; Target=$1; shift ;;
  raid)    Class="DCIM_RAIDService"; shift; Target=$1; shift ;;
  *)       subUsage ;;
esac

METHOD="SetAttribute"
[ $# -gt 1 ] && METHOD="SetAttributes"

OPTS="${WSOPTS} -N root/dcim -O ${RESPONSEFILE} -o -m 256 -M epr"
$WSCOLORCMD; echo wsman enumerate "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/${Class} ${OPTS}"
$WSCOLORREQ;      wsman enumerate  http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/${Class} ${OPTS} >>${WSLOG}
$WSCOLORRSP; cat ${RESPONSEFILE} >>${WSLOG}

ResourceURI=$(grep "wsman:ResourceURI" ${RESPONSEFILE} | xml_grep "wsman:ResourceURI" - --text_only)
Name=$(xml_grep '*[@Name="Name"]' ${RESPONSEFILE} --text_only)
SystemCreationClassName=$(xml_grep '*[@Name="SystemCreationClassName"]' ${RESPONSEFILE} --text_only)
CreationClassName=$(xml_grep '*[@Name="CreationClassName"]' ${RESPONSEFILE} --text_only)
SystemName=$(xml_grep '*[@Name="SystemName"]' ${RESPONSEFILE} --text_only)

echo "<p:${METHOD}_INPUT xmlns:p=\"${ResourceURI}\">" >request.xml
[ ! -z "${Target}" ] && echo -e "   <p:Target>${Target}</p:Target>" >>request.xml
for Attr in "$@"; do
  XName=$(echo ${Attr} | awk -F'=' '{print $1}')
  XValue=$(echo ${Attr} | awk -F'=' '{print $2}')
  echo "   <p:AttributeName>${XName}</p:AttributeName>" >>request.xml
  echo "   <p:AttributeValue>${XValue}</p:AttributeValue>" >>request.xml
done
echo "</p:${METHOD}_INPUT>" >>request.xml

OPTS="${WSOPTS} -N root/dcim -J request.xml -O ${RESPONSEFILE}.1"
$WSCOLORCMD; echo wsman invoke -a ${METHOD} "${ResourceURI}?CreationClassName=${CreationClassName},SystemCreationClassName=${SystemCreationClassName},SystemName=${SystemName},Name=${Name}" $OPTS
$WSCOLORREQ;      wsman invoke -a ${METHOD} "${ResourceURI}?CreationClassName=${CreationClassName},SystemCreationClassName=${SystemCreationClassName},SystemName=${SystemName},Name=${Name}" $OPTS >>${WSLOG}
fDisplayResult ${RESPONSEFILE}.1

$WSCOLORWRN; cat <<EOF
NOTE: The response is saved to file ${RESPONSEFILE}.1
EOF
$WSCOLORNORM

