# fc-macros
Elite Dangerous Fleet Carrier Macros
There are 3 primary macros:
* Ctrl+F11: Refill your ship with Tritium and donate it to the carrier.
* Ctrl+F9: Schedule the next jump on the route
* Alt+F9: Auto jump the remaining route
  * Ctrl+F10: Stop auto jumping
* Ctrl+F5: Empty your ship's cargo to the carrier.

Route files are in CSV format from the spansh router.  Only the first column matres and it must be titled 
"System Name".  https://www.spansh.co.uk/fleet-carrier

![screenshot](images/screenshot.png)

------

Currently, this plugin uses default keybindings and mouse for input.  The mouse is used to navigate the galmap.
Because it uses the keyboard and mouse, it is unlikely to work with a joystick or HOTAS enabled.

Note: See _keymaps.py_ to edit the keboard mappings.  (Only in source coude version.)

It is also unlikely work with custom HUD colors as it uses image
matching to verify its screen navigation.  If the macro cannot find the expected 
ative
user input it will abort for safety.

Because the HUD sizes are different on some ships, this may cause issues.  
In particular the size of the "Carrier Services" UI button varies.
Several different images are used to try and combat this. 
It has been tested on the most likely to be used ships:
* Imperial Cutter
* Anaconda
* Python
* Type 9
* Beluga

If you use the refuel option, make sure your ship has enough room for a full jumps worth of Tritium, 
as much as 150 Tons if your carrier is fully loaded.   This option will load the carrier and the ship before 
setting up a jump to minimize the carrier mass.

---------------

How to install.

Option 1:
* Download a release zip file
* Extract
* Run fcmacros.exe

Option 2:
* Download the source
* pip install keyboard pyautogui pillow opencv-python usersettings 
* python fcmacros.py

-----------------

Copyright (c) 2022 Seth Osher. All Rights Reseved.
Released under the MIT license.

------------------
Tags: Elite Dangerous Fleet Carrier autopilot auto jumper macros
