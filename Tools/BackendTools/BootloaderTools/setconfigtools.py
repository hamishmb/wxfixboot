#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Bootloader Configuration Setting Tools in the Bootloader Tools Package in the Backend Tools package for WxFixBoot Version 2.0~rc1
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

class Main(): #*** Add recovery boot options for LILO/ELILO ***
    def SetGRUB2Config(self, OS, filetoopen, BootloaderTimeout, KernelOptions):
        """Set GRUB2 config."""
        logger.info("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Setting GRUB2 Config in "+filetoopen+"...")
        SetTimeout, SetKOpts, SetDefault = (False, False, False)

        #Match the bootloader-specific default OS to WxFixBoot's OSs by partition.
        logger.info("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Attempting to match the WxFixBoot's default OS for this bootloader to any OS that GRUB2 detected...")

        #Find the partition that WxFixBoot's default OS for this bootloader is on. Also find the /boot partition, as grub may point there in the menu entries.
        DefaultBootDevices = (OSInfo[BootloaderInfo[OS]["Settings"]["DefaultOS"]]["Partition"], OSInfo[BootloaderInfo[OS]["Settings"]["DefaultOS"]]["BootPartition"])

        #Find the ID for the menu entry that correspondes to that OS (Main Menu only to avoid recovery options + misc).
        BLSpecificDefaultOS = "Unknown"

        for Entry in BootloaderInfo[OS]["NewMenuEntries"]["MainMenu"]["Order"]:
            if BootloaderInfo[OS]["NewMenuEntries"]["MainMenu"][Entry]["Partition"] in DefaultBootDevices:
                BLSpecificDefaultOS = BootloaderInfo[OS]["NewMenuEntries"]["MainMenu"][Entry]["ID"]
                logger.info("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Found Default OS's GRUB2 ID...")
                break

        #Log if we couldn't match them.
        if BLSpecificDefaultOS == "Unknown":
            logger.warning("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Couldn't match! We will instead pick the 1st menu entry. Warning user...")
            DialogTools.ShowMsgDlg(Message="Couldn't match the default OS you picked to any that "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+" has detected! This doesn't matter, so instead, the first menu entry will be the default. Click okay to continue...")
            BLSpecificDefaultOS = "0"

        #Open the file in read mode, so we can find the new config that needs setting. Also, use a list to temporarily store the modified lines.
        logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Attempting to modify existing lines in the config file first, without making any new ones...")
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the timeout setting.
            if 'GRUB_TIMEOUT' in line and '=' in line and SetTimeout == False:
                #Found it! Set the value to the current value of BootloaderTimeout.
                logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Found GRUB_TIMEOUT, setting it to '"+unicode(BootloaderTimeout)+"'...")
                SetTimeout = True
                line = "GRUB_TIMEOUT="+unicode(BootloaderTimeout)+"\n"

            #Look for kernel options setting.
            elif 'GRUB_CMDLINE_LINUX_DEFAULT' in line and '=' in line and SetKOpts == False:
                #Found it! Set it to the options in KernelOptions, carefully making sure we aren't double-quoting it.
                logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Found GRUB_CMDLINE_LINUX_DEFAULT, setting it to '"+KernelOptions+"'...")
                SetKOpts = True
                line = "GRUB_CMDLINE_LINUX_DEFAULT='"+KernelOptions+"'\n"

            #Look for the "GRUB_DEFAULT" setting.
            elif "GRUB_DEFAULT" in line and '=' in line and SetDefault == False:
                #Found it. Set it to 'saved', so we can set the default bootloader.
                logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Found GRUB_DEFAULT, setting it to '"+BLSpecificDefaultOS+"' (ID of default OS)...")
                SetDefault = True
                line = "GRUB_DEFAULT="+BLSpecificDefaultOS+"\n"

            #Comment out the GRUB_HIDDEN_TIMEOUT line.
            elif 'GRUB_HIDDEN_TIMEOUT' in line and 'GRUB_HIDDEN_TIMEOUT_QUIET' not in line and '=' in line and '#' not in line:
                logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Commenting out GRUB_HIDDEN_TIMEOUT...")
                line = "#"+line

            #Comment out the GRUB_CMDLINE_LINUX line.
            elif 'GRUB_CMDLINE_LINUX' in line and 'GRUB_CMDLINE_LINUX_DEFAULT' not in line and '=' in line and '#' not in line:
                logger.debug("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Commenting out GRUB_CMDLINE_LINUX...")
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
            NewFileContents.append("GRUB_DEFAULT="+BLSpecificDefaultOS+"\n")

        #Write the finished lines to the file.
        logger.info("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Writing new config to file...")
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

        logger.info("BootloaderConfigSettingTools: Main().SetGRUB2Config(): Done!")

    def InstallGRUB2ToMBR(self, PackageManager, UseChroot, MountPoint, Device):
        """Install GRUB2 (BIOS version) into the MBR of the hard drive"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the MBR.
        #Use --force to make sure grub installs itself, even on a GPT disk with no bios boot partition.
        #Can flag as a warning on Fedora systems when just updating, but ignore it.
        if PackageManager == "apt-get":
            Cmd = "grub-install --force "+Device

        elif PackageManager == "yum":
            Cmd = "grub2-install --force "+Device

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval

    def InstallGRUB2ToEFIPartition(self, PackageManager, UseChroot, MountPoint, UEFISystemPartitionMountPoint, Arch):
        """Install GRUB2 (EFI/UEFI version) into the EFI/UEFI partition"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if PackageManager == "apt-get":
            Cmd = "grub-install --efi-directory="+UEFISystemPartitionMountPoint+" --target="+Arch+"-efi"

        elif PackageManager == "yum":
            Cmd = "grub2-install --efi-directory="+UEFISystemPartitionMountPoint+" --target="+Arch+"-efi"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd
 
        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval

    def UpdateGRUB2(self, OS, PackageManager, UseChroot, MountPoint):
        """Run 'update-grub' to update GRUB2's (BIOS and EFI/UEFI) configuration and bootloader menu"""
        #We need to update grub.
        if PackageManager == "apt-get":
            Cmd = "update-grub2"

        elif PackageManager == "yum" and OSInfo[OS]["EFIPartition"] == "Unknown":
            Cmd = "grub2-mkconfig -o /boot/grub2/grub.cfg"

        elif PackageManager == "yum":
            Cmd = "grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval

    def SetLILOConfig(self, OS, filetoopen):
        """Set config for both LILO and ELILO"""
        logger.info("BootloaderConfigSettingTools: Main().SetLILOConfig(): Setting LILO config in "+filetoopen+"...")
        SetTimeout, SetBootDevice = (False, False)

        #Find the ID for the boot device if possible.
        logger.info("BootloaderConfigSettingTools: Main().SetLILOConfig(): Getting ID for boot device...")
        if DiskInfo[BootloaderInfo[OS]["BootDisk"]]["ID"] != "Unknown":
            #Good, we've got the ID.
            logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Found ID /dev/disk/by-id/"+DiskInfo[BootloaderInfo[OS]["BootDisk"]]["ID"]+"...")

            #Set it to RootDevice's ID.                    
            BootDevice = "/dev/disk/by-id/"+DiskInfo[BootloaderInfo[OS]["BootDisk"]]["ID"]

        else:
            #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
            logger.warning("BootloaderConfigSettingTools: Main().SetLILOConfig(): We don't have the ID! Using "+BootloaderInfo[OS]["BootDisk"]+" instead. This may cause problems if the device name changes!")
            BootDevice = BootloaderInfo[OS]["BootDisk"]

        #Open the file in read mode, so we can find the important bits of config to edit. Also, use a list to temporarily store the modified lines.
        logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Attempting to modify existing lines in the config file first, without creating any new ones...")
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the timeout setting (ELILO).
            if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "ELILO" and 'delay' in line and '=' in line and '#' not in line and SetTimeout == False:
                #Found it! Set it to our value.
                logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Found timeout setting, setting it to "+unicode(BootloaderInfo[OS]["Settings"]["NewTimeout"])+"...") 
                SetTimeout = True

                #Also set prompt to use the text menu, chooser to textmenu, and the text menu file.
                logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Setting up ELILO's text menu...")
                NewFileContents.append("prompt\n")
                NewFileContents.append("chooser=textmenu\n")
                NewFileContents.append("message=elilomenu.msg\n")

                line = "delay="+unicode(BootloaderInfo[OS]["Settings"]["NewTimeout"]*10)+"\n"

            #Look for the timeout setting (LILO).
            elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "LILO" and 'timeout' in line and '=' in line and '#' not in line and SetTimeout == False:
                #Found it! Set it to our value.
                logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Found timeout setting, setting it to "+unicode(BootloaderInfo[OS]["Settings"]["NewTimeout"])+"...")
                SetTimeout = True
                line = "timeout="+unicode(BootloaderInfo[OS]["Settings"]["NewTimeout"]*10)+"\n"

            #Look for the 'boot' setting.
            elif 'boot' in line and '=' in line and '#' not in line and 'map' not in line and SetBootDevice == False: 
                #Found it, seperate the line.
                logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Found boot setting, setting it to "+BootDevice+"...")
                SetBootDevice = True

                #Reassemble the line.
                line = "boot="+BootDevice+"\n"

            #Get rid of any boot entries.
            elif 'image=' in line or '\t' in line:
                #Skip this line, and don't append it to the list.
                logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Found boot entry, removing it...")
                continue

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "ELILO" and SetTimeout == False:
            logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Didn't find timeout in config file. Creating it and setting it to "+unicode(BootloaderInfo[OS]["Settings"]["NewTimeout"])+"...")

            #Also set prompt to use the text menu, chooser to textmenu, and the text menu file.
            logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Setting up ELILO's text menu...")
            NewFileContents.append("prompt\n")
            NewFileContents.append("chooser=textmenu\n")
            NewFileContents.append("message=elilomenu.msg\n")

            NewFileContents.append("delay="+unicode(BootloaderInfo[OS]["Settings"]["NewTimeout"])+"\n")

        elif BootloaderInfo[OS]["Settings"]["NewBootloader"] == "LILO" and SetTimeout == False:
            logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Didn't find timeout in config file. Creating it and setting it to "+unicode(BootloaderInfo[OS]["Settings"]["NewTimeout"])+"...")
            NewFileContents.append("timeout="+unicode(BootloaderInfo[OS]["Settings"]["NewTimeout"])+"\n")

        if SetBootDevice == False:
            #Now let's find the ID of RootDevice.
            logger.debug("BootloaderConfigSettingTools: Main().SetLILOConfig(): Didn't find boot setting in config file. Creating it and setting it to "+BootDevice+"...")
            NewFileContents.append("boot="+BootDevice+"\n")

        #Write the finished lines to the file.
        logger.info("BootloaderConfigSettingTools: Main().SetLILOConfig(): Writing new config to file...")
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

        logger.info("BootloaderConfigSettingTools: Main().SetLILOConfig(): Done!")

    def MakeLILOOSEntries(self, OS, filetoopen, MountPoint, KernelOptions):
        """Make OS Entries in the bootloader menu for LILO and ELILO, and then the default OS"""
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Preparing to make OS entries for "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"...")
        #Okay, we've saved the kopts, timeout, and the boot device in the list.
        #Now we'll set the OS entries, and then the default OS.
        #Open the file, and add each entry to a temporary list, which will be written to the file later.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #First, make sure everything else comes first, because LILO and ELILO are picky with the placement of the image files (they must be at the end of the file).
        #We'll also make a placeholder for the default OS, so it comes before the image entries too.
        #Also remove existing entries first.
        logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Making placeholder for default OS if needed...")

        Temp = False

        for line in ConfigFile:
            if 'default' in line and '=' in line and '#' not in line:
                #The place holder already exists. Set a variable so we don't make one.
                Temp = True

            elif ("image" in line or "initrd" in line or "label" in line) and "=" in line:
                continue

            elif "read-only" in line or "read-write" in line:
                continue

            NewFileContents.append(line)

        #If there isn't a placeholder, make one now.
        if Temp == False:
            NewFileContents.append("default=setthis\n")

        #Make the OS entries.
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Making OS Entries...")

        if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "ELILO":
            NewFileContents.append("#################### ELILO per-image section ####################")

        #As we make these entries, we'll record which ones were actually made, as the user can cancel them if it looks like it won't work.
        CompletedEntriesList = []

        Keys = OSInfo.keys()
        Keys.sort()

        for OS in Keys:
            logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Preparing to make an entry for: "+OS)

            if not os.path.isfile(MountPoint+"/vmlinuz") or not os.path.isfile(MountPoint+"/initrd.img"):
                #We can't make an entry for this OS. Warn the user.
                logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Couldn't find /vmlinuz or /initrd.img for "+OS+"! Telling the user we can't make an entry...")

                Result = DialogTools.ShowMsgDlg(Message="Warning: The shortcut to the latest kernel or initrd weren't found for "+OS+"! Unfortunately, this means WxFixBoot can't make a bootloader entry for this OS. Click okay to continue.", Kind="Warning")

                continue

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

            #Set kernel and initrd.
            logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Adding /vmlinuz to the config file...")
            NewFileContents.append("\nimage=/vmlinuz\n")

            logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Adding /initrd.img to the config file...")
            NewFileContents.append("\tinitrd=/initrd.img\n")

            #Set the root device.
            #Use UUID's here if we can.
            logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS rootfs as a UUID if possible...")

            if DiskInfo[OSInfo[OS]["Partition"]]["UUID"] == "Unknown":
                logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS rootfs to "+OSInfo[OS]["Partition"]+"! This might not work cos it can change!")
                NewFileContents.append("\troot="+OSInfo[OS]["Partition"]+"\n")

            else:
                logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting OS rootfs to "+DiskInfo[OSInfo[OS]["Partition"]]["UUID"]+"...")

                if BootloaderInfo[OS]["Settings"]["NewBootloader"] == "ELILO":
                    NewFileContents.append("\troot=UUID="+DiskInfo[OSInfo[OS]["Partition"]]["UUID"]+"\n")

                else:
                    NewFileContents.append("\troot=\"UUID="+DiskInfo[OSInfo[OS]["Partition"]]["UUID"]+"\"\n")

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
        DefaultOSName = BootloaderInfo[OS]["Settings"]["DefaultOS"].replace(' ','')

        #Check that the name is no longer than 15 characters.
        if len(DefaultOSName) > 15:
            #The name is too long! Truncate it to 15 characters.
            logger.warning("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Truncating OS Name: "+DefaultOSName+" to 15 characters...")
            DefaultOSName = DefaultOSName[0:15]

        #Now, check if its entry was added to the file, and ask the user for a new one if it wasn't.
        if DefaultOSName not in CompletedEntriesList:
            logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Default OS not in the Completed Entries List! Asking the user for a new one...")

            if len(CompletedEntriesList) <= 0:
                #Something went wrong here! No OSs appear to have been added to the list. Warn the user.
                logger.error("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): CompletedEntriesList is empty! This suggests that no OSs have been added to the list! Warn the user, and skip this part of the operation.")
                DialogTools.ShowMsgDlg(Kind="error", Message="No Operating Systems have had entries created for them! If you canceled creating the entries, please reboot WxFixBoot and select only the option 'Update Bootloader Config'. If you didn't do that, and WxFixBoot either couldn't create them, or you see this error with no previous warnings, you may have to create your own bootloader config. If you wish to, you can email me directly via my Launchpad page (www.launchpad.net/~hamishmb) with the contents of /tmp/wxfixboot.log and I'll help you do that.")

            else:
                #Ask the user for a new default OS.
                DefaultOSName = DialogTools.ShowChoiceDlg(Message="The OS you previously selected as the default wasn't added to the boot menu. Please select a new OS you want to use as "+BootloaderInfo[OS]["Settings"]["NewBootloader"]+"'s Default OS. You are setting configuration for "+OS, Title="WxFixBoot - Select Default OS", Choices=CompletedEntriesList)
                logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): User selected new default OS: "+DefaultOSName+"...")

        #Make the entry for the default OS.
        logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Setting default OS...")
        SetDefaultOS = False

        for line in ConfigFile:
            if 'default' in line and '=' in line and '#' not in line:
                logger.debug("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Found default OS setting, setting it to "+DefaultOSName+"...")
                line = "default="+DefaultOSName+"\n"

            NewFileContents.append(line)

        #Write the finished lines to the file.
        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Writing finished config to file...")
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

        logger.info("BootloaderConfigSettingTools: Main().MakeLILOOSEntries(): Done!")

    def InstallLILOToMBR(self, PackageManager, UseChroot, MountPoint):
        """Install LILO into the MBR."""
        Cmd = "lilo"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval

    def InstallELILOToPartition(self, OS, PackageManager, UseChroot, MountPoint):
        """Install ELILO to the EFI/UEFI Partition"""
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if PackageManager == "apt-get":
            Cmd = "elilo -b "+BootloaderInfo[OS]["BootDisk"]+" --efiboot"

        if UseChroot:
            Cmd = "chroot "+MountPoint+" "+Cmd

        Retval = CoreTools.StartProcess(Cmd, ShowOutput=False)

        #Return the return value.
        return Retval
