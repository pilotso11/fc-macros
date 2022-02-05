# fc-macros
Elite Dangerous Fleet Carrier Macros

Currently, this plugin uses default keybindings.   It is unlikely to work with a joystick or HOTAS enabled.

It also may not work with custom HUD colors because it uses image
matching to verify its screen navigation.

Because the HUD sizes are different on some ships, this may cause issues.
It's been tested on:
* Imperial Cutter
* Anaconda
* Python
* Type 9
* Beluga

If you use the refuel option, make sure your ship has enough room for a full jumps worth of Tritium, 
as much as 150 Tons if your carrier is fully loaded.   This option will load the carrier and the ship before 
setting up a jump to minimize the carrier mass.

Requires the following python addins:

* pip install keyboard pyautogui pillow opencv-python usersettings 
