#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Unit tests for WxFixBoot Version 3.0.0
# This file is part of WxFixBoot.
# Copyright (C) 2013-2018 Hamish McIntyre-Bhatty
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
import subprocess
import re
import logging
import plistlib
import os
import getopt
import sys
from bs4 import BeautifulSoup

#Global vars.
VERSION = "3.0.0"

#Custom made modules.
import GetDevInfo
import Tools

import GetDevInfo.getdevinfo as DevInfoTools
import Tools.coretools as CoreTools
import Tools.dialogtools as DialogTools

import Tools.BackendTools.helpers as HelperBackendTools
import Tools.BackendTools.essentials as EssentialBackendTools

import Tools.StartupTools.core as CoreStartupTools
import Tools.StartupTools.main as MainStartupTools

#Import test modules.
from Tests import DialogFunctionsForTests
from Tests.GetDevInfo import GetDevInfoTests
from Tests.Tools import CoreToolsTests
from Tests.Tools import DialogToolsTests

from Tests.Tools.BackendTools import HelperBackendToolsTests
from Tests.Tools.BackendTools import EssentialBackendToolsTests

from Tests.Tools.StartupTools import CoreStartupToolsTests
from Tests.Tools.StartupTools import MainStartupToolsTests

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
    print("WxFixBoot "+VERSION+" is released under the GNU GPL Version 3")
    print("Copyright (C) Hamish McIntyre-Bhatty 2013-2018")

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
TestSuites = [GetDevInfoTests, CoreToolsTests, DialogToolsTests, HelperBackendToolsTests, EssentialBackendToolsTests, CoreStartupToolsTests, MainStartupToolsTests] #*** Set up full defaults when finished ***

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
        TestSuites = [CoreStartupToolsTests, MainStartupToolsTests]
        #Implementation isn't finished ***
    elif o in ["-b", "--backendtools"]:
        TestSuites = [HelperBackendToolsTests, EssentialBackendToolsTests]
        #Implementation isn't finished ***
    elif o in ["-m", "--main"]:
        #TestSuites = [MainTests]
        assert False, "Not implemented yet"
    elif o in ["-a", "--all"]:
        TestSuites = [GetDevInfoTests, CoreToolsTests, DialogToolsTests, HelperBackendToolsTests, EssentialBackendToolsTests, CoreStartupToolsTests, MainStartupToolsTests]
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
#* ^ They are modified versions that log messages and results to enable better test automation without needing user intervention as much.* FIXME DEPRECATED

GetDevInfo.getdevinfo.subprocess = subprocess
GetDevInfo.getdevinfo.re = re
GetDevInfo.getdevinfo.os = os
GetDevInfo.getdevinfo.logger = logger
GetDevInfo.getdevinfo.plistlib = plistlib
GetDevInfo.getdevinfo.BeautifulSoup = BeautifulSoup

#Setup test modules. FIXME DEPRECATED
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

#Main Startup tools tests.
MainStartupToolsTests.DialogFunctionsForTests = DialogFunctionsForTests
MainStartupToolsTests.CoreTools = CoreTools
MainStartupToolsTests.MainStartupTools = MainStartupTools
MainStartupToolsTests.CoreStartupTools = CoreStartupTools
MainStartupToolsTests.DevInfoTools = DevInfoTools
MainStartupToolsTests.GetDevInfo = GetDevInfo
MainStartupToolsTests.Tools = Tools

if __name__ == "__main__":
    for SuiteModule in TestSuites:
        print("\n\nTests in "+unicode(SuiteModule)+"\n\n")
        unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromModule(SuiteModule))
