# Copyright (c) 2022 Seth Osher
# Offset to adjust for menubar missing on fullscreen
FULLSCREEN_OFFSET = -10
WINDOW_TEST = [635, 0, 100, 10]  # Location to test for window border

# Color depth threshold for selected
ENABLED_THRESHOLD = 128

# Known locations
# for screen captures
MAX_CAPACITY_POS = [670, 350, 130, 30]
NAVIGATION_ICON = [80, 240, 40, 40]
NAVIGATION_IMAGE = [80, 240, 200, 40]
GALMAP_IMAGE = [250, 875, 230, 50]
GALMAP_SEARCH = [695, 125, 230, 25]
TRITIUM_EXIT = [585, 930, 45, 45]
INVENTORY_POS = [1135, 265, 150, 30]
TRANSFER_POS = [1475, 320, 125, 35]
SET_CARRIER_DESTINATION_POS = [1420, 400, 330, 60]
GO_TO_LOCATION_POS = [1204, 124, 25, 25]
DONATE_TRITIUM_POS = [870, 860, 190, 35]
CONFIRM_DEPOSIT_POS = [850, 830, 225, 25]
CARRIER_MANAGEMENT_POS = [880, 805, 230, 30]
TRITIUM_DEPOT_POS = [250, 805, 160, 30]
TRANSFER_CANCEL_POS = [624, 771, 75, 18]

is_adjusted_for_fullscreen = False


def adjust_for_fullscreen():
    global is_adjusted_for_fullscreen
    if is_adjusted_for_fullscreen: return
    is_adjusted_for_fullscreen = True
    MAX_CAPACITY_POS[1] += FULLSCREEN_OFFSET
    NAVIGATION_ICON[1] += FULLSCREEN_OFFSET
    NAVIGATION_IMAGE[1] += FULLSCREEN_OFFSET
    GALMAP_IMAGE[1] += FULLSCREEN_OFFSET
    GALMAP_SEARCH[1] += FULLSCREEN_OFFSET
    TRITIUM_EXIT[1] += FULLSCREEN_OFFSET
    INVENTORY_POS[1] += FULLSCREEN_OFFSET
    TRANSFER_POS[1] += FULLSCREEN_OFFSET
    SET_CARRIER_DESTINATION_POS[1] += FULLSCREEN_OFFSET
    GO_TO_LOCATION_POS[1] += FULLSCREEN_OFFSET
    DONATE_TRITIUM_POS[1] += FULLSCREEN_OFFSET
    CONFIRM_DEPOSIT_POS[1] += FULLSCREEN_OFFSET
    CARRIER_MANAGEMENT_POS[1] += FULLSCREEN_OFFSET
    TRITIUM_DEPOT_POS[1] += FULLSCREEN_OFFSET
    TRANSFER_CANCEL_POS[1] += FULLSCREEN_OFFSET


carrier_services_locations = {
    'python':        (884, 840, 962-884+76, 12),
    'diamondbackxl': (882, 863, 961-882+80, 12),  # DBX
    'dolphin':       (885, 832, 964-885+78, 12),
    'asp':           (883, 865, 962-883+78, 11),
    'empire_trader': (881, 789, 958-881+78, 11),  # Imperial Clipper
    'orca':          (894, 848, 971-894+76, 11),
    'type9':         (878, 843, 961-878+82, 12),
    'belugaliner':   (890, 748, 961-890+71, 10),
    'anaconda':      (881, 852, 960-881+78, 13),
    'type9_military':(879, 843, 961-879+83, 12),  # Type10
    'cutter':        (870, 906, 961-870+91, 15),
    'federation_corvette': (882, 853, 961-882+80, 12),
    'empire_eagle':  (865, 835, 962-865+96, 14),
    'ferdelance':    (867, 815, 960-867+93, 14),
    'mamba':         (862, 874, 962-862+99, 16),
    'krait_mkii':    (883, 854, 961-883+79, 11),
    'federation_dropship_mkii': (882, 853, 962-882+79, 11),  # Federal assault ship
    'federation_dropship': (882, 853, 962-882+79, 11),  # Federal drop ship
    'cobramkiii':    (879, 869, 962-879+82, 12),
    'empire_courier':(882, 853, 159, 11),
    'diamondback':   (882, 863, 962-882+79, 12) # DBS
}

####### Notes from screencaps
# Python
# python
# 2022-03-15 20:09:54 - DEBUG - 'CARRIER' conf=96.440369 at 884,840 - 69,12
# 2022-03-15 20:09:54 - DEBUG - 'SERVICES' conf=96.094719 at 962,840 - 76,12
#
# DBX
# diamondbackxl
# 2022-03-15 20:13:21 - DEBUG - 'CARRIER' conf=96.430115 at 882,863 - 71,12
# 2022-03-15 20:13:21 - DEBUG - 'SERVICES' conf=96.853378 at 961,863 - 80,12
#
# Dolphin
# dolphin
# 2022-03-15 20:16:37 - DEBUG - 'CARRIER' conf=91.582306 at 885,832 - 71,12
# 2022-03-15 20:16:37 - DEBUG - 'SERVICES' conf=95.854897 at 964,832 - 78,12
#
# Asp Explorer
# asp
# 2022-03-15 20:17:53 - DEBUG - 'CARRIER' conf=95.824303 at 883,865 - 70,11
# 2022-03-15 20:17:53 - DEBUG - 'SERV' conf=96.637978 at 962,865 - 38,11
# 2022-03-15 20:18:22 - DEBUG - 'CARRIER' conf=96.353050 at 883,865 - 70,11
# 2022-03-15 20:18:22 - DEBUG - 'SERVICES' conf=96.363914 at 962,865 - 78,11
#
# Imperial Clipper
# empire_trader
# 2022-03-15 20:19:43 - DEBUG - 'CARRIER' conf=96.089005 at 881,789 - 69,11
# 2022-03-15 20:19:43 - DEBUG - 'SERVICES' conf=92.866127 at 958,789 - 78,11
#
# Orca
# orca
# 2022-03-15 20:20:48 - DEBUG - 'CARRIER' conf=82.640289 at 894,848 - 69,11
# 2022-03-15 20:20:48 - DEBUG - 'SERVICES' conf=84.101578 at 971,848 - 76,11
#
# Type-9
# type9
# 2022-03-15 20:22:04 - DEBUG - 'CARRIER' conf=81.305870 at 878,843 - 74,13
# 2022-03-15 20:22:04 - DEBUG - 'SERVICES' conf=95.352760 at 961,843 - 82,12
#
# Beluga
# belugaliner
# 2022-03-15 20:26:27 - DEBUG - 'CARRIER' conf=96.448929 at 890,748 - 64,10
# 2022-03-15 20:26:27 - DEBUG - 'SERVICES' conf=96.694786 at 961,748 - 71,10
#
# Anaconda
# anaconda
# 2022-03-15 20:27:39 - DEBUG - 'TARRIER' conf=71.630692 at 879,852 - 72,12
# 2022-03-15 20:27:39 - DEBUG - 'SERVICES' conf=96.245331 at 960,852 - 78,
# 2022-03-15 20:28:27 - DEBUG - 'CARRIER' conf=96.550133 at 881,852 - 70,13
# 2022-03-15 20:28:27 - DEBUG - 'SERVICES' conf=96.760590 at 960,852 - 78,13
#
# Type 10
# type9_military
# 2022-03-15 20:29:47 - DEBUG - 'CARRIER' conf=95.627495 at 879,843 - 74,12
# 2022-03-15 20:29:47 - DEBUG - 'SERVICES' conf=96.276894 at 961,843 - 83,12
#
# Imperial Cutter
# cutter
# 2022-03-15 20:30:58 - DEBUG - 'CARRIER' conf=84.562981 at 870,906 - 82,15
# 2022-03-15 20:30:58 - DEBUG - 'SERVICES' conf=95.720673 at 962,906 - 91,15
#
# Federal Corvette
# federation_corvette
# 2022-03-15 20:31:58 - DEBUG - 'CARRIER' conf=96.335411 at 882,853 - 71,12
# 2022-03-15 20:31:58 - DEBUG - 'SERVICES' conf=95.933846 at 961,853 - 80,12
#
# Imperial Eagle
# empire_eagle
# 2022-03-15 20:33:45 - DEBUG - 'CARRIER' conf=95.286850 at 865,835 - 86,14
# 2022-03-15 20:33:45 - DEBUG - 'SERVICES' conf=96.157745 at 962,835 - 96,14
#
# Fer De Lance
# ferdelance
# 2022-03-15 20:44:38 - DEBUG - 'CARRIER' conf=88.678116 at 867,815 - 84,14
# 2022-03-15 20:44:38 - DEBUG - 'SERVICES' conf=96.354332 at 960,815 - 93,14
#
# Mamba
# mamba
# 2022-03-15 20:38:32 - DEBUG - 'CARRIER' conf=96.125740 at 862,874 - 89,15
# 2022-03-15 20:38:32 - DEBUG - 'SERVICES' conf=96.317787 at 962,873 - 99,16
#
# Krait Mk II
# krait_mkii
# 2022-03-15 20:43:31 - DEBUG - 'CARRIER' conf=96.511787 at 883,854 - 70,11
# 2022-03-15 20:43:31 - DEBUG - 'SERVICES' conf=96.342117 at 961,854 - 79,11
#
# Federal Assault Ship
# federation_dropship_mkii
# 2022-03-15 20:37:15 - DEBUG - 'CARRIER' conf=96.134789 at 882,853 - 71,11
# 2022-03-15 20:37:15 - DEBUG - 'SERVICES' conf=95.974770 at 962,853 - 79,11
#
# Cobra Mk III
# cobramkiii
# 2022-03-15 20:36:14 - DEBUG - 'CARRIER' conf=95.945961 at 879,863 - 74,12
# 2022-03-15 20:36:14 - DEBUG - 'SERVICES' conf=96.082794 at 962,863 - 82,12
#
# Imperial Courier
# empire_courier
# 2022-03-15 20:35:19 - DEBUG - 'CARRIEFCSERVICES' conf=69.902817 at 882,853 - 159,11
#
# DBS
# diamondback
# 2022-03-15 20:34:29 - DEBUG - 'CARRIER' conf=96.507072 at 882,863 - 71,12
# 2022-03-15 20:34:29 - DEBUG - 'SERVICES' conf=96.700348 at 962,863 - 79,12


