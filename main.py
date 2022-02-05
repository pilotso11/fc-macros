from tkinter import *
from tkinter import ttk
import keyboard as kb
import pyautogui
from time import sleep

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
    load_tritium()   # keep fully loaded to reduce tritium consumption

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


root = Tk()
frame = ttk.Frame(root, padding=10)
frame.grid()
ttk.Label(frame, text="Fleet Carrier Tools").grid(column=0, row=0)
ttk.Label(frame, text="Refuel").grid(column=0, row=1)
ttk.Label(frame, text="Ctrl+F11").grid(column=1, row=1)
status = ttk.Label(frame, text="this is the status bar --- nice and wide")
status.grid(column=0, row=2, columnspan=2)
ttk.Button(frame, text="Quit", command=root.destroy).grid(column=0, row=3)


def set_status(msg=''):
    status.config(text=msg)
    root.update_idletasks()


def check_keys():
    if kb.is_pressed('ctrl+f11'):
        set_status("ctrl+f11 pressed")
        root.after(100, refuel())
    root.after(20, check_keys)


check_keys()
root.mainloop()
