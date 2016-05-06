#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Configuration Setting Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 2.0~pre1
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

class Main(): #*** Refactor all of these *** *** Add recovery boot options for LILO/ELILO *** *** Check if LILO installs on GPT disks (GRUB does) ***
    def SetGRUB2Config(self, filetoopen):
        """Set GRUB2 config."""
        logger.info("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Setting GRUB2 Config in "+filetoopen+"...")
        SetTimeout = False
        SetKOpts = False
        SetDefault = False

        #Open the file in read mode, so we can find the new config that needs setting. Also, use a list to temporarily store the modified lines.
        logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Attempting to modify existing lines in the config file first, without making any new ones...")
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the timeout setting.
            if 'GRUB_TIMEOUT' in line and '=' in line:
                #Found it! Set the value to the current value of BootloaderTimeout.
                logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Found GRUB_TIMEOUT, setting it to '"+unicode(BootloaderTimeout)+"'...")
                SetTimeout = True
                head, sep, Temp = line.partition('=')
                Temp = unicode(BootloaderTimeout)

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Look for kernel options setting.
            elif 'GRUB_CMDLINE_LINUX_DEFAULT' in line and '=' in line:
                #Found it! Set it to the options in KernelOptions, carefully making sure we aren't double-quoting it.
                logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Found GRUB_CMDLINE_LINUX_DEFAULT, setting it to '"+KernelOptions+"'...")
                SetKOpts = True
                head, sep, Temp = line.partition('=')

                #Reassemble the line.
                line = head+sep+"'"+KernelOptions+"'"+"\n"

            #Look for the "GRUB_DEFAULT" setting.
            elif "GRUB_DEFAULT" in line and '=' in line:
                #Found it. Set it to 'saved', so we can set the default bootloader.
                logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Found GRUB_DEFAULT, setting it to 'saved'...")
                SetDefault = True
                head, sep, Temp = line.partition('=')
                Temp = "saved"

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Comment out the GRUB_HIDDEN_TIMEOUT line.
            elif 'GRUB_HIDDEN_TIMEOUT' in line and 'GRUB_HIDDEN_TIMEOUT_QUIET' not in line and '=' in line and '#' not in line:
                logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Commenting out GRUB_HIDDEN_TIMEOUT/GRUB_HIDDEN_TIMEOUT_QUIET...")
                line = "#"+line

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetTimeout == False:
            logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Didn't find GRUB_TIMEOUT in config file. Creating and setting it to '"+unicode(BootloaerTimeout)+"'...")
            NewFileContents.append("GRUB_TIMEOUT="+unicode(BootloaderTimeout)+"\n")

        if SetKOpts == False:
            Temp = KernelOptions.replace('\"', '').replace("\'", "").replace("\n", "")
            logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Didn't find GRUB_CMDLINE_LINUX_DEFAULT in config file. Creating and setting it to '"+KernelOptions+"'...")
            NewFileContents.append("GRUB_CMDLINE_LINUX_DEFAULT='"+Temp+"'\n")

        if SetDefault == False:
            logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Didn't find GRUB_DEFAULT in config file. Creating and setting it to 'saved'...")
            NewFileContents.append("GRUB_DEFAULT=saved")

        #Write the finished lines to the file.
        logger.info("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Writing new config to file...")
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

        logger.info("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Done!")

    def InstallGRUB2ToMBR(self, PackageManager, MountPoint): #*** Will need changing when we get rid of the Root Device concept ***
        """Install GRUB2 (BIOS version) into the MBR of the hard drive"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the MBR.
        #Use --force to make sure grub installs itself, even on a GPT disk with no bios boot partition. *** Do we want to do that? ***
        if PackageManager == "apt-get":
            Cmd = "grub-install --force "+RootDevice

        if MountPoint != "":
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval

    def InstallGRUBUEFIToPartition(self, PackageManager, MountPoint, UEFISystemPartitionMountPoint, Arch): #*** Change the name to "InstallGRUB2ToEFIPartition" ***
        """Install GRUB2 (EFI/UEFI version) into the EFI/UEFI partition"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if Arch == "64-bit":
            GRUBArch = "x86_64"

        else:
            GRUBArch = "i386"

        if PackageManager == "apt-get":
            Cmd = "grub-install --efi-directory="+UEFISystemPartitionMountPoint+" --target="+GRUBArch+"-efi"

        if MountPoint != "":
            Cmd = "chroot "+MountPoint+" "+Cmd
 
        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval

    def UpdateGRUB2(self, PackageManager, MountPoint):
        """Run 'update-grub' to update GRUB2's (BIOS and EFI/UEFI) configuration and bootloader menu"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if PackageManager == "apt-get":
            Cmd = "update-grub"

        if MountPoint != "":
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval

    def SetGRUB2DefaultOS(self, OS, MountPoint): #*** Make this more user-friendly ***
        """Set GRUB2's (both BIOS and EFI/UEFI) default OS to boot"""
        #I couldn't find a reliable way of doing this automatically, so give the user a choice box instead. *** Do this before release of final v2.0, probably in the 1st or 2nd rc. Maybe use disk names and save grub's name for each one ***
        logger.info("BootloaderConfigSettingTools: Main().SetGRUB2DefaultOS(): Setting GRUB2's Default OS...")

        #Make a list of OSs grub2 found (hopefully all of them).
        logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2DefaultOS(): Finding GRUB2's menu entries...")
        GrubConfigFilePath = "/boot/grub/grub.cfg"

        if MountPoint != "":
            GrubConfigFilePath = MountPoint+GrubConfigFilePath

        GrubMenuEntries = []

        if OSInfo[OS]["PackageManager"] == "apt-get":
            GrubConfigFile = open(GrubConfigFilePath, "r")
            GrubConfig = GrubConfigFile.read()
            GrubConfigFile.close()

        for Line in GrubConfig.split("\n"):
            if "menuentry " in Line:
                GrubMenuEntries.append(Line)

        if GrubMenuEntries == []:
            #Don't set the default OS. *** There are no menu entries! Why might this happen? ***
            logger.error("BootloaderConfigSettingTools: Main().SetGRUB2DefaultOS(): Couldn't find any menu entries! Warning user and not setting default OS...")
            DialogTools.ShowMsgDlg(Kind="error", Message="WxFixBoot failed to set the default OS. This doesn't really matter. Click okay to continue.")
            return 1

        #Now finally make the list of grub's OS names.
        logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2DefaultOS(): Done! Getting GRUB's OS Names...")
        GRUBOSNameList = []

        for OSName in GrubMenuEntries:
            #Get each OS name, removing all of the unneeeded stuff.
            try:
                GRUBOSNameList.append(OSName.split("\'")[1])

            except IndexError:
                GRUBOSNameList.append(OSName.split("\"")[1])

        #Now ask the user to select the correct one.
        logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2DefaultOS(): Done! Asking user to choose a default OS...")
        DefaultOS = DialogTools.ShowChoiceDlg(Message="Please select the OS you want to use as "+SystemInfo["BootloaderToInstall"]+"'s Default OS. You are setting configuration for: "+OS, Title="WxFixBoot - Select Default OS", Choices=GRUBOSNameList)

        logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2DefaultOS(): User chose "+DefaultOS+". Setting default OS...")
        #Use the user's selection to set the default OS.
        if OSInfo[OS]["PackageManager"] == "apt-get":
            Cmd = "grub-set-default '"+DefaultOS+"'"

        if not (SystemInfo["IsLiveDisk"] == False and MountPoint == ""):
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        logger.info("BootloaderConfigSettingTools: Main().SetGRUB2DefaultOS(): Done!")
        return Retval

    def SetLILOConfig(self, filetoopen, PackageManager, MountPoint):
        """Set LILO's config."""
        logger.info("BootloaderConfigSettingTools: Main().SetLILOConfig(): Setting LILO config in "+filetoopen+"...")
        SetTimeout = False
        SetBootDevice = False

        #Open the file in read mode, so we can find the important bits of config to edit. Also, use a list to temporarily store the modified lines.
        logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Attempting to modify existing lines in the config file first, without creating any new ones...")
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the timeout setting.
            if 'timeout' in line and '=' in line and '#' not in line:
                #Found it! Set it to our value.
                logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Found timeout setting, setting it to "+unicode(BootloaderTimeout)+"...")
                SetTimeout = True

                #Save it, carefully avoiding errors.
                head, sep, Temp = line.partition('=')
                Temp = unicode(BootloaderTimeout*10)

                #Reassemble the line.
                line = "timeout"+sep+Temp+"\n"

            #Look for the 'boot' setting.
            elif 'boot' in line and '=' in line and '#' not in line and 'map' not in line: 
                #Found it, seperate the line.
                logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Found boot setting, setting it to "+RootDevice+"'s ID if possible, else just "+RootDevice+"...")
                SetBootDevice = True
                head, sep, Temp = line.partition('=')

                if DiskInfo[RootDevice]["ID"] != "Unknown":
                    #Good, we've got the ID.
                    logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Setting boot to /dev/disk/by-id/"+DiskInfo[RootDevice]["ID"]+"...")

                    #Set it to RootDevice's ID.                    
                    Temp = "/dev/disk/by-id/"+DiskInfo[RootDevice]["ID"]

                else:
                    #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
                    logger.warning("BootloaderConfigSettingTools: Main().SetLILOConfig(): We don't have the ID! Setting boot to "+RootDevice+". This may cause problems if the device name changes!")
                    Temp = RootDevice

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetTimeout == False:
            logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Didn't find timeout in config file. Creating it and setting it to "+unicode(BootloaderTimeout)+"...")
            NewFileContents.append("timeout="+unicode(BootloaderTimeout)+"\n")

        if SetBootDevice == False:
            #Now let's find the ID of RootDevice.
            logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Didn't find boot setting in config file. Creating it and setting it to "+RootDevice+"'s ID if possible, else just "+RootDevice+"...")

            if DiskInfo[RootDevice]["ID"] != "Unknown":
                #Good, we've got the ID.
                logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Setting boot to /dev/disk/by-id/"+DiskInfo[RootDevice]["ID"]+"...")

                #Set it to RootDevice's ID.                    
                Temp = "/dev/disk/by-id/"+DiskInfo[RootDevice]["ID"]

            else:
                #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
                logger.warning("BootloaderConfigSettingTools: Main().SetLILOConfig(): Setting boot to "+RootDevice+"! This may cause problems if the device name changes!")
                Temp = RootDevice

            NewFileContents.append("boot="+Temp+"\n")

        #Write the finished lines to the file.
        logger.info("BootloaderConfigSettingTools: Main().SetLILOConfig(): Writing new config to file...")
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

        logger.info("BootloaderConfigSettingTools: Main().SetLILOConfig(): Done!")

    def SetELILOConfig(self, filetoopen, PackageManager, MountPoint):
        """Set ELILO config."""
        logger.info("BootloaderConfigSettingTools: Main().SetELILOConfig(): Setting ELILO config in "+filetoopen+"...")
        SetTimeout = False
        SetUEFIPart = False

        #Open the file in read mode, so we can find the important bits of config to edit. Also, use a list to temporarily store the modified lines.
        logger.debug("BootloaderConfigSettingTools: Main().SetELILOConfig(): Attempting to modify existing lines in the config file first, without creating any new ones...")
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the delay setting.
            if 'delay' in line and '=' in line and '#' not in line:
                #Found it! Set it to our value.
                logger.debug("BootloaderConfigSettingTools: Main().SetELILOConfig(): Found delay setting, setting it to "+unicode(BootloaderTimeout*10)+" (tenths of a second)...") 
                SetTimeout = True

                #Save it, carefully avoiding errors.
                head, sep, Temp = line.partition('=')
                Temp = unicode(BootloaderTimeout*10)

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Look for the 'boot' setting.
            elif 'boot' in line and '=' in line and '#' not in line:
                #Found it, seperate the line.
                logger.debug("BootloaderConfigSettingTools: Main().SetELILOConfig(): Found boot setting, setting it to "+UEFISystemPartition+"'s ID if possible, else just "+UEFISystemPartition+"...")
                SetUEFIPart = True
                head, sep, Temp = line.partition('=')

                if DiskInfo[UEFISystemPartition]["ID"] != "Unknown":
                    #Good, we've got the ID.
                    logger.debug("BootloaderConfigSettingTools: Main().SetELILOConfig(): Setting boot to /dev/disk/by-id/"+DiskInfo[UEFISystemPartition]["ID"]+"...")

                    #Set it to UEFISystemPartition's ID.                    
                    Temp = "/dev/disk/by-id/"+DiskInfo[UEFISystemPartition]["ID"]

                else:
                    #Not so good... We'll have to use the partition's name, which may change, especially if we're using chroot.
                    logger.warning("BootloaderConfigSettingTools: Main().SetELILOConfig(): We don't have the ID! Setting boot to "+UEFISystemPartition+". This may cause problems if the device name changes!")
                    Temp = UEFISystemPartition

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Get rid of any boot entries.
            elif 'image=' in line or '\t' in line:
                #Skip this line, and don't append it to the list.
                logger.debug("BootloaderConfigSettingTools: Main().SetELILOConfig(): Found boot entry, removing it...")
                continue

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetTimeout == False:
            logger.debug("BootloaderConfigSettingTools: Main().SetELILOConfig(): Didn't find delay in config file. Creating it and setting it to "+unicode(BootloaderTimeout*10)+" (tenths of a second)...")
            NewFileContents.append("delay="+unicode(BootloaderTimeout)+"\n")

        if SetUEFIPart == False:
            #Now let's find the ID of UEFISystemPartition.
            logger.debug("BootloaderConfigSettingTools: Main().SetELILOConfig(): Didn't find boot setting in config file. Creating it and setting it to "+UEFISystemPartition+"'s ID if possible, else just "+UEFISystemPartition+"...")

            if DiskInfo[UEFISystemPartition]["ID"] != "Unknown":
                #Good, we've got the ID.
                logger.debug("BootloaderConfigSettingTools: Main().SetELILOConfig(): Setting boot to /dev/disk/by-id/"+DiskInfo[UEFISystemPartition]["ID"]+"...")

                #Set it to UEFISystemPartition's ID.                    
                Temp = "/dev/disk/by-id/"+DiskInfo[UEFISystemPartition]["ID"]

            else:
                #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
                logger.warning("BootloaderConfigSettingTools: Main().SetELILOConfig(): We don't have the ID! Setting boot to "+UEFISystemPartition+". This may cause problems if the device name changes!")
                Temp = UEFISystemPartition

            NewFileContents.append("boot="+Temp+"\n")

        #Write the finished lines to the file.
        logger.info("BootloaderConfigSettingTools: Main().SetELILOConfig(): Writing new config to file...")
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()
        logger.info("BootloaderConfigSettingTools: Main().SetELILOConfig(): Done!")

    def MakeLILOOSEntries(self, filetoopen, PackageManager, MountPoint): #*** Maybe set default OS in a separate function? *** *** FIX THIS LATER, IT DOESN'T WORK! *** *** Actually, it seems to be working now??? ***
        """Make OS Entries in the bootloader menu for LILO and ELILO, and then the default OS"""
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Preparing to make OS entries for "+SystemInfo["BootloaderToInstall"]+"...")
        #Okay, we've saved the kopts, timeout, and the boot device in the list.
        #Now we'll set the OS entries, and then the default OS.
        #Open the file, and add each entry to a temporary list, which will be written to the file later.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #First, make sure everything else comes first, because LILO and ELILO are picky with the placement of the image files (they must be at the end of the file).
        #We'll also make a placeholder for the default OS, so it comes before the image entries too.
        logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Making placeholder for default OS if needed...")

        Temp = False

        for line in ConfigFile:
            if 'default' in line and '=' in line and '#' not in line:
                #The place holder already exists. Set a variable so we don't make one.
                Temp = True

            NewFileContents.append(line)

        #If there isn't a placeholder, make one now.
        if Temp == False:
            NewFileContents.append("default=setthis\n")

        #Make the OS entries.
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Making OS Entries...")

        if SystemInfo["BootloaderToInstall"] == "ELILO":
            NewFileContents.append("#################### ELILO per-image section ####################")

        #As we make these entries, we'll record which ones were actually made, as the user can cancel them if it looks like it won't work.
        CompletedEntriesList = []

        Keys = OSInfo.keys()
        Keys.sort()

        for OS in Keys:
            logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Preparing to make an entry for: "+OS)

            #Names in LILO are not allowed to have spaces, so let's remove the spaces from them.
            OSName = OS.replace(' ','')

            #Grab the OS's partition.
            Partition = OSInfo[OS]["Partition"]

            #Check that the name is no longer than 15 characters.
            if len(OSName) > 15:
                #The name is too long! Truncate it to 15 characters.
                logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Truncating OS Name: "+OSName+" to 15 characters...")
                OSName = OSName[0:15]

            #Now let's make the entries.
            logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Checking for /vmlinuz and /initrd.img...")

            CurrentOS = OSInfo[OS]["IsCurrentOS"]

            #Check that MountPoint/vmlinuz and MountPoint/initrd.img exist. (If this is the current OS, MountPoint = "", and so doesn't get in the way).
            if os.path.isfile(MountPoint+"/vmlinuz"):
                #Good, add this to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Found /vmlinuz! Adding it to the config file...")
                NewFileContents.append("\nimage=/vmlinuz\n")

            else:
                #We can't make an entry for this OS. Warn the user. *** Check this beforehand ***
                logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Couldn't find /vmlinuz for: "+OS+"! Telling the user we can't make an entry...")

                Result = DialogTools.ShowMsgDlg(Message="Warning: /vmlinuz (shortcut to the latest kernel) wasn't found for: "+OS+"! Unfortunately, this means WxFixBoot can't make a bootloader entry for this OS. Click okay to continue.", Kind="Warning")
                continue

            if os.path.isfile(MountPoint+"/initrd.img"):
                #Good, add this to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Found /initrd.img! Adding it to the config file...")
                NewFileContents.append("\tinitrd=/initrd.img\n")

            else:
                #We can't make an entry for this OS. Warn the user. *** Check this beforehand ***
                logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Couldn't find /initrd.img for "+OS+"! Telling the user we can't make an entry...")

                Result = DialogTools.ShowMsgDlg(Message="Warning: /initrd.img (shortcut to the latest Initial Filesystem) wasn't found for: "+OS+"! Unfortunately, this means WxFixBoot can't make a bootloader entry for this OS. Click okay to continue.", Title="WxFixBoot - Add OS to boot menu?")

                #Okay, delete the last entry, so we don't have an unconfigured image, and then go back to the start of the loop.
                logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Deleting the unconfigured image, and skipping this OS...")
                Temp = NewFileContents.pop()
                continue

            #Set the root device.
            #Use UUID's here if we can.
            logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS rootfs as a UUID if possible...")

            if SystemInfo["BootloaderToInstall"] == "ELILO": #*** Test this works ***
                if DiskInfo[UEFISystemPartition]["UUID"] == "Unknown": #*** Warn user? ***
                    logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS rootfs to "+UEFISystemPartition+"! This might not work cos it can change!")
                    NewFileContents.append("\troot="+Partition+"\n")

                else:
                    logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS rootfs to "+DiskInfo[UEFISystemPartition]["UUID"]+"...")
                    NewFileContents.append("\troot=UUID="+DiskInfo[Partition]["UUID"]+"\n")

            else:
                if DiskInfo[Partition]["UUID"] == "Unknown": #*** Warn user? ***
                    logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS rootfs to "+Partition+"! This might not work cos it can change!")
                    NewFileContents.append("\troot="+Partition+"\n")

                else:
                    logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS rootfs to "+DiskInfo[Partition]["UUID"]+"...")
                    NewFileContents.append("\troot=\"UUID="+DiskInfo[Partition]["UUID"]+"\"\n")

            #Set the label.
            logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS label to "+OSName+"...")
            NewFileContents.append("\tlabel="+OSName+"\n")

            #Set the kernel options.
            logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS Kernel Options to "+KernelOptions+"...")
            NewFileContents.append("\tappend=\""+KernelOptions+"\"\n")

            #Set one other necessary boot option.
            logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Adding 'read-only' to mount rootfs in ro mode on startup...")
            NewFileContents.append("\tread-only\n")

            #Add this OS to the Completed Entries List, because if we got this far it's done and added.
            logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): OS Entry for "+OS+" is done!")
            CompletedEntriesList.append(OSName)

        #Now set the default OS.
        #First, write the semi-finished lines to the file.
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Writing OS Entries and config to file...")
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Done!")

        #Open the file again, with the new files written.
        logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Preparing to set default OS to boot...")
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Remove all of the spaces, truncating the OS name if necessary.
        DefaultOSName = SystemInfo["DefaultOS"].replace(' ','')

        #Check that the name is no longer than 15 characters.
        if len(DefaultOSName) > 15:
            #The name is too long! Truncate it to 15 characters.
            logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Truncating OS Name: "+DefaultOSName+" to 15 characters...")
            DefaultOSName = DefaultOSName[0:15]

        #Now, check if its entry was added to the file, and ask the user for a new one if it wasn't.
        if DefaultOSName not in CompletedEntriesList:
            logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Default OS not in the Completed Entries List! Asking the user for a new one...")

            if len(CompletedEntriesList) <= 0:
                #Something went wrong here! No OSs appear to have been added to the list. Warn the user. *** How about being helpful and trying to fix it right now? :D ***
                logger.error("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): CompletedEntriesList is empty! This suggests that no OSs have been added to the list! Warn the user, and skip this part of the operation.")
                DialogTools.ShowMsgDlg(Kind="error", Message="No Operating Systems have had entries created for them! If you canceled creating the entries, please reboot WxFixBoot and select only the option 'Update Bootloader Config'. If you didn't do that, and WxFixBoot either couldn't create them, or you see this error with no previous warnings, you may have to create your own bootloader config. Don't worry, this isn't too difficult, and you can search for tutorials for this on the internet. If WxFixBoot couldn't create your entries, or you are seeing this message with no previous warnings, please email me directly via my Launchpad page (www.launchpad.net/~hamishmb) with the contents of /tmp/wxfixboot.log and I'll try to help you.")

            else:
                #Ask the user for a new default OS.
                DefaultOSName = DialogTools.ShowChoiceDlg(Message="The OS you previously selected as the default wasn't added to the boot menu. Please an new OS you want to use as "+Bootloader+"'s Default OS. You are setting configuration for: "+OS, Title="WxFixBoot - Select Default OS", Choices=CompletedEntriesList)
                logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): User selected new default OS: "+DefaultOSName+"...")

        #Make the entry for the default OS.
        logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting default OS...")
        SetDefaultOS = False

        for line in ConfigFile:
            if 'default' in line and '=' in line and '#' not in line:
                logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Found default OS setting, setting it to "+DefaultOSName+"...")
                #Get the LILO name for DefaultOS.
                SetDefaultOS = True

                #Set default to the name.
                line = "default="+DefaultOSName+"\n"

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetDefaultOS == False:
            #*** This won't work! *** *** This needs to be before the OS entries in the file! ***
            logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Didn't find default OS setting in config file. Creating it and setting it to "+DefaultOSName+"...")
            logger.error("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): *** This won't work! *** *** This needs to be before the OS entries in the file! ***")
            NewFileContents.append("default="+DefaultOSName+"\n")

        #Write the finished lines to the file.
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Writing finished config to file...")
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Done!")

    def InstallLILOToMBR(self, PackageManager, MountPoint):
        """Install LILO into the MBR."""
        Cmd = "lilo"

        if MountPoint != "":
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval

    def InstallELILOToPartition(self, PackageManager, MountPoint, UEFISystemPartition):
        """Install ELILO to the EFI/UEFI Partition"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if PackageManager == "apt-get":
            Cmd = "elilo -b "+UEFISystemPartition+" --efiboot"

        if MountPoint != "":
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval
