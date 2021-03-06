#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# GetDevInfo test data for WxFixBoot Version 2.0.3
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

#Classes for test cases.
class Node1:
    def GetCopy(self):
        return self

    class vendor:
        string = "FakeVendor"

    class product:
        string = "FakeProduct"

    class capacity:
        string = 100000000000

class Node2:
    def GetCopy(self):
        return self

    class vendor:
        string = "FakeVendor2"

    class product:
        string = "FakeProduct2"

    class size:
        string = 10000000000000000000

class BadNode1:
    def GetCopy(self):
        return self

    class vendor:
        notstring = ""

    class product:
        notstring = ""

class BadNode2:
    def GetCopy(self):
        return self

    class vendor:
        notstring = ""

    class product:
        notstring = ""

    class capacity:
        #Too long, causes IndexError.
        string = 1000000000000000000000000000000000000000000000000

class BadNode3:
    def GetCopy(self):
        return self

    class vendor:
        notstring = ""

    class product:
        notstring = ""

    class size:
        string = "fghjk"

#Functions to return fake DiskInfo dictionary.
def ReturnFakeDiskInfoLinux():
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
    DiskInfo["/dev/sda"]["Partitions"] = ["/dev/sda1", "/dev/sda2"]

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

    #Fictional /dev/sda3
    DiskInfo["/dev/sda3"] = {}
    DiskInfo["/dev/sda3"]["Product"] = "Host Device: FakeDisk"
    DiskInfo["/dev/sda3"]["Vendor"] = "FakeOS v3"
    DiskInfo["/dev/sda3"]["Name"] = "/dev/sda3"
    DiskInfo["/dev/sda3"]["Description"] = "BTRFS Volume"
    DiskInfo["/dev/sda3"]["RawCapacity"] = "564456313"
    DiskInfo["/dev/sda3"]["HostDevice"] = "/dev/sda"
    DiskInfo["/dev/sda3"]["Capacity"] = "25.5GB"
    DiskInfo["/dev/sda3"]["Type"] = "Partition"
    DiskInfo["/dev/sda3"]["Partitions"] = []

    return DiskInfo

def ReturnFakeDiskInfoMac():
    DiskInfo = {}

    #Fictional /dev/disk0.
    DiskInfo["/dev/disk0"] = {}
    DiskInfo["/dev/disk0"]["Product"] = "FakeDisk"
    DiskInfo["/dev/disk0"]["Vendor"] = "ThereIsNone"
    DiskInfo["/dev/disk0"]["Name"] = "/dev/disk0"
    DiskInfo["/dev/disk0"]["Description"] = "Fake Hard Disk Drive"
    DiskInfo["/dev/disk0"]["RawCapacity"] = "56483132"
    DiskInfo["/dev/disk0"]["HostDevice"] = "N/A"
    DiskInfo["/dev/disk0"]["Capacity"] = "200GB"
    DiskInfo["/dev/disk0"]["Type"] = "Device"
    DiskInfo["/dev/disk0"]["Partitions"] = ["/dev/disk0s1", "/dev/disk0s2", "/dev/disk0s3"]

    #Fictional /dev/disk0s1
    DiskInfo["/dev/disk0s1"] = {}
    DiskInfo["/dev/disk0s1"]["Product"] = "Host Device: FakeDisk"
    DiskInfo["/dev/disk0s1"]["Vendor"] = "FakeOS v3"
    DiskInfo["/dev/disk0s1"]["Name"] = "/dev/disk0s1"
    DiskInfo["/dev/disk0s1"]["Description"] = "HFS+ Volume"
    DiskInfo["/dev/disk0s1"]["RawCapacity"] = "5648313"
    DiskInfo["/dev/disk0s1"]["HostDevice"] = "/dev/disk0"
    DiskInfo["/dev/disk0s1"]["Capacity"] = "20GB"
    DiskInfo["/dev/disk0s1"]["Type"] = "Partition"
    DiskInfo["/dev/disk0s1"]["Partitions"] = []

    #Fictional /dev/disk0s2
    DiskInfo["/dev/disk0s2"] = {}
    DiskInfo["/dev/disk0s2"]["Product"] = "Host Device: FakeDisk"
    DiskInfo["/dev/disk0s2"]["Vendor"] = "FakeOS v3"
    DiskInfo["/dev/disk0s2"]["Name"] = "/dev/disk0s2"
    DiskInfo["/dev/disk0s2"]["Description"] = "NTFS Volume"
    DiskInfo["/dev/disk0s2"]["RawCapacity"] = "564313"
    DiskInfo["/dev/disk0s2"]["HostDevice"] = "/dev/disk0"
    DiskInfo["/dev/disk0s2"]["Capacity"] = "2.5GB"
    DiskInfo["/dev/disk0s2"]["Type"] = "Partition"
    DiskInfo["/dev/disk0s2"]["Partitions"] = []

    #Fictional /dev/disk0s3
    DiskInfo["/dev/disk0s3"] = {}
    DiskInfo["/dev/disk0s3"]["Product"] = "Host Device: FakeDisk"
    DiskInfo["/dev/disk0s3"]["Vendor"] = "FakeOS v3"
    DiskInfo["/dev/disk0s3"]["Name"] = "/dev/disk0s3"
    DiskInfo["/dev/disk0s3"]["Description"] = "FAT Volume"
    DiskInfo["/dev/disk0s3"]["RawCapacity"] = "564313"
    DiskInfo["/dev/disk0s3"]["HostDevice"] = "/dev/disk0"
    DiskInfo["/dev/disk0s3"]["Capacity"] = "24.5GB"
    DiskInfo["/dev/disk0s3"]["Type"] = "Partition"
    DiskInfo["/dev/disk0s3"]["Partitions"] = []

    return DiskInfo

#Functions to return other data.
def ReturnFakeLVMDiskInfo():
    return {u'/dev/sda': {u'Product': u'FakeDisk', u'Vendor': u'ThereIsNone', u'Name': u'/dev/sda', u'RawCapacity': u'56483132', u'HostDevice': u'N/A', u'Capacity': u'200GB', u'Partitions': [u'/dev/sda1', u'/dev/sda2'], u'Type': u'Device', u'Description': u'Fake Hard Disk Drive'}, u'/dev/mapper/fakefedora-root': {u'LVName': u'root', u'VGName': u'fakefedora', u'HostPartition': u'/dev/sda3', u'Vendor': u'Linux', u'Name': u'/dev/mapper/fakefedora-root', u'Capacity': u'13.20 GiB', u'Product': u'LVM Partition', u'UUID': u'TWxt1j-g62o-GYju-3UpB-A4g3-9ZbB-HWb7jf', u'Partitioning': u'N/A', u'HostDevice': u'/dev/sda', u'BootRecord': u'Unknown', u'Flags': [], u'RawCapacity': u'13.20 GiB', u'BootRecordStrings': [u'Unknown'], u'FileSystem': u'', u'Description': u'LVM partition root in volume group fakefedora', u'Aliases': [u'/dev/mapper/fakefedora-root', u'/dev/fakefedora/root'], u'Type': u'Partition', u'ID': u'dm-name-fakefedora-root', u'Partitions': []}, u'/dev/sda3': {u'Product': u'Host Device: FakeDisk', u'Vendor': u'FakeOS v3', u'Name': u'/dev/sda3', u'RawCapacity': u'564456313', u'HostDevice': u'/dev/sda', u'Capacity': u'25.5GB', u'Partitions': [], u'Type': u'Partition', u'Description': u'BTRFS Volume'}, u'/dev/sda1': {u'Product': u'Host Device: FakeDisk', u'Vendor': u'FakeOS v3', u'Name': u'/dev/sda1', u'RawCapacity': u'5648313', u'HostDevice': u'/dev/sda', u'Capacity': u'20GB', u'Partitions': [], u'Type': u'Partition', u'Description': u'EXT4 Volume'}, u'/dev/sda2': {u'Product': u'Host Device: FakeDisk', u'Vendor': u'FakeOS v3', u'Name': u'/dev/sda2', u'RawCapacity': u'564313', u'HostDevice': u'/dev/sda', u'Capacity': u'2.5GB', u'Partitions': [], u'Type': u'Partition', u'Description': u'EXT3 Volume'}, u'/dev/mapper/fakefedora-swap': {u'LVName': u'swap', u'VGName': u'fakefedora', u'HostPartition': u'/dev/sda3', u'Vendor': u'Linux', u'Name': u'/dev/mapper/fakefedora-swap', u'Capacity': u'1.60 GiB', u'Product': u'LVM Partition', u'UUID': u'3e8urm-xsCG-iCAJ-Q3go-2247-OU5N-3AwlD1', u'Partitioning': u'N/A', u'HostDevice': u'/dev/sda', u'BootRecord': u'Unknown', u'Flags': [], u'RawCapacity': u'1.60 GiB', u'BootRecordStrings': [u'Unknown'], u'FileSystem': u'', u'Description': u'LVM partition swap in volume group fakefedora', u'Aliases': [u'/dev/mapper/fakefedora-swap', u'/dev/fakefedora/swap'], u'Type': u'Partition', u'ID': u'dm-name-fakefedora-swap', u'Partitions': []}}

def ReturnFakeDiskutilListPlist():
    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>AllDisks</key>
	<array>
		<string>disk0</string>
		<string>disk0s1</string>
		<string>disk0s2</string>
		<string>disk0s3</string>
	</array>
	<key>AllDisksAndPartitions</key>
	<array>
		<dict>
			<key>Content</key>
			<string>GUID_partition_scheme</string>
			<key>DeviceIdentifier</key>
			<string>disk0</string>
			<key>Partitions</key>
			<array>
				<dict>
					<key>Content</key>
					<string>EFI</string>
					<key>DeviceIdentifier</key>
					<string>disk0s1</string>
					<key>DiskUUID</key>
					<string>A0C85363-E33F-4708-9B6A-68BD0AA062C1</string>
					<key>Size</key>
					<integer>209715200</integer>
					<key>VolumeName</key>
					<string>EFI</string>
					<key>VolumeUUID</key>
					<string>85D67001-D93E-3687-A1C2-79D677F0C2E0</string>
				</dict>
				<dict>
					<key>Content</key>
					<string>Apple_HFS</string>
					<key>DeviceIdentifier</key>
					<string>disk0s2</string>
					<key>DiskUUID</key>
					<string>72914C17-6469-457F-B2F0-26BE5BD03843</string>
					<key>MountPoint</key>
					<string>/</string>
					<key>Size</key>
					<integer>42089095168</integer>
					<key>VolumeName</key>
					<string>OSX</string>
					<key>VolumeUUID</key>
					<string>AC723754-135E-39BE-8A81-C91228501E9B</string>
				</dict>
				<dict>
					<key>Content</key>
					<string>Apple_Boot</string>
					<key>DeviceIdentifier</key>
					<string>disk0s3</string>
					<key>DiskUUID</key>
					<string>353F6CFF-8E9C-4480-BC8B-D6357E15299E</string>
					<key>Size</key>
					<integer>650002432</integer>
					<key>VolumeName</key>
					<string>Recovery HD</string>
					<key>VolumeUUID</key>
					<string>F1573C36-EC30-3501-8E0A-E3A424585875</string>
				</dict>
			</array>
			<key>Size</key>
			<integer>42948853248</integer>
		</dict>
	</array>
	<key>VolumesFromDisks</key>
	<array>
		<string>OSX</string>
	</array>
	<key>WholeDisks</key>
	<array>
		<string>disk0</string>
	</array>
</dict>
</plist>"""

def ReturnFakeDiskutilInfoBadDisk0Plist():
    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Bootable</key>
	<false/>
	<key>CanBeMadeBootable</key>
	<false/>
	<key>CanBeMadeBootableRequiresDestroy</key>
	<false/>
	<key>Content</key>
	<string>GUID_partition_scheme</string>
	<key>DeviceIdentifier</key>
	<string>disk0</string>
	<key>DeviceNode</key>
	<string>/dev/disk0</string>
	<key>DeviceTreePath</key>
	<string>IODeviceTree:/PCI0@1e0000/pci8086,2829@1F,2/PRT0@0/PMP@0</string>
	<key>Ejectable</key>
	<false/>
	<key>EjectableMediaAutomaticUnderSoftwareControl</key>
	<false/>
	<key>EjectableOnly</key>
	<false/>
	<key>FreeSpace</key>
	<integer>0</integer>
	<key>GlobalPermissionsEnabled</key>
	<false/>
	<key>IOKitSize</key>
	<integer>42948853248</integer>
	<key>IORegistryEntryName</key>
	<string>VBOX HARDDISK Media</string>
	<key>LowLevelFormatSupported</key>
	<false/>
	<key>MediaType</key>
	<string>Generic</string>
	<key>MountPoint</key>
	<string></string>
	<key>OS9DriversInstalled</key>
	<false/>
	<key>ParentWholeDisk</key>
	<string>disk0</string>
	<key>RAIDMaster</key>
	<false/>
	<key>RAIDSlice</key>
	<false/>
	<key>Removable</key>
	<false/>
	<key>RemovableMedia</key>
	<false/>
	<key>RemovableMediaOrExternalDevice</key>
	<false/>
	<key>SMARTStatus</key>
	<string>Not Supported</string>
	<key>Size</key>
	<integer>42948853248</integer>
	<key>SupportsGlobalPermissionsDisable</key>
	<false/>
	<key>SystemImage</key>
	<false/>
	<key>VirtualOrPhysical</key>
	<string>Physical</string>
	<key>VolumeName</key>
	<string></string>
	<key>VolumeSize</key>
	<integer>0</integer>
	<key>WholeDisk</key>
	<true/>
	<key>Writable</key>
	<true/>
	<key>WritableMedia</key>
	<true/>
	<key>WritableVolume</key>
	<false/>
</dict>
</plist>"""

def ReturnFakeDiskutilInfoDisk0Plist():
    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Bootable</key>
	<false/>
	<key>BusProtocol</key>
	<string>SATA</string>
	<key>CanBeMadeBootable</key>
	<false/>
	<key>CanBeMadeBootableRequiresDestroy</key>
	<false/>
	<key>Content</key>
	<string>GUID_partition_scheme</string>
	<key>DeviceBlockSize</key>
	<integer>512</integer>
	<key>DeviceIdentifier</key>
	<string>disk0</string>
	<key>DeviceNode</key>
	<string>/dev/disk0</string>
	<key>DeviceTreePath</key>
	<string>IODeviceTree:/PCI0@1e0000/pci8086,2829@1F,2/PRT0@0/PMP@0</string>
	<key>Ejectable</key>
	<false/>
	<key>EjectableMediaAutomaticUnderSoftwareControl</key>
	<false/>
	<key>EjectableOnly</key>
	<false/>
	<key>FreeSpace</key>
	<integer>0</integer>
	<key>GlobalPermissionsEnabled</key>
	<false/>
	<key>IOKitSize</key>
	<integer>42948853248</integer>
	<key>IORegistryEntryName</key>
	<string>VBOX HARDDISK Media</string>
	<key>Internal</key>
	<true/>
	<key>LowLevelFormatSupported</key>
	<false/>
	<key>MediaName</key>
	<string>VBOX HARDDISK</string>
	<key>MediaType</key>
	<string>Generic</string>
	<key>MountPoint</key>
	<string></string>
	<key>OS9DriversInstalled</key>
	<false/>
	<key>ParentWholeDisk</key>
	<string>disk0</string>
	<key>RAIDMaster</key>
	<false/>
	<key>RAIDSlice</key>
	<false/>
	<key>Removable</key>
	<false/>
	<key>RemovableMedia</key>
	<false/>
	<key>RemovableMediaOrExternalDevice</key>
	<false/>
	<key>SMARTStatus</key>
	<string>Not Supported</string>
	<key>Size</key>
	<integer>42948853248</integer>
	<key>SolidState</key>
	<false/>
	<key>SupportsGlobalPermissionsDisable</key>
	<false/>
	<key>SystemImage</key>
	<false/>
	<key>TotalSize</key>
	<integer>42948853248</integer>
	<key>VirtualOrPhysical</key>
	<string>Physical</string>
	<key>VolumeName</key>
	<string></string>
	<key>VolumeSize</key>
	<integer>0</integer>
	<key>WholeDisk</key>
	<true/>
	<key>Writable</key>
	<true/>
	<key>WritableMedia</key>
	<true/>
	<key>WritableVolume</key>
	<false/>
</dict>
</plist>"""

def ReturnFakeDiskutilInfoDisk0s1Plist():
    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Bootable</key>
	<false/>
	<key>BusProtocol</key>
	<string>SATA</string>
	<key>CanBeMadeBootable</key>
	<false/>
	<key>CanBeMadeBootableRequiresDestroy</key>
	<false/>
	<key>Content</key>
	<string>EFI</string>
	<key>VolumeBlockSize</key>
	<integer>1024</integer>
	<key>DeviceIdentifier</key>
	<string>disk0s1</string>
	<key>DeviceNode</key>
	<string>/dev/disk0s1</string>
	<key>DeviceTreePath</key>
	<string>IODeviceTree:/PCI0@1e0000/pci8086,2829@1F,2/PRT0@0/PMP@0</string>
	<key>DiskUUID</key>
	<string>A0C85363-E33F-4708-9B6A-68BD0AA062C1</string>
	<key>Ejectable</key>
	<false/>
	<key>EjectableMediaAutomaticUnderSoftwareControl</key>
	<false/>
	<key>EjectableOnly</key>
	<false/>
	<key>FreeSpace</key>
	<integer>0</integer>
	<key>GlobalPermissionsEnabled</key>
	<false/>
	<key>IOKitSize</key>
	<integer>209715200</integer>
	<key>IORegistryEntryName</key>
	<string>EFI System Partition</string>
	<key>Internal</key>
	<true/>
	<key>MediaName</key>
	<string></string>
	<key>MediaType</key>
	<string>Generic</string>
	<key>MountPoint</key>
	<string></string>
	<key>ParentWholeDisk</key>
	<string>disk0</string>
	<key>RAIDMaster</key>
	<false/>
	<key>RAIDSlice</key>
	<false/>
	<key>Removable</key>
	<false/>
	<key>RemovableMedia</key>
	<false/>
	<key>RemovableMediaOrExternalDevice</key>
	<false/>
	<key>SMARTStatus</key>
	<string>Not Supported</string>
	<key>Size</key>
	<integer>209715200</integer>
	<key>SolidState</key>
	<false/>
	<key>SupportsGlobalPermissionsDisable</key>
	<false/>
	<key>SystemImage</key>
	<false/>
	<key>TotalSize</key>
	<integer>209715200</integer>
	<key>VolumeName</key>
	<string>EFI</string>
	<key>VolumeSize</key>
	<integer>0</integer>
	<key>VolumeUUID</key>
	<string>85D67001-D93E-3687-A1C2-79D677F0C2E0</string>
	<key>WholeDisk</key>
	<false/>
	<key>Writable</key>
	<true/>
	<key>WritableMedia</key>
	<true/>
	<key>WritableVolume</key>
	<false/>
</dict>
</plist>"""

def ReturnFakeDiskutilInfoDisk0s2Plist():
    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Bootable</key>
	<true/>
	<key>BusProtocol</key>
	<string>SATA</string>
	<key>CanBeMadeBootable</key>
	<false/>
	<key>CanBeMadeBootableRequiresDestroy</key>
	<false/>
	<key>Content</key>
	<string>Apple_HFS</string>
	<key>DeviceBlockSize</key>
	<integer>2048</integer>
	<key>DeviceIdentifier</key>
	<string>disk0s2</string>
	<key>DeviceNode</key>
	<string>/dev/disk0s2</string>
	<key>DeviceTreePath</key>
	<string>IODeviceTree:/PCI0@1e0000/pci8086,2829@1F,2/PRT0@0/PMP@0</string>
	<key>DiskUUID</key>
	<string>72914C17-6469-457F-B2F0-26BE5BD03843</string>
	<key>Ejectable</key>
	<false/>
	<key>EjectableMediaAutomaticUnderSoftwareControl</key>
	<false/>
	<key>EjectableOnly</key>
	<false/>
	<key>FilesystemName</key>
	<string>Journaled HFS+</string>
	<key>FilesystemType</key>
	<string>hfs</string>
	<key>FilesystemUserVisibleName</key>
	<string>Mac OS Extended (Journaled)</string>
	<key>FreeSpace</key>
	<integer>18913898496</integer>
	<key>GlobalPermissionsEnabled</key>
	<true/>
	<key>IOKitSize</key>
	<integer>42089095168</integer>
	<key>IORegistryEntryName</key>
	<string>OSX</string>
	<key>Internal</key>
	<true/>
	<key>JournalOffset</key>
	<integer>1310720</integer>
	<key>JournalSize</key>
	<integer>8388608</integer>
	<key>MediaName</key>
	<string></string>
	<key>MediaType</key>
	<string>Generic</string>
	<key>MountPoint</key>
	<string>/</string>
	<key>ParentWholeDisk</key>
	<string>disk0</string>
	<key>RAIDMaster</key>
	<false/>
	<key>RAIDSlice</key>
	<false/>
	<key>RecoveryDeviceIdentifier</key>
	<string>disk0s3</string>
	<key>Removable</key>
	<false/>
	<key>RemovableMedia</key>
	<false/>
	<key>RemovableMediaOrExternalDevice</key>
	<false/>
	<key>SMARTStatus</key>
	<string>Not Supported</string>
	<key>Size</key>
	<integer>42089095168</integer>
	<key>SolidState</key>
	<false/>
	<key>SupportsGlobalPermissionsDisable</key>
	<true/>
	<key>SystemImage</key>
	<false/>
	<key>TotalSize</key>
	<integer>42089095168</integer>
	<key>VolumeAllocationBlockSize</key>
	<integer>4096</integer>
	<key>VolumeName</key>
	<string>OSX</string>
	<key>VolumeSize</key>
	<integer>42089095168</integer>
	<key>VolumeUUID</key>
	<string>AC723754-135E-39BE-8A81-C91228501E9B</string>
	<key>WholeDisk</key>
	<false/>
	<key>Writable</key>
	<true/>
	<key>WritableMedia</key>
	<true/>
	<key>WritableVolume</key>
	<true/>
</dict>
</plist>"""

def ReturnFakeDiskutilInfoDisk0s3Plist():
    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Bootable</key>
	<true/>
	<key>BusProtocol</key>
	<string>SATA</string>
	<key>CanBeMadeBootable</key>
	<false/>
	<key>CanBeMadeBootableRequiresDestroy</key>
	<false/>
	<key>Content</key>
	<string>Apple_Boot</string>
	<key>DeviceBlockSize</key>
	<integer>4096</integer>
	<key>DeviceIdentifier</key>
	<string>disk0s3</string>
	<key>DeviceNode</key>
	<string>/dev/disk0s3</string>
	<key>DeviceTreePath</key>
	<string>IODeviceTree:/PCI0@1e0000/pci8086,2829@1F,2/PRT0@0/PMP@0</string>
	<key>DiskUUID</key>
	<string>353F6CFF-8E9C-4480-BC8B-D6357E15299E</string>
	<key>Ejectable</key>
	<false/>
	<key>EjectableMediaAutomaticUnderSoftwareControl</key>
	<false/>
	<key>EjectableOnly</key>
	<false/>
	<key>FreeSpace</key>
	<integer>0</integer>
	<key>GlobalPermissionsEnabled</key>
	<false/>
	<key>IOKitSize</key>
	<integer>650002432</integer>
	<key>IORegistryEntryName</key>
	<string>Recovery HD</string>
	<key>Internal</key>
	<true/>
	<key>MediaName</key>
	<string></string>
	<key>MediaType</key>
	<string>Generic</string>
	<key>MountPoint</key>
	<string></string>
	<key>ParentWholeDisk</key>
	<string>disk0</string>
	<key>RAIDMaster</key>
	<false/>
	<key>RAIDSlice</key>
	<false/>
	<key>Removable</key>
	<false/>
	<key>RemovableMedia</key>
	<false/>
	<key>RemovableMediaOrExternalDevice</key>
	<false/>
	<key>SMARTStatus</key>
	<string>Not Supported</string>
	<key>Size</key>
	<integer>650002432</integer>
	<key>SolidState</key>
	<false/>
	<key>SupportsGlobalPermissionsDisable</key>
	<false/>
	<key>SystemImage</key>
	<false/>
	<key>TotalSize</key>
	<integer>650002432</integer>
	<key>VolumeName</key>
	<string>Recovery HD</string>
	<key>VolumeSize</key>
	<integer>0</integer>
	<key>VolumeUUID</key>
	<string>F1573C36-EC30-3501-8E0A-E3A424585875</string>
	<key>WholeDisk</key>
	<false/>
	<key>Writable</key>
	<true/>
	<key>WritableMedia</key>
	<true/>
	<key>WritableVolume</key>
	<false/>
</dict>
</plist>"""

def ReturnFakeLVMOutput():
    return """  --- Logical volume ---
  LV Path                /dev/fakefedora/swap
  LV Name                swap
  VG Name                fakefedora
  LV UUID                3e8urm-xsCG-iCAJ-Q3go-2247-OU5N-3AwlD1
  LV Write Access        read/write
  LV Creation host, time localhost-live, 2016-12-22 19:49:26 +0000
  LV Status              available
  # open                 2
  LV Size                1.60 GiB
  Current LE             410
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:1
   
  --- Segments ---
  Logical extents 0 to 409:
    Type		linear
    Physical volume	/dev/sda3
    Physical extents	0 to 409
   
   
  --- Logical volume ---
  LV Path                /dev/fakefedora/root
  LV Name                root
  VG Name                fakefedora
  LV UUID                TWxt1j-g62o-GYju-3UpB-A4g3-9ZbB-HWb7jf
  LV Write Access        read/write
  LV Creation host, time localhost-live, 2016-12-22 19:49:26 +0000
  LV Status              available
  # open                 1
  LV Size                13.20 GiB
  Current LE             3379
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     256
  Block device           253:0
   
  --- Segments ---
  Logical extents 0 to 3378:
    Type		linear
    Physical volume	/dev/sda3
    Physical extents	410 to 3788
   
   """.split("\n")

def ReturnFakeBlockDevOutput():
    return ["No such file or device", "512", "1024", "2048", "4096", "8192"]
