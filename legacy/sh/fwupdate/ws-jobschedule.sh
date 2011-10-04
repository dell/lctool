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

scheduled_time="TIME_NOW "

if [ $2 ]
then
    scheduled_time="$2 "
else
   $WSCOLORERR; echo "USAGE: $0 JobID YYYYMMDDHHmmSS"; 
   echo "Y=year, M=month, D=day, H=hour, m=minutes, and S=seconds."   
   $WSCOLORNORM; exit 1
fi



OPTS="${WSOPTS} -N root/dcim -O ${RESPONSEFILE}"
## OTHER OPTIONS
## -k RunMonth="1" -k RunDay="21"
$WSCOLORCMD; echo wsman invoke -a SetupJobQueue "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_JobService?CreationClassName=DCIM_JobService,Name=JobService,SystemName=Idrac,SystemCreationClassName=DCIM_ComputerSystem" -k JobArray="$1" -k StartTimeInterval=$scheduled_time $OPTS
$WSCOLORREQ;      wsman invoke -a SetupJobQueue "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_JobService?CreationClassName=DCIM_JobService,Name=JobService,SystemName=Idrac,SystemCreationClassName=DCIM_ComputerSystem" -k JobArray="$1" -k StartTimeInterval=$scheduled_time $OPTS >>${WSLOG}
fDisplayResult ${RESPONSEFILE}
$WSCOLORWRN; echo "NOTE: the response is saved to file ${RESPONSEFILE}"
$WSCOLORNORM

