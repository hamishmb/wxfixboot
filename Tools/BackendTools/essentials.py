#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Essential Backend Tools in the BackendTools Package for WxFixBoot Version 2.0~pre3
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

#Begin Main Class.
class Main(): #*** These need refactoring ***
    def CheckInternetConnection(self):
        """Check the internet connection."""
        DialogTools.ShowMsgDlg(Kind="info", Message="Your internet connection will now be tested to ensure it's safe to do bootloader operations. This will be done by pinging the OpenDNS DNS servers.")
        Retry = True

        logger.info("EssentialBackendTools: Main().CheckInternetConnection(): Checking the Internet Connection...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Checking the Internet Connection...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Checking the Internet Connection...###\n")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 5)
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
                for Line in Output:
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
                    break

                else:
                    #We'll just run the loop again
                    logger.info("EssentialBackendTools: Main().CheckInternetConnection(): Testing the internet connection again...")
                    pass

    def FileSystemCheck(self, Type): #*** Will need lots of work when we switch to dictionaries ***
        """Quickly check all filesystems."""
        logger.debug("EssentialBackendTools: Main().FileSystemCheck(): Starting...")

        #Update Current Operation Text.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing for Filesystem Check...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 10)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to do the Filesystem Check...###\n")

        #Determine which partitions are to be checked.
        CheckList = HelperBackendTools.FindCheckableFileSystems()
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 30)

        #Find the length of the list (this is needed to update the progressbars).
        CheckListLength = len(CheckList)

        DialogTools.ShowMsgDlg(Kind="info", Message="WxFixBoot will now perform the disk check. You may wish to open the terminal output box to view the progress of the disk checks.")

        #Run the check on the checkable partitions
        for Element in CheckList:
            #Gather info. *** Do it a different way? Dictionary? ***
            SplitElement = Element.split()
            Partition = SplitElement[0]
            FSType = SplitElement[1]
            RemountPartitionAfter = SplitElement[2]

            logger.info("EssentialBackendTools: Main().FileSystemCheck():: Checking Partition: "+Partition+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Checking Partition: "+Partition+"###\n")
            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Checking Partition: "+Partition)
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 30+((50//CheckListLength)*(CheckList.index(Element)+1)))

            #Create a command list that will work based on the fstype of this partition and the type of check we're performing. If there aren't any use cases for the fstype, display a message to the user and skip it.
            if Type == "Quick":
                if FSType == "jfs":
                    ExecCmds = "fsck.jfs -vf "+Partition

                elif FSType == "minix":
                    ExecCmds = "fsck.minix -avf "+Partition

                elif FSType == "reiserfs":
                    ExecCmds = "fsck.reiserfs -apf "+Partition

                elif FSType == "xfs":
                    ExecCmds = "xfs_repair -Pvd "+Partition

                elif FSType == "vfat":
                    ExecCmds = "fsck.vfat -yv "+Partition

                elif FSType in ('ext2', 'ext3', 'ext4', 'ext4dev'):
                    ExecCmds = "fsck."+FSType+" -yvf "+Partition

                else:
                    ExecCmds = ""
                    logger.warning("EssentialBackendTools: Main().FileSystemCheck(): Skipping Partition: "+Partition+", as WxFixBoot doesn't support checking it yet...")
                    DialogTools.ShowMsgDlg(Kind="error", Message="The filesystem on partition: "+Partition+" could not be checked, as WxFixBoot doesn't support checking it yet. "+Partition+" will now be skipped.")

            else:
                if FSType == "jfs":
                    #No support for bad sector check in jfs. Notify the user and do a normal check instead.
                    DialogTools.ShowMsgDlg(Kind="info", Message="The filesystem type on partition: "+Partition+" (jfs) doesn't support checking for bad sectors. WxFixBoot will perform a normal filesystem check instead.")
                    ExecCmds = "fsck.jfs -vf "+Partition

                elif FSType == "minix":
                    DialogTools.ShowMsgDlg(Kind="info", Message="The filesystem type on partition: "+Partition+" (minix) doesn't support checking for bad sectors. WxFixBoot will perform a normal filesystem check instead.")
                    ExecCmds = "fsck.minix -avf "+Partition

                elif FSType == "reiserfs":
                    DialogTools.ShowMsgDlg(Kind="info", Message="The filesystem type on partition: "+Partition+" (reiserfs) doesn't support checking for bad sectors. WxFixBoot will perform a normal filesystem check instead.")
                    ExecCmds = "fsck.reiserfs -apf "+Partition

                elif FSType == "xfs":
                    DialogTools.ShowMsgDlg(Kind="info", Message="The filesystem type on partition: "+Partition+" (xfs) doesn't support checking for bad sectors. WxFixBoot will perform a normal filesystem check instead.")
                    ExecCmds = "xfs_repair -Pvd "+Partition

                elif FSType == "vfat":
                    ExecCmds = "fsck.vfat -yvt "+Partition

                elif FSType in ('ext2', 'ext3', 'ext4', 'ext4dev'):
                    ExecCmds = "fsck."+FSType+" -yvcf "+Partition

                else:
                    ExecCmds = ""
                    DialogTools.ShowMsgDlg(Kind="info", Message="The filesystem on partition: "+Partition+" could not be checked, as WxFixBoot doesn't support checking it yet. "+Partition+" will now be skipped.")

            #Run the command with Piping = False, if ExecList != ['None'], otherwise do nothing, but do remount the partition if needed.
            if ExecCmds != "":
                retval = CoreTools.StartProcess(ExecCmds)

                #Check the return values, and run the handler if needed.
                if retval == 0:
                    #Success.
                    logger.info("EssentialBackendTools: Main().FileSystemCheck(): Checked partition: "+Partition+". No Errors Found!")

                else:
                    HelperBackendTools.HandleFilesystemCheckReturnValues(ExecCmds=ExecCmds, Retval=retval, Partition=Partition)

            if RemountPartitionAfter == "True":
                logger.debug("EssentialBackendTools: Main().FileSystemCheck(): Remounting Partition: "+Partition+" Read-Write...")
                Retval = CoreTools.MountPartition(Partition=Partition, MountPoint="/tmp/wxfixboot/mountpoints"+Partition)

                if Retval != 0:
                    logger.warning("EssentialBackendTools: Main().FileSystemCheck(): Failed to remount partition: "+Partition+" after check. We probably need to reboot first. Never mind...")

        #Update Current Operation Text.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Filesystem Check!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished Filesystem Check!###\n")

#End Main Class.
