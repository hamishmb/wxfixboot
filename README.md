# WxFixBoot

This repository holds WxFixBoot, which is available under the GNU GPLv3+.

Description of Package
======================
A utility to assist with fixing the bootloader on a computer quickly.

Distribution Packages
=====================

You can find these at https://www.launchpad.net/wxfixboot or https://www.hamishmb.com/html/downloads.php?program_name=wxfixboot.

Documentation
=============
This can be found at https://www.hamishmb.com/html/Docs/wxfixboot.php.

Running The Tests
=================

These have to be run as the superuser.

The process for running these can be done on both Python 2 and Python 3.

Without Coverage Reporting
--------------------------
Run:

"sudo python3 ./tests.py"

or:

"sudo python2 ./tests.py"

With Coverage Reporting
-----------------------
Make sure you have installed Coverage.py using pip or your package manager.

Run:

"sudo python3 -m coverage run --rcfile=./.coveragerc ./tests.py"

or:

"sudo python2 -m coverage run --rcfile=./.coveragerc ./tests.py"

To run the tests. Then run:

"sudo python3 -m coverage html"

or:

"sudo python2 -m coverage html"

To see the report.
