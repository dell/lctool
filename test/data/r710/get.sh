#!/bin/sh

wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h 10.208.46.138 -u root -p calvin http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSEnumeration > wsman1.txt
wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h 10.208.46.138 -u root -p calvin http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSString > wsman2.txt
wsman enumerate -P 443 -V -v -c dummy.cert -j utf-8 -y basic -o -m 512 -h 10.208.46.138 -u root -p calvin http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BIOSinteger > wsman3.txt

