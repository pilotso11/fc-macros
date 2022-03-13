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

Note: See _keymaps.py_ to edit the keyboard mappings.  (Only in source code version.)

The latest version no longer uses image matching, instead of uses known location on the screen
and text recognition.  It may now work with custom HUD colors.  It is also hopefully insensitive
to HUD Brightness options.    It is also tested on both windowed and full screen modes, but only at 1008p full screen.

The tool is written attempting for safety in the UI.  
If the macro cannot find the expected images or text it will abort for safety. 
But I cannot guarantee it won't misbehave in some odd way.  It is just sending keys and mouse
actions so if E:D loses focus while running it will start sending them to whatever application does have the focus.

If you use the refuel option, make sure your ship has enough room for a full jumps worth of Tritium, 
as much as 150 Tons if your carrier is fully loaded.   This option will load the carrier and the ship before 
setting up a jump to minimize the carrier mass.


---------------

# Installation

Option 1:
* Download a release zip file
* Extract
* Run fcmacros.exe

Option 2:
* Download the source
* pip install keyboard pyautogui pillow opencv-python usersettings pywin32 pytesseract
  * Or run "setup.cmd"
* python main.py


--------------
# 3rd Party Dependencies

These are all included in the installation or are part of the pip install in setup.cmd.

The latest edition uses teseract for the text recognition.  
A portable copy is provided in a zip file and is auto extracted at first runtime.   
More about the teseract project can be found [here](https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc).
The provided copy is the [University of Manheim 64bit build.](https://github.com/UB-Mannheim/tesseract/wiki)  

There is heavy use of [OpenCV](https://opencv.org/).  

The latest version uses much less of [pyautogui](https://pyautogui.readthedocs.io/en/latest/)
But much homage is owed to this tool.

The UI theme is [awthemes awdark](https://sourceforge.net/projects/tcl-awthemes/) by Brad Lanam. (Thank you.)

--------------

# Troubleshooting

Summary of actions are written to "fcmacros.log" in the working directory.
If you are experiencing issues, enable debug logging.  The log file will contain
details of every step the macro is taking - what keypresses it is making, 
the images or text it is searching for on the screen etc.   Hopefully there will be enough
information to troubleshoot.   For now it saves many debug_*.png images in the debugimages/ folder. 
These are to also help troubleshoot problems.   You might see something like debug_TRITIUM_threshold.png. 
If it doesn't contain the word "TRITIUM", that's a hint that it's not finding the text properly.

Likely causes:
* The image matching is screen resolution specific.  If you're not running E:D at 1080p the image locations are probably wrong.
It should be possible to make them scale, but some experimentation is needed with different resolutions,
especially those that are at different aspect ratios.
* Custom HUD colours may be a problem, though hopefully not in the latest version.  If for some reason
your colour palette is very bright or very dim, it might make it difficult to find what button is selected as the
image is forced to a very high contrast.
* As with the above, you might try using the default UI brightness.
* Non-standard keybindings can also be a problem.  
* Try running in windowed mode if you are in full-screen mode.  Alt-Enter to switch modes.  This also should be 
working properly on the latest version in both modes, but its worth a try.
* Look at some of the suggestions in the thread on issue report number 2: https://github.com/pilotso11/fc-macros/issues/2
though these are less relevent with the latest releases.

If you have the source code version you can edit the keybindings in "keymaps.py".

# Work in progress

The latest version has abandoned the pyautogui "find this image" technique and instead
uses known offsets and text recognition.  This should be less trouble free.

More work is needed to support non-1080p resolutions.

-----------------

Copyright (c) 2022 Seth Osher. All Rights Reseved.
Released under the MIT license.

------------------
Tags: Elite Dangerous Fleet Carrier autopilot auto jumper macros
