#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# MainStartupTools test data for WxFixBoot
# This file is part of WxFixBoot.
# Copyright (C) 2013-2020 Hamish McIntyre-Bhatty
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

def return_fake_bl_info1():
    return {"Linux Mint": {"IsModifyable": True, "Comments": "x86_64 architecture",
                           "MenuEntries": {}},

            "Windows Vistarg": {"IsModifyable": False,
                                "Comments": "Windows cannot be modified with WxFixBoot",
                                "MenuEntries": {}},

            "macOS Sierra": {"IsModifyable": False,
                             "Comments": "macOS cannot be modified with WxFixBoot",
                             "MenuEntries": {}},

            "Fedora Core 25": {"IsModifyable": True, "Comments": "i386 architecture",
                               "MenuEntries": {}}
           }

def return_fake_bl_info2():
    return {"Linux Mint": {"IsModifyable": True, "Comments": "x86_64 architecture",
                           "MenuEntries": {}},

            "Fedora Core 25": {"IsModifyable": True, "Comments": "i386 architecture",
                               "MenuEntries": {}}
           }

def return_final_check_results1():
    return "Some of the OSs found on your system cannot be modified! These are:\n\nWindows Vistarg, because Windows cannot be modified with WxFixBoot\nmacOS Sierra, because macOS cannot be modified with WxFixBoot\n\nClick okay to continue."
