#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Unit tests for WxFixBoot Version 2.0.1
# This file is part of WxFixBoot.
# Copyright (C) 2013-2017 Hamish McIntyre-Bhatty
# WxFixBoot is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 or,
# at your option, any later version.
#
# WxFixBoot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WxFixBoot.  If not, see <http://www.gnu.org/licenses/>.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import unittest
import wx
import subprocess
import re
import logging
import plistlib
import os
import time
import getopt
import sys
from bs4 import BeautifulSoup

#Global vars.
Version = "2.0.1"

#Custom made modules.
import GetDevInfo
import Tools

from GetDevInfo.getdevinfo import Main as DevInfoTools
from Tools.coretools import Main as CoreTools
from Tools.dialogtools import Main as DialogTools

from Tools.BackendTools.helpers import Main as HelperBackendTools
from Tools.BackendTools.essentials import Main as EssentialBackendTools

from Tools.StartupTools.core import Main as CoreStartupTools

#Import test modules.
import Tests

from Tests import DialogFunctionsForTests
from Tests.GetDevInfo import GetDevInfoTests
from Tests.Tools import CoreToolsTests
from Tests.Tools import DialogToolsTests

from Tests.Tools.BackendTools import HelperBackendToolsTests
from Tests.Tools.BackendTools import EssentialBackendToolsTests

from Tests.Tools.StartupTools import CoreStartupToolsTests

def usage():
    print("\nUsage: Tests.py [OPTION]\n\n")
    print("Options:\n")
    print("       -h, --help:                   Display this help text.")
    print("       -D, --debug:                  Set logging level to debug, to show all logging messages. Default: show only critical logging messages.")
    print("       -s, --startuptools            Run tests for all StartupTools modules.")
    print("       -b, --backendtools            Run tests for all BackendTools modules.")
    print("       -g, --getdevinfo:             Run tests for GetDevInfo module.")
    print("       -c, --coretools:              Run tests for CoreTools module.")
    print("       -d, --dialogtools:            Run tests for DialogTools module.")
    print("       -m, --main:                   Run tests for main file (WxFixBoot.py).")
    print("       -a, --all:                    Run all the tests. The default.\n")
    print("       -t, --tests:                  Ignored.")
    print("WxFixBoot "+Version+" is released under the GNU GPL Version 3")
    print("Copyright (C) Hamish McIntyre-Bhatty 2013-2017")

#Exit if not running as root.
if os.geteuid() != 0:
    sys.exit("You must run the tests as root! Exiting...")

#Check all cmdline options are valid.
try:
    opts, args = getopt.getopt(sys.argv[1:], "hDdsbgcmat", ["help", "debug", "startuptools", "backendtools", "getdevinfo", "coretools", "main", "all", "tests"])

except getopt.GetoptError as err:
    #Invalid option. Show the help message and then exit.
    #Show the error.
    print(unicode(err))
    usage()
    sys.exit(2)

#Set up which tests to run based on options given.
TestSuites = [GetDevInfoTests, CoreToolsTests, DialogToolsTests, HelperBackendToolsTests, EssentialBackendToolsTests, CoreStartupToolsTests] #*** Set up full defaults when finished ***

#Log only critical message by default.
loggerLevel = logging.CRITICAL

for o, a in opts:
    if o in ["-g", "--getdevinfo"]:
        TestSuites = [GetDevInfoTests]
    elif o in ["-c", "--coretools"]:
        TestSuites = [CoreToolsTests]
    elif o in ["-d", "--dialogtools"]:
        TestSuites = [DialogToolsTests]
    elif o in ["-s", "--startuptools"]:
        TestSuites = [CoreStartupToolsTests]
        #Implementation isn't finished ***
    elif o in ["-b", "--backendtools"]:
        TestSuites = [HelperBackendToolsTests, EssentialBackendToolsTests]
        #Implementation isn't finished ***
    elif o in ["-m", "--main"]:
        #TestSuites = [MainTests]
        assert False, "Not implemented yet"
    elif o in ["-a", "--all"]:
        TestSuites = [GetDevInfoTests, CoreToolsTests, DialogToolsTests, HelperBackendToolsTests, EssentialBackendToolsTests, CoreStartupToolsTests]
        #TestSuites.append(MainTests)
    elif o in ["-t", "--tests"]:
        pass
    elif o in ["-D", "--debug"]:
        loggerLevel = logging.DEBUG
    elif o in ["-h", "--help"]:
        usage()
        sys.exit()
    else:
        assert False, "unhandled option"

#Set up the logger (silence all except critical logging messages).
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=loggerLevel)
logger = logging

#Setup custom-made modules (make global variables accessible inside the packages).
#*DialogTools is defined in the test suite files in an as-needed basis.*
#* ^ They are modified versions that log messages and results to enable better test automation without needing user intervention as much.*

GetDevInfo.getdevinfo.subprocess = subprocess
GetDevInfo.getdevinfo.re = re
GetDevInfo.getdevinfo.os = os
GetDevInfo.getdevinfo.logger = logger
GetDevInfo.getdevinfo.plistlib = plistlib
GetDevInfo.getdevinfo.BeautifulSoup = BeautifulSoup

Tools.coretools.wx = wx
Tools.coretools.subprocess = subprocess
Tools.coretools.sys = sys
Tools.coretools.logger = logger
Tools.coretools.logging = logging
Tools.coretools.os = os

Tools.dialogtools.wx = wx
Tools.dialogtools.logger = logger
Tools.dialogtools.time = time

Tools.BackendTools.helpers.logger = logger
Tools.BackendTools.helpers.os = os
Tools.BackendTools.helpers.time = time
Tools.BackendTools.helpers.CoreTools = CoreTools()

Tools.BackendTools.essentials.wx = wx
Tools.BackendTools.essentials.logger = logger
Tools.BackendTools.essentials.CoreTools = CoreTools()
Tools.BackendTools.essentials.HelperBackendTools = HelperBackendTools()

Tools.StartupTools.core.logger = logger
Tools.StartupTools.core.CoreTools = CoreTools()

#Setup test modules.
#GetDevInfo tests.
GetDevInfoTests.DevInfoTools = DevInfoTools
GetDevInfoTests.GetDevInfo = GetDevInfo

#Core tools tests.
CoreToolsTests.DialogFunctionsForTests = DialogFunctionsForTests
CoreToolsTests.CoreTools = CoreTools
CoreToolsTests.Tools = Tools

#Dialog tools tests.
DialogToolsTests.DialogFunctionsForTests = DialogFunctionsForTests
DialogToolsTests.DialogTools = DialogTools
DialogToolsTests.Tools = Tools

#Helper Backend tools tests.
HelperBackendToolsTests.DialogFunctionsForTests = DialogFunctionsForTests
HelperBackendToolsTests.HelperBackendTools = HelperBackendTools
HelperBackendToolsTests.CoreTools = CoreTools
HelperBackendToolsTests.DevInfoTools = DevInfoTools
HelperBackendToolsTests.GetDevInfo = GetDevInfo
HelperBackendToolsTests.Tools = Tools

#Essential Backend tools tests.
EssentialBackendToolsTests.DialogFunctionsForTests = DialogFunctionsForTests
EssentialBackendToolsTests.EssentialBackendTools = EssentialBackendTools
EssentialBackendToolsTests.Tools = Tools

#Core Startup tools tests.
CoreStartupToolsTests.DialogFunctionsForTests = DialogFunctionsForTests
CoreStartupToolsTests.CoreTools = CoreTools
CoreStartupToolsTests.CoreStartupTools = CoreStartupTools
CoreStartupToolsTests.Tools = Tools

if __name__ == "__main__":
    for SuiteModule in TestSuites:
        print("\n\n---------------------------- Tests for "+unicode(SuiteModule)+" ----------------------------\n\n")
        unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromModule(SuiteModule))
