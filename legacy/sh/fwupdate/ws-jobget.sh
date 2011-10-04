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

