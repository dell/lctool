#!/bin/sh
# #############################################################################
#
# Copyright (c) 2011, Dell Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Dell, Inc. nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL Dell, Inc. BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
#
# #############################################################################
# Filename: pushBIOS.sh
# Version: 1.0
# Authors: Sharad Naik

export WSCOLORCMD="echo -en \\033[0;32m"
export WSCOLORREQ="echo -en \\033[0;31m"
export WSCOLORRSP="echo -en \\033[0;34m"
export WSCOLORWRN="echo -en \\033[0;36m"
export WSCOLORERR="echo -en \\033[0;35m"
export WSCOLORNORM="echo -en \\033[0;39m"
export WSNIL="xsi:nil"

subUsage()
{
   $WSCOLORERR; cat <<EOF
USAGE: $0 flag
The flag may be one of the following:
   set    = Only set the attributes from the .ini file
   commit = Commit the attributes set previously,  The host will be rebooted
   now    = Set and then commit, The host will be rebooted
EOF
   $WSCOLORNORM; exit 1
   $WSCOLORNORM;
}

if [ ".$1" = "." ] ; then
  subUsage
fi

case "$1" in
  set)       Flag="Set" ;;
  commit)    Flag="Commit" ;;
  now)       Flag="Now" ;;

  *)       subUsage ;;
esac


read -n 15 -p "IP address (ENTER for default: ${WSENDPOINT}) ? " temp
[ ! "${temp}." = "." ] && export WSENDPOINT=${temp}
temp=
read -p "User name (ENTER for default: ${WSUSER}) ? " temp
[ ! "${temp}." = "." ] && export WSUSER=${temp}
temp=
read -p "User password (ENTER for default: ${WSPASS}) ? " temp
[ ! "${temp}." = "." ] && export WSPASS=${temp}
temp=
read -p "Config attributes(.ini) file, to be pushed: (ENTER for default: ${WSFILE}) ? " temp
[ ! "${temp}." = "." ] && export WSFILE=${temp}
temp=

/usr/bin/python pushattr.py $WSENDPOINT $WSUSER $WSPASS $WSFILE bios $Flag

# =============================================================================
# End of code
# =============================================================================
