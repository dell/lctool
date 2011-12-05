Here is a doc with some sample usage of lctool to get you started.



######## ALIASES ###########

Adding aliases: You can specify a specific RAC to operate on each and every command line using the --rac-host, --rac-user, --rac-password options. This can be a pain, especially if you want to operate against the same RAC with all your commands. You can create "aliases" as well as specify a default RAC to use if none is specified on the CLI

$ lctool add-alias testhost 10.208.46.138 root calvin
$ lctool ls-alias
testhost
$ lctool set-default-rac testhost

Now, any time you just run 'lctool COMMAND', it will operate on your default RAC. Note also that for every 'lctool' command, you can specify multiple RACs, using multiple aliases. You can also create "groups", so you can specify multiple racs very easily. Groups can be nested up to a default of 16 times. Recursively nested groups longer than this limit will trigger an error condition which will launch all of the warheads. Don't do it.



######## CONFIGURATION ###########

You can dump BIOS/RAID/NIC configuration to INI files. You can also use INI files to set configuration options:

$ lctool get-config --subsystem bios --subsystem nic
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
NIC.Embedded.1-1 = ['http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_NICAttribute']
 ... cut ...

[NIC.Embedded.1-1]
DhcpVendId = BRCM ISAN
IscsiInitiatorIpAddr = ::
IscsiInitiatorSubnetPrefix = 0
IscsiInitiatorGateway = ::
IscsiInitiatorPrimDns = ::
 ... CUT ...




