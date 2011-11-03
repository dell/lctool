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
import lcctool.wscim_dell_classes

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")
moduleDebugLog = getLog(prefix="debug.")
moduleVerboseLog.debug("loading plugin module: %s" % __name__)

_ = lcctool._

default_filename = "config-%(host)s.%(output_format)s"

# So we can version the config file output and reject file formats we dont know
# rule is that major version *must* match, minor version shouldn't matter (or,
# in general, we should write code to ensure that minor version changes always
# are forwards and backwards compatible)
CONFIG_FILE_VERSION_MAJOR = "1"
CONFIG_FILE_VERSION_MINOR = "0"

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
        p.set_defaults(func=self.get_config)


        # apply settings from an INI file
        p = ctx.subparsers.add_parser("stage-config", help=_("Stage system settings using values from an INI file."))
        p.add_argument('--input-ini', '-O', action="store", dest="input_filename", default=default_filename, help=_("Change the name of the input INI file (Default: %(default)s)."))
        p.add_argument('--now',    action="append_const", const="now",    dest="flags", default=[], help=_("Commit changes after successful staging. THIS WILL REBOOT THE SERVER."))
        p.set_defaults(func=self.stage_config)


        # reboot server to apply configs
        p = ctx.subparsers.add_parser("commit-config", help=_("Commit previously staged attributes. THIS WILL REBOOT THE SERVER."))
        p.add_argument('--subsystem', action="append", dest="subsystems", choices=lcctool.schemas.get_subsystems(), default=[], help=_("List of the different subsystems to dump settings. May be specified multiple times."))
        p.add_argument('--all-subsystems', action="store_const", dest="subsystems", const=lcctool.schemas.get_subsystems(), help=_("Dump settings for all subsystems."))
        p.set_defaults(func=self.commit)


        # reset pending configurations
        p = ctx.subparsers.add_parser("reset-pending-config", help=_("reset all pending config options."))
        p.add_argument('--subsystem', action="append", dest="subsystems", choices=lcctool.schemas.get_subsystems(), default=[], help=_("List of the different subsystems to dump settings. May be specified multiple times."))
        p.add_argument('--all-subsystems', action="store_const", dest="subsystems", const=lcctool.schemas.get_subsystems(), help=_("Dump settings for all subsystems."))
        p.set_defaults(func=self.reset_pending)


        # monitor jobs
        p = ctx.subparsers.add_parser("job-status", help=_("display job status."))
        p.add_argument('--uri',    action="append", dest="uri",    default=[], help=_("URI."))
        p.add_argument('--job-id', action="append", dest="job_id", default=[], help=_("job id."))
        p.set_defaults(func=self.job_status)

        # change bios password
        pass

        # suggested additional cli methods:
        #  -- method to get one config item. Couple ideas for how this cli looks:
        #       lcctool get-config-item SUBSYS/INSTANCE_ID
        #       lcctool get-config-item --subsys SUBSYS  INSTANCE_ID
        #       lcctool get-config-item --subsys SUBSYS --fqdd FQDD --attribute ATTRIBUTE_NAME
        #     * lcctool get-config-item --subsys SUBSYS --fqdd FQDD ATTRIBUTE_NAME [ATTRIBUTE_NAME ...]
        #  -- method to set one config item. Couple ideas for how this cli looks:
        #       lcctool set-config-item SUBSYS/INSTANCE_ID=NEWVAL
        #       lcctool set-config-item --subsys SUBSYS  INSTANCE_ID=NEWVAL
        #       lcctool set-config-item --subsys SUBSYS --fqdd FQDD --attribute ATTRIBUTE_NAME --value NEWVALUE
        #     * lcctool get-config-item --subsys SUBSYS --fqdd FQDD ATTRIBUTE_NAME=NEWVALUE [ATTRIBUTE_NAME=NEWVALUE ...]
        #
        # the idea marked with (*) are the ones MB thinks are preferrable


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
            ini, xml, fn = get_host_config(host, ctx.args.subsystems, ctx.args.output_filename, ctx.args.output_format, ctx.args.debug)
            moduleLog.info("Configuration for %(host)s saved to file %(fn)s." % {'host': host.get('alias', host['host']), 'fn': fn})

    @traceLog()
    def stage_config(self, ctx):
        for host in ctx.raccfg.iterSpecfiedRacs():
            wsman = lcctool.wsman_factory(host, debug=ctx.args.debug)
            pending = get_changed_items(wsman, host, input_filename, input_fh, debug)
            ret = stage_config(wsman, pending)
            if 'now' in ctx.args.flags:
                for service_ns in ret['service_ns_to_fqdd_map'].keys():
                    fqdd_list = dict([ (i, None) for i in ret['service_ns_to_fqdd_map'][service_ns]])
                    for res in run_method_for_each_fqdd(wsman=wsman, method="CreateTargetedConfigJob",
                                             service_ns=service_ns, fqdd_list=fqdd_list, msg="Committing config for %(fqdd)s",
                                             ScheduledStartTime="TIME_NOW",
                                             UntilTime="20121111111111",   # no idea what that number is....
                                             RebootJobType=1):
                        for job_details in lcctool.plugins.config_cli.iter_job_details(res):
                            ret['jobs'].append(job_details)

        print monitor_jobs(wsman, ret['jobs'])


    @traceLog()
    def commit(self, ctx):
        if not ctx.args.subsystems:
            moduleLog.warning("No subsystems specified! See the --subsystem option for details.")

        jobs = []
        for host in ctx.raccfg.iterSpecfiedRacs():
            wsman = lcctool.wsman_factory(host, debug=ctx.args.debug)
            for subsys in ctx.args.subsystems:
                for res in run_method_for_each_fqdd(wsman=wsman, method="CreateTargetedConfigJob",
                                         subsys=subsys, msg="Committing config for %(fqdd)s",
                                         ScheduledStartTime="TIME_NOW",
                                         # fmt:     YYYYMMDDhhmmss
                                         UntilTime="20121111111111",
                                         RebootJobType=1):
                    for job_details in lcctool.plugins.config_cli.iter_job_details(res):
                        jobs.append(job_details)
        print monitor_jobs(wsman, jobs)

    @traceLog()
    def reset_pending(self, ctx):
        if not ctx.args.subsystems:
            moduleLog.warning("No subsystems specified! See the --subsystem option for details.")

        for host in ctx.raccfg.iterSpecfiedRacs():
            wsman = lcctool.wsman_factory(host, debug=ctx.args.debug)
            for subsys in ctx.args.subsystems:
                for res in run_method_for_each_fqdd(wsman=wsman, method="DeletePendingConfiguration", subsys=subsys, msg="resetting pending configuration for %(fqdd)s"):
                    pass # noop, probably should think about parsing the return code


    @traceLog()
    def job_status(self, ctx):
        for host in ctx.raccfg.iterSpecfiedRacs():
            wsman = lcctool.wsman_factory(host, debug=ctx.args.debug)
            while ctx.args.uri and ctx.args.job_id:
                uri = ctx.args.uri.pop()
                jid = ctx.args.job_id.pop()
                for msg in get_job_status_string(wsman, uri, jid):
                    print msg

@traceLog()
def get_job_status_string(wsman, uri, jid):
    for j in wsman.get_instance_id(uri, jid):
        yield "Job %(id)s  Status (%(status)s)  percent done (%(percent)s)  message (%(message)s)" % {
            'id': j["InstanceID"],
            'status': j["JobStatus"],
            'percent': j["PercentComplete"],
            'message': j["Message"]}

@traceLog()
def monitor_jobs(wsman, jobs):
    s = ""
    if jobs:
        s = s + "Jobs have been created for configuration. To monitor progress of these jobs, run:\n"
        s = s + "\tlcctool job-status "
        s = s + " ".join([ "--uri %s --job-id %s" % (j['uri'], j['InstanceID']) for j in jobs ])
    return s

@traceLog()
def run_method_for_each_fqdd(wsman, method, fqdd_list=None, subsys=None, service_ns=None, msg=None, *args, **kargs):
    if service_ns is None:
        service_ns = lcctool.schemas.std_xml_namespaces["%s_srv"%subsys]
    schema_list = []
    if subsys is not None:
        schema_list = lcctool.schemas.dell_schema_list[subsys]
    if fqdd_list is None:
        fqdd_list = {}

    service_uri = lcctool.get_service_uri(wsman, service_ns)
    service = lcctool.wscim.find_class(service_ns)(wsman=wsman)
    # need to iterate over all the fqdds and run delete with each as target
    for schema in schema_list:
        for item in wsman.enumerate(schema):
            fqdd_list[item["fqdd"]] = None

    for fqdd in fqdd_list.keys():
        if msg:
            moduleLog.info(msg % {'fqdd':fqdd})
        res = service.call_method(service_uri, service_ns, method, Target=fqdd, *args, **kargs)
        moduleLog.info("result: %s" % repr(res))
        yield res

@traceLog()
def get_changed_items(wsman, host, input_filename=None, input_fh=None, debug=False):
    ini = ConfigParser.ConfigParser()
    ini.optionxform = str # need to be case sensitive

    fn_subst = { "output_format": "ini", "host": host.get("alias", host["host"]) }
    if input_filename:
        ini.read(input_filename % fn_subst)
    if input_fh:
        ini.readfp(input_fh)

    try:
        major = ini.get("main", "config_file_version_major")
    except Exception:
        raise Exception("Could not process this config file because it doesnt have proper versioning information. This tool can only process version %s config files." % CONFIG_FILE_VERSION_MAJOR)

    if major != CONFIG_FILE_VERSION_MAJOR:
        raise Exception(_("Config file version mismatch. Could not process this version config file. Config file had %(configmajor)s, but this tool can only process version %s") % (major, CONFIG_FILE_VERSION_MAJOR))

    changed = {}
    for fqdd in ini.sections():
        if not ini.has_option("main", fqdd):
            continue
        schema_list = eval(ini.get("main", fqdd))
        moduleVerboseLog.info("schema list: %s" % repr(schema_list))
        for schema in schema_list:
            moduleVerboseLog.info("Getting current options for schema: %s" % schema)
            for item in wsman.enumerate(schema):
                moduleVerboseLog.info("  getting %s" % item["instanceid"])
                if item.deserialize_ini(ini):
                    d = changed.get(fqdd, {})
                    d[item['instanceid']] = item
                    changed[fqdd] = d
    return changed


@traceLog()
def stage_config(wsman, pending):
    jobs = []
    need_reboot = False
    service_ns_to_fqdd_map = {}
    for fqdd in pending.keys():
        moduleVerboseLog.info("save all pending for fqdd %s" % fqdd)
        items = pending[fqdd].values()
        meth_details = items[0].get_service_uri()
        names = [ ("AttributeName", i.get_name()) for i in pending[fqdd].values() ]
        values = [ ("AttributeValue", i["pendingvalue"]) for i in pending[fqdd].values() ]
        margs = names + values
        res = lcctool.call_method(wsman, meth_details['uri'], meth_details['ns'], meth_details['multi_set_method'], ("Target", fqdd), *margs)
        moduleVerboseLog.info("  RES: %s" % repr(res))
        if res.get('job_children', None):
            jobs.append(res.get('job_children'))

        if "yes" in [ i.lower() for i in res.get("rebootrequired", [])]:
            moduleVerboseLog.info("       Reboot required to enable setting.")
            need_reboot = True

        for  job_det in iter_job_details(res):
            jobs.append( job_det )

        arr = service_ns_to_fqdd_map.get(meth_details['ns'], [])
        arr.append(fqdd)
        service_ns_to_fqdd_map[meth_details['ns']] = arr

    return {'service_ns_to_fqdd_map': service_ns_to_fqdd_map, 'jobs': jobs, 'need_reboot': need_reboot}

@traceLog()
def get_host_config(host, subsystems, output_filename, output_format, debug):
    # set up new config object for each host
    ini = ConfigParser.ConfigParser()
    ini.optionxform = str # need to be case sensitive
    # save host name in INI
    ini.add_section("main")
    ini.set("main", "host", host["host"])
    ini.set("main", "alias", host.get("alias", ""))
    ini.set("main", "config_file_version_major", CONFIG_FILE_VERSION_MAJOR)
    ini.set("main", "config_file_version_minor", CONFIG_FILE_VERSION_MINOR)

    do_close = output_filename != "-"
    fn_subst = { "output_format": output_format, "host": host.get("alias", host["host"]) }
    outfile = None
    if output_filename == "-":
        outfile = sys.stdout
    elif output_filename:
        outfile = open(output_filename % fn_subst, "w+")
    xml = lcctool.schemas.etree.Element("xml_return")

    def sync(full=True):
        # only sync when we are not using stdout (or, if using stdout, when we have full output to write)
        if outfile and (full or do_close):
            outfile.seek(0)
            outfile.truncate()
            if output_format == "ini":
                ini.write( outfile )
            elif output_format == "xml":
                outfile.write( lcctool.schemas.etree.tostring(xml) )

    get_host_subsystems_config(host, subsystems, ini, xml, debug, sync)

    if do_close and outfile:
        outfile.close()

    return (ini, xml, output_filename % fn_subst)


@traceLog()
def get_host_subsystems_config(host, subsystems, ini, xml, debug, sync):
    wsman = lcctool.wsman_factory(host, debug=debug)
    for subsys in subsystems:
        for schema in lcctool.schemas.dell_schema_list[subsys]:
            moduleLog.info("Getting config for schema %s" % schema)
            for item in wsman.enumerate(schema):
                moduleVerboseLog.info("  storing %s" % item["instanceid"])
                item.serialize_ini(ini)
                ini.set("main", item["fqdd"], lcctool.schemas.dell_schema_list[subsys])
                xml.append(item.raw_xml_elem)
                sync(full=False)
    sync(full=True)

#            <n1:Job>
#                <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
#                <wsa:ReferenceParameters>
#                   <wsman:ResourceURI>http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_LifecycleJob</wsman:ResourceURI>
#                   <wsman:SelectorSet>
#                       <wsman:Selector Name="InstanceID">JID_001320083637</wsman:Selector>
#                       <wsman:Selector Name="__cimnamespace">root/dcim</wsman:Selector>
#                   </wsman:SelectorSet>
#                </wsa:ReferenceParameters>
#            </n1:Job>
@traceLog()
def iter_job_details(res):
    for job in res.get('job_children', []):
        job_uri = None
        job_num = None
        job_cimns =  None
        for uri in job[1].iter("{%(wsman)s}ResourceURI" % lcctool.schemas.std_xml_namespaces):
            job_uri = uri.text
        for selector in job[1].iter("{%(wsman)s}Selector" % lcctool.schemas.std_xml_namespaces):
           if selector.get("Name", None) == "InstanceID":
                job_num = selector.text
           if selector.get("Name", None) == "__cimnamespace":
                job_cimns = selector.text
        if None in (job_uri, job_num, job_cimns):
            raise Exception("could not parse required job information from return value")

        yield {"uri": job_uri, "InstanceID": job_num, "CIMNS": job_cimns}
