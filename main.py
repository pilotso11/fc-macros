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

debug = True

current_system = ''
jumping = False
cool_down = False
auto_jump = False
route = []
next_waypoint = ''
route_file = ""
is_odyssey = False

carrier_services_set = ['images/carrier_services.png',  # cutter
                        'images/carrier_services2.png',  # dolphin
                        'images/carrier_services3.png',  # type 9
                        'images/carrier_services4.png',  # mamba
                        'images/carrier_services5.png',  # conda
                        'images/carrier_services6.png',  # beluga
                        'images/carrier_services7.png',  # python
                        ]


# Find most recent E:D log file
def get_lastest_log_file():
    list_of_files = glob.glob(
        f"C:\\Users\\{getpass.getuser()}\\Saved Games\\Frontier Developments\\Elite Dangerous\\Journal.*")
    return max(list_of_files, key=os.path.getmtime)


# Load and parse the route.csv
def load_route(route_file_name):
    global route
    route = [] # Clear prior route

    with open(route_file_name, 'r') as f:
        cnt = 0
        while True:
            line = f.readline()
            parts = line.strip().split(",")
            if len(line) == 0:
                update_route_position()
                set_status("Loaded route with {} systems".format(len(route)))
                return  # Done with file
            if cnt == 0:
                if parts[0].strip('"') != 'System Name':
                    set_status("Invalid route file, first column must be System Name")
                    return
            else:
                system = parts[0].strip('"')
                route.append(system)
            cnt += 1


# Press down key for down_time and wait after for delay
def press(key, delay=0.1, down_time=0.2):
    out = key
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
    if debug: print(out)
    kb.press(key)
    sleep(down_time)
    kb.release(key)
    sleep(delay)


# look for the image on screen , if found, return True
# if not, press the key specified, true this up to max_trues times,
# if max_tries is exceeded return False
# confidence is the confidence interval on the match
def press_and_find(key='a', image='images/tritium.png', max_tries=10, confidence=0.75):
    cnt = 0
    while pyautogui.locateOnScreen(image, confidence=confidence) is None:
        press(key)
        cnt += 1
        if cnt > max_tries:
            set_status('Macro failed')
            return False
    return True


def press_and_find_set(key='a', images=[], max_tries=10, confidence=0.75):
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


# Callback to schedule a jump
def schedule_jump():
    find_system_and_jump()


# Macro to schedule a jump
def find_system_and_jump():
    global jumping
    if len(next_waypoint) < 3 or not auto_jump: return False

    if do_refuel.get() == 1:
        refuel()

    set_status('Finding next waypoint')

    # Back to main menu
    if not press_and_find_set('\b', carrier_services_set): return False
    press('space')
    if not press_and_find('s', 'images/tritium_depot.png'): return False
    if not press_and_find('d', 'images/carrier_management.png'): return False
    press('space')
    sleep(2)
    if not press_and_find('s', 'images/navigation.png'): return False
    press('space')
    sleep(0.5)
    if not press_and_find('s', 'images/open_galmap.png'): return False
    press('space')
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

    if not press_and_find_set('\b', carrier_services_set): return False
    press('space')
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
    if not press_and_find_set('\b', carrier_services_set): return False
    press('4', 0.5)
    if not press_and_find('e', 'images/inventory.png'): return False
    press('d')
    press('w')
    if not press_and_find('d', 'images/transfer.png'): return False
    press('space')
    if not press_and_find('w', 'images/tritium.png'): return False

    # hold down the 'a' key until max capacity is reached
    kb.press('a')
    while pyautogui.locateOnScreen('images/max_capacity.png', confidence=0.75) is None:
        sleep(0.5)
    kb.release('a')

    if not press_and_find('s', 'images/cancel.png'): return False
    press('d')
    press('space')
    set_status('tritium loaded')
    if not press_and_find_set('\b', carrier_services_set): return False

    return True


# Donate tritium
def donate_tritium():
    set_status('Donating tritium')
    if not press_and_find_set('\b', carrier_services_set): return False
    press('space')
    if not press_and_find('s', 'images/tritium_depot.png'): return False
    press('space')
    sleep(0.5)
    if not press_and_find('w', 'images/donate_tritium.png'): return False
    press('space')
    if not press_and_find('w', 'images/confirm_deposit.png'): return False
    press('space')
    set_status('tritium donated')
    if not press_and_find('s', 'images/exit_door.png'): return False
    press('space')
    if not press_and_find_set('\b', carrier_services_set): return False

    return True


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
    global next_waypoint, jumping
    if len(route) == 0: return

    next_waypoint = ""  # Next waypoint requires positive validation

    route_len_label.config(text="{} via {} waypoints".format(route[-1], len(route)))
    n = 0
    if current_system == route[-1]:
        route_pos_label.config(text="Destination reached")
        jumping = False
        return

    for r in route:
        if r == current_system:
            next_waypoint = route[n + 1]
            route_pos_label.config(text="At waypoint {}, next is {}".format(n, next_waypoint))
            return
        n += 1
    route_pos_label.config(text="First waypoint is {}".format(route[0]))


# Setup UI
root = Tk()
root.title("Fleet Carrier Tools")
root.iconbitmap('images/fc_icon.ico')

do_refuel = tkinter.IntVar()

frame = ttk.Frame(root, padding=10)
frame.grid()
row = 0
ttk.Label(frame, text="Fleet Carrier Tools").grid(column=0, row=row)
row += 1

ttk.Label(frame, text="Refuel Carrier:").grid(column=0, row=row, sticky="e")
ttk.Label(frame, text="Ctrl+F11").grid(column=1, row=row, sticky="w")
row += 1

ttk.Label(frame, text="Enable autojump:").grid(column=0, row=row, sticky="e")
ttk.Label(frame, text="Ctrl+F12").grid(column=1, row=row, sticky="w")
row += 1

ttk.Label(frame, text="Cancel autojump:").grid(column=0, row=row, sticky="e")
ttk.Label(frame, text="Ctrl+F10").grid(column=1, row=row, sticky="w")
row += 1

ttk.Separator(frame, orient="horizontal").grid(column=0, row=row, columnspan=2, sticky="ew")
row += 1

ttk.Label(frame, text="Current System:").grid(column=0, row=row, sticky="e")
system_label = ttk.Label(frame, text="Unknown")
system_label.grid(column=1, row=row, sticky="w")
row += 1

ttk.Button(frame, text="Select Route", command=select_route_file).grid(column=0, row=row, sticky="e")
route_label = ttk.Label(frame, text="Unknown")
route_label.grid(column=1, row=row, sticky="w")
row += 1

ttk.Label(frame, text="Refuel on jump?").grid(column=0, row=row, sticky="e")
ttk.Checkbutton(frame, variable=do_refuel).grid(column=1, row=row, sticky="w")
row += 1

ttk.Label(frame, text="Destination:").grid(column=0, row=row, sticky="e")
route_len_label = ttk.Label(frame, text="Unknown")
route_len_label.grid(column=1, row=row, sticky="w")
row += 1

ttk.Label(frame, text="Progress:").grid(column=0, row=row, sticky="e")
route_pos_label = ttk.Label(frame, text="Unknown")
route_pos_label.grid(column=1, row=row, sticky="w")
row += 1

ttk.Separator(frame, orient="horizontal").grid(column=0, row=row, columnspan=2, sticky="ew")
row += 1

status = ttk.Label(frame, text="")
status.grid(column=0, row=row, columnspan=2, sticky="w")
row += 1

ttk.Label(frame, text="                                                                                               ").grid(column=0, row=row, columnspan=2, sticky="w")


row += 1
ttk.Button(frame, text="Quit", command=root.destroy).grid(column=0, row=row)


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
    newest = get_lastest_log_file()
    if log != newest:
        ed_log.close()
        print("Opening newer E:D log: ", log)
        ed_log = open(log, 'r')
    root.after(10000, check_newer_log)

def process_log():
    global current_system, jumping, cool_down, is_odyssey
    lines = ed_log.readlines()
    # print("Got ", len(lines), "lines from E:D log")
    curr_sys = ''
    for line in lines:
        line = line.strip()
        print(line)
        if line.count('StarSystem') > 0:
            curr_sys = line
        if line.count('Odyssey') > 0:
            ody = get_value_from_log_line(line, 'Odyssey')
            if ody == "true":
                is_odyssey = True
                print("We're in Odyssey")
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
            set_status("Current system: " + current_system)
            system_label.config(text=current_system)
            update_route_position()
            root.update_idletasks()

    root.after(1000, process_log)


# Set a status message
def set_status(msg=''):
    status.config(text=msg)
    if debug:
        print(msg)
    root.update_idletasks()


# Check for our macro keys being pressed
def check_keys():
    global auto_jump
    if kb.is_pressed('ctrl+f11'):
        set_status("Refuel requested")
        root.after(100, refuel())
        root.after(1000, check_keys)
        return
    if kb.is_pressed('ctrl+f12'):
        set_status("Enable auto jump")
        auto_jump = True
        root.after(100, schedule_jump)
        root.after(1000, check_keys)
        return
    if kb.is_pressed('ctrl+f10'):
        set_status("Auto jump disabled")
        auto_jump = False
    root.after(20, check_keys)

settings = usersettings.Settings('com.ed.fcmacros')
settings.add_setting("route_file", str, default="")
settings.add_setting("refuel", int, default=1)

settings.load_settings()
do_refuel.set(settings.refuel)


def check_settings():
    global route_file
    if route_file == '' and settings.route_file > '':
        route_file = settings.route_file
        route_label.config(text=route_file)
        load_route(route_file)
    elif route_file != settings.route_file:
        settings.route_file = route_file

    settings.refuel = do_refuel.get()
    settings.save_settings()

    root.after(1000, check_settings)


log = get_lastest_log_file()
print("Opening E:D log: ", log)
ed_log = open(log, 'r')
check_newer_log()  # Start checking for log rotation

process_log()  # start log processing
check_settings() # start monitoring settings
check_keys()  # start key monitoring
root.mainloop()  # run
