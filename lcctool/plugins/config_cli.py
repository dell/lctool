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

import os
import sys
import ConfigParser
import pkg_resources

try:
    import argparse
except (ImportError,), e:
    import stdcli.argparse as argparse

import lcctool
from stdcli.trace_decorator import traceLog, getLog
from stdcli.plugin import Plugin

import lcctool.config
import lcctool.schemas

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")
moduleVerboseLog.debug("loading plugin module: %s" % __name__)

_ = lcctool._

default_filename = "config-%(host)s.%(output_format)s"

class Config(Plugin):
    @traceLog()
    def __init__(self, ctx):
        moduleVerboseLog.debug("initializing plugin: %s" % self.__class__.__name__)

        # enumerate into an INI file or stdout
        p = ctx.subparsers.add_parser("get-config", help=_("Query target system settings and save in an INI-style file."))
        p.add_argument('--output-format', action="store", dest="output_format", default="ini", choices=["ini","xml"], help=_("Specify output format. Default is '%(default)s'"))
        p.add_argument('--output', '-O', action="store", dest="output_filename", default=default_filename, help=_("Change the name of the default filename for saving settings. Use '-' to display on stdout. (Default: %(default)s)"))
        p.add_argument('--subsystem', action="append", dest="subsystems", choices=lcctool.schemas.get_subsystems(), default=[], help=_("List of the different subsystems to dump settings. May be specified multiple times."))
        p.add_argument('--all-subsystems', action="store_const", dest="subsystems", const=lcctool.schemas.get_subsystems(), help=_("Dump settings for all subsystems."))
        p.add_argument('--unit-test', action="store", dest="unit_test", default=None, help=_("Run in unit test mode."))
        p.set_defaults(func=self.getConfig)

        # apply settings from an INI file
        p = ctx.subparsers.add_parser("stage-config", help=_("Stage system settings using values from an INI file."))
        p.add_argument('--input-ini', '-O', action="store", dest="input_filename", default=default_filename, help=_("Change the name of the input INI file (Default: %(default)s)."))
        p.add_argument('--now',    action="store_const", const="now",    dest="flag", help=_("Commit changes after successful staging. THIS WILL REBOOT THE SERVER."))
        p.add_argument('--unit-test', action="store", dest="unit_test", default=None, help=_("Run in unit test mode."))
        p.set_defaults(func=self.stageConfig)

        p = ctx.subparsers.add_parser("commit-config", help=_("Commit previously staged attributes. THIS WILL REBOOT THE SERVER."))
        p.add_argument('--subsystem', action="append", dest="subsystems", choices=lcctool.schemas.get_subsystems(), default=[], help=_("List of the different subsystems to dump settings. May be specified multiple times."))
        p.add_argument('--all-subsystems', action="store_const", dest="subsystems", const=lcctool.schemas.get_subsystems(), help=_("Dump settings for all subsystems."))
        p.add_argument('--unit-test', action="store", dest="unit_test", default=None, help=_("Run in unit test mode."))
        p.set_defaults(func=self.commit)

        # apply settings from an INI file
        p = ctx.subparsers.add_parser("set", help=_("Stage system settings using CLI options."))
        p.add_argument('--now',    action="store_const", const="now",    dest="flag", help=_("Commit changes after successful staging. THIS WILL REBOOT THE SERVER."))
        p.add_argument('--unit-test', action="store", dest="unit_test", default=None, help=_("Run in unit test mode."))
        p.set_defaults(func=self.stageConfig)


    @traceLog()
    def finishedCliParsing(self, ctx):
        if hasattr(ctx.args, "unit_test") and ctx.args.unit_test:
            lcctool.unit_test_mode = True
            lcctool.test_data_dir = ctx.args.unit_test

    @traceLog()
    def getConfig(self, ctx):
        if not ctx.args.subsystems:
            moduleLog.warning("No subsystems specified! See the --subsystem option for details.")

        for host in ctx.raccfg.iterSpecfiedRacs():
            ini = ConfigParser.ConfigParser()
            ini.optionxform = str # need to be case sensitive
            # save host name in INI
            ini.add_section("main")
            ini.set("main", "host", host["host"])
            ini.set("main", "alias", host.get("alias", ""))

            xml = lcctool.schemas.etree.Element("xml_return")
            wsman = lcctool.wsman_factory(host)
            for subsys in ctx.args.subsystems:
                for schema in lcctool.schemas.dell_schema_list[subsys]:
                    for item in wsman.enumerate(schema):
                        print "ITEM: %s" % item
                        print "     properties: %s" % item.properties
                        item.serialize_ini(ini)
                        xml.append(item.raw_xml)

            fn_subst = { "output_format": ctx.args.output_format, "host": host.get("alias", host["host"]) }

            do_close = ctx.args.output_filename != "-"
            outfile = sys.stdout
            if do_close:
                outfile = open(ctx.args.output_filename % fn_subst, "w+")

            if ctx.args.output_format == "ini":
                ini.write( outfile )
            elif ctx.args.output_format == "xml":
                outfile.write( lcctool.schemas.etree.tostring(xml) )

            if do_close:
                outfile.close()

    @traceLog()
    def stageConfig(self, ctx):
        for host in ctx.raccfg.iterSpecfiedRacs():
            fn_subst = { "output_format": "ini", "host": host.get("alias", host["host"]) }
            infile = open(ctx.args.input_filename % fn_subst, "r")
            ini = ConfigParser.ConfigParser()
            ini.optionxform = str # need to be case sensitive
            ini.readfp(infile)
            infile.close()

            for job_ids, ret_xml in lcctool.config.settings_from_ini(host, ini):
                if len(job_ids) > 1:
                    moduleLog.info("Some settings were queued for immediate commit in config job IDs: %s" % job_ids)
                if len(job_ids) == 1:
                    moduleLog.info("Some settings were queued for immediate commit in config job ID: %s" % job_ids[0])

                #for reboot_elem in  ret_xml.iter("{%(wsman)s}RebootRequired" % schemas.std_xml_namespaces):
                #reboot_required = 

        if ctx.args.flag in ("set", "now"):
            self.commit(ctx)

    @traceLog()
    def commit(self, ctx, subsys=None):
        for host in ctx.raccfg.iterSpecfiedRacs():
            for enum in ctx.args.subsystems:
                lcctool.config.commit_settings(host, enum)
