#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Tools in the Tools Package for WxFixBoot Version 1.1~pre1
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
class Main():
    def StartProcess(self, ExecCmds, ShowOutput=True, ReturnOutput=False): #*** Pull in new code from DDRescue-GUI v1.5 *** *** Will also eventually replace MainBackendTools: Main().StartThreadProcess() ***
        """Start a process given a string of commands to execute.
        ShowOutput is boolean and specifies whether to show output in the outputbox (if exists) or not.
        ReturnOutput is boolean and specifies whether to return the output back to the caller or not.
        """
        #*** Add stuff as needed ***
        #Make sure output is always in English.
        ExecCmds = "LC_ALL=C "+ExecCmds

        #Get ready to run the command(s).
        Counter = 0
        Line = ""
        LineList = []

        #Run the command(s).
        logger.debug("CoreTools: Main().StartProcess(): Starting process: "+ExecCmds)
        cmd = subprocess.Popen(ExecCmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        while cmd.poll() == None or Counter < 10000:
            if cmd.poll() != None:
                Counter += 1

            Char = cmd.stdout.read(1)
            Line += Char

            if Char in ("\n", "\r"):
                LineList.append(Line.replace("\n", "").replace("\r", ""))
                #Reset Line.
                Line = ""

        #Save runcmd.returncode, as it tends to reset fairly quickly.
        Retval = int(cmd.returncode)

        #Log this info in a debug message. #*** Fix this error ***
        try:
            logger.debug("CoreTools: Main().StartProcess(): Process: "+ExecCmds+": Return Value: "+unicode(Retval)+", Output: \"\n\n"+'\n'.join(LineList)+"\"\n")

        except UnicodeDecodeError:
	        #Skip logging the output, but do note we couldn't log the output.
            logger.debug("CoreTools: Main().StartProcess(): Process: "+ExecCmds+": Return Value: "+unicode(Retval)+", Output: \"\n\nWxFixBoot: Error: Couldn't log output due to unicode decode error\"\n")

        if ReturnOutput == False:
            #Return the return code back to whichever function ran this process, so it can handle any errors.
            return Retval

        else:
            #Return the return code, as well as the output.
            return (Retval, '\n'.join(LineList))

    def MountPartition(self, Partition, MountPoint, OnlyCheck=False, Options=""): #*** Check this over: What if our partition is mounted somewhere else? *** *** Test using OnlyCheck=True ***
        """Mounts the given partition.
        Partition is the partition to mount.
        MountPoint is where you want to mount the partition.
        Options is non-mandatory and contains whatever option you want to pass to the mount command.
        The default value for Options is an empty string.
        """
        if Options != "":
            logger.info("CoreTools: Main().MountPartition(): Preparing to mount "+Partition+" at "+MountPoint+" with extra options "+Options+"...")

        else:
            logger.info("CoreTools: Main().MountPartition(): Preparing to mount "+Partition+" at "+MountPoint+" with no extra options...")

        if MountPoint in self.StartProcess("mount -l", ReturnOutput=True)[1]:
            #There is a partition mounted here. Check if our partition is already mounted in the right place.
            MountPointFound = None
            Temp = self.StartProcess("mount -l", ReturnOutput=True)[1]

            for Line in Temp.split("\n"):
                if Partition in Line:
                    MountPointFound = Line.split()[2]

            if MountPointFound != MountPoint:
                #Unmount the partition, and continue.
                if OnlyCheck == False:
                    logger.warning("CoreTools: Main().MountPartition(): Unmounting filesystem in the way at "+MountPoint+"...")
                    Retval = self.Unmount(MountPoint)

                    if Retval != 0:
                        logger.error("CoreTools: Main().MountPartition(): Couldn't unmount "+MountPoint+", preventing the mounting of "+Partition+"! Skipping mount attempt.")
                        return False

                else:
                    logger.debug("CoreTools: Main().MountPartition(): Would unmount filesystem in the way at this point, but OnlyCheck == True. Returning False and doing nothing...") #*** Is this the right thing to do here? ***
                    return False

            else:
                #The correct partition is already mounted here.
                logger.debug("CoreTools: Main().MountPartition(): Partition: "+Partition+" was already mounted at: "+MountPoint+". Continuing...")

                if OnlyCheck == False:
                    return 0

                else:
                    return True

        #Create the dir if needed.
        if os.path.isdir(MountPoint) == False:
            os.makedirs(MountPoint)
    
        #Mount the device to the mount point.
        if OnlyCheck == False:
            Retval = self.StartProcess("mount "+Options+" "+Partition+" "+MountPoint)

            if Retval == 0:
                logger.debug("CoreTools: Main().MountPartition(): Successfully mounted partition!")

            else:
                logger.warning("CoreTools: Main().MountPartition(): Failed to mount partition!")

        else:
            logger.debug("CoreTools: Main().MountPartition(): Would attempt to mount filesystem at this point, but OnlyCheck == True. Returning False and doing nothing...")
            return False

        return Retval

    def RemountPartition(self, Partition, Mode="rw"):
        """Remounts the given partition.
        Partition is the partition to remount.
        Mode is non-mandatory and is either rw or ro for read-write or read-only respectively.
        The default value for Mode is rw.
        """
        logger.debug("CoreTools: Main().RemountPartition(): Remounting "+Partition+" as "+Mode+"...")
        Retval = self.StartProcess("mount -o remount,"+Mode+" "+Partition, ShowOutput=False)

        if Retval != 0:
            logger.warning("CoreTools: Main().RemountPartition(): Successfully remounted partition!")

        else:
            logger.info("CoreTools: Main().RemountPartition(): Failed to remount partition!")

        #Return the return value
        return Retval

    def Unmount(self, MountPoint):
        """Unmounts the given mountpoint.
        MountPoint is the mountpoint to unmount.
        MountPoint can also be a partition name (for example /dev/sda1).
        """
        logger.debug("CoreTools: Main().Unmount(): Preparing to unmount "+MountPoint)

        if MountPoint not in self.StartProcess("mount -l", ReturnOutput=True)[1]:
            logger.info("CoreTools: Main().Unmount(): "+MountPoint+" was not mounted. Continuing...")
            Retval = 0

        else:
            logger.debug("CoreTools: Main().Unmount(): Unmounting "+MountPoint+"...")
            Retval = self.StartProcess("umount "+MountPoint, ShowOutput=False)

            if Retval == 0:
                logger.info("CoreTools: Main().Unmount(): Successfully unmounted "+MountPoint+"!")

            else:
                logger.warning("CoreTools: Main().Unmount(): Failed to unmount "+MountPoint+"!")
            
        #Return the return value
        return Retval

#End main Class.
