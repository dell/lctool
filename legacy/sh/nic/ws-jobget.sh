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

# Try "DCIM_SoftwareInstallationConcreteJob"

. sourceme-uenv
if [ ".$1" = "." ] ; then
   $WSCOLORERR; echo "USAGE: $0 JobID"; $WSCOLORNORM; exit 1
fi
MYCLASS="DCIM_LifecycleJob"

OPTS="${WSOPTS} -m 32 -o -N root/dcim"
while : ; do
  echo wsman get "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/${MYCLASS}?InstanceID=$1" $OPTS
  $WSCOLORRSP; wsman get "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/${MYCLASS}?InstanceID=$1" $OPTS | grep -i -e instanceid -e jobstarttime -e jobstatus -e :name -e ":message>"
  $WSCOLORWRN; read -t 6 -n 1 -p "Q: Operation repeats, stop [y|n] ? "
  [ "${REPLY}" = "y" ] && break
  echo
done
$WSCOLORNORM ; echo

