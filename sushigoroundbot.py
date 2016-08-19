#!/usr/bin/env python3
"""Sushi Go Round Bot
Al Sweigart al@inventwithpython.com @AlSweigart

A bot program to automatically play the Sushi Go Round flash game
at http://miniclip.com/games/sushi-go-round/en/
"""

import pyautogui
import time
import os
import logging
import sys
import random
import copy
import pyautogui.screenshotUtil
import PIL

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S')
# logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S')
# logging.disable(logging.DEBUG) # uncomment to block debug log messages

logging.getLogger('PIL').setLevel(logging.WARNING)

# Food order constants (don't change these: the image filenames depend on these specific values)
ONIGIRI = 'onigiri'
GUNKAN_MAKI = 'gunkan_maki'
CALIFORNIA_ROLL = 'california_roll'
SALMON_ROLL = 'salmon_roll'
SHRIMP_SUSHI = 'shrimp_sushi'
UNAGI_ROLL = 'unagi_roll'
DRAGON_ROLL = 'dragon_roll'
COMBO = 'combo'
ALL_ORDER_TYPES = [ONIGIRI, GUNKAN_MAKI, CALIFORNIA_ROLL]  # LEVEL1
ALL_ORDER_TYPES += [SALMON_ROLL]  # LEVEL2
ALL_ORDER_TYPES += [SHRIMP_SUSHI]  # LEVEL3
ALL_ORDER_TYPES += [UNAGI_ROLL]  # LEVEL4
ALL_ORDER_TYPES += [DRAGON_ROLL]  # LEVEL5
ALL_ORDER_TYPES += [COMBO]  # LEVEL6

# Ingredient constants (don't change these: the image filenames depend on these specific values)
SHRIMP = 'shrimp'
RICE = 'rice'
NORI = 'nori'
ROE = 'roe'
SALMON = 'salmon'
UNAGI = 'unagi'
RECIPE = {ONIGIRI:         {RICE: 2, NORI: 1},
          CALIFORNIA_ROLL: {RICE: 1, NORI: 1, ROE: 1},
          GUNKAN_MAKI:     {RICE: 1, NORI: 1, ROE: 2},
          SALMON_ROLL:     {RICE: 1, NORI: 1, SALMON: 2},
          SHRIMP_SUSHI:    {RICE: 1, NORI: 1, SHRIMP: 2},
          UNAGI_ROLL:      {RICE: 1, NORI: 1, UNAGI: 2},
          DRAGON_ROLL:     {RICE: 2, NORI: 1, ROE: 1, UNAGI: 2},
          COMBO:           {RICE: 2, NORI: 1, ROE: 1, SALMON: 1, UNAGI: 1,
                            SHRIMP: 1}, }

LEVEL_WIN_MESSAGE = 'win'  # checkForGameOver() returns this value if the level has been won

# Settings
MIN_INGREDIENTS = 4  # if an ingredient gets below this value, order more
PLATE_CLEARING_FREQ = 8  # plates are cleared every this number of seconds, roughly
NORMAL_RESTOCK_TIME = 7  # the number of seconds it takes to restock inventory
                         # after ordering it (at normal speed, not express)
TIME_TO_REMAKE = 30  # if an order goes unfilled for this number of seconds, remake it

# Global variables
LEVEL = 1  # current level being played
INVENTORY = {SHRIMP: 5, RICE: 10,
             NORI: 10,  ROE: 10,
             SALMON: 5, UNAGI: 5}
ORDERING_COMPLETE = {SHRIMP: None, RICE: None, NORI: None, ROE: None, SALMON:
                     None, UNAGI: None}  # unix timestamp when an ordered ingredient will have arrived
ROLLING_COMPLETE = 0  # unix timestamp of when the rolling of the mat will have completed
LAST_PLATE_CLEARING = 0  # unix timestamp of the last time the plates were cleared
LAST_GAME_OVER_CHECK = 0  # unix timestamp when we last checked for the Game Over or You Win messages

# various coordinates of objects in the game
GAME_REGION = ()  # (left, top, width, height) values coordinates of the entire game window
INGRED_COORDS = None
PHONE_COORDS = None
TOPPING_COORDS = None
ORDER_BUTTON_COORDS = None
RICE1_COORDS = None
RICE2_COORDS = None
NORMAL_DELIVERY_BUTTON_COORDS = None
MAT_COORDS = None


def main():
    """Runs the entire program. The Sushi Go Round game must be visible on the screen and the PLAY button visible."""
    logging.info('Program Started. Press Ctrl-C to abort at any time.')
    logging.info('To interrupt mouse movement, move mouse to upper left corner.')
    getGameRegion()
    navigateStartGameMenu()
    setupCoordinates()
    startServing()


def imPath(filename):
    """A shortcut for joining the 'images/'' file path, since it is used so often. Returns the filename with 'images/' prepended."""
    return os.path.join('images', filename)


def getGameRegion():
    """Obtains the region that the Sushi Go Round game is on the screen and assigns it to GAME_REGION. The game must be at the start screen (where the PLAY button is visible)."""
    global GAME_REGION

    # identify the top-left corner
    logging.info('Finding game region...')
    region = pyautogui.screenshotUtil.locateOnScreen(imPath('top_right_corner.png'), grayscale=True)
    if region is None:
        raise Exception('Could not find game on screen. Is the game visible?')

    # calculate the region of the entire game
    topRightX = region[0] + region[2] # left + width
    topRightY = region[1] # top
    GAME_REGION = (topRightX - 640, topRightY, 640, 480) # the game screen is always 640 x 480
    logging.info('Game region found: %s' % (GAME_REGION,))


def setupCoordinates():
    """Sets several of the coordinate-related global variables, after acquiring the value for GAME_REGION."""
    global INGRED_COORDS, PHONE_COORDS, TOPPING_COORDS, ORDER_BUTTON_COORDS, RICE1_COORDS, RICE2_COORDS, NORMAL_DELIVERY_BUTTON_COORDS, MAT_COORDS, LEVEL
    INGRED_COORDS = {SHRIMP: (GAME_REGION[0] + 40, GAME_REGION[1] + 335),
                     RICE:   (GAME_REGION[0] + 95, GAME_REGION[1] + 335),
                     NORI:   (GAME_REGION[0] + 40, GAME_REGION[1] + 385),
                     ROE:    (GAME_REGION[0] + 95, GAME_REGION[1] + 385),
                     SALMON: (GAME_REGION[0] + 40, GAME_REGION[1] + 425),
                     UNAGI:  (GAME_REGION[0] + 95, GAME_REGION[1] + 425),}
    PHONE_COORDS = (GAME_REGION[0] + 560, GAME_REGION[1] + 360)
    TOPPING_COORDS = (GAME_REGION[0] + 513, GAME_REGION[1] + 269)
    ORDER_BUTTON_COORDS = {SHRIMP: (GAME_REGION[0] + 496, GAME_REGION[1] + 222),
                           UNAGI:  (GAME_REGION[0] + 578, GAME_REGION[1] + 222),
                           NORI:   (GAME_REGION[0] + 496, GAME_REGION[1] + 281),
                           ROE:    (GAME_REGION[0] + 578, GAME_REGION[1] + 281),
                           SALMON: (GAME_REGION[0] + 496, GAME_REGION[1] + 329),}
    RICE1_COORDS = (GAME_REGION[0] + 543, GAME_REGION[1] + 294)
    RICE2_COORDS = (GAME_REGION[0] + 545, GAME_REGION[1] + 269)

    NORMAL_DELIVERY_BUTTON_COORDS = (GAME_REGION[0] + 495, GAME_REGION[1] + 293)

    MAT_COORDS = (GAME_REGION[0] + 190, GAME_REGION[1] + 375)



def navigateStartGameMenu():
    """Performs the clicks to navigate form the start screen (where the PLAY button is visible) to the beginning of the first level."""
    # Click on everything needed to get past the menus at the start of the game.

    # click on Play
    logging.info('Looking for Play button...')
    while True:  # loop because it could be the blue or pink Play button displayed at the moment.
        pos = None
        try:
            pos = pyautogui.screenshotUtil.locateCenterOnScreen(imPath('play_button.png'), region=GAME_REGION, grayscale=True)
        except:
            pass
        if pos is not None:
            break
    pyautogui.click((pos[0]+GAME_REGION[0],pos[1]+GAME_REGION[1]), duration=0.25)
    logging.debug('Clicked on Play button. (pos: %s,%s)' % pos)

    # click on Continue
    logging.debug('Game Region: %s' % repr(GAME_REGION))
    time.sleep(2)
    pos = pyautogui.screenshotUtil.locateCenterOnScreen(imPath('continue_button.png'), region=GAME_REGION, grayscale=True)
    pyautogui.click((pos[0] + GAME_REGION[0], pos[1] + GAME_REGION[1]), duration=0.25)
    logging.debug('Clicked on Continue button (pos: %s)' %repr(pos))

    # click on Skip
    logging.debug('Looking for Skip button...')
    while True:  # loop because it could be the yellow or red Skip button displayed at the moment.
        pos = None
        try:
            pos = pyautogui.screenshotUtil.locateCenterOnScreen(imPath('skip_button.png'), region=GAME_REGION, grayscale=True)
        except:
            pass
        if pos is not None:
            break
    pyautogui.click((pos[0] + GAME_REGION[0], pos[1] + GAME_REGION[1]), duration=0.25)
    logging.debug('Clicked on Skip button (pos: %s)' %repr(pos))

    # click on Continue
    pos = pyautogui.screenshotUtil.locateCenterOnScreen(imPath('continue_button.png'), region=GAME_REGION, grayscale=True)
    pyautogui.click((pos[0] + GAME_REGION[0], pos[1] + GAME_REGION[1]), duration=0.25)
    logging.debug('Clicked on Continue button (pos: %s)' %repr(pos))


def startServing():
    """The main game playing function. This function handles all aspects of game play, including identifying orders, making orders, buying ingredients and other features."""
    global LAST_GAME_OVER_CHECK, INVENTORY, ORDERING_COMPLETE, LEVEL
    logging.info("Serving started")

    # Reset all game state variables.
    oldOrders = {}
    backOrders = {}
    remakeOrders = {}
    remakeTimes = {}
    LAST_GAME_OVER_CHECK = time.time()
    ORDERING_COMPLETE = {SHRIMP: None, RICE: None, NORI: None,
                         ROE: None, SALMON: None, UNAGI: None}

    while True:
        # Check for orders, see which are new and which are gone since last time.
        currentOrders = getOrders()
        logging.debug("in startServing() - currentOrders: %s" % currentOrders)
        added, removed = getOrdersDifference(currentOrders, oldOrders)
        if added != {}:
            logging.info('New orders: %s' % (list(added.values())))
            for k in added:
                remakeTimes[k] = time.time() + TIME_TO_REMAKE
        if removed != {}:
            logging.info('Removed orders: %s' % (list(removed.values())))
            for k in removed:
                del remakeTimes[k]

        # Check if the remake times have past, and add those to the remakeOrders dictionary.
        for k, remakeTime in copy.copy(remakeTimes).items():
            if time.time() > remakeTime:
                remakeTimes[k] = time.time() + TIME_TO_REMAKE # reset remake time
                remakeOrders[k] = currentOrders[k]
                logging.info('%s added to remake orders.' % (currentOrders[k]))

        # Attempt to make the order.
        for pos, order in added.items():
            result = makeOrder(order)
            if result is not None:
                orderIngredient(result)
                backOrders[pos] = order
                logging.info('Ingredients for %s not available. Putting on back order.' % (order))

        # Clear any finished plates.
        if random.randint(1, 10) == 1 or time.time() - PLATE_CLEARING_FREQ > LAST_PLATE_CLEARING:
            clickOnPlates()

        # Check if ingredient orders have arrived.
        updateInventory()

        # Go through and see if any back orders can be filled.
        for pos, order in copy.copy(backOrders).items():
            result = makeOrder(order)
            if result is None:
                del backOrders[pos] # remove from back orders
                logging.info('Filled back order for %s.' % (order))

        # Go through and see if any remake orders can be filled.
        for pos, order in copy.copy(remakeOrders).items():
            if pos not in currentOrders:
                del remakeOrders[pos]
                logging.info('Canceled remake order for %s.' % (order))
                continue
            result = makeOrder(order)
            if result is None:
                del remakeOrders[pos] # remove from remake orders
                logging.info('Filled remake order for %s.' % (order))

        if random.randint(1, 5) == 1:
            # order any ingredients that are below the minimum amount
            for ingredient, amount in INVENTORY.items():
                if amount < MIN_INGREDIENTS:
                    orderIngredient(ingredient)

        # check for the "You Win" or "You Fail" messages
        if time.time() - 12 > LAST_GAME_OVER_CHECK:
            result = checkForGameOver()
            if result == LEVEL_WIN_MESSAGE:
                # player has completed the level

                # Reset inventory and orders.
                INVENTORY = {SHRIMP: 5, RICE: 10,
                             NORI: 10, ROE: 10,
                             SALMON: 5, UNAGI: 5}
                ORDERING_COMPLETE = {SHRIMP: None, RICE: None,
                                     NORI: None, ROE: None,
                                     SALMON: None, UNAGI: None}
                backOrders = {}
                remakeOrders = {}
                currentOrders = {}
                oldOrders = {}


                logging.info('Level %s complete.' % (LEVEL))
                LEVEL += 1
                time.sleep(7) # give another 7 seconds to tally score

                # Click buttons to continue to next level.
                pos = pyautogui.screenshotUtil.locateCenterOnScreen(imPath('continue_button.png'),region=GAME_REGION,grayscale=True)
                pyautogui.click((pos[0] + GAME_REGION[0], pos[1] + GAME_REGION[1]), duration=0.25)
                logging.debug('Clicked on Continue button (pos: %s)' %repr(pos))
                time.sleep(2)
                if LEVEL <= 7:  # click the second continue if the game isn't finished.
                    pyautogui.click((pos[0] + GAME_REGION[0], pos[1] + GAME_REGION[1]), duration=0.25)
                    logging.debug('Clicked on Continue button (pos: %s)' %repr(pos))

        oldOrders = currentOrders


def clickOnPlates():
    """Clicks the mouse on the six places where finished plates will be flashing. This function does not check for flashing plates, but simply clicks on all six places.

    Sets LAST_PLATE_CLEARING to the current time."""
    global LAST_PLATE_CLEARING

    # just blindly click on all the places where a plate should be
    for i in range(6):
        pyautogui.click(83 + GAME_REGION[0] + (i * 101), GAME_REGION[1] + 203)
    LAST_PLATE_CLEARING = time.time()


def getOrders():
    """Scans the screen for orders being made. Returns a dictionary with a (left, top, width, height) tuple of integers for keys and the order constant for a value.

    The order constants are ONIGIRI, GUNKAN_MAKI, CALIFORNIA_ROLL, SALMON_ROLL, SHRIMP_SUSHI, UNAGI_ROLL, DRAGON_ROLL, COMBO."""
    orders = {}
    # GAME_REGION = () # (left, top, width, height) values coordinates of the entire game window
    ##pyautogui.screenshotUtil.screenshot().crop((GAME_REGION[0],GAME_REGION[1],GAME_REGION[0]+640,GAME_REGION[1]+480)).save('/tmp/sss.png')
    #pyautogui.screenshotUtil.screenshot('/tmp/sss.png',region =[GAME_REGION[0],GAME_REGION[1],GAME_REGION[0]+640,GAME_REGION[1]+480])
    pyautogui.screenshotUtil.screenshot('/tmp/sss.png',
                                                           region=(GAME_REGION[0] + 32, GAME_REGION[1] + 46, 558, 44))
    for orderType in (ALL_ORDER_TYPES[:2+LEVEL]):
        logging.debug("checking if this is %s" % orderType)
        allOrders = pyautogui.screenshotUtil.locateAll(imPath('%s_order.png' % orderType),'/tmp/sss.png',grayscale=True) # , region=(GAME_REGION[0] + 32, GAME_REGION[1] + 46, 558, 44))
        #allOrders = pyautogui.screenshotUtil.locateAllOnScreen(imPath('%s_order.png' % orderType), grayscale=True,region=(GAME_REGION[0] + 32, GAME_REGION[1] + 46, 558, 44))

        for order in allOrders:
            #logging.debug("processing order: %s" % order)
            orders[order] = orderType
    return orders


def getOrdersDifference(newOrders, oldOrders):
    """Finds the differences between the orders dictionaries passed. Return value is a tuple of two dictionaries.

    The first dictionary is the "added" dictionary of orders added to newOrders since oldOrders. The second dictionary is the "removed" dictionary of orders in oldOrders but removed in newOrders.

    Each dictionary has (left, top, width, height) for keys and an order constant for a value."""
    added = {}
    removed = {}

    # find all orders in newOrders that are new and not found in oldOrders
    for k in newOrders:
        if k not in oldOrders:
            added[k] = newOrders[k]
    # find all orders in oldOrders that were removed and not found in newOrders
    for k in oldOrders:
        if k not in newOrders:
            removed[k] = oldOrders[k]

    return added, removed


def makeOrder(orderType):
    """Does the mouse clicks needed to create an order.

    The orderType parameter has the value of one of the ONIGIRI, GUNKAN_MAKI, CALIFORNIA_ROLL, SALMON_ROLL, SHRIMP_SUSHI, UNAGI_ROLL, DRAGON_ROLL, COMBO constants.

    The INVENTORY global variable is updated in this function for orders made.

    The return value is None for a successfully made order, or the string of an ingredient constant if that needed ingredient is missing."""
    global ROLLING_COMPLETE, INGRED_COORDS, INVENTORY

    # wait until the mat is clear. The previous order could still be there if the conveyor belt has been full or the mat is currently rolling.
    while time.time() < ROLLING_COMPLETE and pyautogui.screenshotUtil.locateOnScreen(imPath('clear_mat.png'),region=(GAME_REGION[0] + 115, GAME_REGION[1] + 295, 220, 175)) is None:
        time.sleep(0.1)
        time.sleep(0.1)

    # check that all ingredients are available in the inventory.
    for ingredient, amount in RECIPE[orderType].items():
        if INVENTORY[ingredient] < amount:
            logging.info('More %s is needed to make %s.' % (ingredient, orderType))
            return ingredient

    # click on each of the ingredients
    for ingredient, amount in RECIPE[orderType].items():
        for i in range(amount):
            #pyautogui.click(INGRED_COORDS[ingredient], duration=0.25)
            pyautogui.click(INGRED_COORDS[ingredient], duration=0.35)
            logging.info("Clicked ingredient %s" % ingredient)
            INVENTORY[ingredient] -= 1
    #findAndClickPlatesOnBelt() # get rid of any left over meals on the conveyor belt, which may stall this meal from being loaded on the belt
    time.sleep(1)
    pyautogui.click(MAT_COORDS, duration=0.25) # click the rolling mat to make the order
    logging.info('Made a %s order.' % (orderType))
    ROLLING_COMPLETE = time.time() + 1.5 # give the mat enough time (1.5 seconds) to finish rolling before being used again


def findAndClickPlatesOnBelt():
    """Find any plates on the conveyor belt that can be removed and click on them to remove them. This will get rid of excess orders."""
    for color in ('pink', 'blue', 'red'):
        result = pyautogui.screenshotUtil.locateCenterOnScreen(imPath('%s_plate_color.png' % (color)),region=(GAME_REGION[0] + 343, GAME_REGION[1] + 300, 50, 100))
        if result is not None:
            pyautogui.click(result)
            logging.info('Clicked on %s plate on belt at X: %s Y: %s' % (color, result[0], result[1]))


def orderIngredient(ingredient):
    """Do the clicks to purchase an ingredient. If successful, the ORDERING_COMPLETE dictionary is updated for when the ingredients will arive and INVENTORY can be updated. (This is handled in the updateInventory() function.)"""
    logging.info('Ordering more %s (inventory says %s left)...' % (ingredient, INVENTORY[ingredient]))
    pyautogui.click(PHONE_COORDS, duration=0.25)

    if ingredient == RICE and ORDERING_COMPLETE[RICE] is None:
        # Order rice.
        pyautogui.click(RICE1_COORDS, duration=0.25)

        # Check if we can't afford the rice
        if pyautogui.screenshotUtil.locateOnScreen(imPath('cant_afford_rice.png'), region=(GAME_REGION[0] + 498, GAME_REGION[1] + 242, 90, 75)):
            logging.info("Can't afford rice. Canceling.")
            pyautogui.click(GAME_REGION[0] + 585, GAME_REGION[1] + 335, duration=0.25) # click cancel phone button
            return

        # Purchase the rice
        pyautogui.click(RICE2_COORDS, duration=0.25)
        pyautogui.click(NORMAL_DELIVERY_BUTTON_COORDS, duration=0.25)
        ORDERING_COMPLETE[RICE] = time.time() + NORMAL_RESTOCK_TIME
        logging.info('Ordered more %s' % (RICE))
        return

    elif ORDERING_COMPLETE[ingredient] is None:
        # Order non-rice ingredient.
        pyautogui.click(TOPPING_COORDS, duration=0.25)

        # Check if we can't afford the ingredient
        if pyautogui.screenshotUtil.locateOnScreen(imPath('cant_afford_%s.png' % (ingredient)), region=(GAME_REGION[0] + 446, GAME_REGION[1] + 187, 180, 180)):
            logging.info("Can't afford %s. Canceling." % (ingredient))
            pyautogui.click(GAME_REGION[0] + 597, GAME_REGION[1] + 337, duration=0.25) # click cancel phone button
            return

        # Order the ingredient
        pyautogui.click(ORDER_BUTTON_COORDS[ingredient], duration=0.25)
        pyautogui.click(NORMAL_DELIVERY_BUTTON_COORDS, duration=0.25)
        ORDERING_COMPLETE[ingredient] = time.time() + NORMAL_RESTOCK_TIME
        logging.info('Ordered more %s' % (ingredient))
        return

    # The ingredient has already been ordered, so close the phone menu.
    pyautogui.click(GAME_REGION[0] + 589, GAME_REGION[1] + 341) # click cancel phone button
    logging.info('Already ordered %s.' % (ingredient))


def updateInventory():
    """Check if any ordered ingredients have arrived by looking at the timestamps in ORDERING_COMPLETE.
    Update INVENTORY global variable with the new quantities."""
    for ingredient in INVENTORY:
        if ORDERING_COMPLETE[ingredient] is not None and time.time() > ORDERING_COMPLETE[ingredient]:
            ORDERING_COMPLETE[ingredient] = None
            if ingredient in (SHRIMP, UNAGI, SALMON):
                INVENTORY[ingredient] += 5
            elif ingredient in (NORI, ROE, RICE):
                INVENTORY[ingredient] += 10
            logging.info('Updated inventory with added %s:' % (ingredient))
            #logging.info(INVENTORY)


def checkForGameOver():
    """Checks the screen for the "You Win" or "You Fail" message.

    On winning, returns the string in LEVEL_WIN_MESSAGE.

    On losing, the program terminates."""

    # check for "You Win" message
    result = pyautogui.screenshotUtil.locateOnScreen(imPath('you_win.png'),region=(GAME_REGION[0] + 188, GAME_REGION[1] + 94, 262, 60),grayscale=True)
    if result is not None:
        #pyautogui.click((GAME_REGION[0] + 1
        return LEVEL_WIN_MESSAGE

    # check for "You Fail" message
    result = pyautogui.screenshotUtil.locateOnScreen(imPath('you_failed.png'), region=(GAME_REGION[0] + 167, GAME_REGION[1] + 133, 314, 39))
    if result is not None:
        logging.debug('Game over. Quitting.')
        sys.exit()


if __name__ == '__main__':
    main()
