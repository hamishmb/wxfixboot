WxFixBoot (3.1.0):
  * Changes since 3.0.2:
  *
  * Removed support for YUM in favour of DNF.
  * Removed support for obsolete LILO bootloader.
  * Fixed backup and restoring bootloader config to/from file.
  * Make sure splash screen text is readable even with dark themes.
  * Detect Disk Verifier as a live disk.
  * Fix Fedora 33 detection (BTRFS).
  * Fix incompatibilities with wxPython 4.1.0.
  * Fix installing GRUB on Ubuntu when it asks for the installation device (seems random).

WxFixBoot (3.0.2)
  * Changes since 3.0.1:
  *
  * Make temporary mountpoints directory as root - pkgs create it with the wrong permissions.
  * Fix a potential crash when LVM disks are present when checking filesystems.
  * Drop support for Python 2.
  * Fix mounting issues that can occur infrequently with LVM disks.
  * Fix detection of GRUB2 BIOS boot disk.
  * Fix live disk detection when current OS is running on an NVME disk.
  * Fix a permissions problem when creating system folders.
  * Make sure volume groups are re-activated after clearing out unneeded ones (Ubuntu 20.04 fix).
  * Require GetDevInfo 1.0.10 as a dependency.
  * Remove references to Python 2 in documentation.

WxFixBoot (3.0.1)
  * Changes since 3.0.0:
  *
  * Removed support for wxPython 2.8.11, Ubuntu 14.04, Python 2.7.6.
  * Removed support for grub-legacy.
  * Removed support for ELILO.
  * Don't crash when a LILO menu entry doesn't have a valid label.
  * Fix a crash when a kernel/initrd can't be found.
  * On Fedora set GRUB_CMDLINE_LINUX instead of GRUB_CMDLINE_LINUX_DEFAULT for kernel options.
  * Don't attempt to reinstall fwupdate-efi and fwupdate-libs on Fedora - not present in Fedora 31
  * Put OS names in alphabetical order when showing which OSs can't be modified.
  * Mount filesystems under /mnt/wxfixboot instead of /tmp/wxfixboot - fixes os-prober hang.

WxFixBoot (3.0.0):
  * Changes since 2.0.4:
  *
  * Support for Python 3.x and wxPython 4.x.
  * Support running the GUI as a normal user.
  * Mass refactoring and obeying Python style guide.
  * Make all modules in Tools more self-sufficient using more best-practice coding techniques.
  * Add new artwork made by Bhuna (https://www.instagram.com/bhuna42/).
  * Reduce the number of things injected into global namespace of modules - bad practice and makes code confusing.
  * Use the new getdevinfo module.
  * Various smaller bugfixes and improvements.
  * Fix a crash on Fedora when there's no DNF cache available.
  * Add support for checking HFS/HFS+ volumes (used by macOS).
  * Give reasons for why disks can't be checked.
  * Prevent a crash where the bootloader config file is present, but empty.
  * Prevent a crash where there are empty lines in the middle of a GRUB2 menu entry.
  * Remove the xhost hack and the authentication dialog (no longer needed).
  * Clean up the unit tests and make them more reliable.
  * Check getdevinfo version on startup.
  * Improve bootloader detection on Feodra systems.
  * Add support for checking for updates.
  * Don't unmount filesystems on startup any more - causes issues on live disks and Fedora.
  * Add warning for switching between GRUB2 and GRUB-UEFI on Fedora.
  * Read /etc/os-release to determine OS name instead of using mini python script.
  * Improve detection of different Windows versions (read the license file).
  * Create developer documentation (partial in this release).
  * Update and clarify privacy policy.
  * Mount /run in chroot - fixes some issues with Fedora.
  * Various other small fixes and improvements.

WxFixBoot (2.0.4):
  * Changes since 2.0.3:
  *
  * Diagnose and identify a fix for Fedora 28 (grub-bios and grub-efi).
  * Change the way grub2 for bios is identified on Fedora.
  * Don't unmount all filesystems on startup - causes issues with Fedora 28.
  * Check that everything now works as expected.
  * Note that Fedora 26 isn't supported in this build.
  * Make a warning that routinely occurs on Fedora less alarming.
  * Update about box to use domain webaddress.

WxFixBoot (2.0.3):
  * Changes since v2.0.2~update1:
  *
  * Fix for the emergency exit function, which sometimes failed to work or failed to save the log file.
  * Depress the authentication button upon hitting enter - stops a user from trying to authenticate multiple times in rapid succession.
  * Fix an issue when modifying bootloaders when the bootloader is unknown.
  * Warn the user against modifying EFI bootloaders if the partition they reside on was not found.
  * Enable LILO's "compact" option to speed the boot process up when using LILO.
  * Fix a bug very occasionally causing a crash in coretools.TearDownChroot().
  * Don't crash if an unpartitioned disk is present - pulled in from new getdevinfo module.
  * Fix some issues with the bootloader options window.
  * Improve handling of replacing an unknown / missing bootloader.
  * Fix issues with LILO and ELILO installation target.
  * Link to my website in the about dialog.

WxFixBoot (2.0.2):
  * Changes since v2.0.1:

  * Ignore error code 8 when doing startup filesystem check.
  * Fix freezes when doing an emergency exit.

WxFixBoot (2.0.1):
  * Changes since v2.0:

  * Interpret all cmdline input as UTF-8.
  * Try harder to get the correct LV filesystem paths.
  * Fix a bug related to the above.
  * Get all of the aliases for LVM disks in GetDevInfo.
  * Use Aliases to avoid confusion over which OS is the default one.
  * Tell user how to hide the boot menu if there's just 1 OS detected.
  * Enable support for hiding the boot menu.
  * Fix RootFS detection on Ubuntu installations that use LVM.
  * Display the above boot menu message more nicely.
  * If we can't get the OS name with the python script, use lsb_release -sd if possible (fixes detection on eg Devuan).
  * Attempt to veto shutdowns during operations.
  * Wait until the package manager isn't busy, rather than failing if it is.
  * Add the unit tests from DDRescue-GUI.
  * Write unit tests for GetDevInfo.
  * Sort of port BackendToolsTests from DDRescue-GUI to CoreTools.
  * Fix GetCapacityTest.
  * Fix Misc GetDevInfo stuff.
  * Fix CoreTools tests.
  * Write test for CoreTools.GetPartitionMountedAt().
  * Write DlgTools tests.
  * Write EssentialBackendTools tests.
  * Write test for WaitUntilPackageManagerNotInUse().
  * Write test for FindMissingFSCKModules().
  * Write test for FindCheckableFileSystems().
  * Write test for HandleFileSystemCheckReturnValues().
  * Separate the tests into subpackages.
  * Make a file to hold special dialog tools used during the tests.
  * Use the above in CoreToolsTests and DialogToolsTests.
  * Use it in HelperBackendToolsTests, and EssentialBackendToolsTests.
  * Stop dialogs from getting in the way during tests (use wx.Yield() to process events to close them).
  * Make test for DeterminePackageManager.
  * Make test for GetFSTabInfo.
  * Make test for DetermineOSArch.
  * Make test for GetOSNameWithLSB.
  * Write tests for AskForOSName.
  * Write test for CheckDepends.
  * Write test for CheckForLiveDisk.
  * Write test for GetOSs.
  * Write test for GetFirmwareType.
  * Write test for FinalCheck.
  * Test the tests (on Mint 18.1).
  * Handle bootloaders that don't have any menu entries (broken configuration).
  * Detect Windows.
  * Fix ME and XP detection.
  * Detect Mac OS X.
  * Prevent name duplication for Windows and OS X (causes WxFixBoot to "forget" other Windows/OSX OSs).
  * Fix issue detecting OS X 10.10 and later.
  * Test detection of OS X.
  * Fix low-importance bug detecting vfat filesystems on Ubuntu 14.04.
  * Improve reliability of default OS setter/getter.
  * All privacy policy to github.
  * Fix FindCheckableFileSystem test.
  * Fix GetOSs test.
  * Always specify a parent when displaying dialogs during unit tests to avoid weird/random errors.
  * Remove .py~, .pyc files from repo (unnecessary).
  * Test the unit tests on Ubuntu (all supported versions).
  * Fix waiting until YUM isn't busy.
  * Fix GetDevInfo tests on Fedora.
  * Test the unit tests on Fedora (all supported versions).
  * Test the unit tests on Parted Magic.
  * Fix checking if there is 1 or more Linux OS (OS X and Windows were being counted too, causing problems later).
  * Retest the unit tests on Ubuntu.
  * Add LICENSE file to github.
  * Fix a bug where the default OS choice is sometimes forgotten.
  * Fix incorrect LV/VG names.
  * Fix the default OS getter and setter.
  * Update the message prompting to hide the bootloader, because we now detect Mac OS X and Windows.

WxFixBoot (2.0):

  * Changes since v1.0.2:
  * Bring coding techniques up to date.
  * Use a new authentication dialog.
  * Change the splash screen to use a progress bar.
  * Get rid of the move old log files script.
  * Begin optimising startup scripts.
  * Move global function StartProcess into CoreTools.
  * Move functions DetermineOSArchitechure, CheckForLILO, CheckForGRUBBIOS into CoreStartupTools.
  * Move some thread dialog functions into DialogTools and test them.
  * Make a modified version of StartThreadProcess for later use.
  * Move the remaining dialog functions into DialogTools.
  * Get rid of the global StartProcess function.
  * Use tuples instead of lists where possible (read-only, and use less memory).
  * Move SetDefaults to MainStartupTools.
  * Move GetBootloader to MainStartupTools.
  * Move CheckForUEFIPartition to MainStartupTools.
  * Move CheckForGRUBEFI, CheckForELILO to CoreStartupTools.
  * Move FinalCheck to MainStartupTools.
  * Move the rest of the startup tools to their separate packages and modules.
  * Use sizers with InitWindow.
  * Use sizers with MainWindow.
  * Use sizers with SettingsWindow.
  * Use sizers with Bootloader Options Window.
  * Use sizers with ProgressWindow.
  * Move core backend tools to their separate file.
  * Move helper backend tools to their separate file.
  * Move essential backend tools to their separate file.
  * Create a Github repository.
  * Move all bootloader stuff into a separate package.
  * Rename MainBackendThread() to BackendThread()
  * Always name wx.Panels self.Panel.
  * Don't call subprocess directly.
  * Don't call mount directly in most places.
  * Use sizers with RestoreWindow.
  * Fix sizer glitch in SettingsWindow.
  * Pull in new GetDevInfo package from DDRescue-GUI v1.5.
  * Count operations in MainWindow.
  * Fix rescanning for bootloaders from BootloaderOptionsWIndow.
  * No longer depend on grep.
  * No longer depend on find.
  * Move some bootloader stuff to MainBackendTools.
  * Make sure each modules has the "from __future__ import x,y,z" imports.
  * Move HelperBackendTools().CheckInternetConnection() to EssentialBackendTools.
  * Always use Piping=True when calling StartThreadProcess() (preparation for switch to CoreTools().StartProcess).
  * Write docstrings for all functions/methods and classes.
  * Use "//" for integer division where possible.
  * Make Bootloader Options Window more user-friendly.
  * Fix crash on startup when using a BIOS bootloader (doesn't affect v1.0.2).
  * Save MBR to RAM instead of a temporary file in /tmp/wxfixboot/.
  * Get rid of the temporary directory (/tmp/wxfixboot).
  * Don't allow the user to specify partition schemes any more.
  * Rewrite/Add more logging messages.
  * Reduce Duplication in MainBackendTools.
  * Create CoreTools().IsMounted().
  * Modify GetDevInfo package to use dictionaries.
  * Keep more info about/disk/partition relationships.
  * Get partition schemes in GetDevInfo package.
  * Get FileSystem Types in GetDevInfo package.
  * Refactor GetDevInfo package.
  * Use GetDevInfo package on startup.
  * Start phasing out old device info collectors in favour of the GetDevInfo package.
  * Remove dependency on lsblk.
  * Rewrite CoreStartupTools().CheckForUEFIPartition().
  * Write an emergency exit function.
  * Fix UnicodeDecodeError while still showing all info in log file.
  * Design new Bootloader Options Window.
  * Pull in new outputbox code from DDRescue-GUI v1.5.
  * Enable support for the output box in CoreTools().StartProcess().
  * Don't use CoreBackendTools().StartThreadProcess().
  * Remove CoreBackendTools().StartThreadProcess().
  * Enable checking where partitions are mounted in CoreTools().IsMounted().
  * Performance Improvements and better error checking in MainBackendTools.
  * Write more error check and logging messages in.
  * Weight each startup operation to make the progressbar on the splash screen more accurate.
  * Write a function to return the partition mounted at a given mountpoint.
  * Refactor some of the startup scripts.
  * Get rid of MainStartupTools().GetRootFSAndRootDev().
  * Make MainStartupTools().GetLinuxOSs() use dictionaries.
  * Get rid of the 'PartitionListWithFSType' global variable.
  * Save LiveDisk in a dictionary instead of an independent global variable.
  * Get rid of the 'GPTInAutoPartSchemeList' and 'MBRInAutoPartSchemeList' global variables.
  * Get rid of the 'PartSchemeList' global variable.
  * Test badsector and quick fs check.
  * Change the way module functions are called to allow for conditional tests in MainWindow.CountOperations().
  * Test backing up boot sector and partition table.
  * Test restoring boot sector and partition table.
  * Don't use OSList any more.
  * More fixing and refactoring.
  * Don't hunt out kernels + initrds for LILO/ELILO any more.
  * Don't use DeviceList any more.
  * Don't use AutoDefaultOS any more.
  * Use new dictionary based OS format for DefaultOS variable.
  * Don't use DefaultOS any more.
  * Don't use AutoFirmwareType any more.
  * Don't use FirmwareType any more.
  * Move CoreBackendTools.GetPartitionUUID() to GetDevInfo.GetUUID().
  * Remove GetDevInfo.GetPartitions().
  * Move CoreBackendTools.GetDeviceID() to GetDevInfo.GetID().
  * Optimise GetDevInfo.
  * Don't use LinuxPartList any more.
  * Don't use OSListWithPackageManagers any more.
  * Don't use DisableBootloaderOperations any more.
  * Absorb HelperBackendTools.LookForAPTonPartition() into MainBootloaderTools.PrepareForBootloaderInstallation().
  * Refactor MainBootloaderTools.PrepareForBootloaderInstallation().
  * Absorb part of MainBootloaderTools.PrepareForBootloaderInstallation() into MainStartupTools.GetLinuxOSs().
  * Add experimental detection of Ubuntu-based live disks and Parted Magic.
  * Write a function to get the mountpoint of a given partition.
  * Detect live disks more reliably, including fedora-based ones.
  * Don't use OSsForBootloaderRemoval any more.
  * Don't use OSsForBootloaderInstallation any more.
  * Use custom dialog buttons (only possible on wxpython 3) where wanted, to help clarify messages.
  * Don't use RootFS or AutoRootFS any more.
  * Don't use BootloaderToInstall any more.
  * Test updating GRUB2.
  * Test reinstalling GRUB2.
  * Test installing LILO.
  * Test updating LILO.
  * Test reinstalling LILO.
  * Test updating GRUB-EFI.
  * Test reinstalling GRUB-EFI.
  * Rewrite the GetDevInfo package to parse XML output from lshw.
  * Speed up CoreTools.StartProcess().
  * Refactor and improve error handling in GetDevInfo package.
  * Test with installing ELILO.
  * Test with reinstalling ELILO.
  * Test with updating ELILO.
  * Start creating new bootloader options window and system info window.
  * Semi-finish implementing the design of the new bootloader options window.
  * Test with Parted Magic.
  * Changes since 2.0~pre1:
  * Make GetDevInfo work again in Ubuntu 12.04.
  * Don't use UEFIVariables any more.
  * Don't use RootDevice or AutoRootDevice any more.
  * Don't use Bootloader any more.
  * Don't use AutoBootloader any more.
  * Don't use PrevBootloaderSetting any more.
  * Don't use AutoUEFISystemPartition any more.
  * Don't UEFISystemPartition any more.
  * Don't use EmptyEFIPartition any more.
  * Remove "GPTDisks" from SystemInfo.
  * Remove "MBRDisks" from SystemInfo.
  * Start to create infrastructure for NewBootloaderOptionsWindow.
  * Add all the functions in CoreBackendTools to CoreTools.
  * Remove CoreBackendTools.
  * Add 1st bootloader info page to SystemInfoWindow.
  * Add 2nd bootloader info page to SystemInfoWindow.
  * Gather bootloader timeouts and global kernel options on startup.
  * Link /boot partitions and EFI partitions to each OS.
  * On EFI systems and with EFI Bootloaders, set BootloaderInfo[OS]["BootDisk"] to OSInfo[OS]["EFIPartition"].
  * Find the boot disk when LILO is the bootloader.
  * Start to implement finding boot disk with GRUB-LEGACY.
  * Add support for writing lines to a process's stdin in CoreTools.StartProcess().
  * Get boot records for all disks and partitions on startup.
  * Save boot record strings on startup.
  * Write a function to find GRUB2 and GRUB-LEGACY.
  * Get GRUB2's menu entries.
  * Remove deprecated functions in GetDevInfo package.
  * General refactoring and error checking improvements.
  * Write more logging messages in BootloaderConfigObtainingTools.
  * Remove CoreStartupTools.MountUEFIPartition() in favour of using CoreTools.MountPartition().
  * Remove the old bootloader info getter from BootloaderTools.
  * Add experimental support for finding the default OS for GRUB2.
  * Write a GRUB2 menuentry parser.
  * Fix a bug in CoreTools.Find() where not all files are searched in any given folder.
  * Fix detection of GRUB2 default OS.
  * Get kernel options for each of GRUB2's menuentries.
  * Experimental menuentry parsing for GRUB-LEGACY.
  * Fix a bug when parsing global kernel options with GRUB2.
  * Experimental menuentry parsing for LILO/ELILO.
  * Write comments and logging messages in menuentry parsing functions.
  * Test new bootloader config getting functions on LILO.
  * Enable detecting default OS on LILO and ELILO.
  * Test new bootloader config getting functions on ELILO.
  * Disable old bootloader info getter.
  * Remove old bootloader info getter.
  * Make GUI elements in SystemInfoWindow work.
  * Fix a bug where the background image doesn't show on the startup window on Ubuntu > 14.04 (WxPython 3 or higher).
  * Add IsModifyable to SystemInfo and NewBootloaderOptionsWindow.
  * Remove incorrect UEFI variables warning on BIOS systems.
  * Remove SystemInfo["AutoUEFISystemPartition"], SystemInfo["PrevBootloaderSetting"], SystemInfo["OSsWithPackageManagers"], and SystemInfo["EmpyEFIPartition"].
  * Remove all backup/restore functionality relating to partition tables (better tools such as GParted are available for this).
  * Remove dependency on "lsb_release", instead using the "platform" module built into python2 for determining OS names.
  * Add experimental LVM support.
  * Write event-handling code for the new bootloader options window.
  * Initialise GUi state and settings for NewBootloaderOptionsWindow.
  * Load GUI settings in NewBootloaderOptionsWindow.
  * Set GUI state in NewBootloaderOptionsWindow.
  * Save settings in NewBootloaderOptionsWindow.
  * Save GUI state in NewBootloaderOptionsWindow.
  * Make NewBootloaderOptionsWindow respond correctly to changes in the OS selection box.
  * Count new bootloader operations in MainWindow.CountOperations.
  * Count operations after closing NewBootloaderOptionsWindow.
  * Modify MainBackendTools.RemoveOldBootloader to use new bootloader settings.
  * Modify MainBackendTools.InstallNewBootloader to use new bootloader settings.
  * Modify MainBackendTools.SetNewBootloaderConfig to use new bootloader settings.
  * Do a quick test to make sure updating GRUB is working.
  * Don't use SystemInfo["BootloaderToInstall"] any more.
  * Remove the old bootloader options window.
  * Rename NewBootloaderOptionsWindow to BootloaderOptionsWindow.
  * Remove everything previously used for reinstalling the bootloader.
  * Remove everything previously used for updating the bootloader.
  * Remove unneeded GUI elements from SettingsWindow.
  * Remove SystemInfo["AutoBootloader"].
  * Get rid of the BootloaderTimeout variable.
  * Remove the bootloader timeout spinner from SettingsWindow.
  * Remove SystemInfo["AutoRootDevice"].
  * Remove SystemInfo["RootDevice"].
  * Remove the root device choice box from SettingsWindow.
  * Remove MainBootloaderTools.Manage Bootloaders().
  * Remove SystemInfo["RootFS"].
  * Remove SystemInfo["DefaultOS"].
  * Remove SystemInfo["Bootloader"].
  * Remove the installed bootloader choicebox from SettingsWindow.
  * Get rid of the KernelOptions variable.
  * Reduce duplication in CoreTools.IsMounted().
  * General maintenance.
  * Prepare to support Fedora in BootloaderInstallationTools.
  * Prepare to support Fedora in BootloaderRemovalTools.
  * Add proper LVM support in GetDevInfo.
  * Fix a few bugs in GetDevInfo.
  * Start to support Fedora.
  * Add kernel options settings in BootloaderOptionsWindow.
  * Mount filesystems in a temporary directory instead of in /mnt.
  * Unmount EFI partition after modifying EFI bootloaders.
  * Remove BootloaderRemovalTools.
  * Remove BootloaderInstallationTools.
  * Tidy up InitThread.
  * Don't use BackupBootSector any more.
  * Add comments and logging messages in BootloaderOptionsWindow.
  * Add basic functionality for restoring the bootloader in BootloaderOptionsWindow.
  * Remove EssentialBackendTools.BackupBootSector.
  * Remove EssentialBackendTools.RestoreBootSector.
  * Remove the last of the abstraction code for operation-running functions.
  * Don't use "BootSectorFile" any more.
  * Don't use "RestoreBootsector" any more.
  * Don't use "BootSectorBackupType" any more.
  * Don't use "BootSectorTargetDevice" any more.
  * Get rid of RestoreWindow.
  * General maintenance.
  * General maintenance and improve default OS detection with GRUB2.
  * Remove SystemInfo["Devices"].
  * Remove SystemInfo["LinuxPartitions"].
  * Remove MainStartupTools.SoftSomeInfo().
  * Don't use chroot in CoreStartupTools.DetermineOSArch().
  * Put package manager detection code in CoreStartupTools.DeterminePackageManager() and refactor it.
  * Make detection of UEFI firmware more robust.
  * Rename SystemInfo["DetectedFirmwareType"] to SystemInfo["FirmwareType"].
  * Remove Settings["FirmwareType"].
  * General maintenance in MainStartupTools and MainBackendTools.
  * Refactoring and general maintenance in MainBackendTools.
  * Refactoring and general maintenance in HelperBackendTools.
  * Combine both the filesystem check functions in EssentialBackendTools to make EssentialBackendTools.FileSystemCheck().
  * Improve default OS detection with grub2.
  * Fixes for Fedora in CoreTools.SetUpChroot().
  * Bootloader config detection fixes for Fedora.
  * LVM fixes.
  * LVM fix so IsCurrentOS works on Fedora.
  * Fix filesystem check.
  * Fix bug in Authentication dialog.
  * Fix in GetDevInfo.
  * Fixes in GRUB2 menuentry parsing.
  * Ubuntu: Use DEBIAN_FRONTEND=noninteractive when purging bootloaders.
  * Fix in LILO/ELILO config getting.
  * Comment out existing menu entries when configuring ELILO/LILO.
  * Fix some more bootloader config obtaining bugs.
  * Make icon appear in about box in Fedora.
  * Run startup scripts again after restarting WxFixBoot.
  * Remove SystemInfo["UEFISystemPartition"].
  * General maintenance and fixes.
  * Use "arch" to determine OS architecture.
  * Test updating and reinstalling grub2 on Fedora 24.
  * Prepare to use a menu with ELILO.
  * Fix layout glitch in ProgressWindow.
  * Allow installing EFI bootloaders on BIOS systems.
  * Add pty support.
  * Remove pty support.
  * Fix output problems with badblocks.
  * Fix several small issues.
  * Release 2.0~pre2.
  * Fix bug when switching to EFI bootloaders from MBR ones.
  * Remove SettingsWindow, and get rid of the "OptionsDlg1Run" global variable.
  * Get rid of BLOptsDlgRun.
  * First steps for backing up and restoring bootloader config.
  * Small misc changes.
  * Remove code that displays unneeded multi-choice dialogs.
  * Refactor disk checking code, and make it use dictionaries.
  * Move MainBootloaderTools.ManageBootloader() to MainBackendTools.
  * Get rid of MainBootloaderTools.
  * Implement restoring bootloader config.
  * Fix bugs with default OS selection box.
  * Disable partial support for detecting Windows.
  * Build error detection into bootloader config backup and restore code.
  * Use UseChroot in bootloader config setting functions.
  * Partially implement support for disabling bootloader operations.
  * Don't ignore the "Show Diagnostic Terminal Output" checkbox (ignored since work on 2.0 started).
  * Fix a bug with UUID detection.
  * Improve grub2 menuentry parsing.
  * Rewrite the grub2 menu parser to use recursive calls, reducing duplications and increasing reliability and speed.
  * Refactor GetGRUB2Config() and improve GRUB2 default OS detection.
  * Implement checking OS modifiability.
  * Replace SystemInfo["UserFriendlyOSNames"] with SystemInfo["ModifyableOSs"].
  * Refactor ProgressWindow.UpdateOutputBox().
  * General maintenance and better error handling in bootloader operations.
  * Match Bootloader-specific default OS to WxFixBoot's detected OSs.
  * Improve GRUB2 default OS detection.
  * Improve LILO/ELILO config obtaining and default OS detection.
  * Extensive refactoring and rewriting in BootloaderConfigSettingTools().
  * Make ELILO & LILO config getting & setting more robust.
  * Improve error handling in MainBackendTools().
  * General maintenance.
  * Use dictionaries to save settings on MainWindow and get rid of MainStartupTools.SetDefaults().
  * Auto-set GRUB2 default OS without asking the user.
  * Fix + reenable internet connection checking.
  * Reduced duplication in GRUB2 menu entry parser.
  * Remove unneeded code from MainStartupTools.FinalCheck().
  * Improve error handling when importing bootloader config.
  * Make restarting more robust.
  * Make GRUB2 menu entry parsing work with older GRUB2 versions.
  * Enable a text menu for ELILO.
  * Fix a GUI bug when there's more than one OS to modify.
  * Fix a progress bar glitch when doing 2+ operations at once.
  * Find grub.cfg on Fedora with EFI.
  * Enable SystemInfoButton on BootloaderOptionsWindow.
  * Fix finding Fedora's grubenv in chroot.
  * Fix detecting correct grub (EFI or BIOS) on Fedora.
  * General maintenance.
  * General maintenance and refactoring.
  * Run badblocks on filesystems that don't have bad sector checkers.
  * Fix terminal output formatting problems with Ubuntu >= 16.04.
  * Fix problems setting GRUB2 default OS.
  * GRUB: Comment out GRUB_DEFAULT_LINUX if it exists in /etc/default/grub.
  * Fix setting Fedora as GRUB2 default OS.
  * Warn user about LILO + ELILO bad multi OS support & fix some GUI bugs.
  * Major refactoring in BootloaderConfigObtainingTools.
  * Reorganise functions in BootloaderOptionsWindow().
  * Fix a bug in CoreTools.DeterminePackageManager().
  * Make the OS detection code work on more OSs.
  * Make GRUB-LEGACY menu entry parser work on Ubuntu & Fedora.
  * Don't allow the user to modify GRUB-LEGACY.
  * Silence annoying restart errors.
  * Properly fix them with wx.Yield().
  * Make OS revert buttons work.
  * Remove revert all changes button.
  * Only allow installing bootloaders that have been detected for each OS.
  * Handle unexpected error while starting up and running operations.
  * Distract the user with ProgressTextHandlerThread() if needed.
  * Remove duplicate error handler in InitThread().
  * Get GRUB-LEGACY's default OS.
  * General refactoring & better error handling in MainBackendTools()
  * Improve startup speed.
  * Fix a GUI bug.
  * Fix GRUB2-BIOS config when booted with EFI.
  * Fix a bug when restoring bootloader config.
  * Make detecting available bootloaders faster & more robust.
  * Make HelperBackendTools.CopyUEFIFiles() more robust,
  * Rename CopyUEFIFiles() to ManageUEFIFiles() and make it remove unneeded UEFI files.
  * Fix a bug in BootloaderConfigSettingTools.
  * Remove diagnostic printing of information.
  * Partway finish rewriting the system report generator.
  * Finish rewriting system report generator.
  * Fix some bugs in the report generator.
  * Enable report generator by default and warn user about disabled bootloader operations if required.
  * Make sure boot record strings object is always a list.
  * Remove unneeded dependencies and remove CoreTools.Find().
  * Don't make dictionaries accessible when not required.
  * Make privacy policy window.
  * Make sure GRUB2 installs to the right disk.
  * Spit python + wxpython version into log file on startup.
  * General maintenance.
  * Check internet connection again if bootloader operations fail.
  * Don't overwrite old menuentries when setting GRUB2 default OS.
  * Make recovery boot options for ELILO + LILO.
  * General maintenance.
  * Enter final testing.
  * Log tracebacks of errors.
  * Finish test privacy policy and get window working.
  * Use a horrid mishmash of HTML 5 and HTML 4 to make it work in wxpython 2.8 and 3.x.
  * Hide OS info by default in BootloaderOptionsWindow.
  * MainBackendTools & MainStartupTools: Always unmount EFI partitions before /boot partitions.
  * Always set GRUB2 install target (e.g. i386-pc).
  * Stop user from starting more than one instance of WxFixBoot.
  * Fix HelperBackendTools.WriteFSTABEntryForUEFIPartition().
  * Make sure OS's EFI partition is mounted before getting GRUB2 config.
  * Make matching GRUB2 default OS more reliable.
  * Don't run grub2-install on Fedora with GRUB-UEFI.
  * Fix GRUB_UEFI config when booted in BIOS mode.
  * Test on Fedora 25.
  * Fix LILO kernel options detection.
  * Test on Ubuntu 16.10.
  * Test on Fedora 24.
  * Test on Ubuntu 16.04.
  * Test on Fedora 23.
  * Only fix GRUB2 config on Fedora.
  * Don't write FSTAB entries for EFI partitions.
  * Test with Ubuntu 14.04.
  * Only specify target option with GRUB2-BIOS when running on Fedora.
  * Test on Ubuntu 12.04.
  * Fix System report generator on Parted Magic.
  * Make current operation text more OS-specific.
  * Fix typo preventing warning about LILO + ELILO multi OS support.
  * Test on Parted Magic.
  * Test FS Check.
  * Fix warning for ELILO + LILO.
  * Re-evaluate dependency check.
  * Update online changelog.

WxFixBoot (1.0.2):

  * Fix a bug that prevents WxFixBoot from starting on Ubuntu 15.04.
  * Use -s option when calling gnu parted, preventing a freeze if parted attempts to interact with it.
  * Handle empty linux partitions properly without presenting the user with an empty OS selection box.
  * Fix a few other startup bugs that could prevent the gui from starting.

Changes since 1.0~rc4:

  * Fixed the progressbar glitch mentioned on 1.0~rc4 release page.
  * Fixed an issue in Options Window 1, where the lines drawn on the screen occasionally disappeared.
  * Align all the text in the windows dynamically, so it should look and work okay with different font sizes.
  * Remove all mentionings of Fedora/RPM in the GUI.
  * Enable saving system report.
  * Enable saving terminal output in the report.
  * Make sure bootloader operations skip if no OS is marked for bootloader installation.
  * Write non-mandatory detailed license info in the about box.
  * Open the about box on startup.
  * Make sure that text strings don't exceed the borders of the window. If they do, resize the window.
  * Use uuids where possible for LILO and ELILO config.
  * Fix a bug when setting Bootloader configuration, where some low-importance settings aren't set.
  * Ensure compatibility with WxPython 3.0 (Ubuntu 14.10)
  * Give a warning in progresswindow if no operations are to be done.
  * Write /etc/fstab entries to keep the UEFI partition mounted if needed, after EFI bootloader installation.
  * When configuring EFI bootloaders, backup Windows's EFI files if they exist.
  * When configuring EFI bootloaders, copy EFI files to /EFI/boot/bootx64.efi, to make sure the system boots even on buggy firmware.
  * Enable installing the bootloader in more than one OS.
  * Revise the dialog messages, making the GUI more intuitive, and advice more helpful.
  * Finish all tasks, and begin final test.
  * Test updating bootloaders (installed in the current OS) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test reinstalling bootloaders (installed in the current OS) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test switching between bootloaders (installed in the current OS) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test checking all filesystems (both quick and thorough) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test Backing up and restoring partition tables and bootsectors in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Find a serious issue delaying the release!
  * Semi-fix the above issue, and make debugging much easier as a consequence.
  * Get internet connections working and tested in chroot.
  * Change variable names to make the code easier to maintain and navigate.
  * Test the internet connection before performing any operations.
  * Fix a bug where wxfixboot incorrectly handles errors when no linux partitions were found.
  * Use IDs when specifying the boot device with LILO and ELILO.
  * Fix a bug where wxfixboot won't start if it doesn't find the name of the current os.
  * Make sure the package lists are up to date before attempting to install any packages.
  * Fix a bug with elilo that prevented it from installing via chroot.
  * Test all bootloader operations work via chroot.
  * Fix a UI bug in the Options Window.
  * Check everything again.

WxFixBoot (1.0.1):

  * Added support for Parted Magic.
  * Fix a bug where WxFixBoot freezes when checking disks.
  * Fix a bug when remounting filesystems after the disk check, and they aren't remounted because the wrong function is called.

Changes since 1.0~rc4:

  * Fixed the progressbar glitch mentioned on 1.0~rc4 release page.
  * Fixed an issue in Options Window 1, where the lines drawn on the screen occasionally disappeared.
  * Align all the text in the windows dynamically, so it should look and work okay with different font sizes.
  * Remove all mentionings of Fedora/RPM in the GUI.
  * Enable saving system report.
  * Enable saving terminal output in the report.
  * Make sure bootloader operations skip if no OS is marked for bootloader installation.
  * Write non-mandatory detailed license info in the about box.
  * Open the about box on startup.
  * Make sure that text strings don't exceed the borders of the window. If they do, resize the window.
  * Use uuids where possible for LILO and ELILO config.
  * Fix a bug when setting Bootloader configuration, where some low-importance settings aren't set.
  * Ensure compatibility with WxPython 3.0 (Ubuntu 14.10)
  * Give a warning in progresswindow if no operations are to be done.
  * Write /etc/fstab entries to keep the UEFI partition mounted if needed, after EFI bootloader installation.
  * When configuring EFI bootloaders, backup Windows's EFI files if they exist.
  * When configuring EFI bootloaders, copy EFI files to /EFI/boot/bootx64.efi, to make sure the system boots even on buggy firmware.
  * Enable installing the bootloader in more than one OS.
  * Revise the dialog messages, making the GUI more intuitive, and advice more helpful.
  * Finish all tasks, and begin final test.
  * Test updating bootloaders (installed in the current OS) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test reinstalling bootloaders (installed in the current OS) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test switching between bootloaders (installed in the current OS) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test checking all filesystems (both quick and thorough) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test Backing up and restoring partition tables and bootsectors in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Find a serious issue delaying the release!
  * Semi-fix the above issue, and make debugging much easier as a consequence.
  * Get internet connections working and tested in chroot.
  * Change variable names to make the code easier to maintain and navigate.
  * Test the internet connection before performing any operations.
  * Fix a bug where wxfixboot incorrectly handles errors when no linux partition were found.
  * Use IDs when specifying the boot device with LILO and ELILO.
  * Fix a bug where wxfixboot won't start if it doesn't find the name of the current os.
  * Make sure the package lists are up to date before attempting to install any packages.
  * Fix a bug with elilo that prevented it from installing via chroot.
  * Test all bootloaders operations work via chroot.
  * Fix a UI bug in the Options Window.
  * Check everything again.

WxFixBoot (1.0):

  * Initial stable release.

Changes since 1.0~rc4:

  * Fixed the progressbar glitch mentioned on 1.0~rc4 release page.
  * Fixed an issue in Options Window 1, where the lines drawn on the screen occasionally disappeared.
  * Align all the text in the windows dynamically, so it should look and work okay with different font sizes.
  * Remove all mentionings of Fedora/RPM in the GUI.
  * Enable saving system report.
  * Enable saving terminal output in the report.
  * Make sure bootloader operations skip if no OS is marked for bootloader installation.
  * Write non-mandatory detailed license info in the about box.
  * Open the about box on startup.
  * Make sure that text strings don't exceed the borders of the window. If they do, resize the window.
  * Use uuids where possible for LILO and ELILO config.
  * Fix a bug when setting Bootloader configuration, where some low-importance settings aren't set.
  * Ensure compatibility with WxPython 3.0 (Ubuntu 14.10)
  * Give a warning in progresswindow if no operations are to be done.
  * Write /etc/fstab entries to keep the UEFI partition mounted if needed, after EFI bootloader installation.
  * When configuring EFI bootloaders, backup Windows's EFI files if they exist.
  * When configuring EFI bootloaders, copy EFI files to /EFI/boot/bootx64.efi, to make sure the system boots even on buggy firmware.
  * Enable installing the bootloader in more than one OS.
  * Revise the dialog messages, making the GUI more intuitive, and advice more helpful.
  * Finish all tasks, and begin final test.
  * Test updating bootloaders (installed in the current OS) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test reinstalling bootloaders (installed in the current OS) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test switching between bootloaders (installed in the current OS) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test checking all filesystems (both quick and thorough) in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Test Backing up and restoring partition tables and bootsectors in Ubuntu 12.04, Ubuntu 14.04, and Ubuntu 14.10.
  * Find a serious issue delaying the release!
  * Semi-fix the above issue, and make debugging much easier as a consequence.
  * Get internet connections working and tested in chroot.
  * Change variable names to make the code easier to maintain and navigate.
  * Test the internet connection before performing any operations.
  * Fix a bug where wxfixboot incorrectly handles errors when no linux partition were found.
  * Use IDs when specifying the boot device with LILO and ELILO.
  * Fix a bug where wxfixboot won't start if it doesn't find the name of the current os.
  * Make sure the package lists are up to date before attempting to install any packages.
  * Fix a bug with elilo that prevented it from installing via chroot.
  * Test all bootloaders operations work via chroot.
  * Fix a UI bug in the Options Window.
  * Check everything again.

WxFixBoot (1.0~rc4):

Important changes:

  * Fixed various small problems,
  * Use the icon in /usr/share/pixmaps instead,
  * Stop using wx.lib.pubsub, and instead use direct calls using wx.CallAfter, saving disk space and imrpoving memory usage and speed,
  * Changed order of startup scripts, and unmount FSes before checking for errors,
  * Patched and improved EFI partition detection and EFI partitions are now mounted at /boot/efi, with other FSes in the way being unmounted first,
  * Fixed occaisional hang on exit from MainWindow(),
  * Fix issues with warnings related to updating and reinstalling bootloaders,
  * Change and improve the layout of ProgressWindow,
  * Remember lines of terminal output when the outputbox is closed, and add them again when it's opened, avoiding forgetting output,
  * Monitor the last 5 lines for duplication instead, preventing duplicated output in the outputbox (obsolete now, using pipes, see below),
  * When opening and closing outputbox, preserve the state of the buttons on ProgressWindow(),
  * Add support for EFI partition selection once the GUI is started, including an option for none.
  * Fix problem restarting wxfixboot, where program exits.
  * Remove test operations code, including progressbar test.
  * Rewrite progressBar management code.
  * Autodetect grub-legacy/grub2 without asking the user which is present.
  * In InitThread and MainBackendThread use seperate thread methods for message dialog setup and teardown, saving 100 lines of code!!!
  * Patch code in InitThread to improve error-robustness.
  * Fix a few problems in OptionsWindow2(), improving behaviour.
  * Stop the user running any operations until they've checked the settings.
  * Various other fixes to EFI partition management.
  * Write code to determine the package managers (YUM/APT) on any OSes (except live disks).
  * Finally manage to install elilo and lilo on real systems (virtualbox's EFI implementation is unreliable, and it doesn't like lilo or elilo ** Got it working reliably now, see below)
  * Determine packages needed (YUM and APT) for installation/removal of bootloaders.
  * Save partition schemes for all HDDs, and use a very clever way of setting them and remembering which ones have been set manaully.
  * Finished partition table and boot sector restoration dialogs completely.
  * Refactored and simplified various code, saving a lot of lines and disk space, and improving efficency.
  * Determine required fsck modules, and create a list of missing ones, helping with file system checking.
  * Quick File System check implemented for most filesystems, though it needs refinement,
  * Bad sector check implemented for vfat/fat32/fat16 only, but codebase there for other filesystems.
  * Partition Table and Boot Seector backup types can now be autodetermined (GPT or MBR).
  * Refactor and Refine bad sector check and quick fs check.
  * Refactor and speed-up OS detection.
  * Program exit sequence fully.
  * Quick FS and bad sector check work with most filesystems now (xfs, jfs, reiserfs, ext2/3/4, fat32/fat16, minix).
  * Use direct program-to-program pipes to manage updating the output box now, resolving some major issues with missing/incomplete output, and increasing stability.
  * Added comments where needed, and written more debug messages.
  * Better detection of GRUB versions (grub2-bios or legacy),
  * Offer to save existing log files to /var/wxfixboot/wxfxboot.log.old, or delete them, preventing ridiculously long log files with repeated runs.
  * Test the pipes (they work just fine!)
  * Figure out how to get config for LILO and ELILO (Also all GRUB versions (Legacy, 2 and EFI)).
  * Write and test function to obtain LILO, and ELILO config.
  * Determine which OSes need the bootloader removed, and ask the user where to install the new one.
  * Write methods to set up and tear down chroot for each OS.
  * Allow piping with shell=True in MainBackendThread().StartThreadProcess().
  * Write and test functions to get grub-legacy config.
  * Change detection order inInitThread().GetBootLoader(), so that EFI bootloaders are looked for first, increasing the chance of finding the correct one (before if BIOS bootloader was still in the MBR, it would be misdetected).
  * Update Quick FS Check and Bad Sector Check to handle return values, with a new function.
  * Enable remount success check in Quick FS Check and Bad Sector Check.
  * Revised logging info in the startup scripts, making it much easier to debug wxfixboot.
  * Write more than 4000 lines of code in total for WxFixBoot!
  * Update current Operation text in the disk checks.
  * Align the text perfectly on ProgressWindow().
  * Enable determining the architecture of OSes in InitThread().GetLinuxOSes() and save them in the OS name.
  * Refactor the startup scripts. Again!
  * By refactoring the startup scripts, intoduce new features, remove unnecessary code, add new features, and speed it all up again! And also,
  * Fix the language releated bug (no 1353713) in the startup scripts.
  * Write function to remove GRUB Legacy
  * Write function to remove GRUB2
  * Write function to remove LILO
  * Write function to remove ELILO
  * Write function to remove GRUB2-EFI and GRUB-Legacy-EFI.
  * Split MainBackendThread().RemoveOldBootloaders() into one function to serve that purpose, and another to get the config.
  * Finish MainBackendThread().GetOldBootloaderConfig()
  * Change all instances of ShowThreadInfoDlg, to ShowThreadMsgDlg, allowing different types of thread dialogs to be shown (info, warning, error), and also modify the other thread dialog function to enable the setting of titles from the threads too.
  * Test MBR and GPT restore and backup commands work reliably.
  * Write function to install GRUB2
  * Write function to Install GRUB2-EFI
  * Write function to install LILO
  * Write function to install ELILO
  * Find a way of setting the default OS in GRUB2
  * Include better error checking in MainBackendThread() unmount and remount functions.
  * Change some terminology to make wxfixboot easier to use.
  * Refactor the entire program, because it was getting difficult to manage, by:
  * Using default options and keyword arguments in all function with more than one argument passed to them,
  * Combining RestBootSetcorWindow and RestPartTableWindow, to make two visually identical, but more space and memory efficent dialogs, residing in one function.
  * Cutting code duplication,
  * Removing unnecessary code in the startup script, bringing the speed up,
  * Reorganizing all of the functions in MainBackendThread(),
  * Not importing uneeded modules, reducing memory usage,
  * Adding more logging statements and more comments.
  * Write function to set GRUB2 config.
  * Write function to set LILO config.
  * Write function to set ELILO config.
  * Never allow installing EFI bootloader without an EFI partition,
  * Enable showing diagnostic terminal output.
  * Enable backing up and restoring the partition table.
  * Enable backing up and restoring the bootsector.
  * Make MainBackendThread().UnmountPartition() check if filesystems are unmounted before trying to unmount them.
  * As above, but with remounting RO and RW.
  * Use keywords and default values with functions, making the code tidier and easier to manage.
  * Make sure WxFixBoot can handle seperate EFI partitions,
  * Fix a problem that prevented piping output,
  * Change some terminology to make WxFixBoot easier to use.
  * Combine restbootsector window and restparttablewindow, saving space.
  * Write logging info in the new MainBackendThread functons.
  * Write current operations text calls in the MainBackendThread's functions.
  * Write progressbar calls into Main Backend Thread.

WxFixBoot (1.0~rc3):

  * Various UI code fixes and improvements
  * Various fixes to thread code and background scripts, making wxfixboot more stable and able to handle and avoid more errors.
  * The OnCheckBox() method of MainWindow() has been split into a manager method (to insure the checkboxes don't allow dangerous options), still called OnCheckBox(), and a save method called SaveMainOptions(). This has an enormous list of advantages, to many to list here. It includes the ability to remember the settings after looking at options windows, and the code is now MUCH easier to read!
  * Fixes and additions to startup scripts, including
  * Enable showing which dependencies are missing, if any are,
  * Handle junk in command output more effectively, avoiding errors,
  * Increase speed in some cases.
  * Output Box included,
  * Now outputbox with normal terminal-like colour scheme (white text on a black background).
  * Progress bars for operations screen semi-operational.
  * Now includes test for the outputbox and status messages.
  * Outputbox now works with openbox.
  * It now handles grub legacy better (but won't reinstall or update it).
  * Non-device entries are now removed in RootFS selections.
  * Tons of important fixes and improvements in GUI code, including
  * Newly arranged Options dlg,
  * Patched firmware dialog, with better handling of GRUB Legacy, and it now respondes the same way when updating the bootloader as when it reinstalls it.
  * Improved Options dlg, which can now recall previous settings and update itself with that info,
  * New Restore bootsector dialog,
  * New restore partition table dialog.
  * New OutputBox manager thread, fully and inteligently programmed to update the output box reliably and quickly without duplicating or missing lines of output.
  * Logger is now operational, and text to log is now entered.
  * Now includes cmdline options for debug and verbose logging.
  * The startup scripts no longer print to the terminal, instead their output is logged in debug mode.
  * All GUI work is now finished.

WxFixBoot (1.0~rc2):

  * No changelog available.

WxFixBoot (1.0~rc1):

  * No changelog available.

WxFixBoot (0.9):

  * Initial preview release.
