#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Helper Backend Tools in the BackendTools Package for WxFixBoot Version 2.0~pre1
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

#Begin Main Class. *** These need refactoring ***
class Main():
    def FindMissingFSCKModules(self):
        """Check for and return all missing fsck modules (fsck.vfat, fsck.minix, etc)."""
        logger.info("HelperBackendTools: Main().FindMissingFSCKModules(): Looking for missing FSCK modules to ignore...")
        FailedList = []

        Keys = DiskInfo.keys()
        Keys.sort()

        for Disk in Keys:
            FSType = DiskInfo[Disk]["FileSystem"]

            #Check the FSType is known.
            if FSType not in ("Unknown", "N/A"):
                #Check if this module is present.
                Retval = CoreTools.StartProcess("which fsck."+FSType, ShowOutput=False)

                if Retval != 0:
                    #OS probably couldn't find it, add it to the failed list.
                    logger.warning("HelperBackendTools: Main().FSCKModules(): Couldn't find FSCK module: fsck."+FSType+"! Adding it to the list of missing modules...")
                    FailedList.append("fsck."+FSType)

                else:
                    logger.debug("HelperBackendTools: Main().FSCKModules(): Found fsck."+FSType+"...")

        #Return the list, so FSCheck functions know which FSes to ignore.
        logger.info("HelperBackendTools: Main().FindMissingFSCKModules(): Done! Missing FSCK modules: "+', '.join(FailedList))
        return FailedList

    def FindCheckableFileSystems(self): #*** Tidy this up later ***
        """Find all checkable filesystems, and then return them to MainBackendTools().BadSectorCheck()/MainBackendTools().QuickFSCheck()"""
        logger.info("HelperBackendTools: Main().FindCheckableFileSystems(): Finding and returning all filesystems/partitions that can be checked...")

        #Do setup.
        DoNotCheckList = []
        CheckList = []

        #Get a list of missing fsck modules (if any) based on the existing filesystems.
        MissingFSCKModules = self.FindMissingFSCKModules()

        Keys = DiskInfo.keys()
        Keys.sort()

        #Determine checkable partitions.
        for Disk in Keys:
            #Make sure we're looking at a partition, if not, ignore it.
            if DiskInfo[Disk]["Type"] == "Partition":
                #Get the FSType.
                FSType = DiskInfo[Disk]["FileSystem"]

                #Check if the required fsck module is present, and that the partition isn't RootFS
                if "fsck."+FSType not in MissingFSCKModules and FSType not in ("Unknown", "N/A"):
                    #If we're not running on a live disk, skip the filesystem if it's the same as RootFS (in which case checking it may corrupt data)
                    if SystemInfo["IsLiveDisk"] == False and Disk == SystemInfo["RootFS"]:
                        CheckTheFS = False
                        RemountPartitionAfter = False
                        continue

                    #Check if the partition is mounted.
                    PartitionIsMounted = CoreTools.IsMounted(Disk)

                    if PartitionIsMounted == False:
                        #Not mounted.
                        CheckTheFS = True
                        RemountPartitionAfter = False

                    else:
                        #Unmount the FS temporarily, to avoid data corruption.
                        Retval = CoreTools.Unmount(Disk)

                        if Retval != 0:
                            logger.warning("HelperBackendTools: Main().FindCheckableFileSystems(): Failed to unmount "+Disk+", which is necessary for safe disk checking! Ignoring it, becuase it's probably a home directory (if running an OS on the HDD, and not a live disk) or an essential system dir...")
                            CheckTheFS = False
                            RemountPartitionAfter = False

                        else:
                            CheckTheFS = True
                            RemountPartitionAfter = True
                else:
                    CheckTheFS = False
                    RemountPartitionAfter = False

                if CheckTheFS == False:
                    #Add it to the non-checkable list
                    DoNotCheckList.append(Disk+" with Filesystem: "+FSType)

                else:
                    #Add it to the list for checking.
                    CheckList.append(Disk+" "+FSType+" "+unicode(RemountPartitionAfter))

        #Report uncheckable partitions.
        if DoNotCheckList != []:
            #Some filesystems will not be checked. Tell the user.
            DialogTools.ShowMsgDlg(Kind="info", Message="The following filesystems will not be checked:\n\n"+'\n'.join(DoNotCheckList)+".\n\nThe most likely reason for this is that some of the filesystems are in use, or that the required filesystem checkers weren't found. WxFixBoot will now continue to check the remaining filesystems.")

        logger.info("HelperBackendTools: Main().FindCheckableFileSystems(): Done! Filesystems that won't be checked: "+'\n'.join(DoNotCheckList)+"...")
        return CheckList

    def HandleFilesystemCheckReturnValues(self, ExecCmds, Retval, Partition):
        """Handle Filesystem Checker return codes."""
        ExecList = ExecCmds.split()

        #Return values of 1,2 or 3 happen if errors were corrected.
        if Retval in (1, 2, 3):
            if ExecList[0] == "xfs_repair":
                #Fs Corruption Detected.
                logger.warning("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): xfs_repair detected filesystem corruption on FileSystem: "+Partition+". It's probably (and hopefully) been fixed, but we're logging this anyway.")
                DialogTools.ShowMsgDlg(Kind="warning", Message="Corruption was found on the filesystem: "+Partition+"! Fortunately, it looks like the checker utility has fixed the corruption. Click okay to continue.")

            elif ExecList[0] in ('fsck.jfs', 'fsck.minix', 'fsck.reiserfs', 'fsck.vfat', 'fsck.ext2', 'fsck.ex3', 'fsck.ext4', 'fsck.ext4dev'):
                #Fixed Errors.
                logger.info("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): "+ExecList[0]+" successfully fixed errors on the partition: "+Partition+". Continuing...")
                DialogTools.ShowMsgDlg(Kind="warning", Message="The filesystem checker found and successfully fixed errors on partition: "+Partition+". Click okay to continue.")

        else:
            #Something bad happened! *** Check if we're actually doing bootloader operations first! ***
            logger.error("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): "+ExecList[0]+" Errored with exit value "+unicode(retval)+"! This could indicate filesystem corruption or bad sectors! Asking the user whether to skip any bootloader operations...")

            Result = DialogTools.ShowYesNoDlg(Message="Error! The filesystem checker gave exit value: "+unicode(retval)+"! This could indicate filesystem corruption, a problem with the filesystem checker, or bad sectors on partition: "+Partition+". If you perform bootloader operations on this partition, WxFixBoot could become unstable, and your system could become unbootable. Do you want to disable bootloader operations, as is strongly recommended?", Title="WxFixBoot - Disable Bootloader Operations?")

            if Result:
                #A good choice. WxFixBoot will now disable any bootloader operations. *** Keep note of why we disabled bootloader operations here ***
                logger.warning("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): User disabled bootloader operations as recommended, due to bad sectors/HDD problems/FS Checker problems...")

                SystemInfo["OSsForBootloaderRemoval"] = []
                SystemInfo["DisableBootloaderOperations"] = True

            else:
                #Seriously? Well, okay, we'll do it anyway... This is probably a very bad idea...
                logger.warning("HelperBackendTools: Main().HandleFilesystemCheckReturnValues(): User ignored the warning and went ahead with bootloader modifications (if any) anyway, even with possible HDD problems/Bad sectors! This is a REALLY bad idea, but we'll do it anyway, as requested...")

    def AskUserForBootloaderInstallationOSs(self, UpdateBootloader, ReinstallBootloader): #*** Maybe move to BootloaderTools package ***
        """Ask the user where the new bootloader is to be installed."""
        SystemInfo["OSsForBootloaderInstallation"] = []

        if len(SystemInfo["OSsWithPackageManagers"]) == 1:
            if UpdateBootloader:
                DialogTools.ShowMsgDlg(Kind="info", Message="Your bootloader will be updated.")

            else:
                DialogTools.ShowMsgDlg(Kind="info", Message="Your bootloader will be removed from the following Operating Systems ("+', '.join(SystemInfo["OSsForBootloaderRemoval"])+").")

            SystemInfo["OSsForBootloaderInstallation"] = SystemInfo["OSsWithPackageManagers"][:]
            logger.info("HelperBackendTools: Main().AskUserForInstallationOSs(): Installing the new bootloader in OS(s): "+', '.join(SystemInfo["OSsForBootloaderInstallation"]))

        else:
            if UpdateBootloader or ReinstallBootloader:
                DialogTools.ShowMsgDlg(Kind="info", Message="Your bootloader will be updated or reinstalled in all Operating Systems it is installed in ("+', '.join(SystemInfo["OSsForBootloaderRemoval"])+"). Click okay to continue.")
                SystemInfo["OSsForBootloaderInstallation"] = SystemInfo["OSsForBootloaderRemoval"][:]

            else: #*** Check all this works ***
                logger.info("HelperBackendTools: Main().AskUserForBootloaderInstallationOSs(): There is more than one Operating System with a supported package manager. Asking the user which ones to install the new bootloader in...")
                DialogTools.ShowMsgDlg(Kind="info", Message="Your bootloader will be removed in all Operating Systems it is installed in ("+', '.join(SystemInfo["OSsForBootloaderRemoval"])+"). You will now be asked which Operating Systems you want your new bootloader to be installed in.")

                #Make a list of candidates to install the bootloader in (only including OSes that will have their bootloaders removed).
                BootloaderCandidatesList = SystemInfo["OSsWithPackageManagers"][:]

                logger.debug("HelperBackendTools: Main().AskUserForBootloaderInstallationOSs(): Contents of BootloaderCandidatesList: "+', '.join(BootloaderCandidatesList))
                logger.info("HelperBackendTools: Main().AskUserForBootloaderInstallationOSs(): Asking the user which new OS to install the bootloader to...")

                #Ask the user which candidate(s) to use for bootloader installation.
                SystemInfo["OSsForBootloaderInstallation"] = DialogTools.ShowMultiChoiceDlg(Message="Please select each OS you'd like to modify or install the bootloader to.\nIdeally, select the ones that you use most frequently.", Title="WxFixBoot - Select Operating Systems For Bootloader Installation", Choices=BootloaderCandidatesList)

                logger.info("HelperBackendTools: Main().AskUserForBootloaderInstallationOSs(): User selected: "+Result+"...")

        logger.info("HelperBackendTools: Main().AskUserForInstallationOSs(): Finished selecting OSs! Modifying or Installing the new bootloader in: "+', '.join(SystemInfo["OSsForBootloaderInstallation"]))

    def WriteFSTABEntryForUEFIPartition(self, MountPoint):
        """Write an /etc/fstab entry for the UEFI System Partition, if there isn't already one."""
        logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): Preparing to write an fstab entry for the UEFI partition ("+SystemInfo["UEFISystemPartition"]+")...")

        WriteEntry = True

        #Make the directory MountPoint/boot/efi if it doesn't already exist.
        if os.path.isdir(MountPoint+"/boot/efi") == False:
            os.makedirs(MountPoint+"/boot/efi")

        #Open the MountPoint/etc/fstab file for reading. If we aren't using chroot, this'll just be /etc/fstab, otherwise, /mnt/dev/sdxy/etc/fstab. Also, save its contents in a variable.
        fstab = open(MountPoint+"/etc/fstab", "r")
        NewFileContents = []

        for line in fstab:
            if SystemInfo["UEFISystemPartition"] in line or "UUID="+DiskInfo[SystemInfo["UEFISystemPartition"]]["UUID"] in line:
                #This fstab already has an entry for the UEFI System Partition!
                WriteEntry = False

            NewFileContents.append(line)

        #Check if we need to write the entry.
        if WriteEntry == False:
            #We don't!
            logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): fstab entry already present! Skipping...")

        else:
            #We do. If we can use the UUID, then we will, but otherwise we'll use the standard device name.
            logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): Writing fstab entry...")
            NewFileContents.append("\n#fstab entry for UEFI System Partition (Partition "+SystemInfo["UEFISystemPartition"]+"), written by WxFixBoot.\n")

            if DiskInfo[SystemInfo["UEFISystemPartition"]]["UUID"] != "Unknown": #*** Check this earlier ***
                logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): Using UUID to prevent problems down the line...")
                NewFileContents.append("UUID="+UUID+" /boot/efi vfat defaults 0 2\n")

            else:
                logger.warning("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): We have no UUID for the UEFI Partition: "+SystemInfo["UEFISystemPartition"]+"! This isn't good, and may cause problems down the line. Continuing anyway, using device name instead...")
                NewFileContents.append(SystemInfo["UEFISystemPartition"]+" /boot/efi vfat defaults 0 2\n")

            #Write the finished lines to the file.
            fstab.close()
            fstab = open(MountPoint+"/etc/fstab", 'w')
            fstab.write(''.join(NewFileContents))
            fstab.close()

            logger.info("HelperBackendTools: Main().WriteFSTABEntryForUEFIPartition(): Done!")

    def BackupUEFIFiles(self, MountPoint):
        """Backup some .efi files, just in case something goes wrong.""" #*** Make this more user friendly ***
        logger.info("HelperBackendTools: Main().BackupUEFIFiles(): Backing up UEFI Files...")

        #We'll backup /EFI/boot/bootx64.efi if it exists, and we'll also backup Windows's uefi files, if they exist.
        #First do /EFI/boot/bootx64.efi. Fortunately, the UEFI partition is always a fat32/fat16 filesystem, so case doesn't matter.
        logger.info("HelperBackendTools: Main().BackupUEFIFiles(): Backing up "+MountPoint+"/boot/efi/boot/boot*.efi...")
        if os.path.isfile(MountPoint+"/boot/efi/EFI/boot/boot*.efi"):
            retval = CoreTools.StartProcess("cp -v "+MountPoint+"/boot/efi/EFI/boot/boot*.efi "+MountPoint+"/boot/efi/EFI/boot/bkpbootx64.efi", ShowOutput=False)

        else:
            #This doesn't exist. This doesn't matter then, so set retval to 0.
            retval = 0

        #Check the return value.
        if retval != 0:
            logger.error("HelperBackendTools: Main().BackupUEFIFiles(): Failed to backup failsafe UEFI boot file! Warning user and continuing...")
            DialogTools.ShowMsgDlg(Kind="error", Message="Error! WxFixBoot failed to save your UEFI boot files to the backup directory! This probably isn't very important. Click okay to continue.")

        #Now do Windows's files, if they exist.
        logger.info("HelperBackendTools: Main().BackupUEFIFiles(): Backing up Windows's boot files if they exist...")
        if os.path.isfile(MountPoint+"/boot/efi/EFI/Microsoft/boot/bootmgfw.efi"):
            retval = CoreTools.StartProcess("cp -v "+MountPoint+"/boot/efi/EFI/Microsoft/boot/bootmgfw.efi "+MountPoint+"/boot/efi/EFI/Microsoft/boot/bkpbootmgfw.efi", ShowOutput=False)

        else:
            #They don't exist. This doesn't matter then, so set retval to 0.
            retval = 0

        logger.info("HelperBackendTools: Main().BackupUEFIFiles(): Done!")

        #Check the return value.
        if retval != 0:
            logger.error("HelperBackendTools: Main().BackupUEFIFiles(): Failed to backup Windows's UEFI boot files! Warning user and continuing...")
            DialogTools.ShowMsgDlg(Kind="error", Message="Warning: WxFixBoot failed to backup Windows's UEFI boot files! This probably isn't very important. Click okay to continue.")

    def CopyUEFIFiles(self, MountPoint):
        """Copy the new UEFI bootloader's files to default places in case of buggy firmware.""" #*** The error messages here aren't very helpful ***
        logger.info("HelperBackendTools: Main().CopyUEFIFiles(): Copying UEFI Files to UEFIBootDir...")

        #First, let's check if EFI/boot already exists. This is a fat32/fat16 filesystem, so case doesn't matter.
        if os.path.isdir(MountPoint+"/boot/efi/EFI/boot"):
            UEFIBootDir = MountPoint+"/boot/efi/EFI/boot"

        else:
            #It doesn't, so we'll create it.
            UEFIBootDir = MountPoint+"/boot/efi/EFI/boot"
            os.mkdir(UEFIBootDir)

        #Do it differently depending on whether the now-installed UEFI bootloader is ELILO or GRUB-UEFI.
        if SystemInfo["BootloaderToInstall"] == "ELILO":
            #We need to copy both elilo.efi, and elilo.conf to UEFIBootDir.
            logger.info("HelperBackendTools: Main().CopyUEFIFiles(): Copying elilo.efi and elilo.conf to "+UEFIBootDir+"...")
            Retval = CoreTools.StartProcess("cp -v "+MountPoint+"/boot/efi/EFI/ubuntu/elilo.efi "+UEFIBootDir+"/bootx64.efi", ShowOutput=False)

            if Retval != 0:
                logger.error("HelperBackendTools: Main().CopyUEFIFiles(): Failed to copy elilo.efi to "+UEFIBootDir+"/bootx64.efi! Attempting to continue anyway...")
                DialogTools.ShowMsgDlg(Kind="error", Message="Error: WxFixBoot failed to copy one of the new bootloader's UEFI files to the backup directory! This could potentially be a problem. If your system doesn't start, this could be the reason why it doesn't start. Click okay to continue.")

            Retval = CoreTools.StartProcess("cp -v "+MountPoint+"/boot/efi/EFI/ubuntu/elilo.conf "+UEFIBootDir+"/", ShowOutput=False)

            if Retval != 0:
                logger.error("HelperBackendTools: Main().CopyUEFIFiles(): Failed to copy elilo.conf to "+UEFIBootDir+"/! Attempting to continue anyway...")
                DialogTools.ShowMsgDlg(Kind="error", Message="Error: WxFixBoot failed to copy one of the new bootloader's UEFI files to the backup directory! This could potentially be a problem. If your system doesn't start, this could be the reason why it doesn't start. Click okay to continue.")

        elif SystemInfo["BootloaderToInstall"] == "GRUB-UEFI":
            #We need to copy grub*.efi to UEFIBootDir.
            logger.info("HelperBackendTools: Main().CopyUEFIFiles(): Copying grub*.efi to "+UEFIBootDir+"...")
            Retval = CoreTools.StartProcess("cp -v "+MountPoint+"/boot/efi/EFI/ubuntu/grub*.efi "+UEFIBootDir+"/bootx64.efi", ShowOutput=False)

            if Retval != 0:
                logger.error("HelperBackendTools: Main().CopyUEFIFiles(): Failed to copy grub*.efi to "+UEFIBootDir+"/bootx64.efi! Attempting to continue anyway...")
                DialogTools.ShowMsgDlg(Kind="error", Message="Error: WxFixBoot failed to copy the new bootloader's UEFI files to the backup directory! This could potentially be a problem. If your system doesn't start, this could be the reason why it doesn't start. Click okay to continue.")

        logger.info("HelperBackendTools: Main().CopyUEFIFiles(): Done!")
