#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Device Information Obtainer for WxFixBoot Version 2.0~pre1
# This file is part of WxFixBoot.
# Copyright (C) 2013-2016 Hamish McIntyre-Bhatty
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

#Begin Main Class. #*** Refactor and test again ***
class Main():
    def FoundExactMatch(self, Item, Text, Log=True):
        """Check if an exact match of "Item" (arg) can be found in "Text" (arg), seperated by commas or spaces."""
        if Log == True:
            logger.debug("GetDevInfo: Main().FoundExactMatch(): Looking for: "+Item+" in: "+Text+"...")

        Result = re.findall('\\'+Item+'\\b', Text)

        if len(Result) > 0:
            Result = True

        else:
            Result = False

        if Log == True:
            logger.info("GetDevInfo: Main().FoundExactMatch(): Result: "+str(Result)+"...")

        return Result

    def IsPartition(self, Disk, DiskInfo=None): #*** Is this needed any more? ***
        """Check if the given Disk is a partition"""
        if Disk[0:7] not in ["/dev/sr", "/dev/fd"] and Disk[-1].isdigit() and Disk[0:8] in DiskInfo:
            Result = True

        else:
            Result = False

        logger.info("GetDevInfo: Main().IsPartition(): "+Disk+" is a partition: "+str(Result)+"...")
        return Result

    def DeduplicateList(self, ListToDeduplicate): #*** Might not need this ***
        """Deduplicate the given list."""
        logger.debug("GetDevInfo: Main().DeduplicateList(): Deduplicating list: "+str(ListToDeduplicate)+"...")
        ResultsList = []

        for Element in ListToDeduplicate:
            if Element not in ResultsList:
                ResultsList.append(Element)

        #Return the results.
        logger.info("GetDevInfo: Main().DeduplicateList(): Results: "+str(ResultsList)+"...")
        return ResultsList

    def GetUUID(self, Disk):
        """Get the given partition's UUID""" #*** Test this again ***
        UUID = "Unknown"

        #Try to get the UUID from blkid's output.
        for Line in self.BlkidOutput.split('\n'):
            if Disk in Line:
                UUID = Line.split()[-1]
                break

        if UUID != "Unknown":
            logger.info("GetDevInfo: Main().GetUUID(): Found UUID ("+UUID+") for: "+Disk+"...")

        else:
            logger.warning("GetDevInfo: Main().GetUUID(): Couldn't find UUID for: "+Disk+"! This may cause problems down the line.")

        return UUID

    def GetID(self, Disk): #*** Test this again ***
        """Retrive the given partition's/device's ID."""
        logger.info("GetDevInfo: Main().GetID(): Getting ID for: "+Disk+"...")

        ID = "Unknown"

        #Try to get the ID from ls's output.
        for Line in self.LsOutput.split('\n'):
            try:
                SplitLine = Line.split()

                if "../../"+Disk.split('/')[-1] == SplitLine[-1]:
                    ID = SplitLine[-3]
                    break

            except:
                pass

        if ID != "Unknown":
            logger.info("GetDevInfo: Main().GetID(): Found ID ("+ID+") for: "+Disk+"...")

        else:
            logger.warning("GetDevInfo: Main().GetID(): Couldn't find ID for: "+Disk+"! This may cause problems down the line.")

        return ID

    def GetInfo(self, Standalone=False): #*** Test this *** *** Doesn't detect logical partitions ***
        """Get Disk Information."""
        logger.info("GetDevInfo: Main().GetInfo(): Preparing to get Disk info...")

        #Run lshw to try and get disk information.
        logger.debug("GetDevInfo: Main().GetInfo(): Running 'lshw -sanitize -class disk -class volume -xml'...")
        runcmd = subprocess.Popen("LC_ALL=C lshw -sanitize -class disk -class volume -xml", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        #Get the output.
        stdout, stderr = runcmd.communicate()

        if Standalone:
            global DiskInfo
            DiskInfo = {}

        #Save some info for later use.
        #UUIDs.
        cmd = subprocess.Popen("blkid -o list", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        self.BlkidOutput = cmd.communicate()[0]

        #IDs.
        cmd = subprocess.Popen("ls -l /dev/disk/by-id/", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        self.LsOutput = cmd.communicate()[0]

        logger.debug("GetDevInfo: Main().GetInfo(): Done.")

        self.Output = BeautifulSoup(stdout, "xml")

        #Find the disks.
        for Node in self.Output.list.children:
            if unicode(type(Node)) != "<class 'bs4.element.Tag'>":
                continue

            #These are devices.
            HostDisk = unicode(Node.logicalname.string)
            DiskInfo[HostDisk] = {}
            DiskInfo[HostDisk]["Name"] = HostDisk
            DiskInfo[HostDisk]["Type"] = "Device"
            DiskInfo[HostDisk]["HostDevice"] = "N/A"
            DiskInfo[HostDisk]["Partitions"] = []

            try:
                DiskInfo[HostDisk]["Vendor"] = unicode(Node.vendor.string)

            except AttributeError:
                DiskInfo[HostDisk]["Vendor"] = "Unknown"

            try:
                DiskInfo[HostDisk]["Product"] = unicode(Node.product.string)

            except AttributeError:
                DiskInfo[HostDisk]["Product"] = "Unknown"

            try:
                DiskInfo[HostDisk]["RawCapacity"] = unicode(Node.size.string)

            except AttributeError:
                try:
                    DiskInfo[HostDisk]["RawCapacity"] = unicode(Node.capacity.string)

                except AttributeError:
                    DiskInfo[HostDisk]["RawCapacity"] = "Unknown"

            #Round the sizes to make them human-readable.
            UnitList = [None, "B", "KB", "MB", "GB", "TB", "PB"]
            Unit = "B"

            #Catch an error in case Size is unknown.
            try:
                HumanSize = int(DiskInfo[HostDisk]["RawCapacity"])

            except ValueError:
                DiskInfo[HostDisk]["Capacity"] = DiskInfo[HostDisk]["RawCapacity"]

            else:
                while len(unicode(HumanSize)) > 3:
                    #Shift up one unit.
                    Unit = UnitList[UnitList.index(Unit)+1]
                    HumanSize = HumanSize//1000

                #Include the unit in the result for both exact and human-readable sizes.
                DiskInfo[HostDisk]["Capacity"] = unicode(HumanSize)+" "+Unit

            DiskInfo[HostDisk]["Description"] = unicode(Node.description.string)
            DiskInfo[HostDisk]["Flags"] = []

            for Capability in Node.capabilities.children:
                if unicode(type(Capability)) != "<class 'bs4.element.Tag'>" or Capability.name != "capability":
                    continue

                DiskInfo[HostDisk]["Flags"].append(Capability["id"])

            DiskInfo[HostDisk]["Partitioning"] = DiskInfo[HostDisk]["Flags"][-1].split(":")[-1]

            if DiskInfo[HostDisk]["Partitioning"] in ("gpt", "dos"):
                if DiskInfo[HostDisk]["Partitioning"] == "dos":
                    DiskInfo[HostDisk]["Partitioning"] = "mbr"

            else:
                DiskInfo[HostDisk]["Partitioning"] = "Unknown"

            DiskInfo[HostDisk]["FileSystem"] = "N/A"
            DiskInfo[HostDisk]["UUID"] = "N/A"
            DiskInfo[HostDisk]["ID"] = self.GetID(HostDisk)

            #Get the info of any partitions these devices contain.
            for SubNode in Node.children:
                if unicode(type(SubNode)) != "<class 'bs4.element.Tag'>" or SubNode.name != "node":
                    continue

                try:
                    Volume = unicode(SubNode.logicalname.string)

                except AttributeError:
                    Volume = HostDisk+unicode(SubNode.physid.string)

                DiskInfo[Volume] = {}
                DiskInfo[Volume]["Name"] = Volume
                DiskInfo[Volume]["Type"] = "Partition"
                DiskInfo[Volume]["HostDevice"] = HostDisk
                DiskInfo[Volume]["Partitions"] = []
                DiskInfo[HostDisk]["Partitions"].append(Volume)

                try:
                    DiskInfo[Volume]["Vendor"] = unicode(SubNode.vendor.string)

                except AttributeError:
                    DiskInfo[Volume]["Vendor"] = "Unknown"

                DiskInfo[Volume]["Product"] = "Host Device: "+DiskInfo[HostDisk]["Product"]

                try:
                    DiskInfo[Volume]["RawCapacity"] = unicode(SubNode.size.string)

                except AttributeError:
                    try:
                        DiskInfo[Volume]["RawCapacity"] = unicode(SubNode.capacity.string)

                    except AttributeError:
                        DiskInfo[Volume]["RawCapacity"] = "Unknown"

                #Round the sizes to make them human-readable.
                UnitList = [None, "B", "KB", "MB", "GB", "TB", "PB"]
                Unit = "B"

                #Catch an error in case Size is unknown.
                try:
                    HumanSize = int(DiskInfo[Volume]["RawCapacity"])

                except ValueError:
                    DiskInfo[Volume]["Capacity"] = DiskInfo[Volume]["RawCapacity"]

                else:
                    while len(unicode(HumanSize)) > 3:
                        #Shift up one unit.
                        Unit = UnitList[UnitList.index(Unit)+1]
                        HumanSize = HumanSize//1000

                    #Include the unit in the result for both exact and human-readable sizes.
                    DiskInfo[Volume]["Capacity"] = unicode(HumanSize)+" "+Unit

                DiskInfo[Volume]["Description"] = unicode(SubNode.description.string)
                DiskInfo[Volume]["Flags"] = []

                for Capability in SubNode.capabilities.children:
                    if unicode(type(Capability)) != "<class 'bs4.element.Tag'>" or Capability.name != "capability":
                        continue

                    DiskInfo[Volume]["Flags"].append(Capability["id"])

                DiskInfo[Volume]["FileSystem"] = "Unknown"

                for Config in SubNode.configuration.children:
                    if unicode(type(Config)) != "<class 'bs4.element.Tag'>" or Config.name != "setting":
                        continue

                    if Config["id"] == "filesystem":
                        DiskInfo[Volume]["FileSystem"] = unicode(Config["value"])

                        #Use different terminology where wanted.
                        if DiskInfo[Volume]["FileSystem"] == "fat":
                            DiskInfo[Volume]["FileSystem"] = "vfat"

                        break

                DiskInfo[Volume]["Partitioning"] = "N/A"
                DiskInfo[Volume]["UUID"] = self.GetUUID(Volume)
                DiskInfo[Volume]["ID"] = self.GetID(Volume)

        logger.info("GetDevInfo: Main().GetInfo(): Finished!")

    def GetBlockSize(self, Disk): #*** Is this needed in wxfixboot? ***
        """Find the given Disk's blocksize, and return it"""
        logger.debug("GetDevInfo: Main().GetBlockSize(): Finding blocksize for Disk: "+Disk+"...")

        #Run /sbin/blockdev to try and get blocksize information.
        logger.debug("GetDevInfo: Main().GetBlockSize(): Running 'blockdev --getpbsz "+Disk+"'...")
        runcmd = subprocess.Popen("blockdev --getpbsz "+Disk, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        #Get the output.
        stdout, stderr = runcmd.communicate()

        Result = stdout.replace('\n', '')

        #Check it worked (it should be convertable to an integer if it did).
        try:
            tmp = int(Result)

        except ValueError:
            #It didn't, this is probably a file, not a Disk.
            logger.warning("GetDevInfo: Main().GetBlockSize(): Couldn't get blocksize for Disk: "+Disk+"! Returning None...")
            return None

        else:
            #It did.
            logger.info("GetDevInfo: Main().GetBlockSize(): Blocksize for Disk: "+Disk+": "+Result+". Returning it...")
            return Result

#End Main Class.

if __name__ == "__main__":
    #Import modules.
    import subprocess
    import re
    import logging
    from bs4 import BeautifulSoup

    #Set up basic logging to stdout.
    logger = logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)

    Main().GetInfo(Standalone=True)

    #Get blocksizes.
    for Disk in DiskInfo:
        DiskInfo[Disk]["PhysicalBlockSize"] = Main().GetBlockSize(Disk)

    #Print the info in a (semi :D) readable way.
    Keys = DiskInfo.keys()
    Keys.sort()

    for Key in Keys:
        print("\n\n", DiskInfo[Key], "\n\n")
