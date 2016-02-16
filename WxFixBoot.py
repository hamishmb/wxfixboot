#!/usr/bin/env python
# -*- coding: utf-8 -*-
# WxFixBoot Version 1.1~pre1
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

#*** Make note of this: when 'cp' errors, the quotes it uses cause this error "UnicodeDecodeError" (use unicode(thing, , errors='ignore')) ***
#*** Make docstrings for each function as I update and move them ***
#*** Try to avoid using df because it's unreliable in the way it outputs data. Probably use "mount -l" instead for most things ***
#*** Mount filesystems inside the temporary directory instead of in /mnt ***
#*** Also use wx.MultiChoiceDialogs or equivalant where wanted ***
#*** Maybe use parted with the '-m' flag because we get lots of info in a easy to process way that way ***
#*** Always use self.Panel instead of self.MainPanel or whatever. ***
#*** Instead of wx.Exit(), make a emergency exit function that will handle log files and such ***
#*** Make sure to use "//" when we want int division ***

#Do future imports to prepare to support python 3. Use unicode strings rather than ASCII strings, as they fix potential problems.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#Import other modules
from distutils.version import LooseVersion
import wx
import sys
import threading
import time
import os
import shutil
import subprocess
import logging
import getopt
import re
from wx.animate import Animation
from wx.animate import AnimationCtrl

#Define the version number and the release date as global variables.
Version = "1.1~pre1"
ReleaseDate = "15/2/2016"

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

from GetDevInfo.getdevinfo import Main as DevInfoTools

from Tools.coretools import Main as CoreTools

from Tools.dialogtools import Main as DialogTools

from Tools.StartupTools.core import Main as CoreStartupTools
from Tools.StartupTools.main import Main as MainStartupTools

from Tools.BackendTools.core import Main as CoreBackendTools
from Tools.BackendTools.helpers import Main as HelperBackendTools
from Tools.BackendTools.essentials import Main as EssentialBackendTools
from Tools.BackendTools.main import Main as MainBackendTools

from Tools.BackendTools.BootloaderTools.main import Main as MainBootloaderTools
from Tools.BackendTools.BootloaderTools.getconfigtools import Main as GetConfigBootloaderTools
from Tools.BackendTools.BootloaderTools.removaltools import Main as BootloaderRemovalTools

#Setup custom-made modules (make global variables accessible inside the packages). *** Continue to add stuff as needed *** *** Cut/rejig these later ***
#GetDevInfo Package.
GetDevInfo.getdevinfo.subprocess = subprocess
GetDevInfo.getdevinfo.re = re
GetDevInfo.getdevinfo.logger = logger

#CoreTools Module.
Tools.coretools.subprocess = subprocess
Tools.coretools.logger = logger
Tools.coretools.os = os

#DialogTools Module.
Tools.dialogtools.wx = wx
Tools.dialogtools.time = time
Tools.dialogtools.logger = logger

#StartupTools Package (Core).
Tools.StartupTools.core.CoreTools = CoreTools
Tools.StartupTools.core.logger = logger
Tools.StartupTools.core.DialogTools = DialogTools

#StartupTools Package (Main).
Tools.StartupTools.main.CoreTools = CoreTools
Tools.StartupTools.main.logger = logger
Tools.StartupTools.main.DialogTools = DialogTools
Tools.StartupTools.main.CoreStartupTools = CoreStartupTools
Tools.StartupTools.main.time = time
Tools.StartupTools.main.os = os

#BackendTools Package (Core).
Tools.BackendTools.core.wx = wx
Tools.BackendTools.core.CoreTools = CoreTools
Tools.BackendTools.core.logger = logger
Tools.BackendTools.core.subprocess = subprocess #*** Remove this later ***

#BackendTools Package (Helpers)
Tools.BackendTools.helpers.wx = wx
Tools.BackendTools.helpers.CoreTools = CoreTools
Tools.BackendTools.helpers.logger = logger
Tools.BackendTools.helpers.DialogTools = DialogTools
Tools.BackendTools.helpers.CoreBackendTools = CoreBackendTools
Tools.BackendTools.helpers.subprocess = subprocess #*** Remove this later ***
Tools.BackendTools.helpers.LooseVersion = LooseVersion

#BackendTools Package (Essentials)
Tools.BackendTools.essentials.wx = wx
Tools.BackendTools.essentials.CoreTools = CoreTools
Tools.BackendTools.essentials.logger = logger
Tools.BackendTools.essentials.DialogTools = DialogTools
Tools.BackendTools.essentials.CoreBackendTools = CoreBackendTools
Tools.BackendTools.essentials.subprocess = subprocess #*** Remove this later ***
Tools.BackendTools.essentials.HelperBackendTools = HelperBackendTools

#BackendTools Package (Main).
Tools.BackendTools.main.CoreTools = CoreTools
Tools.BackendTools.main.logger = logger

#BootloaderTools Package (Main)
Tools.BackendTools.BootloaderTools.main.CoreTools = CoreTools
Tools.BackendTools.BootloaderTools.main.logger = logger
Tools.BackendTools.BootloaderTools.main.DialogTools = DialogTools
Tools.BackendTools.BootloaderTools.main.HelperBackendTools = HelperBackendTools
Tools.BackendTools.BootloaderTools.main.CoreBackendTools = CoreBackendTools
Tools.BackendTools.BootloaderTools.main.wx = wx
Tools.BackendTools.BootloaderTools.main.GetConfigBootloaderTools = GetConfigBootloaderTools
Tools.BackendTools.BootloaderTools.main.BootloaderRemovalTools = BootloaderRemovalTools

#BootloaderTools Package (GetConfigTools)
Tools.BackendTools.BootloaderTools.getconfigtools.CoreTools = CoreTools
Tools.BackendTools.BootloaderTools.getconfigtools.logger = logger
Tools.BackendTools.BootloaderTools.getconfigtools.DialogTools = DialogTools
Tools.BackendTools.BootloaderTools.getconfigtools.HelperBackendTools = HelperBackendTools
Tools.BackendTools.BootloaderTools.getconfigtools.CoreBackendTools = CoreBackendTools
Tools.BackendTools.BootloaderTools.getconfigtools.wx = wx

#BootloaderTools Package (RemovalTools)
Tools.BackendTools.BootloaderTools.removaltools.CoreTools = CoreTools
Tools.BackendTools.BootloaderTools.removaltools.logger = logger
Tools.BackendTools.BootloaderTools.removaltools.DialogTools = DialogTools
Tools.BackendTools.BootloaderTools.removaltools.HelperBackendTools = HelperBackendTools
Tools.BackendTools.BootloaderTools.removaltools.CoreBackendTools = CoreBackendTools
Tools.BackendTools.BootloaderTools.removaltools.wx = wx

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
        wx.CallAfter(self.ParentWindow.ReceiveDiskInfo, DevInfoTools().GetInfo())

#End Disk Information Handler thread.
#Begin Starter Class
class WxFixBoot(wx.App):
    def OnInit(self):
        InitialWindow().Show()
        return True

#End Starter Class
#Begin Initialization Panel.
class InitialPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.frame = parent
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    def OnEraseBackground(self, Event):
        """Redraw the background image when needed"""
        DC = Event.GetDC()

        if DC == None:
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
        wx.Frame.__init__(self, parent=None, title="WxFixBoot", size=(600,420), style=wx.SIMPLE_BORDER)
        self.Panel = InitialPanel(self)
        self.SetClientSize(wx.Size(600,420))

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
        InitThread(self, Starting=True)       

    def CreateProgressBarAndText(self):
        #Create a progressbar.
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
        self.ProgressBar.SetValue(int(Value))

        if self.ProgressBar.GetValue() == 100:
            self.FinishedInit()

    def UpdateProgressText(self, Message):
        self.ProgressText.SetLabel(Message)
        self.Panel.Layout()

    def FinishedInit(self, Event=None):
        logger.info("Closing Initial Window and Starting Main Window...")

        #Show the user some important information
        wx.MessageDialog(self.Panel, "Make sure you have a working internet connection before performing any operations. Thank you.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        MainFrame = MainWindow()
        app.SetTopWindow(MainFrame)
        self.Destroy()

        #Start MainFrame.
        MainFrame.Show(True)    

#End Initalization Frame.
#Begin Initaization Thread.
class InitThread(threading.Thread):
    def __init__(self, ParentWindow, Starting):
        """Make a temporary directory for data used by this program. If it already exists, delete it and recreate it, unless this isn't first run."""
        self.Starting = Starting

        if self.Starting:
            if os.path.isdir("/tmp/wxfixboot"):
                shutil.rmtree("/tmp/wxfixboot")
                logger.debug("InitThread(): Cleared WxFixBoot's temporary folder. Most of the time this doesn't need to be done, but it's probably not a problem. Logging this purely for paranoia's sake :)")

            else:
                os.mkdir("/tmp/wxfixboot")

        #Set up dialog tools.
        Tools.dialogtools.ParentWindow = ParentWindow

        #Initialize the thread.
        threading.Thread.__init__(self)
        self.ParentWindow = ParentWindow
        self.start()

    def run(self):
        if self.Starting:
            #Set some default settings and wait for the GUI to initialize.
            logger.debug("InitThread(): Starting...")

            #Check for dependencies
            logger.info("InitThread(): Checking For Dependencies...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Checking For Dependencies...")
            MainStartupTools().CheckDepends()
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "9")
            logger.info("InitThread(): Done Checking For Dependencies!")

            #Unmount all filesystems, to avoid any data corruption.
            logger.info("InitThread(): Unmounting Filesystems...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Unmounting Filesystems...")
            MainStartupTools().UnmountAllFS()
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "18")
            logger.info("InitThread(): Done Unmounting Filsystems!")

            #Check filesystems.
            logger.info("InitThread(): Checking Filesystems...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Checking Filesystems...")
            MainStartupTools().CheckFS()
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "27")
            logger.info("InitThread(): Filesystems Checked!")

            #Mount all filesystems.
            logger.info("InitThread(): Mounting Core Filesystems...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Mounting Core Filesystems...")
            MainStartupTools().MountCoreFS()
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "36")
            logger.info("InitThread(): Done Mounting Core Filsystems!")

            #Detect Devices, Partitions, and Partition Schemes
            #Define Global Variables. *** Once I switch to dictonaries, a lot of these variables will be unneeded/irrelevant as we will be able to view info for each device in a heirarchy ***
            global PartitionListWithFSType
            global DeviceList
            global PartSchemeList
            global AutoPartSchemeList
            global GPTInAutoPartSchemeList
            global MBRInAutoPartSchemeList

            logger.info("InitThread(): Detecting Devices, Partitions, and PartSchemes...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Getting Device Information...")
            PartitionListWithFSType, DeviceList, PartSchemeList, AutoPartSchemeList, GPTInAutoPartSchemeList, MBRInAutoPartSchemeList = MainStartupTools().DetectDevicesPartitionsAndPartSchemes()
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "46")
            logger.info("InitThread(): Finished Detecting Devices, Partitions, and PartSchemes!")

            #Detect Linux Partitions. *** Once I switch to dictonaries, a lot of these variables will be unneeded/irrelevant as we will be able to view info for each device in a heirarchy ***
            #Define Global Variables.
            global LinuxPartList

            logger.info("InitThread(): Detecting Linux Partitions...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Detecting Linux Partitions...")
            LinuxPartList = MainStartupTools().DetectLinuxPartitions()
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "55")
            logger.info("InitThread(): Finished Detecting Linux Partitions!")
  
            #Get the root filesystem and root device. *** Once I switch to dictonaries, a lot of these variables will be unneeded/irrelevant as we will be able to view info for each device in a heirarchy ***
            #Define Global Variables.
            global AutoRootFS
            global RootFS
            global AutoRootDevice
            global RootDevice
            global LiveDisk
            global AutoDefaultOS
            global DefaultOS
            global OSList

            logger.info("InitThread(): Determining Root Filesystem and Root Device...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Determining default OS...")
            AutoRootFS, RootFS, AutoRootDevice, RootDevice, LiveDisk, AutoDefaultOS, DefaultOS, OSList = MainStartupTools().GetRootFSandRootDev(LinuxPartList)
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "64")
            logger.info("InitThread(): Determined Root Filesystem as: "+RootFS+ " , Root Device is "+RootDevice)

            #Get a list of Linux OSs (if LiveDisk = True, this has already been run). *** Once I switch to dictonaries, a lot of these variables will be unneeded/irrelevant as we will be able to view info for each device in a heirarchy ***
            logger.info("InitThread(): Finding Linux OSs...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Finding Linux Operating Systems...")
            if LiveDisk == False:
                OSList, DefaultOS, AutoDefaultOS = MainStartupTools().GetLinuxOSs(LinuxPartList, LiveDisk, AutoRootFS)

            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "73")
            logger.info("InitThread(): Found all Linux OSs. Default: "+DefaultOS)

            #Get the firmware type. *** Once I switch to dictonaries, a lot of these variables will be unneeded/irrelevant as we will be able to view info for each device in a heirarchy ***
            #Define global variables.
            global FirmwareType
            global AutoFirmwareType
            global UEFIVariables

            logger.info("InitThread(): Determining Firmware Type...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Determining Filesystem Type...")
            FirmwareType, AutoFirmwareType, UEFIVariables = MainStartupTools().GetFirmwareType()
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "82")
            logger.info("InitThread(): Determined Firmware Type as: "+FirmwareType)

            #Get the Bootloader. *** Once I switch to dictonaries, a lot of these variables will be unneeded/irrelevant as we will be able to view info for each device in a heirarchy *** 
            #Define global variables.
            global Bootloader
            global AutoBootloader
            global PrevBootloaderSetting
            global AutoUEFISystemPartition
            global UEFISystemPartition
            global HelpfulUEFIPartition #*** Is this var actually helpful? ***
            global FatPartitions

            #Initialise them.
            HelpfulUEFIPartition = False
            PrevBootloaderSetting = "None"
            UEFISystemPartition = "None"
            AutoUEFISystemPartition = "None"
            FatPartitions=['None']

            logger.info("InitThread(): Determining The Bootloader...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Determining The Bootloader...")
            Bootloader, AutoBootloader, AutoUEFISystemPartition, UEFISystemPartition, HelpfulUEFIPartition, FatPartitions = MainStartupTools().GetBootloader(self.Starting, RootDevice, LiveDisk, FirmwareType)
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "91")
            logger.info("InitThread(): Bootloader is: "+Bootloader)

            #Perform final check.
            logger.info("InitThread(): Doing Final Check for error situations...")
            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Checking Everything...")
            AutoFirmwareType, FirmwareType = MainStartupTools().FinalCheck(LiveDisk, PartitionListWithFSType, LinuxPartList, DeviceList, AutoRootFS, RootFS, AutoRootDevice, RootDevice, DefaultOS, AutoDefaultOS, OSList, FirmwareType, AutoFirmwareType, UEFIVariables, PartSchemeList, AutoPartSchemeList, GPTInAutoPartSchemeList, MBRInAutoPartSchemeList, Bootloader, AutoBootloader, UEFISystemPartition, HelpfulUEFIPartition)
            wx.CallAfter(self.ParentWindow.UpdateProgressBar, "100")
            logger.info("InitThread(): Done Final Check!")

            #Set some other variables to default values, avoiding problems down the line.
            #Define globals.
            global ReinstallBootloader
            global UpdateBootloader
            global QuickFSCheck
            global BadSectCheck
            global SaveOutput
            global FullVerbose
            global Verify
            global BackupBootSector
            global BackupPartitionTable
            global MakeSystemSummary
            global BootloaderTimeout
            global BootloaderToInstall
            global BLOptsDlgRun
            global RestoreBootSector
            global BootSectorFile
            global BootSectorTargetDevice
            global BootSectorBackupType
            global RestorePartitionTable
            global PartitionTableFile
            global PartitionTableTargetDevice
            global PartitionTableBackupType
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
            BackupPartitionTable = ""
            MakeSystemSummary = ""
            BootloaderTimeout = ""
            BootloaderToInstall = ""
            BLOptsDlgRun = ""
            RestoreBootSector = ""
            BootSectorFile = ""
            BootSectorTargetDevice = ""
            BootSectorBackupType = ""
            RestorePartitionTable = ""
            PartitionTableFile = ""
            PartitionTableTargetDevice = ""
            PartitionTableBackupType = ""
            OptionsDlg1Run = ""

            logger.info("InitThread(): Setting some defaults for other variables set in GUI by user...")
            ReinstallBootloader, UpdateBootloader, QuickFSCheck, BadSectCheck, SaveOutput, FullVerbose, Verify, BackupBootSector, BackupPartitionTable, MakeSystemSummary, BootloaderTimeout, BootloaderToInstall, BLOptsDlgRun, RestoreBootSector, BootSectorFile, BootSectorTargetDevice, BootSectorBackupType, RestorePartitionTable, PartitionTableFile, PartitionTableTargetDevice, PartitionTableBackupType, OptionsDlg1Run = MainStartupTools().SetDefaults()

            wx.CallAfter(self.ParentWindow.UpdateProgressText, "Finished! Starting GUI...")
            logger.info("InitThread(): Finished Determining Settings. Exiting InitThread()...")

        else:
            #Get the Bootloader. It reads self.Starting for itself. **** This is broken, but soon we won't need self.Starting, cos GetBootloader can be called directly now it's in MainStartupTools() ***
            logger.info("InitThread(): Determining The Bootloader...")
            self.GetBootloader()
            logger.info("InitThread(): Bootloader is: "+Bootloader)

#End Initalization Thread.
#Begin Main Window
class MainWindow(wx.Frame):
    def __init__(self):
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
        self.statusbar = self.CreateStatusBar()
        self.StatusBar.SetFieldsCount(2)
        self.StatusBar.SetStatusWidths([-1, 150])
        self.StatusBar.SetStatusText("Ready.", 0)
        self.StatusBar.SetStatusText("v"+Version+" ("+ReleaseDate+")", 1)

    def CreateText(self):
        self.SettingsText = wx.StaticText(self.Panel, -1, "Please set the basic settings here first.")
        self.WelcomeText = wx.StaticText(self.Panel, -1, "Welcome to WxFixBoot!")

        #Add an image.
        img = wx.Image("/usr/share/pixmaps/wxfixboot.png", wx.BITMAP_TYPE_PNG)
        self.Logo = wx.StaticBitmap(self.Panel, -1, wx.BitmapFromImage(img))

    def CreateButtons(self):
        self.AboutButton = wx.Button(self.Panel, wx.ID_ANY, "About")
        self.ExitButton = wx.Button(self.Panel, wx.ID_ANY, "Quit")
        self.OptionsButton = wx.Button(self.Panel, wx.ID_ANY, "View Program Options")
        self.ApplyOperationsButton = wx.Button(self.Panel, wx.ID_ANY, "Apply All Operations")

    def CreateCBs(self):
        self.BadSectorCheckCB = wx.CheckBox(self.Panel, wx.ID_ANY, "Check All File Systems (thorough)")
        self.CheckFileSystemsCB = wx.CheckBox(self.Panel, wx.ID_ANY, "Check All File Systems (quick)")
        self.ReinstallBootloaderCB = wx.CheckBox(self.Panel, wx.ID_ANY, "Reinstall/Fix Bootloader")
        self.UpdateBootloaderCB = wx.CheckBox(self.Panel, wx.ID_ANY, "Update Bootloader Config")

        #If bootloader is grub legacy, disable some options.
        if Bootloader == "GRUB-LEGACY":
            self.DisableBLOptsGrubLegacy()

    def DisableBLOptsGrubLegacy(self):
        self.ReinstallBootloaderCB.Disable()
        self.UpdateBootloaderCB.Disable()

    def EnableBLOptsNoGrubLegacy(self):
        self.ReinstallBootloaderCB.Enable()
        self.ReinstallBootloaderCB.SetValue(False)
        self.UpdateBootloaderCB.Enable()
        self.UpdateBootloaderCB.SetValue(False)

    def CreateMenus(self):
        filemenu = wx.Menu()
        viewmenu = wx.Menu()
        editmenu = wx.Menu()
        helpmenu = wx.Menu() 
   
        #Adding Menu Items.
        self.menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.menuExit = filemenu.Append(wx.ID_EXIT,"&Exit", "Terminate this program")
        self.menuDevInfo = viewmenu.Append(wx.ID_ANY,"&Device Information", "Information about all detected devices") 
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
        logger.debug("MainWindow().OnCheckBox() was triggered.")
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
        if self.ReinstallBootloaderCB.IsChecked() and (Bootloader != "GRUB-LEGACY" or RestorePartitionTable or RestoreBootSector):
            self.ReinstallBootloaderCBwaschecked = True
            self.UpdateBootloaderCB.SetValue(0)
            self.UpdateBootloaderCB.Disable()
        elif self.ReinstallBootloaderCB.IsChecked() == False and Bootloader != "GRUB-LEGACY" and RestorePartitionTable == False and RestoreBootSector == False:
            self.UpdateBootloaderCB.Enable()
            self.ReinstallBootloaderCBwaschecked = False
        else:
            self.ReinstallBootloaderCB.SetValue(0)
            self.ReinstallBootloaderCBwaschecked = False

        #Update Bootloader Choicebox
        if self.UpdateBootloaderCB.IsChecked() and (Bootloader != "GRUB-LEGACY" or RestorePartitionTable or RestoreBootSector):
            self.UpdateBootloaderCBwaschecked = True
            self.ReinstallBootloaderCB.SetValue(0)
            self.ReinstallBootloaderCB.Disable()
        elif self.UpdateBootloaderCB.IsChecked() == False and Bootloader != "GRUB-LEGACY" and RestorePartitionTable == False and RestoreBootSector == False:
            self.ReinstallBootloaderCB.Enable()
            self.UpdateBootloaderCBwaschecked = False
        else:
            self.UpdateBootloaderCB.SetValue(0)
            self.UpdateBootloaderCBwaschecked = False

    def Opts(self, Event=None):
        global OptionsDlg1Run
        logger.debug("MainWindow().Opts(): Starting Options Window 1 and hiding MainWindow...")

        if self.ReinstallBootloaderCBwaschecked or self.UpdateBootloaderCBwaschecked:
            dlg = wx.MessageDialog(self.Panel, "Do you want to continue? If you reinstall or update your bootloader, some options, such as installing a different bootloader, and restoring backups of the bootsector and partition table, will be reset and disabled. If you want to change other settings, you can always do it after restarting WxFixBoot.", "WxFixBoot - Question", style=wx.YES_NO | wx.ICON_QUESTION, pos=wx.DefaultPosition)

            if dlg.ShowModal() == wx.ID_NO:
                wx.MessageDialog(self.Panel, "You will now be returned to the Main Window.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()
                return

        self.SaveMainOpts()

        if UEFISystemPartition == "None":
            wx.MessageDialog(self.Panel, "Seeing as you have no UEFI partition, you will be unable to select a UEFI bootloader to install, or as your current bootloader. However, in the bootloader options window, you can select a new UEFI partition.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()
        elif HelpfulUEFIPartition == False:
            wx.MessageDialog(self.Panel, "No bootloaders were found on your UEFI partition. However, you will still be able to select a UEFI bootloader to install, or as your current bootloader, as UEFI bootloader detection is a little bit sketchy. In the bootloader options window, you can select a different UEFI partition.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        if FirmwareType == "BIOS":
            wx.MessageDialog(self.Panel, "Make sure you set the Root Device correctly here! Chances are, you won't need to change it, but it always needs to be set to the device your system boots off (usually the first hard drive in the system). You can see this information in the default OS selection in the following window. For example if your OS boots off /dev/sdc3, the root device should be set to /dev/sdc. The root device here will also be the device that's backed up if either backup option is selected. Thank you.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()
        else:
            wx.MessageDialog(self.Panel, "Make sure you set the Root Device correctly here, because it will be the device that's backed up if you choose to back up the partition table. The boot sector to backup in this case is the UEFI System Partition, if there is one. Thank you.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        OptionsDlg1Run = True
        self.Hide()
        OptionsWindow1(self).Show()

    def DevInfo(self, Event=None):
        logger.debug("MainWindow().DevInfo(): Starting Device Info Window...")
        DevInfoWindow(self).Show()

    def ProgressWindow(self, Event=None):
        if OptionsDlg1Run and self.ReinstallBootloaderCBwaschecked == False and self.UpdateBootloaderCBwaschecked == False:
            logger.debug("MainWindow().ProgressWindow(): Starting Progress Window...")
            self.SaveMainOpts()
            ProgressFrame = ProgressWindow()
            app.SetTopWindow(ProgressFrame)
            ProgressFrame.Show(True)
            self.Destroy()
        else:
            wx.MessageDialog(self.Panel, "Please check the settings in the Options Window before continuing, especially after changing the options in the Main Window!", "WxFixBoot - Error", style=wx.OK | wx.ICON_ERROR, pos=wx.DefaultPosition).ShowModal()

    def RefreshMainWindow(self,msg):
        #Refresh the main window to reflect changes in the options, or after a restart.
        logger.debug("MainWindow().RefreshMainWindow(): Refreshing MainWindow...")
            
        #Bootloader options. Also check if the partition table or boot sector are to be restored
        if Bootloader == "GRUB-LEGACY" or RestorePartitionTable or RestoreBootSector:
            self.DisableBLOptsGrubLegacy()
        else:
            self.EnableBLOptsNoGrubLegacy()

        #Set settings up how they were when MainWindow was hidden earlier, if possible.
        if Bootloader != "GRUB-LEGACY" and RestorePartitionTable == False and RestoreBootSector == False:
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
        #Bind all mainwindow events in a seperate function
        self.Bind(wx.EVT_MENU, self.OnAbout, self.menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, self.AboutButton)
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.ExitButton)
        self.Bind(wx.EVT_MENU, self.DevInfo, self.menuDevInfo)
        self.Bind(wx.EVT_MENU, self.Opts, self.menuOpts)
        self.Bind(wx.EVT_BUTTON, self.Opts, self.OptionsButton)
        self.Bind(wx.EVT_BUTTON, self.ProgressWindow, self.ApplyOperationsButton)

        #Checkboxes on the main window.
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.ReinstallBootloaderCB)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.UpdateBootloaderCB)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.CheckFileSystemsCB)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.BadSectorCheckCB)

    def SaveMainOpts(self):
        #Save all options here.
        logger.debug("MainWindow().SaveMainOpts(): Saving Options on MainWindow...")
        global BootloaderToInstall
        global BootSectorFile
        global RestoreBootSector
        global PartitionTableFile
        global RestorePartitionTable
        global ReinstallBootloader
        global UpdateBootloader
        global QuickFSCheck
        global BadSectCheck
        global Bootloader

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
            BootloaderToInstall = "None"
            BootSectorFile = "None"
            RestoreBootSector = False
            PartitionTableFile = "None"
            RestorePartitionTable = False
        else:
            ReinstallBootloader = False

        #Update Bootloader Choicebox
        if self.UpdateBootloaderCB.IsChecked():
            UpdateBootloader = True

            #Disable some stuff
            BootloaderToInstall = "None"
            BootSectorFile = "None"
            RestoreBootSector = False
            PartitionTableFile = "None"
            RestorePartitionTable = False
        else:
            UpdateBootloader = False

        logger.debug("MainWindow().SaveMainOpts(): MainWindow options saved!")

    def OnExit(self, Event=None):
        #Shut down.
        Dlg = wx.MessageDialog(self.Panel, 'Are you sure you want to exit?', 'WxFixBoot - Question!', wx.YES_NO | wx.ICON_QUESTION)
        if Dlg.ShowModal() == wx.ID_YES:
            logger.debug("MainWindow().OnExit(): Exiting...")

            #Run the exit sequence *** Check if filesystems here are unmounted first! ***
            if os.path.isdir("/tmp/wxfixboot"):
                shutil.rmtree('/tmp/wxfixboot')

            #Prompt user to save the log file.
            dlg = wx.MessageDialog(self.Panel, "Do you want to keep WxFixBoot's log file? For privacy reasons, WxFixBoot will delete its log file when closing. If you want to save it, which is helpful for debugging if something went wrong, click yes, and otherwise click no.", "WxFixBoot - Question", style=wx.YES_NO | wx.ICON_QUESTION, pos=wx.DefaultPosition)

            if dlg.ShowModal() == wx.ID_YES:
                #Ask the user where to save it.
                Dlg = wx.FileDialog(self.Panel, "Save log file to...", defaultDir="/home", wildcard="Log Files (*.log)|*.log" , style=wx.SAVE)

                if Dlg.ShowModal() == wx.ID_OK:
                    #Get the path.
                    File = Dlg.GetPath()

                    #Copy it to the specified path, using a one-liner, and don't bother handling any errors, because this is run as root.
                    CoreTools().StartProcess("cp /tmp/wxfixboot.log "+File, ReturnOutput=False)

                    wx.MessageDialog(self.Panel, 'Done! WxFixBoot will now exit.', 'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION).ShowModal()

                else:
                    wx.MessageDialog(self.Panel, 'Okay, WxFixBoot will now exit without saving the log file.', 'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION).ShowModal()

            else:
                wx.MessageDialog(self.Panel, 'Okay, WxFixBoot will now exit without saving the log file.', 'WxFixBoot - Information', wx.OK | wx.ICON_INFORMATION).ShowModal()

            #Delete the log file, and don't bother handling any errors, because this is run as root.
            os.remove('/tmp/wxfixboot.log')
            self.Destroy()

#End Main window
#Begin Disk Info Window
class DevInfoWindow(wx.Frame):
    def __init__(self,ParentWindow):
        """Initialize DevInfoWindow"""
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title="WxFixBoot - Disk Information", size=(780,310), style=wx.DEFAULT_FRAME_STYLE)
        self.DevInfoPanel = wx.Panel(self)
        self.SetClientSize(wx.Size(780,310))
        self.ParentWindow = ParentWindow
        wx.Frame.SetIcon(self, AppIcon)

        logger.debug("DevInfoWindow().__init__(): Creating widgets...")
        self.CreateWidgets()

        logger.debug("DevInfoWindow().__init__(): Setting up sizers...")
        self.SetupSizers()

        logger.debug("DevInfoWindow().__init__(): Binding events...")
        self.BindEvents()

        #Use already-present info for the list ctrl if possible.
        if 'DiskInfo' in globals():
            logger.debug("DevInfoWindow().__init__(): Updating list ctrl with Disk info already present...")
            self.UpdateListCtrl()

        #Call Layout() on self.DevInfoPanel() to ensure it displays properly.
        self.DevInfoPanel.Layout()

        logger.info("DevInfoWindow().__init__(): Ready. Waiting for events...")

    def CreateWidgets(self):
        """Create all widgets for DevInfoWindow"""
        self.TitleText = wx.StaticText(self.DevInfoPanel, -1, "Here are all the detected disks on your computer")
        self.ListCtrl = wx.ListCtrl(self.DevInfoPanel, -1, style=wx.LC_REPORT|wx.LC_VRULES)
        self.OkayButton = wx.Button(self.DevInfoPanel, -1, "Okay")
        self.RefreshButton = wx.Button(self.DevInfoPanel, -1, "Refresh")

        #Create the animation for the throbber.
        throb = wx.animate.Animation("/usr/share/wxfixboot/images/Throbber.gif")
        self.Throbber = wx.animate.AnimationCtrl(self.DevInfoPanel, -1, throb)
        self.Throbber.SetUseWindowBackgroundColour(True)
        self.Throbber.SetInactiveBitmap(wx.Bitmap("/usr/share/wxfixboot/images/ThrobberRest.png", wx.BITMAP_TYPE_PNG))
        self.Throbber.SetClientSize(wx.Size(30,30))

    def SetupSizers(self):
        """Set up the sizers for DevInfoWindow"""
        #Make a button boxsizer.
        BottomSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add each object to the bottom sizer.
        BottomSizer.Add(self.RefreshButton, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_LEFT, 10)
        BottomSizer.Add((20,20), 1)
        BottomSizer.Add(self.Throbber, 0, wx.ALIGN_CENTER|wx.FIXED_MINSIZE)
        BottomSizer.Add((20,20), 1)
        BottomSizer.Add(self.OkayButton, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT, 10)

        #Make a boxsizer.
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        #Add each object to the main sizer.
        MainSizer.Add(self.TitleText, 0, wx.ALL|wx.CENTER, 10)
        MainSizer.Add(self.ListCtrl, 1, wx.EXPAND|wx.ALL, 10)
        MainSizer.Add(BottomSizer, 0, wx.EXPAND|wx.ALL ^ wx.TOP, 10)

        #Get the sizer set up for the frame.
        self.DevInfoPanel.SetSizer(MainSizer)
        MainSizer.SetMinSize(wx.Size(780,310))
        MainSizer.SetSizeHints(self)

    def BindEvents(self):
        """Bind all events for DevInfoWindow"""
        self.Bind(wx.EVT_BUTTON, self.GetDiskInfo, self.RefreshButton)
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.OkayButton)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

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

    def GetDiskInfo(self, Event=None):
        """Call the thread to get Disk info, disable the refresh button, and start the throbber"""
        logger.info("DevInfoWindow().UpdateDevInfo(): Generating new Disk info...")
        self.RefreshButton.Disable()
        self.Throbber.Play()
        GetDiskInformation(self)

    def ReceiveDiskInfo(self, Info):
        """Get Disk data, call self.UpdateListCtrl(), and then call MainWindow().UpdateFileChoices() to refresh the file choices with the new info"""
        global DiskInfo
        DiskInfo = Info

        #Update the list control.
        logger.debug("DevInfoWindow().UpdateDevInfo(): Calling self.UpdateListCtrl()...")
        self.UpdateListCtrl()

        #Stop the throbber and enable the refresh button.
        self.Throbber.Stop()
        self.RefreshButton.Enable()

    def UpdateListCtrl(self, Event=None):
        """Update the list control"""
        logger.debug("DevInfoWindow().UpdateListCtrl(): Clearing all objects in list ctrl...")
        self.ListCtrl.ClearAll()

        #Create the columns.
        logger.debug("DevInfoWindow().UpdateListCtrl(): Inserting columns into list ctrl...")
        self.ListCtrl.InsertColumn(col=0, heading="Name", format=wx.LIST_FORMAT_CENTRE)
        self.ListCtrl.InsertColumn(col=1, heading="Type", format=wx.LIST_FORMAT_CENTRE)
        self.ListCtrl.InsertColumn(col=2, heading="Vendor", format=wx.LIST_FORMAT_CENTRE)
        self.ListCtrl.InsertColumn(col=3, heading="Product", format=wx.LIST_FORMAT_CENTRE)
        self.ListCtrl.InsertColumn(col=4, heading="Size", format=wx.LIST_FORMAT_CENTRE)
        self.ListCtrl.InsertColumn(col=5, heading="Description", format=wx.LIST_FORMAT_CENTRE) 

        #Add info from the custom module.
        logger.debug("DevInfoWindow().UpdateListCtrl(): Adding Disk info to list ctrl...")

        Keys = DiskInfo.keys()
        Keys.sort()

        #Do all of the data at the same time.
        Number = -1
        for Disk in Keys:
            Number += 1
            Info = DiskInfo[Disk]
            self.ListCtrl.InsertStringItem(index=Number, label=Info["Name"])
            self.ListCtrl.SetStringItem(index=Number, col=1, label=Info["Type"])
            self.ListCtrl.SetStringItem(index=Number, col=2, label=Info["Vendor"])
            self.ListCtrl.SetStringItem(index=Number, col=3, label=Info["Product"])
            self.ListCtrl.SetStringItem(index=Number, col=4, label=Info["Size"])
            self.ListCtrl.SetStringItem(index=Number, col=5, label=Info["Description"])

        #Auto Resize the columns.
        self.OnSize()

    def OnExit(self, Event=None):
        """Exit DevInfoWindow"""
        logger.info("DevInfoWindow().OnExit(): Closing DevInfoWindow...")
        self.Destroy()

#End Disk Info Window
#Begin Options Window 1
class OptionsWindow1(wx.Frame):
    def __init__(self, ParentWindow):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title="WxFixBoot - Options", size=(600,360), style=wx.DEFAULT_FRAME_STYLE)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(600,360))
        self.ParentWindow = ParentWindow
        wx.Frame.SetIcon(self, AppIcon)

        self.CreateButtons()
        self.CreateText()
        self.UpdateBLOptsText()
        self.CreateCBs()
        self.CreateChoiceBs()
        self.CreateSpinners()
        self.SetupOptions()
        self.SetupSizers()
        self.BindEvents()

        logger.debug("OptionsWindow1().__init__(): OptionsWindow1 Started.")

    def CreateButtons(self):
        #Create Some buttons.
        self.ExitButton = wx.Button(self.Panel, -1, "Apply these Settings and Close")
        self.BootloaderOptionsButton = wx.Button(self.Panel, -1, "View Bootloader Options")
        self.RestoreBootsectorButton = wx.Button(self.Panel, -1, "Restore Boot Sector")
        self.RestorePartitionTableButton = wx.Button(self.Panel, -1, "Restore Partition Table")

    def CreateText(self):
        #Create the text, aligning it where needed.
        self.WelcomeText = wx.StaticText(self.Panel, -1, "Welcome to Options. Please give all the settings a once-over.")
        self.BasicSettingsText = wx.StaticText(self.Panel, -1, "Basic Settings:")
        self.InstalledBootloaderText = wx.StaticText(self.Panel, -1, "Installed Bootloader:")
        self.DefaultOSText = wx.StaticText(self.Panel, -1, "Default OS to boot:")
        self.BootloaderTimeoutText = wx.StaticText(self.Panel, -1, "Bootloader timeout value:")
        self.BootloaderTimeoutText2 = wx.StaticText(self.Panel, -1, "(seconds, -1 represents current value)") 
        self.AdvancedSettingsText = wx.StaticText(self.Panel, -1, "Advanced Settings:")
        self.RootDeviceText = wx.StaticText(self.Panel, -1, "Root device:")
        self.BootloaderToInstallText = wx.StaticText(self.Panel, -1, "Bootloader To Install:")
        self.FirmwareTypeText = wx.StaticText(self.Panel, -1, "Selected Firmware Type:")

    def CreateCBs(self):
        #Basic settings
        self.FullVerboseCheckBox = wx.CheckBox(self.Panel, -1, "Show diagnostic terminal output")

        #Advanced settings
        self.MakeSummaryCheckBox = wx.CheckBox(self.Panel, -1, "Save System Report To File")
        self.LogOutputCheckBox = wx.CheckBox(self.Panel, -1, "Save terminal output in Report")
        self.BackupBootsectorCheckBox = wx.CheckBox(self.Panel, -1, "Backup the Bootsector of "+RootDevice)
        self.BackupPartitionTableCheckBox = wx.CheckBox(self.Panel, -1, "Backup the Partition Table of "+RootDevice)

    def CreateChoiceBs(self):
        #Basic settings
        self.DefaultOSChoice = wx.Choice(self.Panel, -1, size=(140,30), choices=OSList)

        #Advanced settings
        self.RootDeviceChoice = wx.Choice(self.Panel, -1, size=(140,30), choices=["Auto: "+AutoRootDevice]+DeviceList)

    def CreateSpinners(self):
        #Basic option here.
        self.BootloaderTimeoutSpinner = wx.SpinCtrl(self.Panel, -1, "")
        self.BootloaderTimeoutSpinner.SetRange(-1,100)
        self.BootloaderTimeoutSpinner.SetValue(-1)

    def OnCheckBox(self, Event=None):
        #Manage the checkboxes states.
        if self.MakeSummaryCheckBox.IsChecked():
            self.LogOutputCheckBox.Enable()
            self.LogOutputCheckBox.SetValue(True)
        else:
            self.LogOutputCheckBox.SetValue(False)
            self.LogOutputCheckBox.Disable()

    def SetupOptions(self):
        #Load all Options here.
        logger.debug("OptionsWindow1().SetupOptions(): Setting up options in OptionsDlg1...")

        global BootloaderToInstall
        global DefaultOS

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

        #Backup Partition Table CheckBox
        if BackupPartitionTable:
            self.BackupPartitionTableCheckBox.SetValue(True)
        else:
            self.BackupPartitionTableCheckBox.SetValue(False)

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

        if UEFISystemPartition == "None":
            self.InstalledBootloaderChoice = wx.Choice(self.Panel, -1, size=(140,30), choices=['Auto: '+AutoBootloader, 'GRUB-LEGACY', 'GRUB2', 'LILO'])
        else:
            self.InstalledBootloaderChoice = wx.Choice(self.Panel, -1, size=(140,30), choices=['Auto: '+AutoBootloader, 'GRUB-LEGACY', 'GRUB2', 'GRUB-UEFI', 'LILO', 'ELILO'])

        #Installed Bootloader
        if Bootloader != AutoBootloader:
            self.InstalledBootloaderChoice.SetStringSelection(Bootloader)
        else:
            self.InstalledBootloaderChoice.SetSelection(0)

        #Default OS
        self.DefaultOSChoice.SetStringSelection(DefaultOS)
        
        #Root Device
        if RootDevice != AutoRootDevice:
            self.RootDeviceChoice.SetStringSelection(RootDevice)
        else:
            self.RootDeviceChoice.SetSelection(0)

        if RestoreBootSector or RestorePartitionTable:
            #Disable/reset some options.
            self.BootloaderOptionsButton.Disable()
            self.InstalledBootloaderChoice.Disable()
            self.DefaultOSChoice.Disable()
            self.BootloaderTimeoutSpinner.SetValue(-1)
            self.BootloaderTimeoutSpinner.Disable()

            #Reset some settings.
            BootloaderToInstall = "None"
            DefaultOS = AutoDefaultOS
        else:
            #Enable some options.
            self.BootloaderOptionsButton.Enable()
            self.InstalledBootloaderChoice.Enable()
            self.DefaultOSChoice.Enable()

        #Disable some options if the bootloader is to be reinstalled or updated.
        if ReinstallBootloader or UpdateBootloader:
            self.BootloaderOptionsButton.Disable()
            self.RestoreBootsectorButton.Disable()
            self.RestorePartitionTableButton.Disable()

        logger.debug("OptionsWindow1().SetupOptions(): Options in OptionsDlg1 set up!")

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
        InstalledBootloaderChoiceSizer = wx.BoxSizer(wx.HORIZONTAL)

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
        InstalledBootloaderChoiceSizer.Add(self.InstalledBootloaderText, 1, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        InstalledBootloaderChoiceSizer.Add(self.InstalledBootloaderChoice, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)

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
        BasicSettingsSizer.Add(InstalledBootloaderChoiceSizer, 1, wx.BOTTOM|wx.EXPAND, 10)
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
        AdvancedSettingsSizer.Add(self.BackupPartitionTableCheckBox, 1, wx.BOTTOM, 10)

        #Add items to the all settings sizer.
        AllSettingsSizer.Add(BasicSettingsSizer, 4, wx.RIGHT|wx.EXPAND, 5)
        AllSettingsSizer.Add(wx.StaticLine(self.Panel), 0, wx.EXPAND) #*** Check if this works on wx 3 or not ***
        AllSettingsSizer.Add(AdvancedSettingsSizer, 3, wx.LEFT|wx.EXPAND, 5)

        #Add items to the bootloader options sizer. #*** Sort out alignment ***
        BootloaderOptionsSizer.Add(self.BootloaderToInstallText, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        BootloaderOptionsSizer.Add(self.BootloaderOptionsButton, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        BootloaderOptionsSizer.Add(self.FirmwareTypeText, 1, wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to the bottom button sizer.
        BottomButtonSizer.Add(self.RestoreBootsectorButton, 2, wx.RIGHT|wx.ALIGN_CENTER, 5)
        BottomButtonSizer.Add(self.ExitButton, 3, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        BottomButtonSizer.Add(self.RestorePartitionTableButton, 2, wx.LEFT|wx.ALIGN_CENTER, 5)

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

    def UpdateBLOptsText(self):
        #Recreate the Bootloader options text, and make sure it's in the right place. *** Get rid of this and just call the function on the wx.StaticTexts ***
        #We have to lie about the Panel's Width here, so the text is placed where we want it.
        logger.debug("OptionsWindow1().UpdateBLOptsText(): Updating Bootloader Options text in OptionsDlg1...")

        #Do the Bootloader to install text first.
        self.BootloaderToInstallText.SetLabel("Installed Bootloader: "+BootloaderToInstall)

        #Do the Firmware Type Text now.
        self.FirmwareTypeText.SetLabel("Selected Firmware Type: "+FirmwareType)

        logger.debug("OptionsWindow1().UpdateBLOptsText(): Bootloader Options text in OptionsDlg1 updated!")

    def BindEvents(self):
        self.Bind(wx.EVT_BUTTON, self.CloseOpts, self.ExitButton)
        self.Bind(wx.EVT_CLOSE, self.CloseOpts)
        self.Bind(wx.EVT_BUTTON, self.LaunchblOpts, self.BootloaderOptionsButton)
        self.Bind(wx.EVT_BUTTON, self.LaunchBootSectWindow, self.RestoreBootsectorButton)
        self.Bind(wx.EVT_BUTTON, self.LaunchPartTableWindow, self.RestorePartitionTableButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.MakeSummaryCheckBox)

    def LaunchblOpts(self, Event=None):
        #Safeguard program reliability (and continuity) by saving the settings in optionswindow1 first. *** Destroy dialogs here ***
        self.SaveOptions()

        #Give some warnings here if needed.
        #Tell the user some options will be disabled if the bootloader is to be reinstalled or updated.
        if ReinstallBootloader or UpdateBootloader:
            wx.MessageDialog(self.Panel, "Your current bootloader is to be reinstalled or updated, therefore almost all bootloader-related options here will be disabled. If you want to install a different bootloader, please uncheck the reinstall or update bootloader option in the main window.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        #Recommend a MBR bootloader on BIOS systems.
        if FirmwareType == "BIOS":
            wx.MessageDialog(self.Panel, "Your firmware type is BIOS. Unless you're sure WxFixBoot has misdetected this, and it's actually UEFI, it's recommended that you install an BIOS bootloader, if you are installing a bootloader, such as GRUB2 or LILO, or your system might not boot correctly.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        #Recommend a UEFI boot loader on UEFI systems, if needed.
        elif FirmwareType == "UEFI":
            wx.MessageDialog(self.Panel, "Your firmware type is UEFI. Unless you're sure WxFixBoot has misdetected this, and it's actually BIOS, it's recommended that you install a UEFI bootloader, if you are installing a bootloader, such as GRUB-UEFI or ELILO, or your system might not boot correctly.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        if UEFISystemPartition == "None" and Bootloader in ('GRUB-UEFI', 'ELILO'):
            wx.MessageDialog(self.Panel, "You have a UEFI Bootloader, but no UEFI Partition! Something has gone wrong here! WxFixBoot will not install a UEFI bootloader without a UEFI partition, as it's impossible, and those options will now be disabled. Did you change your selected UEFI Partition?", "WxFixBoot - ERROR", style=wx.OK | wx.ICON_ERROR, pos=wx.DefaultPosition).ShowModal()

        elif UEFISystemPartition == "None":
            wx.MessageDialog(self.Panel, "You have no UEFI Partition. If you wish to install a UEFI bootloader, you'll need to create one first. WxFixBoot will not install a UEFI bootloader without a UEFI partition, as it's impossible, and those options will now be disabled.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        wx.MessageDialog(self.Panel, "Most of the settings in the following dialog do not need to be and shouldn't be touched, with the exception of autodetermining the bootloader, or manually selecting one. The firmware type and partition schemes should not normally be changed. Thank you.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        #Open the Firmware Options window
        logger.debug("OptionsWindow1().LaunchblOpts(): Starting Options Window 2 (aka Bootloader Options Dlg)...")
        self.Hide()
        OptionsWindow2(self).Show()

    def LaunchBootSectWindow(self, Event=None):
        #Safeguard program reliability (and continuity) by saving the settings in optionswindow1 first.
        self.SaveOptions()

        logger.debug("OptionsWindow1().LaunchBootSectWindow(): Starting Restore BootSector dialog...")
        #Show helpful info if the root device uses gpt.
        Tempnum = DeviceList.index(RootDevice)
        Temp = PartSchemeList[Tempnum]

        if Temp == "gpt":
             wx.MessageDialog(self.Panel, "Because the selected root device uses gpt, the Target Device selection in the following dialog will be ignored, though you must still set it, and the backup will always be restored to the UEFI Partition. Please keep this in mind and be sure that the UEFI Partition chosen is correct. You can check and change this in the Bootloader Options.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        self.Hide()
        RestoreWindow(ParentWindow=self,Type="BootSector").Show()

    def LaunchPartTableWindow(self, Event=None):
        #Safeguard program reliability (and continuity) by saving the settings in optionswindow1 first.
        self.SaveOptions()

        logger.debug("OptionsWindow1().LaunchPartTableWindow(): Starting Restore PartTable dialog...")
        self.Hide()
        RestoreWindow(ParentWindow=self,Type="PartTable").Show()

    def RefreshOptionsDlg1(self,msg):
        #Check if the partition table or boot sector are to be restored.
        logger.debug("OptionsWindow1().RefreshOptionsDlg1(): Refreshing OptionsDlg1...")
        if RestorePartitionTable or RestoreBootSector:
            #Disable/reset some options.
            self.BootloaderOptionsButton.Disable()
            self.InstalledBootloaderChoice.Disable()
            self.DefaultOSChoice.Disable()
            self.BootloaderTimeoutSpinner.SetValue(-1)
            self.BootloaderTimeoutSpinner.Disable()

            #Reset some settings.
            global BootloaderToInstall
            global FirmwareType
            global DefaultOS
            BootloaderToInstall = "None"
            FirmwareType = AutoFirmwareType
            DefaultOS = AutoDefaultOS

        else:
            #Enable some options.
            self.BootloaderOptionsButton.Enable()
            self.InstalledBootloaderChoice.Enable()
            self.DefaultOSChoice.Enable()
            self.BootloaderTimeoutSpinner.Enable()

        #Setup options again, but destroy a widget first so it isn't duplicated. *** This doesn't work with the sizer, fix it ***
        self.InstalledBootloaderChoice.Destroy()
        self.SetupOptions()

        #Update the BootloaderToInstall and FirmwareType text.
        self.UpdateBLOptsText()

        #Show OptionsDlg1.
        self.Show()

    def SaveOptions(self, Event=None):
        #Save all options in this window here.
        global SaveOutput
        global FullVerbose
        global SaveOutput
        global BackupBootSector
        global BackupPartitionTable
        global MakeSystemSummary
        global Bootloader
        global PrevBootloaderSetting
        global DefaultOS
        global RootDevice
        global RootFS
        global BootloaderTimeout

        logger.info("OptionsWindow1().SaveOptions(): Saving Options...")
        
        #Checkboxes.

        #Create Log checkbox.
        if self.LogOutputCheckBox.IsChecked():
            SaveOutput = True
        else:
            SaveOutput = False
        logger.debug("OptionsWindow1().SaveOptions(): Value of SaveOutput is: "+unicode(SaveOutput))

        #Check FS cb
        if self.FullVerboseCheckBox.IsChecked():
            FullVerbose = True
        else:
            FullVerbose = False
        logger.debug("OptionsWindow1().SaveOptions(): Value of FullVerbose is: "+unicode(FullVerbose))

        #Remount FS CB
        if self.LogOutputCheckBox.IsChecked():
            SaveOutput = True
        else:
            SaveOutput = False
        logger.debug("OptionsWindow1().SaveOptions(): Value of SaveOutput is: "+unicode(SaveOutput))

        #Backup BootSector checkbox.
        if self.BackupBootsectorCheckBox.IsChecked():
            BackupBootSector = True
        else:
            BackupBootSector = False
        logger.debug("OptionsWindow1().SaveOptions(): Value of BackupBootSector is: "+unicode(BackupBootSector))

        #Backup Partition Table checkbox.
        if self.BackupPartitionTableCheckBox.IsChecked():
            BackupPartitionTable = True
        else:
            BackupPartitionTable = False
        logger.debug("OptionsWindow1().SaveOptions(): Value of BackupPartitionTable is: "+unicode(BackupPartitionTable))

        #Use chroot in operations checkbox
        if self.MakeSummaryCheckBox.IsChecked():
            MakeSystemSummary = True
        else:
            MakeSystemSummary = False
        logger.debug("OptionsWindow1().SaveOptions(): Value of MakeSystemSummary is: "+unicode(MakeSystemSummary))

        #ChoiceBoxes
        #Currently Installed Bootloader ChoiceBox
        PrevBootloaderSetting = Bootloader
        if self.InstalledBootloaderChoice.GetSelection() != 0:
            Bootloader = self.InstalledBootloaderChoice.GetStringSelection()
        else:
            #Set it to the auto value, using AutoBootloader
            Bootloader = AutoBootloader
        logger.debug("OptionsWindow1().SaveOptions(): Value of Bootloader is: "+Bootloader)

        #Default OS choicebox
        DefaultOS = self.DefaultOSChoice.GetStringSelection()
        logger.debug("OptionsWindow1().SaveOptions(): Value of DefaultOS is: "+DefaultOS)

        #Root Filesystem.
        RootFS = self.DefaultOSChoice.GetStringSelection().split()[-1]
        logger.debug("OptionsWindow1().SaveOptions(): Value of RootFS is: "+RootFS)

        #Root device ChoiceBox
        if self.RootDeviceChoice.GetSelection() != 0:
            RootDevice = self.RootDeviceChoice.GetStringSelection()            
        else:
            #Set it to the auto value, in case this has already been changed.
            RootDevice = AutoRootDevice
        logger.debug("OptionsWindow1().SaveOptions(): Value of RootDevice is: "+RootDevice)

        #Spinner
        BootloaderTimeout = int(self.BootloaderTimeoutSpinner.GetValue())
        logger.debug("OptionsWindow1().SaveOptions(): Value of BootloaderTimeout is: "+unicode(BootloaderTimeout))

        logger.info("OptionsWindow1().SaveOptions(): Saved options.")

    def CloseOpts(self, Event=None):
        #Save the options first.
        self.SaveOptions()

        #Send a message to mainwindow so it can refresh.
        wx.CallAfter(self.ParentWindow.RefreshMainWindow, "Closed")

        #Exit options window 1.
        logger.debug("OptionsWindow1().SaveOptions(): OptionsWindow1 is closing. Revealing MainWindow...")
        self.Destroy()

#End Options window 1
#Begin Options window 2 *** Maybe say what the changes will be before closing to make it easier for the user *** *** The partitioning stuff can be changed and made better when we switch to dictionaries ***
class OptionsWindow2(wx.Frame):
    def __init__(self,ParentWindow):
        wx.Frame.__init__(self, parent=wx.GetApp().TopWindow, title="WxFixBoot - Bootloader Options", size=(450,330), style=wx.DEFAULT_FRAME_STYLE)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(450,330))
        self.ParentWindow = ParentWindow
        wx.Frame.SetIcon(self, AppIcon)

        self.CreateButtons()
        self.CreateCheckboxes()
        self.CreateText()
        self.CreateRadios()
        self.CreateChoiceBs()
        self.SetDefaults()
        self.SetupSizers()
        self.BindEvents()

        logger.debug("OptionsWindow2().__init__(): OptionsWindow2 Started.")

    def CreateButtons(self):
        self.ExitButton = wx.Button(self.Panel, -1, "Close")

    def CreateCheckboxes(self): #*** Change the text here to make it clearer ***
        self.UEFItoBIOSCheckBox = wx.CheckBox(self.Panel, -1, "Replace a UEFI bootloader with the BIOS equivalent")
        self.BIOStoUEFICheckBox = wx.CheckBox(self.Panel, -1, "Replace a BIOS bootloader with the UEFI equivalent")
        self.AutoDetermineCheckBox = wx.CheckBox(self.Panel, -1, "Automatically determine the bootloader to install")
        self.DoNotChangeBootloaderCheckBox = wx.CheckBox(self.Panel, -1, "Do not install a new bootloader")

    def CreateText(self):
        self.FirmwareTypeText = wx.StaticText(self.Panel, -1, "Firmware type:")
        self.OptionsText = wx.StaticText(self.Panel, -1, "Options:")
        self.PartitioningText = wx.StaticText(self.Panel, -1, "Partitioning on "+RootDevice+":")
        self.BootloaderToInstallText = wx.StaticText(self.Panel, -1, "Bootloader to install:")
        self.UEFIPartitionText = wx.StaticText(self.Panel, -1, "UEFI Partition:")
 
    def CreateRadios(self):
        #Create radio buttons.
        self.AutoFirmwareTypeRadioButton = wx.RadioButton(self.Panel, -1, "Auto: "+AutoFirmwareType, style=wx.RB_GROUP)
        self.UEFIFirmwareTypeRadioButton = wx.RadioButton(self.Panel, -1, "EFI/UEFI")
        self.BIOSFirmwareTypeRadioButton = wx.RadioButton(self.Panel, -1, "BIOS/Legacy")

    def CreateChoiceBs(self):
        #Make sure the right device's partition scheme is used here.
        tempnum = DeviceList.index(RootDevice)

        #Set up self.PartitionTypeChoice based on whether that value has been changed for this device.
        if PartSchemeList[tempnum] == AutoPartSchemeList[tempnum]:
            self.PartitionTypeChoice = wx.Choice(self.Panel, -1, choices=['Auto: '+PartSchemeList[tempnum], 'msdos', 'gpt'])

        else:
            self.PartitionTypeChoice = wx.Choice(self.Panel, -1, choices=['Auto: '+AutoPartSchemeList[tempnum], 'Manual Value: '+PartSchemeList[tempnum], 'msdos', 'gpt'])  
            self.PartitionTypeChoice.SetSelection(1)     

        #Disable UEFI bootloaders if there is no UEFI system partition.
        if UEFISystemPartition == "None":
            self.BootloaderToInstallChoice = wx.Choice(self.Panel, -1, choices=['Auto', 'GRUB2', 'LILO'])

        else:
            self.BootloaderToInstallChoice = wx.Choice(self.Panel, -1, choices=['Auto', 'GRUB-UEFI', 'GRUB2', 'ELILO', 'LILO'])

        self.BootloaderToInstallChoice.SetSelection(0)
        self.EFISystemPartitionChoice = wx.Choice(self.Panel, -1, choices=["None"]+FatPartitions) #*** Add auto here ***

    def SetDefaults(self):
        global BootloaderToInstall
    
        logger.debug("OptionsWindow2().SetDefaults(): Setting up OptionsWindow2...")
        self.EFISystemPartitionChoice.SetStringSelection(UEFISystemPartition)

        #Check if the dialog has already been run, or if the bootloader setting has changed (so it must discard the setting to avoid errors).
        if BLOptsDlgRun == False or Bootloader != PrevBootloaderSetting:
            #Use defaults.
            self.BootloaderToInstallChoicelastvalue = "Auto"
            #If bootloader is to be reinstalled, updated, or if a UEFI partition isn't available, or if bootloader is grub-legacy, disable some stuff.
            if ReinstallBootloader or UpdateBootloader:
                self.UEFItoBIOSCheckBox.Disable()
                self.BIOStoUEFICheckBox.Disable()
                self.AutoDetermineCheckBox.Disable()
                self.BootloaderToInstallChoice.Disable()
                self.DoNotChangeBootloaderCheckBox.SetValue(True)

            elif UEFISystemPartition == "None":
                self.UEFItoBIOSCheckBox.Disable()
                self.BIOStoUEFICheckBox.Disable()
                self.AutoDetermineCheckBox.Disable()
                self.DoNotChangeBootloaderCheckBox.SetValue(True)

            elif Bootloader == "GRUB-LEGACY":
                self.UEFItoBIOSCheckBox.Disable()
                self.BIOStoUEFICheckBox.Disable()
                self.AutoDetermineCheckBox.Disable()
                self.AutoDetermineCheckBox.SetValue(False)
                self.AutoFirmwareTypeRadioButton.SetValue(True)
                self.DoNotChangeBootloaderCheckBox.SetValue(True)

            else:
                self.UEFItoBIOSCheckBox.Disable()
                self.BIOStoUEFICheckBox.Disable()
                self.AutoDetermineCheckBox.Disable()
                self.AutoDetermineCheckBox.SetValue(False)
                self.DoNotChangeBootloaderCheckBox.SetValue(True)
                self.AutoFirmwareTypeRadioButton.SetValue(True)
                self.UEFIFirmwareTypeRadioButton.SetValue(False)
                self.BIOSFirmwareTypeRadioButton.SetValue(False)
                self.PartitionTypeChoice.SetSelection(0)

        else:
            #Setup using the previous options.
            #First do options that will be set even if the current bootloader is to be reinstalled or updated.
            #Set up Firmware Type radio buttons.
            if FirmwareType == AutoFirmwareType:
                self.UEFIFirmwareTypeRadioButton.SetValue(False)
                self.BIOSFirmwareTypeRadioButton.SetValue(False)
                self.AutoFirmwareTypeRadioButton.SetValue(True)

            elif FirmwareType == "BIOS":
                self.UEFIFirmwareTypeRadioButton.SetValue(False)
                self.BIOSFirmwareTypeRadioButton.SetValue(True)
                self.AutoFirmwareTypeRadioButton.SetValue(False)

            elif FirmwareType == "UEFI":
                self.UEFIFirmwareTypeRadioButton.SetValue(True)
                self.BIOSFirmwareTypeRadioButton.SetValue(False)
                self.AutoFirmwareTypeRadioButton.SetValue(False)

            #Bootloader To Install Choice
            if BootloaderToInstall not in ("None", "Unknown") and ReinstallBootloader == False and UpdateBootloader == False:
                self.BootloaderToInstallChoice.Enable()
                self.BootloaderToInstallChoice.SetStringSelection(BootloaderToInstall)
                self.BootloaderToInstallChoicelastvalue = BootloaderToInstall
                #Insure the window gets updated properly.
                self.BlToInstallChoiceChange()

            elif ReinstallBootloader or UpdateBootloader:
                BootloaderToInstall = "None"
                self.BootloaderToInstallChoice.SetSelection(0)
                self.BootloaderToInstallChoicelastvalue = "Auto"
                #Insure the window gets updated properly.
                self.BlToInstallChoiceChange()
                self.ActivateOptsforNoModification()
                self.BootloaderToInstallChoice.Disable()

            else:
                self.BootloaderToInstallChoicelastvalue = "None"
                self.BootloaderToInstallChoice.SetSelection(0)
                #Insure the window gets updated properly.
                self.BlToInstallChoiceChange()
                self.ActivateOptsforNoModification()

            self.PartitionTypeChoice.SetSelection(0)

        logger.debug("OptionsWindow2().SetDefaults(): OptionsDlg2 Set up!")

    def SetupSizers(self):
        """Setup sizers for bootloader options window"""
        #Create the main sizer.
        MainSizer = wx.BoxSizer(wx.VERTICAL)

        #Create the sizer that holds all the options.
        AllOptionsSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the firmware type options sizer.
        FirmwareOptionsSizer = wx.BoxSizer(wx.VERTICAL)

        #Create the other options sizer.
        OtherOptionsSizer = wx.BoxSizer(wx.VERTICAL)

        #Create the partitioning sizer.
        PartitionSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the bootloader to install sizer.
        BootloaderToInstallSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the UEFI Partition Sizer.
        UEFIPartitionSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the firmware options sizer.
        FirmwareOptionsSizer.Add(self.FirmwareTypeText, 0, wx.TOP|wx.BOTTOM, 10)
        FirmwareOptionsSizer.Add(self.AutoFirmwareTypeRadioButton, 1, wx.BOTTOM, 10)
        FirmwareOptionsSizer.Add(self.UEFIFirmwareTypeRadioButton, 1, wx.BOTTOM, 10)
        FirmwareOptionsSizer.Add(self.BIOSFirmwareTypeRadioButton, 1, wx.BOTTOM, 10)

        #Add items to the partitioning sizer.
        PartitionSizer.Add(self.PartitioningText, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        PartitionSizer.Add(self.PartitionTypeChoice, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to the bootloader to install sizer.
        BootloaderToInstallSizer.Add(self.BootloaderToInstallText, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        BootloaderToInstallSizer.Add(self.BootloaderToInstallChoice, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to the UEFI partition sizer.
        UEFIPartitionSizer.Add(self.UEFIPartitionText, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        UEFIPartitionSizer.Add(self.EFISystemPartitionChoice, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to the other options sizer.
        OtherOptionsSizer.Add(self.OptionsText, 0, wx.TOP|wx.BOTTOM, 10)
        OtherOptionsSizer.Add(PartitionSizer, 1, wx.BOTTOM|wx.EXPAND, 10)
        OtherOptionsSizer.Add(BootloaderToInstallSizer, 1, wx.BOTTOM|wx.EXPAND, 10)
        OtherOptionsSizer.Add(UEFIPartitionSizer, 1, wx.BOTTOM|wx.EXPAND, 10)

        #Add items to the all option sizer.
        AllOptionsSizer.Add(FirmwareOptionsSizer, 1, wx.RIGHT|wx.EXPAND, 5)
        AllOptionsSizer.Add(OtherOptionsSizer, 2, wx.LEFT|wx.EXPAND, 5)

        #Add items to the main sizer.
        MainSizer.Add(AllOptionsSizer, 5, wx.ALL|wx.EXPAND, 10)
        MainSizer.Add(self.UEFItoBIOSCheckBox, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        MainSizer.Add(self.BIOStoUEFICheckBox, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        MainSizer.Add(self.AutoDetermineCheckBox, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        MainSizer.Add(self.DoNotChangeBootloaderCheckBox, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        MainSizer.Add(self.ExitButton, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        #Get the sizer set up for the frame.
        self.Panel.SetSizer(MainSizer)
        MainSizer.SetMinSize(wx.Size(450,330))
        MainSizer.SetSizeHints(self)

    def BindEvents(self):
        self.Bind(wx.EVT_BUTTON, self.CheckOpts, self.ExitButton)
        self.Bind(wx.EVT_CLOSE, self.CheckOpts)
        self.Bind(wx.EVT_CHECKBOX, self.ActivateOptsforNoModification, self.DoNotChangeBootloaderCheckBox)
        self.Bind(wx.EVT_CHOICE, self.BlToInstallChoiceChange, self.BootloaderToInstallChoice)
        self.Bind(wx.EVT_CHOICE, self.UEFISysPChoiceChange, self.EFISystemPartitionChoice) 
        self.Bind(wx.EVT_RADIOBUTTON, self.ActivateOptsforAutoFW, self.AutoFirmwareTypeRadioButton)
        self.Bind(wx.EVT_RADIOBUTTON, self.ActivateOptsforUEFIFW, self.UEFIFirmwareTypeRadioButton)
        self.Bind(wx.EVT_RADIOBUTTON, self.ActivateOptsforBIOSFW, self.BIOSFirmwareTypeRadioButton)

    def ActivateOptsforAutoFW(self, Event=None):
        logger.debug("OptionsWindow2().ActivateOptsForAutoFW() has been triggered...")
        if self.DoNotChangeBootloaderCheckBox.IsChecked() == False and self.BootloaderToInstallChoice.GetSelection() == 0 and ReinstallBootloader == False and UpdateBootloader == False:
            self.UEFItoBIOSCheckBox.SetValue(False)
            self.UEFItoBIOSCheckBox.Disable()
            self.BIOStoUEFICheckBox.SetValue(False)
            self.BIOStoUEFICheckBox.Disable()
            self.AutoDetermineCheckBox.Enable()
            self.AutoDetermineCheckBox.SetValue(True)

    def ActivateOptsforUEFIFW(self, Event=None):
        logger.debug("OptionsWindow2().ActivateOptsForUEFIFW() has been triggered...")
        if self.DoNotChangeBootloaderCheckBox.IsChecked() == False and self.BootloaderToInstallChoice.GetSelection() == 0 and ReinstallBootloader == False and Bootloader != "GRUB-LEGACY" and UpdateBootloader == False:
            self.AutoDetermineCheckBox.SetValue(False)
            self.AutoDetermineCheckBox.Disable()
            self.BIOStoUEFICheckBox.SetValue(True)
            self.BIOStoUEFICheckBox.Enable()
            self.UEFItoBIOSCheckBox.SetValue(False)
            self.UEFItoBIOSCheckBox.Disable()

        elif Bootloader == "GRUB-LEGACY" and self.DoNotChangeBootloaderCheckBox.IsChecked() == False:
            self.AutoDetermineCheckBox.Enable()
            self.AutoDetermineCheckBox.SetValue(True)

    def ActivateOptsforBIOSFW(self, Event=None):
        logger.debug("OptionsWindow2().ActivateOptsForBIOSFW() has been triggered...")
        if self.DoNotChangeBootloaderCheckBox.IsChecked() == False and self.BootloaderToInstallChoice.GetSelection() == 0 and ReinstallBootloader == False and Bootloader != "GRUB-LEGACY" and UpdateBootloader == False:
            self.UEFItoBIOSCheckBox.SetValue(True)
            self.UEFItoBIOSCheckBox.Enable()
            self.AutoDetermineCheckBox.SetValue(False)
            self.AutoDetermineCheckBox.Disable()
            self.BIOStoUEFICheckBox.Disable()
            self.BIOStoUEFICheckBox.SetValue(False)

        elif Bootloader == "GRUB-LEGACY" and self.DoNotChangeBootloaderCheckBox.IsChecked() == False:
            self.AutoDetermineCheckBox.Enable()
            self.AutoDetermineCheckBox.SetValue(True)

    def ActivateOptsforNoModification(self, Event=None):
        logger.debug("OptionsWindow2().ActivateOptsForNoModification() has been triggered...")
        if self.DoNotChangeBootloaderCheckBox.IsChecked() and self.BootloaderToInstallChoice.GetSelection() == 0 and ReinstallBootloader == False and UpdateBootloader == False:
            self.UEFItoBIOSCheckBox.SetValue(False)
            self.UEFItoBIOSCheckBox.Disable()
            self.AutoDetermineCheckBox.SetValue(False)
            self.AutoDetermineCheckBox.Disable()
            self.BIOStoUEFICheckBox.SetValue(False)
            self.BIOStoUEFICheckBox.Disable()

        elif ReinstallBootloader == False and UpdateBootloader == False:
            #In this circumstance, use the correct settings for the current firmware type selected.
            if self.AutoFirmwareTypeRadioButton.GetValue():
                self.ActivateOptsforAutoFW()

            elif self.UEFIFirmwareTypeRadioButton.GetValue():
                self.ActivateOptsforUEFIFW()

            elif self.BIOSFirmwareTypeRadioButton.GetValue():
                self.ActivateOptsforBIOSFW()

        else:
            self.DoNotChangeBootloaderCheckBox.SetValue(True)
            self.UEFItoBIOSCheckBox.SetValue(False)
            self.UEFItoBIOSCheckBox.Disable()
            self.AutoDetermineCheckBox.SetValue(False)
            self.AutoDetermineCheckBox.Disable()
            self.BIOStoUEFICheckBox.SetValue(False)
            self.BIOStoUEFICheckBox.Disable()

    def BlToInstallChoiceChange(self, Event=None):
        logger.debug("OptionsWindow2().BLToInstallChoiceChange() has been triggered...")
        if self.BootloaderToInstallChoice.GetSelection() == 0 and self.BootloaderToInstallChoicelastvalue != self.BootloaderToInstallChoice.GetStringSelection():
            self.BootloaderToInstallChoicelastvalue = self.BootloaderToInstallChoice.GetStringSelection()
            self.DoNotChangeBootloaderCheckBox.Enable()
            self.DoNotChangeBootloaderCheckBox.SetValue(True)
            if self.AutoFirmwareTypeRadioButton.GetValue():
                self.ActivateOptsforAutoFW()

            elif self.UEFIFirmwareTypeRadioButton.GetValue():
                self.ActivateOptsforUEFIFW()

            elif self.BIOSFirmwareTypeRadioButton.GetValue():
                self.ActivateOptsforBIOSFW()

        elif self.BootloaderToInstallChoice.GetSelection() != 0:
            self.BootloaderToInstallChoicelastvalue = self.BootloaderToInstallChoice.GetStringSelection()
            self.UEFItoBIOSCheckBox.SetValue(False)
            self.UEFItoBIOSCheckBox.Disable()
            self.AutoDetermineCheckBox.SetValue(False)
            self.AutoDetermineCheckBox.Disable()
            self.BIOStoUEFICheckBox.SetValue(False)
            self.BIOStoUEFICheckBox.Disable()
            self.DoNotChangeBootloaderCheckBox.SetValue(False)
            self.DoNotChangeBootloaderCheckBox.Disable()

    def UEFISysPChoiceChange(self, Event=None):
        #Function to handle selection of new UEFI system partition. It's pretty self-explanatory.
        global UEFISystemPartition
        logger.debug("OptionsWindow2().UEFISysPChoiceChange() has been triggered...")
        if self.EFISystemPartitionChoice.GetStringSelection() == UEFISystemPartition:
            logger.debug("OptionsWindow2().UEFISysPChoiceChange(): No action required, UEFISystemPartition unchanged...")

        elif self.EFISystemPartitionChoice.GetStringSelection() == "None":
            logger.debug("OptionsWindow2().UEFISysPChoiceChange(): UEFISystemPartition changed to None. Disabling UEFI Bootloader installation, rescanning for bootloaders, and exiting OptionsWindow2()...")
            UEFISystemPartition = self.EFISystemPartitionChoice.GetStringSelection()

            wx.MessageDialog(self.Panel, "As you have selected no UEFI partition, WxFixBoot will disable UEFI bootloaders. Please wait a few seconds while your system is scanned for bootloaders. If none are found, you will be prompted to enter one manually. After that, you will be returned to the first options window with any new bootloader settings detected. Any other settings you have set here will be ignored, unless you go back and set them again.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

            self.Hide()

            #Check for bootloaders on the suggested UEFI partition.
            InitThread(self, False)

        else:
            logger.debug("OptionsWindow2().UEFISysPChoiceChange(): UEFISystemPartition changed! Rescanning for UEFI bootloaders and exiting OptionsWindow2()...")
            UEFISystemPartition = self.EFISystemPartitionChoice.GetStringSelection()

            wx.MessageDialog(self.Panel, "You have selected a different UEFI Partition. Please wait a few seconds while it is scanned for bootloaders. If none are found, you will be prompted to enter one manually. After that, you will be returned to the first options window with any new bootloader settings detected. Any other settings you have set here will be ignored, unless you go back and set them again.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

            self.Hide()

            #Check for bootloaders on the suggested UEFI partition.
            InitThread(self, False)

    def UEFIPartitionScanned(self,msg):
        #Okay, the UEFI partition has been scanned, and the bootloader has been set, either manually or automatically.
        #Send a message to OptionsDlg1, so it can show itself again.
        wx.CallAfter(self.ParentWindow.RefreshOptionsDlg1, "Closed.")

        #Exit.
        self.Destroy()

    def CheckOpts(self, Event=None):
        if self.DoNotChangeBootloaderCheckBox.IsChecked() == False and self.UEFItoBIOSCheckBox.IsChecked() == False and self.AutoDetermineCheckBox.IsChecked() == False and self.BIOStoUEFICheckBox.IsChecked() == False and self.BootloaderToInstallChoice.GetSelection() == 0:
            #Do nothing, as settings are invalid.
            logger.error("OptionsWindow2().CheckOpts(): No options selected, although the 'do not modify' checkbox is unticked, or the options selected are invalid. Won't save options, waitng for user change...")
            wx.MessageDialog(self.Panel, "Your current selection suggests a modification will take place, but it doesn't specify which modification to do! Please select a valid modification to do.", "WxFixBoot - Error", style=wx.OK | wx.ICON_ERROR, pos=wx.DefaultPosition).ShowModal()

        else:
            self.SaveBLOpts()

    def SaveBLOpts(self):
        #Save all selected Operations here.
        global BootloaderToInstall
        global PrevBootloaderSetting
        global PartSchemeList
        global Bootloader
        global FirmwareType
        global AutoFirmwareType

        logger.info("OptionsWindow2().SaveBLOpts(): Saving Options...")

        BootloaderList = ('GRUB-LEGACY', 'GRUB-UEFI','GRUB2','ELILO','LILO')

        #Partition scheme choice.
        if self.PartitionTypeChoice.GetStringSelection()[0:6] == "Manual":
            #No action required.
            logger.info("OptionsWindow2().SaveBLOpts(): No Change in any PartScheme values...")

        else:
            #Figure out which entry in PartSchemeList to change and then delete and recreate it using the options in the dlg (msdos, or gpt)
            tempnum = DeviceList.index(RootDevice)
            PartSchemeList.pop(tempnum)
            PartSchemeList.insert(tempnum, self.PartitionTypeChoice.GetStringSelection().split()[-1])
            if self.PartitionTypeChoice.GetStringSelection()[0:4] != "Auto":
                logger.info("OptionsWindow2().SaveBLOpts(): Changed value of PartScheme for device: "+RootDevice+" to: "+PartSchemeList[tempnum])

            else:
                logger.info("OptionsWindow2().SaveBLOpts(): Changed value of PartScheme for device: "+RootDevice+" to: "+PartSchemeList[tempnum]+" the default...")

        #Firmware Choice.
        if self.UEFIFirmwareTypeRadioButton.GetValue():
            FirmwareType = "UEFI"

        elif self.BIOSFirmwareTypeRadioButton.GetValue():
            FirmwareType = "BIOS"

        else:
            #Use auto value.
            FirmwareType = AutoFirmwareType

        logger.info("OptionsWindow2().SaveBLOpts(): Value of FirmwareType is: "+FirmwareType)

        #Bootloader to install choice.
        #Offer some warnings here if needed. This is a little complicated, but is still fairly easy to read.
        if self.BootloaderToInstallChoice.GetStringSelection()[0:4] == "Auto" and ReinstallBootloader == False:
            #Use autodetect value
            if self.DoNotChangeBootloaderCheckBox.IsChecked() == False:

                if self.UEFItoBIOSCheckBox.IsChecked():

                    if Bootloader in ('GRUB-UEFI', 'ELILO'):
                        #Find the BIOS/MBR equivalent to a UEFI bootloader.
                        bootloadernum = BootloaderList.index(Bootloader)
                        BootloaderToInstall = BootloaderList[bootloadernum+1]

                    else:
                        #Do nothing, already using BIOS bootloader.
                        wx.MessageDialog(self.Panel, "Your current bootloader already supports your firmware type, so it won't be modified based on your firmware. If you wish to, you can install an alternative bootloader with this window, or reinstall the bootoader using the selection in the main window.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()
                        BootloaderToInstall = "None"

                elif self.BIOStoUEFICheckBox.IsChecked():

                    if UEFISystemPartition != "None" and Bootloader in ('GRUB2', 'LILO'):

                        #Find the EFI/UEFI equivalent to a BIOS bootloader, provided there is a UEFI partition.
                        bootloadernum = BootloaderList.index(Bootloader)
                        BootloaderToInstall = BootloaderList[bootloadernum-1]

                    elif UEFISystemPartition == "None":
                        #Refuse to install a UEFI bootloader, as there is no UEFI partition.
                        wx.MessageDialog(self.Panel, "Your current bootloader to install requires a UEFI partition, which either doesn't exist or has not been selected. Please create or select a UEFI partition to install a UEFI bootloader or the operation will be cancelled.", "WxFixBoot - Error", style=wx.OK | wx.ICON_ERROR, pos=wx.DefaultPosition).ShowModal()
                        BootloaderToInstall = "None"

                    else:
                        #Do nothing, already using EFI/UEFI bootloader.
                        wx.MessageDialog(self.Panel, "Your current bootloader already supports your firmware type, so it won't be modified based on your firmware. If you wish to, you can install an alternative bootloader with this window, or reinstall the bootoader using the selection in the main window.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()
                        BootloaderToInstall = "None"

                elif self.AutoDetermineCheckBox.IsChecked():

                    bootloadernum = BootloaderList.index(Bootloader)

                    if FirmwareType == "BIOS" and Bootloader not in ('GRUB2', 'LILO', 'GRUB-LEGACY'):
                        #Find the BIOS/MBR equivalent to a UEFI bootloader.
                        BootloaderToInstall = BootloaderList[bootloadernum+1]

                    elif FirmwareType == "UEFI" and Bootloader not in ('GRUB-UEFI', 'ELILO', 'GRUB-LEGACY') and UEFISystemPartition != "None":
                        #Find the EFI/UEFI equivalent to a BIOS bootloader, provided there is a UEFI partition, and it isn't GRUB-LEGACY
                        BootloaderToInstall = BootloaderList[bootloadernum-1]

                    elif FirmwareType == "BIOS" and Bootloader == "GRUB-LEGACY":
                        #Recommend GRUB2 for BIOS systems using GRUB-LEGACY
                        dlg = wx.MessageDialog(self.Panel, 'Seeing as your bootloader is grub legacy, and you use BIOS firmware, the recommended bootloader for your hardware is GRUB2. If you want to install a different bootloader, click no and return to this window to manually select your bootloader. Click yes to comfirm installing GRUB2.', 'WxFixBoot -- Comfirmation', wx.YES_NO | wx.ICON_QUESTION).ShowModal()
                        if dlg == wx.ID_YES:
                            BootloaderToInstall = "GRUB2"
                        else:
                            #Do nothing
                            BootloaderToInstall = "None"

                    elif FirmwareType == "UEFI" and Bootloader == "GRUB-LEGACY":
                        #Suggest GRUB-UEFI for UEFI systems using GRUB-LEGACY
                        wx.MessageDialog(self.Panel, "You have a combination of UEFI firmware and grub legacy. This is an odd combination, and WxFixBoot doesn't know what to do. If you've imaged your HDD from another system, you probably want to install GRUB-UEFI manually by returning to this window after it closes. If you manually suggested you have grub legacy earlier, please double check that was correct.", "WxFixBoot - Warning!", style=wx.OK | wx.ICON_WARNING, pos=wx.DefaultPosition).ShowModal()
                        BootloaderToInstall = "Unknown"

                    elif FirmwareType == "UEFI" and UEFISystemPartition == "None":
                        #Refuse to install a UEFI bootloader, as there is no UEFI partition.
                        wx.MessageDialog(self.Panel, "Your current bootloader to install requires a UEFI partition, which either doesn't exist or has not been selected. Please create or select a UEFI partition to install a UEFI bootloader or the operation will be cancelled.", "WxFixBoot - Error", style=wx.OK | wx.ICON_ERROR, pos=wx.DefaultPosition).ShowModal()
                        BootloaderToInstall = "None"

                    else:
                        #Correct bootloader for firmware type.
                        BootloaderToInstall = "None"
                        wx.MessageDialog(self.Panel, "Your current bootloader already supports your firmware type, so it won't be modified based on your firmware. If you wish to, you can install an alternative bootloader with this window, or reinstall the bootoader using the selection in the main window.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

            else:
                #Do nothing.
                BootloaderToInstall = "None"

        elif self.DoNotChangeBootloaderCheckBox.IsChecked() == False and ReinstallBootloader == False and UpdateBootloader == False:
            BootloaderToInstall = self.BootloaderToInstallChoice.GetStringSelection()

        else:
            BootloaderToInstall = "None"

        if BootloaderToInstall == Bootloader:
            BootloaderToInstall = "None"
            wx.MessageDialog(self.Panel, "Your current bootloader is the same as the one you've selected to install! Please select 'Reinstall Bootloader' in the Main Window instead.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        if BootloaderToInstall in ('LILO', 'ELILO'):  
            wx.MessageDialog(self.Panel, "Either, you've selected or WxFixBoot has autodetermined to use LILO or ELILO as the bootloader to install! Both ELILO and LILO can be a complete pain to set up and maintain. Please do not use either unless you know how to set up and maintain them, and you're sure you want them. If WxFixBoot recommended either of them to you, it's a good idea to select the equivalent GRUB version manually instead: GRUB-UEFI for ELILO, GRUB2 for LILO.", "WxFixBoot - Warning", style=wx.OK | wx.ICON_WARNING, pos=wx.DefaultPosition).ShowModal()

            if GPTInAutoPartSchemeList and BootloaderToInstall == "LILO":
                wx.MessageDialog(self.Panel, "LILO is going to be installed, but at least one device connected to this computer uses an incompatble partition system! LILO will not boot from that device, so this may be a bad idea, in case you boot from it. Please consider installing GRUB2 instead as it will boot from that device.", "WxFixBoot - Warning", style=wx.OK | wx.ICON_WARNING, pos=wx.DefaultPosition).ShowModal()

        #Avoid an error situation.
        PrevBootloaderSetting = Bootloader

        logger.info("OptionsWindow2().SaveBLOpts(): Value of BootloaderToInstall is: "+BootloaderToInstall)
        logger.info("OptionsWindow2().SaveBLOpts(): Finished saving options.")

        self.CloseBLOpts()
        
    def CloseBLOpts(self):
        logger.debug("OptionsWindow2().CloseBLOpts(): OptionsWindow2 Closing.")
        #Save that this window has been run once, so it can update itself with the new info if it's started again.
        global BLOptsDlgRun
        BLOptsDlgRun = True

        #Send a message to OptionsDlg1, so it can show itself again.
        wx.CallAfter(self.ParentWindow.RefreshOptionsDlg1, "Closed.")

        #Exit.
        self.Destroy()

#End Options window 2
#Begin Restore Window
class RestoreWindow(wx.Frame):
    def __init__(self,ParentWindow,Type):
        if Type == "BootSector":
            logger.debug("RestoreWindow().__init__(): Restore Boot Sector Window Started.")
            title = "WxFixBoot - Restore the Boot Sector"
        else:
            logger.debug("RestoreWindow().__init__(): Restore Partition Table Window Started.")
            title = "WxFixBoot - Restore the Partition Table"

        wx.Frame.__init__(self, parent=wx.GetApp().TopWindow, title=title, size=(400,200), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.RestorePanel = wx.Panel(self)
        self.SetClientSize(wx.Size(400,200))
        self.ParentWindow = ParentWindow
        self.Type = Type
        wx.Frame.SetIcon(self, AppIcon)

        #Save the frame's width and height, making it easier to centre text.
        self.width, self.height = self.GetSizeTuple()

        self.CreateText()
        self.CreateRadios()
        self.CreateChoiceBs()
        self.CreateButtons()
        self.BindEvents()

        #Set up the window.
        self.SetupOptions()

    def CreateText(self):
        #Create text, and centre it.
        if self.Type == "BootSector":
            wx.StaticText(self.RestorePanel, -1, "What type of Boot Sector backup do you have?", pos=(10,40))
            wx.StaticText(self.RestorePanel, -1, "Easily restore your bootsector here!", pos=(10,10))

        else:
            wx.StaticText(self.RestorePanel, -1, "What type of partition table backup do you have?", pos=(10,40))
            wx.StaticText(self.RestorePanel, -1, "Easily restore your partition table here!", pos=(10,10))

        wx.StaticText(self.RestorePanel, -1, "Backup file:", pos=(10,100))
        wx.StaticText(self.RestorePanel, -1, "Target Device:", pos=(230,100))

    def CreateRadios(self):
        #Create Radio Buttons
        self.autodetectradio = wx.RadioButton(self.RestorePanel, -1, "Autodetect", pos=(10,70), style=wx.RB_GROUP)
        self.msdosradio = wx.RadioButton(self.RestorePanel, -1, "MBR(msdos)", pos=(150,70))
        self.gptradio = wx.RadioButton(self.RestorePanel, -1, "GUID(gpt)", pos=(290,70))  

    def CreateChoiceBs(self):
        #Create ChoiceBoxes
        self.filechoice = wx.Choice(self.RestorePanel, -1, pos=(10,120), size=(150,30), choices=['-- Please Select --', 'Specify File Path...'])
        self.targetchoice = wx.Choice(self.RestorePanel, -1 , pos=(230,120), size=(150,30), choices=['-- Please Select --', 'Auto: '+AutoRootDevice]+DeviceList+['Specify Path...'])

    def CreateButtons(self):
        #Create Buttons
        self.ExitButton = wx.Button(self.RestorePanel, -1, "Close and Set Options", pos=(120,160))

    def BindEvents(self):
        #Bind events
        self.Bind(wx.EVT_BUTTON, self.ExitWindow, self.ExitButton)
        self.Bind(wx.EVT_CLOSE, self.ExitWindow)
        self.Bind(wx.EVT_CHOICE, self.SelectFile, self.filechoice)
        self.Bind(wx.EVT_CHOICE, self.SelectTargetDevice, self.targetchoice)

    def SetupOptions(self):
        #Set up the choiceboxes according to the values of the variables.
        if self.Type == "BootSector":
            File = BootSectorFile
            TargetDevice = BootSectorTargetDevice
        else:
            File = PartitionTableFile
            TargetDevice = PartitionTableTargetDevice

        #Image file choice.
        if File != "None":
            self.filechoice.Append(File)
            self.filechoice.SetStringSelection(File)
        else:
            self.filechoice.SetSelection(0)

        #Target device file choice.
        if TargetDevice != "None":
            self.targetchoice.Append(TargetDevice)
            self.targetchoice.SetStringSelection(TargetDevice)
        else:
            self.targetchoice.SetSelection(0)

    def SelectFile(self, Event=None):
        #Grab Image path.
        logger.debug("RestoreWindow().SelectFile() has been triggered...")

        #Set up global variables.
        global BootSectorFile
        global RestoreBootSector
        global BootSectorBackupType
        global PartitionTableFile
        global RestorePartitionTable
        global PartitionTableBackupType

        File = self.filechoice.GetStringSelection()

        #Determine what to do here.
        if File == "-- Please Select --":
            File = "None"
            Restore = False

        elif File == "Specify File Path...":
            if self.Type == "BootSector":
                Dlg = wx.FileDialog(self.RestorePanel, "Select Boot Sector File...", wildcard="All Files/Devices (*)|*|GPT Backup File (*.gpt)|*.gpt|MBR Backup File (*.mbr)|*.mbr|IMG Image file (*.img)|*.img", style=wx.OPEN)
            else:
                Dlg = wx.FileDialog(self.RestorePanel, "Select Partition Table File...", wildcard="All Files/Devices (*)|*|GPT Backup File (*.gpt)|*.gpt|MBR Backup File (*.mbr)|*.mbr|IMG Image file (*.img)|*.img", style=wx.OPEN)

            if Dlg.ShowModal() == wx.ID_OK:
                Restore = True
                File = Dlg.GetPath()
                self.filechoice.Append(File)
                self.filechoice.SetStringSelection(File)
            else:
                File = "None"
                Restore = False
                self.filechoice.SetStringSelection("-- Please Select --")

        else:
            File = self.filechoice.GetStringSelection()
            Restore = True

        #Detect backup type, if files are selected.
        if File != "None" and Restore:
            #Use os.stat(filename).st_size, if bigger than 512 bytes (MBR bootsector), it's GPT
            Temp = os.stat(File).st_size
            if Temp < 512:
                #Bad file.
                wx.MessageDialog(self.RestorePanel, "The size of the selected file is less than 512 bytes! This is cannot be a backup file. Please select a new backup file.", "WxFixBoot - Error", style=wx.OK | wx.ICON_ERROR, pos=wx.DefaultPosition).ShowModal()
                File = "None"
                Restore = "False"
                BackupType = "None"
                self.autodetectradio.SetValue(True)
                Temp = self.filechoice.GetSelection()
                self.filechoice.Delete(Temp)
                self.filechoice.SetStringSelection("-- Please Select --")
                return
            elif Temp == 512:
                #Backup is MBR(msdos)
                BackupType = "msdos"
                self.msdosradio.SetValue(True)
            elif Temp > 512 and Temp < 20000:
                #Backup is GPT  
                BackupType = "gpt"
                self.gptradio.SetValue(True)
            else:
                #Backup is *PROBABLY* GPT, but might not be a backup file! If this is the BootSector, it's fine, because for that we backup the UEFI partition.
                BackupType = "gpt"
                self.gptradio.SetValue(True)
                if self.Type == "PartTable":
                    wx.MessageDialog(self.RestorePanel, "Your backup file type is probably valid, but WxFixBoot isn't sure, as the file size is odd. Please ensure that this is your backup file!", "WxFixBoot - Warning", style=wx.OK | wx.ICON_WARNING, pos=wx.DefaultPosition).ShowModal()

            wx.MessageDialog(self.RestorePanel, "Your backup file type was detected as: "+BackupType+". If this is correct, then continuing is safe. If not, ensure you made the backup file with WxFixBoot and that it is the correct backup file, and manually set the right backup type. If you made the backup with another program, please use that program to restore it instead to avoid problems.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition).ShowModal()

        else:
            BackupType = "None"
            self.autodetectradio.SetValue(True)

        #Save File, Restoring, and BackupType to the correct global variables, depending on which purpose this class is serving (Boot Sector Restoration Window, or Partition Table Restoration Window).
        logger.info("RestoreWindow().SelectFile(): Current config: File = "+File+", Restore = "+unicode(Restore)+", BackupType = "+BackupType+"...")

        if self.Type == "BootSector":
            BootSectorFile = File
            RestoreBootSector = Restore
            BootSectorBackupType = BackupType
        else:
            PartitionTableFile = File
            RestorePartitionTable = Restore
            PartitionTableBackupType = BackupType

    def SelectTargetDevice(self, Event=None):
        #Grab Boot Sector Image path.
        logger.debug("RestoreWindow().SelectTargetDevice() has been triggered...")

        #Set up global variables.
        global BootSectorTargetDevice
        global PartitionTableTargetDevice

        TargetDevice = self.targetchoice.GetStringSelection()

        #Determine what to do here.
        if TargetDevice == "-- Please Select --":
            TargetDevice = "None"
        elif TargetDevice[0:4] == "Auto":
            TargetDevice = RootDevice
        elif TargetDevice == "Specify File Path...":
            Dlg = wx.FileDialog(self.RestorePanel, "Select Target Device...", wildcard="All Files/Devices (*)|*", defaultDir='/dev', style=wx.OPEN)
            if Dlg.ShowModal() == wx.ID_OK:
                TargetDevice = Dlg.GetPath()
                self.targetchoice.Append(TargetDevice)
                self.targetchoice.SetStringSelection(TargetDevice)
            else:
                TargetDevice = "None"
                self.targetchoice.SetStringSelection("-- Please Select --")
        else:
            TargetDevice = self.targetchoice.GetStringSelection()

        #Save TargetDevice to the correct global variable, depending on which purpose this class is serving (Boot Sector Restoration Window, or Partition Table Restoration Window).
        logger.info("RestoreWindow().SelectTargetDevice(): Current config: TargetDevice = "+TargetDevice+"...")

        if self.Type == "BootSector":
            BootSectorTargetDevice = TargetDevice
        else:
            PartitionTableTargetDevice = TargetDevice

    def ExitWindow(self, Event=None):
        if self.Type == "BootSector":
            File = BootSectorFile
            Restore = RestoreBootSector
            TargetDevice = BootSectorTargetDevice
        else:
            File = PartitionTableFile
            Restore = RestorePartitionTable
            TargetDevice = PartitionTableTargetDevice

        if File != "None" and Restore and TargetDevice != "None":
            #Show an info message.
            dlg = wx.MessageDialog(self.RestorePanel, "Do you want to continue? This operation can cause data loss. Only continue if you are certain you've selected the right target device and backup file, and if the backup was created with WxFixBoot. If you restore a partition table or bootsector some options, such as installing a different bootloader and reinstalling or updating your bootloader will be disabled. If you want to change other settings, you can always restart WxFixBoot afterwards and then change them.", "WxFixBoot - Information", style=wx.YES_NO | wx.ICON_EXCLAMATION, pos=wx.DefaultPosition)
            if dlg.ShowModal() == wx.ID_YES:
                #Send a message to OptionsDlg1, so it can show itself again.
                wx.CallAfter(self.ParentWindow.RefreshOptionsDlg1, "Closed.")

                #Exit.
                self.Destroy()

        elif File != "None" or Restore or TargetDevice != "None":
            if self.Type == "Bootsector":
                wx.MessageDialog(self.RestorePanel, "You haven't entered all of the required settings! Please either enter all required settings to do this operation, or no settings at all to disable boot sector resoration.", "WxFixBoot - Warning", style=wx.OK | wx.ICON_WARNING, pos=wx.DefaultPosition).ShowModal()

            else:
                wx.MessageDialog(self.RestorePanel, "You haven't entered all of the required settings! Please either enter all required settings to do this operation, or no settings at all to disable partition table restoration.", "WxFixBoot - Warning", style=wx.OK | wx.ICON_WARNING, pos=wx.DefaultPosition).ShowModal()

        else:
            dlg = wx.MessageDialog(self.RestorePanel, "Do you want to exit this window?", "WxFixBoot - Information", style=wx.YES_NO | wx.ICON_EXCLAMATION, pos=wx.DefaultPosition)

            if dlg.ShowModal() == wx.ID_YES:
                logger.debug("RestoreWindow().ExitWindow(): Restore Boot Sector/Partion Table Window Closing.")
                #Send a message to OptionsDlg1, so it can show itself again.
                wx.CallAfter(self.ParentWindow.RefreshOptionsDlg1, "Closed.")

                #Exit.
                self.Destroy()

#End Restore Window
#Begin Progress Window
class ProgressWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="WxFixBoot - Operations Progress", size=(500,300), style=wx.CAPTION|wx.MINIMIZE|wx.RESIZE_BORDER)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(500,300))
        wx.Frame.SetIcon(self, AppIcon)

        #Save the frame's width and height, making it easier to centre text.
        self.width, self.height = self.GetSizeTuple()

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
        logger.debug("ProgressWindow().__init__(): Starting Main Backend Thread...")

        MainBackendThread(self)

    def CreateText(self):
        #Create Text, and centre it.
        self.PerformingOperationsText = wx.StaticText(self.Panel, -1, "WxFixBoot is performing operations... Please wait.")
        self.CurrentOperationHeadingText = wx.StaticText(self.Panel, -1, "Current Operation:")
        self.CurrentOperationText = wx.StaticText(self.Panel, -1, "Initializating...")
        self.CurrentOperationProgressText = wx.StaticText(self.Panel, -1, "Current Operation Progress:")
        self.OverallProgressText = wx.StaticText(self.Panel, -1, "Overall Progress:")

    def CreateButtons(self):
        #Create buttons.
        self.ShowOutputButton = wx.ToggleButton(self.Panel, -1, "Show Terminal Output")
        self.RestartButton = wx.Button(self.Panel, -1, "Restart WxFixBoot")
        self.ExitButton = wx.Button(self.Panel, -1, "Exit")
        self.RestartButton.Disable()
        self.ExitButton.Disable()

    def CreateProgressBars(self):
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
        self.Bind(wx.EVT_TOGGLEBUTTON, self.ShowOutput, self.ShowOutputButton)
        self.Bind(wx.EVT_BUTTON, self.RestartWxFixBoot, self.RestartButton)
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.ExitButton)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def ShowOutput(self, Event=None):
        """Show and Hide the output box in ProgressWindow()"""
        logger.debug("ProgressWindow().ShowOutput() was Toggled to position: "+unicode(self.ShowOutputButton.GetValue())+", where True = Depressed and vice versa.")
        if self.ShowOutputButton.GetValue() == True: #*** Including == True for readability ***
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

    def UpdateOutputBox(self,msg):
        """Adds a line of text to the output box""" #*** Add output box stuff from ddrescue-gui v1.5***
        self.OutputBox.AppendText(msg)

    def UpdateCurrentProgress(self,msg):
        #Do current progress.
        #Called at various points during operation code.
        self.CurrentOperationProgressBar.SetValue(int(msg))
        if self.CurrentOperationProgressBar.GetValue() == 100:
            self.UpdateTotalProgress()
            #Stop this resetting when all operations are complete.
            if self.OverallProgressBar.GetValue() != 100:
                self.CurrentOperationProgressBar.SetValue(0)

    def UpdateTotalProgress(self):
        #Do total progress.
        #This is called when self.CurrentOperationProgressBar reaches 100 (aka full).
        if self.OverallProgressBar.GetValue() < 100:
            self.OverallProgressBar.SetValue(self.OverallProgressBar.GetValue()+(100/NumberOfOperationsToDo))

    def UpdateCurrentOpText(self, Message):
        #Function to keep the current operations status text up to date.
        self.CurrentOperationText.SetLabel(Message)
        self.Panel.Layout()

    def MainBackendThreadFinished(self):
        self.RestartButton.Enable()
        self.ExitButton.Enable()

    def RestartWxFixBoot(self, Event=None):
        #Restart WxFixBoot
        logger.debug("ProgressWindow().RestartWxFixBoot(): Restarting WxFixBoot...")
        self.Hide()

        #Reset all settings to defaults, except ones like LiveDisk, which won't ever need to change.
        SetDefaults()

        global Bootloader
        global FirmwareType
        global RootFS
        global RootDevice
        global DefaultOS
        global PartScheme
        global UEFISystemPartition

        Bootloader = AutoBootloader
        FirmwareType = AutoFirmwareType
        RootFS = AutoRootFS
        RootDevice = AutoRootDevice
        DefaultOS = AutoDefaultOS
        PartSchemeList = AutoPartSchemeList
        UEFISystemPartition = AutoUEFISystemPartition

        #Show MainWindow
        MainFrame = MainWindow()
        app.SetTopWindow(MainFrame)
        MainFrame.Show(True)

        #Destroy Progress Window.
        logger.debug("ProgressWindow().RestartWxFixBoot(): WxFixBoot has been reset and restarted, returning to MainWindow()")
        self.Destroy()

    def OnExit(self, Event=None): #*** Add logfile moving stuff here ***
        #No need to check if operations are running, the button isn't clickable if any are.
        exitdlg = wx.MessageDialog(self.Panel, 'Are you sure you want to exit?', 'WxFixBoot -- Question!', wx.YES_NO | wx.ICON_QUESTION).ShowModal()
        if exitdlg == wx.ID_YES:
            #Run the exit sequence
            logger.debug("ProgressWindow().OnExit(): User triggered exit sequence. Exiting...")
            if os.path.isdir("/tmp/wxfixboot"):
                shutil.rmtree('/tmp/wxfixboot')
            self.Destroy()

#End Progress Window
#Begin Main Backend Thread
class MainBackendThread(threading.Thread):
    def __init__(self, ParentWindow):
        """Initialize MainBackendThread"""
        #Set up the backend tools.
        Tools.dialogtools.ParentWindow = ParentWindow
        Tools.BackendTools.core.ParentWindow = ParentWindow
        Tools.BackendTools.helpers.ParentWindow = ParentWindow
        Tools.BackendTools.essentials.ParentWindow = ParentWindow
        Tools.BackendTools.BootloaderTools.main.ParentWindow = ParentWindow
        Tools.BackendTools.BootloaderTools.getconfigtools.ParentWindow = ParentWindow
        Tools.BackendTools.BootloaderTools.removaltools.ParentWindow = ParentWindow

        #Start the main part of this thread.
        threading.Thread.__init__(self)
        self.ParentWindow = ParentWindow
        self.start()

    def run(self):
        #Do setup
        self.templog = [] #*** Do we need this? ***
        time.sleep(1)

        #*** Temporarily do this until I switch to dictionaries ***
        #Define global vars
        global BootloaderTimeout
        global KernelOptions

        #Set to default values
        BootloaderTimeout = 10
        KernelOptions = "quiet splash nomodeset"
 
        #Log the MainBackendThread start event (in debug mode).
        logger.debug("MainBackendThread().run(): Started. Calculating Operations to do...")

        self.CountOperations()
        self.StartOperations()

    def CountOperations(self):
        #Count the number of operations to do. *** Check this before going to progress window ***
        global NumberOfOperationsToDo

        #List to contain operations (and their functions) to run.
        self.OperationsToDo = []

        #Run a series of if statements to determine what operations to do, which order to do them in, and the total number to do.
        #Do essential processes first.
        if BackupPartitionTable:
            self.OperationsToDo.append(EssentialBackendTools().BackupPartitionTable)            
            logger.info("MainBackendThread().CountOperations(): Added EssentialBackendTools().BackupPartitionTable to self.OperationsToDo...")

        if BackupBootSector:
            self.OperationsToDo.append(EssentialBackendTools().BackupBootSector)
            logger.info("MainBackendThread().CountOperations(): Added EssentialBackendTools().BackupBootSector to self.OperationsToDo...")

        if RestorePartitionTable:
            self.OperationsToDo.append(EssentialBackendTools().RestorePartitionTable)
            logger.info("MainBackendThread().CountOperations(): Added EssentialBackendTools().RestorePartitionTable to self.OperationsToDo...")

        if RestoreBootSector:
            self.OperationsToDo.append(EssentialBackendTools().RestoreBootSector)
            logger.info("MainBackendThread().CountOperations(): Added EssentialBackendTools().RestoreBootSector to self.OperationsToDo...")

        if QuickFSCheck:
            self.OperationsToDo.append(EssentialBackendTools().QuickFileSystemCheck)
            logger.info("MainBackendThread().CountOperations(): Added EssentialBackendTools().QuickFileSystemCheck to self.OperationsToDo...")

        if BadSectCheck:
            self.OperationsToDo.append(EssentialBackendTools().BadSectorCheck)
            logger.info("MainBackendThread().CountOperations(): Added EssentialBackendTools().BadSectorCheck to self.OperationsToDo...")

        #Now do other processes
        if BootloaderToInstall != "None":
            self.OperationsToDo.append(MainBootloaderTools().ManageBootloaders)
            logger.info("MainBackendThread().CountOperations(): Added MainBootloaderTools().ManageBootloaders to self.OperationsToDo...")

        if ReinstallBootloader:
            self.OperationsToDo.append(MainBootloaderTools().ReinstallBootloader)
            logger.info("MainBackendThread().CountOperations(): Added MainBootloaderTools().ReinstallBootloader to self.OperationsToDo...")

        if UpdateBootloader:
            self.OperationsToDo.append(MainBootloaderTools().UpdateBootloader)
            logger.info("MainBackendThread().CountOperations(): Added MainBootloaderTools().UpdateBootloader to self.OperationsToDo...")

        #Check if we need to prepare to install a new bootloader, and do so first if needed. *** Log this ***
        for element in (MainBootloaderTools().ManageBootloaders, MainBootloaderTools().ReinstallBootloader, MainBootloaderTools().UpdateBootloader):
            if element in self.OperationsToDo:
                self.OperationsToDo.insert(0, MainBootloaderTools().PrepareForBootloaderInstallation) #*** Don't insert this before the essential operations ***

        NumberOfOperationsToDo = len(self.OperationsToDo)

        #Log gathered operations to do, and the number (verbose mode, default).
        logger.info("MainBackendThread().CountOperations(): Number of operations: "+unicode(NumberOfOperationsToDo))
        logger.info("MainBackendThread().CountOperations(): Starting Operation Running Code...")

    def StartOperations(self):
        #Start doing operations.
        if NumberOfOperationsToDo == 0:
            DialogTools().ShowMsgDlg(Kind="error", Message="You didn't select any operations! Please restart WxFixBoot to select any operations you wish to perform.")

        else:
            DialogTools().ShowMsgDlg(Kind="info", Message="Please stay within sight of the system, as operations are not fully automated and you may be asked the occasional queston, or be shown warnings. You may also see the occasional file manager dialog pop up as well, so feel free to either close them or ignore them.")

            #Run functions to do operations. *** Some of these might not work correctly until switch to dictionaries even ith the extra code after running the function ***
            for function in self.OperationsToDo:
                #*** Extra temporary stuff needed to make things work for the time being until we switch to dictionaries (Set vars inside modules) ***
                #*** We temporarily neeed global declarations in modules to make sure the global variables are set right, when they aren't directly passed to the functions within ***
                #*** Essential backend tools ***
                Tools.BackendTools.essentials.RootDevice = RootDevice
                Tools.BackendTools.essentials.DeviceList = DeviceList
                Tools.BackendTools.essentials.PartSchemeList = PartSchemeList
                Tools.BackendTools.essentials.PartitionTableFile = PartitionTableFile
                Tools.BackendTools.essentials.PartitionTableBackupType = PartitionTableBackupType
                Tools.BackendTools.essentials.PartitionTableTargetDevice = PartitionTableTargetDevice
                Tools.BackendTools.essentials.BootSectorFile = BootSectorFile
                Tools.BackendTools.essentials.BootSectorBackupType = BootSectorBackupType
                Tools.BackendTools.essentials.BootSectorTargetDevice = BootSectorTargetDevice
                Tools.BackendTools.essentials.UEFISystemPartition = UEFISystemPartition
                Tools.BackendTools.essentials.PartitionListWithFSType = PartitionListWithFSType
                Tools.BackendTools.essentials.LiveDisk = LiveDisk
                Tools.BackendTools.essentials.AutoRootFS = AutoRootFS
                Tools.BackendTools.essentials.OSsForBootloaderRemoval = OSsForBootloaderRemoval
                Tools.BackendTools.essentials.OSsForBootloaderInstallation = OSsForBootloaderInstallation

                #*** Main Bootloader Tools (in Backend Tools package) ***
                Tools.BackendTools.BootloaderTools.main.OSsForBootloaderRemoval = OSsForBootloaderRemoval
                Tools.BackendTools.BootloaderTools.main.OSsForBootloaderInstallation = OSsForBootloaderInstallation
                Tools.BackendTools.BootloaderTools.main.LiveDisk = LiveDisk
                Tools.BackendTools.BootloaderTools.main.AutoRootFS = AutoRootFS
                Tools.BackendTools.BootloaderTools.main.Bootloader = Bootloader
                Tools.BackendTools.BootloaderTools.main.UpdateBootloader = UpdateBootloader
                Tools.BackendTools.BootloaderTools.main.ReinstallBootloader = ReinstallBootloader
                Tools.BackendTools.BootloaderTools.main.DisableBootloaderOperations = DisableBootloaderOperations
                Tools.BackendTools.BootloaderTools.main.BootloaderToInstall = BootloaderToInstall

                #*** Bootloader Configuration Obtaining Tools (in Backend Tools package) ***
                Tools.BackendTools.BootloaderTools.getconfigtools.BootloaderTimeout = BootloaderTimeout
                Tools.BackendTools.BootloaderTools.getconfigtools.KernelOptions = KernelOptions
                Tools.BackendTools.BootloaderTools.getconfigtools.OSsForBootloaderRemoval = OSsForBootloaderRemoval
                Tools.BackendTools.BootloaderTools.getconfigtools.LiveDisk = LiveDisk
                Tools.BackendTools.BootloaderTools.getconfigtools.AutoRootFS = AutoRootFS
                Tools.BackendTools.BootloaderTools.getconfigtools.Bootloader = Bootloader

                #*** Bootloader Removal Tools (in Backend Tools package) ***
                Tools.BackendTools.BootloaderTools.removaltools.OSsForBootloaderInstallation = OSsForBootloaderInstallation
                Tools.BackendTools.BootloaderTools.removaltools.OSsForBootloaderRemoval = OSsForBootloaderRemoval
                Tools.BackendTools.BootloaderTools.removaltools.LiveDisk = LiveDisk
                Tools.BackendTools.BootloaderTools.removaltools.AutoRootFS = AutoRootFS
                Tools.BackendTools.BootloaderTools.removaltools.Bootloader = Bootloader

                #Run the function.
                function()

                #*** Extra temporary stuff needed to make things work for the time being until we switch to dictionaries (Set the vars global to this file) ***
                #*** Essential backend tools ***
                OSsForBootloaderRemoval = Tools.BackendTools.Essentials.OSsForBootloaderRemoval
                OSsForBootloaderInstallation = Tools.BackendTools.Essentials.OSsForBootloaderInstallation
    
                #*** Main Bootloader Tools (in Backend Tools package) ***
                OSsForBootloaderRemoval = Tools.BackendTools.BootloaderTools.main.OSsForBootloaderRemoval
                OSsForBootloaderInstallation = Tools.BackendTools.BootloaderTools.main.OSsForBootloaderInstallation
                BootloaderToInstall = Tools.BackendTools.BootloaderTools.main.BootloaderToInstall

            logger.info("MainBackendThread().StartOperations(): Finished Operation Running Code.")

            #Save a system report if needed.
            if MakeSystemSummary:
                logger.info("MainBackendThread().StartOperations(): Generating System Report...")
                self.GenerateSystemReport()
                logger.info("MainBackendThread().StartOperations(): Done, finished all operations.")

            wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Finished!")

            DialogTools().ShowMsgDlg(Kind="info", Message="Your operations are all done! Thank you for using WxFixBoot. If you performed any bootloader operations, please now reboot your system.") #*** Check this and customise message if needed ***

        wx.CallAfter(self.ParentWindow.MainBackendThreadFinished)

    ####################Start Of Bootloader Operation functions.#################### #*** Move these to their seperate package ***
    ####################Start Of Bootloader Removal Functions.#################### #*** Move these to their seperate package ***

    ####################End Of Bootloader Removal Functions.####################
    ####################Start Of Bootloader Installation Functions.####################

    def InstallNewBootloader(self):
        #Function to install a new bootloader.
        #Install the new bootloader on the chosen OS.
        wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Preparing to install the new bootloader(s)...")
        wx.CallAfter(self.ParentWindow.UpdateCurrentProgress, 52)  
        BootloaderInstallSucceded = True     

        #Loop through OSsForBootloaderInstallation, and provide information to the function that will install the bootloader.
        for OS in OSsForBootloaderInstallation:
            #For each OS that needs the new bootloader installed, grab the partition, and the package manager.
            Partition = OS.split()[-5]
            PackageManager = OS.split()[-1]

            logger.info("MainBackendThread().InstallNewBootloader(): Preparing to install the new bootloader "+BootloaderToInstall+" in OS: "+OS+"...")
            wx.CallAfter(self.ParentWindow.UpdateOutputBox, "\n###Preparing to install the new bootloader in OS: "+OS+"...###\n")
            wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Preparing to install the new bootloader(s)...")

            #Grab the architecture.
            Arch = OS.split()[-8]
            if Arch == "64-bit":
                Arch = "x86_64"
            else:
                Arch = "i686"

            #If we're not on a live disk, and the partition is AutoRootFS, let the installer function know that we aren't using chroot.
            if LiveDisk == False and Partition == AutoRootFS:
                #Update the package lists.
                retval = self.UpdatePackageLists(PackageManager=PackageManager, UseChroot=False)

                wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Installing the new bootloader(s)...")
                wx.CallAfter(self.ParentWindow.UpdateCurrentProgress, 55)       
                wx.CallAfter(self.ParentWindow.UpdateOutputBox, "\n###Installing the new bootloader in OS: "+OS+"...###\n")

                if BootloaderToInstall == "GRUB2":
                    retval = self.InstallGRUB2(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

                elif BootloaderToInstall == "LILO":
                    retval = self.InstallLILO(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

                elif BootloaderToInstall == "GRUB-UEFI":
                    #Mount the UEFI partition at /boot/efi.
                    #Unmount it first though, in case it's already mounted.
                    CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                    CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint="/boot/efi") #*** Check this worked! ***

                    retval = self.InstallGRUBUEFI(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

                elif BootloaderToInstall == "ELILO":
                    #Unmount the UEFI Partition now.
                    CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***

                    retval = self.InstallELILO(PackageManager=PackageManager, UseChroot=False, Arch=Arch)

            #Otherwise, setup the chroot and everything else first, and tell it we are using chroot, and pass the mountpoint to it.
            else:
                #Mount the partition using the global mount function.
                MountPoint = "/mnt"+Partition
                Retval = CoreTools().MountPartition(Partition=Partition, MountPoint=MountPoint)

                if Retval != 0:
                    logger.error("MainBackendThread().InstallNewBootloader(): Failed to remount "+Partition+"! Warn the user and skip this OS.")
                    DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to mount the partition containing: "+OS+"! Bootloader installation cannot continue! This may leave your system, or this OS, in an unbootable state. It is recommended to do a Bad Sector check, and then try again.")

                else:
                    #Set up chroot.
                    CoreBackendTools().SetUpChroot(MountPoint=MountPoint)

                    #If there's a seperate /boot partition for this OS, make sure it's mounted.
                    CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'mount', '-av'], ShowOutput=False)

                    #Update the package lists.
                    retval = self.UpdatePackageLists(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint)

                    wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Installing the new bootloader(s)...")
                    wx.CallAfter(self.ParentWindow.UpdateCurrentProgress, 55)       
                    wx.CallAfter(self.ParentWindow.UpdateOutputBox, "\n###Installing the new bootloader in OS: "+OS+"...###\n")

                    #Install the bootloader.
                    if BootloaderToInstall == "GRUB2":
                        retval = self.InstallGRUB2(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    elif BootloaderToInstall == "LILO":
                        retval = self.InstallLILO(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    elif BootloaderToInstall == "GRUB-UEFI":
                        #Mount the UEFI partition at MountPoint/boot/efi.
                        #Unmount it first though, in case it's already mounted.
                        CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                        CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint=MountPoint+"/boot/efi") #*** Check it worked! ***
                        retval = self.InstallGRUBUEFI(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    elif BootloaderToInstall == "ELILO":
                        #Unmount the UEFI Partition now, and update the mtab inside chroot.
                        CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                        CoreBackendTools().UpdateChrootMtab(MountPoint=MountPoint)

                        retval = self.InstallELILO(PackageManager=PackageManager, UseChroot=True, MountPoint=MountPoint, Arch=Arch)

                    #If there's a seperate /boot partition for this OS, make sure it's unmounted before removing the chroot. *** No need to use chroot for this ***
                    CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'umount', '/boot'], ShowOutput=False)

                    #Tear down chroot.
                    CoreBackendTools().TearDownChroot(MountPoint=MountPoint)

            if retval != 0:
                #Something went wrong! Log it and notify the user.
                BootloaderInstallSucceded = False
                logger.error("MainBackendThread().InstallNewBootloader(): Failed to install "+BootloaderToInstall+" in OS: "+OS+"! This may mean the system (or this OS) is now unbootable! We'll continue anyway. Warn the user.")
                DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to install "+BootloaderToInstall+" in: "+OS+"! This may leave your system, or this OS, in an unbootable state. It is recommended to do a Bad Sector check, unplug any non-essential devices, and then try again.")

            wx.CallAfter(self.ParentWindow.UpdateOutputBox, "\n###Finished installing the new bootloader in OS: "+OS+"...###\n")

        #Log and notify the user that we're finished removing bootloaders.
        logger.info("MainBackendThread().InstallNewBootloader(): Finished Installing bootloaders...")
        wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Finished Installing bootloaders...")
        wx.CallAfter(self.ParentWindow.UpdateCurrentProgress, 75)
        return BootloaderInstallSucceded

    def UpdatePackageLists(self, PackageManager, UseChroot, MountPoint="None"):
        #Function to update thpackage lists so the required packages can always be found.
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get update", Piping=True)
            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get update'", Piping=True)
        
        #Return the return value.
        return retval

    def InstallGRUB2(self, PackageManager, UseChroot, Arch, MountPoint="None"):
        #Function to install GRUB2.
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y grub-pc os-prober", Piping=True)
            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-pc os-prober'", Piping=True)
        
        #Return the return value.
        return retval

    def InstallLILO(self, PackageManager, UseChroot, Arch, MountPoint="None"):
        #Function to install LILO.
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y lilo", Piping=True)
            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y lilo'", Piping=True)
        
        #Return the return value.
        return retval

    def InstallGRUBUEFI(self, PackageManager, UseChroot, Arch, MountPoint="None"):
        #Function to Install GRUB-UEFI.
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y grub-efi os-prober", Piping=True)
            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y grub-efi os-prober'", Piping=True)
        
        #Return the return value.
        return retval

    def InstallELILO(self, PackageManager, UseChroot, Arch, MountPoint="None"):
        #Function to install ELILO.
        if PackageManager == "apt-get":
            if UseChroot == False:
                retval = CoreBackendTools().StartThreadProcess("DEBIAN_FRONTEND=noninteractive apt-get install -y elilo", Piping=True)
            else:
                retval = CoreBackendTools().StartThreadProcess("chroot "+MountPoint+" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y elilo'", Piping=True)
        
        #Return the return value.
        return retval

    ####################End Of Bootloader Installation Functions.####################
    ####################Start Of Bootloader Configuration Setting Functions.####################

    def SetNewBootloaderConfig(self):
        #Function to manage setting new bootloader config.
        logger.debug("MainBackendThread().SetNewBootloaderConfig(): Preparing to set bootloader config in OS(s): "+', '.join(OSsForBootloaderInstallation)+"...")
        wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Preparing to set the new bootloaders' config...")
        wx.CallAfter(self.ParentWindow.UpdateCurrentProgress, 77)

        #Loop through OSsForBootloaderInstallation, and provide information to the function that will set the bootloaders' config.
        for OS in OSsForBootloaderInstallation:
            #For each OS that needs the new bootloader configured, grab the partition, and the package manager.
            logger.info("MainBackendThread().SetNewBootloaderConfig(): Setting the new bootloader config for OS: "+OS+"...")

            #Grab the OS's partition and package manager.
            Partition = OS.split()[-5]
            PackageManager = OS.split()[-1]

            wx.CallAfter(self.ParentWindow.UpdateOutputBox, "\n###Preparing to set the new bootloaders' config for OS: "+OS+"...###\n")

            #Grab the architecture.
            Arch = OS.split()[-8]
            if Arch == "64-bit":
                Arch = "x86_64"
            else:
                Arch = "i686"

            wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Setting the new bootloader's config...")
            wx.CallAfter(self.ParentWindow.UpdateCurrentProgress, 79)
            wx.CallAfter(self.ParentWindow.UpdateOutputBox, "\n###Setting the new bootloader's config for OS: "+OS+"...###\n")

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
                    logger.warning("MainBackendThread().SetNewBootloaderConfig(): Failed to mount "+Partition+"! Ignoring this partition...")
                    continue

                else:
                    #Set up chroot.
                    CoreBackendTools().SetUpChroot(MountPoint=MountPoint)

                wx.CallAfter(self.ParentWindow.UpdateCurrentProgress, 81)

            #Look for the configuration file, based on which SetConfig() function we're about to run.
            if BootloaderToInstall == "GRUB2":
                #Check MountPoint/etc/default/grub exists.
                if os.path.isfile(MountPoint+"/etc/default/grub"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendThread().SetNewBootloaderConfig(): Setting GRUB2-BIOS Configuration...")
                    self.SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")

                #Now Install GRUB2 to the MBR.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Installing GRUB2 to MBR...")
                self.InstallGRUB2ToMBR(PackageManager=PackageManager, MountPoint=MountPoint)

                #Update GRUB.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
                self.UpdateGRUB2(PackageManager=PackageManager, MountPoint=MountPoint)

                #Set the default OS.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
                self.SetGRUB2DefaultOS(OS=OS, PackageManager=PackageManager, MountPoint=MountPoint)

            elif BootloaderToInstall == "GRUB-UEFI":
                #Check MountPoint/etc/default/grub exists.
                if os.path.isfile(MountPoint+"/etc/default/grub"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendThread().SetNewBootloaderConfig(): Setting GRUB2-UEFI Configuration...")
                    self.SetGRUB2Config(filetoopen=MountPoint+"/etc/default/grub")

                #Mount the UEFI partition at MountPoint/boot/efi.
                CoreTools().MountPartition(Partition=UEFISystemPartition, MountPoint=MountPoint+"/boot/efi") #*** Check it worked! ***

                #Now Install GRUB-UEFI to the UEFI Partition.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Installing GRUB2 to UEFISystemPartition...")
                self.InstallGRUBUEFIToPartition(PackageManager=PackageManager, MountPoint=MountPoint, UEFISystemPartitionMountPoint=MountPoint+"/boot/efi", Arch=Arch)

                #Update GRUB.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Updating GRUB2 Configuration...")
                self.UpdateGRUB2(PackageManager=PackageManager, MountPoint=MountPoint)

                #Make an entry in fstab for the UEFI Partition, if needed.
                HelperBackendTools().WriteFSTABEntryForUEFIPartition(MountPoint=MountPoint, UEFISystemPartition=UEFISystemPartition)

                #Copy and backup EFI files where needed.
                HelperBackendTools().BackupUEFIFiles(MountPoint=MountPoint)
                HelperBackendTools().CopyUEFIFiles(MountPoint=MountPoint)

                #Set the default OS.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Setting GRUB2 Default OS...")
                self.SetGRUB2DefaultOS(OS=OS, PackageManager=PackageManager, MountPoint=MountPoint)

            elif BootloaderToInstall == "LILO":
                #Make LILO's config file.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Making LILO's configuration file...")
                if MountPoint == "":
                    CoreBackendTools().StartThreadProcess(['liloconfig', '-f'], ShowOutput=False)
                else:
                    CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'liloconfig', '-f'], ShowOutput=False)

                #Check the config file exists for lilo
                if os.path.isfile(MountPoint+"/etc/lilo.conf"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendThread().SetNewBootloaderConfig(): Setting LILO Configuration...")
                    self.SetLILOConfig(filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)
    
                    #Also, set the OS entries.
                    logger.info("MainBackendThread().SetNewBootloaderConfig(): Creating LILO OS Entries...")
                    self.MakeLILOOSEntries(filetoopen=MountPoint+"/etc/lilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                #Now Install LILO to the MBR.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Installing LILO to the MBR...")
                self.InstallLILOToMBR(PackageManager=PackageManager, MountPoint=MountPoint)

            elif BootloaderToInstall == "ELILO":
                #Unmount the UEFI Partition now, and update mtab in the chroot.
                CoreTools().Unmount(UEFISystemPartition) #*** Check it worked! ***
                CoreBackendTools().UpdateChrootMtab(MountPoint=MountPoint)

                #Make ELILO's config file.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Making ELILO's configuration file...")
                if MountPoint == "":
                    CoreBackendTools().StartThreadProcess(['elilo', '-b', UEFISystemPartition, '--autoconf'], ShowOutput=False)
                else:
                    CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'elilo', '-b', UEFISystemPartition, '--autoconf'], ShowOutput=False)

                #Check elilo's config file exists.
                if os.path.isfile(MountPoint+"/etc/elilo.conf"):
                    #It does, we'll run the function to set the config now.
                    logger.info("MainBackendThread().SetNewBootloaderConfig(): Setting ELILO Configuration...")
                    self.SetELILOConfig(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                    #Also, set the OS entries.
                    logger.info("MainBackendThread().SetNewBootloaderConfig(): Creating ELILO OS Entries...")
                    self.MakeLILOOSEntries(filetoopen=MountPoint+"/etc/elilo.conf", PackageManager=PackageManager, MountPoint=MountPoint)

                #Now Install ELILO to the UEFI Partition.
                logger.info("MainBackendThread().SetNewBootloaderConfig(): Installing ELILO to UEFISystemPartition...")
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

            wx.CallAfter(self.ParentWindow.UpdateOutputBox, "\n###Finished setting the new bootloader's config for OS: "+OS+"...###\n")

        logger.debug("MainBackendThread().SetNewBootloaderConfig(): Finished setting bootloader config.")
        wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Finished setting the new bootloader's config!")
        wx.CallAfter(self.ParentWindow.UpdateCurrentProgress, 100)

    ####################Start Of GRUB Bootloader Configuration Setting Functions.####################

    def SetGRUB2Config(self, filetoopen):
        #Function to set GRUB2 config.
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

    def InstallGRUB2ToMBR(self, PackageManager, MountPoint):
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the MBR.
        #Use --force to make sure grub installs itself, even on a GPT disk with no bios boot partition.
        if MountPoint == "":
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['grub-install', '--force', RootDevice], ShowOutput=False)
        else:
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'grub-install', '--force', RootDevice], ShowOutput=False)

        #Return the return value.
        return retval

    def InstallGRUBUEFIToPartition(self, PackageManager, MountPoint, UEFISystemPartitionMountPoint, Arch):
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if MountPoint == "":
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['grub-install', '--efi-directory='+UEFISystemPartitionMountPoint, '--target='+Arch+'-efi'], ShowOutput=False)
        else:
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'grub-install', '--efi-directory=/boot/efi', '--target='+Arch+'-efi'], ShowOutput=False)

        #Return the return value.
        return retval

    def UpdateGRUB2(self, PackageManager, MountPoint):
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if MountPoint == "":
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['update-grub'], ShowOutput=False)
        else:
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'update-grub'], ShowOutput=False)

        #Return the return value.
        return retval

    def SetGRUB2DefaultOS(self, OS, PackageManager, MountPoint):
        #Now we need to set the default os.
        #I couldn't find a reliable way of doing this automatically, so give the user a choice box instead.
        global DefaultOS

        #Make a list of OSs grub2 found (hopefully all of them).
        if MountPoint == "":
            if PackageManager == "apt-get":
                Temp = CoreBackendTools().StartThreadProcess(["grep", '-w', "menuentry", "/boot/grub/grub.cfg"], ShowOutput=False, ReturnOutput=True)
                retcode = Temp[0]
                GrubMenuEntries = Temp[1]
        else:
            if PackageManager == "apt-get":
                Temp = CoreBackendTools().StartThreadProcess(["grep", '-w', "menuentry", MountPoint+"/boot/grub/grub.cfg"], ShowOutput=False, ReturnOutput=True)
                retcode = Temp[0]
                GrubMenuEntries = Temp[1]

        if retcode != 0:
            #Don't set the default OS.
            DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot failed to set the default OS. This doesn't really matter. Click okay to continue.")

        else:
            #Now finally make the list of grub's OS names.
            GRUBOSNameList = []

            #Split with each newline character found in the returned string.
            GrubMenuEntriesList = GrubMenuEntries.split('\n')
            for OSName in GrubMenuEntriesList:
                #Get each OS name, removing all of the unneeeded characters.
                junk,sep,info = OSName.partition("'")
                info,sep,junk = info.partition("'")
                GRUBOSNameList.append(info)

            #Now ask the user to select the correct one.
            DefaultOS = DialogTools().ShowChoiceDlg(Message="Please select the OS you want to use as "+BootloaderToInstall+"'s Default OS. You are setting configuration for: "+OS, Title="WxFixBoot - Select Default OS", Choices=GRUBOSNameList)

            #Use the user's selection to set the default OS.
            if LiveDisk == False and MountPoint == "":
                #If the OS is AutoRootFS, and we're not on a live disk, do it differently.
                if PackageManager == "apt-get":
                    retval = CoreBackendTools().StartThreadProcess(["grub-set-default", DefaultOS], ShowOutput=False)
                else:
                    retval = CoreBackendTools().StartThreadProcess(["grub2-set-default", DefaultOS], ShowOutput=False)
            else:
                if PackageManager == "apt-get":
                    retval = CoreBackendTools().StartThreadProcess(["chroot", MountPoint, "grub-set-default", DefaultOS], ShowOutput=False)
                else:
                    retval = CoreBackendTools().StartThreadProcess(["chroot", MountPoint, "grub2-set-default", DefaultOS], ShowOutput=False)

            #Return the return value.
            return retval

    ####################End Of GRUB Bootloader Configuration Setting Functions.####################
    ####################Start Of LILO and ELILO Bootloader Configuration Setting Functions.####################

    def SetLILOConfig(self, filetoopen, PackageManager, MountPoint):
        #Function to set LILO config.
        SetTimeout = False
        SetBootDevice = False

        #Open the file in read mode, so we can find the important bits of config to edit. Also, use a list to temporarily store the modified lines.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the timeout setting.
            if 'timeout' in line and '=' in line and '#' not in line:
                #Found it! Set it to our value.
                SetTimeout = True

                #Save it, carefully avoiding errors.
                head, sep, Temp = line.partition('=')
                Temp = unicode(BootloaderTimeout*10)

                #Reassemble the line.
                line = "timeout"+sep+Temp+"\n"

            #Look for the 'boot' setting.
            elif 'boot' in line and '=' in line and '#' not in line and 'map' not in line: 
                #Found it, seperate the line.
                SetBootDevice = True
                head, sep, Temp = line.partition('=')

                #Now let's find the ID of RootDevice.
                ID = CoreBackendTools().GetDeviceID(Device=RootDevice)
                if ID != "None":
                    #Good, we've got the ID.
                    #Set it to RootDevice's ID.                    
                    Temp = "/dev/disk/by-id/"+ID
                else:
                    #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
                    Temp = RootDevice

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetTimeout == False:
            NewFileContents.append("timeout="+unicode(BootloaderTimeout)+"\n")

        if SetBootDevice == False:
            #Now let's find the ID of RootDevice.
            ID = CoreBackendTools().GetDeviceID(Device=RootDevice)
            if ID != "None":
                #Good, we've got the ID.
                #Set it to RootDevice's ID.                    
                Temp = "/dev/disk/by-id/"+ID
            else:
                #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
                Temp = RootDevice

            NewFileContents.append("boot="+Temp+"\n")

        #Write the finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

    def SetELILOConfig(self, filetoopen, PackageManager, MountPoint):
        #Function to set ELILO config.
        SetTimeout = False
        SetUEFIPart = False

        #Open the file in read mode, so we can find the important bits of config to edit. Also, use a list to temporarily store the modified lines.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Loop through each line in the file, paying attention only to the important ones.
        for line in ConfigFile:
            #Look for the delay setting.
            if 'delay' in line and '=' in line and '#' not in line:
                #Found it! Set it to our value.
                SetTimeout = True

                #Save it, carefully avoiding errors.
                head, sep, Temp = line.partition('=')
                Temp = unicode(BootloaderTimeout*10)

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Look for the 'boot' setting.
            elif 'boot' in line and '=' in line and '#' not in line:
                #Found it, seperate the line.
                SetUEFIPart = True
                head, sep, Temp = line.partition('=')

                #Now let's find the ID of UEFISystemPartition.
                ID = CoreBackendTools().GetDeviceID(Device=UEFISystemPartition)

                if ID != "None":
                    #Good, we've got the ID.
                    #Set it to UEFISystemPartition's ID.                    
                    Temp = "/dev/disk/by-id/"+ID
                else:
                    #Not so good... We'll have to use the partition's name, which may change, especially if we're using chroot.
                    Temp = UEFISystemPartition

                #Reassemble the line.
                line = head+sep+Temp+"\n"

            #Get rid of any boot entries.
            elif 'image=' in line or '\t' in line:
                #Skip this line, and don't append it to the list.
                continue

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetTimeout == False:
            NewFileContents.append("delay="+unicode(BootloaderTimeout)+"\n")

        if SetUEFIPart == False:
            #Now let's find the ID of UEFISystemPartition.
            ID = CoreBackendTools().GetDeviceID(Device=UEFISystemPartition)
            if ID != "None":
                #Good, we've got the ID.
                #Set it to UEFISystemPartition's ID.                    
                Temp = "/dev/disk/by-id/"+ID
            else:
                #Not so good... We'll have to use the device name, which may change, especially if we're using chroot.
                Temp = UEFISystemPartition

            NewFileContents.append("boot="+Temp+"\n")

        #Write the finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

    def MakeLILOOSEntries(self, filetoopen, PackageManager, MountPoint):
        #Okay, we've saved the kopts, timeout, and the boot device in the list.
        #Now we'll set the OS entries, and then the default OS.
        #Open the file, and add each entry to a temporary list, which will be written to the file later.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #First, make sure everything else comes first, because LILO and ELILO are picky with the placement of the image files (they must be at the end of the file).
        #We'll also make a placeholder for the default OS, so it comes before the image entries too.
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
        if BootloaderToInstall == "ELILO":
            NewFileContents.append("#################### ELILO per-image section ####################")

        #As we make these entries, we'll record which ones were actually made, as the user can cancel them if it looks like it won't work.
        CompletedEntriesList = []

        for OS in OSList:
            logger.info("MainBackendThread().MakeLILOOSEntries(): Preparing to make an entry for: "+OS)

            #Names in LILO are not allowed to have spaces, so let's grab the names and remove the spaces from them.
            #If this OS is the currently running one, we'll need to access a different part of the element.
            if OS.split()[-5] == "OS)":
                OSName = ''.join(OS.split()[0:-6])
            else:
                OSName = ''.join(OS.split()[0:-4])

            #Remove all the spaces from the OS's name.
            OSName = OSName.replace(' ','')

            #Grab the OS's partition.
            Partition = OS.split()[-1]

            #Check that the name is no longer than 15 characters.
            if len(OSName) > 15:
                #The name is too long! Truncate it to 15 characters.
                logger.warning("MainBackendThread().MakeLILOOSEntries(): Truncating OS Name: "+OSName+" to 15 characters...")
                OSName = OSName[0:15]

            #Now let's make the entries.
            logger.debug("MainBackendThread().MakeLILOOSEntries(): Checking for /vmlinuz and /initrd.img...")

            if OS[-5] == "OS)":
                CurrentOS = True
            else:
                CurrentOS = False

            #Check that MountPoint/vmlinuz and MountPoint/initrd.img exist. (If this is the current OS, MountPoint = "", and so doesn't get in the way).
            if os.path.isfile(MountPoint+"/vmlinuz"):
                #Good, add this to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                logger.info("MainBackendThread().MakeLILOOSEntries(): Found /vmlinuz! Adding it to the config file...")
                NewFileContents.append("\nimage=/vmlinuz\n")
            else:
                #Not so good... This probably means changing LILO's config each time we do a kernel update... Let's ask the user if we should still add it.
                logger.warning("MainBackendThread().MakeLILOOSEntries(): Couldn't find /vmlinuz for: "+OS+"! Asking the user if we should search for vmlinuz and make an entry anyway...")

                Result = DialogTools().ShowYesNoDlg(Message="Warning: /vmlinuz (shortcut to the latest kernel) wasn't found for: "+OS+"! Your new bootloader will still work, but this might mean you'll have to manaully change its config file each time you update your kernel on this OS. You can do this with WxFixBoot, but that won't stop it from being annoying and introducing security risks if you forget. However, this OS will be unbootable if you don't add it to the boot menu. Do you want to add it to the boot menu anyway?", Title="WxFixBoot - Add OS to boot menu?")

                if Result == False:
                    #Okay, go back to the start of the loop.
                    logger.warning("MainBackendThread().MakeLILOOSEntries(): Not making an entry for "+OS+"! Skipping this OS...")
                    continue

                else:
                    #Right, we'll have to hunt out the Kernel.
                    logger.warning("MainBackendThread().MakeLILOOSEntries(): Okay, we'll make an entry for "+OS+" anyway. Now let's try and find the latest Kernel...")
                    Kernel = HelperBackendTools().FindLatestVersion(Directory=MountPoint+"/boot", Type="Kernel")

                    #Check if we found it.
                    if Kernel == "None":
                        #We didn't! Tell the user, and skip this OS.
                        logger.error("MainBackendThread().MakeLILOOSEntries(): Couldn't find the latest kernel for "+OS+"! This OS will now be skipped!") 
                        DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot couldn't find the latest kernel for this OS. This OS will now be skipped.")
                        continue

                    else:
                        #We did! Add it to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                        logger.info("MainBackendThread().MakeLILOOSEntries(): Found the latest kernel at: "+Kernel+"! Adding it to the config file...")
                        NewFileContents.append("\nimage=/boot/"+Kernel+"\n")

            if os.path.isfile(MountPoint+"/initrd.img"):
                #Good, add this to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                logger.info("MainBackendThread().MakeLILOOSEntries(): Found /initrd.img! Adding it to the config file...")
                NewFileContents.append("\tinitrd=/initrd.img\n")
            else:
                #Not so good... This probably means changing LILO's config each time we do a kernel update... Let's ask the user if we should still add it.
                logger.warning("MainBackendThread().MakeLILOOSEntries(): Couldn't find /initrd.img for "+OS+"! Asking the user if we should search for initrd.img and make an entry anyway...")

                Result = DialogTools().ShowYesNoDlg(Message="Warning: /initrd.img (shortcut to the latest Initial Filesystem) wasn't found for: "+OS+"! Your new bootloader will still work, but this might mean you'll have to manaully change its config file each time you update your kernel on this OS. You can do this with WxFixBoot, but that won't stop it from being annoying and introducing security risks if you forget. Do you want to add it to the boot menu anyway?", Title="WxFixBoot - Add OS to boot menu?")

                if Result == False:
                    #Okay, delete the last entry, so we don't have an unconfigured image, and then go back to the start of the loop.
                    logger.warning("MainBackendThread().MakeLILOOSEntries(): Not making an entry for "+OS+"! Deleting the unconfigured image, and skipping this OS...")
                    Temp = NewFileContents.pop()
                    continue

                else:
                    #Right, we'll have to hunt out the Initrd/Initramfs.
                    logger.warning("MainBackendThread().MakeLILOOSEntries(): Okay, we'll make an entry for "+OS+" anyway. Now let's try and find the latest Initrd...")
                    Initrd = HelperBackendTools().FindLatestVersion(Directory=MountPoint+"/boot", Type="Initrd")

                    #Check if we found it.
                    if Initrd == "None":
                        #We didn't! Tell the user, delete the unconfigured image entry (logically there must be one), and skip this OS.
                        logger.error("MainBackendThread().MakeLILOOSEntries(): Couldn't find the latest Initrd for "+OS+"! This OS will now be skipped, and the unconfigured image deleted!") 
                        DialogTools().ShowMsgDlg(Kind="error", Message="WxFixBoot couldn't find the latest initrd.img for this OS. This OS will now be skipped.")
                        Temp = NewFileContents.pop()
                        continue

                    else:
                        #We did! Add it to the file. (It's local to the partition, so we don't need to include MountPoint in the path)
                        logger.info("MainBackendThread().MakeLILOOSEntries(): Found the latest Initrd at: "+Initrd+"! Adding it to the config file...")
                        NewFileContents.append("\tinitrd=/boot/"+Initrd+"\n")

            #Set the root device.
            #Use UUID's here if we can.
            UUID = CoreBackendTools().GetPartitionUUID(Partition)
            if UUID == "None":
                NewFileContents.append("\troot="+Partition+"\n")
            else:
                #If we're using ELILO, we have to do this differently.
                if BootloaderToInstall == "ELILO":
                    NewFileContents.append("\troot=UUID="+UUID+"\n")
                else:
                    NewFileContents.append("\troot=\"UUID="+UUID+"\"\n")

            #Set the label.
            NewFileContents.append("\tlabel="+OSName+"\n")

            #Set the kernel options.
            NewFileContents.append("\tappend=\""+KernelOptions+"\"\n")

            #Set one other necessary boot option.
            NewFileContents.append("\tread-only\n")

            #Add this OS to the Completed Entries List, because if we got this far it's done and added.
            CompletedEntriesList.append(OSName)

        #Now set the default OS.
        #First, write the semi-finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

        #Open the file again, with the new files written.
        ConfigFile = open(filetoopen, 'r')
        NewFileContents = []

        #Get the OS name and truncate it if necessary.
        logger.info("MainBackendThread().MakeLILOOSEntries(): Getting and truncating the default OS's name...")

        #If DefaultOS is the currently running one, we'll need to access a different part of the variable.
        if DefaultOS.split()[-5] == "OS)":
            OSName = ''.join(DefaultOS.split()[0:-6])
        else:
            OSName = ''.join(DefaultOS.split()[0:-4])

        #Remove all of the spaces.
        DefaultOSName = OSName.replace(' ','')

        #Check that the name is no longer than 15 characters.
        if len(DefaultOSName) > 15:
            #The name is too long! Truncate it to 15 characters.
            logger.warning("MainBackendThread().MakeLILOOSEntries(): Truncating OS Name: "+DefaultOSName+" to 15 characters...")
            DefaultOSName = DefaultOSName[0:15]

        #Now, check if its entry was added to the file, and ask the user for a new one if it wasn't.
        if DefaultOSName not in CompletedEntriesList:
            logger.info("MainBackendThread().MakeLILOOSEntries(): Default OS not in the Completed Entries List! Asking the user for a new one...")

            if len(CompletedEntriesList) <= 0:
                #Something went wrong here! No OSs appear to have been added to the list. Warn the user.
                logger.error("MainBackendThread().MakeLILOOSEntries(): CompletedEntriesList is empty! This suggests that no OSs have been added to the list! Warn the user, and skip this part of the operation.")
                DialogTools().ShowMsgDlg(Kind="error", Message="No Operating Systems have had entries created for them! If you canceled creating the entries, please reboot WxFixBoot and select only the option 'Update Bootloader Config'. If you didn't do that, and WxFixBoot either couldn't create them, or you see this error with no previous warnings, you may have to create your own bootloader config. Don't worry, this isn't too difficult, and you can search for tutorials for this on the internet. If WxFixBoot couldn't create your entries, or you are seeing this message with no previous warnings, please also email me directly via my Launchpad page with the contents of /tmp/wxfixboot.log and I'll try to help you.")

            else:
                #Ask the user for a new default OS.
                DefaultOSName = DialogTools().ShowChoiceDlg(Message="The OS you previously selected as the default wasn't added to the boot menu. Please an new OS you want to use as "+Bootloader+"'s Default OS. You are setting configuration for: "+OS, Title="WxFixBoot - Select Default OS", Choices=CompletedEntriesList)
                logger.info("MainBackendThread().MakeLILOOSEntries(): User selected new default OS: "+DefaultOSName+"...")

        #Make the entry for the default OS.
        logger.info("MainBackendThread().MakeLILOOSEntries(): Setting default OS...")
        SetDefaultOS = False

        for line in ConfigFile:
            if 'default' in line and '=' in line and '#' not in line:
                #Get the LILO name for DefaultOS.
                SetDefaultOS = True

                #Set default to the name.
                line = "default="+DefaultOSName+"\n"

            NewFileContents.append(line)

        #Check that everything was set. If not, write that config now.
        if SetDefaultOS == False:
            NewFileContents.append("default="+DefaultOSName+"\n")

        #Write the finished lines to the file.
        ConfigFile.close()
        ConfigFile = open(filetoopen, 'w')
        ConfigFile.write(''.join(NewFileContents))
        ConfigFile.close()

    def InstallLILOToMBR(self, PackageManager, MountPoint):
        #Install lilo to the MBR of RootDev.
        if MountPoint == "":
            retval = CoreBackendTools().StartThreadProcess(['lilo'], ShowOutput=False)
        else:
            retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'lilo'], ShowOutput=False)

        #Return the return value.
        return retval

    def InstallELILOToPartition(self, PackageManager, MountPoint, UEFISystemPartitionMountPoint, Arch):
        #Okay, we've modified the kernel options and the timeout. Now we need to install grub to the UEFI partition.
        if MountPoint == "":
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['elilo', '-b', UEFISystemPartition, '--efiboot'], ShowOutput=False)
        else:
            if PackageManager == "apt-get":
                retval = CoreBackendTools().StartThreadProcess(['chroot', MountPoint, 'elilo', '-b', UEFISystemPartition, '--efiboot'], ShowOutput=False)

        #Return the return value.
        return retval

    ####################End Of LILO and ELILO Bootloader Configuration Setting Functions.####################
    ####################End Of Bootloader Configuration Setting Functions.####################
    ####################End Of Bootloader Operation functions.####################
    ####################Start of system report generation function.####################
    def GenerateSystemReport(self):
        #Function to create a system report, containing various information helpful for debugging and fixing problems. It's pretty much like a bootinfo summary.
        DialogTools().ShowMsgDlg(Kind="info", Message="WxFixBoot will now create your system report. Click okay to continue.")

        #Ask the user where to save the file.
        ReportFile = DialogTools().ShowSaveFileDlg(Title="WxFixBoot - Select System Report File", Wildcard="Text Files|*.txt|Log Files|*.log|All Files/Devices (*)|*")

        #Write everything directly to the file.
        ReportList = open(ReportFile, 'w')
        ReportList.write("This system report was created with WxFixBoot version "+Version+". It can be used like a bootinfo summary.\n\n")

        #Do OS Information.
        ReportList.write("\n##########OS Information##########\n")
        ReportList.write("Detected Operating Systems: "+', '.join(OSList)+"\n")
        ReportList.write("Currently running OS is on Live Disk: "+unicode(LiveDisk)+"\n")

        #Do Firmware Information.
        ReportList.write("\n##########Firmware Information##########\n")
        ReportList.write("Detected firmware type: "+AutoFirmwareType+"\n")
        ReportList.write("Selected Firmware Type: "+FirmwareType+"\n")
        ReportList.write("UEFI System Partition (UEFI Bootloader target): "+UEFISystemPartition+"\n")

        if FirmwareType == "UEFI":
            ReportList.write("Found UEFI Variables: "+unicode(UEFIVariables)+"\n")

        #Do Bootloader information
        ReportList.write("\n##########BootLoader Information##########\n")
        ReportList.write("Detected Bootloader: "+AutoBootloader+"\n")
        ReportList.write("Selected Bootloader: "+Bootloader+"\n")

        if BootloaderToInstall != "None":
            #Display specific information depending on the operation to be done (if we're update/reinstalling bootloaders, don't make it look like we're doing something else).
            ReportList.write("Disabled Bootloader Operations: "+unicode(DisableBootloaderOperations)+"\n")

            if DisableBootloaderOperations == False:
                if ReinstallBootloader:
                    ReportList.write("Reinstall/Fix The Current BootLoader: "+unicode(ReinstallBootloader)+"\n")
                    ReportList.write("Selected Bootloader To Reinstall/Fix: "+BootloaderToInstall+"\n")
                    ReportList.write("Reinstall/Fix bootloader in: "+', '.join(OSsForBootloaderInstallation)+"\n")
                    ReportList.write("\nBootloader's New Configuration:"+"\n")
                    ReportList.write("\tDefault OS: "+DefaultOS+"\n")
                    ReportList.write("\tTimeout: "+unicode(BootloaderTimeout)+" seconds"+"\n")
                    ReportList.write("\tGlobal Kernel Options: "+KernelOptions+"\n")

                elif UpdateBootloader:
                    ReportList.write("Update The Current BootLoader's Config: "+unicode(UpdateBootloader)+"\n")
                    ReportList.write("Selected Bootloader To Update: "+BootloaderToInstall+"\n")
                    ReportList.write("Update Bootloader in: "+', '.join(OSsForBootloaderInstallation)+"\n")
                    ReportList.write("\nBootloader's New Configuration:"+"\n")
                    ReportList.write("\tDefault OS: "+DefaultOS+"\n")
                    ReportList.write("\tTimeout: "+unicode(BootloaderTimeout)+" seconds"+"\n")
                    ReportList.write("\tGlobal Kernel Options: "+KernelOptions+"\n")

                else:
                    #We must be installing a new bootloader.
                    ReportList.write("Selected Bootloader To Install: "+BootloaderToInstall+"\n")
                    ReportList.write("Remove Old Bootloader from: "+', '.join(OSsForBootloaderRemoval)+"\n")
                    ReportList.write("Install New Bootloader to: "+', '.join(OSsForBootloaderInstallation)+"\n")
                    ReportList.write("\nNew Bootloader's Configuration:"+"\n")
                    ReportList.write("\tDefault OS: "+DefaultOS+"\n")
                    ReportList.write("\tTimeout: "+unicode(BootloaderTimeout)+" seconds"+"\n")
                    ReportList.write("\tGlobal Kernel Options: "+KernelOptions+"\n")

        #Do Disk Information
        ReportList.write("\n##########Disk Information##########\n")
        ReportList.write("Detected Linux Partitions: "+', '.join(LinuxPartList)+"\n")
        ReportList.write("Detected Root Filesystem (MBR bootloader target): "+AutoRootFS+"\n")
        ReportList.write("Selected Root Filesystem (MBR bootloader target): "+RootFS+"\n")
        ReportList.write("Detected Root Device (MBR Bootloader Target): "+AutoRootDevice+"\n")
        ReportList.write("Selected Root Device (MBR Bootloader Target): "+RootDevice+"\n")
        ReportList.write("Partition Scheme List (In the same order as Detected Linux Partitions): "+', '.join(PartSchemeList)+"\n")
        ReportList.write("List of partitions with their filesystem types following: "+', '.join(PartitionListWithFSType)+"\n")

        #Do Boot Sector Information.
        ReportList.write("\n##########Boot Sector Information##########\n")
        ReportList.write("Backup Boot Sector: "+unicode(BackupBootSector)+"\n")
        if BackupBootSector:
            ReportList.write("\n\tBacked up Boot Sector From: "+RootDevice+"\n")
            ReportList.write("\tTarget Boot Sector File: (*** Disabled as no way of saving this until switch to dictionaries ***)\n\n") # *** +BootSectorBackupFile+"\n\n")

        ReportList.write("Restore Boot Sector: "+unicode(RestoreBootSector)+"\n")
        if RestoreBootSector:
            ReportList.write("\n\tBoot Sector Backup File: "+BootSectorFile+"\n")
            ReportList.write("\tBoot Sector Target Device: "+BootSectorTargetDevice+"\n")
            ReportList.write("\tBoot Sector Backup Type: "+BootSectorBackupType+"\n") 

        #Do Partition Table Information.
        ReportList.write("\n##########Partition Table Information##########\n")
        ReportList.write("Backup Partition Table: "+unicode(BackupPartitionTable)+"\n")
        if BackupPartitionTable:
            ReportList.write("\n\tBacked up Partition Table from: "+RootDevice+"\n")
            ReportList.write("\tTarget Partition Table File: (*** Disabled as no way of saving this until switch to dictionaries ***)\n\n") # *** +PartitionTableBackupFile+"\n\n")

        ReportList.write("Restore Partition Table: "+unicode(RestorePartitionTable)+"\n")
        if RestorePartitionTable:
            ReportList.write("\n\tPartition Table Backup File: "+PartitionTableFile+"\n")
            ReportList.write("\tPartition Table Target Device: "+PartitionTableTargetDevice+"\n")
            ReportList.write("\tPartition Table Backup Type: "+PartitionTableBackupType+"\n")

        #Do WxFixBoot's settings.
        ReportList.write("\n##########Other WxFixBoot Settings##########\n")
        ReportList.write("Do Quick Filesystem Check: "+unicode(QuickFSCheck)+"\n")
        ReportList.write("Do Bad Sector Check: "+unicode(BadSectCheck)+"\n")
        ReportList.write("Show Diagnostic Terminal Output (***ignored***): "+unicode(FullVerbose)+"\n")
        ReportList.write("Save System Report To File: "+unicode(MakeSystemSummary)+"\n")

        if MakeSystemSummary:
            ReportList.write("\n\tSave Terminal Output in Report: "+unicode(SaveOutput)+"\n")
            ReportList.write("\tSystem Report Target File: "+ReportFile+"\n\n")

        ReportList.write("Number of operations to do: "+unicode(NumberOfOperationsToDo)+"\n")

        #Save terminal output.
        if SaveOutput:
            ReportList.write("\n##########Terminal Output##########\n")
            ReportList.write(self.ParentWindow.OutputBox.GetValue()) #*** Only works if FullVerbose is enabled, otherwise some output will be hidden. As such, all output is being shown with no regard to FullVerbose or ShowOutput passed to the function, or the user's checkbox in settingswindow ***

        #Save Log File.
        ReportList.write("\n##########WxFixBoot's Log File##########\n")
        logfile = open("/tmp/wxfixboot.log", "r")
        for line in logfile:
            ReportList.write(line)

        logfile.close()
 
#End Main Backend Thread
app = WxFixBoot(False)
app.MainLoop()
