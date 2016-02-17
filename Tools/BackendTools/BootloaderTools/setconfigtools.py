#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Configuration Setting Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 1.1~pre1
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
class Main(): #*** Refactor and test all of these ***
    def SetNewBootloaderConfig(self): #*** Reduce duplication and maybe move to MainBackendTools? ***
        """Manage setting new bootloader config."""
        logger.debug("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Preparing to set bootloader config in OS(s): "+', '.join(OSsForBootloaderInstallation)+"...")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Preparing to set the new bootloaders' config...")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 77)

        #Loop through OSsForBootloaderInstallation, and provide information to the function that will set the bootloaders' config.
        for OS in OSsForBootloaderInstallation:
            #For each OS that needs the new bootloader configured, grab the partition, and the package manager.
            logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Setting the new bootloader config for OS: "+OS+"...")

            #Grab the OS's partition and package manager.
            Partition = OS.split()[-5]
            PackageManager = OS.split()[-1]

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Preparing to set the new bootloaders' config for OS: "+OS+"...###\n")

            #Grab the architecture.
            Arch = OS.split()[-8]
            if Arch == "64-bit":
                Arch = "x86_64"

            else:
                Arch = "i686"

            wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Setting the new bootloader's config...")
            wx.CallAfter(ParentWindow.UpdateCurrentProgress, 79)
            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Setting the new bootloader's config for OS: "+OS+"...###\n")

            #Check if the Partition is AutoRootFS, if we're not on a live disk.
            if LiveDisk == False and Partition == AutoRootFS:
                #If so, make sure this will work for this OS too, and avoid setting mountpoint, so the config instructions below look in the right place for the config files.
                MountPoint = ""

            else:
                #If not, set mountpoint to the actual mountpoint.
                MountPoint = "/mnt"+Partition

                #Mount the partition.
                Retval = CoreTools().MountPartition(Partition=Partition, MountPoint=MountPoint)

                if Retval != 0:
                    #Ignore this partition.
                    logger.warning("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Failed to mount "+Partition+"! Ignoring this partition...")
                    continue

                else:
                    #Set up chroot.
                    CoreBackendTools().SetUpChroot(MountPoint=MountPoint)

                wx.CallAfter(ParentWindow.UpdateCurrentProgress, 81)

            #Look for the configuration file, based on which SetConfig() function we're about to run.
            if BootloaderToInstall == "GRUB2":
                #Check MountPoint/etc/default/grub exists. *** What do we do if it doesn't? Maybe have a template to put there ***
                if os.path.isfile(MountPoint+"/etc/default/grub"):
                    #It does, we'll run the function to set the config now.
                    logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Setting GRUB2-BIOS Configuration...")
                    self.SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")

                #Now Install GRUB2 to the MBR.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Installing GRUB2 to MBR...")
                self.InstallGRUB2ToMBR(PackageManager=PackageManager, MountPoint=MountPoint)

                #Update GRUB.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
                self.UpdateGRUB2(PackageManager=PackageManager, MountPoint=MountPoint)

                #Set the default OS.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
                self.SetGRUB2DefaultOS(OS=OS, PackageManager=PackageManager, MountPoint=MountPoint)

            elif BootloaderToInstall == "GRUB-UEFI":
                #Check MountPoint/etc/default/grub exists. *** What do we do if it doesn't? Maybe have a template to put there ***
                if os.path.isfile(MountPoint+"/etc/default/grub"):
                    #It does, we'll run the function to set the config now.
                    logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Setting GRUB2-UEFI Configuration...")
                    self.SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")

                #Mount the UEFI partition at MountPoint/boot/efi.
                CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint=MountPoint+"/boot/efi") #*** Check it worked! ***

                #Now Install GRUB-UEFI to the UEFI Partition.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Installing GRUB2 to UEFISystemPartition...")
                self.InstallGRUBUEFIToPartition(PackageManager=PackageManager, MountPoint=MountPoint, UEFISystemPartitionMountPoint=MountPoint+"/boot/efi", Arch=Arch)

                #Update GRUB.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
                self.UpdateGRUB2(PackageManager=PackageManager, MountPoint=MountPoint)

                #Make an entry in fstab for the UEFI Partition, if needed.
                HelperBackendTools().WriteFSTABEntryForUEFIPartition(MountPoint=MountPoint, UEFISystemPartition=UEFISystemPartition)

                #Copy and backup EFI files where needed.
                HelperBackendTools().BackupUEFIFiles(MountPoint=MountPoint)
                HelperBackendTools().CopyUEFIFiles(MountPoint=MountPoint)

                #Set the default OS.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
                self.SetGRUB2DefaultOS(OS=OS, PackageManager=PackageManager, MountPoint=MountPoint)

            elif BootloaderToInstall == "LILO":
                #Make LILO's config file.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Making LILO's configuration file...")
                if MountPoint == "":
                    CoreBackendTools().StartThreadProcess(['liloconfig', '-f'], ShowOutput=False)

                else:
                    CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'liloconfig', '-f'], ShowOutput=False)

                #Check the config file exists for lilo. *** What do we do if it doesn't? Check the last command ran successfully ***
                if os.path.isfile(MountPoint+"/etc/lilo.conf"):
                    #It does, we'll run the function to set the config now.
                    logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Setting LILO Configuration...")
                    self.SetLILOConfig(filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)
    
                    #Also, set the OS entries.
                    logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Creating LILO OS Entries...")
                    self.MakeLILOOSEntries(filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                #Now Install LILO to the MBR.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Installing LILO to the MBR...")
                self.InstallLILOToMBR(PackageManager=PackageManager, MountPoint=MountPoint)

            elif BootloaderToInstall == "ELILO":
                #Unmount the UEFI Partition now, and update mtab in the chroot.
                CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                CoreBackendTools().UpdateChrootMtab(MountPoint=MountPoint)

                #Make ELILO's config file.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Making ELILO's configuration file...")
                if MountPoint == "":
                    CoreBackendTools().StartThreadProcess(['elilo', '-b', UEFISystemPartition, '--autoconf'], ShowOutput=False)

                else:
                    CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'elilo', '-b', UEFISystemPartition, '--autoconf'], ShowOutput=False)

                #Check elilo's config file exists. *** What do we do if it doesn't? Check the last command ran successfully ***
                if os.path.isfile(MountPoint+"/etc/elilo.conf"):
                    #It does, we'll run the function to set the config now.
                    logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Setting ELILO Configuration...")
                    self.SetELILOConfig(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                    #Also, set the OS entries.
                    logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Creating ELILO OS Entries...")
                    self.MakeLILOOSEntries(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                #Now Install ELILO to the UEFI Partition.
                logger.info("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Installing ELILO to UEFISystemPartition...")
                self.InstallELILOToPartition(PackageManager=PackageManager, MountPoint=MountPoint, UEFISystemPartitionMountPoint=MountPoint+"/boot/efi", Arch=Arch)

                #Mount the UEFI partition at MountPoint/boot/efi.
                CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint=MountPoint+"/boot/efi") #*** Check it worked! ***

                #Copy and backup UEFI files where needed.
                HelperBackendTools().BackupUEFIFiles(MountPoint=MountPoint)
                HelperBackendTools().CopyUEFIFiles(MountPoint=MountPoint)

            #Unmount the partition, if needed.
            if MountPoint != "":
                #Tear down chroot.
                CoreBackendTools().TearDownChroot(MountPoint=MountPoint)
                CoreTools().Unmount(MountPoint) #*** Check it worked! ***

            wx.CallAfter(ParentWindow.UpdateOutputBox, "\n###Finished setting the new bootloader's config for OS: "+OS+"...###\n")

        logger.debug("SetBootloaderConfigTools: Main().SetNewBootloaderConfig(): Finished setting bootloader config.")
        wx.CallAfter(ParentWindow.UpdateCurrentOpText, Message="Finished setting the new bootloader's config!")
        wx.CallAfter(ParentWindow.UpdateCurrentProgress, 100)

    def SetGRUB2Config(self, filetoopen): #*** Add logging stuff ***
        """Set GRUB2 config."""
        SetTimeout = False
        SetKOpts = False
        SetDefault = False

        #Open the file in read mode, so we can find the new config that needs setting. Also, use a list to temporarily store the modified lines.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the timeout setting.
            if 'GRUB_TIMEOUT' in line and '=' in line:
                #Found it! Set the value to the current value of BootloaderTimeout.
                SetTimeout = True
                head, sep, Temp = line.partition('=')
                Temp = unicode(BootloaderTimeout)

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Look for kernel options setting.
            elif 'GRUB_CMDLINE_LINUX_DEFAULT' in line and '=' in line:
                #Found it! Set it to the options in KernelOptions, carefully making sure we aren't double-quoting it.
                SetKOpts = True
                head, sep, Temp = line.partition('=')

                #Reassemble the line.
                line = head+sep+"'"+KernelOptions+"'"+"\n"

            #Look for the "GRUB_DEFAULT" setting.
            elif "GRUB_DEFAULT" in line and '=' in line:
                #Found it. Set it to 'saved', so we can set the default bootloader.
                SetDefault = True
                head, sep, Temp = line.partition('=')
                Temp = "saved"

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Comment out the GRUB_HIDDEN_TIMEOUT line.
            elif 'GRUB_HIDDEN_TIMEOUT' in line and 'GRUB_HIDDEN_TIMEOUT_QUIET' not in line and '=' in line and '#' not in line:
                line = "#"+line

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetTimeout == False:
            NewFileContents.append("GRUB_TIMEOUT="+unicode(BootloaderTimeout)+"\n")

        if SetKOpts == False:
            Temp = KernelOptions.replace('\"', '').replace("\'", "").replace("\n", "")
            NewFileContents.append("GRUB_CMDLINE_LINUX_DEFAULT='"+Temp+"'\n")

        if SetDefault == False:
            NewFileContents.append("GRUB_DEFAULT=saved")

        #Write the finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

    def InstallGRUB2ToMBR(self, PackageManager, MountPoint): #*** Needs to change when we switch to always using shell=True ***
        """Install GRUB2 (BIOS version) into the MBR of the hard drive"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the MBR.
        #Use --force to make sure grub installs itself, even on a GPT disk with no bios boot partition. *** Do we always want to do that? ***
        if MountPoint == "":
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['grub-install', '--force', RootDevice], ShowOutput=False)

        else:
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'grub-install', '--force', RootDevice], ShowOutput=False)

        #Return the return value.
        return retval
