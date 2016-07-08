#!/usr/bin/env python
# -*- coding: utf-8 -*-
# WxFixBoot Version 2.0~pre2
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

#*** Don't allow modification of 64-bit OSs from 32-bit ones (it won't work) ***
#*** Figure out what to do in each instance where something might fail ***
#*** Remove grub's .efi files after installing elilo and vice versa ***
#*** Support EFI on 32-bit firmware? ***
#*** When backing up, save bootloader config, instead of bootloader itself? That way WxFixBoot can handle reinstalling/fixing the bootloader as required ***
#*** Enable menu in ELILO ***
#*** ELILO Kernel options not detected ***
#*** Look at original LILO config, does it allow booting OSes with different vmlinuz/initrds? If so do what it does ***
#*** Use OS short name (e.g. 16.04 instead of Xenial Xerus) for LILO + ELILO ***
#*** Match LILO default OS to ours ***
#*** Is /etc/default/grub created after switching to grub? ***

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
ReleaseDate = "8/7/2016"

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

        if int(Value) == 100:
            self.FinishedInit()

    def UpdateProgressText(self, Message):
        """Update the progress text with the given string"""
        self.ProgressText.SetLabel(Message)
        self.Panel.Layout()

    def UpdateOutputBox(self, Message):
        """Dummy function, accepts a message argument but ignores it. Allows CoreTools.StartProcess to work."""
        pass

    def FinishedInit(self, Event=None):
        """Starts MainWindow, called when StartupScripts are finished"""
        logger.info("Closing Initial Window and Starting Main Window...")

        #Show the user some important information
        dlg = wx.MessageDialog(self.Panel, "Please make sure you have a working internet connection before performing any bootloader operations. Thank you.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
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
        """Start the thread."""
        #Initialize the thread.
        threading.Thread.__init__(self)
        self.ParentWindow = ParentWindow

        #Set up dialog tools.
        Tools.dialogtools.ParentWindow = ParentWindow

        #Start the thread.
        self.start()

    def run(self):
        """Create the temporary mount point folder and set some default settings."""
        logger.debug("InitThread(): Starting...")

        #Remove the temporary directory if it exists.
        if os.path.isdir("/tmp/wxfixboot/mountpoints"):
            #Check nothing is using it.
            if "/tmp/wxfixboot/mountpoints" in CoreTools.StartProcess("mount", ReturnOutput=True)[1]:
                CoreTools.EmergencyExit("There are mounted filesystems in /tmp/wxfixboot/mountpoints, WxFixBoot's temporary mountpoints directory! Please unmount any filesystems there and try again.")

            shutil.rmtree("/tmp/wxfixboot/mountpoints")

        os.makedirs("/tmp/wxfixboot/mountpoints")

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

        #Make dictionaries available to modules.
        Tools.coretools.DiskInfo = DiskInfo
        Tools.StartupTools.core.DiskInfo = DiskInfo
        Tools.StartupTools.core.SystemInfo = SystemInfo
        Tools.StartupTools.core.Settings = Settings
        Tools.StartupTools.main.DiskInfo = DiskInfo
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

        #Mount all filesystems.
        logger.info("InitThread(): Mounting Core Filesystems...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Mounting Core Filesystems...")
        MainStartupTools.MountCoreFS()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "63")
        logger.info("InitThread(): Done Mounting Core Filsystems!")

        #Check if there are any linux partitions in the list. *** How to do this warning now? ***
        #if SystemInfo["LinuxPartitions"] == []:
            #There are none, exit.
        #    logger.critical("InitThread(): No Linux Partitions (on HDD) of type ext(1,2,3,4), btrfs, xfs, jfs, zfs, minix or resierfs found! If you do have Linux partitions but WxFixBoot hasn't found them, please file a bug or ask a question on WxFixBoot's launchpad page. If you're using Windows or Mac OS X, then sorry as WxFixBoot has no support for these operating systems. You could instead use the tools provided by Microsoft and Apple to fix any issues with your computer. Exiting...")

            #Exit.
        #    CoreTools.EmergencyExit("You don't appear to have any Linux partitions on your hard disks. If you do have Linux partitions but WxFixBoot hasn't found them, please file a bug or ask a question on WxFixBoot's launchpad page. If you're using Windows or Mac OS X, then sorry as WxFixBoot has no support for these operating systems. You could instead use the tools provided by Microsoft and Apple to fix any issues with your computer.")

        #Get a list of Linux OSs.
        logger.info("InitThread(): Finding Linux OSs...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Finding Linux Operating Systems...")
        OSInfo, SystemInfo = MainStartupTools.GetLinuxOSs()

        Tools.StartupTools.main.OSInfo = OSInfo

        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "65")
        logger.info("InitThread(): Done...")

        #Get the firmware type.
        logger.info("InitThread(): Determining Firmware Type...")
        wx.CallAfter(self.ParentWindow.UpdateProgressText, "Determining Firmware Type...")
        MainStartupTools.GetFirmwareType()
        wx.CallAfter(self.ParentWindow.UpdateProgressBar, "70")
        logger.info("InitThread(): Determined Firmware Type as: "+SystemInfo["FirmwareType"])

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

        #***************************
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

        print("\n\nSettings:")
        Keys = Settings.keys()
        Keys.sort()

        for Key in Keys:
            print(Key)

        print("\n\nGlobals:")
        Vars = globals().keys()
        Vars.sort()

        for Var in Vars:
            print(Var)

        #***************************
        #Set some other variables to default values, avoiding problems down the line. *** Save these in a dictionary later ***
        #Define globals.
        global QuickFSCheck
        global BadSectCheck
        global SaveOutput
        global FullVerbose
        global Verify
        global MakeSystemSummary
        global BLOptsDlgRun
        global OptionsDlg1Run

        #Initialise them.
        QuickFSCheck = ""
        BadSectCheck = ""
        SaveOutput = ""
        FullVerbose = ""
        Verify = ""
        MakeSystemSummary = ""
        BLOptsDlgRun = ""
        OptionsDlg1Run = ""

        logger.info("InitThread(): Setting some defaults for other variables set in GUI by user...")
        QuickFSCheck, BadSectCheck, SaveOutput, FullVerbose, Verify, MakeSystemSummary, BLOptsDlgRun, OptionsDlg1Run = MainStartupTools.SetDefaults()

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

        logger.debug("MainWindow().OnCheckBox(): Done. Calling self.SaveMainOpts()...")
        self.SaveMainOpts()

    def Opts(self, Event=None):
        """Starts Settings Window"""
        global OptionsDlg1Run
        logger.debug("MainWindow().Opts(): Starting Settings Window and hiding MainWindow...")

        self.SaveMainOpts()

        OptionsDlg1Run = True
        self.Hide()
        SettingsWindow(self).Show()

    def SystemInfo(self, Event=None):
        """Start SystemInfoWindow"""
        logger.debug("MainWindow().SystemInfo(): Starting System Info Window...")
        SystemInfoWindow(self).Show()

    def ProgressWindow(self, Event=None):
        """Starts Progress Window"""
        if OptionsDlg1Run:
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

        self.CheckFileSystemsCB.SetValue(QuickFSCheck)
        self.BadSectorCheckCB.SetValue(BadSectCheck)

        #Enable and Disable Checkboxes as necessary
        self.OnCheckBox()

        #Reveal MainWindow
        self.Show()

    def OnAbout(self, Event=None):
        """Shows the About Box"""
        logger.debug("MainWindow().OnAbout(): Showing About Box...")
        aboutbox = wx.AboutDialogInfo()
        aboutbox.Name = "WxFixBoot"
        aboutbox.SetIcon(AppIcon)
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
        self.Bind(wx.EVT_MENU, self.Opts, self.menuOpts)
        self.Bind(wx.EVT_BUTTON, self.Opts, self.OptionsButton)
        self.Bind(wx.EVT_BUTTON, self.ProgressWindow, self.ApplyOperationsButton)

        #Checkboxes on the main window.
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.CheckFileSystemsCB)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.BadSectorCheckCB)

    def SaveMainOpts(self):
        """Save all options"""
        logger.debug("MainWindow().SaveMainOpts(): Saving Options on MainWindow...")
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
        if QuickFSCheck:
            Operations.append((EssentialBackendTools.FileSystemCheck, "Quick"))
            logger.info("MainWindow().CountOperations(): Added EssentialBackendTools.FileSystemCheck to Operations...")

        if BadSectCheck:
            Operations.append((EssentialBackendTools.FileSystemCheck, "Thorough"))
            logger.info("MainWindow().CountOperations(): Added EssentialBackendTools.FileSystemCheck to Operations...")

        #Now do other processes.
        for OS in BootloaderInfo.keys():
            if BootloaderInfo[OS]["Settings"]["ChangeThisOS"]:
                Operations.append((MainBootloaderTools.ManageBootloader, OS))
                logger.info("MainWindow().CountOperations(): Added (MainBootloaderTools.ManageBootloader, "+OS+") to Operations...")

        #*** Disabled temporarily ***
        #if MakeSystemSummary:
        #    Operations.append(BackendThread(self).GenerateSystemReport)
        #    logger.info("MainWindow().CountOperations(): Added BackendThread().GenerateSystemReport to Operations...")

        #Check if we need to check the internet connection, and do so first if needed.
        for Function in Operations:
            if type(Function) == type([]) and Function[0] == MainBootloaderTools.ManageBootloader:
                logger.info("MainWindow().CountOperations(): Doing bootloader operations. Adding EssentialBackendTools.CheckInternetConnection()...")
                Operations.insert(0, EssentialBackendTools.CheckInternetConnection())
                break

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
        NoteBookSharedFunctions.UpdateListCtrl(self, Headings=["Name", "IsCurrentOS", "Arch", "Partition", "PackageManager"], Dictionary=OSInfo)

    def OnSize(self, Event=None):
        """Auto resize the ListCtrl columns"""
        Width, Height = self.ListCtrl.GetClientSizeTuple()

        self.ListCtrl.SetColumnWidth(0, int(Width * 0.4))
        self.ListCtrl.SetColumnWidth(1, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(2, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.2))
        self.ListCtrl.SetColumnWidth(4, int(Width * 0.2))

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
        self.SetupOptions()
        self.SetupSizers()
        self.BindEvents()

        logger.debug("SettingsWindow().__init__(): SettingsWindow Started.")

    def CreateButtons(self):
        """Create Some buttons."""
        self.ExitButton = wx.Button(self.Panel, -1, "Apply these Settings and Close")
        self.BootloaderOptionsButton = wx.Button(self.Panel, -1, "Bootloader Options")

    def CreateText(self):
        """Create the text."""
        self.WelcomeText = wx.StaticText(self.Panel, -1, "Welcome to Settings. Please give everything a once-over.")
        self.BasicSettingsText = wx.StaticText(self.Panel, -1, "Basic Settings:")
        self.AdvancedSettingsText = wx.StaticText(self.Panel, -1, "Advanced Settings:")

    def CreateCBs(self):
        """Create the checkboxes"""
        #Basic settings
        self.FullVerboseCheckBox = wx.CheckBox(self.Panel, -1, "Show diagnostic terminal output")

        #Advanced settings
        self.MakeSummaryCheckBox = wx.CheckBox(self.Panel, -1, "Save System Report To File")
        self.LogOutputCheckBox = wx.CheckBox(self.Panel, -1, "Save terminal output in Report")

    def OnCheckBox(self, Event=None):
        """Manage the checkboxes' states"""
        if self.MakeSummaryCheckBox.IsChecked():
            self.LogOutputCheckBox.Enable()
            self.LogOutputCheckBox.SetValue(True)

        else:
            self.LogOutputCheckBox.SetValue(False)
            self.LogOutputCheckBox.Disable()

    def SetupOptions(self):
        """Load all Options here."""
        logger.debug("SettingsWindow().SetupOptions(): Setting up options...")

        #Checkboxes
        #Diagnostic output checkbox.
        if FullVerbose:
            self.FullVerboseCheckBox.SetValue(True)

        else:
            self.FullVerboseCheckBox.SetValue(False)

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

        #Create the sizer that holds the default OS choice and text.
        DefaultOSChoiceSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the sizer that holds the bootloader options button and text.
        BootloaderOptionsSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Create the sizer that holds the buttons at the bottom of the window.
        BottomButtonSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to the basic settings sizer.
        BasicSettingsSizer.Add(self.BasicSettingsText, 1, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, 10)
        BasicSettingsSizer.Add(self.FullVerboseCheckBox, 1, wx.BOTTOM, 10)

        #Add items to the advanced settings sizer.
        AdvancedSettingsSizer.Add(self.AdvancedSettingsText, 1, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, 10)
        AdvancedSettingsSizer.Add(self.MakeSummaryCheckBox, 1, wx.BOTTOM, 10)
        AdvancedSettingsSizer.Add(self.LogOutputCheckBox, 1, wx.BOTTOM, 10)

        #Add items to the all settings sizer.
        AllSettingsSizer.Add(BasicSettingsSizer, 4, wx.RIGHT|wx.EXPAND, 5)
        AllSettingsSizer.Add(wx.StaticLine(self.Panel), 0, wx.EXPAND)
        AllSettingsSizer.Add(AdvancedSettingsSizer, 3, wx.LEFT|wx.EXPAND, 5)

        #Add items to the bootloader options sizer.
        BootloaderOptionsSizer.Add(self.BootloaderOptionsButton, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)

        #Add items to the bottom button sizer.
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
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, self.MakeSummaryCheckBox)

    def LaunchblOpts(self, Event=None):
        """Start the Bootloader Options Window"""
        #Safeguard program reliability (and continuity) by saving the settings in optionswindow1 first.
        logger.debug("SettingsWindow().LaunchblOpts(): Calling self.SaveOptions()...")
        self.SaveOptions()

        #Open the Firmware Options window
        logger.debug("SettingsWindow().LaunchblOpts(): Starting Bootloader Settings Window...")
        self.Hide()
        BootloaderOptionsWindow(self).Show()

    def RefreshOptionsDlg1(self,msg):
        """Refresh the settings in SettingsWindow before re-showing it"""
        #Check if the boot sector is to be restored.
        logger.debug("SettingsWindow().RefreshOptionsDlg1(): Refreshing SettingsWindow...")

        #Setup options again.
        self.SetupOptions()
        self.Panel.Layout()

        #Show OptionsDlg1.
        self.Show()

    def SaveOptions(self, Event=None):
        """Save all options"""
        global SaveOutput
        global FullVerbose
        global SaveOutput
        global MakeSystemSummary

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

        #Use chroot in operations checkbox
        if self.MakeSummaryCheckBox.IsChecked():
            MakeSystemSummary = True

        else:
            MakeSystemSummary = False

        logger.debug("SettingsWindow().SaveOptions(): Value of MakeSystemSummary is: "+unicode(MakeSystemSummary))
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
#Begin Bootloader Options Window.
class BootloaderOptionsWindow(wx.Frame):
    def __init__(self, ParentWindow):
        """Initialise bootloader options window"""
        wx.Frame.__init__(self, parent=wx.GetApp().TopWindow, title="WxFixBoot - Bootloader Options", size=(400,200), style=wx.DEFAULT_FRAME_STYLE)
        self.Panel = wx.Panel(self)
        self.SetClientSize(wx.Size(800,800))
        self.ParentWindow = ParentWindow
        wx.Frame.SetIcon(self, AppIcon)

        #Set up the previous OS choice.
        if SystemInfo["PreviousOSChoice"] == "":
            SystemInfo["PreviousOSChoice"] = SystemInfo["UserFriendlyOSNames"][0]

        self.CreateText()
        self.CreateChoiceBoxes()
        self.CreateCheckBoxes()
        self.CreateButtons()
        self.CreateOtherWidgets()
        self.SetupSizers()
        self.BindEvents()

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
        self.NewKernelOptionsText = wx.StaticText(self.Panel, -1, "New kernel options:")
        self.BackupBootloaderText = wx.StaticText(self.Panel, -1, "Backup to:")
        self.RestoreBootloaderText = wx.StaticText(self.Panel, -1, "Restore from:")

    def CreateChoiceBoxes(self):
        """Create the choice boxes"""
        self.OSChoice = wx.Choice(self.Panel, -1, choices=SystemInfo["UserFriendlyOSNames"])
        self.OSChoice.SetStringSelection(SystemInfo["PreviousOSChoice"])

        #Basic Options.
        self.DefaultOSChoice = wx.Choice(self.Panel, -1, choices=SystemInfo["UserFriendlyOSNames"])

        #Advanced Options.
        self.NewBootloaderChoice = wx.Choice(self.Panel, -1, choices=[])
        self.BackupBootloaderChoice = wx.Choice(self.Panel, -1, choices=["-- Please Select --", "Specify File Path..."])
        self.RestoreBootloaderChoice = wx.Choice(self.Panel, -1, choices=["-- Please Select --", "Specify File Path..."])

    def CreateCheckBoxes(self):
        """Create the check boxes"""
        #Basic Options.
        self.ReinstallBootloaderCheckBox = wx.CheckBox(self.Panel, -1, "")
        self.UpdateBootloaderCheckBox = wx.CheckBox(self.Panel, -1, "")
        self.KeepBootloaderTimeoutCheckBox = wx.CheckBox(self.Panel, -1, "")

        #Advanced Options.
        self.KeepKernelOptionsCheckBox = wx.CheckBox(self.Panel, -1, "")
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
        NoteBookSharedFunctions.UpdateListCtrl(self, Headings=["Name", "IsCurrentOS", "Arch", "Partition", "PackageManager"], Dictionary=OSInfo)

        #Text ctrl.
        self.NewKernelOptionsTextCtrl = wx.TextCtrl(self.Panel, -1, "")

    def OnSize(self, Event=None):
        """Auto resize the ListCtrl columns"""
        Width, Height = self.ListCtrl.GetClientSizeTuple()

        self.ListCtrl.SetColumnWidth(0, int(Width * 0.4))
        self.ListCtrl.SetColumnWidth(1, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(2, int(Width * 0.1))
        self.ListCtrl.SetColumnWidth(3, int(Width * 0.2))
        self.ListCtrl.SetColumnWidth(4, int(Width * 0.2))

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

        self.KernelOptionsSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to KernelOptionsSizer.
        self.KernelOptionsSizer.Add(self.KeepKernelOptionsCheckBox, 2, wx.RIGHT|wx.ALIGN_CENTER, 5)
        self.KernelOptionsSizer.Add(self.NewKernelOptionsText, 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        self.KernelOptionsSizer.Add(self.NewKernelOptionsTextCtrl, 2, wx.LEFT|wx.ALIGN_CENTER, 5)

        self.InstallNewBootloaderSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Add items to InstallNewBootloaderSizer.
        self.InstallNewBootloaderSizer.Add(self.InstallNewBootloaderCheckBox, 2, wx.RIGHT|wx.ALIGN_CENTER, 5)
        self.InstallNewBootloaderSizer.Add((5,5), 1, wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER, 5)
        self.InstallNewBootloaderSizer.Add(self.NewBootloaderChoice, 2, wx.LEFT|wx.ALIGN_CENTER, 5)

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
        self.MainSizer.Add(self.KernelOptionsSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
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

        logger.debug("BootloaderOptionsWindow().LoadSettings(): Loading settings for "+OS+"...")
        self.ReinstallBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["Reinstall"])
        self.UpdateBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["Update"])
        self.KeepBootloaderTimeoutCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["KeepExistingTimeout"])
        self.BootloaderTimeoutSpinner.SetValue(BootloaderInfo[OS]["Settings"]["NewTimeout"])
        self.KeepKernelOptionsCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["KeepExistingKernelOptions"])
        self.NewKernelOptionsTextCtrl.SetValue(BootloaderInfo[OS]["Settings"]["NewKernelOptions"])
        self.DefaultOSChoice.SetStringSelection(BootloaderInfo[OS]["Settings"]["DefaultOS"])
        self.InstallNewBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["InstallNewBootloader"])
        self.NewBootloaderChoice.SetStringSelection(BootloaderInfo[OS]["Settings"]["NewBootloader"])
        self.BackupBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["BackupBootloader"])
        self.BackupBootloaderChoice.SetStringSelection(BootloaderInfo[OS]["Settings"]["BootloaderBackupTarget"])
        self.RestoreBootloaderCheckBox.SetValue(BootloaderInfo[OS]["Settings"]["RestoreBootloader"])
        self.RestoreBootloaderChoice.SetStringSelection(BootloaderInfo[OS]["Settings"]["BootloaderRestoreSource"])
        self.OnTimeoutCheckBox()

    def SetGUIState(self, Event=None):
        """Set all the GUI element's states (enabled/disabled) for this OS"""
        OS = self.OSChoice.GetStringSelection()

        logger.debug("BootloaderOptionsWindow().SetGUIState(): Setting GUI state for "+OS+"...")
        self.ReinstallBootloaderCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["ReinstallCheckBoxState"])
        self.UpdateBootloaderCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["UpdateCheckBoxState"])
        self.KeepBootloaderTimeoutCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["KeepExistingTimeoutCheckBoxState"])
        self.BootloaderTimeoutSpinner.Enable(BootloaderInfo[OS]["GUIState"]["NewTimeoutSpinnerState"])
        self.KeepKernelOptionsCheckBox.Enable(BootloaderInfo[OS]["GUIState"]["KeepExistingKernelOptionsCheckBoxState"])
        self.NewKernelOptionsTextCtrl.Enable(BootloaderInfo[OS]["GUIState"]["NewKernelOptionsTextCtrlState"])
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
        self.Bind(wx.EVT_CHECKBOX, self.OnKernelOptionsCheckBox, self.KeepKernelOptionsCheckBox)

        #Buttons.
        self.Bind(wx.EVT_BUTTON, self.OnClose, self.SaveButton)

        #Choiceboxes.
        self.Bind(wx.EVT_CHOICE, self.OnOSChoiceChange, self.OSChoice)
        self.Bind(wx.EVT_CHOICE, self.OnRestoreBootloaderChoice, self.RestoreBootloaderChoice)

    def OnRestoreBootloaderChoice(self, Event=None):
        """Allow the user to select a config file to restore the bootloader from"""
        logger.debug("BootloaderOptionsWindow().OnRestoreBootloaderChoice(): Selecting bootloader config backup file...")

        File = self.RestoreBootloaderChoice.GetStringSelection()

        #Determine what to do here.
        if File == "Specify File Path...":
            Dlg = wx.FileDialog(self.Panel, "Select Backup File...", defaultDir="/home", wildcard="All Files/Devices (*)|*|WxFixBoot Bootloader Config Backup (.wxfbc)|*.wxfbc", style=wx.OPEN)

            if Dlg.ShowModal() == wx.ID_OK: #*** Load config from file ***
                File = Dlg.GetPath()
                self.RestoreBootloaderChoice.Append(File)
                self.RestoreBootloaderChoice.SetStringSelection(File)
                logger.debug("BootloaderOptionsWindow().OnRestoreBootloaderChoice(): File is "+File+"...")
                logger.debug("BootloaderOptionsWindow().OnRestoreBootloaderChoice(): ***TODO*** Loading config from "+File+"...")

            Dlg.Destroy()

        elif File != "-- Please Select --":
            logger.debug("BootloaderOptionsWindow().OnRestoreBootloaderChoice(): ***TODO*** Loading config from "+File+"...")
            pass #*** Load config from file ***

    def OnOSChoiceChange(self, Event=None, Startup=False):
        """Save and load new GUI settings and states in accordance with the OS choice change"""
        logger.debug("BootloaderOptionsWindow().OnOSChoiceChange(): OS choice has changed. Saving and then loading settings...")
        #Save settings when selection a new choice, but not when this is called when the window is first opened.
        if Startup == False:
            self.SaveSettings(OS=SystemInfo["PreviousOSChoice"])
            self.SaveGUIState(OS=SystemInfo["PreviousOSChoice"])

        self.LoadSettings()
        self.SetGUIState()
        self.SetTextLabels()

        #Set up NewBootloaderChoice.
        if OSInfo[self.OSChoice.GetStringSelection()]["EFIPartition"] == "Unknown":
            Choices = ["GRUB2", "LILO"]
            dlg = wx.MessageDialog(self.Panel, "This OS has no UEFI partition, so you will be unable to select a UEFI bootloader to install.", "WxFixBoot - Information", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition)
            dlg.ShowModal()
            dlg.Destroy()

        else:
            Choices = ["GRUB-UEFI", "GRUB2", "ELILO", "LILO"]

        #Disable ELILO and LILO on Fedora systems. *** Check this works ***
        if "Fedora" in self.OSChoice.GetStringSelection():
            if "ELILO" in Choices:
                Choices.remove("ELILO")

            if "LILO" in Choices:
                Choices.remove("LILO")

        self.NewBootloaderChoice.Clear()

        #Add choices.
        for Choice in ["-- Please Select --"]+Choices:
            self.NewBootloaderChoice.Append(Choice)

        self.NewBootloaderChoice.SetStringSelection("-- Please Select --")

        #Make sure the window displays properly.
        self.MainSizer.SetSizeHints(self)

    def SetTextLabels(self):
        """Set text labels for GUI elements"""
        OS = self.OSChoice.GetStringSelection()

        logger.debug("BootloaderOptionsWindow().SetTextLabels(): Setting text labels for "+OS+"...")
        self.KeepKernelOptionsCheckBox.SetLabel("Keep "+BootloaderInfo[OS]["Bootloader"]+"'s existing kernel options")
        self.InstallNewBootloaderCheckBox.SetLabel("Replace "+BootloaderInfo[OS]["Bootloader"]+" with:")
        self.ReinstallBootloaderCheckBox.SetLabel("Fix/Reinstall "+BootloaderInfo[OS]["Bootloader"])
        self.UpdateBootloaderCheckBox.SetLabel("Update "+BootloaderInfo[OS]["Bootloader"]+"'s Config")
        self.KeepBootloaderTimeoutCheckBox.SetLabel("Keep "+BootloaderInfo[OS]["Bootloader"]+"'s existing menu timeout")
        self.BackupBootloaderCheckBox.SetLabel("Backup "+BootloaderInfo[OS]["Bootloader"])

    def OnUpdateOrReinstallCheckBox(self, Event=None):
        """Enable/Disable options, based on the value of the update/reinstall checkboxes."""
        logger.debug("BootloaderOptionsWindow().OnUpdateOrReinstallCheckBox(): Enabling and isabling options as needed...")
 
        if self.ReinstallBootloaderCheckBox.IsChecked():
            self.UpdateBootloaderCheckBox.Disable()
            self.KeepBootloaderTimeoutCheckBox.Enable()
            self.KeepBootloaderTimeoutCheckBox.SetValue(1)
            self.KeepKernelOptionsCheckBox.Enable()
            self.KeepKernelOptionsCheckBox.SetValue(1)
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
            self.KeepKernelOptionsCheckBox.Enable()
            self.KeepKernelOptionsCheckBox.SetValue(1)
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
            self.KeepKernelOptionsCheckBox.SetValue(0)
            self.KeepKernelOptionsCheckBox.Disable()
            self.BootloaderTimeoutSpinner.Disable()
            self.NewKernelOptionsTextCtrl.Disable()
            self.DefaultOSChoice.Disable()
            self.InstallNewBootloaderCheckBox.Enable()
            self.NewBootloaderChoice.Disable()
            self.RestoreBootloaderCheckBox.Enable()
            self.RestoreBootloaderChoice.Disable()

    def OnKernelOptionsCheckBox(self, Event=None):
        """Enable/Disable the kernel options text ctrl, based on the value of the kernel options checkbox."""
        logger.debug("BootloaderOptionsWindow().OnKernelOptionsCheckBox(): Enabling and Disabling options as needed...")

        if self.KeepKernelOptionsCheckBox.IsChecked():
            self.NewKernelOptionsTextCtrl.SetValue(BootloaderInfo[self.OSChoice.GetStringSelection()]["Settings"]["NewKernelOptions"])
            self.NewKernelOptionsTextCtrl.Disable()

        else:
            self.NewKernelOptionsTextCtrl.Enable()

    def OnTimeoutCheckBox(self, Event=None):
        """Enable/Disable the bootloader timeout spinner, based on the value of the timeout checkbox."""
        logger.debug("BootloaderOptionsWindow().OnTimeoutCheckBox(): Enabling and Disabling options s needed...")

        if self.KeepBootloaderTimeoutCheckBox.IsChecked():
            self.BootloaderTimeoutSpinner.SetValue(BootloaderInfo[self.OSChoice.GetStringSelection()]["Settings"]["NewTimeout"])
            self.BootloaderTimeoutSpinner.Disable()

        else:
            self.BootloaderTimeoutSpinner.Enable()

    def OnBackupBootloaderCheckBox(self, Event=None):
        """Enable/Disable the bootloader timeout spinner, based on the value of the timeout checkbox."""
        logger.debug("BootloaderOptionsWindow().OnBackupBootloaderCheckBox(): Enabling and Disabling options as needed...")

        if self.BackupBootloaderCheckBox.IsChecked():
            self.BackupBootloaderChoice.Enable()

        else:
            self.BackupBootloaderChoice.Disable()

    def OnRestoreBootloaderCheckBox(self, Event=None):
        """Enable/Disable options, based on the value of the timeout checkbox."""
        logger.debug("BootloaderOptionsWindow(). Enabling and disabling options as needed...")

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
        """Enable/Disable options, based on the value of the new bootloader checkbox."""
        logger.debug("BootloaderOptionsWindow().OnInstallNewBootloaderCheckBox(): Enabling and disabling options as needed...")

        if self.InstallNewBootloaderCheckBox.IsChecked():
            self.NewBootloaderChoice.Enable()
            self.ReinstallBootloaderCheckBox.Disable()
            self.UpdateBootloaderCheckBox.Disable()
            self.KeepBootloaderTimeoutCheckBox.Enable()
            self.KeepBootloaderTimeoutCheckBox.SetValue(1)
            self.KeepKernelOptionsCheckBox.Enable()
            self.KeepKernelOptionsCheckBox.SetValue(1)
            self.DefaultOSChoice.Enable()
            self.RestoreBootloaderCheckBox.Disable()
            self.RestoreBootloaderChoice.Disable()

        else:
            self.NewBootloaderChoice.Disable()
            self.ReinstallBootloaderCheckBox.Enable()
            self.UpdateBootloaderCheckBox.Enable()
            self.KeepBootloaderTimeoutCheckBox.SetValue(0)
            self.KeepBootloaderTimeoutCheckBox.Disable()
            self.KeepKernelOptionsCheckBox.SetValue(0)
            self.KeepKernelOptionsCheckBox.Disable()
            self.BootloaderTimeoutSpinner.Disable()
            self.NewKernelOptionsTextCtrl.Disable()
            self.DefaultOSChoice.Disable()
            self.RestoreBootloaderCheckBox.Enable()
            self.RestoreBootloaderChoice.Disable()

    def OnOSInfo(self, Event=None):
        """Hide/Show the OS info, and rotate the arrow"""
        if self.ListCtrl.IsShown():
            logger.debug("BootloaderOptionsWindow().OnOSInfo(): Hiding OS Info...")
            self.Arrow1.SetBitmap(self.RightArrowImage)

            self.MainSizer.Detach(self.ListCtrl)
            self.MainSizer.Detach(self.SystemInfoButton)
            self.ListCtrl.Hide()
            self.SystemInfoButton.Hide()

        else:
            logger.debug("BootloaderOptionsWindow().OnOSInfo(): Showing OS Info...")
            self.Arrow1.SetBitmap(self.DownArrowImage)

            self.MainSizer.Insert(4, self.ListCtrl, 5, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.MainSizer.Insert(5, self.SystemInfoButton, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.ListCtrl.Show()
            self.SystemInfoButton.Show()

        #Make sure the window is displayed properly.
        self.MainSizer.SetSizeHints(self)

    def OnBasicOptions(self, Event=None):
        """Hide/Show the basic options, and rotate the arrow"""
        if self.ReinstallBootloaderCheckBox.IsShown():
            logger.debug("BootloaderOptionsWindow().OnBasicOptions(): Hiding Basic Options...")

            #Refuse to collapse this section if Advanced Settings are shown.
            if self.InstallNewBootloaderCheckBox.IsShown():
                logger.debug("BootloaderOptionsWindow().OnBasicOptions(): Cancelling because Advanced Options are shown...")
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
            logger.debug("BootloaderOptionsWindow().OnBasicOptions(): Showing Basic Options...")
            self.Arrow2.SetBitmap(self.DownArrowImage)

            #Find the first index to re-add items in MainSizer.
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

        #Make sure the window displays properly.
        self.MainSizer.SetSizeHints(self)

    def OnAdvancedOptions(self, Event=None):
        """Show/Hide the advanced options, and rotate the arrow"""
        if self.InstallNewBootloaderCheckBox.IsShown():
            logger.debug("BootloaderOptionsWindow().OnAdvancedOptions(): Hiding Advanced Options...")
            self.Arrow3.SetBitmap(self.RightArrowImage)

            self.MainSizer.Detach(self.KernelOptionsSizer)
            self.MainSizer.Detach(self.InstallNewBootloaderSizer)
            self.MainSizer.Detach(self.BackupBootloaderSizer)
            self.MainSizer.Detach(self.RestoreBootloaderSizer)

            self.KeepKernelOptionsCheckBox.Hide()
            self.NewKernelOptionsText.Hide()
            self.NewKernelOptionsTextCtrl.Hide()
            self.InstallNewBootloaderCheckBox.Hide()
            self.NewBootloaderChoice.Hide()
            self.BackupBootloaderCheckBox.Hide()
            self.BackupBootloaderText.Hide()
            self.BackupBootloaderChoice.Hide()
            self.RestoreBootloaderCheckBox.Hide()
            self.RestoreBootloaderText.Hide()
            self.RestoreBootloaderChoice.Hide()

        else:
            logger.debug("BootloaderOptionsWindow().OnAdvancedOptions(): Showing Advanced Options...")

            #If Basic Options are hidden, show them.
            if self.ReinstallBootloaderCheckBox.IsShown() == False:
                logger.debug("BootloaderOptionsWindow().OnAdvancedOptions(): Showing Basic Options first...")
                self.OnBasicOptions()

            self.Arrow3.SetBitmap(self.DownArrowImage)

            if self.ListCtrl.IsShown():
                FirstNumber = 13

            else:
                FirstNumber = 11

            self.MainSizer.Insert(FirstNumber, self.KernelOptionsSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.MainSizer.Insert(FirstNumber+1, self.InstallNewBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.MainSizer.Insert(FirstNumber+2, self.BackupBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
            self.MainSizer.Insert(FirstNumber+3, self.RestoreBootloaderSizer, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

            self.KeepKernelOptionsCheckBox.Show()
            self.NewKernelOptionsText.Show()
            self.NewKernelOptionsTextCtrl.Show()
            self.InstallNewBootloaderCheckBox.Show()
            self.NewBootloaderChoice.Show()
            self.BackupBootloaderCheckBox.Show()
            self.BackupBootloaderText.Show()
            self.BackupBootloaderChoice.Show()
            self.RestoreBootloaderCheckBox.Show()
            self.RestoreBootloaderText.Show()
            self.RestoreBootloaderChoice.Show()

        #Make sure the window displays properly.
        self.MainSizer.SetSizeHints(self)

    def SaveSettings(self, Event=None, OS=None):
        """Save all settings for this OS from the checkboxes and choice boxes"""
        logger.debug("BootloaderOptionsWindow().SaveSettings(): Saving settings for "+OS+"...")

        BootloaderInfo[OS]["Settings"]["Reinstall"] = self.ReinstallBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["Update"] = self.UpdateBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["KeepExistingTimeout"] = self.KeepBootloaderTimeoutCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["NewTimeout"] = self.BootloaderTimeoutSpinner.GetValue()
        BootloaderInfo[OS]["Settings"]["KeepExistingKernelOptions"] = self.KeepKernelOptionsCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["NewKernelOptions"] = self.NewKernelOptionsTextCtrl.GetValue()
        BootloaderInfo[OS]["Settings"]["DefaultOS"] = self.DefaultOSChoice.GetStringSelection()
        BootloaderInfo[OS]["Settings"]["InstallNewBootloader"] = self.InstallNewBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["NewBootloader"] = self.NewBootloaderChoice.GetStringSelection()
        BootloaderInfo[OS]["Settings"]["BackupBootloader"] = self.BackupBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["BootloaderBackupTarget"] = self.BackupBootloaderChoice.GetStringSelection()
        BootloaderInfo[OS]["Settings"]["RestoreBootloader"] = self.RestoreBootloaderCheckBox.GetValue()
        BootloaderInfo[OS]["Settings"]["BootloaderRestoreSource"] = self.RestoreBootloaderChoice.GetStringSelection()

        if BootloaderInfo[OS]["Settings"]["Reinstall"] or BootloaderInfo[OS]["Settings"]["Update"] or BootloaderInfo[OS]["Settings"]["InstallNewBootloader"] or BootloaderInfo[OS]["Settings"]["RestoreBootloader"]:
            logger.debug("BootloaderOptionsWindow().SaveSettings(): "+OS+" is being modified...")
            BootloaderInfo[OS]["Settings"]["ChangeThisOS"] = True

        else:
            logger.debug("BootloaderOptionsWindow().SaveSettings(): "+OS+" is not being modified...")
            BootloaderInfo[OS]["Settings"]["ChangeThisOS"] = False

    def SaveGUIState(self, Event=None, OS=None):
        """Save all the GUI element's states (enabled/disabled) for this OS"""
        logger.debug("BootloaderOptionsWindow().SaveGUIState(): Saving GUI state for "+OS+"...")
        BootloaderInfo[OS]["GUIState"]["ReinstallCheckBoxState"] = self.ReinstallBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["UpdateCheckBoxState"] = self.UpdateBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["KeepExistingTimeoutCheckBoxState"] = self.KeepBootloaderTimeoutCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["NewTimeoutSpinnerState"] = self.BootloaderTimeoutSpinner.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["KeepExistingKernelOptionsCheckBoxState"] = self.KeepKernelOptionsCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["NewKernelOptionsTextCtrlState"] = self.NewKernelOptionsTextCtrl.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["DefaultOSChoiceState"] = self.DefaultOSChoice.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["InstallNewBootloaderCheckBoxState"] = self.InstallNewBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["NewBootloaderChoiceState"] = self.NewBootloaderChoice.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["BackupBootloaderCheckBoxState"] = self.BackupBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["BackupBootloaderChoiceState"] = self.BackupBootloaderChoice.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["RestoreBootloaderCheckBoxState"] = self.RestoreBootloaderCheckBox.IsEnabled()
        BootloaderInfo[OS]["GUIState"]["RestoreBootloaderChoiceState"] = self.RestoreBootloaderChoice.IsEnabled()

    def OnClose(self, Event=None):
        """Save settings and GUI state, and then close BootloaderOptionsWindow"""
        logger.debug("BootloaderOptionsWindow().OnClose(): Closing BootloaderOptionsWindow...")
        self.SaveSettings(OS=self.OSChoice.GetStringSelection())
        self.SaveGUIState(OS=self.OSChoice.GetStringSelection())

        #Send a message to SettingsWindow so it can refresh.
        wx.CallAfter(self.ParentWindow.RefreshOptionsDlg1, "Closed")

        self.Destroy()

#End New Bootloader Options Window.
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

        #Make sure the panel displays properly.
        self.Panel.Layout()

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

        #Prevent focus on Output Box.
        self.OutputBox.Bind(wx.EVT_SET_FOCUS, self.FocusOnOutputButton)

    def FocusOnOutputButton(self, Event=None):
        """Focus on the show output button instead of the TextCtrl, and reset the insertion point back after 30 milliseconds, preventing the user from changing the insertion point and messing the formatting up."""
        #Just a slightly hacky way of trying to make sure the user can't change the insertion point! Works unless you start doing silly stuff like tapping on the output box constantly :)
        self.ShowOutputButton.SetFocus()
        InsertionPoint = self.OutputBox.GetInsertionPoint()
        wx.CallLater(30, self.OutputBox.SetInsertionPoint, InsertionPoint)

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

    def BackSpace(self):
        """Handles backspaces in output"""
        #Move the insertion point 1 char to the left.
        self.OutputBox.SetInsertionPoint(self.OutputBox.GetInsertionPoint()-1)

    def UpdateOutputBox(self, Line):
        """Update the output box"""
        CRs = []
        BKSPs = []
        CharNo = 0

        for Char in Line:
            CharNo += 1

            if Char == "\r":
                CRs.append(CharNo)

            elif Char == "\x08":
                BKSPs.append(CharNo)

        CharNo = 0
        TempLine = ""

        for Char in Line:
            CharNo += 1

            if CharNo not in CRs and CharNo not in BKSPs:
                TempLine += Char
                if Char == "\n":
                    self.AddLineToOutputBox(TempLine, CRs, BKSPs, CharNo)
                    TempLine = ""

            else:
                self.AddLineToOutputBox(TempLine, CRs, BKSPs, CharNo)
                TempLine = ""

    def AddLineToOutputBox(self, Line, CRs, BKSPs, CharNo):
        InsertionPoint = self.OutputBox.GetInsertionPoint()

        #Handle \r\n as \n, fixing formatting problems.
        if InsertionPoint != 0:
            if Line == "\n" and self.OutputBox.GetRange(InsertionPoint-1, InsertionPoint) == "\r":
                self.OutputBox.Remove(InsertionPoint-1, InsertionPoint)

        self.OutputBox.Replace(InsertionPoint, InsertionPoint+len(Line), Line)

        if CharNo in CRs:
            self.CarriageReturn()

        elif CharNo in BKSPs:
            self.BackSpace()

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

        #Make sure any mounted filesystems in /tmp/wxfixbootmountpoints are unmounted first. *** Fix later, no filesystems should be mounted there after operations anyway ***
        #MainStartupTools.UnmountAllFS()

        InitialFrame = InitialWindow()
        app.SetTopWindow(InitialFrame)
        InitialFrame.Show(True)

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
        Tools.BackendTools.essentials.SystemInfo = SystemInfo

        Tools.BackendTools.helpers.BootloaderInfo = BootloaderInfo
        Tools.BackendTools.helpers.DiskInfo = DiskInfo
        Tools.BackendTools.helpers.OSInfo = OSInfo
        Tools.BackendTools.helpers.SystemInfo = SystemInfo

        Tools.BackendTools.main.OSInfo = OSInfo
        Tools.BackendTools.main.DiskInfo = DiskInfo
        Tools.BackendTools.main.SystemInfo = SystemInfo
        Tools.BackendTools.main.BootloaderInfo = BootloaderInfo

        Tools.BackendTools.BootloaderTools.main.BootloaderInfo = BootloaderInfo
        Tools.BackendTools.BootloaderTools.main.SystemInfo = SystemInfo
        Tools.BackendTools.BootloaderTools.main.OSInfo = OSInfo

        Tools.BackendTools.BootloaderTools.setconfigtools.BootloaderInfo = BootloaderInfo
        Tools.BackendTools.BootloaderTools.setconfigtools.DiskInfo = DiskInfo
        Tools.BackendTools.BootloaderTools.setconfigtools.SystemInfo = SystemInfo
        Tools.BackendTools.BootloaderTools.setconfigtools.OSInfo = OSInfo

        #Run functions to do operations.
        for function in Operations:
            #Run the function.
            if type(function) != type(()):
                function()

            else:
                function[0](function[1])

        logger.info("BackendThread().StartOperations(): Finished Operation Running Code.")

        wx.CallAfter(self.ParentWindow.UpdateCurrentOpText, Message="Finished!")

        #Change the dialog's message if needed.
        DialogMessage = "Your operations are all done! Thank you for using WxFixBoot."

        for Function in Operations:
            if type(Function) == type(()):
                if MainBootloaderTools.ManageBootloader in Function:
                    DialogMessage += " You performed bootloader operations on at least one OS, so please now reboot your system."
                    break

        DialogTools.ShowMsgDlg(Kind="info", Message=DialogMessage)

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
        ReportList.write("Detected firmware type: "+SystemInfo["FirmwareType"]+"\n")
        #ReportList.write("UEFI System Partition (UEFI Bootloader target): "+SystemInfo["UEFISystemPartition"]+"\n")

        #Do Bootloader information
        ReportList.write("\n##########BootLoader Information##########\n")
        if True: #*** Needs rewriting for new bootloader options ***
            #Display specific information depending on the operation to be done (if we're update/reinstalling bootloaders, don't make it look like we're doing something else). *** Show what we would do if they weren't disabled too ***
            ReportList.write("Disabled Bootloader Operations: "+unicode(SystemInfo["DisableBootloaderOperations"])+"\n")

            if SystemInfo["DisableBootloaderOperations"] == False: #*** Adapt to using dictionary-based system ***
                if ReinstallBootloader:
                    ReportList.write("Reinstall/Fix The Current BootLoader: "+unicode(ReinstallBootloader)+"\n")
                    #ReportList.write("Selected Bootloader To Reinstall/Fix: "+SystemInfo["BootloaderToInstall"]+"\n")
                    #ReportList.write("Reinstall/Fix bootloader in: "+', '.join(SystemInfo["OSsForBootloaderInstallation"])+"\n")
                    ReportList.write("\nBootloader's New Configuration:"+"\n")
                    #ReportList.write("\tDefault OS: "+SystemInfo["DefaultOS"]+"\n")
                    #ReportList.write("\tTimeout: "+unicode(BootloaderTimeout)+" seconds"+"\n")
                    #ReportList.write("\tGlobal Kernel Options: "+KernelOptions+"\n")

                elif UpdateBootloader:
                    ReportList.write("Update The Current BootLoader's Config: "+unicode(UpdateBootloader)+"\n")
                    #ReportList.write("Selected Bootloader To Update: "+SystemInfo["BootloaderToInstall"]+"\n")
                    #ReportList.write("Update Bootloader in: "+', '.join(SystemInfo["OSsForBootloaderInstallation"])+"\n")
                    ReportList.write("\nBootloader's New Configuration:"+"\n")
                    #ReportList.write("\tDefault OS: "+SystemInfo["DefaultOS"]+"\n")
                    #ReportList.write("\tTimeout: "+unicode(BootloaderTimeout)+" seconds"+"\n")
                    #ReportList.write("\tGlobal Kernel Options: "+KernelOptions+"\n")

                else:
                    #We must be installing a new bootloader.
                    #ReportList.write("Selected Bootloader To Install: "+SystemInfo["BootloaderToInstall"]+"\n")
                    #ReportList.write("Remove Old Bootloader from: "+', '.join(SystemInfo["OSsForBootloaderRemoval"])+"\n")
                    #ReportList.write("Install New Bootloader to: "+', '.join(SystemInfo["OSsForBootloaderInstallation"])+"\n")
                    ReportList.write("\nNew Bootloader's Configuration:"+"\n")
                    #ReportList.write("\tDefault OS: "+SystemInfo["DefaultOS"]+"\n")
                    #ReportList.write("\tTimeout: "+unicode(BootloaderTimeout)+" seconds"+"\n")
                    #ReportList.write("\tGlobal Kernel Options: "+KernelOptions+"\n")

        #Do Disk Information
        ReportList.write("\n##########Disk Information##########\n")
        #ReportList.write("Detected Linux Partitions: "+', '.join(SystemInfo["LinuxPartitions"])+"\n")

        #Do Boot Sector Information.
        ReportList.write("\n##########Boot Sector Information##########\n")
        #ReportList.write("Backup Boot Sector: "+unicode(BackupBootSector)+"\n")

        #if BackupBootSector: *** global var not used any more ***
            #ReportList.write("\n\tBacked up Boot Sector From: "+SystemInfo["RootDevice"]+"\n")
        #    ReportList.write("\tTarget Boot Sector File: (*** Disabled as no way of saving this until switch to dictionaries ***)\n\n") #*** +BootSectorBackupFile+"\n\n")

        #ReportList.write("Restore Boot Sector: "+unicode(RestoreBootSector)+"\n")
        #if RestoreBootSector:
        #    ReportList.write("\n\tBoot Sector Backup File: "+BootSectorFile+"\n")
        #    ReportList.write("\tBoot Sector Target Device: "+BootSectorTargetDevice+"\n")
        #    ReportList.write("\tBoot Sector Backup Type: "+BootSectorBackupType+"\n") 

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
