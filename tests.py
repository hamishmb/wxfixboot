#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Unit tests for WxFixBoot
# This file is part of WxFixBoot.
# Copyright (C) 2013-2019 Hamish McIntyre-Bhatty
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

"""
This module contains the code used to run the test suites for WxFixBoot.
"""

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII
#strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import modules.
import unittest
import logging
import os
import getopt
import sys

#Global vars.
VERSION = "3.0.0"

#Set up the logger (silence all except critical logging messages).
logger = logging.getLogger('WxFixBoot')

#Log only critical messages by default.
LOGGER_LEVEL = logging.CRITICAL

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p', level=LOGGER_LEVEL)

#Make unicode an alias for str in Python 3.
if sys.version_info[0] == 3:
    #Disable cos necessary to keep supporting python 2.
    unicode = str #pylint: disable=redefined-builtin,invalid-name

def usage():
    print("\nUsage: Tests.py [OPTION]\n\n")
    print("Options:\n")
    print("       -h, --help:                   Display this help text.")
    print("       -D, --debug:                  Set logging level to debug, to show all logging")
    print("                                     messages. Default: show only critical logging")
    print("                                     messages.")
    print("       -s, --startuptools            Run tests for all StartupTools modules.")
    print("       -b, --backendtools            Run tests for all BackendTools modules.")
    print("       -c, --coretools:              Run tests for CoreTools module.")
    print("       -d, --dialogtools:            Run tests for DialogTools module.")
    print("       -m, --main:                   Run tests for main file (WxFixBoot.py).")
    print("       -a, --all:                    Run all the tests. The default.\n")
    print("       -t, --tests:                  Ignored.")
    print("WxFixBoot "+VERSION+" is released under the GNU GPL Version 3")
    print("Copyright (C) Hamish McIntyre-Bhatty 2013-2019")

if __name__ == "__main__":
    #Exit if not running as root.
    if os.geteuid() != 0:
        sys.exit("You must run the tests as root! Exiting...")

    #Check all cmdline options are valid.
    try:
        OPTS = getopt.getopt(sys.argv[1:], "hDdsbcmat", ["help", "debug", "startuptools",
                                                         "backendtools", "coretools", "main",
                                                         "all", "tests"])[0]

    except getopt.GetoptError as err:
        #Invalid option. Show the help message and then exit.
        #Show the error.
        print(unicode(err))
        usage()
        sys.exit(2)

    #We have to handle options twice for this to work - a bit strange, but it works.
    #Handle debugging mode here.
    for o, a in OPTS:
        if o in ["-D", "--debug"]:
            LOGGER_LEVEL = logging.DEBUG

    logger.setLevel(LOGGER_LEVEL)

    #Import test modules here so the logging level is right - debug mode will work.
    from Tests.Tools import CoreToolsTests
    from Tests.Tools import DialogToolsTests

    from Tests.Tools.BackendTools import HelperBackendToolsTests
    from Tests.Tools.BackendTools import EssentialBackendToolsTests

    from Tests.Tools.StartupTools import CoreStartupToolsTests
    from Tests.Tools.StartupTools import MainStartupToolsTests

    #Set up which tests to run based on options given.
    #TODO Set up full defaults when finished.
    TESTSUITES = [CoreToolsTests, DialogToolsTests, HelperBackendToolsTests,
                  EssentialBackendToolsTests, CoreStartupToolsTests,
                  MainStartupToolsTests]

    for o, a in OPTS:
        if o in ["-c", "--coretools"]:
            TESTSUITES = [CoreToolsTests]
        elif o in ["-d", "--dialogtools"]:
            TESTSUITES = [DialogToolsTests]
        elif o in ["-s", "--startuptools"]:
            TESTSUITES = [CoreStartupToolsTests, MainStartupToolsTests]
            #Implementation isn't finished ***
        elif o in ["-b", "--backendtools"]:
            TESTSUITES = [HelperBackendToolsTests, EssentialBackendToolsTests]
            #Implementation isn't finished ***
        elif o in ["-m", "--main"]:
            #TESTSUITES = [MainTests]
            assert False, "Not implemented yet"
        elif o in ["-a", "--all"]:
            TESTSUITES = [CoreToolsTests, DialogToolsTests, HelperBackendToolsTests,
                          EssentialBackendToolsTests, CoreStartupToolsTests, MainStartupToolsTests]
            #TESTSUITES.append(MainTests)
        elif o in ["-t", "--tests"]:
            pass
        elif o in ["-D", "--debug"]:
            LOGGER_LEVEL = logging.DEBUG
        elif o in ["-h", "--help"]:
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    for SuiteModule in TESTSUITES:
        print("\n\nTests in "+unicode(SuiteModule)+"\n\n")
        unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromModule(SuiteModule))
