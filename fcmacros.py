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
import webbrowser
import ocr
from keymaps import *
from locations import *
import logging
import logging.handlers
import sys
import win32gui
import zipfile

VERSION = "0.2.3"
BUNDLED = False
LOGFILE = "fcmacros.log"

# Global state
current_system = ''
jumping = False
cool_down = False
auto_jump = False
jump_one = False
ship = ''
route = []
next_waypoint = ''
route_file = ""
is_odyssey = False
screen_shape = [1080, 1920, 3]
fullscreen = False
carrier_services_loc = None

# initialize settings
settings = usersettings.Settings('com.ed.fcmacros')
settings.add_setting("route_file", str, default="")
settings.add_setting("refuel", int, default=1)
settings.add_setting("debug", int, default=0)
settings.add_setting("grayscale", int, default=0)
settings.add_setting("confidence", int, default=75)

logger = logging.getLogger()


def log_setup():
    global BUNDLED
    # Logging setup
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
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logging.info(f"Starting fcmacros.py version: {VERSION}")
    if BUNDLED: logging.info('Running in a PyInstaller bundle')
    else: logging.info('Running as a console application')


def check_for_themes():
    logging.debug("Check for awthemes")
    r = glob.glob("./awthemes-10.4.0/awthemes.tcl")
    if len(r) == 0:
        logging.info("Unzipping awthemes")
        with zipfile.ZipFile("awthemes-10.4.0.zip", "r") as zipf:
            zipf.extractall(".")


def set_debug_level():
    if settings.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


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
    settings.grayscale = GRAYSCALE.get()
    try:
        settings.confidence = int(CONFIDENCE.get())
    except ValueError:
        pass

    settings.save_settings()

    root.after(1000, check_settings)


# Find most recent E:D log file
def get_latest_log_file():
    list_of_files = glob.glob(
        f"C:\\Users\\{getpass.getuser()}\\Saved Games\\Frontier Developments\\Elite Dangerous\\Journal.*")
    return max(list_of_files, key=os.path.getmtime)


def get_current_focus():
    global screen_shape, fullscreen
    logging.debug("Checking window focus before running macro")
    win = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(win)
    if title != "Elite - Dangerous (CLIENT)":
        logging.warning(f"Current window is '{title}' and not 'Elite - Dangerous' abort macro")
        set_status("Elite - Dangerous does not have the focus, aborting")
        return False
    logging.debug("Elite - Dangerous has the focus, macro proceeding")
    screen_shape = ocr.get_screen_width()
    fullscreen = ocr.is_fullscreen()
    if fullscreen: adjust_for_fullscreen()

    return True


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
def press(key, delay=0.5, down_time=0.2):
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


# Hold image list
images_dict = {}


def get_matching_images(image):
    if image in images_dict:
        image_set = images_dict[image]
    else:
        image_set = glob.glob("images/" + image + "-*.png")
        logging.info(f"Found { len(image_set)} images for {image}: {image_set}")
        images_dict[image] = image_set

    return image_set


# look for the image on screen , if found, return True
# if not, press the key specified, true this up to max_trues times,
# if max_tries is exceeded return False
# confidence is the confidence interval on the match
def deprecated_press_and_find(key, image, max_tries=10, do_log=True):
    image_set = get_matching_images(image)
    grayscale = settings.grayscale == 1
    confidence = settings.confidence / 100.0
    return deprecated_press_and_find_set(key, image_set, max_tries, confidence, grayscale, do_log)


# look for words on screen , if found, return True
# if not, press the key specified, true this up to max_trues times,
# if max_tries is exceeded return False
def press_and_find_text(key, words, region=None, max_tries=10):
    while max_tries >= 0:
        max_tries -= 1
        found, where = ocr.is_text_on_screen(words, region=region)
        if found:
            return True
        press(key)
    return False


# As above, but for a list of a list of words - used to validate the right HUD is selected
def press_and_find_text_list(key, words_list, region=None, max_tries=10):
    while max_tries >= 0:
        max_tries -= 1
        found, where = ocr.is_text_on_screen_list(words_list, region=region)
        if found:
            return True
        press(key)
    return False


# Press a key until the indicated region is highlighted
def press_until_selected_region(key, region, debug_text, max_count=10):
    logging.info(f"Selecting region {debug_text} at {region}")
    while max_count >= 0:
        max_count -= 1
        if ocr.get_average_color_bw(region, debug_text=debug_text) > ENABLED_THRESHOLD: return True
        press(key)
    return False


# Search for any of a set of text on the screen
# If not found, press key
# Repeat
def press_until_text_found(key, word_list, max_count=10, pause=0.5):
    while max_count > 0:
        b, res = ocr.is_text_on_screen_list(word_list)
        if b:
            logging.debug(f"Found Words {res}")
            return True
        press(key)
        max_count -= 1
        sleep(pause)
    return False


# Return to the center HUD
def return_hud_to_start():
    if not press_until_text_found(ED_BACK, [["LAUNCH"], ["AUTO"], ["DISEMBARK"], ["CARRIER", "SERVICES"]], max_count=10):
        set_status("Unable to find main HUD")
        return False
    if ocr.get_average_color_bw(get_carrier_services_location(), debug_text="CARRIER SERVICES") > ENABLED_THRESHOLD:
        return True
    press(ED_UI_UP)
    press(ED_UI_UP)
    press(ED_UI_UP)
    return press_until_selected_region(ED_UI_DOWN, get_carrier_services_location(), debug_text="CARRIER SERVICES", max_count=5)


# Locate an image(set) on the screen, return its found position
def deprecated_locate_on_screen(image, do_log=True):
    image_set = get_matching_images(image)

    grayscale = settings.grayscale == 1
    confidence = settings.confidence / 100.0
    return locate_on_screen_set(image_set, confidence, grayscale, do_log)


def locate_on_screen_set(images=None, confidence=0.75, grayscale=False, do_log=True):
    if images is None:
        images = []
    for i in images:
        pos = pyautogui.locateOnScreen(i, confidence=confidence, grayscale=grayscale)
        if pos is not None:
            if do_log: logging.debug(f"Found {i}")
            return pos
    return None


def deprecated_press_and_find_set(key=ED_UI_LEFT, images=None, max_tries=10, confidence=0.75, grayscale=False, do_log=True):
    if images is None:
        images = []
    cnt = 0
    if do_log: logging.debug(f"Looking for one of {images}")
    while True:
        for i in images:
            if pyautogui.locateOnScreen(i, confidence=confidence, grayscale=grayscale) is not None:
                if do_log: logging.debug(f"Found {i}")
                return True
        press(key)
        cnt += 1
        if cnt > max_tries:
            logging.debug(f"No image found after {max_tries} attempts")
            set_status('Macro failed')
            return False


def mouse_move_to_region(region, x_offset=0, y_offset=0):
    x = region[0] + region[2]//2 + x_offset
    y = region[1] + region[3]//2 + y_offset
    pyautogui.moveTo(x, y)


def mouse_click_at_region(region, pause=0.25, click_duration=0.25, x_offset=0, y_offset=0):
    x = region[0] + region[2]//2 + x_offset
    y = region[1] + region[3]//2 + y_offset
    mouse_click_at(x, y, pause=pause, click_duration=click_duration)


def mouse_click_at(x, y, pause=0.25, click_duration=0.25):
    pyautogui.moveTo(x, y)
    sleep(pause)
    pyautogui.mouseDown()
    sleep(click_duration)
    pyautogui.mouseUp()


def get_carrier_services_location():
    global carrier_services_loc
    if carrier_services_loc is not None:
        return carrier_services_loc

    if ship in carrier_services_locations.keys():
        loc = carrier_services_locations[ship]
        carrier_services_loc = (loc[0]-10, loc[1]-3, loc[2]+20, loc[3]+6)
        logging.info(f'Found know carrier services location for {ship} at {carrier_services_loc}')
        return carrier_services_loc

    carrier_services_loc = ocr.get_carrier_services_loc()
    if carrier_services_loc is None:
        set_status("Unable to find CARRIER SERVICES")
        return None

    new_loc = (carrier_services_loc[0], carrier_services_loc[1],
               carrier_services_loc[2]-carrier_services_loc[0],
               carrier_services_loc[3] - carrier_services_loc[1])
    carrier_services_loc = new_loc
    logging.info(f"Found CARRIER SERVICES at {new_loc}")

    return carrier_services_loc


# Move back to the carrier main screen after a jump
def reset_to_main_hud_after_jump():
    sleep(5)
    logging.debug("Select right HUD (workaround)")
    if not press_and_find_text_list(ED_RIGHT_WINDOW, [["MODULES"], ["STATUS"], ["FIRE", "GROUPS"]]):
        set_status("Unable to verify right HUD - cant find MODULES, STATUS or FIRE GROUPS")
        return False
    sleep(1)
    logging.debug("Back to center HUD")
    if not return_hud_to_start(): return False
    if ocr.get_average_color_bw(get_carrier_services_location(), debug_text="CARRIER SERVICES") <= ENABLED_THRESHOLD:
        set_status("Unable to find selected CARRIER SERVICES")
        return False


# Callback to schedule a jump
def schedule_jump():
    find_system_and_jump()


# Macro to schedule a jump
def find_system_and_jump(*args):
    global jumping, jump_one

    # Check E:D still has the focus
    if not get_current_focus(): return False

    # Get next waypoint and check I'm still enabled for auto jump
    if len(next_waypoint) < 3:
        set_status("No next waypoint")
        return False

    if not (auto_jump or jump_one):
        logging.warning("Jump requested but no jump is enabled")
        set_status("Jump is disabled, aborting")
        return False

    if do_refuel.get() == 1:
        new_args = [donate_tritium, load_tritium, find_system_and_jump_1]
        for a in args: new_args.append(a)
        load_tritium(*new_args)
    else:
        root.after(100, find_system_and_jump_1, *args)


def find_system_and_jump_1(*args):
    global jumping, jump_one
    if jump_one: jump_one = False
    set_status('Finding next waypoint')

    # Back to main menu
    if not return_hud_to_start(): return False
    press(ED_UI_SELECT)

    if not press_until_selected_region(ED_UI_DOWN, TRITIUM_DEPOT_POS, ED_UI_UP): return False
    if not press_until_selected_region(ED_UI_RIGHT, CARRIER_MANAGEMENT_POS, ED_UI_DOWN): return False
    press(ED_UI_SELECT)
    sleep(5)  # Wait for galmap, sometimes slow
    if not press_until_selected_region(ED_UI_DOWN, NAVIGATION_ICON, debug_text="NAVIGATION ICON", max_count=5):
        set_status("Unable to select NAVIGATION ICON")
        return False
    press(ED_UI_SELECT)
    sleep(0.5)
    if not press_until_selected_region(ED_UI_DOWN, GALMAP_IMAGE, debug_text="OPEN GALMAP", max_count=5):
        set_status("Unable to SELECT OPEN GALMAP")
        return False
    press(ED_UI_SELECT)
    root.after(3000, find_system_and_jump_2, *args)


def find_system_and_jump_2(*args):
    global jumping, jump_one
    mouse_click_at_region(GALMAP_SEARCH)
    kb.write(next_waypoint)
    sleep(1)
    mouse_click_at_region(GALMAP_SEARCH, y_offset=GALMAP_SEARCH[3])
    sleep(2)
    mouse_move_to_region(SET_CARRIER_DESTINATION_POS)
    sleep(0.25)
    # Check if set carrier destination is selectable
    if ocr.get_average_color_bw(SET_CARRIER_DESTINATION_POS) <= ENABLED_THRESHOLD:
        set_status("Destination is invalid")
        return
    mouse_click_at_region(SET_CARRIER_DESTINATION_POS)
    set_status("Jump set for {}".format(next_waypoint))
    jumping = True

    if not return_hud_to_start(): return False
    press(ED_UI_SELECT)
    call_next_args(100, *args)


# Callback to refuel the ship, the carrier and then the ship
# to optimise carrier mass and save up to 1 ton of fuel per jump
def refuel():
    if not get_current_focus(): return
    set_status('Refueling')
    if not load_tritium(donate_tritium): return


# Refill ship with tritium
def load_tritium(*args):
    # Check E:D still has the focus
    if not get_current_focus(): return False

    set_status('Filling ship with tritium')
    if not return_hud_to_start(): return False
    press(ED_RIGHT_WINDOW, 0.5)
    root.after(100, load_tritium_1, *args)


def load_tritium_1(*args):
    if not press_until_selected_region(ED_MENU_RIGHT, INVENTORY_POS, debug_text="INVENTORY", max_count=15):
        set_status("Unable to select INVENTORY")
        return False
    if not press_until_selected_region(ED_UI_RIGHT, TRANSFER_POS, debug_text="TRANSFER", max_count=5):
        press(ED_UI_UP)
        sleep(0.5)
        press(ED_UI_UP)
        if not press_until_selected_region(ED_UI_RIGHT, TRANSFER_POS, debug_text="TRANSFER"):
            set_status("Unable to select TRANSFER")
            return False
    press(ED_UI_SELECT)
    root.after(100, load_tritium_2, *args)


# Find the select words on the screen  (bounding box)
# Press key until the words are selectable
# If the Words are not found, press the alt_key_if_words_not_found
# Retry both operations up to max_Cnt
def press_until_selected_text(key, words, alt_key_if_words_not_found, max_cnt=10):
    cnt = 0
    while True:
        cnt += 1
        if cnt >= max_cnt:
            logging.warning(f"Unable to find words for selection: {words}")
            return False
        b, loc = ocr.is_text_on_screen(words, debug=True, show=False, save=words[0])
        if not b:
            press(alt_key_if_words_not_found)
        else:
            break
    region = [loc[0]-20, loc[1], loc[2]-loc[0]+40, loc[3]-loc[1]]
    cnt = 0
    while cnt < max_cnt:
        if ocr.get_average_color_bw(region) > ENABLED_THRESHOLD:
            break
        press(key)
        cnt += 1
    if cnt >= max_cnt:
        logging.debug(f"Unable to find selected text: {words} at: {region}")
        return False
    return True


def load_tritium_2(*args):
    if not press_until_selected_text(ED_UI_UP, ["TRITIUM"], ED_UI_DOWN): return False

    # hold down the ED_UI_LEFT key until max capacity is reached
    kb.press(ED_UI_LEFT)
    logging.debug(f"Press and hold {ED_UI_LEFT}")
    while True:
        res, loc = ocr.is_text_on_screen(["MAX", "CAPACITY"], region=MAX_CAPACITY_POS, debug=True, save='max_capacity', show=False)
        if res: break
        sleep(0.3)
    logging.debug(f"max_capacity found")
    logging.debug(f"Release {ED_UI_LEFT}")
    kb.release(ED_UI_LEFT)
    root.after(100, load_tritium_3, *args)


def load_tritium_3(*args):
    if not press_until_selected_region(ED_UI_DOWN, TRANSFER_CANCEL_POS, ED_UI_UP): return False
    press(ED_UI_RIGHT)
    press(ED_UI_SELECT)
    set_status('tritium loaded')
    if not return_hud_to_start(): return False
    call_next_args(100, *args)


def call_next_args(delay_ms=100, *args):
    if len(args) > 0:
        if len(args) > 1:
            new_args = args[1:]
            root.after(delay_ms, args[0], *new_args)
        else:
            root.after(delay_ms, args[0])


# Donate tritium
def donate_tritium(*args):
    set_status('Donating tritium')
    if not return_hud_to_start(): return False
    press(ED_UI_SELECT)

    if not press_until_selected_region(ED_UI_DOWN, TRITIUM_DEPOT_POS, ED_UI_UP): return False
    press(ED_UI_SELECT)
    sleep(0.5)
    if not press_until_selected_region(ED_UI_UP, DONATE_TRITIUM_POS, debug_text="DONATE TRITIUM"): return False
    press(ED_UI_SELECT)
    if not press_until_selected_region(ED_UI_UP, CONFIRM_DEPOSIT_POS, debug_text="CONFIRM DEPOSIT"): return False
    press(ED_UI_SELECT)
    set_status('tritium donated')
    if not press_until_selected_region(ED_UI_DOWN, TRITIUM_EXIT, debug_text="EXIT DOOR"): return False
    press(ED_UI_SELECT)

    return_hud_to_start()

    call_next_args(100, *args)


def empty_cargo():
    # Check focus is E:D
    if not get_current_focus(): return False

    set_status('Emptying your cargo hold')
    if not return_hud_to_start(): return False

    press(ED_RIGHT_WINDOW, 0.5)
    if not press_until_selected_region(ED_MENU_RIGHT, INVENTORY_POS, max_count=15, debug_text="INVENTORY"): return False
    press(ED_UI_RIGHT)
    press(ED_UI_RIGHT)
    press(ED_UI_UP)
    press(ED_UI_UP)
    if not press_until_selected_region(ED_UI_RIGHT, TRANSFER_POS, debug_text="TRANSFER"): return False
    press(ED_UI_SELECT)
    if not press_until_selected_text(ED_UI_UP, ["TO", "CARRIER"], ED_UI_DOWN): return False
    press(ED_UI_SELECT)
    sleep(0.5)
    press(ED_UI_SELECT)
    set_status('Cargo hold emptied')

    return_hud_to_start()


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
    next_waypoint = route[0]


def dark_style2(tk_root):
    _style = ttk.Style(tk_root)
    tk_root.tk.call('source', 'awthemes-10.4.0/awdark.tcl')
    _style.theme_use('awdark')
    return _style


ui_started = False
root: Tk
do_refuel: tkinter.IntVar
DEBUG: tkinter.IntVar
GRAYSCALE: tkinter.IntVar
CONFIDENCE: tkinter.IntVar
progress: tkinter.IntVar
system_label: ttk.Label
route_label: ttk.Label
route_pos_label: ttk.Label
route_jump_label: ttk.Label
route_len_label: ttk.Label
auto_jump_label: ttk.Label
status: ttk.Label
log = ""
if log > "":
    ed_log = open(log, 'r')
else:
    ed_log = None


def on_debug_change(*args):
    if DEBUG is not None and DEBUG.get() == 1:
        logging.info("Debug enabled")
    else:
        logging.info("Debug disabled")
    check_settings()


# Setup UI
def setup_ui():
    global root, ui_started, do_refuel, DEBUG, GRAYSCALE, CONFIDENCE, progress, system_label, route_label, route_jump_label, route_len_label, route_pos_label, status, auto_jump_label, log, ed_log

    root = Tk()
    root.title("Fleet Carrier Macros")
    root.iconbitmap('images/fc_icon.ico')
    dark_style2(root)

    do_refuel = tkinter.IntVar()
    DEBUG = tkinter.IntVar()
    GRAYSCALE = tkinter.IntVar()
    CONFIDENCE = tkinter.StringVar()
    CONFIDENCE.set("75")

    DEBUG.trace_add("write", on_debug_change)
    GRAYSCALE.trace_add("write", on_debug_change)
    CONFIDENCE.trace_add("write", on_debug_change)

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

    ttk.Label(frame, text="Debug Log?").grid(column=0, row=row, sticky="e")
    ttk.Checkbutton(frame, variable=DEBUG).grid(column=1, row=row, sticky="w")
    # ttk.Label(frame, text="Image matching confidence?").grid(column=2, row=row, sticky="e")
    # ttk.Checkbutton(frame, variable=GRAYSCALE).grid(column=3, row=row, sticky="w")
    # ttk.Spinbox(frame, from_=10, to=90, textvariable=CONFIDENCE).grid(column=3, row=row, sticky="e")

    row += 1
    ttk.Label(frame, text="Version " + VERSION).grid(column=0, row=row, sticky="w")
    auto_jump_label = ttk.Label(frame, text="")
    auto_jump_label.grid(column=2, row=row, sticky="ew", columnspan=2)

    row += 1
    link1 = ttk.Label(frame, text="FCMacros Homepage (github)", cursor="hand2", foreground="lightblue")
    link1.grid(column=0, row=row, columnspan=4, sticky="w")
    link1.bind("<Button-1>", lambda e: callback("https://github.com/pilotso11/fc-macros"))
    ttk.Button(frame, text="Quit", command=root.destroy).grid(column=4, row=row)

    settings.load_settings()
    do_refuel.set(settings.refuel)
    DEBUG.set(settings.debug)
    set_debug_level()
    GRAYSCALE.set(settings.grayscale)
    CONFIDENCE.set(settings.confidence)

    log = get_latest_log_file()
    logging.info(f"Opening E:D log: {log}")
    ed_log = open(log, 'r')

    return root


def callback(url):
    webbrowser.open_new(url)


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
        ed_log = open(log, 'r', encoding='utf-8')
    root.after(10000, check_newer_log)


def process_log():
    global current_system, jumping, cool_down, is_odyssey, ship, carrier_services_loc
    try:
        lines = ed_log.readlines()
        if len(lines) > 0:
            logging.debug(f"Got {len(lines)} lines from E:D log")
        new_system = ''
        new_ship = ''
        for line in lines:
            line = line.strip()
            # logging.debug(line)
            if line.count('StarSystem') > 0:
                new_system = get_value_from_log_line(line, 'StarSystem')
            if line.count('Odyssey') > 0:
                ody = get_value_from_log_line(line, 'Odyssey')
                if ody == "true":
                    is_odyssey = True
                    logging.info("We're in Odyssey")
            if line.count('CarrierJumpRequest') > 0:
                dest = get_value_from_log_line(line, 'SystemName')
                if dest == next_waypoint:
                    set_status("Jump to {} confirmed".format(dest))
            if line.count('event":"Loadout') > 0:
                new_ship = get_value_from_log_line(line, 'Ship')

        # Process last ship
        if '' < new_ship != ship:
            ship = new_ship
            carrier_services_loc = None
            logging.info(f"Current ship is '{ship}'")

        # Process last system
        if '' < new_system != current_system:
            current_system = new_system
            if jumping:
                jumping = False
                cool_down = True
                root.after(1000 * 210, cool_down_complete)
                reset_to_main_hud_after_jump()
                # and into the CARRIER SERVICES
                press(ED_UI_SELECT)

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
        root.after(1000, check_keys)
        return
    if kb.is_pressed('Ctrl+F3'):
        ocr.capture_debug()
        root.after(5000, check_keys)
        return
    root.after(20, check_keys)


# Run the UI
def run_ui():
    ui_root = setup_ui()
    check_newer_log()  # Start checking for log rotation
    process_log()  # start log processing
    check_settings()  # start monitoring settings
    check_keys()  # start key monitoring
    ui_root.mainloop()  # run


def run_main():
    global ui_started, screen_shape
    if ui_started: return
    ui_started = True
    log_setup()
    check_for_themes()
    ocr.check_for_tesseract_exe()
    run_ui()


if __name__ == '__main__':
    run_main()
