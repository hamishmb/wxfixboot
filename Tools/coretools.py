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

#Import modules.
import subprocess
import sys
import logging
import os
import wx

#Import other modules.
from . import dialogtools as DialogTools

#Set up logging. FIXME Set logger level as specified on cmdline.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def start_process(ExecCmds, ShowOutput=True, ReturnOutput=False, Testing=False):
    """Start a process given a string of commands to execute.
    ShowOutput is boolean and specifies whether to show output in the outputbox (if exists) or not.
    ReturnOutput is boolean and specifies whether to return the output back to the caller or not.
    """
    #Make sure output is always in English.
    ExecCmds = "LC_ALL=C "+ExecCmds

    #Run the command(s).
    logger.debug("start_process(): Starting process: "+ExecCmds)
    cmd = subprocess.Popen(ExecCmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    #Use a simpler output reader on startup to improve performance.
    if Startup:
        line_list = read(cmd, Testing=Testing)

    else:
        line_list = read_and_send_output(cmd, ShowOutput)

    #Save runcmd.returncode, as it tends to reset fairly quickly.
    ret_val = int(cmd.returncode)

    #Log this info in a debug message.
    logger.debug("start_process(): Process: "+ExecCmds+": Return Value: "+unicode(ret_val)+", Output: \"\n\n"+'\n'.join(line_list)+"\"\n")

    if ReturnOutput is False:
        #Return the return code back to whichever function ran this process, so it can handle any errors.
        return ret_val

    elif Testing:
        #Return the return code, as well as the output.
        return (ret_val, ''.join(line_list))

    else:
        #Return the return code, as well as the output.
        return (ret_val, '\n'.join(line_list))

def read(cmd, Testing=False):
    """Read the cmd's output char by char, but do as little processing as possible to improve startup performance"""
    #Get ready to run the command(s). Read up to 100 empty "" characters after the process finishes to make sure we get all the output.
    counter = 0
    line = str("")
    line_list = []

    while cmd.poll() is None or counter < 100:
        char = cmd.stdout.read(1)

        if char == "":
            counter += 1
            continue

        line += char

        if char in ("\n", "\r"):
            #Interpret as Unicode and remove "NULL" characters.
            line = line.decode("UTF-8", errors="replace").replace("\x00", "")

            if Testing:
                line_list.append(line)

            else:
                line_list.append(line.replace("\n", "").replace("\r", ""))

            #Reset line.
            line = str("")

    return line_list
    
def read_and_send_output(cmd, ShowOutput):
    """Read the cmd's output char by char, and send the output to the output box"""
    #Get ready to run the command(s). Read up to 100 empty "" characters after the process finishes to make sure we get all the output.
    counter = 0
    line = str("")
    line_list = []
    hold = False
    send_line = False

    while cmd.poll() is None or counter < 100:
        char = cmd.stdout.read(1)

        if char == "":
            counter += 1
            continue

        line += char

        if hold:
            #Check if this char is \n.
            if char == "\n":
                #Send the line as is but replace \r\n with \n.
                line = str(line.replace("\r\n", "\n"))

            else:
                #Send the line as is.
                send_line = True

            hold = False

        if char in ("\n", "\x08") or send_line:
            #Interpret as Unicode and remove "NULL" characters.
            line = line.decode("UTF-8", errors="replace").replace("\x00", "")

            wx.CallAfter(ParentWindow.UpdateOutputBox, line, ShowOutput)
            line_list.append(line.replace("\n", "").replace("\r", "").replace("\x08", ""))

            #Reset line.
            line = str("")
            send_line = False

        elif char == "\r":
            #Take the next character too in case it's \n, so we can just handle \r\n as \n.
            hold = True

    return line_list

def is_mounted(Partition, MountPoint=None):
    """Checks if the given partition is mounted.
    Partition is the given partition to check.
    If MountPoint is specified, check if the partition is mounted there, rather than just if it's mounted.
    Return boolean True/False.
    """
    if MountPoint is None:
        logger.debug("is_mounted(): Checking if "+Partition+" is mounted...")
        mount_info = start_process("mount -l", ShowOutput=False, ReturnOutput=True)[1]

        mounted = False

        for line in mount_info.split("\n"):
            if line.split()[0] == Partition:
                mounted = True

    else:
        #Check where it's mounted to.
        logger.debug("is_mounted(): Checking if "+Partition+" is mounted at "+MountPoint+"...")

        mounted = False

        if GetMountPointOf(Partition) == MountPoint:
            mounted = True

    if mounted:
        logger.debug("is_mounted(): It is. Returning True...")
        return True

    else:
        logger.debug("is_mounted(): It isn't. Returning False...")
        return False

def GetPartitionMountedAt(MountPoint):
    """Returns the partition mounted at the given mountpoint, if any.
    Otherwise, return None"""
    logger.info("GetPartitionMountedAt(): Trying to get partition mounted at "+MountPoint+"...")

    mount_info = start_process("mount -l", ShowOutput=False, ReturnOutput=True)[1]
    partition = None

    for line in mount_info.split("\n"):
        split_line = line.split()

        if MountPoint == split_line[2]:
            partition = split_line[0]

    if partition != None:
        logger.info("GetPartitionMountedAt(): Found it! Partition is "+partition+"...")

    else:
        logger.info("GetPartitionMountedAt(): Didn't find it...")

    return partition

def GetMountPointOf(Partition):
    """Returns the mountpoint of the given partition, if any.
    Otherwise, return None"""
    logger.info("GetMountPointOf(): Trying to get mount point of partition "+Partition+"...")

    mount_info = start_process("mount -l", ShowOutput=False, ReturnOutput=True)[1]
    mount_point = None

    for line in mount_info.split("\n"):
        split_line = line.split()

        if Partition == split_line[0]:
            mount_point = split_line[2]

    if mount_point != None:
        logger.info("GetMountPointOf(): Found it! MountPoint is "+mount_point+"...")

    else:
        logger.info("GetMountPointOf(): Didn't find it...")

    return mount_point

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
        
    mount_info = start_process("mount -l", ShowOutput=False, ReturnOutput=True)[1]

    #There is a partition mounted here. Check if our partition is already mounted in the right place.
    if MountPoint == GetMountPointOf(Partition):
        #The correct partition is already mounted here.
        logger.debug("MountPartition(): Partition: "+Partition+" was already mounted at: "+MountPoint+". Continuing...")
        return 0

    elif MountPoint in mount_info:
        #Something else is in the way. Unmount that partition, and continue.
        logger.warning("MountPartition(): Unmounting filesystem in the way at "+MountPoint+"...")
        ret_val = Unmount(MountPoint)

        if ret_val != 0:
            logger.error("MountPartition(): Couldn't unmount "+MountPoint+", preventing the mounting of "+Partition+"! Skipping mount attempt.")
            return False

    #Create the dir if needed.
    if os.path.isdir(MountPoint) is False:
        os.makedirs(MountPoint)

    #Mount the device to the mount point.
    ret_val = start_process("mount "+Options+" "+Partition+" "+MountPoint, ShowOutput=False)

    if ret_val == 0:
        logger.debug("MountPartition(): Successfully mounted partition!")

    else:
        logger.warning("MountPartition(): Failed to mount partition!")

    return ret_val

def RemountPartition(Partition, Mode="rw"):
    """Remounts the given partition.
    Partition is the partition to remount.
    Mode is non-mandatory and is either rw or ro for read-write or read-only respectively.
    The default value for Mode is rw.
    """
    logger.debug("RemountPartition(): Remounting "+Partition+" as "+Mode+"...")
    ret_val = start_process("mount -o remount,"+Mode+" "+Partition, ShowOutput=False)

    if ret_val == 0:
        logger.warning("RemountPartition(): Successfully remounted partition!")

    else:
        logger.info("RemountPartition(): Failed to remount partition!")

    #Return the return value
    return ret_val

def Unmount(MountPoint):
    """Unmounts the given mountpoint.
    MountPoint is the mountpoint to unmount.
    MountPoint can also be a partition name (for example /dev/sda1).
    """
    logger.debug("Unmount(): Preparing to unmount "+MountPoint)

    if MountPoint not in start_process("mount -l", ShowOutput=False, ReturnOutput=True)[1]:
        logger.info("Unmount(): "+MountPoint+" was not mounted. Continuing...")
        ret_val = 0

    else:
        logger.debug("Unmount(): Unmounting "+MountPoint+"...")
        ret_val = start_process("umount "+MountPoint, ShowOutput=False)

        if ret_val == 0:
            logger.info("Unmount(): Successfully unmounted "+MountPoint+"!")

        else:
            logger.warning("Unmount(): Failed to unmount "+MountPoint+"!")
        
    #Return the return value
    return ret_val

def UpdateChrootMtab(MountPoint):
    """Update /etc/mtab inside a chroot, so the list of mounted filesystems is always right."""
    logger.debug("UpdateChrootMtab(): Updating /etc/mtab for chroot at: "+MountPoint+"...")

    retval = start_process("cp -vf /proc/self/mounts "+MountPoint+"/etc/mtab", ShowOutput=False)

    if retval != 0:
        logger.warning("UpdateChrootMtab(): Failed to run command: cp -vf /proc/self/mounts "+MountPoint+"/etc/mtab! Chroot may not set up properly! This *probably* doesn't matter, but in rare situations it could cause problems. If the chrooted OS is Fedora-based, this is normal because /etc/mtab is a symlink to /proc/self/mounts.")

    logger.debug("UpdateChrootMtab(): Finished updating /etc/mtab for chroot at: "+MountPoint+".")

def SetUpChroot(MountPoint):
    """Set up a chroot for the given mountpoint."""
    logger.debug("SetUpChroot(): Setting up chroot for MountPoint: "+MountPoint+"...")

    #Mount /dev, /dev/pts, /proc and /sys for the chroot.
    #We might also need internet access in chroot, so to do this first backup MountPoint/etc/resolv.conf to MountPoint/etc/resolv.conf.bak (if it's a link, this will also preserve it),
    #then copy current system's /etc/resolv.conf (the contents, not the link) to MountPoint/etc/resolv.conf, enabling internet access.

    mount_list = ("/dev", "/dev/pts", "/proc", "/sys")

    for file_system in mount_list:
        if MountPartition(Partition=file_system, MountPoint=MountPoint+file_system, Options="--bind") != 0:
            logger.error("SetUpChroot(): Failed to bind "+file_system+" to "+MountPoint+Filesystem+"! Chroot isn't set up properly! Attempting to continue anyway...")

    exec_list = ("mv -vf "+MountPoint+"/etc/resolv.conf "+MountPoint+"/etc/resolv.conf.bak", "cp -fv /etc/resolv.conf "+MountPoint+"/etc/resolv.conf")

    for exec_cmd in exec_list:
        ret_val = start_process(exec_cmd, ShowOutput=False, ReturnOutput=True)[0]

        if ret_val != 0:
            logger.error("SetUpChroot(): Error: Failed to run command: '"+exec_cmd+"'! Chroot may not be set up properly! On Fedora systems this probably doesn't matter. Continuing anyway...")
            #Ignore these errors, the only happen on Fedora and they don't really matter.
            ret_val = 0

    UpdateChrootMtab(MountPoint=MountPoint)

    logger.debug("SetUpChroot(): Finished setting up chroot for MountPoint: "+MountPoint+"...")
    return ret_val

def TearDownChroot(MountPoint):
    """Remove a chroot at the given mountpoint."""
    logger.debug("TearDownChroot(): Removing chroot at MountPoint: "+MountPoint+"...")

    #Unmount /dev/pts, /dev, /proc and /sys in the chroot.
    unmount_list = (MountPoint+"/dev/pts", MountPoint+"/dev", MountPoint+"/proc", MountPoint+"/sys")

    for file_system in unmount_list:
        if Unmount(file_system) != 0:
            logger.error("TearDownChroot(): Faied to unmount "+file_system+"! Chroot isn't removed properly! Attempting to continue anyway...")

    #We'll also need to replace the MountPoint/etc/resolv.conf with the backup file, MountPoint/etc/resolv.conf.bak.
    ret_val = start_process("mv -vf "+MountPoint+"/etc/resolv.conf.bak "+MountPoint+"/etc/resolv.conf", ShowOutput=False)

    if ret_val != 0:
        logger.error("TearDownChroot(): Failed to run command: 'mv -vf "+MountPoint+"/etc/resolv.conf.bak "+MountPoint+"/etc/resolv.conf'! Return value was: "+unicode(ret_val)+". Chroot may not be removed properly!")

    logger.debug("TearDownChroot(): Finished removing chroot at MountPoint: "+MountPoint+"...")
    return ret_val

def EmergencyExit(Message):
    """Handle emergency exits. Warn the user, log, and exit to terminal with the given message"""
    logger.critical("EmergencyExit(): Emergency exit has been triggered! Giving user message dialog and saving the logfile...")
    logger.critical("EmergencyExit(): The error is: "+Message)

    #Warn the user.
    DialogTools.ShowMsgDlg(Message="Emergency exit triggered.\n\n"+Message+"\n\nYou'll now be asked for a location to save the log file.\nIf you email me at hamishmb@live.co.uk with the contents of that file I'll be happy to help you fix this problem.", Kind="error")

    #Shut down the logger.
    logging.shutdown()

    #Save the log file.
    log_file = DialogTools.ShowSaveFileDlg(Wildcard="Log Files|*.log")
    start_process("mv -v /tmp/wxfixboot.log "+log_file, ShowOutput=False)

    #If we're using wayland, remove the workaround we have to use to make this work.
    #XXX Fix for running on Wayland until we get policy kit stuff done.
    try:
        subprocess.check_call("xhost -si:localuser:root", shell=True)
    except subprocess.CalledProcessError: pass

    #Exit.
    DialogTools.ShowMsgDlg(Message="Done. WxFixBoot will now exit.")
    wx.Exit()
    sys.stdout.write(Message+"\n")
    os.exit(1) #TODO Was os._exit(1). Why? Does this work?
