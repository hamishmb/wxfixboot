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
    def StartProcess(self, ExecCmds, ShowOutput=True, ReturnOutput=False): #*** ShowOutput is ignored currently ***
        """Start a process given a string of commands to execute.
        ShowOutput is boolean and specifies whether to show output in the outputbox (if exists) or not.
        ReturnOutput is boolean and specifies whether to return the output back to the caller or not.
        """
        #Make sure output is always in English.
        ExecCmds = "LC_ALL=C "+ExecCmds

        #Get ready to run the command(s). Read up to 100 empty "" characters after the process finishes to make sure we get all the output.
        Counter = 0
        Line = str("")
        LineList = []

        #Run the command(s). *** Silence UnicodeWarning when failing to convert Char to unicode *** *** Not really a problem cos if char can't be converted it isn't = to \n anyway, but annoying ***
        logger.debug("CoreTools: Main().StartProcess(): Starting process: "+ExecCmds)
        cmd = subprocess.Popen(ExecCmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        while cmd.poll() == None or Counter < 100:
            Char = cmd.stdout.read(1)

            if cmd.poll() != None and Char == "":
                Counter += 1
                break

            Line += Char

            if Char in ("\n", "\r"):
                #Convert to unicode if needed and remove "NULL" characters.
                if unicode(type(Line)) != "<type 'unicode'>":
                    Line = unicode(Line, errors="replace").replace("\x00", "")

                wx.CallAfter(ParentWindow.UpdateOutputBox, Line)
                LineList.append(Line.replace("\n", "").replace("\r", ""))

                #Reset Line.
                Line = str("")

        #Save runcmd.returncode, as it tends to reset fairly quickly.
        Retval = int(cmd.returncode)

        #Log this info in a debug message.
        logger.debug("CoreTools: Main().StartProcess(): Process: "+ExecCmds+": Return Value: "+unicode(Retval)+", Output: \"\n\n"+'\n'.join(LineList)+"\"\n")

        if ReturnOutput == False:
            #Return the return code back to whichever function ran this process, so it can handle any errors.
            return Retval

        else:
            #Return the return code, as well as the output.
            return (Retval, '\n'.join(LineList))

    def IsMounted(self, Partition, MountPoint=None): #*** Reduce duplication maybe ***
        """Checks if the given partition is mounted.
        Partition is the given partition to check.
        If MountPoint is specified, check if the partition is mounted there, rather than just if it's mounted.
        Return boolean True/False.
        """
        MountInfo = self.StartProcess("mount -l", ReturnOutput=True)[1]

        if MountPoint == None:
            logger.debug("CoreTools: Main().IsMounted(): Checking if "+Partition+" is mounted...")

            Mounted = False

            for Line in MountInfo.split("\n"):
                if Line.split()[0] == Partition:
                    Mounted = True

            if Mounted:
                logger.debug("CoreTools: Main().IsMounted(): It is. Returning True...")
                return True

            else:
                logger.debug("CoreTools: Main().IsMounted(): It isn't. Returning False...")
                return False

        else:
            #Check where it's mounted too.
            logger.debug("CoreTools: Main().IsMounted(): Checking if "+Partition+" is mounted at "+MountPoint+"...")

            Mounted = False

            for Line in MountInfo.split("\n"):
                if Line.split()[0] == Partition and Line.split()[2] == MountPoint:
                    Mounted = True

            if Mounted:
                logger.debug("CoreTools: Main().IsMounted(): It is. Returning True...")
                return True

            else:
                logger.debug("CoreTools: Main().IsMounted(): It isn't. Returning False...")
                return False

    def GetPartitionMountedAt(self, MountPoint): #*** Check this works *** *** What if we get a UUID? ***
        """Returns the partition mounted at the given mountpoint, if any.
        Otherwise, return None"""
        logger.info("CoreTools: Main().GetPartitionMountedAt(): Trying to get partition mounted at "+MountPoint+"...")

        MountInfo = self.StartProcess("mount -l", ReturnOutput=True)[1]
        Partition = None

        for Line in MountInfo.split("\n"):
            SplitLine = Line.split()

            if MountPoint == SplitLine[2]:
                Partition = SplitLine[0]

        if Partition != None:
            logger.info("CoreTools: Main().GetPartitionMountedAt(): Found it! Partition is "+Partition+"...")

        else:
            logger.info("CoreTools: Main().GetPartitionMountedAt(): Didn't find it...")

        return Partition

    def GetMountPointOf(self, Partition): #*** Check this works ***
        """Returns the mountpoint of the given partition, if any.
        Otherwise, return None"""
        logger.info("CoreTools: Main().GetMountPointOf(): Trying to mount point of partition "+Partition+"...")

        MountInfo = self.StartProcess("mount -l", ReturnOutput=True)[1]
        MountPoint = None

        for Line in MountInfo.split("\n"):
            SplitLine = Line.split()

            if Partition == SplitLine[0]:
                MountPoint = SplitLine[2]

        if MountPoint != None:
            logger.info("CoreTools: Main().GetMountPointOf(): Found it! MountPoint is "+MountPoint+"...")

        else:
            logger.info("CoreTools: Main().GetMountPointOf(): Didn't find it...")

        return MountPoint

    def MountPartition(self, Partition, MountPoint, Options=""): #*** Check this works *** *** Check this over: What if our partition is mounted somewhere else? Does that matter? Make this more bullet-proof ***
        """Mounts the given partition.
        Partition is the partition to mount.
        MountPoint is where you want to mount the partition.
        Options is non-mandatory and contains whatever options you want to pass to the mount command.
        The default value for Options is an empty string.
        """
        if Options != "":
            logger.info("CoreTools: Main().MountPartition(): Preparing to mount "+Partition+" at "+MountPoint+" with extra options "+Options+"...")

        else:
            logger.info("CoreTools: Main().MountPartition(): Preparing to mount "+Partition+" at "+MountPoint+" with no extra options...")
            
        MountInfo = self.StartProcess("mount -l", ReturnOutput=True)[1]

        #There is a partition mounted here. Check if our partition is already mounted in the right place.
        if MountPoint == self.GetMountPointOf(Partition):
            #The correct partition is already mounted here.
            logger.debug("CoreTools: Main().MountPartition(): Partition: "+Partition+" was already mounted at: "+MountPoint+". Continuing...")
            return 0

        elif MountPoint in MountInfo:
            #Something else is in the way. Unmount that partition, and continue.
            logger.warning("CoreTools: Main().MountPartition(): Unmounting filesystem in the way at "+MountPoint+"...")
            Retval = self.Unmount(MountPoint)

            if Retval != 0:
                logger.error("CoreTools: Main().MountPartition(): Couldn't unmount "+MountPoint+", preventing the mounting of "+Partition+"! Skipping mount attempt.")
                return False

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

    def EmergencyExit(self, Message):
        """Handle emergency exits. Warn the user, log, and exit to terminal with the given message"""
        logger.critical("CoreTools: Main().EmergencyExit(): Emergency exit has been triggered! Giving user message dialog and saving the logfile...")
        logger.critical("CoreTools: Main().EmergencyExit(): The error is: "+Message)

        #Warn the user.
        DialogTools.ShowMsgDlg(Message="Emergency exit triggered.\n\n"+Message+"\n\nYou'll now be asked for a location to save the log file.\nIf you email me at hamishmb@live.co.uk with the contents of that file I'll be willing to help you fix this problem.", Kind="error")

        #Shut down the logger.
        logging.shutdown()

        #Save the log file.
        LogFile = DialogTools.ShowSaveFileDlg(Wildcard="Log Files|*.log")
        self.StartProcess("mv -v /tmp/wxfixboot.log "+LogFile)

        #Exit.
        DialogTools.ShowMsgDlg(Message="Done. WxFixBoot will now exit.")
        wx.Exit()
        sys.exit(Message)

#End main Class.
