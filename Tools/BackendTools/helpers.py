#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Helper Backend Tools in the BackendTools Package for WxFixBoot Version 2.0.1
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

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Begin Main Class.
class Main():
    def PartitionMatchesOS(self, Partition, OS):
        """Matches the given boot device to an OS, using the info we gathered at startup using the function above"""
        #Try to match it by UUID or by name, looking for the same type of match we got before, to avoid false positives.
        print("Type of Match: "+BootloaderInfo[OS]["DefaultBootDeviceMatchedWith"])
        print("Partition to match: "+Partition)
        print("OS to match with: "+OS)
        print("Trying to match (1st) with: "+OSInfo[OS]["Partition"])
        print("Trying to match (2nd) with: "+OSInfo[OS]["BootPartition"])
        print("Trying to match (3rd) with: "+OSInfo[OS]["EFIPartition"])

        #If partition is unknown ignore it.
        if Partition == "Unknown":
            return False

        #If the eg EFI partition isn't known, don't do the rest of the test in the if statement to avoid erors (short-circuit logic).
        if OSInfo[OS]["Partition"] != "Unknown" and Partition in (OSInfo[OS]["Partition"], DiskInfo[OSInfo[OS]["Partition"]]["UUID"]):
            return True

        elif OSInfo[OS]["BootPartition"] != "Unknown" and Partition in (OSInfo[OS]["BootPartition"], DiskInfo[OSInfo[OS]["BootPartition"]]["UUID"]):
            return True

        elif OSInfo[OS]["EFIPartition"] != "Unknown" and Partition in (OSInfo[OS]["BootPartition"], DiskInfo[OSInfo[OS]["BootPartition"]]["UUID"]):
            return True

        else:
            return False

    def WaitUntilPackageManagerNotInUse(self, MountPoint, PackageManager):
        """Check if the package manager is in use, and if so, wait until it is no longer in use."""
        if PackageManager == "apt-get":
            Cmd = "apt-get check"

        elif PackageManager == "yum":
            Cmd = "yum -C check-update"

        if MountPoint != "":
            Cmd = "chroot "+MountPoint+" "+Cmd

        RetVal = 1

        #Trap in while loop until package manager is free.
        while RetVal != 0:
            RetVal = CoreTools.StartProcess(Cmd, ShowOutput=False)
            time.sleep(5)

    def FindMissingFSCKModules(self):
        """Check for and return all missing fsck modules (fsck.vfat, fsck.minix, etc)."""
        logger.info("HelperBackendTools: Main().FindMissingFSCKModules(): Looking for missing FSCK modules to ignore...")
        FailedList = []

        Keys = DiskInfo.keys()
        Keys.sort()

        for Disk in Keys:
            #Check the FSType is known and isn't swap.
            if DiskInfo[Disk]["FileSystem"] not in ("Unknown", "N/A"):
                #Check if this module is present.
                if CoreTools.StartProcess("which fsck."+DiskInfo[Disk]["FileSystem"], ShowOutput=False) != 0:
                    #Couldn't find it, add it to the failed list.
                    logger.warning("HelperBackendTools: Main().FSCKModules(): Couldn't find FSCK module fsck."+DiskInfo[Disk]["FileSystem"]+"! Adding it to the list of missing modules...")
                    FailedList.append("fsck."+DiskInfo[Disk]["FileSystem"])

                else:
                    logger.debug("HelperBackendTools: Main().FSCKModules(): Found fsck."+DiskInfo[Disk]["FileSystem"]+"...")

        #Return the list, so FSCheck functions know which FSes to ignore.
        logger.info("HelperBackendTools: Main().FindMissingFSCKModules(): Done! Missing FSCK modules: "+', '.join(FailedList))
        return FailedList

    def FindCheckableFileSystems(self):
        """Find all checkable filesystems, and then return them to EssentialBackendTools().FileSystemCheck()"""
        logger.info("HelperBackendTools: Main().FindCheckableFileSystems(): Finding and returning all filesystems/partitions that can be checked...")

        #Do setup.
        DoNotCheckList = []
        FileSystemsToCheck = {}
        RootFS = CoreTools.GetPartitionMountedAt("/")

        #Get a list of missing fsck modules (if any) based on the existing filesystems.
        MissingFSCKModules = self.FindMissingFSCKModules()

        Keys = DiskInfo.keys()
        Keys.sort()

        #Determine checkable partitions.
        for Disk in Keys:
            #Ignore all devices.
            if DiskInfo[Disk]["Type"] == "Device":
                continue

            #Check if the required fsck module is present, and that the partition isn't RootFS
            if "fsck."+DiskInfo[Disk]["FileSystem"] in MissingFSCKModules:
                MountPoint = "None"
                CheckTheFS = False
                RemountPartitionAfter = False

            else:
                #If we're not running on a live disk, skip the filesystem if it's the same as RootFS (in which case checking it may corrupt data).
                if SystemInfo["IsLiveDisk"] == False and Disk == RootFS:
                    MountPoint = "/"
                    CheckTheFS = False
                    RemountPartitionAfter = False
                    continue

                #Check if the partition is mounted.
                if CoreTools.IsMounted(Disk) == False:
                    MountPoint = "None"
                    CheckTheFS = True
                    RemountPartitionAfter = False

                else:
                    #Unmount the FS temporarily, to avoid data corruption.
                    MountPoint = CoreTools.GetMountPointOf(Disk)

                    if CoreTools.Unmount(Disk) != 0:
                        logger.warning("HelperBackendTools: Main().FindCheckableFileSystems(): Failed to unmount "+Disk+", which is necessary for safe disk checking! Ignoring it...")
                        CheckTheFS = False
                        RemountPartitionAfter = False

                    else:
                        CheckTheFS = True
                        RemountPartitionAfter = True

            if CheckTheFS:
                #Add it to the dictionary for checking.
                FileSystemsToCheck[Disk] = {}
                FileSystemsToCheck[Disk]["Remount"] = RemountPartitionAfter
                FileSystemsToCheck[Disk]["MountPoint"] = MountPoint

            else:
                #Add it to the non-checkable list
                DoNotCheckList.append(Disk+" with Filesystem: "+DiskInfo[Disk]["FileSystem"])

        #Report uncheckable partitions.
        if DoNotCheckList != []:
            #Some filesystems will not be checked. Tell the user.
            DialogTools.ShowMsgDlg(Kind="info", Message="The following filesystems will not be checked:\n\n"+'\n'.join(DoNotCheckList)+".\n\nThe most likely reason for this is that some of the filesystems are in use, or that the required filesystem checkers weren't found. WxFixBoot will now continue to check the remaining filesystems.")

        logger.info("HelperBackendTools: Main().FindCheckableFileSystems(): Done! Filesystems that won't be checked: "+'\n'.join(DoNotCheckList)+"...")
        return FileSystemsToCheck

    def HandleFilesystemCheckReturnValues(self, ExecCmds, Retval, Partition):
        """Handle Filesystem Checker return codes."""
        ExecList = ExecCmds.split()

        #Return values of 1,2 or 3 happen if errors were corrected.
        if Retval in (1, 2, 3) and ExecList[0] != "badblocks":
            if ExecList[0] == "xfs_repair":
                #Fs Corruption Detected.
                logger.warning("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): xfs_repair detected filesystem corruption on FileSystem: "+Partition+". It's probably (and hopefully) been fixed, but we're logging this anyway.")
                DialogTools.ShowMsgDlg(Kind="warning", Message="Corruption was found on the filesystem: "+Partition+"! Fortunately, it looks like the checker utility has fixed the corruption. Click okay to continue.")

            elif ExecList[0] in ('fsck.jfs', 'fsck.minix', 'fsck.reiserfs', 'fsck.vfat', 'fsck.ext2', 'fsck.ex3', 'fsck.ext4', 'fsck.ext4dev'):
                #Fixed Errors.
                logger.info("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): "+ExecList[0]+" successfully fixed errors on the partition: "+Partition+". Continuing...")
                DialogTools.ShowMsgDlg(Kind="warning", Message="The filesystem checker found and successfully fixed errors on partition: "+Partition+". Click okay to continue.")

        else:
            #Something bad happened!
            #If we're doing bootloader operations, prompt the user to disable them.
            BootloaderOperations = False

            for Function in Operations:
                if type(Function) == type(()):
                    if MainBackendTools.ManageBootloader == Function: #*** check again ***
                        BootloaderOperations = True
                        break

            logger.error("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): "+ExecList[0]+" Errored with exit value "+unicode(Retval)+"! This could indicate filesystem corruption or bad sectors!")

            if BootloaderOperations:
                logger.error("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): Asking the user whether to skip bootloader operations...")

                Result = DialogTools.ShowYesNoDlg(Message="Error! The filesystem checker gave exit value: "+unicode(Retval)+"! This could indicate filesystem corruption, a problem with the filesystem checker, or bad sectors on partition: "+Partition+". If you perform bootloader operations on this partition, your system could become unstable or unbootable. Do you want to disable bootloader operations, as is strongly recommended?", Title="WxFixBoot - Disable Bootloader Operations?", Buttons=("Disable Bootloader Operations", "Ignore and Continue Anyway"))

                if Result:
                    #A good choice. WxFixBoot will now disable any bootloader operations.
                    logger.warning("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): User disabled bootloader operations as recommended, due to bad sectors/HDD problems/FS Checker problems...")
                    SystemInfo["DisableBootloaderOperations"] = True
                    SystemInfo["DisableBootloaderOperationsBecause"].append("Filesystem corruption was detected on "+Partition)

                else:
                    #Seriously? Well, okay, we'll do it anyway... This is probably a very bad idea...
                    logger.warning("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): User ignored the warning and went ahead with bootloader modifications (if any) anyway, even with possible HDD problems/Bad sectors! This is a REALLY bad idea, but we'll do it anyway, as requested...")

    def WriteFSTABEntryForUEFIPartition(self, OS, MountPoint):
        """Write an /etc/fstab entry for the UEFI System Partition, if there isn't already one. DISABLED***"""
        return True

        logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): Preparing to write an fstab entry for the UEFI partition ("+OSInfo[OS]["EFIPartition"]+")...")

        WriteEntry = True

        #Make the directory MountPoint/boot/efi if it doesn't already exist.
        if os.path.isdir(MountPoint+"/boot/efi") == False:
            os.makedirs(MountPoint+"/boot/efi")

        #Open the MountPoint/etc/fstab file for reading. If we aren't using chroot, this'll just be /etc/fstab, otherwise, /tmp/wxfixboot/mountpoints/dev/sdxy/etc/fstab. Also, save its contents in a variable.
        fstab = open(MountPoint+"/etc/fstab", "r")
        NewFileContents = []

        for line in fstab:
            if OSInfo[OS]["EFIPartition"] in line or "UUID="+DiskInfo[OSInfo[OS]["EFIPartition"]]["UUID"] in line:
                #This fstab already has an entry for the UEFI System Partition!
                WriteEntry = False

            NewFileContents.append(line)

        #Check if we need to write the entry.
        if WriteEntry == False:
            #We don't!
            logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): fstab entry already present! Skipping...")
            fstab.close()

        else:
            #We do. If we can use the UUID, then we will, but otherwise we'll use the standard device name.
            logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): Writing fstab entry...")
            NewFileContents.append("\n#fstab entry for UEFI System Partition ("+OSInfo[OS]["EFIPartition"]+"), written by WxFixBoot.\n")

            if DiskInfo[OSInfo[OS]["EFIPartition"]]["UUID"] != "Unknown":
                logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): Using UUID to prevent problems down the line...")
                NewFileContents.append("UUID="+DiskInfo[OSInfo[OS]["EFIPartition"]]["UUID"]+" /boot/efi vfat defaults 0 2\n")

            else:
                logger.warning("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): We have no UUID for the UEFI Partition: "+OSInfo[OS]["EFIPartition"]+"! This isn't good, and may cause problems down the line. Continuing anyway, using device name instead...")
                NewFileContents.append(OSInfo[OS]["EFIPartition"]+" /boot/efi vfat defaults 0 2\n")

            #Write the finished lines to the file.
            fstab.close()
            fstab = open(MountPoint+"/etc/fstab", 'w')
            fstab.write(''.join(NewFileContents))
            fstab.close()

            logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): Done!")

    def BackupUEFIFiles(self, MountPoint):
        """Backup some .efi files, just in case something goes wrong.""" #NOTE: v2.1: Make this smarter when we detect Windows.
        logger.info("HelperBackendTools: Main().BackupUEFIFiles(): Backing up UEFI Files...")

        #We'll backup /EFI/boot/bootx64.efi if it exists, and we'll also backup Windows's uefi files, if they exist.
        #First do /EFI/boot/bootx64.efi. Fortunately, the UEFI partition is always a fat32/fat16 filesystem, so case doesn't matter.
        logger.info("HelperBackendTools: Main().BackupUEFIFiles(): Backing up "+MountPoint+"/boot/efi/boot/boot*.efi...")

        if os.path.isfile(MountPoint+"/boot/efi/EFI/boot/boot*.efi"):
            if CoreTools.StartProcess("cp -v "+MountPoint+"/boot/efi/EFI/boot/boot*.efi "+MountPoint+"/boot/efi/EFI/boot/bkpbootx64.efi", ShowOutput=False) != 0:
                #Log and warn user if this went wrong.
                logger.error("HelperBackendTools: Main().BackupUEFIFiles(): Failed to backup failsafe UEFI boot file! Warning user and continuing...")
                DialogTools.ShowMsgDlg(Kind="error", Message="Error! WxFixBoot failed to save your UEFI boot files to the backup directory! This probably isn't very important. Click okay to continue.")

        #Now do Windows's files, if they exist.
        logger.info("HelperBackendTools: Main().BackupUEFIFiles(): Backing up Windows's boot files if they exist...")

        if os.path.isfile(MountPoint+"/boot/efi/EFI/Microsoft/boot/bootmgfw.efi"):
            if CoreTools.StartProcess("cp -v "+MountPoint+"/boot/efi/EFI/Microsoft/boot/bootmgfw.efi "+MountPoint+"/boot/efi/EFI/Microsoft/boot/bkpbootmgfw.efi", ShowOutput=False) != 0:
                #Log and warn user if this went wrong.
                logger.error("HelperBackendTools: Main().BackupUEFIFiles(): Failed to backup Windows's UEFI boot files! Warning user and continuing...")
                DialogTools.ShowMsgDlg(Kind="error", Message="Warning: WxFixBoot failed to backup Windows's UEFI boot files! This probably isn't very important. Click okay to continue.")

        logger.info("HelperBackendTools: Main().BackupUEFIFiles(): Done!")

    def ManageUEFIFiles(self, OS, MountPoint):
        """Manage UEFI bootloader files."""
        logger.info("HelperBackendTools: Main().ManageUEFIFiles(): Copying UEFI Files to UEFIBootDir...")

        #First, let's check if EFI/boot already exists. This is a fat32/fat16 filesystem, so case doesn't matter.
        if os.path.isdir(MountPoint+"/boot/efi/EFI/boot"):
            UEFIBootDir = MountPoint+"/boot/efi/EFI/boot"

        else:
            #It doesn't, so we'll create it.
            UEFIBootDir = MountPoint+"/boot/efi/EFI/boot"
            os.mkdir(UEFIBootDir)

        #Do this different depending on whether the OS is ubuntu or fedora-based.
        if OSInfo[OS]["PackageManager"] == "apt-get":
            SourceDir = MountPoint+"/boot/efi/EFI/ubuntu"

        elif OSInfo[OS]["PackageManager"] == "yum":
            SourceDir = MountPoint+"/boot/efi/EFI/fedora"
            
        #Do it differently depending on whether the now-installed UEFI bootloader is ELILO or GRUB-UEFI.
        if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "ELILO":
            #We need to copy both elilo.efi, and elilo.conf to UEFIBootDir.
            logger.info("HelperBackendTools: Main().ManageUEFIFiles(): Copying elilo.efi, elilo.conf and elilomenu.msg to "+UEFIBootDir+"...")

            if CoreTools.StartProcess("cp -v "+SourceDir+"/elilo.efi "+UEFIBootDir+"/bootx64.efi", ShowOutput=False) != 0:
                logger.error("HelperBackendTools: Main().ManageUEFIFiles(): Failed to copy "+SourceDir+"/elilo.efi to "+UEFIBootDir+"/bootx64.efi! Attempting to continue anyway...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to copy one of the new bootloader's UEFI files to the failsafe directory! This could potentially be a problem, but it's probably fine. Click okay to continue.")

            if CoreTools.StartProcess("cp -v "+SourceDir+"/elilo.conf "+UEFIBootDir+"/", ShowOutput=False) != 0:
                logger.error("HelperBackendTools: Main().ManageUEFIFiles(): Failed to copy "+SourceDir+"/elilo.conf to "+UEFIBootDir+"/! Attempting to continue anyway...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to copy one of the new bootloader's UEFI files to the failsafe directory! This could potentially be a problem, but it's probably fine. Click okay to continue.")

            if CoreTools.StartProcess("cp -v /usr/share/wxfixboot/sampleconfig/elilomenu.msg "+UEFIBootDir+"/", ShowOutput=False) != 0:
                logger.error("HelperBackendTools: Main().ManageUEFIFiles(): Failed to copy elilomenu.msg to "+UEFIBootDir+"! Attempting to continue anyway...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to copy one of the new bootloader's UEFI files to the failsafe directory! This could potentially be a problem, but it's probably fine. Click okay to continue.")

            if CoreTools.StartProcess("cp -v /usr/share/wxfixboot/sampleconfig/elilomenu.msg "+SourceDir+"/", ShowOutput=False) != 0:
                logger.error("HelperBackendTools: Main().ManageUEFIFiles(): Failed to copy elilomenu.msg to "+SourceDir+"/! Attempting to continue anyway...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to copy one of the new bootloader's UEFI files to the failsafe directory! This could potentially be a problem, but it's probably fine. Click okay to continue.")

            #If we were previously using GRUB-EFI, remove its EFI files.
            if BootloaderInfo[OS]["Bootloader"] == "GRUB-UEFI":
                if CoreTools.StartProcess("rm -v "+SourceDir+"/grub*.efi", ShowOutput=False) != 0:
                    logger.warning("HelperBackendTools: Main().ManageUEFIFiles(): Failed to remove "+SourceDir+"/grub*.efi! Attempting to continue anyway...")

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "GRUB-UEFI":
            #We need to copy grub*.efi to UEFIBootDir.
            logger.info("HelperBackendTools: Main().ManageUEFIFiles(): Copying grub*.efi to "+UEFIBootDir+"...")

            if CoreTools.StartProcess("cp -v "+SourceDir+"/grub*.efi "+UEFIBootDir+"/bootx64.efi", ShowOutput=False) != 0:
                logger.error("HelperBackendTools: Main().ManageUEFIFiles(): Failed to copy "+SourceDir+"/grub*.efi to "+UEFIBootDir+"/bootx64.efi! Attempting to continue anyway...")
                DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to copy the new bootloader's UEFI files to the failsafe directory! This could potentially be a problem, but it's probably fine. Click okay to continue.")

            #If we were previously using ELILO, remove its EFI files.
            if BootloaderInfo[OS]["Bootloader"] == "ELILO":
                if CoreTools.StartProcess("rm -v "+SourceDir+"/elilo*", ShowOutput=False) != 0:
                    logger.warning("HelperBackendTools: Main().ManageUEFIFiles(): Failed to remove "+SourceDir+"/elilo*! Attempting to continue anyway...")

        logger.info("HelperBackendTools: Main().ManageUEFIFiles(): Done!")
