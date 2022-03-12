import cv2
import pyautogui
import pytesseract
import numpy as np
import fcmacros
from time import sleep
from keymaps import *
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


# Take a screenshot and save it , with region, return CV image
def get_and_save_cv_screenshot(file, x, y, x2, y2):
    pil_image = pyautogui.screenshot(file, region=(x - 5, y - 5, x2 - x + 10, y2 - y + 10))
    image = np.array(pil_image)
    image = image[:, :, ::-1].copy()
    return image


# Screencap CARRIER MANAGEMENT selected
def capture_carrier_management_and_tritium_depot(debug=False):
    fcmacros.set_to_carrier()
    sleep(5)  # Wait for fleet carrier to be ready
    image = get_cv_screenshot()
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    results = recognise(gray_image)
    mid_cm = find_words(["CARRIER", "MANAGEMENT"], results)
    mid_td = find_words(["TRITIUM", "DEPOT"], results)
    if mid_cm is None:
        logging.warning("Didn't find CARRIER MANAGEMENT")
        fcmacros.set_status("Didn't find CARRIER MANAGEMENT")
        return None, None
    if mid_td is None:
        logging.warning("Didn't find TRITIUM DEPOT")
        fcmacros.set_status("Didn't find TRITIUM DEPOT")
        return None, None
    carrier_services_loc = mid_cm
    tritium_depot_loc = mid_td
    fcmacros.press(ED_UI_DOWN)
    fcmacros.press(ED_UI_DOWN)
    # on TRITIUM DEPOT
    x, y, x2, y2 = tritium_depot_loc[0], tritium_depot_loc[1], tritium_depot_loc[2], tritium_depot_loc[3]
    part = get_and_save_cv_screenshot('images/tritium_depot99.png', x, y, x2, y2)
    if debug:
        cv2.imshow('depot', part)
    fcmacros.set_status('Saved tritium_depot99.png')
    fcmacros.press(ED_UI_RIGHT)
    fcmacros.press(ED_UI_RIGHT)
    # Carrier Services is selected
    x, y, x2, y2 = carrier_services_loc[0], carrier_services_loc[1], carrier_services_loc[2], carrier_services_loc[3]
    part = get_and_save_cv_screenshot('images/carrier_management9.png', x, y, x2, y2)
    if debug:
        cv2.imshow('carrier management', part)
        cv2.waitKey(0)
    fcmacros.set_status('Saved carrier_management99.png')
    fcmacros.press(ED_BACK)
    return mid_cm, mid_td


# Screencap selected INVENTORY menu
def capture_inventory_and_transfer(debug=False):
    region = (600, 220, 1200, 200)
    sleep(2)
    inventory_box = None
    transfer_box = None
    cnt = 0
    while not fcmacros.get_current_focus():
        cnt += 1
        fcmacros.set_status(f'Looking for E:D {cnt}')
        if cnt > 5:
            fcmacros.set_status(f'E:D Does not have focus, aborting')
            return False
        sleep(2)

    while True:
        image = get_cv_screenshot(region)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        results = recognise(gray_image, debug=True, confidence=50)
        mid = find_words(["INVENTORY"], results)
        mid_trans = find_words(["TRANSFER"], results, confidence=50)
        ship_mid = find_words(["SHIP"], results)

        if mid_trans is not None and transfer_box is None:
            transfer_box = mid_trans
        if mid is None and inventory_box is None and ship_mid is None:
            logging.debug("Menu not found")
            fcmacros.press(ED_MENU_RIGHT)
            fcmacros.press(ED_RIGHT_WINDOW, delay=1)
        elif mid is None and inventory_box is None:
            fcmacros.press(ED_MENU_LEFT)
        elif mid is None:
            if mid_trans is None:  # Maybe smoke on the label?
                sleep(1)
                continue
            logging.debug("Inventory not found - get screencap")
            x, y, x2, y2 = inventory_box[0], inventory_box[1], inventory_box[2], inventory_box[3]
            x += region[0]
            y += region[1]
            x2 += region[0]
            y2 += region[1]
            part = get_and_save_cv_screenshot('images/inventory99.png', x, y, x2, y2)
            if debug:
                cv2.imshow('inventory', part)
            fcmacros.set_status('Saved inventory99.png')
            fcmacros.press(ED_UI_RIGHT)
            fcmacros.press(ED_UI_RIGHT)
            x, y, x2, y2 = transfer_box[0], transfer_box[1], transfer_box[2], transfer_box[3]
            x += region[0]
            y += region[1]
            x2 += region[0]
            y2 += region[1]
            part = get_and_save_cv_screenshot('images/transfer99.png', x, y, x2, y2)
            fcmacros.set_status('Saved transfer99.png')
            if debug:
                cv2.imshow('transfer', part)
                cv2.waitKey(0)
            fcmacros.press(ED_BACK)
            fcmacros.press(ED_BACK)
            return True
        else:
            if inventory_box is None:
                print(f"INVENTORY at {mid}")
                inventory_box = mid
                x, y, x2, y2 = inventory_box[0], inventory_box[1], inventory_box[2], inventory_box[3]
                x += region[0]
                y += region[1]
                x2 += region[0]
                y2 += region[1]
                part = get_and_save_cv_screenshot('images/inventory_unselected99.png', x, y, x2, y2)
                if debug:
                    cv2.imshow('unselected', part)
                fcmacros.set_status('Saved inventory_unselected99.png')
            fcmacros.press(ED_MENU_RIGHT, delay=0.5)


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
        mid_al = find_words(["AUTO", "LAUNCH"], results)
        mid_cs = find_words(["CARRIER", "SERVICES"], results)
        if mid_cs is None and mid_al is not None:
            logging.debug(f"Found AUTO LAUNCH at {mid_al}")
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
                return True
            else:
                fcmacros.press(ED_UI_UP, delay=0.5)


def test():
    image1 = cv2.imread('test/test5.jpg')
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

    results = recognise(gray_image, confidence=51, debug=True, show=True, save=True)

    mid = find_words(["INVENTORY"], results)
    if mid is not None:
        print(f"Found INVENTORY at {mid}")


def dist(x1, y1, x2, y2):
    try:
        result = np.sqrt((x2 - x1) ** 2 - (y1 - y2) ** 2)
        return result
    except RuntimeWarning:
        return 0


# Find closest set of lines
def find_close(lines, max_dist=20):
    max_set = []
    for line in lines:
        results = [line]
        for x1, y1, x2, y2 in line:
            for line2 in lines:
                for x3, y3, x4, y4 in line2:
                    d1 = dist(x1, y1, x3, y3)
                    d2 = dist(x2, y2, x4, y4)
                    if 0 < d1 < max_dist and d2 < max_dist:
                        results.append(line2)
        if len(results) > len(max_set):
            max_set = results
    return max_set


# Box is top left, top right, bottom left, bottom right
# Find largest box encompassing the lines provided
def get_bounding_box(lines):
    x_tl, y_tl, x_tr, y_tr, x_bl, y_bl, x_br, y_br = 0, 0, 0, 0, 0, 0, 0, 0
    for line in lines:
        for x1, y1, x2, y2 in line:
            if x_tl == 0:
                x_tl = x1
                x_bl = x1
                y_tl = y1
                y_bl = y1
                x_tr = x2
                x_br = x2
                y_tr = y2
                y_br = y2
            else:
                x_tl = min(x_tl, x1)
                y_tl = min(y_tl, y1)
                x_bl = max(x_bl, x1)
                y_bl = max(y_bl, y1)

                x_tr = min(x_tr, x2)
                y_tr = min(y_tr, y2)
                x_br = max(x_br, x2)
                y_br = max(y_br, y2)
    return x_tl, y_tl, x_tr, y_tr, x_bl, y_bl, x_br, y_br


# Box is top left, top right, bottom left, bottom right
def bounding_box_scale(w, h, bound_box):
    x_tl, y_tl, x_tr, y_tr, x_bl, y_bl, x_br, y_br = bound_box[0], bound_box[1], bound_box[2], bound_box[3], bound_box[
        4], bound_box[5], bound_box[6], bound_box[7]
    x_scale = w / (x_tr - x_tl)
    y_scale = x_scale  # h / (y_bl-y_tl)

    x_missing = w - (x_tr * x_scale - x_tl)
    y_missing = h - (y_bl * y_scale - y_tl)
    x_shift = x_tl
    y_shift = y_tl

    x_tl = x_tl - x_shift
    x_tr = x_tr * x_scale - x_shift + x_missing
    x_bl = x_bl - x_shift
    x_br = x_br * x_scale - x_shift + x_missing

    y_tl = y_tl - y_shift
    y_bl = y_bl * y_scale - y_shift + y_missing
    y_tr = y_tr - y_shift
    y_br = y_br * y_scale - y_shift + y_missing

    if x_tr < 0:
        x_tl -= x_tr
        x_bl -= x_tr
        x_br -= x_tr
        x_tr = 0
    if y_tr < 0:
        y_bl -= y_tr
        y_tl -= y_tr
        y_br -= y_tr
        y_tr = 0

    return x_tl, y_tl, x_tr, y_tr, x_bl, y_bl, x_br, y_br


def remove_perspective(image):
    threshold_image = cv2.threshold(image, 50, 200, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    cv2.imshow('threshold', threshold_image)
    edges = cv2.Canny(threshold_image, 50, 150)
    cv2.imshow('edges', edges)
    lines = cv2.HoughLinesP(threshold_image, 1, np.pi / 180, 15, minLineLength=400, maxLineGap=30)
    line_image = np.copy(image) * 0  # creating a blank to draw lines on
    for line in lines:
        for x1, y1, x2, y2 in line:
            slope = (x2 - x1) / (y2 - y1)
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 1)

    close = find_close(lines)
    bound_box = get_bounding_box(close)
    print(f'--------Closest size {len(close)}--------')
    print(close)
    print('--------')
    print(
        f'Bounding box = ({bound_box[0]},{bound_box[1]}) ({bound_box[2]},{bound_box[3]}) ({bound_box[4]},{bound_box[5]}) ({bound_box[6]},{bound_box[7]})')
    window_box = bounding_box_scale(1500, 900, bound_box)
    x1, y1, x2, y2, x3, y3, x4, y4 = window_box[0], window_box[1], window_box[2], window_box[3], window_box[4], \
                                     window_box[5], window_box[6], window_box[7]
    print(f'Scaled box = ({x1},{y1}) ({x2},{y2}) ({x3},{y3}) ({x4},{y4}) ')
    cv2.imshow('line image', line_image)
    pts_src = np.float32([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
    pts_dst = np.float32([[0.0, 0.0], [1500.0, 0.0], [0.0, 900.0], [1500.0, 900.0]])
    xform = cv2.getPerspectiveTransform(pts_src, pts_dst)
    warped_image = cv2.warpPerspective(image, xform, (1500, 900))
    cv2.imshow('warped image', warped_image)


def recognise(image, debug=False, show=False, save=False, confidence=80):
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
                print(
                    f"'{details['text'][sequence_number]}' conf={details['conf'][sequence_number]} at {x},{y} - {w},{h}")
        if show:
            cv2.imshow('captured text', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        if save:
            cv2.imwrite('debug.png', image)

    return details


def get_box_dist(x1, y1, w1, h1, x2, y2, w2, h2):
    d = 1000
    d = min(d, abs(x1 - x2))
    d = min(d, abs(y1 - y2))
    d = min(d, abs(x1 + w1 - x2))
    d = min(d, abs(y1 + h1 - y2))
    return d


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
            print(f"found {words[0]} at {x},{y} {w}x{h}")
            loc = [(x, y, w, h)]
            if len(words) == 1:  # just one word
                return get_box_from_set(loc)

            for word in words[1:]:
                for j in range(len(results['text'])):
                    conf = float(results['conf'][j])
                    text = results['text'][j]
                    (x2, y2, w2, h2) = (
                        results['left'][j], results['top'][j], results['width'][j], results['height'][j])
                    if conf > confidence and text == word:
                        if get_box_dist(x, y, w, h, x2, y2, w2, h2) < max_dist:
                            print(f"found {word} at {x2},{y2} {w2}x{h2}")
                            loc.append((x2, y2, w2, h2))
                            if len(loc) == len(words):
                                print("Found all words")
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


# Capture the screen and ORR it, show the results
def capture_debug():
    check_for_tesseract_exe()
    test()


# Capture all needed images
# Work in progresss ....
def capture_all_images():
    check_for_tesseract_exe()
    if not capture_carrier_services(): return
    if not capture_inventory_and_transfer(): return
    a, b = capture_carrier_management_and_tritium_depot()
    if a is None: return
    fcmacros.set_status("Saved images .... ")

