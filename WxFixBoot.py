#!/usr/bin/env python
# -*- coding: utf-8 -*-
# WxFixBoot Version 2.0~pre1
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

#*** Add package dependancy on lvm2 ***
#*** Add package dependency on binutils (for strings command) ***
#*** Remove package dependancy on lsb_release ***
#*** Don't allow modification of 64-bit OSs from 32-bit ones (it won't work) ***
#*** Mount filesystems inside a temporary directory instead of in /mnt, perhaps /tmp/wxfixbootmountpoints/, to keep them out of the way of interference ***
#*** Test DialogTools.ShowMultiChoiceDlg() ***
#*** Figure out what to do in each instance where something might fail ***
#*** Remove grub's .efi files after installing elilo and vice versa ***
#*** Support EFI on 32-bit firmware? ***
#*** /boot/efi not unmounted after modifying EFI bootloaders on parted magic (possibly also on other platforms), preventing unmounting of chrooted rootfs. Doesn't cause an error or any problems. ***
#*** Make OSInfo accessible to CoreBackendTools? ***
#*** Save bootloader config, instead of bootloader itself? That way WxFixBoot can handle reinstalling/fixing the bootloader as required ***

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import other modules
import wx
import wx.lib.statbmp
import wx.lib.stattext
import threading
import subprocess
import sys
import getopt
import logging
import os
import shutil
import time
import re
from distutils.version import LooseVersion
from wx.animate import AnimationCtrl
from wx.animate import Animation
from bs4 import BeautifulSoup

#Define the version number and the release date as global variables.
Version = "2.0~pre2"
ReleaseDate = "9/6/2016"

def usage():
    print("\nUsage: WxFixBoot.py [OPTION]\n")
    print("       -h, --help:                   Show this help message")
    print("       -q, --quiet:                  Show only warning, error and critical messages in the log file. Very unhelpful for debugging, and not recommended.")
    print("       -v, --verbose:                Enable logging of info messages, as well as warnings, errors and critical errors.")
    print("                                     Not the best for debugging, but acceptable if there is little disk space.")
    print("       -d, --debug:                  Log lots of boring debug messages, as well as information, warnings, errors and critical errors. Usually used for diagnostic purposes.")
    print("                                     The default, as it's very helpful if problems are encountered, and the user needs help\n")
    print("WxFixBoot "+Version+" is released under the GNU GPL Version 3")
    print("Copyright (C) Hamish McIntyre-Bhatty 2013-2016")

#If this isn't running as root, relaunch.
if not os.geteuid() == 0:
    subprocess.Popen(["/usr/share/wxfixboot/AuthenticationDialog.py"])
    sys.exit("\nSorry, WxFixBoot must be run with root privileges.\nRestarting as Root...")

#Set up according to cmdline options.
try:
    opts, args = getopt.getopt(sys.argv[1:], "hqvd", ("help", "quiet", "verbose", "debug"))

except getopt.GetoptError as err:
    #Invalid option. Show the help message and then exit.
    #Show the error.
    print(unicode(err))
    usage()
    sys.exit(2)

#Set up logging.
logger = logging.getLogger('WxFixBoot '+Version)
logging.basicConfig(filename='/tmp/wxfixboot.log', format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logger.setLevel(logging.DEBUG)

#Determine the option(s) given, and change the level of logging based on cmdline options.
for o, a in opts:
    if o in ("-q", "--quiet"):
        logger.setLevel(logging.WARNING)

    elif o in ("-v", "--verbose"):
        logger.setLevel(logging.INFO)

    elif o in ("-d", "--debug"):
        logger.setLevel(logging.DEBUG)

    elif o in ("-h", "--help"):
        usage()
        sys.exit()

    else:
        assert False, "unhandled option"

#Import custom-made modules
import GetDevInfo
import Tools

from GetDevInfo.getdevinfo import Main as DevInfoToolsCallable

from Tools.coretools import Main as CoreToolsCallable

from Tools.dialogtools import Main as DialogToolsCallable

from Tools.StartupTools.core import Main as CoreStartupToolsCallable
from Tools.StartupTools.main import Main as MainStartupToolsCallable
from Tools.StartupTools.getbootloaderconfigtools import Main as BootloaderConfigObtainingToolsCallable
from Tools.BackendTools.helpers import Main as HelperBackendToolsCallable
from Tools.BackendTools.essentials import Main as EssentialBackendToolsCallable
from Tools.BackendTools.main import Main as MainBackendToolsCallable

from Tools.BackendTools.BootloaderTools.main import Main as MainBootloaderToolsCallable
from Tools.BackendTools.BootloaderTools.removaltools import Main as BootloaderRemovalToolsCallable
from Tools.BackendTools.BootloaderTools.installationtools import Main as BootloaderInstallationToolsCallable
from Tools.BackendTools.BootloaderTools.setconfigtools import Main as BootloaderConfigSettingToolsCallable

import SystemInfoNoteBookSharedFunctions as NoteBookSharedFunctions

#Access these modules without the "()" so conditional tests can work.
DevInfoTools = DevInfoToolsCallable()

CoreTools = CoreToolsCallable()

DialogTools = DialogToolsCallable()

CoreStartupTools = CoreStartupToolsCallable()
MainStartupTools = MainStartupToolsCallable()

HelperBackendTools = HelperBackendToolsCallable()
EssentialBackendTools = EssentialBackendToolsCallable()
MainBackendTools = MainBackendToolsCallable()

MainBootloaderTools = MainBootloaderToolsCallable()
BootloaderConfigObtainingTools = BootloaderConfigObtainingToolsCallable()
BootloaderRemovalTools = BootloaderRemovalToolsCallable()
BootloaderInstallationTools = BootloaderInstallationToolsCallable()
BootloaderConfigSettingTools = BootloaderConfigSettingToolsCallable()

#Setup custom-made modules (make global variables accessible inside the packages). *** Continue to change stuff as needed ***
#GetDevInfo Package.
GetDevInfo.getdevinfo.subprocess = subprocess
GetDevInfo.getdevinfo.logger = logger
GetDevInfo.getdevinfo.re = re
GetDevInfo.getdevinfo.BeautifulSoup = BeautifulSoup

#CoreTools Module.
Tools.coretools.wx = wx
Tools.coretools.subprocess = subprocess
Tools.coretools.sys = sys
Tools.coretools.logger = logger
Tools.coretools.logging = logging
Tools.coretools.os = os
Tools.coretools.re = re
Tools.coretools.DialogTools = DialogTools

#DialogTools Module.
Tools.dialogtools.wx = wx
Tools.dialogtools.logger = logger
Tools.dialogtools.time = time

#StartupTools Package (Core).
Tools.StartupTools.core.logger = logger
Tools.StartupTools.core.CoreTools = CoreTools
Tools.StartupTools.core.DialogTools = DialogTools

#StartupTools Package (Main).
Tools.StartupTools.main.logger = logger
Tools.StartupTools.main.os = os
Tools.StartupTools.main.CoreTools = CoreTools
Tools.StartupTools.main.CoreStartupTools = CoreStartupTools
Tools.StartupTools.main.BootloaderConfigObtainingTools = BootloaderConfigObtainingTools
Tools.StartupTools.main.DialogTools = DialogTools

#StartupTools Package (BootloaderConfigObtainingTools).
Tools.StartupTools.getbootloaderconfigtools.CoreTools = CoreTools

#BackendTools Package (Helpers)
Tools.BackendTools.helpers.logger = logger
Tools.BackendTools.helpers.os = os
Tools.BackendTools.helpers.CoreTools = CoreTools
Tools.BackendTools.helpers.DialogTools = DialogTools
Tools.BackendTools.helpers.LooseVersion = LooseVersion

#BackendTools Package (Essentials)
Tools.BackendTools.essentials.wx = wx
Tools.BackendTools.essentials.logger = logger
Tools.BackendTools.essentials.CoreTools = CoreTools
Tools.BackendTools.essentials.HelperBackendTools = HelperBackendTools
Tools.BackendTools.essentials.DialogTools = DialogTools

#BackendTools Package (Main).
Tools.BackendTools.main.wx = wx
Tools.BackendTools.main.logger = logger
Tools.BackendTools.main.os = os
Tools.BackendTools.main.CoreTools = CoreTools
Tools.BackendTools.main.HelperBackendTools = HelperBackendTools
Tools.BackendTools.main.BootloaderConfigObtainingTools = BootloaderConfigObtainingTools
Tools.BackendTools.main.BootloaderRemovalTools = BootloaderRemovalTools
Tools.BackendTools.main.BootloaderInstallationTools = BootloaderInstallationTools
Tools.BackendTools.main.BootloaderConfigSettingTools = BootloaderConfigSettingTools
Tools.BackendTools.main.DialogTools = DialogTools

#BootloaderTools Package (Main)
Tools.BackendTools.BootloaderTools.main.wx = wx
Tools.BackendTools.BootloaderTools.main.logger = logger
Tools.BackendTools.BootloaderTools.main.CoreTools = CoreTools
Tools.BackendTools.BootloaderTools.main.HelperBackendTools = HelperBackendTools
Tools.BackendTools.BootloaderTools.main.EssentialBackendTools = EssentialBackendTools
Tools.BackendTools.BootloaderTools.main.MainBackendTools = MainBackendTools
Tools.BackendTools.BootloaderTools.main.DialogTools = DialogTools

#BootloaderTools Package (GetConfigTools)
Tools.StartupTools.getbootloaderconfigtools.logger = logger

#BootloaderTools Package (RemovalTools)
Tools.BackendTools.BootloaderTools.removaltools.CoreTools = CoreTools

#BootloaderTools Package (InstallationTools)
Tools.BackendTools.BootloaderTools.installationtools.CoreTools = CoreTools

#BootloaderTools Package (SetConfigTools)
Tools.BackendTools.BootloaderTools.setconfigtools.logger = logger
Tools.BackendTools.BootloaderTools.setconfigtools.os = os
Tools.BackendTools.BootloaderTools.setconfigtools.CoreTools = CoreTools
Tools.BackendTools.BootloaderTools.setconfigtools.HelperBackendTools = HelperBackendTools
Tools.BackendTools.BootloaderTools.setconfigtools.DialogTools = DialogTools

#NoteBookSharedFunctions module.
NoteBookSharedFunctions.wx = wx
NoteBookSharedFunctions.logger = logger

#Begin Disk Information Handler thread.
class GetDiskInformation(threading.Thread):
    def __init__(self, ParentWindow):
        """Initialize and start the thread."""
        self.ParentWindow = ParentWindow
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        """Get Disk Information and return it as a list with embedded lists"""
        #Use a module I've written to collect data about connected Disks, and return it.
        wx.CallAfter(self.ParentWindow.ReceiveDiskInfo, DevInfoTools.GetInfo())

#End Disk Information Handler thread.
#Begin Starter Class
class WxFixBoot(wx.App):
    def OnInit(self):
        """Starts InitialWindow()"""
        InitialWindow().Show()
        return True

#End Starter Class
#Begin Initialization Panel.
class InitialPanel(wx.Panel):
    def __init__(self, parent):
        """Initialises the panel"""
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.frame = parent
        self.Bind(wx.EVT_PAINT, self.OnEraseBackground)

    def OnEraseBackground(self, Event):
        """Redraw the background image when needed"""
        DC = wx.ClientDC(self)
        Rectangle = self.GetUpdateRegion().GetBox()
        DC.SetClippingRect(Rectangle)

        DC.Clear()
        Splash = wx.Bitmap("/usr/share/wxfixboot/images/splash.jpg")
        DC.DrawBitmap(Splash, 0, 0)

#End Initialization Panel.
#Begin Initialization Frame.
class InitialWindow(wx.Frame):
    def __init__(self):
        """Initialises InitialWindow"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot", size=(600,420), style=wx.SIMPLE_BORDER)
        self.Panel = InitialPanel(self)
        self.SetClientSize(wx.Size(600,420))
        Tools.coretools.ParentWindow = self

        print("WxFixBoot Version "+Version+" Starting...")
        logger.info("WxFixBoot Version "+Version+" Starting...")

        #Set the frame's icon.
        global AppIcon
        AppIcon = wx.Icon("/usr/share/wxfixboot/images/Logo.png", wx.BITMAP_TYPE_PNG)
        wx.Frame.SetIcon(self, AppIcon)

        #Create the progress bar and text.
        self.CreateProgressBarAndText()

        #Setup sizers.
        self.SetupSizers()

        #Start the Initalization Thread, which performs all necessary startup scripts and checks, and let it know this is the first start.
        logger.debug("Starting InitThread()...")
        InitThread(self)       

    def CreateProgressBarAndText(self):
        """Create a progressbar and some progress text"""
        self.ProgressBar = wx.Gauge(self.Panel, -1, 100)
        self.ProgressBar.SetBezelFace(3)
        self.ProgressBar.SetShadowWidth(3)
        self.ProgressBar.SetValue(0)
        self.ProgressBar.Show()

        #Create the progress text.
        self.ProgressText = wx.StaticText(self.Panel, -1, "Initialising...")

    def SetupSizers(self):
        """Setup sizers for InitialWindow"""
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        MainSizer.Add((50,50), 10, wx.EXPAND)
        MainSizer.Add(self.ProgressText, 1, wx.CENTER|wx.BOTTOM|wx.LEFT|wx.RIGHT, 10)
        MainSizer.Add(self.ProgressBar, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.Panel.SetSizer(MainSizer)
        MainSizer.SetMinSize(wx.Size(600,420))
        MainSizer.SetSizeHints(self)

    def UpdateProgressBar(self, Value):
        """Update the progress bar with the given value"""
        self.ProgressBar.SetValue(int(Value))

        if self.ProgressBar.GetValue() == 100:
            self.FinishedInit()

    def UpdateProgressText(self, Message):
        """Update the progress text with the given string"""
        self.ProgressText.SetLabel(Message)
        self.Panel.Layout()

    def UpdateOutputBox(self, Message): #*** Get rid of this later? ***
        """Dummy function, accepts a message argument but ignores it. Allows CoreTools.StartProcess to work."""
        pass

    def FinishedInit(self, Event=None):
        """Starts MainWindow, called when StartupScripts are finished"""
        logger.info("Closing Initial Window and Starting Main Window...")

        #Show the user some important information
        dlg = wx.MessageDialog(self.Panel, "Make sure you have a working internet connection before performing any operations. Thank you.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
        dlg.ShowModal()
        dlg.Destroy()

        MainGUI = MainWindow()
        app.SetTopWindow(MainGUI)
        self.Destroy()

        #Start MainFrame.
        MainGUI.Show(True)    

#End Initalization Frame.
#Begin Initaization Thread.
class InitThread(threading.Thread):
    def __init__(self, ParentWindow):
        """Make a temporary directory for mountpoints used by this program *** TODO ***. If it already exists, delete it and recreate it."""

        #Set up dialog tools.
        Tools.dialogtools.ParentWindow = ParentWindow

        #Initialize the thread.
        threading.Thread.__init__(self)
        self.ParentWindow = ParentWindow
        self.start()

    def run(self):
        """Set some default settings and wait for the GUI to initialize."""
        logger.debug("InitThread(): Starting...")

        #Define dictionaries.
        global SystemInfo
        global DiskInfo
        global OSInfo
        global BootloaderInfo
        global Settings

        SystemInfo = {}
        DiskInfo = {}
        OSInfo = {}
        BootloaderInfo = {}
        Settings = {}

        #*** Put this somewhere else ***
        Settings["MainSettings"] = {}
        Settings["BootloaderSettings"] = {}

        #Make dictionaries available to modules.
        Tools.StartupTools.core.DiskInfo = DiskInfo
        Tools.StartupTools.core.SystemInfo = SystemInfo
        Tools.StartupTools.core.Settings = Settings
        Tools.StartupTools.main.DiskInfo = DiskInfo #*** Temporary cos of MainStartupTools.SortSomeInfo() ***
        Tools.StartupTools.main.BootloaderInfo = BootloaderInfo
        Tools.StartupTools.main.SystemInfo = SystemInfo
        Tools.StartupTools.main.Settings = Settings
        Tools.StartupTools.getbootloaderconfigtools.DiskInfo = DiskInfo
        GetDevInfo.getdevinfo.DiskInfo = DiskInfo

        #Check for dependencies
        logger.info("InitThread(): Checking For Dependencies...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Checking For Dependencies...")
        MainStartupTools.CheckDepends()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "2")
        logger.info("InitThread(): Done Checking For Dependencies!")

        #Check if we're on a Live Disk.
        logger.info("InitThread(): Checking For Live Disk...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Checking For Live Disk...")
        MainStartupTools.CheckForLiveDisk()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "4")
        logger.info("InitThread(): Done Checking For Live Disk!")

        #Unmount all filesystems, to avoid any data corruption.
        logger.info("InitThread(): Unmounting Filesystems...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Unmounting Filesystems...")
        MainStartupTools.UnmountAllFS()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "5")
        logger.info("InitThread(): Done Unmounting Filsystems!")

        #Check filesystems.
        logger.info("InitThread(): Checking Filesystems...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Checking Filesystems...")
        MainStartupTools.CheckFS()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "15")
        logger.info("InitThread(): Filesystems Checked!")

        #Get device info.
        logger.info("InitThread(): Getting Device Information...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Getting Device Information...")
        DevInfoTools.GetInfo()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "60")
        logger.info("InitThread(): Finished Getting Device Information...")

        #Sort some info. *** Move it again later ***
        MainStartupTools.SortSomeInfo()

        #Mount all filesystems.
        logger.info("InitThread(): Mounting Core Filesystems...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Mounting Core Filesystems...")
        MainStartupTools.MountCoreFS()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "63")
        logger.info("InitThread(): Done Mounting Core Filsystems!")

        #Check if there are any linux partitions in the list.
        if SystemInfo["LinuxPartitions"] == []:
            #There are none, exit.
            logger.critical("InitThread(): No Linux Partitions (on HDD) of type ext(1,2,3,4), btrfs, xfs, jfs, zfs, minix or resierfs found! If you do have Linux partitions but WxFixBoot hasn't found them, please file a bug or ask a question on WxFixBoot's launchpad page. If you're using Windows or Mac OS X, then sorry as WxFixBoot has no support for these operating systems. You could instead use the tools provided by Microsoft and Apple to fix any issues with your computer. Exiting...")

            #Exit.
            CoreTools.EmergencyExit("You don't appear to have any Linux partitions on your hard disks. If you do have Linux partitions but WxFixBoot hasn't found them, please file a bug or ask a question on WxFixBoot's launchpad page. If you're using Windows or Mac OS X, then sorry as WxFixBoot has no support for these operating systems. You could instead use the tools provided by Microsoft and Apple to fix any issues with your computer.")

        #Get a list of Linux OSs.
        logger.info("InitThread(): Finding Linux OSs...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Finding Linux Operating Systems...")
        OSInfo, SystemInfo = MainStartupTools.GetLinuxOSs()

        Tools.StartupTools.main.OSInfo = OSInfo

        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "65")
        logger.info("InitThread(): Done...")

        logger.info("InitThread(): *** ABSTRACTION CODE *** Setting default OS...")
        MainStartupTools.SetDefaultOS() #*** Get rid of this; soon to be selected on a per-bootloader basis in Bootloader Options Window ***
        logger.info("InitThread(): *** ABSTRACTION CODE *** Done...")

        #Set rootfs. *** Find mountpoint of / if not on livedisk *** *** Can't do this yet cos other code doesn't expect that ***
        logger.info("InitThread(): *** ABSTRACTION CODE *** Setting SystemInfo['RootFS']...")

        SystemInfo["RootFS"] = OSInfo[SystemInfo["DefaultOS"]]["Partition"]

        logger.info("InitThread(): *** ABSTRACTION CODE *** Done...")

        #Get the firmware type.
        logger.info("InitThread(): Determining Firmware Type...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Determining Firmware Type...")
        MainStartupTools.GetFirmwareType()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "70")
        logger.info("InitThread(): Determined Firmware Type as: "+Settings["MainSettings"]["FirmwareType"])

        #*** Temporary abstraction code ***
        logger.info("InitThread(): *** ABSTRACTION CODE *** Setting RootDev...")

        SystemInfo["RootDevice"] = DiskInfo[SystemInfo["RootFS"]]["HostDevice"]
        SystemInfo["AutoRootDevice"] = SystemInfo["RootDevice"]

        #*** Get rid of this. Just used to sort of keep legacy code working for now ***
        SystemInfo["Bootloader"] = "GRUB-UEFI"
        SystemInfo["AutoBootloader"] = "GRUB-UEFI"

        #New bootloader info getting function.
        logger.info("InitThread(): Finding all Bootloaders and getting their settings...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Finding Bootloaders...")
        MainStartupTools.GetBootloaders()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "80")
        logger.info("InitThread(): Done!")

        #Perform final check.
        logger.info("InitThread(): Doing Final Check for error situations...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Checking Everything...")
        MainStartupTools.FinalCheck()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "100")
        logger.info("InitThread(): Done Final Check!")

        #**************************
        print("\n\nSystemInfo:")
        Keys = SystemInfo.keys()
        Keys.sort()

        for Key in Keys:
            print(Key)

        print("\n\nOSInfo:")
        Keys = OSInfo.keys()
        Keys.sort()

        for Key in Keys:
            print(Key)

        print("\n\nDiskInfo:")
        Keys = DiskInfo.keys()
        Keys.sort()

        for Key in Keys:
            print(Key)

        print("\n\nBootloaderInfo:")
        Keys = BootloaderInfo.keys()
        Keys.sort()

        for Key in Keys:
            print(Key)

        #***************************
        #Set some other variables to default values, avoiding problems down the line. *** Save these in a dictionary later ***
        #Define globals.
        global ReinstallBootloader
        global UpdateBootloader
        global QuickFSCheck
        global BadSectCheck
        global SaveOutput
        global FullVerbose
        global Verify
        global BackupBootSector
        global MakeSystemSummary
        global BootloaderTimeout
        global BLOptsDlgRun
        global RestoreBootSector
        global BootSectorFile
        global BootSectorTargetDevice
        global BootSectorBackupType
        global OptionsDlg1Run

        #Initialise them.
        ReinstallBootloader = ""
        UpdateBootloader = ""
        QuickFSCheck = ""
        BadSectCheck = ""
        SaveOutput = ""
        FullVerbose = ""
        Verify = ""
        BackupBootSector = ""
        MakeSystemSummary = ""
        BootloaderTimeout = ""
        BLOptsDlgRun = ""
        RestoreBootSector = ""
        BootSectorFile = ""
        BootSectorTargetDevice = ""
        BootSectorBackupType = ""
        OptionsDlg1Run = ""

        logger.info("InitThread(): Setting some defaults for other variables set in GUI by user...")
        ReinstallBootloader, UpdateBootloader, QuickFSCheck, BadSectCheck, SaveOutput, FullVerbose, Verify, BackupBootSector, MakeSystemSummary, BootloaderTimeout, BLOptsDlgRun, RestoreBootSector, BootSectorFile, BootSectorTargetDevice, BootSectorBackupType, OptionsDlg1Run = MainStartupTools.SetDefaults()

        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Finished! Starting GUI...")
        logger.info("InitThread(): Finished Determining Settings. Exiting InitThread()...")

#End Initalization Thread.
#Begin Main Window
class MainWindow(wx.Frame):
    def __init__(self):
        """Initialise MainWindow"""
        wx.Frame.__init__(self,None,title="WxFixBoot", size=(400,300),style=wx.DEFAULT_FRAME_STYLE)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(400,300))

        #Set the frame's icon.
        wx.Frame.SetIcon(self, AppIcon)

        #Create a Statusbar in the bottom of the window and set the text.
        self.MakeStatusBar()

        #Add text.
        self.CreateText()

        #Create some buttons
        self.CreateButtons()

        #Create some checkboxes
        self.CreateCBs()

        #Create the menus.
        self.CreateMenus()

        #Set up checkboxes
        self.OnCheckBox()

        #Setup Sizers.
        self.SetupSizers()

        #Bind all events.
        self.BindEvents()

        logger.debug("MainWindow().__init__(): Started. Waiting for events...")

    def MakeStatusBar(self):
        """Create the status bar"""
        self.statusbar = self.CreateStatusBar()
        self.StatusBar.SetFieldsCount(2)
        self.StatusBar.SetStatusWidths([-1, 150])
        self.StatusBar.SetStatusText("Ready.", 0)
        self.StatusBar.SetStatusText("v"+Version+" ("+ReleaseDate+")", 1)

    def CreateText(self):
        """Create the text"""
        self.SettingsText = wx.StaticText(self.Panel, -1, "Please set the basic settings here first.")
        self.WelcomeText = wx.StaticText(self.Panel, -1, "Welcome to WxFixBoot!")

        #Add an image.
        img = wx.Image("/usr/share/pixmaps/wxfixboot.png", wx.BITMAP_TYPE_PNG)
        self.Logo = wx.StaticBitmap(self.Panel, -1, wx.BitmapFromImage(img))

    def CreateButtons(self):
        """Create the buttons"""
        self.AboutButton = wx.Button(self.Panel, wx.ID_ANY, "About")
        self.ExitButton = wx.Button(self.Panel, wx.ID_ANY, "Quit")
        self.OptionsButton = wx.Button(self.Panel, wx.ID_ANY, "View Program Options")
        self.ApplyOperationsButton = wx.Button(self.Panel, wx.ID_ANY, "Apply All Operations")

    def CreateCBs(self):
        """Create the checkboxes"""
        self.BadSectorCheckCB = wx.CheckBox(self.Panel, wx.ID_ANY, "Check All File Systems (thorough)")
        self.CheckFileSystemsCB = wx.CheckBox(self.Panel, wx.ID_ANY, "Check All File Systems (quick)")
        self.ReinstallBootloaderCB = wx.CheckBox(self.Panel, wx.ID_ANY, "Reinstall/Fix Bootloader")
        self.UpdateBootloaderCB = wx.CheckBox(self.Panel, wx.ID_ANY, "Update Bootloader Config")

        #If bootloader is grub legacy, disable some options.
        if SystemInfo["Bootloader"] == "GRUB-LEGACY":
            self.DisableBLOptsGrubLegacy()

    def DisableBLOptsGrubLegacy(self):
        """Called to disable bootloader operations if the bootloader is grub legacy"""
        self.ReinstallBootloaderCB.Disable()
        self.UpdateBootloaderCB.Disable()

    def EnableBLOptsNoGrubLegacy(self):
        """Called to re-enable bootloader operations if the bootloader isn't grub legacy"""
        self.ReinstallBootloaderCB.Enable()
        self.ReinstallBootloaderCB.SetValue(False)
        self.UpdateBootloaderCB.Enable()
        self.UpdateBootloaderCB.SetValue(False)

    def CreateMenus(self):
        """Create the menus"""
        filemenu = wx.Menu()
        viewmenu = wx.Menu()
        editmenu = wx.Menu()
        helpmenu = wx.Menu() 
   
        #Adding Menu Items.
        self.menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.menuExit = filemenu.Append(wx.ID_EXIT,"&Exit", "Terminate this program")
        self.menuSystemInfo = viewmenu.Append(wx.ID_ANY,"&System Information", "Information about all detected disks, OSs, and Bootloaders")
        self.menuNewBootloaderOptions = viewmenu.Append(wx.ID_ANY,"&New Bootloader Options Window", "Have a look at what the new bootloader options window will look like!")
        self.menuOpts = editmenu.Append(wx.ID_PREFERENCES, "&Options", "General settings used to modify your system")

        #Creating the menubar.
        menuBar = wx.MenuBar()

        #Adding menus to the MenuBar
        menuBar.Append(filemenu,"&File")
        menuBar.Append(editmenu,"&Edit")
        menuBar.Append(viewmenu,"&View")
        menuBar.Append(helpmenu,"&Help")

        #Adding the MenuBar to the Frame content.
        self.SetMenuBar(menuBar)

    def OnCheckBox(self, Event=None):
        """Called when one of the checkboxes is checked/unchecked to make sure the options stay valid"""
        logger.debug("MainWindow().OnCheckBox(): Checkboxes have been changed. Making sure options are valid and don't conflict...")
        #Bad Sector Check Choicebox
        if self.BadSectorCheckCB.IsChecked():
            self.CheckFileSystemsCB.Disable()

        else:
            self.CheckFileSystemsCB.Enable()

        #Quick Disk Check Choicebox
        if self.CheckFileSystemsCB.IsChecked():
            self.BadSectorCheckCB.Disable()

        else:
            self.BadSectorCheckCB.Enable()

        #Reinstall Bootloader Choicebox
        if self.ReinstallBootloaderCB.IsChecked() and (SystemInfo["Bootloader"] != "GRUB-LEGACY" or RestoreBootSector):
            self.ReinstallBootloaderCBwaschecked = True
            self.UpdateBootloaderCB.SetValue(0)
            self.UpdateBootloaderCB.Disable()

        elif self.ReinstallBootloaderCB.IsChecked() == False and SystemInfo["Bootloader"] != "GRUB-LEGACY" and RestoreBootSector == False:
            self.UpdateBootloaderCB.Enable()
            self.ReinstallBootloaderCBwaschecked = False

        else:
            self.ReinstallBootloaderCB.SetValue(0)
            self.ReinstallBootloaderCBwaschecked = False

        #Update Bootloader Choicebox
        if self.UpdateBootloaderCB.IsChecked() and (SystemInfo["Bootloader"] != "GRUB-LEGACY" or RestoreBootSector):
            self.UpdateBootloaderCBwaschecked = True
            self.ReinstallBootloaderCB.SetValue(0)
            self.ReinstallBootloaderCB.Disable()

        elif self.UpdateBootloaderCB.IsChecked() == False and SystemInfo["Bootloader"] != "GRUB-LEGACY" and RestoreBootSector == False:
            self.ReinstallBootloaderCB.Enable()
            self.UpdateBootloaderCBwaschecked = False

        else:
            self.UpdateBootloaderCB.SetValue(0)
            self.UpdateBootloaderCBwaschecked = False

        logger.debug("MainWindow().OnCheckBox(): Done. Calling self.SaveMainOpts()...")
        self.SaveMainOpts()

    def Opts(self, Event=None):
        """Starts Settings Window"""
        global OptionsDlg1Run
        logger.debug("MainWindow().Opts(): Starting Settings Window and hiding MainWindow...")

        if self.ReinstallBootloaderCBwaschecked or self.UpdateBootloaderCBwaschecked:
            dlg = wx.MessageDialog(self.Panel, "Do you want to continue? If you reinstall or update your bootloader, some options, such as installing a different bootloader, and restoring a backup of the bootsector, will be reset and disabled. If you want to change other settings, you can always do it after restarting WxFixBoot.", "WxFixBoot - Question", style=wx.YES_NO | wx.ICON_QUESTION, pos=wx.DefaultPosition)

            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()

                dlg = wx.MessageDialog(self.Panel, "You will now be returned to the Main Window.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
                dlg.ShowModal()
                dlg.Destroy()
                return

            dlg.Destroy()

        self.SaveMainOpts()

        if SystemInfo["UEFISystemPartition"] == None:
            dlg = wx.MessageDialog(self.Panel, "Seeing as you have no UEFI partition, you will be unable to select a UEFI bootloader to install, or as your current bootloader. However, in the bootloader options window, you can select a new UEFI partition.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

        if Settings["MainSettings"]["FirmwareType"] == "BIOS":
            dlg = wx.MessageDialog(self.Panel, "Make sure you set the Root Device correctly here! Chances are, you won't need to change it, but it always needs to be set to the device your system boots off (usually the first hard drive in the system). You can see this information in the default OS selection in the following window. For example if your OS boots off /dev/sdc3, the root device should be set to /dev/sdc. The root device here will also be the device that's backed up if either backup option is selected. Thank you.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
            dlg.ShowModal()

        else:
            dlg = wx.MessageDialog(self.Panel, "The boot sector to backup in this case is the UEFI System Partition, if there is one. Thank you.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
            dlg.ShowModal()

        dlg.Destroy()

        OptionsDlg1Run = True
        self.Hide()
        SettingsWindow(self).Show()

    def SystemInfo(self, Event=None):
        """Start SystemInfoWindow"""
        logger.debug("MainWindow().SystemInfo(): Starting System Info Window...")
        SystemInfoWindow(self).Show()

    def ShowNewBLWindow(self, Event=None):
        """Start NewBootloaderOptionsWindow"""
        logger.debug("MainWindow().ShowNewBLWindow(): Starting New Bootloader Options Window...")
        NewBootloaderOptionsWindow(self).Show()

    def ProgressWindow(self, Event=None):
        """Starts Progress Window"""
        if OptionsDlg1Run and self.ReinstallBootloaderCBwaschecked == False and self.UpdateBootloaderCBwaschecked == False:
            logger.debug("MainWindow().ProgressWindow(): Starting Progress Window...")
            self.SaveMainOpts()
            ProgressFrame = ProgressWindow()
            app.SetTopWindow(ProgressFrame)
            ProgressFrame.Show(True)
            self.Destroy()

        else:
            dlg = wx.MessageDialog(self.Panel, "Please check the settings in the Settings Window before continuing, especially after changing the options in the Main Window!", "WxFixBoot - Error", style=wx.OK | wx.ICON_ERROR, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

    def RefreshMainWindow(self,msg):
        """Refresh the main window to reflect changes in the options, or after a restart."""
        logger.debug("MainWindow().RefreshMainWindow(): Refreshing MainWindow...")
            
        #Bootloader options. Also check if the boot sector is to be restored
        if SystemInfo["Bootloader"] == "GRUB-LEGACY" or RestoreBootSector:
            self.DisableBLOptsGrubLegacy()

        else:
            self.EnableBLOptsNoGrubLegacy()

        #Set settings up how they were when MainWindow was hidden earlier, if possible.
        if SystemInfo["Bootloader"] != "GRUB-LEGACY" and RestoreBootSector == False:
            self.ReinstallBootloaderCB.SetValue(ReinstallBootloader)
            self.UpdateBootloaderCB.SetValue(UpdateBootloader)

        self.CheckFileSystemsCB.SetValue(QuickFSCheck)
        self.BadSectorCheckCB.SetValue(BadSectCheck)

        #Enable and Disable Checkboxes as necessary
        self.OnCheckBox()

        #Reset these to avoid errors.
        self.ReinstallBootloaderCBwaschecked = False
        self.UpdateBootloaderCBwaschecked = False

        #Reveal MainWindow
        self.Show()

    def OnAbout(self, Event=None):
        """Shows the About Box"""
        logger.debug("MainWindow().OnAbout(): Showing About Box...")
        aboutbox = wx.AboutDialogInfo()
        aboutbox.Name = "WxFixBoot"
        aboutbox.Version = Version
        aboutbox.Copyright = "(C) 2013-2016 Hamish McIntyre-Bhatty"
        aboutbox.Description = "Utility to fix the bootloader on a\ncomputer quickly"
        aboutbox.WebSite = ("https://launchpad.net/wxfixboot", "Launchpad page")
        aboutbox.Developers = ["Hamish McIntyre-Bhatty"]
        aboutbox.Artists = ["Holly McIntyre-Bhatty (Logo and Splash Screen)"]
        aboutbox.License = "WxFixBoot is free software: you can redistribute it and/or modify it\nunder the terms of the GNU General Public License version 3 or,\nat your option, any later version.\n\nWxFixBoot is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public License\nalong with WxFixBoot.  If not, see <http://www.gnu.org/licenses/>."

        #Show the AboutBox.
        wx.AboutBox(aboutbox)

    def SetupSizers(self):
        """Setup sizers for MainWindow"""
        #Create the main sizer.
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        #Create the check box and Logo sizer.
        CheckBoxAndLogoSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the check box sizer.
        CheckBoxSizer = wx.BoxSizer(wx.VERTICAL)

        #Create the bottom button sizer.
        BottomButtonSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the check box sizer.
        CheckBoxSizer.Add(self.BadSectorCheckCB, 1, wx.BOTTOM, 10)
        CheckBoxSizer.Add(self.CheckFileSystemsCB, 1, wx.BOTTOM, 10)
        CheckBoxSizer.Add(self.ReinstallBootloaderCB, 1, wx.BOTTOM, 10)
        CheckBoxSizer.Add(self.UpdateBootloaderCB, 1, wx.BOTTOM, 10)

        #Add items to the check box and logo sizer.
        CheckBoxAndLogoSizer.Add(CheckBoxSizer, 2, wx.RIGHT, 10)
        CheckBoxAndLogoSizer.Add(self.Logo, 1, wx.TOP|wx.LEFT|wx.ALIGN_RIGHT, 10)

        #Add items to the bottom button sizer.
        BottomButtonSizer.Add(self.AboutButton, 1, wx.RIGHT|wx.EXPAND, 10)
        BottomButtonSizer.Add(self.OptionsButton, 2, wx.RIGHT|wx.EXPAND, 10)
        BottomButtonSizer.Add(self.ExitButton, 1, wx.EXPAND)

        #Add items to the main sizer.
        MainSizer.Add(self.WelcomeText, 10, wx.TOP|wx.BOTTOM|wx.CENTER, 10)
        MainSizer.Add(self.SettingsText, 10, wx.BOTTOM|wx.CENTER, 10)
        MainSizer.Add(CheckBoxAndLogoSizer, 36, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        MainSizer.Add(self.ApplyOperationsButton, 10, wx.BOTTOM|wx.CENTER, 10)
        MainSizer.Add(BottomButtonSizer, 10, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.Panel.SetSizer(MainSizer)
        MainSizer.SetMinSize(wx.Size(400,300))
        MainSizer.SetSizeHints(self)

    def BindEvents(self): 
        """Bind all mainwindow events"""
        self.Bind(wx.EVT_MENU, self.OnAbout, self.menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, self.AboutButton)
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.ExitButton)
        self.Bind(wx.EVT_MENU, self.SystemInfo, self.menuSystemInfo)
        self.Bind(wx.EVT_MENU, self.ShowNewBLWindow, self.menuNewBootloaderOptions)
        self.Bind(wx.EVT_MENU, self.Opts, self.menuOpts)
        self.Bind(wx.EVT_BUTTON, self.Opts, self.OptionsButton)
        self.Bind(wx.EVT_BUTTON, self.ProgressWindow, self.ApplyOperationsButton)

        #Checkboxes on the main window.
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.ReinstallBootloaderCB)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.UpdateBootloaderCB)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.CheckFileSystemsCB)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.BadSectorCheckCB)

    def SaveMainOpts(self):
        """Save all options"""
        logger.debug("MainWindow().SaveMainOpts(): Saving Options on MainWindow...")
        global BootSectorFile
        global RestoreBootSector
        global ReinstallBootloader
        global UpdateBootloader
        global QuickFSCheck
        global BadSectCheck

        #Bad Sector Check Choicebox
        if self.BadSectorCheckCB.IsChecked():
            self.CheckFileSystemsCB.Disable()
            BadSectCheck = True

        else:
            self.CheckFileSystemsCB.Enable()
            BadSectCheck = False

        #Quick Disk Check Choicebox
        if self.CheckFileSystemsCB.IsChecked():
            self.BadSectorCheckCB.Disable()
            QuickFSCheck = True

        else:
            self.BadSectorCheckCB.Enable()
            QuickFSCheck = False

        #Reinstall Bootloader Choicebox
        if self.ReinstallBootloaderCB.IsChecked():
            ReinstallBootloader = True

            #Disable some stuff
            BootSectorFile = "None"
            RestoreBootSector = False

        else:
            ReinstallBootloader = False

        #Update Bootloader Choicebox
        if self.UpdateBootloaderCB.IsChecked():
            UpdateBootloader = True

            #Disable some stuff
            BootSectorFile = "None"
            RestoreBootSector = False

        else:
            UpdateBootloader = False

        logger.debug("MainWindow().SaveMainOpts(): MainWindow options saved! Counting operations to do...")
        self.CountOperations()

    def CountOperations(self):
        """Count the number of operations to do. Called by self.MainMainOpts()"""
        global NumberOfOperations
        global Operations

        #List to contain operations (and their functions) to run.
        Operations = []

        #Run a series of if statements to determine what operations to do, which order to do them in, and the total number to do.
        #Do essential processes first.
        if BackupBootSector:
            Operations.append(EssentialBackendTools.BackupBootSector)
            logger.info("MainWindow().CountOperations(): Added EssentialBackendTools.BackupBootSector to Operations...")

        if RestoreBootSector:
            Operations.append(EssentialBackendTools.RestoreBootSector)
            logger.info("MainWindow().CountOperations(): Added EssentialBackendTools.RestoreBootSector to Operations...")

        if QuickFSCheck:
            Operations.append(EssentialBackendTools.QuickFileSystemCheck)
            logger.info("MainWindow().CountOperations(): Added EssentialBackendTools.QuickFileSystemCheck to Operations...")

        if BadSectCheck:
            Operations.append(EssentialBackendTools.BadSectorCheck)
            logger.info("MainWindow().CountOperations(): Added EssentialBackendTools.BadSectorCheck to Operations...")

        #Now do other processes *** deprecated ***

        if ReinstallBootloader:
            Operations.append(MainBootloaderTools.ReinstallBootloader)
            logger.info("MainWindow().CountOperations(): Added MainBootloaderTools.ReinstallBootloader to Operations...")

        if UpdateBootloader:
            Operations.append(MainBootloaderTools.UpdateBootloader)
            logger.info("MainWindow().CountOperations(): Added MainBootloaderTools.UpdateBootloader to Operations...")

        #*** End of deprecated section ***
        for OS in BootloaderInfo.keys():
            if BootloaderInfo[OS]["Settings"]["ChangeThisOS"]:
                Operations.append([MainBootloaderTools.ManageBootloader, OS])
                logger.info("MainWindow().CountOperations(): Added [MainBootloaderTools.ManageBootloader, "+OS+"] to Operations...")

        #*** Disabled temporarily ***
        #if MakeSystemSummary:
        #    Operations.append(BackendThread(self).GenerateSystemReport)
        #    logger.info("MainWindow().CountOperations(): Added BackendThread().GenerateSystemReport to Operations...")

        #Check if we need to check the internet connection, and do so first if needed.
        if MainBootloaderTools.ManageBootloaders in Operations or MainBootloaderTools.ReinstallBootloader in Operations or MainBootloaderTools.UpdateBootloader in Operations:
            logger.info("MainWindow().CountOperations(): Doing bootloader operations. Adding EssentialBackendTools.CheckInternetConnection()()...")
            Operations.insert(0, EssentialBackendTools.CheckInternetConnection())

        NumberOfOperations = len(Operations)

        #Log gathered operations to do, and the number (verbose mode, default).
        logger.info("MainWindow().CountOperations(): Number of operations: "+unicode(NumberOfOperations))

        if NumberOfOperations == 0:
            logger.info("MainWindow().CountOperations(): No operations to do. Disabling self.ApplyOperationsButton...")
            self.ApplyOperationsButton.SetLabel("No Operations Enabled")
            self.ApplyOperationsButton.Disable()

        else:
            logger.info("MainWindow().CountOperations(): There are operations to do. Enabling self.ApplyOperationsButton...")
            self.ApplyOperationsButton.SetLabel("Apply All Operations")
            self.ApplyOperationsButton.Enable()

    def OnExit(self, Event=None):
        """Shut down."""
        logger.info("MainWindow().OnExit(): Double-checking the exit attempt with the user...")
        dlg = wx.MessageDialog(self.Panel, 'Are you sure you want to exit?', 'WxFixBoot - Question!', wx.YES_NO | wx.ICON_QUESTION)
        Answer = dlg.ShowModal()
        dlg.Destroy()

        if Answer == wx.ID_YES:
            #Run the exit sequence
            logger.info("MainWindow().OnExit(): Exiting...")

            #Shutdown the logger.
            logging.shutdown()

            #Prompt user to save the log file.
            dlg = wx.MessageDialog(self.Panel, "Do you want to keep WxFixBoot's log file? For privacy reasons, WxFixBoot will delete its log file when closing. If you want to save it, which is helpful for debugging if something went wrong, click yes, and otherwise click no.", "WxFixBoot - Question", style=wx.YES_NO | wx.ICON_QUESTION, pos=wx.DefaultPosition)
            Answer = dlg.ShowModal()
            dlg.Destroy()

            if Answer == wx.ID_YES:
                #Ask the user where to save it.
                dlg = wx.FileDialog(self.Panel, "Save log file to...", defaultDir="/home", wildcard="Log Files (*.log)|*.log" , style=wx.SAVE|wx.OVERWRITE_PROMPT)
                Answer = dlg.ShowModal()
                File = dlg.GetPath()
                dlg.Destroy()

                if Answer == wx.ID_OK:
                    #Copy it to the specified path, using a one-liner, and don't bother handling any errors, because this is run as root.
                    CoreTools.StartProcess("cp /tmp/wxfixboot.log "+File)

                    dlg = wx.MessageDialog(self.Panel, 'Done! WxFixBoot will now exit.', 'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()

                else:
                    dlg = wx.MessageDialog(self.Panel, 'Okay, WxFixBoot will now exit without saving the log file.', 'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()

            else:
                dlg = wx.MessageDialog(self.Panel, 'Okay, WxFixBoot will now exit without saving the log file.', 'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

            #Delete the log file, and don't bother handling any errors, because this is run as root.
            os.remove('/tmp/wxfixboot.log')

            self.Destroy()

#End Main window
#Begin System Info Page 1.
class SystemInfoPage1(wx.Panel):
    def __init__(self, ParentWindow, SystemInfoWindow):
        """Initialise SystemInfoPage1"""
        wx.Panel.__init__(self, ParentWindow)
        self.ParentWindow = ParentWindow
        self.SystemInfoWindow = SystemInfoWindow

        logger.debug("SystemInfoPage1().__init__(): Creating widgets...")
        self.Title = "Here are all the detected disks on your computer"
        NoteBookSharedFunctions.CreateWidgets(self)

        logger.debug("SystemInfoPage1().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.SetupSizers(self)

        logger.debug("SystemInfoPage1().__init__(): Binding events...")
        NoteBookSharedFunctions.BindEvents(self)

        logger.debug("SystemInfoPage1().__init__(): Updating list ctrl with Disk info...")
        NoteBookSharedFunctions.UpdateListCtrl(self, Headings=["Name", "Type", "Vendor", "Product", "Capacity", "Description"], Dictionary=DiskInfo)

    def OnSize(self, Event=None):
        """Auto resize the ListCtrl columns"""
        Width, Height = self.ListCtrl.GetClientSizeTuple()

        self.ListCtrl.SetColumnWidth(0, int(Width * 0.15))
        self.ListCtrl.SetColumnWidth(1, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(2, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.3))
        self.ListCtrl.SetColumnWidth(4, int(Width * 0.15))
        self.ListCtrl.SetColumnWidth(5, int(Width * 0.2))

        if Event != None:
            Event.Skip()

#End System Info Page 1
#Begin System Info Page 2.
class SystemInfoPage2(wx.Panel):
    def __init__(self, ParentWindow, SystemInfoWindow):
        """Initialise SystemInfoPage2"""
        wx.Panel.__init__(self, ParentWindow)
        self.ParentWindow = ParentWindow
        self.SystemInfoWindow = SystemInfoWindow

        logger.debug("SystemInfoPage2().__init__(): Creating widgets...")
        self.Title = "Here are all the detected disks on your computer"
        NoteBookSharedFunctions.CreateWidgets(self)

        logger.debug("SystemInfoPage2().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.SetupSizers(self)

        logger.debug("SystemInfoPage2().__init__(): Binding events...")
        NoteBookSharedFunctions.BindEvents(self)

        logger.debug("SystemInfoPage2().__init__(): Updating list ctrl with Disk info...")
        NoteBookSharedFunctions.UpdateListCtrl(self, Headings=["Name", "Type", "Partitions", "Flags", "Partitioning", "FileSystem"], Dictionary=DiskInfo)

    def OnSize(self, Event=None):
        """Auto resize the ListCtrl columns"""
        Width, Height = self.ListCtrl.GetClientSizeTuple()

        self.ListCtrl.SetColumnWidth(0, int(Width * 0.15))
        self.ListCtrl.SetColumnWidth(1, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(2, int(Width * 0.25))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.3))
        self.ListCtrl.SetColumnWidth(4, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(5, int(Width * 0.1))

        if Event != None:
            Event.Skip()

#End System Info Page 2
#Begin System Info Page 3.
class SystemInfoPage3(wx.Panel):
    def __init__(self, ParentWindow, SystemInfoWindow):
        """Initialise SystemInfoPage3"""
        wx.Panel.__init__(self, ParentWindow)
        self.ParentWindow = ParentWindow
        self.SystemInfoWindow = SystemInfoWindow

        logger.debug("SystemInfoPage3().__init__(): Creating widgets...")
        self.Title = "Here are all the detected disks on your computer"
        NoteBookSharedFunctions.CreateWidgets(self)

        logger.debug("SystemInfoPage3().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.SetupSizers(self)

        logger.debug("SystemInfoPage3().__init__(): Binding events...")
        NoteBookSharedFunctions.BindEvents(self)

        logger.debug("SystemInfoPage3().__init__(): Updating list ctrl with Disk info...")
        NoteBookSharedFunctions.UpdateListCtrl(self, Headings=["Name", "Type", "ID", "UUID"], Dictionary=DiskInfo)

    def OnSize(self, Event=None):
        """Auto resize the ListCtrl columns"""
        Width, Height = self.ListCtrl.GetClientSizeTuple()

        self.ListCtrl.SetColumnWidth(0, int(Width * 0.15))
        self.ListCtrl.SetColumnWidth(1, int(Width * 0.15))
        self.ListCtrl.SetColumnWidth(2, int(Width * 0.35))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.35))

        if Event != None:
            Event.Skip()

#End System Info Page 3
#Begin System Info Page 4.
class SystemInfoPage4(wx.Panel):
    def __init__(self, ParentWindow, SystemInfoWindow):
        """Initialise SystemInfoPage4"""
        wx.Panel.__init__(self, ParentWindow)
        self.ParentWindow = ParentWindow
        self.SystemInfoWindow = SystemInfoWindow

        logger.debug("SystemInfoPage4().__init__(): Creating widgets...")
        self.Title = "Here are all the operating systems WxFixBoot detected on your computer"
        NoteBookSharedFunctions.CreateWidgets(self)

        logger.debug("SystemInfoPage4().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.SetupSizers(self)

        logger.debug("SystemInfoPage4().__init__(): Binding events...")
        NoteBookSharedFunctions.BindEvents(self)

        logger.debug("SystemInfoPage4().__init__(): Updating list ctrl with OS Info...")
        NoteBookSharedFunctions.UpdateListCtrl(self, Headings=["Name", "IsCurrentOS", "Arch", "Partition", "PackageManager", "IsModifyable"], Dictionary=OSInfo)

    def OnSize(self, Event=None):
        """Auto resize the ListCtrl columns"""
        Width, Height = self.ListCtrl.GetClientSizeTuple()

        self.ListCtrl.SetColumnWidth(0, int(Width * 0.25))
        self.ListCtrl.SetColumnWidth(1, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(2, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.15))
        self.ListCtrl.SetColumnWidth(4, int(Width * 0.2))
        self.ListCtrl.SetColumnWidth(5, int(Width * 0.2))

        if Event != None:
            Event.Skip()

#End System Info Page 4
#Begin System Info Page 5.
class SystemInfoPage5(wx.Panel):
    def __init__(self, ParentWindow, SystemInfoWindow):
        """Initialise SystemInfoPage5"""
        wx.Panel.__init__(self, ParentWindow)
        self.ParentWindow = ParentWindow
        self.SystemInfoWindow = SystemInfoWindow

        logger.debug("SystemInfoPage5().__init__(): Creating widgets...")
        self.Title = "Here are all the bootloaders WxFixBoot detected on your computer"
        NoteBookSharedFunctions.CreateWidgets(self)

        logger.debug("SystemInfoPage5().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.SetupSizers(self)

        logger.debug("SystemInfoPage5().__init__(): Binding events...")
        NoteBookSharedFunctions.BindEvents(self)

        logger.debug("SystemInfoPage5().__init__(): Updating list ctrl with Bootloader Info...")
        NoteBookSharedFunctions.UpdateListCtrl(self, Headings=["OSName", "Bootloader", "BootDisk", "DefaultOS"], Dictionary=BootloaderInfo)

    def OnSize(self, Event=None):
        """Auto resize the ListCtrl columns"""
        Width, Height = self.ListCtrl.GetClientSizeTuple()

        self.ListCtrl.SetColumnWidth(0, int(Width * 0.4))
        self.ListCtrl.SetColumnWidth(1, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(2, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.4))

        if Event != None:
            Event.Skip()

#End System Info Page 5
#Begin System Info Page 6.
class SystemInfoPage6(wx.Panel):
    def __init__(self, ParentWindow, SystemInfoWindow):
        """Initialise SystemInfoPage6"""
        wx.Panel.__init__(self, ParentWindow)
        self.ParentWindow = ParentWindow
        self.SystemInfoWindow = SystemInfoWindow

        logger.debug("SystemInfoPage6().__init__(): Creating widgets...")
        self.Title = "Here are all the bootloaders WxFixBoot detected on your computer"
        NoteBookSharedFunctions.CreateWidgets(self)

        logger.debug("SystemInfoPage6().__init__(): Setting up sizers...")
        NoteBookSharedFunctions.SetupSizers(self)

        logger.debug("SystemInfoPage6().__init__(): Binding events...")
        NoteBookSharedFunctions.BindEvents(self)

        logger.debug("SystemInfoPage6().__init__(): Updating list ctrl with Bootloader Info...")
        NoteBookSharedFunctions.UpdateListCtrl(self, Headings=["OSName", "Timeout", "GlobalKernelOptions", "IsModifyable", "Comments"], Dictionary=BootloaderInfo)

    def OnSize(self, Event=None):
        """Auto resize the ListCtrl columns"""
        Width, Height = self.ListCtrl.GetClientSizeTuple()

        self.ListCtrl.SetColumnWidth(0, int(Width * 0.4))
        self.ListCtrl.SetColumnWidth(1, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(2, int(Width * 0.2))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.2))

        if Event != None:
            Event.Skip()

#End System Info Page 6
#Begin System Info Window
class SystemInfoWindow(wx.Frame):
    def __init__(self, ParentWindow):
        """Initialize SystemInfoWindow"""
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title="WxFixBoot - System Information", size=(780,310), style=wx.DEFAULT_FRAME_STYLE)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(780,310))
        self.ParentWindow = ParentWindow
        wx.Frame.SetIcon(self, AppIcon)

        #Set up the notebook and the pages.
        self.NoteBook = wx.Notebook(self.Panel)
        Page1 = SystemInfoPage1(self.NoteBook, self)
        Page2 = SystemInfoPage2(self.NoteBook, self)
        Page3 = SystemInfoPage3(self.NoteBook, self)
        Page4 = SystemInfoPage4(self.NoteBook, self)
        Page5 = SystemInfoPage5(self.NoteBook, self)
        Page6 = SystemInfoPage6(self.NoteBook, self)

        self.NoteBook.AddPage(Page1, "Disk Info 1")
        self.NoteBook.AddPage(Page2, "Disk Info 2")
        self.NoteBook.AddPage(Page3, "Disk Info 3")
        self.NoteBook.AddPage(Page4, "OS Info")
        self.NoteBook.AddPage(Page5, "Bootloader Info 1")
        self.NoteBook.AddPage(Page6, "Bootloader Info 2")

        #Set up the sizer.
        MainSizer = wx.BoxSizer()
        MainSizer.Add(self.NoteBook, 1, wx.EXPAND)
        self.Panel.SetSizer(MainSizer)
        MainSizer.SetMinSize(wx.Size(780,310))
        MainSizer.SetSizeHints(self)

        self.BindEvents()

        #Call Layout() on self.Panel() to ensure it displays properly.
        self.Panel.Layout()

        logger.info("SystemInfoWindow().__init__(): Ready. Waiting for events...")

    def BindEvents(self):
        """Bind all events for SystemInfoWindow"""
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def OnExit(self, Event=None):
        """Exit SystemInfoWindow"""
        logger.info("SystemInfoWindow().OnExit(): Closing SystemInfoWindow...")
        self.Destroy()

#End System Info Window
#Begin Settings Window
class SettingsWindow(wx.Frame):
    def __init__(self, ParentWindow):
        """Initialise SettingsWindow"""
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title="WxFixBoot - Settings", size=(600,360), style=wx.DEFAULT_FRAME_STYLE)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(600,360))
        self.ParentWindow = ParentWindow
        wx.Frame.SetIcon(self, AppIcon)

        self.CreateButtons()
        self.CreateText()
        self.CreateCBs()
        self.CreateChoiceBs()
        self.CreateSpinners()
        self.SetupOptions()
        self.SetupSizers()
        self.BindEvents()

        logger.debug("SettingsWindow().__init__(): SettingsWindow Started.")

    def CreateButtons(self):
        """Create Some buttons."""
        self.ExitButton = wx.Button(self.Panel, -1, "Apply these Settings and Close")
        self.BootloaderOptionsButton = wx.Button(self.Panel, -1, "Bootloader Options")
        self.RestoreBootsectorButton = wx.Button(self.Panel, -1, "Restore Boot Sector")

    def CreateText(self):
        """Create the text."""
        self.WelcomeText = wx.StaticText(self.Panel, -1, "Welcome to Settings. Please give everything a once-over.")
        self.BasicSettingsText = wx.StaticText(self.Panel, -1, "Basic Settings:")
        self.InstalledBootloaderText = wx.StaticText(self.Panel, -1, "Installed Bootloader:")
        self.DefaultOSText = wx.StaticText(self.Panel, -1, "Default OS to boot:")
        self.BootloaderTimeoutText = wx.StaticText(self.Panel, -1, "Bootloader timeout value:")
        self.BootloaderTimeoutText2 = wx.StaticText(self.Panel, -1, "(seconds, -1 represents current value)") 
        self.AdvancedSettingsText = wx.StaticText(self.Panel, -1, "Advanced Settings:")
        self.RootDeviceText = wx.StaticText(self.Panel, -1, "Root device:")
        self.BootloaderToInstallText = wx.StaticText(self.Panel, -1, "Bootloader To Install: *** DISABLED DUE TO DEPRECATION ***")
        self.FirmwareTypeText = wx.StaticText(self.Panel, -1, "Selected Firmware Type: "+Settings["MainSettings"]["FirmwareType"])

    def CreateCBs(self):
        """Create the checkboxes"""
        #Basic settings
        self.FullVerboseCheckBox = wx.CheckBox(self.Panel, -1, "Show diagnostic terminal output")

        #Advanced settings
        self.MakeSummaryCheckBox = wx.CheckBox(self.Panel, -1, "Save System Report To File")
        self.LogOutputCheckBox = wx.CheckBox(self.Panel, -1, "Save terminal output in Report")
        self.BackupBootsectorCheckBox = wx.CheckBox(self.Panel, -1, "Backup the Bootsector of "+SystemInfo["RootDevice"])

    def CreateChoiceBs(self):
        """Create the choice boxes"""
        #Basic settings
        self.DefaultOSChoice = wx.Choice(self.Panel, -1, size=(140,30), choices=SystemInfo["UserFriendlyOSNames"])

        #Advanced settings
        self.RootDeviceChoice = wx.Choice(self.Panel, -1, size=(140,30), choices=["Auto: "+SystemInfo["AutoRootDevice"]]+SystemInfo["Devices"])

    def CreateSpinners(self):
        """Create the bootloader time out spinner"""
        #Basic setting.
        self.BootloaderTimeoutSpinner = wx.SpinCtrl(self.Panel, -1, "")
        self.BootloaderTimeoutSpinner.SetRange(-1,100)
        self.BootloaderTimeoutSpinner.SetValue(-1)

    def OnCheckBox(self, Event=None):
        """Manage the checkboxes' states"""
        if self.MakeSummaryCheckBox.IsChecked():
            self.LogOutputCheckBox.Enable()
            self.LogOutputCheckBox.SetValue(True)

        else:
            self.LogOutputCheckBox.SetValue(False)
            self.LogOutputCheckBox.Disable()

    def SetupOptions(self):
        """Load all Options here, and create self.InstalledBootloaderChoice"""
        logger.debug("SettingsWindow().SetupOptions(): Setting up options...")

        #Boot Loader Time Out
        self.BootloaderTimeoutSpinner.SetValue(BootloaderTimeout)

        #Checkboxes
        #Diagnostic output checkbox.
        if FullVerbose:
            self.FullVerboseCheckBox.SetValue(True)

        else:
            self.FullVerboseCheckBox.SetValue(False)

        #Backup Boot Sector CheckBox
        if BackupBootSector:
            self.BackupBootsectorCheckBox.SetValue(True)

        else:
            self.BackupBootsectorCheckBox.SetValue(False)

        #System Summary checkBox
        if MakeSystemSummary:
            self.MakeSummaryCheckBox.SetValue(True)

        else:
            self.MakeSummaryCheckBox.SetValue(False)

        #Save output checkbox.
        if SaveOutput:
            self.LogOutputCheckBox.SetValue(True)

        else:
            self.LogOutputCheckBox.SetValue(False)

        if SystemInfo["UEFISystemPartition"] == None:
            self.InstalledBootloaderChoice = wx.Choice(self.Panel, -1, size=(140,30), choices=['Auto: '+SystemInfo["AutoBootloader"], 'GRUB-LEGACY', 'GRUB2', 'LILO'])

        else:
            self.InstalledBootloaderChoice = wx.Choice(self.Panel, -1, size=(140,30), choices=['Auto: '+SystemInfo["AutoBootloader"], 'GRUB-LEGACY', 'GRUB2', 'GRUB-UEFI', 'LILO', 'ELILO'])

        #Installed Bootloader
        if SystemInfo["Bootloader"] != SystemInfo["AutoBootloader"]:
            self.InstalledBootloaderChoice.SetStringSelection(SystemInfo["Bootloader"])

        else:
            self.InstalledBootloaderChoice.SetSelection(0)

        #Default OS
        self.DefaultOSChoice.SetStringSelection(SystemInfo["DefaultOS"])
        
        #Root Device
        if SystemInfo["RootDevice"] != SystemInfo["AutoRootDevice"]:
            self.RootDeviceChoice.SetStringSelection(SystemInfo["RootDevice"])

        else:
            self.RootDeviceChoice.SetSelection(0)

        if RestoreBootSector:
            #Disable/reset some options.
            self.BootloaderOptionsButton.Disable()
            self.InstalledBootloaderChoice.Disable()
            self.DefaultOSChoice.Disable()
            self.BootloaderTimeoutSpinner.SetValue(-1)
            self.BootloaderTimeoutSpinner.Disable()

        else:
            #Enable some options.
            self.BootloaderOptionsButton.Enable()
            self.InstalledBootloaderChoice.Enable()
            self.DefaultOSChoice.Enable()

        #Disable some options if the bootloader is to be reinstalled or updated.
        if ReinstallBootloader or UpdateBootloader:
            self.BootloaderOptionsButton.Disable()
            self.RestoreBootsectorButton.Disable()

        logger.debug("SettingsWindow().SetupOptions(): Finished!")

    def SetupSizers(self):
        """Setup all sizers for OptionsWindow"""
        #Create the main sizer.
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        #Create the highest-level sizer that holds all of the settings.
        AllSettingsSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the sizer that holds the basic settings.
        BasicSettingsSizer = wx.BoxSizer(wx.VERTICAL)

        #Create the sizer that holds the advanced settings.
        AdvancedSettingsSizer = wx.BoxSizer(wx.VERTICAL)

        #Create the sizer that holds the intalled bootloader choice and text.
        self.InstalledBootloaderChoiceSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the sizer that holds the default OS choice and text.
        DefaultOSChoiceSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the sizer that holds the bootloader timeout choice and text.
        BootloaderTimeoutSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the sizer that holds the root device choice and text.
        RootDeviceChoiceSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the sizer that holds the bootloader options button and text.
        BootloaderOptionsSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the sizer that holds the buttons at the bottom of the window.
        BottomButtonSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the Installed Bootloader Choice Sizer.
        self.InstalledBootloaderChoiceSizer.Add(self.InstalledBootloaderText, 1, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        self.InstalledBootloaderChoiceSizer.Add(self.InstalledBootloaderChoice, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)

        #Add items to the Default OS Choice Sizer.
        DefaultOSChoiceSizer.Add(self.DefaultOSText, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        DefaultOSChoiceSizer.Add(self.DefaultOSChoice, 1, wx.RIGHT|wx.LEFT|wx.FIXED_MINSIZE|wx.ALIGN_CENTER, 5)

        #Add items to the Bootloader timeout Sizer.
        BootloaderTimeoutSizer.Add(self.BootloaderTimeoutText, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        BootloaderTimeoutSizer.Add(self.BootloaderTimeoutSpinner, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to the Root Device Choice Sizer.
        RootDeviceChoiceSizer.Add(self.RootDeviceText, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        RootDeviceChoiceSizer.Add(self.RootDeviceChoice, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to the basic settings sizer.
        BasicSettingsSizer.Add(self.BasicSettingsText, 1, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, 10)
        BasicSettingsSizer.Add(self.InstalledBootloaderChoiceSizer, 1, wx.BOTTOM|wx.EXPAND, 10)
        BasicSettingsSizer.Add(DefaultOSChoiceSizer, 1, wx.BOTTOM|wx.EXPAND, 10)
        BasicSettingsSizer.Add(self.FullVerboseCheckBox, 1, wx.BOTTOM, 10)
        BasicSettingsSizer.Add(BootloaderTimeoutSizer, 1, wx.BOTTOM|wx.EXPAND, 10)
        BasicSettingsSizer.Add(self.BootloaderTimeoutText2, 1, wx.BOTTOM, 10)

        #Add items to the advanced settings sizer.
        AdvancedSettingsSizer.Add(self.AdvancedSettingsText, 1, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, 10)
        AdvancedSettingsSizer.Add(RootDeviceChoiceSizer, 1, wx.BOTTOM|wx.EXPAND, 10)
        AdvancedSettingsSizer.Add(self.MakeSummaryCheckBox, 1, wx.BOTTOM, 10)
        AdvancedSettingsSizer.Add(self.LogOutputCheckBox, 1, wx.BOTTOM, 10)
        AdvancedSettingsSizer.Add(self.BackupBootsectorCheckBox, 1, wx.BOTTOM, 10)

        #Add items to the all settings sizer.
        AllSettingsSizer.Add(BasicSettingsSizer, 4, wx.RIGHT|wx.EXPAND, 5)
        AllSettingsSizer.Add(wx.StaticLine(self.Panel), 0, wx.EXPAND)
        AllSettingsSizer.Add(AdvancedSettingsSizer, 3, wx.LEFT|wx.EXPAND, 5)

        #Add items to the bootloader options sizer.
        BootloaderOptionsSizer.Add(self.BootloaderToInstallText, 1, wx.RIGHT|wx.EXPAND|wx.ALIGN_CENTER, 5)
        BootloaderOptionsSizer.Add(self.BootloaderOptionsButton, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        BootloaderOptionsSizer.Add(self.FirmwareTypeText, 1, wx.LEFT|wx.EXPAND|wx.ALIGN_CENTER, 5)

        #Add items to the bottom button sizer.
        BottomButtonSizer.Add(self.RestoreBootsectorButton, 2, wx.RIGHT|wx.ALIGN_CENTER, 5)
        BottomButtonSizer.Add(self.ExitButton, 3, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to the main sizer.
        MainSizer.Add(self.WelcomeText, 1, wx.ALL|wx.ALIGN_CENTER, 10)
        MainSizer.Add(wx.StaticLine(self.Panel), 0, wx.BOTTOM|wx.EXPAND, 10)
        MainSizer.Add(AllSettingsSizer, 6, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 10)
        MainSizer.Add(wx.StaticLine(self.Panel), 0, wx.BOTTOM|wx.EXPAND, 10)
        MainSizer.Add(BootloaderOptionsSizer, 1, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 10)
        MainSizer.Add(wx.StaticLine(self.Panel), 0, wx.BOTTOM|wx.EXPAND, 10)
        MainSizer.Add(BottomButtonSizer, 1, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.Panel.SetSizer(MainSizer)
        MainSizer.SetMinSize(wx.Size(600,360))
        MainSizer.SetSizeHints(self)

    def BindEvents(self):
        """Bind events for SettingsWindow"""
        self.Bind(wx.EVT_BUTTON, self.CloseOpts, self.ExitButton)
        self.Bind(wx.EVT_CLOSE, self.CloseOpts)
        self.Bind(wx.EVT_BUTTON, self.LaunchblOpts, self.BootloaderOptionsButton)
        self.Bind(wx.EVT_BUTTON, self.LaunchBootSectWindow, self.RestoreBootsectorButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.MakeSummaryCheckBox)

    def LaunchblOpts(self, Event=None):
        """Start the Bootloader Options Window"""
        #Safeguard program reliability (and continuity) by saving the settings in optionswindow1 first.
        logger.debug("SettingsWindow().LaunchblOpts(): Calling self.SaveOptions()...")
        self.SaveOptions()

        #Give some warnings here if needed.
        #Tell the user some options will be disabled if the bootloader is to be reinstalled or updated.
        if ReinstallBootloader or UpdateBootloader:
            logger.info("SettingsWindow().LaunchblOpts(): Bootloader will be reinstalled or updated, almost all options relating to bootloaders will be disabled.")
            dlg = wx.MessageDialog(self.Panel, "Your current bootloader is to be reinstalled or updated, therefore almost all bootloader-related options here will be disabled. If you want to install a different bootloader, please uncheck the reinstall or update bootloader option in the main window.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

        #Recommend a MBR bootloader on BIOS systems.
        if Settings["MainSettings"]["FirmwareType"] == "BIOS":
            dlg = wx.MessageDialog(self.Panel, "Your firmware type is BIOS. Unless you're sure WxFixBoot has misdetected this, and it's actually UEFI, it's recommended that you install an BIOS bootloader, if you are installing a bootloader, such as GRUB2 or LILO, or your system might not boot correctly.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)

        #Recommend a UEFI boot loader on UEFI systems, if needed.
        else:
            dlg = wx.MessageDialog(self.Panel, "Your firmware type is UEFI. Unless you're sure WxFixBoot has misdetected this, and it's actually BIOS, it's recommended that you install a UEFI bootloader, if you are installing a bootloader, such as GRUB-UEFI or ELILO, or your system might not boot correctly.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)

        dlg.ShowModal()
        dlg.Destroy()

        if SystemInfo["UEFISystemPartition"] == None and SystemInfo["Bootloader"] in ('GRUB-UEFI', 'ELILO'):
            logger.info("SettingsWindow().LaunchblOpts(): UEFI bootloader, but no UEFI partition! Something has gone wrong here! WxFixBoot will not install a UEFI bootloader without a UEFI partition, as it's impossible, and those options will now be disabled.")
            dlg = wx.MessageDialog(self.Panel, "You have a UEFI Bootloader, but no UEFI Partition! Something has gone wrong here! WxFixBoot will not install a UEFI bootloader without a UEFI partition, as it's impossible, and those options will now be disabled. Did you change your selected UEFI Partition?", "WxFixBoot - ERROR", style=wx.OK | wx.ICON_ERROR, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

        elif SystemInfo["UEFISystemPartition"] == None:
            logger.info("SettingsWindow().LaunchblOpts(): No UEFI partition. Therefore installing UEFI bootloaders will be disabled.")
            dlg = wx.MessageDialog(self.Panel, "You have no UEFI Partition. If you wish to install a UEFI bootloader, you'll need to create one first. WxFixBoot will not install a UEFI bootloader without a UEFI partition, as it's impossible, and those options will now be disabled.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

        dlg = wx.MessageDialog(self.Panel, "Most of the settings in the following dialog do not need to be and shouldn't be touched, with the exception of autodetermining the bootloader, or manually selecting one. The firmware type and partition schemes should not normally be changed. Thank you.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
        dlg.ShowModal()
        dlg.Destroy()

        #Open the Firmware Options window
        logger.debug("SettingsWindow().LaunchblOpts(): Starting Bootloader Settings Window...")
        self.Hide()
        BootloaderOptionsWindow(self).Show()

    def LaunchBootSectWindow(self, Event=None):
        """Launch RestoreWindow in boot sector mode"""
        #Safeguard program reliability (and continuity) by saving the settings in optionswindow1 first.
        self.SaveOptions()

        logger.debug("SettingsWindow().LaunchBootSectWindow(): Starting Restore Bootsector Window...")
        #Show helpful info if the root device uses gpt.
        if DiskInfo[SystemInfo["RootDevice"]]["Partitioning"] == "gpt": #*** This is silly ***
            dlg = wx.MessageDialog(self.Panel, "Because the selected root device uses gpt, the Target Device selection in the following dialog will be ignored, though you must still set it, and the backup will always be restored to the UEFI Partition. Please keep this in mind and be sure that the UEFI Partition chosen is correct. You can check and change this in the Bootloader Options.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

        self.Hide()
        RestoreWindow(ParentWindow=self).Show()

    def RefreshOptionsDlg1(self,msg):
        """Refresh the settings in SettingsWindow before re-showing it"""
        #Check if the boot sector is to be restored.
        logger.debug("SettingsWindow().RefreshOptionsDlg1(): Refreshing SettingsWindow...")
        if RestoreBootSector:
            #Disable/reset some options.
            self.BootloaderOptionsButton.Disable()
            self.InstalledBootloaderChoice.Disable()
            self.DefaultOSChoice.Disable()
            self.BootloaderTimeoutSpinner.SetValue(-1)
            self.BootloaderTimeoutSpinner.Disable()

            #Reset some settings.
            Settings["MainSettings"]["FirmwareType"] = SystemInfo["DetectedFirmwareType"]

        else:
            #Enable some options.
            self.BootloaderOptionsButton.Enable()
            self.InstalledBootloaderChoice.Enable()
            self.DefaultOSChoice.Enable()
            self.BootloaderTimeoutSpinner.Enable()

        #Setup options again, but destroy a widget first so it isn't duplicated.
        self.InstalledBootloaderChoice.Destroy()
        self.SetupOptions()

        #Red add self.InstalledBootloaderChoice into its sizer.
        self.InstalledBootloaderChoiceSizer.Add(self.InstalledBootloaderChoice, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        self.Panel.Layout()

        #Update the FirmwareType text.
        self.FirmwareTypeText.SetLabel("Selected Firmware Type: "+Settings["MainSettings"]["FirmwareType"])

        #Show OptionsDlg1.
        self.Show()

    def SaveOptions(self, Event=None):
        """Save all options"""
        global SaveOutput
        global FullVerbose
        global SaveOutput
        global BackupBootSector
        global MakeSystemSummary
        global BootloaderTimeout

        logger.info("SettingsWindow().SaveOptions(): Saving Options...")
        
        #Checkboxes.
        #Create Log checkbox.
        if self.LogOutputCheckBox.IsChecked():
            SaveOutput = True

        else:
            SaveOutput = False

        logger.debug("SettingsWindow().SaveOptions(): Value of SaveOutput is: "+unicode(SaveOutput))

        #Check FS cb
        if self.FullVerboseCheckBox.IsChecked():
            FullVerbose = True

        else:
            FullVerbose = False

        logger.debug("SettingsWindow().SaveOptions(): Value of FullVerbose is: "+unicode(FullVerbose))

        #Remount FS CB
        if self.LogOutputCheckBox.IsChecked():
            SaveOutput = True

        else:
            SaveOutput = False

        logger.debug("SettingsWindow().SaveOptions(): Value of SaveOutput is: "+unicode(SaveOutput))

        #Backup BootSector checkbox.
        if self.BackupBootsectorCheckBox.IsChecked():
            BackupBootSector = True

        else:
            BackupBootSector = False

        logger.debug("SettingsWindow().SaveOptions(): Value of BackupBootSector is: "+unicode(BackupBootSector))

        #Use chroot in operations checkbox
        if self.MakeSummaryCheckBox.IsChecked():
            MakeSystemSummary = True

        else:
            MakeSystemSummary = False

        logger.debug("SettingsWindow().SaveOptions(): Value of MakeSystemSummary is: "+unicode(MakeSystemSummary))

        #ChoiceBoxes
        #Currently Installed Bootloader ChoiceBox
        if self.InstalledBootloaderChoice.GetSelection() != 0:
            SystemInfo["Bootloader"] = self.InstalledBootloaderChoice.GetStringSelection()

        else:
            #Set it to the auto value, using AutoBootloader
            SystemInfo["Bootloader"] = SystemInfo["AutoBootloader"]

        logger.debug("SettingsWindow().SaveOptions(): Value of Bootloader is: "+SystemInfo["Bootloader"])

        #Default OS choicebox.
        SystemInfo["DefaultOS"] = self.DefaultOSChoice.GetStringSelection()

        logger.debug("SettingsWindow().SaveOptions(): The default OS is: "+SystemInfo["DefaultOS"])

        #Root Filesystem.
        SystemInfo["RootFS"] = OSInfo[SystemInfo["DefaultOS"]]["Partition"]
        logger.debug("SettingsWindow().SaveOptions(): Value of SystemInfo['RootFS'] is: "+SystemInfo["RootFS"])

        #Root device ChoiceBox
        if self.RootDeviceChoice.GetSelection() != 0:
            SystemInfo["RootDevice"] = self.RootDeviceChoice.GetStringSelection()

        else:
            #Set it to the auto value, in case this has already been changed.
            SystemInfo["RootDevice"] = SystemInfo["AutoRootDevice"]

        logger.debug("SettingsWindow().SaveOptions(): Value of RootDevice is: "+SystemInfo["RootDevice"])

        #Spinner
        BootloaderTimeout = int(self.BootloaderTimeoutSpinner.GetValue())
        logger.debug("SettingsWindow().SaveOptions(): Value of BootloaderTimeout is: "+unicode(BootloaderTimeout))

        logger.info("SettingsWindow().SaveOptions(): Saved options.")

    def CloseOpts(self, Event=None):
        """Save options and close SettingsWindow"""
        #Save the options first.
        self.SaveOptions()

        #Send a message to mainwindow so it can refresh.
        wx.CallAfter(self.ParentWindow.RefreshMainWindow, "Closed")

        #Exit options window 1.
        logger.debug("SettingsWindow().SaveOptions(): SettingsWindow is closing. Revealing MainWindow...")
        self.Destroy()

#End Settings Window
#Begin New Bootloader Options Window.
class NewBootloaderOptionsWindow(wx.Frame): #*** Add comments and logging stuff ***
    def __init__(self, ParentWindow):
        """Initialise bootloader options window"""
        wx.Frame.__init__(self, parent=wx.GetApp().TopWindow, title="WxFixBoot - Bootloader Options", size=(400,200), style=wx.DEFAULT_FRAME_STYLE)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(800,800))
        self.ParentWindow = ParentWindow
        wx.Frame.SetIcon(self, AppIcon)

        self.CreateText()
        self.CreateChoiceBoxes()
        self.CreateCheckBoxes()
        self.CreateButtons()
        self.CreateOtherWidgets()
        self.SetupSizers()
        self.BindEvents()

        #Set up the window.
        if SystemInfo["PreviousOSChoice"] == "":
            SystemInfo["PreviousOSChoice"] = SystemInfo["UserFriendlyOSNames"][0]

        self.OnOSChoiceChange(Startup=True)
        
        logger.debug("BootloaderOptionsWindow().__init__(): Bootloader Options Window Started.")

    def CreateText(self):
        """Create the text"""
        self.TitleText = wx.StaticText(self.Panel, -1, "Select each OS you want to modify")
        self.OSInfoText = wx.lib.stattext.GenStaticText(self.Panel, -1, "OS Info")

        #Basic Options.
        self.BasicOptionsText = wx.lib.stattext.GenStaticText(self.Panel, -1, "Basic Options")
        self.NewTimeoutText = wx.StaticText(self.Panel, -1, "New timeout (in seconds):")
        self.DefaultOSText = wx.StaticText(self.Panel, -1, "Default OS to boot:")

        #Advanced Options.
        self.AdvancedOptionsText = wx.lib.stattext.GenStaticText(self.Panel, -1, "Advanced Options")
        self.NewBootloaderText = wx.StaticText(self.Panel, -1, "")
        self.BackupBootloaderText = wx.StaticText(self.Panel, -1, "Backup to:")
        self.RestoreBootloaderText = wx.StaticText(self.Panel, -1, "Restore from:")

    def CreateChoiceBoxes(self):
        """Create the choice boxes"""
        self.OSChoice = wx.Choice(self.Panel, -1, choices=SystemInfo["UserFriendlyOSNames"])
        self.OSChoice.SetStringSelection(SystemInfo["PreviousOSChoice"])

        #Basic Options.
        self.DefaultOSChoice = wx.Choice(self.Panel, -1, choices=SystemInfo["UserFriendlyOSNames"])

        #Advanced Options.
        self.NewBootloaderChoice = wx.Choice(self.Panel, -1, choices=["-- Please Select --", "GRUB-UEFI", "GRUB2", "ELILO", "LILO"]) #*** Disable EFI options on BIOS systems ***
        self.BackupBootloaderChoice = wx.Choice(self.Panel, -1, choices=["-- Please Select --", "Specify"])
        self.RestoreBootloaderChoice = wx.Choice(self.Panel, -1, choices=["-- Please Select --", "Specify"])

    def CreateCheckBoxes(self):
        """Create the check boxes"""
        #Basic Options.
        self.ReinstallBootloaderCheckBox = wx.CheckBox(self.Panel, -1, "")
        self.UpdateBootloaderCheckBox = wx.CheckBox(self.Panel, -1, "")
        self.KeepBootloaderTimeoutCheckBox = wx.CheckBox(self.Panel, -1, "")

        #Advanced Options.
        self.InstallNewBootloaderCheckBox = wx.CheckBox(self.Panel, -1, "Install a New Bootloader")
        self.BackupBootloaderCheckBox = wx.CheckBox(self.Panel, -1, "")
        self.RestoreBootloaderCheckBox = wx.CheckBox(self.Panel, -1, "Restore this OS's bootloader")

    def CreateButtons(self):
        """Create the buttons"""
        self.SystemInfoButton = wx.Button(self.Panel, -1, "View More Details")
        self.RevertOSChangesButton = wx.Button(self.Panel, -1, "Revert Changes for this OS")
        self.RevertAllChangesButton = wx.Button(self.Panel, -1, "Revert All Changes")
        self.SaveButton = wx.Button(self.Panel, -1, "Save All Changes And Close")

    def CreateOtherWidgets(self):
        """Create all other widgets"""
        #Bootloader timeout spinner.
        self.BootloaderTimeoutSpinner = wx.SpinCtrl(self.Panel, -1, "")
        self.BootloaderTimeoutSpinner.SetRange(1,100)

        #Arrows.
        img1 = wx.Image("/usr/share/wxfixboot/images/ArrowDown.png", wx.BITMAP_TYPE_PNG)
        img2 = wx.Image("/usr/share/wxfixboot/images/ArrowRight.png", wx.BITMAP_TYPE_PNG)
        self.DownArrowImage = wx.BitmapFromImage(img1)
        self.RightArrowImage = wx.BitmapFromImage(img2)

        self.Arrow1 = wx.lib.statbmp.GenStaticBitmap(self.Panel, -1, self.DownArrowImage)
        self.Arrow2 = wx.lib.statbmp.GenStaticBitmap(self.Panel, -1, self.DownArrowImage)
        self.Arrow3 = wx.lib.statbmp.GenStaticBitmap(self.Panel, -1, self.DownArrowImage)

        #List Ctrl.
        self.ListCtrl = wx.ListCtrl(self.Panel, -1, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_VRULES)
        NoteBookSharedFunctions.UpdateListCtrl(self, Headings=["Name", "IsCurrentOS", "Arch", "Partition", "PackageManager", "IsModifyable"], Dictionary=OSInfo)

    def OnSize(self, Event=None):
        """Auto resize the ListCtrl columns"""
        Width, Height = self.ListCtrl.GetClientSizeTuple()

        self.ListCtrl.SetColumnWidth(0, int(Width * 0.25))
        self.ListCtrl.SetColumnWidth(1, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(2, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.15))
        self.ListCtrl.SetColumnWidth(4, int(Width * 0.2))
        self.ListCtrl.SetColumnWidth(5, int(Width * 0.2))

        if Event != None:
            Event.Skip()

    def SetupSizers(self):
        """Setup the sizers"""
        self.MainSizer = wx.BoxSizer(wx.VERTICAL)

        OSInfoSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to OSInfoSizer.
        OSInfoSizer.Add((5,5), 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        OSInfoSizer.Add(self.OSInfoText, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        OSInfoSizer.Add(self.Arrow1, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        OSInfoSizer.Add((5,5), 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        BasicOptionsSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to BasicOptionsSizer.
        BasicOptionsSizer.Add((5,5), 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        BasicOptionsSizer.Add(self.BasicOptionsText, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        BasicOptionsSizer.Add(self.Arrow2, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        BasicOptionsSizer.Add((5,5), 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        self.FixAndUpdateBootloaderSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to FixAndUpdateBootloaderSizer.
        self.FixAndUpdateBootloaderSizer.Add(self.ReinstallBootloaderCheckBox, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        self.FixAndUpdateBootloaderSizer.Add(self.UpdateBootloaderCheckBox, 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        self.TimeoutSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to TimeoutSizer.
        self.TimeoutSizer.Add(self.KeepBootloaderTimeoutCheckBox, 3, wx.RIGHT|wx.ALIGN_CENTER, 5)
        self.TimeoutSizer.Add((5,5), 1, wx.RIGHT|wx.LEFT, 5)
        self.TimeoutSizer.Add(self.NewTimeoutText, 2, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        self.TimeoutSizer.Add(self.BootloaderTimeoutSpinner, 3, wx.LEFT|wx.ALIGN_CENTER, 5)

        self.DefaultOSSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to DefaultOSSizer.
        self.DefaultOSSizer.Add(self.DefaultOSText, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        self.DefaultOSSizer.Add(self.DefaultOSChoice, 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        AdvancedOptionsSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to AdvancedOptionsSizer.
        AdvancedOptionsSizer.Add((5,5), 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        AdvancedOptionsSizer.Add(self.AdvancedOptionsText, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        AdvancedOptionsSizer.Add(self.Arrow3, 0, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        AdvancedOptionsSizer.Add((5,5), 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        self.InstallNewBootloaderSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to InstallNewBootloaderSizer.
        self.InstallNewBootloaderSizer.Add(self.InstallNewBootloaderCheckBox, 2, wx.RIGHT, 5)
        self.InstallNewBootloaderSizer.Add(self.NewBootloaderText, 1, wx.RIGHT|wx.LEFT, 5)
        self.InstallNewBootloaderSizer.Add(self.NewBootloaderChoice, 2, wx.LEFT, 5)

        self.BackupBootloaderSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to BackupBootloaderSizer.
        self.BackupBootloaderSizer.Add(self.BackupBootloaderCheckBox, 2, wx.RIGHT|wx.ALIGN_CENTER, 5)
        self.BackupBootloaderSizer.Add(self.BackupBootloaderText, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        self.BackupBootloaderSizer.Add(self.BackupBootloaderChoice, 2, wx.LEFT|wx.ALIGN_CENTER, 5)

        self.RestoreBootloaderSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to RestoreBootloaderSizer.
        self.RestoreBootloaderSizer.Add(self.RestoreBootloaderCheckBox, 2, wx.RIGHT|wx.ALIGN_CENTER, 5)
        self.RestoreBootloaderSizer.Add(self.RestoreBootloaderText, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        self.RestoreBootloaderSizer.Add(self.RestoreBootloaderChoice, 2, wx.LEFT|wx.ALIGN_CENTER, 5)

        BottomButtonSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to BottomButtonSizer.
        BottomButtonSizer.Add(self.RevertOSChangesButton, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        BottomButtonSizer.Add(self.RevertAllChangesButton, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        BottomButtonSizer.Add(self.SaveButton, 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to MainSizer.
        self.MainSizer.Add(self.TitleText, 1, wx.ALL|wx.CENTER, 10)
        self.MainSizer.Add(self.OSChoice, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(wx.StaticLine(self.Panel), 0, wx.ALL|wx.EXPAND, 10)
        self.MainSizer.Add(OSInfoSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.ListCtrl, 5, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.SystemInfoButton, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(wx.StaticLine(self.Panel), 0, wx.ALL|wx.EXPAND, 10)
        self.MainSizer.Add(BasicOptionsSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.FixAndUpdateBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.TimeoutSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.DefaultOSSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(wx.StaticLine(self.Panel), 0, wx.ALL|wx.EXPAND, 10)
        self.MainSizer.Add(AdvancedOptionsSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.InstallNewBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.BackupBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.RestoreBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(wx.StaticLine(self.Panel), 0, wx.ALL|wx.EXPAND, 10)
        self.MainSizer.Add(BottomButtonSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.Panel.SetSizer(self.MainSizer)
        #self.MainSizer.SetMinSize(wx.Size(936,360))

    def LoadSettings(self, Event=None):
        """Load all settings for this OS into the checkboxes and choice boxes"""
        OS = self.OSChoice.GetStringSelection()

        self.ReinstallBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["Reinstall"])
        self.UpdateBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["Update"])
        self.KeepBootloaderTimeoutCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["KeepExistingTimeout"])
        self.BootloaderTimeoutSpinner.SetValue(BootloaderInfo[OS]["Settings"]["NewTimeout"])
        self.DefaultOSChoice.SetStringSelection(BootloaderInfo[OS]["Settings"]["DefaultOS"])
        self.InstallNewBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["InstallNewBootloader"])
        self.NewBootloaderChoice.SetStringSelection(BootloaderInfo[OS]["Settings"]["NewBootloader"])
        self.BackupBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["BackupBootloader"])
        self.BackupBootloaderChoice.SetStringSelection(BootloaderInfo[OS]["Settings"]["BootloaderBackupTarget"])
        self.RestoreBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["RestoreBootloader"])
        self.RestoreBootloaderChoice.SetStringSelection(BootloaderInfo[OS]["Settings"]["BootloaderRestoreSource"])

    def SetGUIState(self, Event=None):
        """Set all the GUI element's states (enabled/disabled) for this OS"""
        OS = self.OSChoice.GetStringSelection()

        self.ReinstallBootloaderCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["ReinstallCheckBoxState"])
        self.UpdateBootloaderCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["UpdateCheckBoxState"])
        self.KeepBootloaderTimeoutCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["KeepExistingTimeoutCheckBoxState"])
        self.BootloaderTimeoutSpinner.Enable(BootloaderInfo[OS]["GUIState"]["NewTimeoutSpinnerState"])
        self.DefaultOSChoice.Enable(BootloaderInfo[OS]["GUIState"]["DefaultOSChoiceState"])
        self.InstallNewBootloaderCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["InstallNewBootloaderCheckBoxState"])
        self.NewBootloaderChoice.Enable(BootloaderInfo[OS]["GUIState"]["NewBootloaderChoiceState"])
        self.BackupBootloaderCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["BackupBootloaderCheckBoxState"])
        self.BackupBootloaderChoice.Enable(BootloaderInfo[OS]["GUIState"]["BackupBootloaderChoiceState"])
        self.RestoreBootloaderCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["RestoreBootloaderCheckBoxState"])
        self.RestoreBootloaderChoice.Enable(BootloaderInfo[OS]["GUIState"]["RestoreBootloaderChoiceState"])

    def BindEvents(self):
        """Bind all events for BootloaderOptionsWindow"""
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        #Text.
        self.OSInfoText.Bind(wx.EVT_LEFT_DOWN, self.OnOSInfo)
        self.BasicOptionsText.Bind(wx.EVT_LEFT_DOWN, self.OnBasicOptions)
        self.AdvancedOptionsText.Bind(wx.EVT_LEFT_DOWN, self.OnAdvancedOptions)

        #Images.
        self.Arrow1.Bind(wx.EVT_LEFT_DOWN, self.OnOSInfo)
        self.Arrow2.Bind(wx.EVT_LEFT_DOWN, self.OnBasicOptions)
        self.Arrow3.Bind(wx.EVT_LEFT_DOWN, self.OnAdvancedOptions)

        #Checkboxes.
        self.Bind(wx.EVT_CHECKBOX, self.OnTimeoutCheckBox, self.KeepBootloaderTimeoutCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnUpdateOrReinstallCheckBox, self.ReinstallBootloaderCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnUpdateOrReinstallCheckBox, self.UpdateBootloaderCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnInstallNewBootloaderCheckBox, self.InstallNewBootloaderCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnBackupBootloaderCheckBox, self.BackupBootloaderCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.OnRestoreBootloaderCheckBox, self.RestoreBootloaderCheckBox)

        #Buttons.
        self.Bind(wx.EVT_BUTTON, self.OnClose, self.SaveButton)

        #Choiceboxes.
        self.Bind(wx.EVT_CHOICE, self.OnOSChoiceChange, self.OSChoice)

    def OnOSChoiceChange(self, Event=None, Startup=False):
        """Save and load new GUI settings and states in accordance with the OS choice change"""
        if Startup == False:
            self.SaveSettings(OS=SystemInfo["PreviousOSChoice"])
            self.SaveGUIState(OS=SystemInfo["PreviousOSChoice"])

        self.LoadSettings()
        self.SetGUIState()
        self.SetTextLabels()

        #Make sure the window displays properly.
        self.MainSizer.SetSizeHints(self)

    def SetTextLabels(self):
        """Set text labels for GUI elements"""
        OS = self.OSChoice.GetStringSelection()

        self.InstallNewBootloaderCheckBox.SetLabel("Replace "+BootloaderInfo[OS]["Bootloader"]+" with:")
        self.ReinstallBootloaderCheckBox.SetLabel("Fix/Reinstall "+BootloaderInfo[OS]["Bootloader"])
        self.UpdateBootloaderCheckBox.SetLabel("Update "+BootloaderInfo[OS]["Bootloader"]+"'s Config")
        self.KeepBootloaderTimeoutCheckBox.SetLabel("Keep "+BootloaderInfo[OS]["Bootloader"]+"'s existing menu timeout")
        self.BackupBootloaderCheckBox.SetLabel("Backup "+BootloaderInfo[OS]["Bootloader"])

    def OnUpdateOrReinstallCheckBox(self, Event=None):
        """Enable/Disable the bootloader timeout checkbox, based on the value of the update/reinstall checkboxes."""
        if self.ReinstallBootloaderCheckBox.IsChecked():
            self.UpdateBootloaderCheckBox.Disable()
            self.KeepBootloaderTimeoutCheckBox.Enable()
            self.KeepBootloaderTimeoutCheckBox.SetValue(1)
            self.DefaultOSChoice.Enable()
            self.InstallNewBootloaderCheckBox.SetValue(0)
            self.InstallNewBootloaderCheckBox.Disable()
            self.NewBootloaderChoice.Disable()
            self.RestoreBootloaderCheckBox.Disable()
            self.RestoreBootloaderChoice.Disable()

        elif self.UpdateBootloaderCheckBox.IsChecked():
            self.ReinstallBootloaderCheckBox.Disable()
            self.KeepBootloaderTimeoutCheckBox.Enable()
            self.KeepBootloaderTimeoutCheckBox.SetValue(1)
            self.DefaultOSChoice.Enable()
            self.InstallNewBootloaderCheckBox.SetValue(0)
            self.InstallNewBootloaderCheckBox.Disable()
            self.NewBootloaderChoice.Disable()
            self.RestoreBootloaderCheckBox.Disable()
            self.RestoreBootloaderChoice.Disable()

        else:
            self.ReinstallBootloaderCheckBox.Enable()
            self.UpdateBootloaderCheckBox.Enable()
            self.KeepBootloaderTimeoutCheckBox.SetValue(0)
            self.KeepBootloaderTimeoutCheckBox.Disable()
            self.BootloaderTimeoutSpinner.Disable()
            self.DefaultOSChoice.Disable()
            self.InstallNewBootloaderCheckBox.Enable()
            self.NewBootloaderChoice.Disable()
            self.RestoreBootloaderCheckBox.Enable()
            self.RestoreBootloaderChoice.Disable()

    def OnTimeoutCheckBox(self, Event=None):
        """Enable/Disable the bootloader timeout spinner, based on the value of the timeout checkbox."""
        if self.KeepBootloaderTimeoutCheckBox.IsChecked():
            self.BootloaderTimeoutSpinner.Disable()

        else:
            self.BootloaderTimeoutSpinner.Enable()

    def OnBackupBootloaderCheckBox(self, Event=None):
        """Enable/Disable the bootloader timeout spinner, based on the value of the timeout checkbox."""
        if self.BackupBootloaderCheckBox.IsChecked():
            self.BackupBootloaderChoice.Enable()

        else:
            self.BackupBootloaderChoice.Disable()

    def OnRestoreBootloaderCheckBox(self, Event=None):
        """Enable/Disable the bootloader timeout spinner, based on the value of the timeout checkbox."""
        if self.RestoreBootloaderCheckBox.IsChecked():
            self.RestoreBootloaderChoice.Enable()
            self.ReinstallBootloaderCheckBox.Disable()
            self.UpdateBootloaderCheckBox.Disable()
            self.InstallNewBootloaderCheckBox.Disable()
            self.NewBootloaderChoice.Disable()

        else:
            self.RestoreBootloaderChoice.Disable()
            self.ReinstallBootloaderCheckBox.Enable()
            self.UpdateBootloaderCheckBox.Enable()
            self.InstallNewBootloaderCheckBox.Enable()
            self.NewBootloaderChoice.Disable()

    def OnInstallNewBootloaderCheckBox(self, Event=None):
        """Enable/Disable the new bootloader choice box, based on the value of the new bootloader checkbox."""
        if self.InstallNewBootloaderCheckBox.IsChecked():
            self.NewBootloaderChoice.Enable()
            self.ReinstallBootloaderCheckBox.Disable()
            self.UpdateBootloaderCheckBox.Disable()
            self.KeepBootloaderTimeoutCheckBox.Enable()
            self.KeepBootloaderTimeoutCheckBox.SetValue(1)
            self.DefaultOSChoice.Enable()
            self.RestoreBootloaderCheckBox.Disable()
            self.RestoreBootloaderChoice.Disable()

        else:
            self.NewBootloaderChoice.Disable()
            self.ReinstallBootloaderCheckBox.Enable()
            self.UpdateBootloaderCheckBox.Enable()
            self.KeepBootloaderTimeoutCheckBox.SetValue(0)
            self.KeepBootloaderTimeoutCheckBox.Disable()
            self.BootloaderTimeoutSpinner.Disable()
            self.DefaultOSChoice.Disable()
            self.RestoreBootloaderCheckBox.Enable()
            self.RestoreBootloaderChoice.Disable()

    def OnOSInfo(self, Event=None):
        """Hide/Show the OS info, and rotate the arrow"""
        if self.ListCtrl.IsShown():
            self.Arrow1.SetBitmap(self.RightArrowImage)

            self.MainSizer.Detach(self.ListCtrl)
            self.MainSizer.Detach(self.SystemInfoButton)
            self.ListCtrl.Hide()
            self.SystemInfoButton.Hide()

        else:
            self.Arrow1.SetBitmap(self.DownArrowImage)

            self.MainSizer.Insert(4, self.ListCtrl, 5, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.MainSizer.Insert(5, self.SystemInfoButton, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.ListCtrl.Show()
            self.SystemInfoButton.Show()

        self.MainSizer.SetSizeHints(self)

    def OnBasicOptions(self, Event=None):
        """Hide/Show the basic options, and rotate the arrow"""
        if self.ReinstallBootloaderCheckBox.IsShown():
            if self.InstallNewBootloaderCheckBox.IsShown():
                return True

            self.Arrow2.SetBitmap(self.RightArrowImage)

            self.MainSizer.Detach(self.FixAndUpdateBootloaderSizer)
            self.MainSizer.Detach(self.TimeoutSizer)
            self.MainSizer.Detach(self.DefaultOSSizer)

            self.ReinstallBootloaderCheckBox.Hide()
            self.UpdateBootloaderCheckBox.Hide()
            self.KeepBootloaderTimeoutCheckBox.Hide()
            self.NewTimeoutText.Hide()
            self.BootloaderTimeoutSpinner.Hide()
            self.DefaultOSText.Hide()
            self.DefaultOSChoice.Hide()

        else:
            self.Arrow2.SetBitmap(self.DownArrowImage)

            if self.ListCtrl.IsShown():
                FirstNumber = 8

            else:
                FirstNumber = 6

            self.MainSizer.Insert(FirstNumber, self.FixAndUpdateBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.MainSizer.Insert(FirstNumber+1, self.TimeoutSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.MainSizer.Insert(FirstNumber+2, self.DefaultOSSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.ReinstallBootloaderCheckBox.Show()
            self.UpdateBootloaderCheckBox.Show()
            self.KeepBootloaderTimeoutCheckBox.Show()
            self.NewTimeoutText.Show()
            self.BootloaderTimeoutSpinner.Show()
            self.DefaultOSText.Show()
            self.DefaultOSChoice.Show()

        self.MainSizer.SetSizeHints(self)

    def OnAdvancedOptions(self, Event=None):
        """Show/Hide the advanced options, and rotate the arrow"""
        if self.InstallNewBootloaderCheckBox.IsShown():
            self.Arrow3.SetBitmap(self.RightArrowImage)

            self.MainSizer.Detach(self.InstallNewBootloaderSizer)
            self.MainSizer.Detach(self.BackupBootloaderSizer)
            self.MainSizer.Detach(self.RestoreBootloaderSizer)

            self.InstallNewBootloaderCheckBox.Hide()
            self.NewBootloaderText.Hide()
            self.NewBootloaderChoice.Hide()
            self.BackupBootloaderCheckBox.Hide()
            self.BackupBootloaderText.Hide()
            self.BackupBootloaderChoice.Hide()
            self.RestoreBootloaderCheckBox.Hide()
            self.RestoreBootloaderText.Hide()
            self.RestoreBootloaderChoice.Hide()

        else:
            if self.ReinstallBootloaderCheckBox.IsShown() == False:
                self.OnBasicOptions()

            self.Arrow3.SetBitmap(self.DownArrowImage)

            if self.ListCtrl.IsShown():
                FirstNumber = 13

            else:
                FirstNumber = 11

            self.MainSizer.Insert(FirstNumber, self.InstallNewBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.MainSizer.Insert(FirstNumber+1, self.BackupBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.MainSizer.Insert(FirstNumber+2, self.RestoreBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.InstallNewBootloaderCheckBox.Show()
            self.NewBootloaderText.Show()
            self.NewBootloaderChoice.Show()
            self.BackupBootloaderCheckBox.Show()
            self.BackupBootloaderText.Show()
            self.BackupBootloaderChoice.Show()
            self.RestoreBootloaderCheckBox.Show()
            self.RestoreBootloaderText.Show()
            self.RestoreBootloaderChoice.Show()

        self.MainSizer.SetSizeHints(self)

    def SaveSettings(self, Event=None, OS=None): #*** Save settings and state if the OS choice is changed ***
        """Save all settings for this OS from the checkboxes and choice boxes"""
        BootloaderInfo[OS]["Settings"]["Reinstall"] = self.ReinstallBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["Update"] = self.UpdateBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["KeepExistingTimeout"] = self.KeepBootloaderTimeoutCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["NewTimeout"] = self.BootloaderTimeoutSpinner.GetValue()
        BootloaderInfo[OS]["Settings"]["DefaultOS"] = self.DefaultOSChoice.GetStringSelection()
        BootloaderInfo[OS]["Settings"]["InstallNewBootloader"] = self.InstallNewBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["NewBootloader"] = self.NewBootloaderChoice.GetStringSelection()
        BootloaderInfo[OS]["Settings"]["BackupBootloader"] = self.BackupBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["BootloaderBackupTarget"] = self.BackupBootloaderChoice.GetStringSelection()
        BootloaderInfo[OS]["Settings"]["RestoreBootloader"] = self.RestoreBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["BootloaderRestoreSource"] = self.RestoreBootloaderChoice.GetStringSelection()

        if BootloaderInfo[OS]["Settings"]["Reinstall"] or BootloaderInfo[OS]["Settings"]["Update"] or BootloaderInfo[OS]["Settings"]["InstallNewBootloader"] or BootloaderInfo[OS]["Settings"]["RestoreBootloader"]:
            BootloaderInfo[OS]["Settings"]["ChangeThisOS"] = True

        else:
            BootloaderInfo[OS]["Settings"]["ChangeThisOS"] = False

    def SaveGUIState(self, Event=None, OS=None):
        """Save all the GUI element's states (enabled/disabled) for this OS"""
        BootloaderInfo[OS]["GUIState"]["ReinstallCheckBoxState"] = self.ReinstallBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["UpdateCheckBoxState"] = self.UpdateBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["KeepExistingTimeoutCheckBoxState"] = self.KeepBootloaderTimeoutCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["NewTimeoutSpinnerState"] = self.BootloaderTimeoutSpinner.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["DefaultOSChoiceState"] = self.DefaultOSChoice.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["InstallNewBootloaderCheckBoxState"] = self.InstallNewBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["NewBootloaderChoiceState"] = self.NewBootloaderChoice.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["BackupBootloaderCheckBoxState"] = self.BackupBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["BackupBootloaderChoiceState"] = self.BackupBootloaderChoice.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["RestoreBootloaderCheckBoxState"] = self.RestoreBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["RestoreBootloaderChoiceState"] = self.RestoreBootloaderChoice.IsEnabled()

    def OnClose(self, Event=None):
        """Save settings and GUI state, and then close NewBootloaderOptionsWindow"""
        self.SaveSettings(OS=self.OSChoice.GetStringSelection())
        self.SaveGUIState(OS=self.OSChoice.GetStringSelection())

        #Send a message to mainwindow so it can refresh.
        wx.CallAfter(self.ParentWindow.RefreshMainWindow, "Closed")

        self.Destroy()

#End New Bootloader Options Window.
#Begin Restore Window *** This uses the flawed concept of RootDevice, will need to change later *** *** This is buggy, but fix it later *** *** Will be removed upon integration of the new bootloader options window ***
class RestoreWindow(wx.Frame):
    def __init__(self, ParentWindow):
        """Initialise RestoreWindow"""
        logger.debug("RestoreWindow().__init__(): Restore BootSector Window Started.")
        title = "WxFixBoot - Restore the BootSector"

        wx.Frame.__init__(self, parent=wx.GetApp().TopWindow, title=title, size=(400,200), style=wx.DEFAULT_FRAME_STYLE)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(400,200))
        self.ParentWindow = ParentWindow
        wx.Frame.SetIcon(self, AppIcon)

        self.CreateText()
        self.CreateRadios()
        self.CreateChoiceBs()
        self.CreateButtons()
        self.SetupSizers()
        self.BindEvents()

        #Set up the window.
        self.SetupOptions()

        logger.debug("RestoreWindow().__init__(): Ready. Waiting for events...")

    def CreateText(self):
        """Create the text"""
        WelcomeText1Text = "What type of Boot Sector backup do you have?"
        WelcomeText2Text = "Easily restore your bootsector here!"

        self.WelcomeText1 = wx.StaticText(self.Panel, -1, WelcomeText1Text)
        self.WelcomeText2 = wx.StaticText(self.Panel, -1, WelcomeText2Text)

        self.BackupFileText = wx.StaticText(self.Panel, -1, "Backup file:")
        self.TargetDeviceText = wx.StaticText(self.Panel, -1, "Target Device:")

    def CreateRadios(self):
        """Create Radio Buttons"""
        self.AutoDetectTypeRadio = wx.RadioButton(self.Panel, -1, "Autodetect", style=wx.RB_GROUP)
        self.MBRBackupTypeRadio = wx.RadioButton(self.Panel, -1, "MBR")
        self.GPTBackupTypeRadio = wx.RadioButton(self.Panel, -1, "GPT")  

    def CreateChoiceBs(self):
        """Create Choice Boxes"""
        self.BackupFileChoice = wx.Choice(self.Panel, -1, size=(150,30), choices=['-- Please Select --', 'Specify File Path...'])
        self.TargetDeviceChoice = wx.Choice(self.Panel, -1, size=(150,30), choices=['-- Please Select --', 'Auto: '+SystemInfo["AutoRootDevice"]]+SystemInfo["Devices"]+['Specify Path...'])

    def CreateButtons(self):
        """Create Buttons"""
        self.ExitButton = wx.Button(self.Panel, -1, "Close and Save Options")

    def SetupSizers(self):
        """Setup Sizers for Restore Window"""
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        RadioButtonSizer = wx.BoxSizer(wx.HORIZONTAL)

        BackupFileTextSizer = wx.BoxSizer(wx.HORIZONTAL)

        BackupFileChoiceSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the radio button sizer.
        RadioButtonSizer.Add(self.AutoDetectTypeRadio, 1, wx.RIGHT|wx.LEFT, 10)
        RadioButtonSizer.Add(self.MBRBackupTypeRadio, 1, wx.RIGHT|wx.LEFT, 10)
        RadioButtonSizer.Add(self.GPTBackupTypeRadio, 1, wx.RIGHT|wx.LEFT, 10)

        #Add items to the backup file text sizer.
        BackupFileTextSizer.Add(self.BackupFileText, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 10)
        BackupFileTextSizer.Add(self.TargetDeviceText, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 10)

        #Add items to the backup file choice sizer.
        BackupFileChoiceSizer.Add(self.BackupFileChoice, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 10)
        BackupFileChoiceSizer.Add(self.TargetDeviceChoice, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 10)

        #Add items to the main sizer.
        MainSizer.Add(self.WelcomeText1, 0, wx.ALL|wx.ALIGN_CENTER, 10)
        MainSizer.Add(self.WelcomeText2, 0, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER, 10)
        MainSizer.Add(RadioButtonSizer, 1, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 10)
        MainSizer.Add(BackupFileTextSizer, 1, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 10)
        MainSizer.Add(BackupFileChoiceSizer, 1, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 10)
        MainSizer.Add(self.ExitButton, 1, wx.RIGHT|wx.LEFT|wx.BOTTOM|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.Panel.SetSizer(MainSizer)
        MainSizer.SetMinSize(wx.Size(400,200))
        MainSizer.SetSizeHints(self)

    def BindEvents(self):
        """Bind events"""
        self.Bind(wx.EVT_BUTTON, self.ExitWindow, self.ExitButton)
        self.Bind(wx.EVT_CLOSE, self.ExitWindow)
        self.Bind(wx.EVT_CHOICE, self.SelectFile, self.BackupFileChoice)
        self.Bind(wx.EVT_CHOICE, self.SelectTargetDevice, self.TargetDeviceChoice)

    def SetupOptions(self):
        """Set up the choiceboxes according to the values of the variables."""
        File = BootSectorFile
        TargetDevice = BootSectorTargetDevice

        #Image file choice.
        if File != "None":
            self.BackupFileChoice.Append(File)
            self.BackupFileChoice.SetStringSelection(File)

        else:
            self.BackupFileChoice.SetSelection(0)

        #Target device file choice.
        if TargetDevice != "None":
            self.TargetDeviceChoice.Append(TargetDevice)
            self.TargetDeviceChoice.SetStringSelection(TargetDevice)

        else:
            self.TargetDeviceChoice.SetSelection(0)

    def SelectFile(self, Event=None):
        """Grab Image path"""
        logger.debug("RestoreWindow().SelectFile(): File selection choice box changed...")

        #Set up global variables.
        global BootSectorFile
        global RestoreBootSector
        global BootSectorBackupType

        File = self.BackupFileChoice.GetStringSelection()

        #Determine what to do here.
        if File == "-- Please Select --":
            File = "None"
            Restore = False

        elif File == "Specify File Path...":
            Dlg = wx.FileDialog(self.Panel, "Select BootSector File...", defaultDir="/home", wildcard="All Files/Devices (*)|*|GPT Backup File (*.gpt)|*.gpt|MBR Backup File (*.mbr)|*.mbr|IMG Image file (*.img)|*.img", style=wx.OPEN)

            if Dlg.ShowModal() == wx.ID_OK:
                Restore = True
                File = Dlg.GetPath()
                self.BackupFileChoice.Append(File)
                self.BackupFileChoice.SetStringSelection(File)

            else:
                File = "None"
                Restore = False
                self.BackupFileChoice.SetStringSelection("-- Please Select --")

            Dlg.Destroy()

        else:
            File = self.BackupFileChoice.GetStringSelection()
            Restore = True

        #Detect backup type, if files are selected.
        if File != "None" and Restore:
            #Use os.stat(filename).st_size, if bigger than 512 bytes (MBR bootsector), it's GPT
            Temp = os.stat(File).st_size
            if Temp < 512:
                #Bad file.
                dlg = wx.MessageDialog(self.Panel, "The size of the selected file is less than 512 bytes! This isn't a valid backup file. Please select a new backup file.", "WxFixBoot - Error", style=wx.OK | wx.ICON_ERROR, pos=wx.DefaultPosition)
                dlg.ShowModal()
                dlg.Destroy()
                File = "None"
                Restore = "False"
                BackupType = "None"
                self.AutoDetectTypeRadio.SetValue(True)
                Temp = self.BackupFileChoice.GetSelection()
                self.BackupFileChoice.Delete(Temp)
                self.BackupFileChoice.SetStringSelection("-- Please Select --")
                return

            elif Temp == 512:
                #Backup is MBR(msdos)
                BackupType = "mbr"
                self.MBRBackupTypeRadio.SetValue(True)

            elif Temp >= 16384 and Temp < 20000: #*** Find the max size of a GPT ***
                #Backup is GPT  
                BackupType = "gpt"
                self.GPTBackupTypeRadio.SetValue(True)

            else:
                #Backup is *PROBABLY* GPT, but might not be a backup file! If this is the BootSector, it's fine, because for that we backup the UEFI partition.
                BackupType = "gpt"
                self.GPTBackupTypeRadio.SetValue(True)

            dlg = wx.MessageDialog(self.Panel, "Your backup file type was detected as: "+BackupType+". If this is correct, then continuing is safe. If not, ensure you made the backup file with WxFixBoot and that it is the correct backup file, and manually set the right backup type. If you made the backup with another program, please use that program to restore it instead to avoid problems.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

        else:
            BackupType = "None"
            self.AutoDetectTypeRadio.SetValue(True)

        #Save File, Restoring, and BackupType to the correct global variables, depending on which purpose this class is serving (Boot Sector Restoration Window).
        logger.info("RestoreWindow().SelectFile(): Current config: File = "+File+", Restore = "+unicode(Restore)+", BackupType = "+BackupType+"...")

        BootSectorFile = File
        RestoreBootSector = Restore
        BootSectorBackupType = BackupType

    def SelectTargetDevice(self, Event=None):
        """Grab Boot Sector Image path."""
        logger.debug("RestoreWindow().SelectTargetDevice(): Target device selection choice box has changed...")

        #Set up global variables.
        global BootSectorTargetDevice

        TargetDevice = self.TargetDeviceChoice.GetStringSelection()

        #Determine what to do here.
        if TargetDevice == "-- Please Select --":
            TargetDevice = "None"

        elif TargetDevice[0:4] == "Auto":
            TargetDevice = SystemInfo["RootDevice"]

        elif TargetDevice == "Specify File Path...":
            Dlg = wx.FileDialog(self.Panel, "Select Target Device...", wildcard="All Files/Devices (*)|*", defaultDir='/dev', style=wx.OPEN)
            if Dlg.ShowModal() == wx.ID_OK:
                TargetDevice = Dlg.GetPath()
                self.TargetDeviceChoice.Append(TargetDevice)
                self.TargetDeviceChoice.SetStringSelection(TargetDevice)

            else:
                TargetDevice = "None"
                self.TargetDeviceChoice.SetStringSelection("-- Please Select --")

        else:
            TargetDevice = self.TargetDeviceChoice.GetStringSelection()

        #Save TargetDevice to the correct global variable, depending on which purpose this class is serving (Boot Sector Restoration Window).
        logger.info("RestoreWindow().SelectTargetDevice(): Current config: TargetDevice = "+TargetDevice+"...")

        BootSectorTargetDevice = TargetDevice

    def ExitWindow(self, Event=None):
        """Exits Restore Window, or shows a warning to the user if needed"""
        File = BootSectorFile
        Restore = RestoreBootSector
        TargetDevice = BootSectorTargetDevice

        if File != "None" and Restore and TargetDevice != "None":
            #Show an info message.
            dlg = wx.MessageDialog(self.Panel, "Do you want to continue? This operation can cause data loss. Only continue if you are certain you've selected the right target device and backup file, and if the backup was created with WxFixBoot. If you restore a bootsector, some options, such as installing a different bootloader and reinstalling or updating your bootloader, will be disabled. If you want to change other settings, you can always restart WxFixBoot afterwards and then change them.", "WxFixBoot - Information", style=wx.YES_NO | wx.ICON_EXCLAMATION, pos=wx.DefaultPosition)

            if dlg.ShowModal() == wx.ID_YES:
                #Send a message to OptionsDlg1, so it can show itself again.
                logger.debug("RestoreWindow().ExitWindow(): Restore BootSector Window Closing...")
                wx.CallAfter(self.ParentWindow.RefreshOptionsDlg1, "Closed.")

                #Exit.
                dlg.Destroy()
                self.Destroy()

            dlg.Destroy()

        elif File != "None" or Restore or TargetDevice != "None":
            dlg = wx.MessageDialog(self.Panel, "You haven't entered all of the required settings! Please either enter all required settings to do this operation, or no settings at all to disable resoration.", "WxFixBoot - Warning", style=wx.OK | wx.ICON_WARNING, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

        else:
            logger.debug("RestoreWindow().ExitWindow(): Restore BootSector Window Closing...")
            #Send a message to OptionsDlg1, so it can show itself again.
            wx.CallAfter(self.ParentWindow.RefreshOptionsDlg1, "Closed.")

            #Exit.
            self.Destroy()

#End Restore Window
#Begin Progress Window
class ProgressWindow(wx.Frame):
    def __init__(self):
        """Initialse Progress Window"""
        wx.Frame.__init__(self, parent=None, title="WxFixBoot - Operations Progress", size=(500,300), style=wx.CAPTION|wx.MINIMIZE|wx.RESIZE_BORDER)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(500,300))
        wx.Frame.SetIcon(self, AppIcon)
        Tools.coretools.ParentWindow = self

        self.CreateText()
        self.CreateButtons()
        self.CreateProgressBars()

        #Create the output box.
        self.OutputBox = wx.TextCtrl(self.Panel, -1, "", size=(480,240), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP)
        self.OutputBox.SetBackgroundColour((0,0,0))
        self.OutputBox.SetDefaultStyle(wx.TextAttr(wx.WHITE))

        self.SetupSizers()
        self.BindEvents()

        logger.debug("ProgressWindow().__init__(): Progress Window Started.")
        logger.debug("ProgressWindow().__init__(): Starting Backend Thread...")

        BackendThread(self)

    def CreateText(self):
        """Create the Text"""
        self.PerformingOperationsText = wx.StaticText(self.Panel, -1, "WxFixBoot is performing operations... Please wait.")
        self.CurrentOperationHeadingText = wx.StaticText(self.Panel, -1, "Current Operation:")
        self.CurrentOperationText = wx.StaticText(self.Panel, -1, "Initializating...")
        self.CurrentOperationProgressText = wx.StaticText(self.Panel, -1, "Current Operation Progress:")
        self.OverallProgressText = wx.StaticText(self.Panel, -1, "Overall Progress:")

    def CreateButtons(self):
        """Create buttons."""
        self.ShowOutputButton = wx.ToggleButton(self.Panel, -1, "Show Terminal Output")
        self.RestartButton = wx.Button(self.Panel, -1, "Restart WxFixBoot")
        self.ExitButton = wx.Button(self.Panel, -1, "Exit")
        self.RestartButton.Disable()
        self.ExitButton.Disable()

    def CreateProgressBars(self):
        """Create both progres bars"""
        #Create the progress bar for the current operation.
        self.CurrentOperationProgressBar = wx.Gauge(self.Panel, -1, 100)
        self.CurrentOperationProgressBar.SetBezelFace(3)
        self.CurrentOperationProgressBar.SetShadowWidth(3)
        self.CurrentOperationProgressBar.SetValue(0)
        self.CurrentOperationProgressBar.Show()

        #Create the progress bar for overall progress.
        self.OverallProgressBar = wx.Gauge(self.Panel, -1, 100)
        self.OverallProgressBar.SetBezelFace(3)
        self.OverallProgressBar.SetShadowWidth(3)
        self.OverallProgressBar.SetValue(0)
        self.OverallProgressBar.Show()

    def SetupSizers(self):
        """Setup sizers for Progress Window"""
        #Create the Main Sizer.
        self.MainSizer = wx.BoxSizer(wx.VERTICAL)

        #Create the first button sizer.
        ButtonSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        #Create the second button sizer.
        ButtonSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the first button sizer.
        ButtonSizer1.Add(self.RestartButton, 1, wx.RIGHT, 5)
        ButtonSizer1.Add((5,5), 1, wx.LEFT|wx.RIGHT, 5)
        ButtonSizer1.Add(self.ShowOutputButton, 1, wx.LEFT|wx.RIGHT, 5)

        #Add items to the second button sizer.
        ButtonSizer2.Add((5,5), 1, wx.RIGHT, 5)
        ButtonSizer2.Add(self.ExitButton, 1, wx.LEFT|wx.RIGHT, 5)
        ButtonSizer2.Add((5,5), 1, wx.LEFT|wx.RIGHT, 5)

        #Add items to the main sizer.
        self.MainSizer.Add(self.PerformingOperationsText, 0, wx.ALL|wx.ALIGN_CENTER, 10)
        self.MainSizer.Add(self.CurrentOperationHeadingText, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 10)
        self.MainSizer.Add(self.CurrentOperationText, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 10)
        self.MainSizer.Add(self.CurrentOperationProgressText, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 10)
        self.MainSizer.Add(self.CurrentOperationProgressBar, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.OverallProgressText, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 10)
        self.MainSizer.Add(self.OverallProgressBar, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(ButtonSizer1, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(self.OutputBox, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.MainSizer.Add(ButtonSizer2, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        self.ShowOutput()

        #Get the sizer set up for the frame.
        self.Panel.SetSizer(self.MainSizer)
        self.MainSizer.SetMinSize(wx.Size(500,300))
        self.MainSizer.SetSizeHints(self)

    def BindEvents(self):
        """Bind events for Progress Window"""
        self.Bind(wx.EVT_TOGGLEBUTTON, self.ShowOutput, self.ShowOutputButton)
        self.Bind(wx.EVT_BUTTON, self.RestartWxFixBoot, self.RestartButton)
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.ExitButton)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def ShowOutput(self, Event=None):
        """Show and Hide the output box in ProgressWindow()"""
        logger.debug("ProgressWindow().ShowOutput() was Toggled to position: "+unicode(self.ShowOutputButton.GetValue())+", where True = Depressed and vice versa.")
        if self.ShowOutputButton.GetValue():
            #Remove the empty space.
            self.MainSizer.Detach(8)

            #Show the output box.
            self.MainSizer.Insert(8, self.OutputBox, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.OutputBox.Show()

        else:
            #Hide the output box.
            self.MainSizer.Detach(self.OutputBox)
            self.OutputBox.Hide()

            #Insert some empty space.
            self.MainSizer.Insert(8, (1,1), 1, wx.EXPAND)

        #Call Layout() on self.Panel() to ensure it displays properly.
        self.Panel.Layout()
        self.MainSizer.SetSizeHints(self)

    def CarriageReturn(self):
        """Handles carriage returns in output"""
        #Go back until the last newline character, and overwrite anything in the way on the next write.
        #Get the current insertion point.
        CurrentInsertionPoint = self.OutputBox.GetInsertionPoint()

        #Get the text up to the current insertion point.
        Text = self.OutputBox.GetRange(0, CurrentInsertionPoint)

        #Find the last newline char in the text.
        NewlineNos = []
        Counter = 0
        for Char in Text:
            if Char == "\n":
                NewlineNos.append(Counter)

            Counter += 1

        if NewlineNos != []:
            LastNewline = NewlineNos[-1]

        else:
            #Hacky bit to make the new insertion point 0 :)
            LastNewline = -1

        #Set the insertion point to just after that newline, unless we're already there, and in that case set the insertion point just after the previous newline.
        NewInsertionPoint = LastNewline + 1

        self.OutputBox.SetInsertionPoint(NewInsertionPoint)

    def UpdateOutputBox(self, Line):
        """Update the output box"""
        CRs = []
        CharNo = 0

        for Char in Line:
            CharNo += 1

            if Char == "\r":
                CRs.append(CharNo)

        CharNo = 0
        TempLine = ""
        for Char in Line:
            CharNo += 1

            if CharNo not in CRs:
                TempLine += Char
                if Char == "\n":
                    self.AddLineToOutputBox(TempLine, CRs, CharNo)
                    TempLine = ""

            else:
                self.AddLineToOutputBox(TempLine, CRs, CharNo)
                TempLine = ""

    def AddLineToOutputBox(self, Line, CRs, CharNo):
        InsertionPoint = self.OutputBox.GetInsertionPoint()
        self.OutputBox.Replace(InsertionPoint, InsertionPoint+len(Line), Line)

        if CharNo in CRs:
            self.CarriageReturn()

    def UpdateCurrentProgress(self,msg):
        """Update the progress of the current progress progress bar"""
        #Called at various points during operation code.
        self.CurrentOperationProgressBar.SetValue(int(msg))
        if self.CurrentOperationProgressBar.GetValue() == 100:
            self.UpdateTotalProgress()
            #Stop this resetting when all operations are complete.
            if self.OverallProgressBar.GetValue() != 100:
                self.CurrentOperationProgressBar.SetValue(0)

    def UpdateTotalProgress(self):
        """Update the progress of the overall progress progress bar"""
        #This is called when self.CurrentOperationProgressBar reaches 100 (aka full).
        if self.OverallProgressBar.GetValue() < 100:
            self.OverallProgressBar.SetValue(self.OverallProgressBar.GetValue()+(100//NumberOfOperations))

    def UpdateCurrentOpText(self, Message):
        """Keep the current operations status text up to date."""
        self.CurrentOperationText.SetLabel(Message)
        self.Panel.Layout()

    def BackendThreadFinished(self):
        """Called when the BackendThread is finished, enables self.RestartButton and self.ExitButton"""
        self.RestartButton.Enable()
        self.ExitButton.Enable()

    def RestartWxFixBoot(self, Event=None):
        """Restart WxFixBoot"""
        logger.debug("ProgressWindow().RestartWxFixBoot(): Restarting WxFixBoot...")
        self.Hide()

        #Reset all settings to defaults, except ones like LiveDisk, which won't ever need to change.
        MainStartupTools.SetDefaults()

        global PartScheme

        SystemInfo["Bootloader"] = SystemInfo["AutoBootloader"]
        Settings["MainSettings"]["FirmwareType"] = SystemInfo["DetectedFirmwareType"]
        SystemInfo["RootDevice"] = SystemInfo["AutoRootDevice"]

        #Show MainWindow
        MainFrame = MainWindow()
        app.SetTopWindow(MainFrame)
        MainFrame.Show(True)

        #Destroy Progress Window.
        logger.debug("ProgressWindow().RestartWxFixBoot(): WxFixBoot has been reset and restarted, returning to MainWindow()")
        self.Destroy()

    def OnExit(self, Event=None):
        """Exits the programs, and sorts out log file saving/deleting stuff"""
        dlg = wx.MessageDialog(self.Panel, 'Are you sure you want to exit?', 'WxFixBoot - Question!', wx.YES_NO | wx.ICON_QUESTION)
        Answer = dlg.ShowModal()
        dlg.Destroy()

        if Answer == wx.ID_YES:
            #Run the exit sequence
            logger.info("MainWindow().OnExit(): Exiting...")

            #Shutdown the logger.
            logging.shutdown()

            #Prompt user to save the log file.
            dlg = wx.MessageDialog(self.Panel, "Do you want to keep WxFixBoot's log file? For privacy reasons, WxFixBoot will delete its log file when closing. If you want to save it, which is helpful for debugging if something went wrong, click yes, and otherwise click no.", "WxFixBoot - Question", style=wx.YES_NO | wx.ICON_QUESTION, pos=wx.DefaultPosition)
            Answer = dlg.ShowModal()
            dlg.Destroy()

            if Answer == wx.ID_YES:
                #Ask the user where to save it.
                dlg = wx.FileDialog(self.Panel, "Save log file to...", defaultDir="/home", wildcard="Log Files (*.log)|*.log" , style=wx.SAVE|wx.OVERWRITE_PROMPT)
                Answer = dlg.ShowModal()
                File = dlg.GetPath()
                dlg.Destroy()

                if Answer == wx.ID_OK:
                    #Copy it to the specified path, using a one-liner, and don't bother handling any errors, because this is run as root.
                    CoreTools.StartProcess("cp /tmp/wxfixboot.log "+File)

                    dlg = wx.MessageDialog(self.Panel, 'Done! WxFixBoot will now exit.', 'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()

                else:
                    dlg = wx.MessageDialog(self.Panel, 'Okay, WxFixBoot will now exit without saving the log file.', 'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()

            else:
                dlg = wx.MessageDialog(self.Panel, 'Okay, WxFixBoot will now exit without saving the log file.', 'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

            #Delete the log file, and don't bother handling any errors, because this is run as root.
            os.remove('/tmp/wxfixboot.log')

            self.Destroy()

#End Progress Window
#Begin Backend Thread
class BackendThread(threading.Thread):
    def __init__(self, ParentWindow):
        """Initialize BackendThread"""
        #Set up the backend tools.
        Tools.dialogtools.ParentWindow = ParentWindow
        Tools.BackendTools.helpers.ParentWindow = ParentWindow
        Tools.BackendTools.essentials.ParentWindow = ParentWindow
        Tools.BackendTools.main.ParentWindow = ParentWindow
        Tools.BackendTools.BootloaderTools.main.ParentWindow = ParentWindow

        #Start the main part of this thread.
        threading.Thread.__init__(self)
        self.ParentWindow = ParentWindow
        self.start()

    def run(self):
        """Do setup, and call self.StartOperations()"""
        #Log the BackendThread start event (in debug mode).
        logger.debug("BackendThread().run(): Started. Calling self.StartOperations()...")

        self.StartOperations()

    def StartOperations(self):
        """Start doing operations."""
        logger.debug("BackendThread().StartOperations(): Running operations...")

        DialogTools.ShowMsgDlg(Kind="info", Message="Please stay within sight of the system, as operations are not fully automated and you may be asked the occasional queston, or be shown warnings. You may see the occasional file manager dialog pop up as well, so feel free to either close them or ignore them.")

        #Make dictionaries accessible. *** Add as needed *** *** Minimise these later if possible ***
        Tools.BackendTools.essentials.DiskInfo = DiskInfo
        Tools.BackendTools.essentials.SystemInfo = SystemInfo

        Tools.BackendTools.helpers.BootloaderInfo = BootloaderInfo
        Tools.BackendTools.helpers.DiskInfo = DiskInfo
        Tools.BackendTools.helpers.OSInfo = OSInfo
        Tools.BackendTools.helpers.SystemInfo = SystemInfo

        Tools.BackendTools.main.OSInfo = OSInfo
        Tools.BackendTools.main.SystemInfo = SystemInfo
        Tools.BackendTools.main.BootloaderInfo = BootloaderInfo

        Tools.BackendTools.BootloaderTools.main.BootloaderInfo = BootloaderInfo
        Tools.BackendTools.BootloaderTools.main.SystemInfo = SystemInfo
        Tools.BackendTools.BootloaderTools.main.OSInfo = OSInfo

        Tools.BackendTools.BootloaderTools.setconfigtools.BootloaderInfo = BootloaderInfo
        Tools.BackendTools.BootloaderTools.setconfigtools.DiskInfo = DiskInfo
        Tools.BackendTools.BootloaderTools.setconfigtools.SystemInfo = SystemInfo
        Tools.BackendTools.BootloaderTools.setconfigtools.OSInfo = OSInfo

        #*** Temporarily set some variables to make stuff work for now ***
        global BootloaderTimeout
        global KernelOptions

        BootloaderTimeout = 10
        KernelOptions = "quiet splash nomodeset"

        #Run functions to do operations. *** Some of these might not work correctly until switch to dictionaries even with the extra abstraction code after running the function ***
        for function in Operations:
            #*** Extra temporary stuff needed to make things work for the time being until we switch to dictionaries (Set vars inside modules) ***
            #*** We temporarily need global declarations in modules to make sure the global variables are set right, when they aren't directly passed to the functions within ***
            #*** Essential backend tools ***
            Tools.BackendTools.essentials.BootSectorFile = BootSectorFile
            Tools.BackendTools.essentials.BootSectorBackupType = BootSectorBackupType
            Tools.BackendTools.essentials.BootSectorTargetDevice = BootSectorTargetDevice

            #*** Main Backend Tools ***
            Tools.BackendTools.main.BootloaderTimeout = BootloaderTimeout
            Tools.BackendTools.main.KernelOptions = KernelOptions

            #*** Bootloader Configuration Setting Tools (in Backend Tools package) ***
            Tools.BackendTools.BootloaderTools.setconfigtools.BootloaderTimeout = BootloaderTimeout

            try:
                Tools.BackendTools.BootloaderTools.setconfigtools.KernelOptions = KernelOptions

            except NameError: pass

            #Run the function.
            if type(function) != type([]):
                function()

            else:
                function[0](function[1])

        logger.info("BackendThread().StartOperations(): Finished Operation Running Code.")

        wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Finished!")

        DialogTools.ShowMsgDlg(Kind="info", Message="Your operations are all done! Thank you for using WxFixBoot. If you performed any bootloader operations, please now reboot your system.") #*** Check this and customise message if needed ***

        wx.CallAfter(self.ParentWindow.BackendThreadFinished)

    def GenerateSystemReport(self): #*** Leave this here until switch to dictionaries cos otherwise this'll be a mighty pain in the backside! :) *** *** Use dictionaries here ***
        """Create a system report, containing various information helpful for debugging and fixing problems. It's pretty much like a bootinfo summary."""
        DialogTools.ShowMsgDlg(Kind="info", Message="WxFixBoot will now create your system report. Click okay to continue.")

        #Ask the user where to save the file.
        ReportFile = DialogTools.ShowSaveFileDlg(Title="WxFixBoot - Select System Report File", Wildcard="Text Files|*.txt|Log Files|*.log|All Files/Devices (*)|*")

        #Write everything directly to the file.
        ReportList = open(ReportFile, 'w')
        ReportList.write("This system report was created with WxFixBoot version "+Version+". It can be used like a bootinfo summary.\n\n")

        #Do OS Information.
        ReportList.write("\n##########OS Information##########\n")
        ReportList.write("Detected Operating Systems: "+', '.join(OSList)+"\n")
        ReportList.write("Currently running OS is on Live Disk: "+unicode(SystemInfo["IsLiveDisk"])+"\n")

        #Do Firmware Information.
        ReportList.write("\n##########Firmware Information##########\n")
        ReportList.write("Detected firmware type: "+SystemInfo["DetectedFirmwareType"]+"\n")
        ReportList.write("Selected Firmware Type: "+Settings["MainSettings"]["FirmwareType"]+"\n")
        ReportList.write("UEFI System Partition (UEFI Bootloader target): "+SystemInfo["UEFISystemPartition"]+"\n")

        #Do Bootloader information
        ReportList.write("\n##########BootLoader Information##########\n")
        ReportList.write("Detected Bootloader: "+SystemInfo["AutoBootloader"]+"\n")
        ReportList.write("Selected Bootloader: "+SystemInfo["Bootloader"]+"\n")

        if True: #*** Needs rewriting for new bootloader options ***
            #Display specific information depending on the operation to be done (if we're update/reinstalling bootloaders, don't make it look like we're doing something else). *** Show what we would do if they weren't disabled too ***
            ReportList.write("Disabled Bootloader Operations: "+unicode(SystemInfo["DisableBootloaderOperations"])+"\n")

            if SystemInfo["DisableBootloaderOperations"] == False:
                if ReinstallBootloader:
                    ReportList.write("Reinstall/Fix The Current BootLoader: "+unicode(ReinstallBootloader)+"\n")
                    #ReportList.write("Selected Bootloader To Reinstall/Fix: "+SystemInfo["BootloaderToInstall"]+"\n")
                    ReportList.write("Reinstall/Fix bootloader in: "+', '.join(SystemInfo["OSsForBootloaderInstallation"])+"\n")
                    ReportList.write("\nBootloader's New Configuration:"+"\n")
                    ReportList.write("\tDefault OS: "+SystemInfo["DefaultOS"]+"\n")
                    ReportList.write("\tTimeout: "+unicode(BootloaderTimeout)+" seconds"+"\n")
                    ReportList.write("\tGlobal Kernel Options: "+KernelOptions+"\n")

                elif UpdateBootloader:
                    ReportList.write("Update The Current BootLoader's Config: "+unicode(UpdateBootloader)+"\n")
                    #ReportList.write("Selected Bootloader To Update: "+SystemInfo["BootloaderToInstall"]+"\n")
                    ReportList.write("Update Bootloader in: "+', '.join(SystemInfo["OSsForBootloaderInstallation"])+"\n")
                    ReportList.write("\nBootloader's New Configuration:"+"\n")
                    ReportList.write("\tDefault OS: "+SystemInfo["DefaultOS"]+"\n")
                    ReportList.write("\tTimeout: "+unicode(BootloaderTimeout)+" seconds"+"\n")
                    ReportList.write("\tGlobal Kernel Options: "+KernelOptions+"\n")

                else:
                    #We must be installing a new bootloader.
                    #ReportList.write("Selected Bootloader To Install: "+SystemInfo["BootloaderToInstall"]+"\n")
                    ReportList.write("Remove Old Bootloader from: "+', '.join(SystemInfo["OSsForBootloaderRemoval"])+"\n")
                    ReportList.write("Install New Bootloader to: "+', '.join(SystemInfo["OSsForBootloaderInstallation"])+"\n")
                    ReportList.write("\nNew Bootloader's Configuration:"+"\n")
                    ReportList.write("\tDefault OS: "+SystemInfo["DefaultOS"]+"\n")
                    ReportList.write("\tTimeout: "+unicode(BootloaderTimeout)+" seconds"+"\n")
                    ReportList.write("\tGlobal Kernel Options: "+KernelOptions+"\n")

        #Do Disk Information
        ReportList.write("\n##########Disk Information##########\n")
        ReportList.write("Detected Linux Partitions: "+', '.join(SystemInfo["LinuxPartitions"])+"\n")
        ReportList.write("Delected Root Filesystem (MBR bootloader target): "+SystemInfo["RootFS"]+"\n")
        ReportList.write("Detected Root Device (MBR Bootloader Target): "+SystemInfo["AutoRootDevice"]+"\n")
        ReportList.write("Selected Root Device (MBR Bootloader Target): "+SystemInfo["RootDevice"]+"\n")

        #Do Boot Sector Information.
        ReportList.write("\n##########Boot Sector Information##########\n")
        ReportList.write("Backup Boot Sector: "+unicode(BackupBootSector)+"\n")
        if BackupBootSector:
            ReportList.write("\n\tBacked up Boot Sector From: "+SystemInfo["RootDevice"]+"\n")
            ReportList.write("\tTarget Boot Sector File: (*** Disabled as no way of saving this until switch to dictionaries ***)\n\n") #*** +BootSectorBackupFile+"\n\n")

        ReportList.write("Restore Boot Sector: "+unicode(RestoreBootSector)+"\n")
        if RestoreBootSector:
            ReportList.write("\n\tBoot Sector Backup File: "+BootSectorFile+"\n")
            ReportList.write("\tBoot Sector Target Device: "+BootSectorTargetDevice+"\n")
            ReportList.write("\tBoot Sector Backup Type: "+BootSectorBackupType+"\n") 

        #Do WxFixBoot's settings.
        ReportList.write("\n##########Other WxFixBoot Settings##########\n")
        ReportList.write("Do Quick Filesystem Check: "+unicode(QuickFSCheck)+"\n")
        ReportList.write("Do Bad Sector Check: "+unicode(BadSectCheck)+"\n")
        ReportList.write("Show Diagnostic Terminal Output (***ignored***): "+unicode(FullVerbose)+"\n")
        ReportList.write("Save System Report To File: "+unicode(MakeSystemSummary)+"\n")

        if MakeSystemSummary:
            ReportList.write("\n\tSave Terminal Output in Report: "+unicode(SaveOutput)+"\n")
            ReportList.write("\tSystem Report Target File: "+ReportFile+"\n\n")

        ReportList.write("Number of operations to do: "+unicode(NumberOfOperations)+"\n")

        #Save terminal output.
        if SaveOutput:
            ReportList.write("\n##########Terminal Output##########\n")
            ReportList.write(self.ParentWindow.OutputBox.GetValue()) #*** Only works if FullVerbose is enabled, otherwise some output will be hidden. As such, all output is currently being shown with absolutely no regard to FullVerbose or ShowOutput passed to the function, or the user's checkbox in settingswindow ***

        #Save Log File.
        ReportList.write("\n##########WxFixBoot's Log File##########\n")
        logfile = open("/tmp/wxfixboot.log", "r")
        for line in logfile:
            ReportList.write(line)

        logfile.close()
 
#End Backend Thread
app = WxFixBoot(False)
app.MainLoop()
