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

# all of the variables below are substituted by the build system
__VERSION__="1.0.0"

import TestLib

exeName = os.path.realpath(sys.argv[0])
top_srcdir = os.path.join(os.path.dirname(exeName), "..")
top_builddir = os.getcwd()

sys.path.insert(0,top_srcdir)
sys.path.insert(0,"%s/lcctool/" % top_srcdir)

# runs all modules TestCase() classes in files that match test*.py
if __name__ == "__main__":
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
