#!/bin/bash

unset ALL_PROXY all_proxy NO_PROXY no_proxy HTTP_PROXY http_proxy HTTPS_PROXY https_proxy

host=${1:-10.208.46.138}
user=${2:-root}
pass=${3:-calvin}

mkdir $host

wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h $host -u $user -p $pass http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSEnumeration > $host/http___schemas_dmtf_org_wbem_wscim_1_cim_schema_2_root_dcim_DCIM_BIOSEnumeration
wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h $host -u $user -p $pass http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSString > $host/http___schemas_dmtf_org_wbem_wscim_1_cim_schema_2_root_dcim_DCIM_BIOSString
wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h $host -u $user -p $pass http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSinteger > $host/http___schemas_dmtf_org_wbem_wscim_1_cim_schema_2_root_dcim_DCIM_BIOSinteger

wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h $host -u $user -p $pass http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_iDRACCardAttribute > $host/http___schemas_dmtf_org_wbem_wscim_1_cim_schema_2_root_dcim_DCIM_iDRACCardAttribute

wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h $host -u $user -p $pass http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICAttribute > $host/http___schemas_dmtf_org_wbem_wscim_1_cim_schema_2_root_dcim_DCIM_NICAttribute
