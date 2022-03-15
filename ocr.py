# Copyright (c) 2022 Seth Osher
# OCR and Screen Image detection for fcmacros
import os

import cv2
import pyautogui
import pytesseract
import numpy as np
import fcmacros
from time import sleep
from keymaps import *
from locations import *
import logging
import glob
import zipfile

# Teserect installer for windows
# https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = "./Tesseract-OCR/tesseract.exe"
custom_config = r'--oem 3 --psm 12'


# Get screenshot as CV image
def get_cv_screenshot(region=None):
    if region is None:
        pil_image = pyautogui.screenshot()
    else:
        pil_image = pyautogui.screenshot(region=region)
    image = np.array(pil_image)
    image = image[:, :, ::-1].copy()
    return image


# Take a screenshot and save it , with region x, y, w, h, return CV image
def get_and_save_cv_screenshot_region(file, region):
    pil_image = pyautogui.screenshot(file, region=region)
    image = np.array(pil_image)
    image = image[:, :, ::-1].copy()
    return image


# Take a screenshot and save it , with region, x, y, x2, y2, return CV image
def get_and_save_cv_screenshot(file, x, y, x2, y2):
    pil_image = pyautogui.screenshot(file, region=(x - 5, y - 5, x2 - x + 10, y2 - y + 10))
    image = np.array(pil_image)
    image = image[:, :, ::-1].copy()
    return image


def get_carrier_services_loc():
    cnt = 0
    while not fcmacros.get_current_focus():
        cnt += 1
        fcmacros.set_status(f'Looking for E:D {cnt}')
        if cnt > 5:
            fcmacros.set_status(f'E:D Does not have focus, aborting')
            return None
        sleep(2)
    fcmacros.press(ED_BACK)
    fcmacros.press(ED_BACK)
    cnt = 0
    while True:
        image = get_cv_screenshot()
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        results = recognise(gray_image)
        mid_al = find_words(["LAUNCH"], results)
        mid_cs = find_words(["CARRIER", "SERVICES"], results)
        if mid_cs is None and mid_al is not None:
            logging.debug(f"Found LAUNCH at {mid_al}")
            fcmacros.press(ED_UI_DOWN, delay=0.5)
        else:
            if mid_cs is not None:
                logging.info(f"Found CARRIER SERVICES at {mid_cs}")
                return mid_cs
            else:
                fcmacros.press(ED_UI_UP, delay=0.5)
        cnt += 1
        if cnt > 5:
            logging.warning("Unable to find CARRIER SERVICES after 5 loops, aborting.")
            return None


# Screencap CARRIER SERVICES selected
def capture_carrier_services(debug=False):
    cnt = 0
    while not fcmacros.get_current_focus():
        cnt += 1
        fcmacros.set_status(f'Looking for E:D {cnt}')
        if cnt > 5:
            fcmacros.set_status(f'E:D Does not have focus, aborting')
            return False
        sleep(2)

    fcmacros.press(ED_BACK)
    fcmacros.press(ED_BACK)
    while True:
        image = get_cv_screenshot()
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        results = recognise(gray_image)
        mid_al = find_words(["LAUNCH"], results)
        mid_cs = find_words(["CARRIER", "SERVICES"], results)
        if mid_cs is None and mid_al is not None:
            logging.debug(f"Found LAUNCH at {mid_al}")
            fcmacros.press(ED_UI_DOWN, delay=0.5)
        else:
            if mid_cs is not None:
                logging.debug(f"Found CARRIER SERVICES at {mid_cs}")
                fcmacros.press(ED_UI_UP, delay=0.25)
                fcmacros.press(ED_UI_UP, delay=0.25)
                fcmacros.press(ED_UI_UP, delay=0.25)
                fcmacros.press(ED_UI_UP, delay=0.25)
                fcmacros.press(ED_UI_DOWN, delay=0.25)
                x, y, x2, y2 = mid_cs[0], mid_cs[1], mid_cs[2], mid_cs[3]
                part = get_and_save_cv_screenshot('images/carrier_services99.png', x, y, x2, y2)
                fcmacros.set_status("Saved carrier_services99.png")
                if debug:
                    cv2.imshow('screencap', part)
                    cv2.waitKey(0)
                fcmacros.root.after(100, after_carrier_services)
                return True
            else:
                fcmacros.press(ED_UI_UP, delay=0.5)


# Capture, regocnise, show and save the current screen
def test():
    image = get_cv_screenshot()
    # cv2.imshow('screen', image)
    # cv2.waitKey(0)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gray_image = cv2.bitwise_not(gray_image)
    # gray_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # gray_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 5, 2)
    # edges = cv2.Canny(image, 50, 150)

    # threshold_image = cv2.threshold(gray_image, 50, 200, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # cv2.imshow('original', image)
    # cv2.imshow('gray image', gray_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    recognise(gray_image, confidence=51, debug=True, show=True, save=True)


# Recognize text in image
# If debug is true then:
#    Text recognized with details will be logged
#    Show will create bounding boxes on an image copy and show it
#    Save will save the image
def recognise(image, debug=False, show=False, save=False, confidence=80, save_suffix=""):
    details = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=custom_config, lang='eng')

    if debug:
        # print(details['text'])
        total_boxes = len(details['text'])
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        # add rectangles on threshold image
        for sequence_number in range(total_boxes):
            if float(details['conf'][sequence_number]) > confidence and len(details['text'][sequence_number]) > 1:
                (x, y, w, h) = (
                    details['left'][sequence_number], details['top'][sequence_number],
                    details['width'][sequence_number],
                    details['height'][sequence_number])
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                logging.debug(
                    f"'{details['text'][sequence_number]}' conf={details['conf'][sequence_number]} at {x},{y} - {w},{h}")
        if show:
            cv2.imshow('captured text', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        if save:
            cv2.imwrite(f'debugimages/debug_{save_suffix}.png', image)

    return details


# Find min distance of two boxes (H or V, it doesn't look for a diagonal)
def get_box_dist(x1, y1, w1, h1, x2, y2):
    d = 1000
    d = min(d, abs(x1 - x2))
    d = min(d, abs(y1 - y2))
    d = min(d, abs(x1 + w1 - x2))
    d = min(d, abs(y1 + h1 - y2))
    return d


# Find bounding area for a set of locations (close words)
def get_box_from_set(locs):
    max_x = 0
    min_x = 10000
    max_y = 0
    min_y = 10000
    for loc in locs:
        x, y, w, h = loc[0], loc[1], loc[2], loc[3]
        max_x = max(max_x, x + w)
        min_x = min(min_x, x)
        max_y = max(max_y, y + h)
        min_y = min(min_y, y)

    return min_x, min_y, max_x, max_y


# Search for words near each other in the output
def find_words(words, results, confidence=90, max_dist=50):
    for i in range(len(results['text'])):
        conf = float(results['conf'][i])
        text = results['text'][i]
        (x, y, w, h) = (results['left'][i], results['top'][i], results['width'][i], results['height'][i])
        if conf > confidence and text == words[0]:
            logging.debug(f"found {words[0]} at {x},{y} {w}x{h}")
            loc = [(x, y, w, h)]
            if len(words) == 1:  # just one word
                return get_box_from_set(loc)

            for word in words[1:]:
                logging.debug(f"Looking for {word}")
                for j in range(len(results['text'])):
                    conf = float(results['conf'][j])
                    text = results['text'][j]
                    (x2, y2, w2, h2) = (
                        results['left'][j], results['top'][j], results['width'][j], results['height'][j])
                    if conf > confidence and text[:len(word)] == word:
                        if get_box_dist(x, y, w, h, x2, y2) < max_dist:   # w2, h2 not used
                            logging.debug(f"found {word} at {x2},{y2} {w2}x{h2}")
                            loc.append((x2, y2, w2, h2))
                            if len(loc) == len(words):
                                logging.debug("Found all words")
                                return get_box_from_set(loc)
    return None


def check_for_tesseract_exe():
    r = glob.glob("./Tesseract-OCR/tesseract.exe")
    if len(r) == 0:
        with zipfile.ZipFile("Tesseract-OCR.zip", "r") as zipf:
            zipf.extractall(".")


if __name__ == '__main__':
    check_for_tesseract_exe()
    test()


def get_screen_width():
    image = get_cv_screenshot()
    logging.info(f"Screen shape: {image.shape}")
    return image.shape


def is_text_on_screen_list(words_list, region=None, debug=False, save="", show=False):
    image = get_cv_screenshot(region)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    results = recognise(gray_image, confidence=51, debug=debug, save=len(save) > 0, show=show, save_suffix=save)
    for words in words_list:
        res = find_words(words, results, confidence=51)
        if res is not None:
            logging.debug(f"Found {words} at {res}")
            return True, res

    return False, None


def is_text_on_screen(words, region=None, debug=False, save="", show=False):
    image = get_cv_screenshot(region)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    results = recognise(gray_image, confidence=51, debug=debug, save=len(save) > 0, show=show, save_suffix=save)
    res = find_words(words, results, confidence=51)
    if res is None: return False, None
    return True, res


def get_average_color(region, debug_text=""):
    image = get_cv_screenshot(region)
    avg_color_per_row = np.average(image, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    logging.debug(f"Average color for {debug_text} at {region} is {avg_color}")
    return avg_color


def get_average_color_gray(region, debug_text=""):
    image = get_cv_screenshot(region)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    avg_color_per_row = np.average(gray_image, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    logging.debug(f"Average color for {debug_text} at {region} is {avg_color}")
    return avg_color


def get_average_color_bw(region, debug_text=""):
    image = get_cv_screenshot(region)
    cv2.imwrite(f'debugimages/debug_{debug_text}_color.png', image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f'debugimages/debug_{debug_text}_gray.png', gray_image)
    gray_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    cv2.imwrite(f'debugimages/debug_{debug_text}_thresh.png', gray_image)
    avg_color_per_row = np.average(gray_image, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    logging.debug(f"Average color for {debug_text} at {region} is {avg_color}")
    return avg_color


# Capture the screen and ORR it, show the results
def capture_debug():
    check_for_tesseract_exe()
    test()


# Capture all needed images
# Work in progresss ....
def capture_all_images():
    check_for_tesseract_exe()
    # capture_carrier_services()


def after_carrier_services(*args):
    fcmacros.set_status("Saved images .... ")


def is_fullscreen():
    f = glob.glob("debugimages")
    if len(f) == 0:
        os.mkdir("debugimages")
        logging.info("Created debugimages folder")

    val = get_average_color_bw(WINDOW_TEST) <= ENABLED_THRESHOLD
    logging.info(f"Fullscreen={val}")
    return val
