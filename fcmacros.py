# fcmacros.py
# Elite Dangerous Fleet Carrier Macros - autopilot/auto jumper
# Copyright (c) 2022 Seth Osher
#
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import keyboard as kb
import pyautogui
from time import sleep
import glob
import getpass
import os
import usersettings
from keymaps import *
import logging
import logging.handlers
import sys


VERSION = "0.1.2"
BUNDLED = False
LOGFILE = "fcmacros.log"
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    LOGFILE, maxBytes=(1048576*5), backupCount=10
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BUNDLED = True
else:
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

logging.info(f"Starting fcmacros.py version: {VERSION}")
if BUNDLED: logging.info('Running in a PyInstaller bundle')
else: logging.info('Running as a console application')

current_system = ''
jumping = False
cool_down = False
auto_jump = False
jump_one = False
route = []
next_waypoint = ''
route_file = ""
is_odyssey = False

# Use all available carrier_services images
carrier_services_set = glob.glob("images/carrier_services*.png")
logging.info(f"Loaded {len(carrier_services_set)} carrier services images")


# Find most recent E:D log file
def get_latest_log_file():
    list_of_files = glob.glob(
        f"C:\\Users\\{getpass.getuser()}\\Saved Games\\Frontier Developments\\Elite Dangerous\\Journal.*")
    return max(list_of_files, key=os.path.getmtime)


# Load and parse the route.csv
def load_route(route_file_name):
    global route, route_file
    route = []  # Clear prior route
    if len(route_file_name) < 4: return

    with open(route_file_name, 'r') as f:
        cnt = 0
        while True:
            try:
                line = f.readline()
                parts = line.strip().split(",")
                if len(line) == 0:
                    update_route_position()
                    set_status("Loaded route with {} systems".format(len(route)))
                    return  # Done with file
                if cnt == 0:
                    if parts[0].strip('"') != 'System Name':
                        set_status("Invalid route file, first column must be System Name")
                        route_file = ""
                        return
                else:
                    system = parts[0].strip('"')
                    route.append(system)
                cnt += 1
            except (RuntimeError, UnicodeDecodeError) as err:
                logging.warning(f"Exception loading route file {route_file_name}: {err}")
                set_status("Invalid route file, first column must be System Name")
                route_file = ""


# Press down key for down_time and wait after for delay
def press(key, delay=0.1, down_time=0.2):
    if key == '\b':
        out = "Press: backspace"
    elif key == '\t':
        out = "Press: tab"
    elif key == '\r':
        out = "Press: return"
    elif key == '\n':
        out = "Press: newline"
    elif key == ' ':
        out = "Press: space"
    else:
        out = "Press: " + key
    logging.debug(out)
    kb.press(key)
    sleep(down_time)
    kb.release(key)
    sleep(delay)


# look for the image on screen , if found, return True
# if not, press the key specified, true this up to max_trues times,
# if max_tries is exceeded return False
# confidence is the confidence interval on the match
def press_and_find(key=ED_UI_LEFT, image='images/tritium.png', max_tries=10, confidence=0.75, do_log=True):
    cnt = 0
    if do_log: logging.debug(f"Looking for: {image}")
    while pyautogui.locateOnScreen(image, confidence=confidence) is None:
        if do_log: logging.debug(f"{image} not found")
        press(key)
        cnt += 1
        if cnt > max_tries:
            logging.warning(f"Unable to find {image} after {max_tries}")
            set_status('Macro failed')
            return False
    if do_log: logging.debug(f"{image} found")
    return True


def press_and_find_set(key=ED_UI_LEFT, images=[], max_tries=10, confidence=0.75):
    cnt = 0
    while True:
        for i in images:
            if pyautogui.locateOnScreen(i, confidence=confidence) is not None:
                return True
        press(key)
        cnt += 1
        if cnt > max_tries:
            set_status('Macro failed')
            return False


def mouse_click_at(x, y, pause=0.25, click_duration=0.25):
    pyautogui.moveTo(x, y)
    sleep(pause)
    pyautogui.mouseDown()
    sleep(click_duration)
    pyautogui.mouseUp()


# Move back to the carrier main screen after a jump
def set_to_carrier():
    sleep(5)
    press(ED_RIGHT_WINDOW)
    sleep(1)
    if not press_and_find_set(ED_BACK, carrier_services_set): return False
    press(ED_UI_SELECT)


# Callback to schedule a jump
def schedule_jump():
    find_system_and_jump()


# Macro to schedule a jump
def find_system_and_jump():
    global jumping, jump_one
    if len(next_waypoint) < 3 or not (auto_jump or jump_one): return False

    if do_refuel.get() == 1:
        if not load_tritium(): return False
        if not donate_tritium(): return False
        if not load_tritium(): return False

    if jump_one: jump_one = False

    set_status('Finding next waypoint')

    # Back to main menu
    if not press_and_find_set(ED_BACK, carrier_services_set): return False
    press(ED_UI_SELECT)
    if not press_and_find(ED_UI_DOWN, 'images/tritium_depot.png'): return False
    if not press_and_find(ED_UI_RIGHT, 'images/carrier_management.png'): return False
    press(ED_UI_SELECT)
    sleep(2)
    if not press_and_find(ED_UI_DOWN, 'images/navigation.png'): return False
    press(ED_UI_SELECT)
    sleep(0.5)
    if not press_and_find(ED_UI_DOWN, 'images/open_galmap.png'): return False
    press(ED_UI_SELECT)
    sleep(3)

    pos = pyautogui.locateOnScreen('images/search_the_galaxy.png', confidence=0.75)
    if pos is None:
        set_status("Unable to find search")
        return False
    x, y = pos.left + pos.width // 2, pos.top + pos.height // 2
    mouse_click_at(x, y)
    kb.write(next_waypoint)
    sleep(1)
    mouse_click_at(x, y + pos.height)
    sleep(2)
    pos = pyautogui.locateOnScreen('images/set_carrier_destination.png', confidence=0.75)
    if pos is None:
        set_status("Unable to find set carrier destination")
        return False
    x, y = pos.left + pos.width // 2, pos.top + pos.height // 2
    mouse_click_at(x, y)
    set_status("Jump set for {}".format(next_waypoint))
    jumping = True

    if not press_and_find_set(ED_BACK, carrier_services_set): return False
    press(ED_UI_SELECT)
    return True


# Callback to refuel the ship, the carrier and then the ship
# to optimise carrier mass and save up to 1 ton of fuel per jump
def refuel():
    set_status('Refueling')
    sleep(1)
    if not load_tritium(): return
    if not donate_tritium(): return
    if not load_tritium(): return  # keep fully loaded to reduce tritium consumption


# Refill ship with tritium
def load_tritium():
    set_status('Filling ship with tritium')
    if not press_and_find_set(ED_BACK, carrier_services_set): return False
    press(ED_RIGHT_WINDOW, 0.5)
    if not press_and_find('e', 'images/inventory.png'): return False
    press(ED_UI_RIGHT)
    press(ED_UI_UP)
    if not press_and_find(ED_UI_RIGHT, 'images/transfer.png'): return False
    press(ED_UI_SELECT)
    if not press_and_find(ED_UI_UP, 'images/tritium.png'): return False

    # hold down the ED_UI_LEFT key until max capacity is reached
    kb.press(ED_UI_LEFT)
    logging.debug(f"Press and hold {ED_UI_LEFT}")
    while pyautogui.locateOnScreen('images/max_capacity.png', confidence=0.75) is None:
        sleep(0.5)
    logging.debug(f"images/max_capacity.png found")
    logging.debug(f"Release {ED_UI_LEFT}")
    kb.release(ED_UI_LEFT)

    if not press_and_find(ED_UI_DOWN, 'images/cancel.png'): return False
    press(ED_UI_RIGHT)
    press(ED_UI_SELECT)
    set_status('tritium loaded')
    if not press_and_find_set(ED_BACK, carrier_services_set): return False

    return True


# Donate tritium
def donate_tritium():
    set_status('Donating tritium')
    if not press_and_find_set(ED_BACK, carrier_services_set): return False
    press(ED_UI_SELECT)
    if not press_and_find(ED_UI_DOWN, 'images/tritium_depot.png'): return False
    press(ED_UI_SELECT)
    sleep(0.5)
    if not press_and_find(ED_UI_UP, 'images/donate_tritium.png'): return False
    press(ED_UI_SELECT)
    if not press_and_find(ED_UI_UP, 'images/confirm_deposit.png'): return False
    press(ED_UI_SELECT)
    set_status('tritium donated')
    if not press_and_find(ED_UI_DOWN, 'images/exit_door.png'): return False
    press(ED_UI_SELECT)
    if not press_and_find_set(ED_BACK, carrier_services_set): return False

    return True


def empty_cargo():
    set_status('Emptying your cargo hold')
    if not press_and_find_set(ED_BACK, carrier_services_set): return False
    press(ED_RIGHT_WINDOW, 0.5)
    if not press_and_find('e', 'images/inventory.png'): return False
    press(ED_UI_RIGHT)
    press(ED_UI_UP)
    if not press_and_find(ED_UI_RIGHT, 'images/transfer.png'): return False
    press(ED_UI_SELECT)
    if not press_and_find(ED_UI_UP, 'images/all_to_carrier.png'): return False
    press(ED_UI_SELECT)
    sleep(1)
    press(ED_UI_SELECT)
    set_status('Cargo hold emptied')
    if not press_and_find_set(ED_BACK, carrier_services_set): return False


# Select route file dialog
def select_route_file():
    global route_file
    route_file = fd.askopenfilename()
    route_label.config(text=route_file)
    load_route(route_file)
    settings.route_file = route_file
    settings.save_settings()


# Update UI with route details and find next waypoint
def update_route_position():
    global next_waypoint, jumping, auto_jump
    if len(route) == 0: return

    next_waypoint = ""  # Next waypoint requires positive validation

    route_len_label.config(text="{} via {} waypoints".format(route[-1], len(route)))
    n = 0
    if current_system == route[-1]:
        route_pos_label.config(text="Destination reached")
        progress.set(100)
        jumping = False
        auto_jump = False
        auto_jump_label.config(text="Route Complete")

        return

    for r in route:
        if r == current_system:
            next_waypoint = route[n + 1]
            route_pos_label.config(text="At waypoint {}, next is {}".format(n, next_waypoint))
            progress.set(100 * n // len(route))
            return
        n += 1
    route_pos_label.config(text="First waypoint is {}".format(route[0]))


def dark_style2(tk_root):
    _style = ttk.Style(root)
    tk_root.tk.call('source', 'awthemes-10.4.0/awdark.tcl')
    _style.theme_use('awdark')
    return _style


# Setup UI
root = Tk()
root.title("Fleet Carrier Macros")
root.iconbitmap('images/fc_icon.ico')
style = dark_style2(root)

do_refuel = tkinter.IntVar()
DEBUG = tkinter.IntVar()
progress = tkinter.IntVar()

frame = ttk.Frame(root, padding=10)
frame.grid()
row = 0

ttk.Label(frame, text="Refuel Carrier:").grid(column=0, row=row, sticky="e")
ttk.Label(frame, text="Ctrl+F11").grid(column=1, row=row, sticky="w")

ttk.Label(frame, text="Empty cargo hold:").grid(column=2, row=row, sticky="e")
ttk.Label(frame, text="Ctrl+F5").grid(column=3, row=row, sticky="w")
row += 1

ttk.Label(frame, text="Enable autojump:").grid(column=0, row=row, sticky="e")
ttk.Label(frame, text="Alt+F9").grid(column=1, row=row, sticky="w")

ttk.Label(frame, text="Cancel autojump:").grid(column=2, row=row, sticky="e")
ttk.Label(frame, text="Ctrl+F10").grid(column=3, row=row, sticky="w")
row += 1

ttk.Label(frame, text="Engage next jump on route:").grid(column=0, row=row, sticky="e")
ttk.Label(frame, text="Ctrl+F9").grid(column=1, row=row, sticky="w")
row += 1


ttk.Separator(frame, orient="horizontal").grid(column=0, row=row, columnspan=5, sticky="ew")
row += 1

ttk.Label(frame, text="Current System:").grid(column=0, row=row, sticky="e")
system_label = ttk.Label(frame, text="Unknown")
system_label.grid(column=1, row=row, sticky="w")
row += 1

ttk.Button(frame, text="Select Route", command=select_route_file).grid(column=0, row=row, sticky="e")
route_label = ttk.Label(frame, text="Unknown")
route_label.grid(column=1, row=row, sticky="w", columnspan=5)
row += 1

ttk.Label(frame, text="Refuel on jump?").grid(column=0, row=row, sticky="e")
ttk.Checkbutton(frame, variable=do_refuel).grid(column=1, row=row, sticky="w")
row += 1

ttk.Label(frame, text="Destination:").grid(column=0, row=row, sticky="e")
route_len_label = ttk.Label(frame, text="Unknown")
route_len_label.grid(column=1, row=row, sticky="w", columnspan=3)
row += 1

ttk.Label(frame, text="Progress:").grid(column=0, row=row, sticky="e")
route_pos_label = ttk.Label(frame, text="Unknown")
route_pos_label.grid(column=1, row=row, sticky="w", columnspan=3)
row += 1
ttk.Progressbar(frame, variable=progress, length=200).grid(column=1, row=row, columnspan=2, sticky="ew")
row += 1

ttk.Separator(frame, orient="horizontal").grid(column=0, row=row, columnspan=5, sticky="ew")
row += 1

status = ttk.Label(frame, text="")
status.grid(column=0, row=row, columnspan=5, sticky="w")
row += 1

if not BUNDLED:
    ttk.Label(frame, text="Debug Log?").grid(column=0, row=row, sticky="e")
    ttk.Checkbutton(frame, variable=DEBUG).grid(column=1, row=row, sticky="w")
else:
    ttk.Label(frame, text="Version " + VERSION).grid(column=0, row=row, sticky="e")

auto_jump_label = ttk.Label(frame, text="")
auto_jump_label.grid(column=2, row=row, sticky="ew", columnspan=2)

ttk.Button(frame, text="Quit", command=root.destroy).grid(column=4, row=row)


def cool_down_complete():
    global cool_down
    cool_down = False
    set_status("Carrier cool down complete")
    if auto_jump:
        schedule_jump()


def get_value_from_log_line(line, key):
    parts = line.strip('{} ').split(',')
    for p in parts:
        keys = p.split(':')
        k = keys[0].strip('" ')
        if k == key:
            return keys[1].strip('" ')
    return ''


def check_newer_log():
    global ed_log, log
    newest = get_latest_log_file()
    if log != newest:
        ed_log.close()
        log = newest
        logging.info(f"Opening newer E:D log: {log}")
        ed_log = open(log, 'r')
    root.after(10000, check_newer_log)


def process_log():
    global current_system, jumping, cool_down, is_odyssey
    try:
        lines = ed_log.readlines()
        if len(lines) > 0:
            logging.debug(f"Got {len(lines)} lines from E:D log")
        curr_sys = ''
        for line in lines:
            line = line.strip()
            #logging.debug(line)
            if line.count('StarSystem') > 0:
                curr_sys = line
            if line.count('Odyssey') > 0:
                ody = get_value_from_log_line(line, 'Odyssey')
                if ody == "true":
                    is_odyssey = True
                    logging.info("We're in Odyssey")
            if line.count('CarrierJumpRequest') > 0:
                dest = get_value_from_log_line(line, 'SystemName')
                if dest == next_waypoint:
                    set_status("Jump to {} confirmed".format(dest))

        if curr_sys > '':
            new_system = curr_sys.split('"StarSystem":"')[1].split('"')[0]
            if current_system != new_system:
                current_system = new_system
                if jumping:
                    jumping = False
                    cool_down = True
                    root.after(1000 * 210, cool_down_complete)
                    set_to_carrier()

                set_status("Current system: " + current_system)
                system_label.config(text=current_system)
                update_route_position()
                root.update_idletasks()

    except (UnicodeDecodeError, ) as err:
        logging.warning(f"Exception processing log file: {err}")

    root.after(1000, process_log)


# Set a status message
def set_status(msg=''):
    status.config(text=msg)
    logging.info(msg)
    root.update_idletasks()


# Check for our macro keys being pressed
def check_keys():
    global auto_jump, jump_one
    if kb.is_pressed('ctrl+f11'):
        set_status("Refuel requested")
        root.after(100, refuel)
        root.after(1000, check_keys)
        return
    if kb.is_pressed('ctrl+f5'):
        set_status("Cargo unload requested")
        root.after(100, empty_cargo)
        root.after(1000, check_keys)
        return
    if kb.is_pressed('alt+f9'):
        set_status("Enable auto jump")
        auto_jump = True
        auto_jump_label.config(text="Auto Jump Enabled")
        root.after(100, schedule_jump)
        root.after(1000, check_keys)
        return
    if kb.is_pressed('ctrl+f9'):
        set_status("Scheduling next jump")
        jump_one = True
        root.after(100, schedule_jump)
        root.after(1000, check_keys)
        return
    if kb.is_pressed('ctrl+f10'):
        set_status("Auto jump disabled")
        auto_jump = False
        auto_jump_label.config(text="")

    root.after(20, check_keys)


# initialize settings
settings = usersettings.Settings('com.ed.fcmacros')
settings.add_setting("route_file", str, default="")
settings.add_setting("refuel", int, default=1)
settings.add_setting("debug", int, default=0)


def set_debug_level():
    if settings.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


settings.load_settings()
do_refuel.set(settings.refuel)
DEBUG.set(settings.debug)
set_debug_level()


def check_settings():
    global route_file
    if route_file == '' and settings.route_file > '':
        route_file = settings.route_file
        route_label.config(text=route_file)
        load_route(route_file)
    elif route_file != settings.route_file:
        settings.route_file = route_file

    settings.refuel = do_refuel.get()
    settings.debug = DEBUG.get()
    set_debug_level()
    settings.save_settings()

    root.after(1000, check_settings)


log = get_latest_log_file()
logging.info(f"Opening E:D log: {log}")
ed_log = open(log, 'r')


# Run the UI
def run_ui():
    check_newer_log()  # Start checking for log rotation
    process_log()  # start log processing
    check_settings()  # start monitoring settings
    check_keys()  # start key monitoring
    root.mainloop()  # run


if __name__ == '__main__':
    run_ui()

