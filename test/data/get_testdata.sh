#!/bin/bash

set -x
#set -e

unset ALL_PROXY all_proxy NO_PROXY no_proxy HTTP_PROXY http_proxy HTTPS_PROXY https_proxy

host=${1:-${host:-10.208.46.138}}
user=${2:-${user:-root}}
pass=${3:-${pass:-calvin}}

mkdir $host ||:

dell_uri=http://schemas.dell.com/wbem/wscim/1/cim-schema/2
 dell_fn=http___schemas_dell_com_wbem_wscim_1_cim-schema_2
std_opts="-P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512"

for enum in DCIM_BIOSEnumeration DCIM_BIOSString DCIM_BIOSinteger  DCIM_iDRACCardAttribute DCIM_NICAttribute DCIM_RAIDAttribute DCIM_BIOSService DCIM_RAIDService DCIM_NICService DCIM_iDRACCardService CIM_BIOSAttribute
do
    wsman enumerate $std_opts -h $host -u "$user" -p "$pass" $dell_uri/$enum > $host/enumerate_${dell_fn}_$enum
done
