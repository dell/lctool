#! /usr/bin/env python
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

#alphabetical
import os
import sys
import glob
import logging
try:
    import argparse
except ImportError:
    import lcctool.argparse

# all of the variables below are substituted by the build system
__VERSION__="1.0.0"

import TestLib

exeName = os.path.realpath(sys.argv[0])
top_srcdir = os.path.join(os.path.dirname(exeName), "..")
top_builddir = os.getcwd()

sys.path.insert(0,top_srcdir)
sys.path.insert(0,"%s/lcctool/" % top_srcdir)

def setupLogging(log_file=None, config_file=None, verbosity=1, trace=0, debug=0):
    # set up logging
    try:
        logging.config.fileConfig(config_file)
    except:
        # manually set up basic logging if not present in cfg file
        root_log = logging.getLogger()
        root_log.setLevel(logging.NOTSET)
        hdlr = logging.StreamHandler(sys.stderr)
        hdlr.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        hdlr.setFormatter(formatter)
        root_log.addHandler(hdlr)

    root_log        = logging.getLogger()
    module_log         = logging.getLogger("test")
    module_debug_log   = logging.getLogger("debug")
    module_verbose_log = logging.getLogger("verbose")
    module_trace_log   = logging.getLogger("trace")

    # if logfile is specified, it will get everything
    root_log_hdlr = None
    if log_file:
        root_log_hdlr = logging.FileHandler(log_file)
        root_log.addHandler(root_log_hdlr)

    module_log.propagate = 0
    module_trace_log.propagate = 0
    module_verbose_log.propagate = 0
    module_debug_log.propagate = 0

    # debug stuff doesnt go to default root log, unless requested
    if debug >= 1:
        module_debug_log.propagate = 1

    # debug stuff doesnt go to default root log, unless requested
    if trace:
        module_trace_log.propagate = 1

    # verbose stuff always goes to logfile if configured
    if verbosity >= 1:
        module_log.propagate = 1
    elif root_log_hdlr:
        module_log.addHandler(root_log_hdlr)

    if verbosity >= 2:
        module_verbose_log.propagate = 1
    elif root_log_hdlr:
        module_verbose_log.addHandler(root_log_hdlr)

    if verbosity >= 3:
        for hdlr in root_log.handlers:
            hdlr.setLevel(logging.DEBUG)

def _(s): return s

# runs all modules TestCase() classes in files that match test*.py
if __name__ == "__main__":

    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('--version', action='version', version='%(prog)s ' + __VERSION__)
    p.add_argument("-v", "--verbose", action="count", dest="verbosity", help=_("Display more verbose output."))
    p.add_argument("-q", "--quiet", action="store_const", const=0, dest="verbosity", help=_("Minimize program output. Only errors and warnings are displayed."))
    p.add_argument("--debug", action="count", dest="debug", help=_("Enable debugging output."))
    p.add_argument("--trace", action="store_true", dest="trace", help=_("Enable verbose function tracing."))
    p.add_argument("--trace-off", action="store_false", dest="trace", help=_("Disable verbose function tracing."))
    p.add_argument("--logfile", action="store", dest="logfile", help=_("Specify a file to log all operations to"))
    args = p.parse_args()
    setupLogging(verbosity=args.verbosity, trace=args.trace, debug=args.debug, log_file=args.logfile)

    testModulePath="%s/test/" % top_srcdir

    moduleNames = glob.glob( "%s/test*.py" % testModulePath )
    moduleNames = [ m[len(testModulePath):-3] for m in moduleNames ]

    tests = []
    for moduleName in moduleNames:
        if "testAll" in moduleName:
            continue
        module = __import__(moduleName, globals(), locals(), [])
        module.TestCase.top_srcdir=top_srcdir
        module.TestCase.top_builddir=top_builddir
        tests.append(module.TestCase)

    retval = 1
    if tests:
        retval = TestLib.runTests( tests )

    sys.exit( not retval )
