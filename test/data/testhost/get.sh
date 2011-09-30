#!/bin/sh

host=10.208.46.138
user=root
pass=calvin

unset ALL_PROXY all_proxy NO_PROXY no_proxy HTTP_PROXY http_proxy HTTPS_PROXY https_proxy

#wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h 10.208.46.138 -u root -p calvin http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSEnumeration > wsman1.txt
#wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h 10.208.46.138 -u root -p calvin http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSString > wsman2.txt
#wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h 10.208.46.138 -u root -p calvin http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSinteger > wsman3.txt

wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h $host -u $user -p $pass http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_NICAttribute > http___schemas_dmtf_org_wbem_wscim_1_cim_schema_2_root_dcim_DCIM_NICAttribute
