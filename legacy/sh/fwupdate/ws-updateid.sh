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

