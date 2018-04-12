#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Essential Backend Tools in the BackendTools Package for WxFixBoot Version 2.0.3
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

#Begin Main Class.
class Main():
    def CheckInternetConnection(self):
        """Check the internet connection."""
        DialogTools.ShowMsgDlg(Kind="info", Message="Your internet connection will now be tested to ensure it's safe to do bootloader operations. This will be done by pinging the OpenDNS DNS servers.")
        Retry = True

        logger.info("EssentialBackendTools: Main().CheckInternetConnection(): Checking the Internet Connection...")
        SystemInfo["DisableBootloaderOperations"] = False

        while True:
            #Test the internet connection by pinging an OpenDNS DNS server.
            PacketLoss = "100%"

            logger.debug("EssentialBackendTools: Main().CheckInternetConnection(): Running 'ping -c 5 -i 0.5 208.67.222.222'...")
            Retval, Output = CoreTools.StartProcess("ping -c 5 -i 0.5 208.67.222.222", ShowOutput=False, ReturnOutput=True)

            if Retval != 0:
                #This errored for some reason. Probably no internet connection.
                logger.error("EssentialBackendTools: Main().CheckInternetConnection(): Command errored!")
                PacketLoss = "100%"

            else:
                #Get the % packet loss.
                for Line in Output.split("\n"):
                    if 'packet loss' in Line:
                        PacketLoss = Line.split()[-5]

            if PacketLoss == "0%":
                #Good! We have a reliable internet connection.
                logger.info("EssentialBackendTools: Main().CheckInternetConnection(): Internet Connection Test Succeeded!")
                break

            else:
                #Uh oh! We DON'T have a reliable internet connection! Ask the user to either try again, or skip Bootloader operations.
                logger.error("EssentialBackendTools: Main().CheckInternetConnection(): Internet Connection test failed! Asking user to try again or disable bootloader operations...")
                Result = DialogTools.ShowYesNoDlg(Message="Your Internet Connection failed the test! Without a working internet connection, you cannot perform bootloader operations. Click yes to try again, and click no to give up and skip bootloader operations.", Title="WxFixBoot - Disable Bootloader Operations?", Buttons=("Try again", "Cancel Bootloader Operations"))

                if Result == False:
                    logger.warning("EssentialBackendTools: Main().CheckInternetConnection(): Disabling bootloader operations due to bad internet connection...")
                    SystemInfo["DisableBootloaderOperations"] = True
                    SystemInfo["DisableBootloaderOperationsBecause"].append("Internet Connection test failed.")
                    break

                else:
                    #We'll just run the loop again
                    logger.info("EssentialBackendTools: Main().CheckInternetConnection(): Testing the internet connection again...")
                    pass

    def FileSystemCheck(self, Type):
        """Quickly check all filesystems."""
        logger.debug("EssentialBackendTools: Main().FileSystemCheck(): Starting...")

        #Update Current Operation Text.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing for Filesystem Check...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 10)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to do the Filesystem Check...###\n")

        #Determine which Disks are to be checked.
        FileSystemsToCheck = HelperBackendTools.FindCheckableFileSystems()
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 30)

        #Find the length of the list (this is needed to update the progressbars).
        FileSystemsToCheckLength = len(FileSystemsToCheck)
        Checked = 0

        DialogTools.ShowMsgDlg(Kind="info", Message="WxFixBoot will now perform the disk check. You may wish to open the terminal output box to view the progress of the disk checks.")

        #Run the check on the checkable Disks
        for Disk in FileSystemsToCheck:
            #Gather info.
            logger.info("EssentialBackendTools: Main().FileSystemCheck():: Checking "+Disk+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Checking Disk: "+Disk+"###\n")
            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Checking Disk: "+Disk)
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 30+((50//FileSystemsToCheckLength)*(Checked+1)))
            RunBadBlocks = False

            #Create a command list that will work based on the fstype of this Disk and the type of check we're performing. If there aren't any use cases for the fstype, display a message to the user and skip it.
            if Type == "Quick":
                if DiskInfo[Disk]["FileSystem"] == "jfs":
                    ExecCmds = "fsck.jfs -vf "+Disk

                elif DiskInfo[Disk]["FileSystem"] == "minix":
                    ExecCmds = "fsck.minix -avf "+Disk

                elif DiskInfo[Disk]["FileSystem"] == "reiserfs":
                    ExecCmds = "fsck.reiserfs -apf "+Disk

                elif DiskInfo[Disk]["FileSystem"] == "xfs":
                    ExecCmds = "xfs_repair -Pvd "+Disk

                elif DiskInfo[Disk]["FileSystem"] == "vfat":
                    ExecCmds = "fsck.vfat -yv "+Disk

                elif DiskInfo[Disk]["FileSystem"] in ('ext2', 'ext3', 'ext4', 'ext4dev'):
                    ExecCmds = "fsck."+DiskInfo[Disk]["FileSystem"]+" -yvf "+Disk

                else:
                    ExecCmds = ""
                    logger.warning("EssentialBackendTools: Main().FileSystemCheck(): Skipping Disk: "+Disk+", as WxFixBoot doesn't support checking it yet...")
                    DialogTools.ShowMsgDlg(Kind="error", Message="The filesystem on Disk: "+Disk+" could not be checked, as WxFixBoot doesn't support checking it yet. "+Disk+" will now be skipped.")

            else:
                #For disks that doesn't do bad sector checks with the normal FS checker, run badblocks manually on them.
                if DiskInfo[Disk]["FileSystem"] == "jfs":
                    ExecCmds = "fsck.jfs -vf "+Disk
                    RunBadBlocks = True

                elif DiskInfo[Disk]["FileSystem"] == "minix":
                    ExecCmds = "fsck.minix -avf "+Disk
                    RunBadBlocks = True

                elif DiskInfo[Disk]["FileSystem"] == "reiserfs":
                    ExecCmds = "fsck.reiserfs -apf "+Disk
                    RunBadBlocks = True

                elif DiskInfo[Disk]["FileSystem"] == "xfs":
                    ExecCmds = "xfs_repair -Pvd "+Disk
                    RunBadBlocks = True

                elif DiskInfo[Disk]["FileSystem"] == "vfat":
                    ExecCmds = "fsck.vfat -yvt "+Disk

                elif DiskInfo[Disk]["FileSystem"] in ('ext2', 'ext3', 'ext4', 'ext4dev'):
                    ExecCmds = "fsck."+DiskInfo[Disk]["FileSystem"]+" -yvcf "+Disk

                else:
                    ExecCmds = ""
                    DialogTools.ShowMsgDlg(Kind="info", Message="The filesystem on Disk: "+Disk+" could not be checked, as WxFixBoot doesn't support checking it yet. "+Disk+" will now be skipped.")

            #Run the command, and remount the Disk if needed.
            if ExecCmds != "":
                retval = CoreTools.StartProcess(ExecCmds)

                #Check the return values, and run the handler if needed.
                if retval == 0:
                    #Success.
                    logger.info("EssentialBackendTools: Main().FileSystemCheck(): Checked Disk: "+Disk+". No Errors Found!")

                else:
                    HelperBackendTools.HandleFilesystemCheckReturnValues(ExecCmds=ExecCmds, Retval=retval, Partition=Disk)

            #Run bad blocks if requested.
            if RunBadBlocks:
                Retval = CoreTools.StartProcess("badblocks -sv "+Disk)

                #Check the return values, and run the handler if needed.
                if retval == 0:
                    #Success.
                    logger.info("EssentialBackendTools: Main().FileSystemCheck(): Checked Disk: "+Disk+" for bad sectors. No Errors Found!")

                else:
                    HelperBackendTools.HandleFilesystemCheckReturnValues(ExecCmds="badblocks -sv "+Disk, Retval=retval, Partition=Disk)

            if FileSystemsToCheck[Disk]["Remount"]:
                logger.debug("EssentialBackendTools: Main().FileSystemCheck(): Remounting Disk: "+Disk+" Read-Write...")
                Retval = CoreTools.MountPartition(Partition=Disk, MountPoint=FileSystemsToCheck[Disk]["MountPoint"])

                if Retval != 0:
                    logger.warning("EssentialBackendTools: Main().FileSystemCheck(): Failed to remount "+Disk+" after check. We probably need to reboot first. Never mind...")

            Checked += 1

        #Update Current Operation Text.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Filesystem Check!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished Filesystem Check!###\n")

#End Main Class.
