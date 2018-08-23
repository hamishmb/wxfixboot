#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core Tools in the Tools Package for WxFixBoot Version 3.0.0
# This file is part of WxFixBoot.
# Copyright (C) 2013-2018 Hamish McIntyre-Bhatty
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

import subprocess
import sys
import logging
import os
import wx

#Set up logging. FIXME Set logger level as specified on cmdline.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def StartProcess(ExecCmds, StdinLines=[], ShowOutput=True, ReturnOutput=False, Testing=False):
    """Start a process given a string of commands to execute.
    ShowOutput is boolean and specifies whether to show output in the outputbox (if exists) or not.
    ReturnOutput is boolean and specifies whether to return the output back to the caller or not.
    """
    #Make sure output is always in English.
    ExecCmds = "LC_ALL=C "+ExecCmds

    #Run the command(s).
    logger.debug("StartProcess(): Starting process: "+ExecCmds)
    cmd = subprocess.Popen(ExecCmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    #Use a simpler output reader on startup to improve performance.
    if Startup:
        LineList = Read(cmd, Testing=Testing)

    else:
        LineList = ReadAndSendOutput(cmd, ShowOutput)

    #Save runcmd.returncode, as it tends to reset fairly quickly.
    Retval = int(cmd.returncode)

    #Log this info in a debug message.
    logger.debug("StartProcess(): Process: "+ExecCmds+": Return Value: "+unicode(Retval)+", Output: \"\n\n"+'\n'.join(LineList)+"\"\n")

    if ReturnOutput == False:
        #Return the return code back to whichever function ran this process, so it can handle any errors.
        return Retval

    elif Testing:
        #Return the return code, as well as the output.
        return (Retval, ''.join(LineList))

    else:
        #Return the return code, as well as the output.
        return (Retval, '\n'.join(LineList))

def Read(cmd, Testing=False):
    """Read the cmd's output char by char, but do as little processing as possible to improve startup performance"""
    #Get ready to run the command(s). Read up to 100 empty "" characters after the process finishes to make sure we get all the output.
    Counter = 0
    Line = str("")
    LineList = []

    while cmd.poll() == None or Counter < 100:
        Char = cmd.stdout.read(1)

        if Char == "":
            Counter += 1
            continue

        Line += Char

        if Char in ("\n", "\r"):
            #Interpret as Unicode and remove "NULL" characters.
            Line = Line.decode("UTF-8", errors="replace").replace("\x00", "")

            if Testing:
                LineList.append(Line)

            else:
                LineList.append(Line.replace("\n", "").replace("\r", ""))

            #Reset Line.
            Line = str("")

    return LineList
    
def ReadAndSendOutput(cmd, ShowOutput):
    """Read the cmd's output char by char, and send the output to the output box"""
    #Get ready to run the command(s). Read up to 100 empty "" characters after the process finishes to make sure we get all the output.
    Counter = 0
    Line = str("")
    LineList = []
    Hold = False
    SendLine = False

    while cmd.poll() == None or Counter < 100:
        Char = cmd.stdout.read(1)

        if Char == "":
            Counter += 1
            continue

        Line += Char

        if Hold:
            #Check if this char is \n.
            if Char == "\n":
                #Send the line as is but replace \r\n with \n.
                Line = str(Line.replace("\r\n", "\n"))

            else:
                #Send the line as is.
                SendLine = True

            Hold = False

        if Char in ("\n", "\x08") or SendLine:
            #Interpret as Unicode and remove "NULL" characters.
            Line = Line.decode("UTF-8", errors="replace").replace("\x00", "")

            wx.CallAfter(ParentWindow.UpdateOutputBox, Line, ShowOutput)
            LineList.append(Line.replace("\n", "").replace("\r", "").replace("\x08", ""))

            #Reset Line.
            Line = str("")
            SendLine = False

        elif Char == "\r":
            #Take the next character too in case it's \n, so we can just handle \r\n as \n.
            Hold = True

    return LineList

def IsMounted(Partition, MountPoint=None):
    """Checks if the given partition is mounted.
    Partition is the given partition to check.
    If MountPoint is specified, check if the partition is mounted there, rather than just if it's mounted.
    Return boolean True/False.
    """
    if MountPoint == None:
        logger.debug("IsMounted(): Checking if "+Partition+" is mounted...")
        MountInfo = StartProcess("mount -l", ShowOutput=False, ReturnOutput=True)[1]

        Mounted = False

        for Line in MountInfo.split("\n"):
            if Line.split()[0] == Partition:
                Mounted = True

    else:
        #Check where it's mounted to.
        logger.debug("IsMounted(): Checking if "+Partition+" is mounted at "+MountPoint+"...")

        Mounted = False

        if GetMountPointOf(Partition) == MountPoint:
            Mounted = True

    if Mounted:
        logger.debug("IsMounted(): It is. Returning True...")
        return True

    else:
        logger.debug("IsMounted(): It isn't. Returning False...")
        return False

def GetPartitionMountedAt(MountPoint):
    """Returns the partition mounted at the given mountpoint, if any.
    Otherwise, return None"""
    logger.info("GetPartitionMountedAt(): Trying to get partition mounted at "+MountPoint+"...")

    MountInfo = StartProcess("mount -l", ShowOutput=False, ReturnOutput=True)[1]
    Partition = None

    for Line in MountInfo.split("\n"):
        SplitLine = Line.split()

        if MountPoint == SplitLine[2]:
            Partition = SplitLine[0]

    if Partition != None:
        logger.info("GetPartitionMountedAt(): Found it! Partition is "+Partition+"...")

    else:
        logger.info("GetPartitionMountedAt(): Didn't find it...")

    return Partition

def GetMountPointOf(Partition):
    """Returns the mountpoint of the given partition, if any.
    Otherwise, return None"""
    logger.info("GetMountPointOf(): Trying to get mount point of partition "+Partition+"...")

    MountInfo = StartProcess("mount -l", ShowOutput=False, ReturnOutput=True)[1]
    MountPoint = None

    for Line in MountInfo.split("\n"):
        SplitLine = Line.split()

        if Partition == SplitLine[0]:
            MountPoint = SplitLine[2]

    if MountPoint != None:
        logger.info("GetMountPointOf(): Found it! MountPoint is "+MountPoint+"...")

    else:
        logger.info("GetMountPointOf(): Didn't find it...")

    return MountPoint

def MountPartition(Partition, MountPoint, Options=""):
    """Mounts the given partition.
    Partition is the partition to mount.
    MountPoint is where you want to mount the partition.
    Options is non-mandatory and contains whatever options you want to pass to the mount command.
    The default value for Options is an empty string.
    """
    if Options != "":
        logger.info("MountPartition(): Preparing to mount "+Partition+" at "+MountPoint+" with extra options "+Options+"...")

    else:
        logger.info("MountPartition(): Preparing to mount "+Partition+" at "+MountPoint+" with no extra options...")
        
    MountInfo = StartProcess("mount -l", ShowOutput=False, ReturnOutput=True)[1]

    #There is a partition mounted here. Check if our partition is already mounted in the right place.
    if MountPoint == GetMountPointOf(Partition):
        #The correct partition is already mounted here.
        logger.debug("MountPartition(): Partition: "+Partition+" was already mounted at: "+MountPoint+". Continuing...")
        return 0

    elif MountPoint in MountInfo:
        #Something else is in the way. Unmount that partition, and continue.
        logger.warning("MountPartition(): Unmounting filesystem in the way at "+MountPoint+"...")
        Retval = Unmount(MountPoint)

        if Retval != 0:
            logger.error("MountPartition(): Couldn't unmount "+MountPoint+", preventing the mounting of "+Partition+"! Skipping mount attempt.")
            return False

    #Create the dir if needed.
    if os.path.isdir(MountPoint) == False:
        os.makedirs(MountPoint)

    #Mount the device to the mount point.
    Retval = StartProcess("mount "+Options+" "+Partition+" "+MountPoint, ShowOutput=False)

    if Retval == 0:
        logger.debug("MountPartition(): Successfully mounted partition!")

    else:
        logger.warning("MountPartition(): Failed to mount partition!")

    return Retval

def RemountPartition(Partition, Mode="rw"):
    """Remounts the given partition.
    Partition is the partition to remount.
    Mode is non-mandatory and is either rw or ro for read-write or read-only respectively.
    The default value for Mode is rw.
    """
    logger.debug("RemountPartition(): Remounting "+Partition+" as "+Mode+"...")
    Retval = StartProcess("mount -o remount,"+Mode+" "+Partition, ShowOutput=False)

    if Retval == 0:
        logger.warning("RemountPartition(): Successfully remounted partition!")

    else:
        logger.info("RemountPartition(): Failed to remount partition!")

    #Return the return value
    return Retval

def Unmount(MountPoint):
    """Unmounts the given mountpoint.
    MountPoint is the mountpoint to unmount.
    MountPoint can also be a partition name (for example /dev/sda1).
    """
    logger.debug("Unmount(): Preparing to unmount "+MountPoint)

    if MountPoint not in StartProcess("mount -l", ShowOutput=False, ReturnOutput=True)[1]:
        logger.info("Unmount(): "+MountPoint+" was not mounted. Continuing...")
        Retval = 0

    else:
        logger.debug("Unmount(): Unmounting "+MountPoint+"...")
        Retval = StartProcess("umount "+MountPoint, ShowOutput=False)

        if Retval == 0:
            logger.info("Unmount(): Successfully unmounted "+MountPoint+"!")

        else:
            logger.warning("Unmount(): Failed to unmount "+MountPoint+"!")
        
    #Return the return value
    return Retval

def UpdateChrootMtab(MountPoint):
    """Update /etc/mtab inside a chroot, so the list of mounted filesystems is always right."""
    logger.debug("UpdateChrootMtab(): Updating /etc/mtab for chroot at: "+MountPoint+"...")

    retval = StartProcess("cp -vf /proc/self/mounts "+MountPoint+"/etc/mtab", ShowOutput=False)

    if retval != 0:
        logger.warning("UpdateChrootMtab(): Failed to run command: cp -vf /proc/self/mounts "+MountPoint+"/etc/mtab! Chroot may not set up properly! This *probably* doesn't matter, but in rare situations it could cause problems. If the chrooted OS is Fedora-based, this is normal because /etc/mtab is a symlink to /proc/self/mounts.")

    logger.debug("UpdateChrootMtab(): Finished updating /etc/mtab for chroot at: "+MountPoint+".")

def SetUpChroot(MountPoint):
    """Set up a chroot for the given mountpoint."""
    logger.debug("SetUpChroot(): Setting up chroot for MountPoint: "+MountPoint+"...")

    #Mount /dev, /dev/pts, /proc and /sys for the chroot.
    #We might also need internet access in chroot, so to do this first backup MountPoint/etc/resolv.conf to MountPoint/etc/resolv.conf.bak (if it's a link, this will also preserve it),
    #then copy current system's /etc/resolv.conf (the contents, not the link) to MountPoint/etc/resolv.conf, enabling internet access.

    MountList = ("/dev", "/dev/pts", "/proc", "/sys")

    for FileSystem in MountList:
        if MountPartition(Partition=FileSystem, MountPoint=MountPoint+FileSystem, Options="--bind") != 0:
            logger.error("SetUpChroot(): Failed to bind "+FileSystem+" to "+MountPoint+Filesystem+"! Chroot isn't set up properly! Attempting to continue anyway...")

    ExecList = ("mv -vf "+MountPoint+"/etc/resolv.conf "+MountPoint+"/etc/resolv.conf.bak", "cp -fv /etc/resolv.conf "+MountPoint+"/etc/resolv.conf")

    for ExecCmd in ExecList:
        Result = StartProcess(ExecCmd, ShowOutput=False, ReturnOutput=True)
        output = Result[1]
        Retval = Result[0]

        if Retval != 0:
            logger.error("SetUpChroot(): Error: Failed to run command: '"+ExecCmd+"'! Chroot may not be set up properly! On Fedora systems this probably doesn't matter. Continuing anyway...")
            #Ignore these errors, the only happen on Fedora and they don't really matter.
            Retval = 0

    UpdateChrootMtab(MountPoint=MountPoint)

    logger.debug("SetUpChroot(): Finished setting up chroot for MountPoint: "+MountPoint+"...")
    return Retval

def TearDownChroot(MountPoint):
    """Remove a chroot at the given mountpoint."""
    logger.debug("TearDownChroot(): Removing chroot at MountPoint: "+MountPoint+"...")

    #Unmount /dev/pts, /dev, /proc and /sys in the chroot.
    UnmountList = (MountPoint+"/dev/pts", MountPoint+"/dev", MountPoint+"/proc", MountPoint+"/sys")

    for FileSystem in UnmountList:
        if Unmount(FileSystem) != 0:
            logger.error("TearDownChroot(): Faied to unmount "+FileSystem+"! Chroot isn't removed properly! Attempting to continue anyway...")

    #We'll also need to replace the MountPoint/etc/resolv.conf with the backup file, MountPoint/etc/resolv.conf.bak.
    Retval = StartProcess("mv -vf "+MountPoint+"/etc/resolv.conf.bak "+MountPoint+"/etc/resolv.conf", ShowOutput=False)

    if Retval != 0:
        logger.error("TearDownChroot(): Failed to run command: 'mv -vf "+MountPoint+"/etc/resolv.conf.bak "+MountPoint+"/etc/resolv.conf'! Return value was: "+unicode(Retval)+". Chroot may not be removed properly!")

    logger.debug("TearDownChroot(): Finished removing chroot at MountPoint: "+MountPoint+"...")
    return Retval

def EmergencyExit(Message):
    """Handle emergency exits. Warn the user, log, and exit to terminal with the given message"""
    logger.critical("EmergencyExit(): Emergency exit has been triggered! Giving user message dialog and saving the logfile...")
    logger.critical("EmergencyExit(): The error is: "+Message)

    #Warn the user.
    DialogTools.ShowMsgDlg(Message="Emergency exit triggered.\n\n"+Message+"\n\nYou'll now be asked for a location to save the log file.\nIf you email me at hamishmb@live.co.uk with the contents of that file I'll be happy to help you fix this problem.", Kind="error")

    #Shut down the logger.
    logging.shutdown()

    #Save the log file.
    LogFile = DialogTools.ShowSaveFileDlg(Wildcard="Log Files|*.log")
    StartProcess("mv -v /tmp/wxfixboot.log "+LogFile, ShowOutput=False)

    #If we're using wayland, remove the workaround we have to use to make this work.
    #XXX Fix for running on Wayland until we get policy kit stuff done.
    try:
        subprocess.check_call("xhost -si:localuser:root", shell=True)
    except subprocess.CalledProcessError: pass

    #Exit.
    DialogTools.ShowMsgDlg(Message="Done. WxFixBoot will now exit.")
    wx.Exit()
    sys.stdout.write(Message+"\n")
    os._exit(1)
