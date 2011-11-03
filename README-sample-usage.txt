Here is a doc with some sample usage of lcctool to get you started.


$ lcctool add-alias testhost 10.208.46.138 root calvin
$ lcctool ls-alias
testhost
$ lcctool set-default-rac testhost
$ lcctool get-config --subsystem bios --subsystem nic
Getting config for schema http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSEnumeration
Getting config for schema http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSString
Getting config for schema http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_BIOSinteger
Getting config for schema http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute
Configuration for testhost saved to file config-testhost.ini.

$ head config-testhost.ini  -n 20
[main]
host = 10.208.46.138
alias = testhost
config_file_version_major = 1
NIC.Embedded.4-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute']
NIC.Embedded.3-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute']
NIC.Embedded.2-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute']
NIC.Embedded.1-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute']

[NIC.Embedded.4-1]
#readonly#  ChipMdl = BCM5709 C0
#readonly#  MacAddr = 00:24:E8:67:99:1B
#readonly#  VirtMacAddr = 00:24:E8:67:99:1B
#readonly#  IscsiMacAddr = 00:24:E8:67:99:1C
#readonly#  VirtIscsiMacAddr = 00:24:E8:67:99:1C
DhcpVendId = BRCM ISAN
IscsiInitiatorIpAddr = ::
IscsiInitiatorSubnetPrefix = 0
IscsiInitiatorGateway = ::
IscsiInitiatorPrimDns = ::




