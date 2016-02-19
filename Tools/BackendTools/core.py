#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Backend Tools in the BackendTools Package for WxFixBoot Version 1.1~pre1
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
class Main(): #*** These need refactoring and proper testing ***
    def StartThreadProcess(self, ExecCmds, Piping=False, ShowOutput=True, ReturnOutput=False): #*** Get rid of this in favour of CoreTools().StartProcess() ***
        """Start a process given a list with commands to execute, specifically for this thread, as it also sends the output to ParentWindow.UpdateOutputBox()."""
        #This now uses a set of default values, to keep it simple. It can be called with self.StartThreadProcess(ExecCmds=[], ShowOutput=True) etc. Only ExecCmds is compulsory.
        #Reset templog
        templog = []

        #Run the cmd.
        if Piping == False:
            #*** Temporary abstraction in preparation to switch to CoreTools().StartProcess() ***
            ExecCmds = ' '.join(ExecCmds)

        logger.debug("CoreBackendTools: Main().StartThreadProcess(): Starting process: "+ExecCmds)
        runcmd = subprocess.Popen(ExecCmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        while runcmd.poll() == None:
            #Send given line to the outputbox and Log it too, if ShowOutput == True or if FullVerbose == True 
            line = runcmd.stdout.readline()
            templog.append(line)
            wx.CallAfter(ParentWindow.UpdateOutputBox, line)

        #Save runcmd.stdout.readlines, and runcmd.returncode, as they tend to reset fairly quickly.
        output = runcmd.stdout.readlines()
        retval = int(runcmd.returncode)

        #Add any missing output (this is what templog is helpful for: it'll contain only output from this command).
        for line in output:
            if line not in templog:
                templog.append(line)
                wx.CallAfter(ParentWindow.UpdateOutputBox, line)

        #Log this info in a debug message.
        try:
            logger.debug("CoreBackendTools: Main().StartThreadProcess(): Process: "+ExecCmds+": Return Value: "+unicode(retval)+", Output: \"\n\n"+''.join(templog)+"\"\n")

        except UnicodeDecodeError:
	        #Skip logging the output, but do note we couldn't log the output.
            logger.debug("CoreBackendTools: Main().StartThreadProcess(): Process: "+ExecCmds+": Return Value: "+unicode(retval)+", Output: \"\n\nCouldn't write data due to unicode decode error\"\n")

        if ReturnOutput == False:
            #Return the return code back to whichever function ran this process, so it can handle any errors.
            return retval

        else:
            #Return the return code, as well as the output.
            return (retval, ''.join(templog))

    def UpdateChrootMtab(self, MountPoint):
        """Update /etc/mtab inside a chroot, so the list of mounted filesystems is always right.""" #*** Don't copy to /etc/mtab, as this may screw up mounting in target os later. Copy to MountPoint/proc/self/mounts. Actually, /proc is bound to /MountPoint/proc. What's not working with this command?! ***
        logger.debug("CoreBackendTools: Main().UpdateChrootMtab: Updating /etc/mtab for chroot at: "+MountPoint+"...")

        retval = self.StartThreadProcess(['cp', '-vf', '/proc/self/mounts', MountPoint+'/etc/mtab'], ShowOutput=False)

        if retval != 0:
            logger.error("CoreBackendTools: Main().UpdateChrootMtab(): Failed to run command: cp -vf /proc/self/mounts "+MountPoint+"/etc/mtab! Chroot may not set up properly! This *probably* doesn't matter, but in rare situations it could cause problems.")

        logger.debug("CoreBackendTools: Main().UpdateChrootMtab: Finished updating /etc/mtab for chroot at: "+MountPoint+".")

    def SetUpChroot(self, MountPoint): #*** Test this again ***
        """Set up a chroot for the given mountpoint."""
        logger.debug("CoreBackendTools: Main().SetUpChroot(): Setting up chroot for MountPoint: "+MountPoint+"...")

        #Mount /dev, /dev/pts, /proc and /sys for the chroot.
        #We might also need internet access in chroot, so to do this first backup MountPoint/etc/resolv.conf to MountPoint/etc/resolv.conf.bak (if it's a link, this will also preserve it),
        #then copy current system's /etc/resolv.conf (the contents, not the link) to MountPoint/etc/resolv.conf, enabling internet access.

        MountList = ("/dev", "/dev/pts", "/proc", "/sys")
        for FileSystem in MountList:
            CoreTools().MountPartition(Partition=FileSystem, MountPoint=MountPoint+FileSystem, Options="--bind") #*** Check it worked ***

        ExecList = ("mv -vf "+MountPoint+"/etc/resolv.conf "+MountPoint+"/etc/resolv.conf.bak", "cp -fv /etc/resolv.conf "+MountPoint+"/etc/resolv.conf")
        for ExecCmd in ExecList:
            Result = self.StartThreadProcess(ExecCmd, Piping=True, ShowOutput=False, ReturnOutput=True)
            output = Result[1]
            retval = Result[0]

            if retval != 0:
                logger.error("CoreBackendTools: Main().SetUpChroot(): Error: Failed to run command: "+', '.join(ExecList)+"! Chroot may not be set up properly!")

        self.UpdateChrootMtab(MountPoint=MountPoint)

        logger.debug("CoreBackendTools: Main().SetUpChroot(): Finished setting up chroot for MountPoint: "+MountPoint+"...")

    def TearDownChroot(self, MountPoint): #*** Test this again ***
        """Remove a chroot at the given mountpoint."""
        logger.debug("CoreBackendTools: Main().TearDownChroot(): Removing chroot at MountPoint: "+MountPoint+"...")

        #Unmount /dev/pts, /dev, /proc and /sys in the chroot. Return values and terminal output will be logged by CoreBackendTools().StartThreadProcess().
        UnmountList = (MountPoint+"/dev/pts", MountPoint+"/dev", MountPoint+"/proc", MountPoint+"/sys")

        for FileSystem in UnmountList:
            CoreTools().Unmount(FileSystem) #*** Check it worked ***

        #We'll also need to replace the MountPoint/etc/resolv.conf with the backup file, MountPoint/etc/resolv.conf.bak.
        Result = self.StartThreadProcess("mv -vf "+MountPoint+"/etc/resolv.conf.bak "+MountPoint+"/etc/resolv.conf", Piping=True, ShowOutput=False, ReturnOutput=True)
        output = Result[1]
        Retval = Result[0]

        if Retval != 0:
            logger.error("CoreBackendTools: Main().TearDownChroot(): Failed to run command: "+', '.join(ExecList)+"! Chroot may not be removed properly!") #*** Log Retval ***

        logger.debug("CoreBackendTools: Main().TearDownChroot(): Finished removing chroot at MountPoint: "+MountPoint+"...")

    def GetPartitionUUID(self, Partition):
        """Retrive the given partition's UUID""" #*** Will be removed/moved to startuptools soon after switching to dictionaries *** *** Give full path? ***
        logger.info("CoreBackendTools: Main().GetPartitionUUID(): Getting UUID for partition: "+Partition+"...")

        Temp = self.StartThreadProcess(['blkid', '-o', 'list'], ShowOutput=False, ReturnOutput=True)
        retval = Temp[0]
        output = Temp[1].split('\n')

        if retval != 0:
            #We couldn't find the UUID! Return "None".
            logger.warning("CoreBackendTools: Main().GetPartitionUUID(): Couldn't find UUID for partition: "+Partition+"! This may cause problems down the line.")
            return "None"

        else:
            #Try to get the UUID from blkid's output.
            UUID="None"

            for line in output:
                if Partition in line:
                    UUID=line.split()[-1]

            if UUID != "None":
                logger.info("CoreBackendTools: Main().GetPartitionUUID(): Found UUID ("+UUID+") for partition: "+Partition+"...")

            else:
                logger.warning("CoreBackendTools: Main().GetPartitionUUID(): Couldn't find UUID for partition: "+Partition+"! This may cause problems down the line.")

            return UUID

    def GetDeviceID(self, Device):
        """Retrive the given partition's/device's ID.""" #*** Will be removed/moved to startuptools soon after switching to dictionaries *** *** Give full path? ***
        logger.info("CoreBackendTools: Main().GetDeviceID(): Getting ID for partition/device: "+Device+"...")

        Temp = CoreBackendTools().StartThreadProcess(['ls', '-l', '/dev/disk/by-id/'], ShowOutput=False, ReturnOutput=True)
        retval = Temp[0]
        output = Temp[1].split('\n')

        if retval != 0:
            #We couldn't find the ID! Return "None".
            logger.warning("CoreBackendTools: Main().GetDeviceID(): Couldn't find ID for partition/device: "+Device+"! This may cause problems down the line.")
            return "None"

        else:
            #Try to get the ID from ls's output.
            ID = "None"

            for line in output:
                try:
                    SplitLine = line.split()
                    if "../../"+Device.split('/')[-1] == SplitLine[-1]:
                        ID = SplitLine[-3]
                except:
                    pass

            if ID != "None":
                logger.info("CoreBackendTools: Main().GetDeviceID(): Found ID ("+ID+") for partition/device: "+Device+"...")

            else:
                logger.warning("CoreBackendTools: Main().GetDeviceID(): Couldn't find ID for partition/device: "+Device+"! This may cause problems down the line.")

            return ID

#End main Class.
