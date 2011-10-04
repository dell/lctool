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
if [ ".$2" = "." ] ; then
   $WSCOLORERR; cat <<EOF
USAGE: $0 ClassName InstanceID
For example: DCIM_BIOSEnumeration BIOS.Setup.1-1:NumLock
EOF
   $WSCOLORNORM; exit 1
fi
ClassName=$1
ID=$2

OPTS="${WSOPTS} -N root/dcim -O ${RESPONSEFILE}"
$WSCOLORCMD; echo wsman get "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/${ClassName}?InstanceID=${ID}" $OPTS
$WSCOLORREQ;      wsman get "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/${ClassName}?InstanceID=${ID}" $OPTS >>${WSLOG}
$WSCOLORRSP; cat ${RESPONSEFILE} >>${WSLOG}
fDisplayResult ${RESPONSEFILE}
$WSCOLORWRN; echo "NOTE: the response is saved to file ${RESPONSEFILE}"
$WSCOLORNORM

