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

from stdcli.trace_decorator import traceLog, getLog
from stdcli.plugin import Plugin
import lcctool
import lcctool.schemas

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")
moduleDebugLog = getLog(prefix="debug.")
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
        p.set_defaults(func=self.get_config)


        # apply settings from an INI file
        p = ctx.subparsers.add_parser("stage-config", help=_("Stage system settings using values from an INI file."))
        p.add_argument('--input-ini', '-O', action="store", dest="input_filename", default=default_filename, help=_("Change the name of the input INI file (Default: %(default)s)."))
        p.add_argument('--now',    action="store_const", const="now",    dest="flag", help=_("Commit changes after successful staging. THIS WILL REBOOT THE SERVER."))
        p.add_argument('--unit-test', action="store", dest="unit_test", default=None, help=_("Run in unit test mode."))
        p.set_defaults(func=self.stage_config)


        # reboot server to apply configs
        p = ctx.subparsers.add_parser("commit-config", help=_("Commit previously staged attributes. THIS WILL REBOOT THE SERVER."))
        p.add_argument('--subsystem', action="append", dest="subsystems", choices=lcctool.schemas.get_subsystems(), default=[], help=_("List of the different subsystems to dump settings. May be specified multiple times."))
        p.add_argument('--all-subsystems', action="store_const", dest="subsystems", const=lcctool.schemas.get_subsystems(), help=_("Dump settings for all subsystems."))
        p.add_argument('--unit-test', action="store", dest="unit_test", default=None, help=_("Run in unit test mode."))
        p.set_defaults(func=self.commit)


        # reset pending configurations
        p = ctx.subparsers.add_parser("reset-pending-config", help=_("reset all pending config options."))
        p.add_argument('--subsystem', action="append", dest="subsystems", choices=lcctool.schemas.get_subsystems(), default=[], help=_("List of the different subsystems to dump settings. May be specified multiple times."))
        p.add_argument('--all-subsystems', action="store_const", dest="subsystems", const=lcctool.schemas.get_subsystems(), help=_("Dump settings for all subsystems."))
        p.set_defaults(func=self.reset_pending)


        # change bios password
        pass




    @traceLog()
    def finishedCliParsing(self, ctx):
        if hasattr(ctx.args, "unit_test") and ctx.args.unit_test:
            lcctool.unit_test_mode = True
            lcctool.test_data_dir = ctx.args.unit_test

    @traceLog()
    def get_config(self, ctx):
        if not ctx.args.subsystems:
            moduleLog.warning("No subsystems specified! See the --subsystem option for details.")

        for host in ctx.raccfg.iterSpecfiedRacs():
            # set up new config object for each host
            ini = ConfigParser.ConfigParser()
            ini.optionxform = str # need to be case sensitive
            # save host name in INI
            ini.add_section("main")
            ini.set("main", "host", host["host"])
            ini.set("main", "alias", host.get("alias", ""))

            do_close = ctx.args.output_filename != "-"
            fn_subst = { "output_format": ctx.args.output_format, "host": host.get("alias", host["host"]) }
            outfile = sys.stdout
            if do_close:
                outfile = open(ctx.args.output_filename % fn_subst, "w+")

            def sync(full=True):
                # only sync when we are not using stdout (or, if using stdout, when we have full output to write)
                if full or do_close:
                    outfile.seek(0)
                    outfile.truncate()
                    if ctx.args.output_format == "ini":
                        ini.write( outfile )
                    elif ctx.args.output_format == "xml":
                        outfile.write( lcctool.schemas.etree.tostring(xml) )

            wsman = lcctool.wsman_factory(host, debug=ctx.args.debug)
            xml = lcctool.schemas.etree.Element("xml_return")
            for subsys in ctx.args.subsystems:
                for schema in lcctool.schemas.dell_schema_list[subsys]:
                    moduleLog.info("Getting config for schema %s" % schema)
                    for item in wsman.enumerate(schema):
                        moduleVerboseLog.info("  storing %s" % item["instanceid"])
                        item.serialize_ini(ini)
                        ini.set("main", item["fqdd"], lcctool.schemas.dell_schema_list[subsys])
                        xml.append(item.raw_xml_elem)
                        sync(full=False)


            sync(full=True)
            if do_close:
                outfile.close()

    @traceLog()
    def stage_config(self, ctx):
        for host in ctx.raccfg.iterSpecfiedRacs():
            ini = ConfigParser.ConfigParser()
            ini.optionxform = str # need to be case sensitive

            fn_subst = { "output_format": "ini", "host": host.get("alias", host["host"]) }
            ini.read(ctx.args.input_filename % fn_subst)

            wsman = lcctool.wsman_factory(host, debug=ctx.args.debug)

            pending = {}
            for fqdd in ini.sections():
                if not ini.has_option("main", fqdd):
                    continue
                pending[fqdd] = {}
                schema_list = eval(ini.get("main", fqdd))
                moduleVerboseLog.info("schema list: %s" % repr(schema_list))
                for schema in schema_list:
                    moduleVerboseLog.info("Getting current options for schema: %s" % schema)
                    for item in wsman.enumerate(schema):
                        moduleVerboseLog.info("  getting %s" % item["instanceid"])
                        if item.deserialize_ini(ini):
                            pending[fqdd][item['instanceid']] = item

            last_attribute = None
            need_reboot = False
            jobs = []
            for fqdd in pending.keys():
                if not pending[fqdd].values():
                    continue

                moduleVerboseLog.info("save all pending for fqdd %s" % fqdd)
                items = pending[fqdd].values()
                meth_details = items[0].get_service_uri()
                names = [ ("AttributeName", i.get_name()) for i in pending[fqdd].values() ]
                values = [ ("AttributeValue", i["pendingvalue"]) for i in pending[fqdd].values() ]
                margs = names + values
                res = items[0].call_method(meth_details['uri'], meth_details['ns'], meth_details['multi_set_method'], ("Target", fqdd), *margs)
                moduleVerboseLog.info("  RES: %s" % repr(res))

                if "yes" in [ i.lower() for i in res.get("rebootrequired", [])]:
                    moduleVerboseLog.info("       Reboot required to enable setting.")
                    need_reboot = True

#                for job in res.get('job_children', []):
#                    job_num = "could not get job #"
#                    for selector in job[1].iter("{%(wsman)s}Selector" % lcctool.schemas.std_xml_namespaces):
#                        if selector.get("Name", None) == "InstanceID":
#                            job_num = selector.text
#                            jobs.append(job_num)
#
#                    moduleVerboseLog.info("    JOB %s created for %s" % (job_num, item["instanceid"]))
#                    jobs.append(res["job_children"])
#                moduleVerboseLog.info("    attribute set. ReturnValue: %s" % res.get("returnvalue", []))
#                moduleVerboseLog.info("    attribute set. Message was: %s" % res.get("message", []))
#                moduleVerboseLog.info("    attribute set. SetResult was: %s" % res.get("setresult", []))
#                moduleVerboseLog.info("    attribute set. res: %s" % repr(res))
#
#            # use last attribute to commit the whole fqdd
#            if ctx.args.flag in ("set", "now") and last_attribute:
#                moduleVerboseLog.info("commit pending for attribute %s" % last_attribute["attributename"])
#                last_attribute.commit_pending()

    @traceLog()
    def commit(self, ctx, *args, **kargs):
        if not ctx.args.subsystems:
            moduleLog.warning("No subsystems specified! See the --subsystem option for details.")

        for host in ctx.raccfg.iterSpecfiedRacs():
            wsman = lcctool.wsman_factory(host, debug=ctx.args.debug)
            for subsys in ctx.args.subsystems:
                run_method_for_each_fqdd(wsman, "CreateTargetedConfigJob", subsys
                                              ScheduledStartTime="TIME_NOW",
                                              UntilTime="20121111111111",   # no idea what that number is....
                                              RebootJobType=reboot_type,
                                                )

    @traceLog()
    def reset_pending(self, ctx, *args, **kargs):
        if not ctx.args.subsystems:
            moduleLog.warning("No subsystems specified! See the --subsystem option for details.")

        for host in ctx.raccfg.iterSpecfiedRacs():
            wsman = lcctool.wsman_factory(host, debug=ctx.args.debug)
            for subsys in ctx.args.subsystems:
                run_method_for_each_fqdd(wsman, "DeletePendingConfiguration", subsys)


@traceLog()
def run_method_for_each_fqdd(wsman, method, subsys, *args, **kargs):
    service_ns = lcctool.schemas.std_xml_namespaces["%s_srv"%subsys]
    service_uri = lcctool.get_service_uri(wsman, service_ns)
    service = lcctool.wscim.find_class(service_ns)(wsman=wsman)
    # need to iterate over all the fqdds and run delete with each as target
    fqdd_list = {}
    for schema in lcctool.schemas.dell_schema_list[subsys]:
        for item in wsman.enumerate(schema):
            fqdd_list[item["fqdd"]] = None

    for fqdd in fqdd_list.keys():
        moduleLog.info("resetting pending configuration for %s" % fqdd)
        res = service.call_method(service_uri, service_ns, method, Target=fqdd, *args, **kargs)
        moduleLog.info("result: %s" % repr(res))
