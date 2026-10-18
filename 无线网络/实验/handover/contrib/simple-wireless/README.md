## Simple wireless module for ns-3

### Contents

`simple-wireless` has the following contents:

```
simple-wireless/:
  /doc
  /examples
  /model
  wscript
  README

simple-wireless/doc:
  simple-wireless.rst

simple-wireless/examples:
  directional_test.cc
  error_model_test.cc
  fixed_contention_test.cc
  mixed_directional_network.cc
  multiple_interface_example.cc
  queue_test.cc
  wscript

simple-wireless/model:
  drop-head-queue.cc
  drop-head-queue.h
  priority-queue.cc
  priority-queue.h
  simple-wireless-channel.cc
  simple-wireless-channel.h
  simple-wireless-net-device.cc
  simple-wireless-net-device.h
```

** Please refer to the file simple-wireless.rst in the /doc folder for more information about this model.**

### Installation Instructions

(assumes `ns-3` is already installed; see below for NS3/DCE installation instructions)

These installation instructions have been updated for the `ns-3.29` release.

1. Install the simple wireless in `ns-3` source using one of these methods:
    1. Copy the files directly to the `src` or `contrib` directory: `src/simple-wireless` or `contrib/simple-wireless` (either works the same way), or
    2. Use a softlink to your location of `simple-wireless` to create the `ns-3` directory `src/simple-wireless` or `contrib/simple-wireless`, or
    3. Download using `bake`
     
2. Add the `simple-wireless` as a module in the wscript used to build your `ns-3` scenario.  For example:
```
       def configure(conf): 
          ns3waf.check_modules(conf, ['core', 'internet', 'simple-wireless'], mandatory = True)

       def build(bld):
          bld.build_a_script('dce', needed = ['core', 'internet', 'dce', 'mobility', 'simple-wireless'],
          target='bin/my_test_script',
          cxxflags=['-std=c++0x'],
          source=[ my_test_script.cc'] )
```

3. Rebuild `ns-3` being sure to enable examples if you want to run the example models provided with the Simple Wireless model

### Miscellaneous Notes

* The Simple Wireless model available here is compatible with `ns-3.29`.
* The Simple Wireless model available at MIT-LL github site has been run with NS3.22/DCE1.5, NS3.21/DCE1.4 and NS3.20/DCE1.3
* The PriorityQueue uses libpcap to classify control packets so this must be installed to use priority queues.

### Installation Instructions for NS3/DCE

**Note:** The following instructions pertain to the older v1.0 release.

The Simple Wireless model works in NS3.20/DCE1.3, NS3.21/DCE1.4 and NS3.22/DCE1.5. 
If you have any of these versions currently installed you do not need to install a different version. 
The instructions below are for installing NS3.22 and DCE1.5 release but it is not necessary to install
these if you have an earlier, compatible version already installed.

NOTE: It is assumed that DCE will be installed at ~/dce

1. Install Bake from your home directory
```
      hg clone http://code.nsnam.org/bake bake
```

2. Set path variables. Add the following lines to .profile:
```
           BAKE_HOME="$HOME/bake"
           PATH="$PATH:$BAKE_HOME"
           PYTHONPATH="/usr/lib/python2.7:$BAKE_HOME"
```

3. Execute the .profile:

```
           . .profile
```

4. Increase file descriptor limit to 2048
    * To check the current value:  	`$ ulimit –n`
    * To change the current value: 	`$ ulimit –n 2048`

5. Create a directory for DCE
```
      mkdir dce 
```

6. Configure, download and build DCE 1.5 (note: this automatically includes ns3.22)
```
      cd dce
      bake.py configure -e dce-ns3-1.5
      bake.py download    [See note below]
      bake.py build
```
   During download and build, you may run into missing packages. If so, install them using:

```
   sudo apt-get install xxxx  (where xxxx is the name of the missing package)
```
   Then after installing re-run the download or build command before proceeding to the next step.

   If the gccxml package is missing, the build may complain about pybindgen instead.  Install gccxml and the pybindgen problem will probably go away. 

   To diagnose a build failure, you may need to use the –vvv flag to get more information:
```
        bake.py build -vvv
```
   NOTE: Some of the package names may not match what the dce install says is missing. Examples:

```
        DCE name                Actual Install Name
        --------------------    -------------------
        pybindgen-0.17.0.868    bzr
        qt4                     qt4-dev-tools
        lib_debug               libc6-dbg
        pygraphviz              python-pygraphviz
        pygoocanvas             python-pygoocanvas
```


### Distribution Statement

```
 Copyright (C) 2010 University of Washington
 Copyright (C) 2015 Massachusetts Institute of Technology

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License version 2 as
 published by the Free Software Foundation;

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
```
