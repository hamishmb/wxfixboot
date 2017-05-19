#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# MainStartupTools test functions for WxFixBoot Version 2.0.1
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

#If you're wondering why this is here, it's so that there are some known good/sane functions to aid testing the ones in DialogTools.

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

WouldEmergencyExit = False
WouldEmergencyExitBecause = []

def EmergencyExit(Message):
    """Test suite special: sets a variable so the tests know if an Emergency Exit would have been triggered."""
    global WouldEmergencyExit
    global WouldEmergencyExitBecause

    WouldEmergencyExit = True
    WouldEmergencyExitBecause.append(Message)

def CheckDepends():
    """Check dependencies, and show an error message and kill the app if the dependencies are not met."""
    #Create a temporary list to allow WxFixBoot to notify the user of particular unmet dependencies.
    CmdList = ("cp", "mv", "which", "uname", "fsck", "ls", "modprobe", "mount", "umount", "rm", "ping", "badblocks", "arch", "python", "file", "sh", "echo", "lshw", "lvdisplay", "dmidecode", "chroot", "strings", "dd", "blkid")

    #Create a list to contain names of failed commands.
    FailedList = []

    for Command in CmdList:
        #Run the command with its argument and log the output (if in debug mode)
        Retval, Output = CoreTools.StartProcess("which "+Command, ReturnOutput=True)

        if Retval != 0:
            FailedList.append(Command)

    #Check if any commands failed.
    if FailedList != []:
        #Missing dependencies!
        EmergencyExit("The following dependencies could not be found on your system: "+', '.join(FailedList)+".\n\nPlease install the missing dependencies.")
