#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Tools in the Tools Package for WxFixBoot Version 2.0~pre1
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
        Line = str("")
        LineList = []

        #Run the command(s).
        logger.debug("CoreTools: Main().StartProcess(): Starting process: "+ExecCmds)
        cmd = subprocess.Popen(ExecCmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        while cmd.poll() == None or Counter < 10000:
            if cmd.poll() != None:
                Counter += 1

            Char = cmd.stdout.read(1)
            Line += str(Char)

            if Char in (str("\n"), str("\r")):
                LineList.append(Line.replace(str("\n"), str("")).replace(str("\r"), str("")))
                #Reset Line.
                Line = str("")

        #Save runcmd.returncode, as it tends to reset fairly quickly.
        Retval = int(cmd.returncode)

        #Log this info in a debug message. #*** Fix this error *** *** Make note of this: when 'cp' errors, the quotes it uses cause this error "UnicodeDecodeError" (use unicode(thing, , errors='ignore')) ***
        try:
            logger.debug("CoreTools: Main().StartProcess(): Process: "+ExecCmds+": Return Value: "+unicode(Retval)+", Output: \"\n\n"+'\n'.join(LineList)+"\"\n")

        except UnicodeDecodeError:
	        #Skip logging the output, but do note we couldn't log the output.
            logger.debug("CoreTools: Main().StartProcess(): Process: "+ExecCmds+": Return Value: "+unicode(Retval)+", Output: \"\n\n*** WxFixBoot: Error: Couldn't log output due to unicode decode error ***\"\n")

        if ReturnOutput == False:
            #Return the return code back to whichever function ran this process, so it can handle any errors.
            return Retval

        else:
            #Return the return code, as well as the output.
            return (Retval, '\n'.join(LineList))

    def IsMounted(self, Partition): #*** Check this works ***
        """Checks if the given partition is mounted.
        Partition is the given partition to check.
        Doesn't check WHERE the partition is mounted,
        just whether it is or not.
        Return boolean True/False.
        """
        logger.debug("CoreTools: Main().IsMounted(): Checking if "+Partition+" is mounted...")

        MountInfo = self.StartProcess("mount -l", ReturnOutput=True)[1]

        if Partition in MountInfo:
            logger.debug("CoreTools: Main().IsMounted(): It is. Returning True...")
            return True

        else:
            logger.debug("CoreTools: Main().IsMounted(): It isn't. Returning False...")
            return False

    def MountPartition(self, Partition, MountPoint, Options=""): #*** Check this works *** #*** Check this over: What if our partition is mounted somewhere else? Make this more bullet-proof ***
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

        MountInfo = self.StartProcess("mount -l", ReturnOutput=True)[1]

        if MountPoint in MountInfo:
            #There is a partition mounted here. Check if our partition is already mounted in the right place.
            MountPointFound = None

            for Line in MountInfo.split("\n"):
                if Partition in Line:
                    MountPointFound = Line.split()[2]

            if MountPointFound != MountPoint:
                #Unmount the partition, and continue.
                logger.warning("CoreTools: Main().MountPartition(): Unmounting filesystem in the way at "+MountPoint+"...")
                Retval = self.Unmount(MountPoint)

                if Retval != 0:
                    logger.error("CoreTools: Main().MountPartition(): Couldn't unmount "+MountPoint+", preventing the mounting of "+Partition+"! Skipping mount attempt.")
                    return False

            else:
                #The correct partition is already mounted here.
                logger.debug("CoreTools: Main().MountPartition(): Partition: "+Partition+" was already mounted at: "+MountPoint+". Continuing...")
                return 0

        #Create the dir if needed.
        if os.path.isdir(MountPoint) == False:
            os.makedirs(MountPoint)
    
        #Mount the device to the mount point.
        Retval = self.StartProcess("mount "+Options+" "+Partition+" "+MountPoint)

        if Retval == 0:
            logger.debug("CoreTools: Main().MountPartition(): Successfully mounted partition!")

        else:
            logger.warning("CoreTools: Main().MountPartition(): Failed to mount partition!")

        return Retval

    def RemountPartition(self, Partition, Mode="rw"):
        """Remounts the given partition.
        Partition is the partition to remount.
        Mode is non-mandatory and is either rw or ro for read-write or read-only respectively.
        The default value for Mode is rw.
        """
        logger.debug("CoreTools: Main().RemountPartition(): Remounting "+Partition+" as "+Mode+"...")
        Retval = self.StartProcess("mount -o remount,"+Mode+" "+Partition, ShowOutput=False)

        if Retval == 0:
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

    def Find(self, RegExp, TopLevelDirectory):
        """Finds the given file, somewhere in or below the given directory, and returns True or False depending on if it was found or not"""
        logger.info("CoreTools: Main().Find(): Looking in "+TopLevelDirectory+" with regular expression "+RegExp+"...")
        FilesFound = []
        for Root, Directory, File in os.walk(TopLevelDirectory):
            if unicode(type(File)) == "<type 'list'>":
                try:
                    File = File[0]

                except IndexError: continue

            if re.match(RegExp, File, re.M|re.I) is not None:
                FilesFound.append(os.path.join(Root, File))

        if FilesFound != []:
            logger.info("CoreTools: Main().Find(): Found files "+' '.join(FilesFound)+"...")

        else:
            logger.info("CoreTools: Main().Find() Didn't find any files...")

        return FilesFound

#End main Class.
