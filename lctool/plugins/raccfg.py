# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0
# Copyright (c) 2011, Dell Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Dell, Inc. nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Dell, Inc. BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pkg_resources
import ConfigParser
import fnmatch

import lctool
from stdcli.trace_decorator import traceLog, getLog
from stdcli.plugin import Plugin

moduleVerboseLog = getLog(prefix="verbose.")
moduleVerboseLog.debug("initializing plugin module: %s" % __name__)

_ = lctool._

class SampleTestRacCfg(Plugin):
    @traceLog()
    def __init__(self, ctx):
        moduleVerboseLog.debug("initializing plugin: %s" % self.__class__.__name__)
        # subparser for dumping config (note this is what plugins should do)
        dump_p = ctx.subparsers.add_parser("testrac", help="test cmd")
        dump_p.set_defaults(func=self.testit)

    @traceLog()
    def testit(self, ctx):
        print ", ".join((repr(i) for i in ctx.raccfg.iterSpecfiedRacs()))


class RacCfg(Plugin):
    @traceLog()
    def __init__(self, ctx):
        moduleVerboseLog.debug("initializing plugin: %s" % self.__class__.__name__)
        ctx.raccfg = self
        self.ctx = ctx
        configfile = pkg_resources.resource_filename("lctool","rachosts.ini")

        # --rac-host=HOST  --rac-user=USER  --rac-pass=PASS
        # --rac-alias=HOSTALIAS1,HOSTALIAS2,HOSTALIAS3,...
        group = ctx.parser.add_argument_group("Options to specify RAC")
        group.add_argument("--rac-hosts-cfg", dest="rachosts_cfg", action="store", default=configfile, metavar="FILENAME", help=_("Config file with RAC host aliases."))
        group.add_argument("--rac-host",     action="store", dest="rac_host", help=_("The hostname or IP of the RAC to operate on"))
        group.add_argument("--rac-user",     action="store", dest="rac_user", help=_("The username to authenticate against --rac-host"))
        group.add_argument("--rac-password", action="store", dest="rac_password", help=_("The password to authenticate against --rac-host"))
        # not yet implemented
        # --rac-uri=rac://USER:PASS@HOST/  --rac-uri=rac://USER2:PASS2@HOST2/ ...
        #group.add_argument("--rac-uri",      action="store", dest="rac_uri",   help=_(""))
        group.add_argument("--rac-alias",    action="append", dest="rac_alias", help=_("The alias or group of the RAC hosts to operate on. Groups are specified with @groupname."))

        # add-rac-alias ALIAS HOST USER PASS
        add_alias_p = ctx.subparsers.add_parser("add-alias", help=_("Add a RAC alias"))
        add_alias_p.add_argument("alias", action="store", help=_("Name of alias to add."))
        add_alias_p.add_argument("host", action="store", help=_("Hostname or IP of RAC."))
        add_alias_p.add_argument("user", action="store", help=_("Username to access RAC."))
        add_alias_p.add_argument("password", action="store", help=_("Password to access RAC."))
        add_alias_p.set_defaults(func=self.addAlias)

        # rm-rac-alias ALIAS
        rm_alias_p = ctx.subparsers.add_parser("rm-alias", help=_("Remove a RAC alias"))
        rm_alias_p.add_argument("alias", nargs='*', action="store", help=_("Name of alias or hostname to remove."))
        rm_alias_p.set_defaults(func=self.rmAlias)

        # ls-rac-alias
        ls_alias_p = ctx.subparsers.add_parser("ls-alias", help=_("List stored RAC aliases"))
        ls_alias_p.add_argument("glob", nargs='*', default='*', action="store", help=_("pattern to limit returned results."))
        ls_alias_p.set_defaults(func=self.lsAlias)

        # group-create GROUPNAME [alias...]
        group_create_p = ctx.subparsers.add_parser("group-create", help=_("Create a group to allow operation on more than one RAC"))
        group_create_p.add_argument("groupname", action="store", help=_("Name of group to create"))
        group_create_p.add_argument("alias", nargs='*', default=[], action="store", help=_("List of aliases to add to the group"))
        group_create_p.set_defaults(func=self.groupCreate)

        group_destroy_p = ctx.subparsers.add_parser("group-destroy", help=_("Remove a group name"))
        group_destroy_p.add_argument("groupname", nargs="+", action="store", help=_("name of group to remove"))
        group_destroy_p.set_defaults(func=self.groupDestroy)

        group_add_alias_p = ctx.subparsers.add_parser("group-add-alias", help=_("Add an alias to a group"))
        group_add_alias_p.add_argument("groupname", action="store", help=_("Name of group to modify"))
        group_add_alias_p.add_argument("alias", nargs='+', default=[], action="store", help=_("Aliases to add"))
        group_add_alias_p.set_defaults(func=self.groupAddAlias)

        group_rm_alias_p = ctx.subparsers.add_parser("group-rm-alias", help=_("Remove an alias from a group"))
        group_rm_alias_p.add_argument("groupname", action="store", help=_("Name of group to modify"))
        group_rm_alias_p.add_argument("alias", nargs='+', default=[], action="store", help=_("Aliases to remove"))
        group_rm_alias_p.set_defaults(func=self.groupRmAlias)

        # set-default-rac HOST|ALIAS
        ls_alias_p = ctx.subparsers.add_parser("set-default-rac", help=_("Set the default RAC host alias when none is specified"))
        ls_alias_p.add_argument("alias", action="store", help=_("RAC alias to use as the default."))
        ls_alias_p.set_defaults(func=self.setDefault)

    @traceLog()
    def finishedCliParsing(self, ctx):
        self.readConfig()

    @traceLog()
    def flatten(self, aliasList, recursionDepth=1):
        if recursionDepth > self.maxGroupLookupRecursionDepth:
            return []
        expanded = {}
        # some aliases may be comma separated list, expand
        for i in aliasList:
            for a in i.split(","):
                if a.startswith("@"):
                    for b in self.flatten(self.getGroupAliases(a[1:]), recursionDepth=recursionDepth + 1):
                        expanded[b] = None
                else:
                    expanded[a] = None

        return expanded.keys()

    @traceLog()
    def iterSpecfiedRacs(self):
        if self.ctx.args.rac_alias is not None:
            for a in self.flatten(self.ctx.args.rac_alias):
                yield self.getRacAliasDetails(a)

        elif self.ctx.args.rac_host is not None:
            host = self.ctx.args.rac_host
            user = self.ctx.args.rac_user
            password = self.ctx.args.rac_password
            yield {"host":host, "user":user, "password":password}

        # uri parsing not yet implemented
        #elif self.ctx.args.rac_uri is not None:
        #    for uri in self.ctx.args.rac_uri:
        #        pass

        elif self.defaultAlias:
            for a in self.flatten( [self.defaultAlias,] ):
                yield self.getRacAliasDetails(a)


    @traceLog()
    def getRacAliasDetails(self, alias):
        section = 'alias:%s' % alias
        self.racconf.get(section, 'alias')
        host = self.racconf.get(section, 'host')
        user = self.racconf.get(section, 'user')
        password = self.racconf.get(section, 'password')
        return {"alias": alias, "host":host, "user":user, "password":password}

    @traceLog()
    def readConfig(self):
        self.racconf = ConfigParser.SafeConfigParser()
        self.racconf.read(self.ctx.args.rachosts_cfg)

        required_options = {"general": [("default-alias", ""), ('max-group-lookup-recursion-depth', 8)], "groups": []}
        for section, name_values in required_options.items():
            if not self.racconf.has_section(section):
                self.racconf.add_section(section)
            for name, value in name_values:
                if not self.racconf.has_option(section, name):
                    self.racconf.set(section, name, str(value))

        self.maxGroupLookupRecursionDepth = self.racconf.getint('general', 'max-group-lookup-recursion-depth')
        self.defaultAlias = self.racconf.get('general', 'default-alias').strip()

    @traceLog()
    def writeConfig(self):
        self.racconf.set('general', 'max-group-lookup-recursion-depth', str(self.maxGroupLookupRecursionDepth))
        self.racconf.set('general', 'default-alias', self.defaultAlias)

        fp = open(self.ctx.args.rachosts_cfg, "w")
        self.racconf.write(fp)
        fp.close()

    @traceLog()
    def addAlias(self, ctx):
        section = 'alias:%s' % ctx.args.alias
        if self.racconf.has_section(section):
            self.racconf.remove_section(section)

        self.racconf.add_section(section)
        self.racconf.set(section, 'alias', ctx.args.alias)
        self.racconf.set(section, 'host', ctx.args.host)
        self.racconf.set(section, 'user', ctx.args.user)
        self.racconf.set(section, 'password', ctx.args.password)

        self.writeConfig()

    @traceLog()
    def rmAlias(self, ctx):
        for alias in ctx.args.alias:
            section = 'alias:%s' % alias
            if self.racconf.has_section(section):
                self.racconf.remove_section(section)
        self.writeConfig()

    @traceLog()
    def lsAlias(self, ctx):
        for section in self.racconf.sections():
            if section.startswith("alias:"):
                for pat in ctx.args.glob:
                    if fnmatch.fnmatch(section[6:], pat):
                        print section[6:]
                        break
        if self.racconf.has_section("groups"):
            for group in self.racconf.options("groups"):
                print "@%s: %s" % (group, " ".join(self.getGroupAliases(group)))

    @traceLog()
    def getGroupAliases(self, group):
        if self.racconf.has_section("groups"):
            if self.racconf.has_option("groups", group):
                groups = self.racconf.get("groups", group)
                return [ s.strip() for s in groups.split(",") if s ]
        return []

    @traceLog()
    def groupCreate(self, ctx):
        if not self.racconf.has_section("groups"):
            self.racconf.add_section("groups")

        self.racconf.set("groups", ctx.args.groupname, ",".join(ctx.args.alias))
        self.writeConfig()

    @traceLog()
    def groupDestroy(self, ctx):
        for group in ctx.args.groupname:
            if self.racconf.has_section("groups"):
                self.racconf.remove_option("groups", group)
        self.writeConfig()

    @traceLog()
    def groupAddAlias(self, ctx):
        set = {}
        map(set.__setitem__, self.getGroupAliases(ctx.args.groupname), [])
        map(set.__setitem__, ctx.args.alias, [])
        self.racconf.set("groups", ctx.args.groupname, ",".join(set.keys()))
        self.writeConfig()


    @traceLog()
    def groupRmAlias(self, ctx):
        self.racconf.set("groups", ctx.args.groupname, ",".join( [a for a in self.getGroupAliases(ctx.args.groupname) if a not in ctx.args.alias] ))
        self.writeConfig()

    @traceLog()
    def setDefault(self, ctx):
        self.defaultAlias = ctx.args.alias
        self.writeConfig()
