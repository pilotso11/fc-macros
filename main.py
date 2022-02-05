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

current_system = ''
jumping = False
cool_down = False
auto_jump = False
route = []
next_waypoint = ''


# Find most recent E:D log file
def get_lastest_log_file():
    list_of_files = glob.glob(
        f"C:\\Users\\{getpass.getuser()}\\Saved Games\\Frontier Developments\\Elite Dangerous\\Journal.*")
    return max(list_of_files, key=os.path.getmtime)


# Load and parse the route.csv
def load_route(route_file):
    global route

    with open(route_file, 'r') as f:
        row = 0
        while True:
            line = f.readline()
            parts = line.strip().split(",")
            if len(line) == 0:
                update_route_position()
                set_status("Loaded route with {} systems".format(len(route)))
                return # Done with file
            if row == 0:
                if parts[0].strip('"') != 'System Name':
                    set_status("Invalid route file, first column must be System Name")
                    return
            else:
                system = parts[0].strip('"')
                route.append(system)
            row += 1


# Press down key for down_time and wait after for delay
def press(key, delay=0.1, down_time=0.2):
    print("Press: ", key)
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


def refuel():
    sleep(1)
    load_tritium()
    donate_tritium()
    load_tritium()  # keep fully loaded to reduce tritium consumption


def load_tritium():
    if not press_and_find('\b', 'images/carrier_services.png'): return
    press('4', 0.5)
    if not press_and_find('e', 'images/inventory.png'): return
    press('d')
    press('w')
    if not press_and_find('d', 'images/transfer.png'): return
    press('space')
    if not press_and_find('w', 'images/tritium.png'): return

    # hold down the 'a' key until max capacity is reached
    kb.press('a')
    while pyautogui.locateOnScreen('images/max_capacity.png', confidence=0.75) is None:
        sleep(0.5)
    kb.release('a')

    if not press_and_find('s', 'images/cancel.png'): return
    press('d')
    press('space')
    set_status('tritium loaded')
    if not press_and_find('\b', 'images/carrier_services.png'): return


def donate_tritium():
    if not press_and_find('\b', 'images/carrier_services.png'): return
    press('space')
    if not press_and_find('s', 'images/tritium_depot.png'): return
    press('space')
    sleep(0.5)
    if not press_and_find('w', 'images/donate_tritium.png'): return
    press('space')
    if not press_and_find('w', 'images/confirm_deposit.png'): return
    press('space')
    set_status('tritium donated')
    if not press_and_find('s', 'images/exit_door.png'): return
    press('space')
    if not press_and_find('\b', 'images/carrier_services.png'): return


route_file = ""


def select_route_file():
    global route_file
    route_file = fd.askopenfilename()
    route_label.config(text=route_file)
    load_route(route_file)


def update_route_position():
    global next_waypoint
    route_len_label.config(text="{} via {} waypoints".format(route[-1], len(route)))
    n = 0
    if current_system == route[-1]:
        route_pos_label.config(text="Destination reached")
        return
    for r in route:
        if r == current_system:
            next_waypoint = route[n+1]
            route_pos_label.config(text="At waypoint {}, next is {}".format(n, next_waypoint))
            return
        n += 1
    route_pos_label.config(text="First waypoint is {}".format(route[0]))

root = Tk()

do_refuel = tkinter.IntVar()

frame = ttk.Frame(root, padding=10)
frame.grid()
r = 0
ttk.Label(frame, text="Fleet Carrier Tools").grid(column=0, row=r)
r += 1

ttk.Label(frame, text="Refuel Carrier:").grid(column=0, row=r, sticky="e")
ttk.Label(frame, text="Ctrl+F11").grid(column=1, row=r, sticky="w")
r += 1

ttk.Label(frame, text="Enable autojump:").grid(column=0, row=r, sticky="e")
ttk.Label(frame, text="Ctrl+F12").grid(column=1, row=r, sticky="w")
r += 1

ttk.Label(frame, text="Cancel autojump:").grid(column=0, row=r, sticky="e")
ttk.Label(frame, text="Ctrl+F10").grid(column=1, row=r, sticky="w")
r += 1

ttk.Separator(frame, orient="horizontal").grid(column=0, row=r, columnspan=2, sticky="ew")
r += 1

ttk.Label(frame, text="Current System:").grid(column=0, row=r,sticky="e")
system_label = ttk.Label(frame, text="Unknown")
system_label.grid(column=1, row=r, sticky="w")
r += 1

ttk.Button(frame, text="Select Route", command=select_route_file).grid(column=0, row=r, sticky="e")
route_label = ttk.Label(frame, text="Unknown")
route_label.grid(column=1, row=r, sticky="w")
r += 1

ttk.Label(frame, text="Refuel on jump?").grid(column=0, row=r,sticky="e")
ttk.Checkbutton(frame, variable=do_refuel).grid(column=1, row=r, sticky="w")
r += 1

ttk.Label(frame, text="Destination:").grid(column=0, row=r,sticky="e")
route_len_label = ttk.Label(frame, text="Unknown")
route_len_label.grid(column=1, row=r, sticky="w")
r += 1

ttk.Label(frame, text="Progress:").grid(column=0, row=r,sticky="e")
route_pos_label = ttk.Label(frame, text="Unknown")
route_pos_label.grid(column=1, row=r, sticky="w")
r += 1

ttk.Separator(frame, orient="horizontal").grid(column=0, row=r, columnspan=2, sticky="ew")
r += 1

status = ttk.Label(frame, text="")
status.grid(column=0, row=r, columnspan=2, sticky="w")

r += 1
ttk.Button(frame, text="Quit", command=root.destroy).grid(column=0, row=r)


def cool_down_complete():
    global cool_down
    cool_down = False
    print("Carrier cool down compete")
    set_status("Carrier cool down complete")


def process_log():
    global current_system, jumping, cool_down
    lines = ed_log.readlines()
    # print("Got ", len(lines), "lines from E:D log")
    curr_sys = ''
    for line in lines:
        line = line.strip()
        print(line)
        if line.count('StarSystem') > 0:
            curr_sys = line

    if curr_sys > '':
        new_system = curr_sys.split('"StarSystem":"')[1].split('"')[0]
        if current_system != new_system:
            current_system = new_system
            if jumping:
                jumping = False
                cool_down = True
                root.after(1000 * 180, cool_down_complete)
            print("Current system=", current_system)
            system_label.config(text=current_system)
            root.update_idletasks()

    root.after(1000, process_log)


def set_status(msg=''):
    status.config(text=msg)
    root.update_idletasks()


def check_keys():
    if kb.is_pressed('ctrl+f11'):
        set_status("ctrl+f11 pressed")
        root.after(100, refuel())
    root.after(20, check_keys)


log = get_lastest_log_file()
print("Opening E:D log: ", log)
ed_log = open(log, 'r')
process_log()  # start log processing

check_keys()  # start key monitoring
root.mainloop()  # run
