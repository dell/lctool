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
USAGE: $0 AttrService
The attribute service AttrService may be one of the following:
   bconfig   = List BIOS Enumerations
   bsource   = List BIOS String Inventory
EOF
#   $WSCOLORNORM; exit 1
   $WSCOLORNORM;
}
if [ ".$1" = "." ] ; then
  subUsage
fi
case "$1" in
  bconfig) Classes="DCIM_BootConfigSetting" ;;
  bsource) Classes="DCIM_BootSourceSetting" ;;

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

