#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# HelperBackendTools test data for WxFixBoot Version 2.0.3
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

#Functions to return test data.
#Return fake SystemInfo dictionary.
def ReturnInitialSystemInfoDict():
    return {"DisableBootloaderOperationsBecause": [], "IsLiveDisk": False}

def ReturnInitialSystemInfoDict2():
    return {"DisableBootloaderOperationsBecause": [], "IsLiveDisk": True}

def ReturnSystemInfoDictWithDisabledBLOpts():
    return {"DisableBootloaderOperations": True, "DisableBootloaderOperationsBecause": ["Internet Connection test failed."]}

def ReturnSystemInfoDictWithEnabledBLOpts():
    return {"DisableBootloaderOperations": False, "DisableBootloaderOperationsBecause": []}

#Return fake DiskInfo dictionary.
def ReturnFakeDiskInfo():
    DiskInfo = {}

    #Fictional /dev/sda.
    DiskInfo["/dev/sda"] = {}
    DiskInfo["/dev/sda"]["Product"] = "FakeDisk"
    DiskInfo["/dev/sda"]["Vendor"] = "ThereIsNone"
    DiskInfo["/dev/sda"]["Name"] = "/dev/sda"
    DiskInfo["/dev/sda"]["Description"] = "Fake Hard Disk Drive"
    DiskInfo["/dev/sda"]["RawCapacity"] = "56483132"
    DiskInfo["/dev/sda"]["HostDevice"] = "N/A"
    DiskInfo["/dev/sda"]["Capacity"] = "200GB"
    DiskInfo["/dev/sda"]["Type"] = "Device"
    DiskInfo["/dev/sda"]["Partitions"] = ["/dev/sda1", "/dev/sda2", "/dev/sda3"]
    DiskInfo["/dev/sda"]["FileSystem"] = "jfs"

    #Fictional /dev/sda1
    DiskInfo["/dev/sda1"] = {}
    DiskInfo["/dev/sda1"]["Product"] = "Host Device: FakeDisk"
    DiskInfo["/dev/sda1"]["Vendor"] = "FakeOS v3"
    DiskInfo["/dev/sda1"]["Name"] = "/dev/sda1"
    DiskInfo["/dev/sda1"]["Description"] = "EXT4 Volume"
    DiskInfo["/dev/sda1"]["RawCapacity"] = "5648313"
    DiskInfo["/dev/sda1"]["HostDevice"] = "/dev/sda"
    DiskInfo["/dev/sda1"]["Capacity"] = "20GB"
    DiskInfo["/dev/sda1"]["Type"] = "Partition"
    DiskInfo["/dev/sda1"]["Partitions"] = []
    DiskInfo["/dev/sda1"]["FileSystem"] = "ext4"

    #Fictional /dev/sda2
    DiskInfo["/dev/sda2"] = {}
    DiskInfo["/dev/sda2"]["Product"] = "Host Device: FakeDisk"
    DiskInfo["/dev/sda2"]["Vendor"] = "FakeOS v3"
    DiskInfo["/dev/sda2"]["Name"] = "/dev/sda2"
    DiskInfo["/dev/sda2"]["Description"] = "EXT3 Volume"
    DiskInfo["/dev/sda2"]["RawCapacity"] = "564313"
    DiskInfo["/dev/sda2"]["HostDevice"] = "/dev/sda"
    DiskInfo["/dev/sda2"]["Capacity"] = "2.5GB"
    DiskInfo["/dev/sda2"]["Type"] = "Partition"
    DiskInfo["/dev/sda2"]["Partitions"] = []
    DiskInfo["/dev/sda2"]["FileSystem"] = "ext3"

    #Fictional /dev/sda3
    DiskInfo["/dev/sda3"] = {}
    DiskInfo["/dev/sda3"]["Product"] = "Host Device: FakeDisk"
    DiskInfo["/dev/sda3"]["Vendor"] = "FakeOS v3"
    DiskInfo["/dev/sda3"]["Name"] = "/dev/sda3"
    DiskInfo["/dev/sda3"]["Description"] = "MSDOS Volume"
    DiskInfo["/dev/sda3"]["RawCapacity"] = "564456313"
    DiskInfo["/dev/sda3"]["HostDevice"] = "/dev/sda"
    DiskInfo["/dev/sda3"]["Capacity"] = "25.5GB"
    DiskInfo["/dev/sda3"]["Type"] = "Partition"
    DiskInfo["/dev/sda3"]["Partitions"] = []
    DiskInfo["/dev/sda3"]["FileSystem"] = "vfat"

    return DiskInfo

def ReturnExpectedResultFindingMissingFSCKModules():
    return []
