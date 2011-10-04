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

FIRST=$( echo $1 | awk '{print tolower($0)}')
if [ "${FIRST}" = "-h" -o "${FIRST}" = "--help" ]; then
   $WSCOLORERR; cat <<EOF
USAGE: $0 InstanceID enable_status sourceid
EOF
   $WSCOLORNORM; exit 1
fi

subUsage()
{
   $WSCOLORERR; cat <<EOF
USAGE: $0 InstanceID enable_status instance_sourceid
EOF
   $WSCOLORNORM; exit 1
}
if  [ ".$1" = "."  -o ".$2" = "." -o ".$3" = "."  ] ; then
  subUsage
fi


METHOD="ChangeBootSourceState"
instance=$1
enable=$2
boot_source=$3

OPTS="${WSOPTS} -N root/dcim -O ${RESPONSEFILE} -o -m 256 -M epr"
$WSCOLORCMD; echo wsman enumerate "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_BootConfigSetting ${OPTS}"
$WSCOLORREQ;      wsman enumerate  http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_BootConfigSetting ${OPTS} >>${WSLOG}
$WSCOLORRSP; cat ${RESPONSEFILE} >>${WSLOG}

#ResourceURI=$(grep "wsman:ResourceURI" ${RESPONSEFILE} | xml_grep "wsman:ResourceURI" - --text_only)

OPTS="${WSOPTS} -N root/dcim -O ${RESPONSEFILE}.1"
$WSCOLORCMD; echo wsman invoke -a ${METHOD} "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_BootConfigSetting?InstanceID=${instance}" -k EnabledState=$enable -k source=$boot_source $OPTS
$WSCOLORREQ;      wsman invoke -a ${METHOD} "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_BootConfigSetting?InstanceID=${instance}" -k EnabledState=$enable -k source=$boot_source $OPTS >>${WSLOG}
fDisplayResult ${RESPONSEFILE}.1

$WSCOLORWRN; cat <<EOF
NOTE: the response is saved to file ${RESPONSEFILE}.1
EOF
$WSCOLORNORM
