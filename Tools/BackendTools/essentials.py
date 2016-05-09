#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Essential Backend Tools in the BackendTools Package for WxFixBoot Version 2.0~pre1
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

            try:
                logger.debug("EssentialBackendTools: Main().CheckInternetConnection(): Running 'ping -c 5 -i 0.5 208.67.222.222'...")
                Output = CoreTools.StartProcess("ping -c 5 -i 0.5 208.67.222.222", ShowOutput=False, ReturnOutput=True)[1].split("\n")
                #Get the % packet loss.
                for Line in Output:
                    if 'packet loss' in Line:
                        PacketLoss = Line.split()[-5]

            except IndexError:
                #This errored for some reason. Probably no internet connection.
                logger.error("EssentialBackendTools: Main().CheckInternetConnection(): Command errored!")
                PacketLoss = "100%"

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

    def BackupPartitionTable(self): #*** Will need modification when we switch away from the rootdevice model *** *** Can't save partition table backup file variable like this, move to settings window *** *** Handle return values *** *** Reduce duplication with function below ***
        """Backup the partition table."""
        #For GPT disks, backup with sgdisk -b/--backup=<file> <SOURCEDIRVE>.
        #For MBR disks, backup with dd if=/dev/sdX of=<somefile> bs=512 count=1.
        #We need to find RootDevice's partition scheme.
        PartScheme = DiskInfo[SystemInfo["RootDevice"]]["Partitioning"]

        logger.info("EssentialBackendTools: Main().BackupPartitionTable(): Preparing to backup the partition table...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to backup the Partition Table...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to Backup the Partition Table...###\n")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 10)

        if PartScheme == "mbr":
            #Let's backup the MBR, but we need to ask where to back it up first. *** Maybe do this in settings window? ***
            PartitionTableBackupFile = DialogTools.ShowSaveFileDlg(Title="WxFixBoot - Select Partition Table Backup Target File", Wildcard="MBR Backup File (*.mbr)|*.mbr|IMG Image file (*.img)|*.img|All Files/Devices (*)|*")

            #Make sure the backup file always has the correct file extension on it.
            if PartitionTableBackupFile[-4:] != ".mbr":
                PartitionTableBackupFile = PartitionTableBackupFile+".mbr"

            Cmd = "dd if="+SystemInfo["RootDevice"]+" of="+PartitionTableBackupFile+" bs=512 count=1"

        else:
            #Let's backup the GPT, but we need to ask where to back it up first. *** Maybe do this in settings window? ***
            PartitionTableBackupFile = DialogTools.ShowSaveFileDlg(Title="WxFixBoot - Select Partition Table Backup Target File", Wildcard="GPT Backup File (*.gpt)|*.gpt|IMG Image file (*.img)|*.img|All Files/Devices (*)|*")

            #Make sure the backup file always has the correct file extension on it.
            if PartitionTableBackupFile[-4:] != ".gpt":
                PartitionTableBackupFile = PartitionTableBackupFile+".gpt"

            Cmd = "sgdisk --backup="+PartitionTableBackupFile+" "+SystemInfo["RootDevice"]

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Backing up Partition Table...")
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Backing up the Partition Table...###\n")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)

        #Backup the partition table.
        logger.info("EssentialBackendTools: Main().BackupPartitionTable(): Backing up partition table to file: "+PartitionTableBackupFile+", from device: "+SystemInfo["RootDevice"]+"...")
        retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Backing up Partition Table!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished Backing up the Partition Table!###\n")
        logger.info("EssentialBackendTools: Main().BackupPartitionTable(): Finished Backing up Partition Table! Exit code: "+unicode(retval))

    def BackupBootSector(self): #*** Will need lots of modification when we switch away from the rootdevice model *** *** Can't save boot sector backup file variable like this, move to settings window *** *** Reduce duplication *** *** What if we need to backup a PBR? ***
        """Backup the bootsector."""
        #For GPT disks, backup UEFI System Partition.
        #For MBR disks, backup with dd if=/dev/sdX of=<somefile> bs=512 count=1.
        #We need to find RootDevice's partition scheme.
        PartScheme = DiskInfo[SystemInfo["RootDevice"]]["Partitioning"]

        logger.info("EssentialBackendTools: Main().BackupPartitionTable(): Preparing to backup the boot sector...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to backup the Boot Sector...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 10)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to Backup the Boot Sector...###\n")

        if PartScheme == "mbr":
            #Let's backup the MBR, but we need to ask where to back it up first. *** Maybe do this in settings window? ***
            BootSectorBackupFile = DialogTools.ShowSaveFileDlg(Title="WxFixBoot - Select Bootsector Backup Target File", Wildcard="IMG Image file (*.img)|*.img|All Files/Devices (*)|*")

            #Make sure the backup file always has the correct file extension on it.
            if BootSectorBackupFile[-4:] != ".img":
                BootSectorBackupFile = BootSectorBackupFile+".img"

            Cmd = "dd if="+SystemInfo["RootDevice"]+" of="+BootSectorBackupFile+" bs=512 count=1"

        elif SystemInfo["UEFISystemPartition"] != None:
            #We need to ask where to back it up to. *** Maybe do this in settings window? ***
            BootSectorBackupFile = DialogTools.ShowSaveFileDlg(Title="WxFixBoot - Select Bootsector Backup Target File", Wildcard="IMG Image file (*.img)|*.img|All Files/Devices (*)|*")

            #Make sure the backup file always has the correct file extension on it.
            if BootSectorBackupFile[-4:] != ".img":
                BootSectorBackupFile = BootSectorBackupFile+".img"

            Cmd = "dd if="+SystemInfo["UEFISystemPartition"]+" of="+BootSectorBackupFile

        else:
            logger.error("EssentialBackendTools: Main().BackupBootSector(): Failed to backup UEFI Partition, because there isn't one!") #*** What if we're booting GRUB on gpt? ***
            DialogTools.ShowMsgDlg(Kind="error", Message="You have no UEFI Partition, so WxFixBoot couldn't backup your bootsector! Click okay to skip this operation.")
            return

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Backing up the Boot Sector...")
        wx.CallAfter(ParentWindow.UpdateCurrentOutputBox, Message="\n###Backing up the Boot Sector...###\n")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)

        #Backup the boot sector.
        logger.info("EssentialBackendTools: Main().BackupBootSector(): Backing up the boot sector to file: "+BootSectorBackupFile+"...")
        retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Backing up the Boot Sector!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished Backing up the Boot Sector!###\n")
        logger.info("EssentialBackendTools: Main().BackupBootSector(): Finished backing up Boot Sector! Exit code: "+unicode(retval))

    def RestorePartitionTable(self):
        """Restore the partition table.""" #*** Will need lots of modification when switching to dictionaries ***
        #Use sgdisk for GPT disks, restore with sgdisk -l/--load-backup=<file> <TARGETDEVICE>
        #Use dd for MBR disks, restore with dd if=<somefile> of=/dev/sdX bs=1 count=64 skip=446 seek=446
        logger.info("EssentialBackendTools: Main().RestorePartitionTable(): Preparing to restore the Partition Table...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to restore the Partition Table...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 10)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to restore the Partition Table...###\n")

        #We need to check if PartitionTableFile is on a different partition or device, so we can make sure it's available (this is necessary if the user did an FS check) *** Actually I don't think it unmounts anything, just remounts read-only. I will investigate. ***
        if "/mnt/" in PartitionTableFile:
            #It is! Determine which partition we need to mount. *** Does looking for '/mnt/' work? ***
            Temp = PartitionTableFile.split('/')
            PartitionToMount = "/"+'/'.join(Temp[2:4])

            #Mount it, and set a variable so we can unmount it afterwards. *** With that variable, check if it was mounted before, and if so leave it alone! ***
            if CoreTools.MountPartition(Partition=PartitionToMount, MountPoint="/mnt"+PartitionToMount) != 0:
                logger.error("EssentialBackendTools: Main().RestorePartitionTable(): Failed to mount "+PartitionToMount+" at /mnt"+PartitionToMount+"! Continuing anyway...")

            MountedFS = PartitionToMount
            logger.info("EssentialBackendTools: Main().RestorePartitionTable(): Okay. Mounted the partition: "+MountedFS+" that houses the file. Now let's restore the Partition Table...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 35)

        else:
            #Nope, it's on this partition.
            MountedFS = "None"
            logger.info("EssentialBackendTools: Main().RestorePartitionTable(): Okay. Now let's restore the Partition Table...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 35)

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Restoring the Partition Table...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Restoring the Partition Table...###\n")

        if PartitionTableBackupType == "mbr":
            #Let's restore the MBR Partition Table.
            logger.info("EssentialBackendTools: Main().RestorePartitionTable(): Restoring MBR partition table from file: "+PartitionTableFile+" to device: "+PartitionTableTargetDevice+"...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 65)
            retval = CoreTools.StartProcess("dd if="+PartitionTableFile+" of="+PartitionTableTargetDevice+" bs=1 count=64 skip=446 seek=446", ShowOutput=False)

        else:
            #Let's restore the GPT.
            retval = CoreTools.StartProcess("sgdisk --load-backup="+PartitionTableFile+" "+PartitionTableTargetDevice, ShowOutput=False)
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 65)
            logger.info("EssentialBackendTools: Main().RestorePartitionTable(): Restoring GPT partition table from file: "+PartitionTableFile+" to device: "+PartitionTableTargetDevice+"...")

        #Unmount the partition containing the file, if there is one. *** Is this necessary? ***
        if MountedFS != "None":
            logger.info("EssentialBackendTools: Main().RestorePartitionTable(): Unmounting partition: "+MountedFS+"...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 85)
            if CoreTools.Unmount(MountedFS) != 0: 
                logger.error("EssentialBackendTools: Main().RestorePartitionTable(): Failed to unmount "+MountedFS+"! Continuing anyway...")

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Restoring the Partition Table!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished Restoring the Partition Table!###\n")
        logger.info("EssentialBackendTools: Main().RestorePartitionTable(): Finished Restoring the Partition Table!")

    def RestoreBootSector(self):
        """Restore the bootsector‎."""
        #For GPT disks, restore with dd.
        #For MBR disks, restore with dd if=<somefile> of=/dev/sdX bs=446 count=1
        logger.info("EssentialBackendTools: Main().RestoreBootSector(): Preparing to restore the Boot Sector...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to restore the Boot Sector...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 10)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to restore the Boot Sector...###\n")

        #We need to check if BootSectorFile is on a different partition or device, so we can make sure it's available. (this is necessary if the user did an FS check). *** Actually I don't think it unmounts anything, just remounts read-only. I will investigate. ***
        if "/mnt/" in BootSectorFile: #*** Does looking for '/mnt/' work? ***
            #It is! Determine which partition we need to mount.
            Temp = BootSectorFile.split('/')
            PartitionToMount = "/"+'/'.join(Temp[2:4])

            #Mount it, and set a variable so we can unmount it afterwards. *** With that variable, check if it was mounted before, and if so leave it alone! ***
            if CoreTools.MountPartition(Partition=PartitionToMount, MountPoint="/mnt"+PartitionToMount) != 0:
                logger.error("EssentialBackendTools: Main().RestoreBootSector(): Failed to mount "+PartitionToMount+" to /mnt"+PartitionToMount+"! Continuing anyway...")

            MountedFS = PartitionToMount
            logger.info("EssentialBackendTools: Main().RestoreBootSector(): Okay. Mounted the partition: "+MountedFS+" that houses the file. Now let's restore the Boot Sector...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 35)

        else:
            #Nope, it's on this partition.
            MountedFS = "None"
            logger.info("EssentialBackendTools: Main().RestoreBootSector(): Okay. Now let's restore the Boot Sector...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 35)

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Restoring the Boot Sector...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 55)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Restoring the Boot Sector...###\n")

        if BootSectorBackupType == "mbr":
            #Let's restore the MBR bootsector.
            logger.info("EssentialBackendTools: Main().RestoreBootSector(): Restoring MBR boot sector from file: "+BootSectorFile+" to device: "+BootSectorTargetDevice+"...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 65)
            CoreTools.StartProcess("dd if="+BootSectorFile+" of="+BootSectorTargetDevice+" bs=446 count=1", ShowOutput=False)

        else:
            #Restore the UEFISystemPartition.
            logger.info("EssentialBackendTools: Main().RestoreBootSector(): Restoring UEFI Partition ("+SystemInfo["UEFISystemPartition"]+") from file: "+BootSectorFile+"...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 65)
            CoreTools.StartProcess("dd if="+BootSectorFile+" of="+SystemInfo["UEFISystemPartition"], ShowOutput=False)

        #Unmount the partition containing the file, if there is one. *** Is this necessary? ***
        if MountedFS != "None":
            logger.info("EssentialBackendTools: Main().RestoreBootSector(): Unmounting partition: "+MountedFS+"...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 85)
            if CoreTools.Unmount(MountedFS) != 0:
                logger.error("EssentialBackendTools: Main().RestoreBootSector(): Failed to unmount "+MountedFS+"! Continuing anyway...")

        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Restoring the Boot Sector!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished Restoring the Boot Sector...###\n")
        logger.info("EssentialBackendTools: Main().RestoreBootSector(): Finished restoring the boot sector!")

    def QuickFileSystemCheck(self): #*** This is very duplicated with BadSectorCheck, can we merge them and put a check in? *** *** Will need lots of work when we switch to dictionaries ***
        """Quickly check all filesystems."""
        logger.debug("EssentialBackendTools: Main().QuickFileSystemCheck(): Starting...")

        #Update Current Operation Text.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing for Quick Filesystem Check...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 10)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to do the Quick Filesystem Check...###\n")

        #Determine which partitions are to be checked.
        CheckList = HelperBackendTools.FindCheckableFileSystems()
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 30)

        #Find the length of the list (this is needed to update the progressbars).
        CheckListLength = len(CheckList)

        DialogTools.ShowMsgDlg(Kind="info", Message="WxFixBoot will now perform the disk check. Do not be alarmed by on-screen inactivity, even in the terminal output box, as this operation could take a long time to complete.")

        #Run the check on the checkable partitions
        for Element in CheckList:
            #Gather info.
            SplitElement = Element.split()
            Partition = SplitElement[0]
            FSType = SplitElement[1]
            RemountPartitionAfter = SplitElement[2]

            logger.info("EssentialBackendTools: Main().QuickFileSystemCheck(): Checking Partition: "+Partition+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Checking Partition: "+Partition+"###\n")
            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Checking Partition: "+Partition)
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 30+((50//CheckListLength)*(CheckList.index(Element)+1)))

            #Create a command list that will work based on the fstype of this partition. If there aren't any use cases for the fstype, display a message to the user and skip it.
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
                logger.warning("EssentialBackendTools: Main().QuickFileSystemCheck(): Skipping Partition: "+Partition+", as WxFixBoot doesn't support checking it yet...")
                DialogTools.ShowMsgDlg(Kind="error", Message="The filesystem on partition: "+Partition+" could not be checked, as WxFixBoot doesn't support checking it yet. "+Partition+" will now be skipped.")

            #Run the command with Piping = False, if ExecList != ['None'], otherwise do nothing, but do remount the partition if needed.
            if ExecCmds != "":
                retval = CoreTools.StartProcess(ExecCmds)

                #Check the return values, and run the handler if needed.
                if retval == 0:
                    #Success.
                    logger.info("EssentialBackendTools: Main().QuickFileSystemCheck(): Checked partition: "+Partition+". No Errors Found!")

                else:
                    HelperBackendTools.HandleFilesystemCheckReturnValues(ExecCmds=ExecCmds, Retval=retval, Partition=Partition) #*** Needs to change to use strings, at the moment it splits the string into a list ***

            if RemountPartitionAfter == "True":
                logger.debug("EssentialBackendTools: Main().QuickFileSystemCheck(): Remounting Partition: "+Partition+" Read-Write...")
                Retval = CoreTools.MountPartition(Partition=Partition, MountPoint="/mnt"+Partition)

                if Retval != 0:
                    logger.warning("EssentialBackendTools: Main().QuickFileSystemCheck(): Failed to remount partition: "+Partition+" after check. We probably need to reboot first. Never mind...")

        #Update Current Operation Text.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Quick Filesystem Check!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished Quick Filesystem Check!###\n")

    def BadSectorCheck(self): #*** This is very duplicated with QuickFSCheck, can we merge them and put a check in? ***
        """Check all filesystems for bad sectors."""
        logger.debug("EssentialBackendTools: Main().BadSectorCheck(): Starting...")

        #Update Current Operation Text.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing for Bad Sector Check...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 10)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to do the Bad Sector Check...###\n")

        #Determine which partitions are to be checked.
        CheckList = HelperBackendTools.FindCheckableFileSystems()
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 30)

        #Find the length of the list (this is needed to update the progressbars).
        CheckListLength = len(CheckList)

        DialogTools.ShowMsgDlg(Kind="info", Message="WxFixBoot will now perform the disk check. Do not be alarmed by on-screen inactivity, even in the terminal output box, as this operation could take a long time to complete.")

        #Run the check on the checkable partitions
        for Element in CheckList:
            #Gather info.
            SplitElement = Element.split()
            Partition = SplitElement[0]
            FSType = SplitElement[1]
            RemountPartitionAfter = SplitElement[2]

            logger.info("EssentialBackendTools: Main(.BadSectorCheck(): Checking Partition: "+Partition+"...")
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Checking Partition: "+Partition+"###\n")
            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Checking Partition: "+Partition)
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 30+((50//CheckListLength)*(CheckList.index(Element)+1)))

            #Run a command that will work based on the fstype of this partition. If there aren't any use cases for the fstype, display a message to the user and skip it. Ignore return values.
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
                    logger.info("EssentialBackendTools: Main().BadSectorCheck(): Checked partition: "+Partition+" No Errors Found!")

                else:
                    HelperBackendTools.HandleFilesystemCheckReturnValues(ExecCmds=ExecCmds, Retval=retval, Partition=Partition) #*** Needs to change to use strings, at the moment it splits the string into a list *** 

            if RemountPartitionAfter == "True":
                logger.debug("EssentialBackendTools: Main().BadSectorCheck(): Remounting Partition: "+Partition+" Read-Write...")
                Retval = CoreTools.MountPartition(Partition=Partition, MountPoint="/mnt"+Partition)

                if Retval != 0:
                    logger.warning("EssentialBackendTools: Main().BadSectorCheck(): Failed to remount partition: "+Partition+" after check. We probably need to reboot first. Never mind...")

        #Update Current Operation Text.
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished Bad Sector Check!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)
        wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished Bad Sector Check!###\n")

