#!/usr/bin/env python
# -*- coding: utf-8 -*-
# HelperBackendTools test data for WxFixBoot Version 3.0.0
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
def return_initial_system_info_dict():
    return {"DisableBootloaderOperationsBecause": [], "IsLiveDisk": False}

def return_initial_system_info_dict2():
    return {"DisableBootloaderOperationsBecause": [], "IsLiveDisk": True}

def return_system_info_dict_with_disabled_bl_opts():
    return {"DisableBootloaderOperations": True, "DisableBootloaderOperationsBecause": ["Internet Connection test failed."]}

def return_system_info_dict_with_enabled_bl_opts():
    return {"DisableBootloaderOperations": False, "DisableBootloaderOperationsBecause": []}

#Return fake disk_info dictionary.
def return_fake_disk_info():
    disk_info = {}

    #Fictional /dev/sda.
    disk_info["/dev/sda"] = {}
    disk_info["/dev/sda"]["Product"] = "FakeDisk"
    disk_info["/dev/sda"]["Vendor"] = "ThereIsNone"
    disk_info["/dev/sda"]["Name"] = "/dev/sda"
    disk_info["/dev/sda"]["Description"] = "Fake Hard Disk Drive"
    disk_info["/dev/sda"]["RawCapacity"] = "56483132"
    disk_info["/dev/sda"]["HostDevice"] = "N/A"
    disk_info["/dev/sda"]["Capacity"] = "200GB"
    disk_info["/dev/sda"]["Type"] = "Device"
    disk_info["/dev/sda"]["Partitions"] = ["/dev/sda1", "/dev/sda2", "/dev/sda3"]
    disk_info["/dev/sda"]["FileSystem"] = "jfs"

    #Fictional /dev/sda1
    disk_info["/dev/sda1"] = {}
    disk_info["/dev/sda1"]["Product"] = "Host Device: FakeDisk"
    disk_info["/dev/sda1"]["Vendor"] = "FakeOS v3"
    disk_info["/dev/sda1"]["Name"] = "/dev/sda1"
    disk_info["/dev/sda1"]["Description"] = "EXT4 Volume"
    disk_info["/dev/sda1"]["RawCapacity"] = "5648313"
    disk_info["/dev/sda1"]["HostDevice"] = "/dev/sda"
    disk_info["/dev/sda1"]["Capacity"] = "20GB"
    disk_info["/dev/sda1"]["Type"] = "Partition"
    disk_info["/dev/sda1"]["Partitions"] = []
    disk_info["/dev/sda1"]["FileSystem"] = "ext4"

    #Fictional /dev/sda2
    disk_info["/dev/sda2"] = {}
    disk_info["/dev/sda2"]["Product"] = "Host Device: FakeDisk"
    disk_info["/dev/sda2"]["Vendor"] = "FakeOS v3"
    disk_info["/dev/sda2"]["Name"] = "/dev/sda2"
    disk_info["/dev/sda2"]["Description"] = "EXT3 Volume"
    disk_info["/dev/sda2"]["RawCapacity"] = "564313"
    disk_info["/dev/sda2"]["HostDevice"] = "/dev/sda"
    disk_info["/dev/sda2"]["Capacity"] = "2.5GB"
    disk_info["/dev/sda2"]["Type"] = "Partition"
    disk_info["/dev/sda2"]["Partitions"] = []
    disk_info["/dev/sda2"]["FileSystem"] = "ext3"

    #Fictional /dev/sda3
    disk_info["/dev/sda3"] = {}
    disk_info["/dev/sda3"]["Product"] = "Host Device: FakeDisk"
    disk_info["/dev/sda3"]["Vendor"] = "FakeOS v3"
    disk_info["/dev/sda3"]["Name"] = "/dev/sda3"
    disk_info["/dev/sda3"]["Description"] = "MSDOS Volume"
    disk_info["/dev/sda3"]["RawCapacity"] = "564456313"
    disk_info["/dev/sda3"]["HostDevice"] = "/dev/sda"
    disk_info["/dev/sda3"]["Capacity"] = "25.5GB"
    disk_info["/dev/sda3"]["Type"] = "Partition"
    disk_info["/dev/sda3"]["Partitions"] = []
    disk_info["/dev/sda3"]["FileSystem"] = "vfat"

    return disk_info

def return_expected_result_finding_missing_fsck_modules():
    return []
