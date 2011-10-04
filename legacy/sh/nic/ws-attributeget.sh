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

