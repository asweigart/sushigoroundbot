#! python3

import pyautogui, time, os, logging, sys, random, pprint, copy

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

pyautogui.pyscreeze.GRAYSCALE_DEFAULT = True

# order constants (don't change these: the image filenames depend on these specific values)
ONIGIRI = 'onigiri'
GUNKAN_MAKI = 'gunkan_maki'
CALIFORNIA_ROLL = 'california_roll'
SALMON_ROLL = 'salmon_roll'
ALL_ORDER_TYPES = (ONIGIRI, GUNKAN_MAKI, CALIFORNIA_ROLL, SALMON_ROLL)

# ingredient constants (don't change these: the image filenames depend on these specific values)
SHRIMP = 'shrimp'
RICE = 'rice'
NORI = 'nori'
ROE = 'roe'
SALMON = 'salmon'
UNAGI = 'unagi'

MIN_INGREDIENTS = 4 # if an ingredient gets below this value, order more.
PLATE_CLEARING_FREQ = 8 # plates are cleared roughly ever this number of seconds at least

# inventory constant
INVENTORY = {SHRIMP: 5, RICE: 10,
             NORI: 10, ROE: 10,
             SALMON: 5, UNAGI: 5}
RECIPE = {ONIGIRI:         {RICE: 2, NORI: 1},
          CALIFORNIA_ROLL: {RICE: 1, NORI: 1, ROE: 1},
          GUNKAN_MAKI:     {RICE: 1, NORI: 1, ROE: 2},
          SALMON_ROLL:     {RICE: 1, NORI: 1, SALMON: 2},}

GAME_REGION = ()
ORDERING_COMPLETE = {SHRIMP: None, RICE: None, NORI: None, ROE: None, SALMON: None, UNAGI: None}
ROLLING_COMPLETE = 0 # the unix timestamp when the current order being made will be done and a new order can start
LAST_PLATE_CLEARING = 0 # the unix timestamp of the last time the plates were cleared
LAST_GAME_OVER_CHECK = 0 # the unix timestamp when we last checked for the Game Over or You Win messages

INGRED_COORDS = None
PHONE_COORDS = None
TOPPING_COORDS = None
ORDER_BUTTON_COORDS = None
RICE1_COORDS = None
RICE2_COORDS = None
NORMAL_DELIVERY_BUTTON_COORDS = None
MAT_COORDS = None


def main():
    logging.debug('Program Started. Press Ctrl-C to abort at any time.')
    logging.debug('To interrupt mouse movement, move mouse to upper left corner.')
    getGameRegion()
    navigateStartGameMenu()
    setupCoordinates()
    startServing()


def imPath(filename):
    return os.path.join('images', filename)


def setupCoordinates():
    global INGRED_COORDS, PHONE_COORDS, TOPPING_COORDS, ORDER_BUTTON_COORDS, RICE1_COORDS, RICE2_COORDS, NORMAL_DELIVERY_BUTTON_COORDS, MAT_COORDS
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


def getGameRegion():
    global GAME_REGION

    # identify the top-left corner
    logging.debug('Finding game region...')
    region = pyautogui.locateOnScreen(imPath('top_right_corner.png'))
    if region is None:
        raise Exception('Could not find game on screen. Is the game visible?')

    # calculate the region of the entire game
    topRightX = region[0] + region[2] # left + width
    topRightY = region[1] # top
    GAME_REGION = (topRightX - 640, topRightY, 640, 480) # the game screen is always 640 x 480
    logging.debug('Game region found: %s' % (GAME_REGION,))


def navigateStartGameMenu():
    # Click on everything needed to get past the menus at the start of the game.

    # click on Play
    logging.debug('Looking for Play button...')
    while True: # loop because it could be the blue or pink Play button displayed at the moment.
        pos = pyautogui.locateCenterOnScreen(imPath('play_button.png'), region=GAME_REGION)
        if pos is not None:
            break
    pyautogui.click(pos, duration=0.25)
    logging.debug('Clicked on Play button.')

    # click on Continue
    pos = pyautogui.locateCenterOnScreen(imPath('continue_button.png'), region=GAME_REGION)
    pyautogui.click(pos, duration=0.25)
    logging.debug('Clicked on Continue button.')

    # click on Skip
    logging.debug('Looking for Skip button...')
    while True: # loop because it could be the yellow or red Skip button displayed at the moment.
        pos = pyautogui.locateCenterOnScreen(imPath('skip_button.png'), region=GAME_REGION)
        if pos is not None:
            break
    pyautogui.click(pos, duration=0.25)
    logging.debug('Clicked on Skip button.')

    # click on Continue
    pos = pyautogui.locateCenterOnScreen(imPath('continue_button.png'), region=GAME_REGION)
    pyautogui.click(pos, duration=0.25)
    logging.debug('Clicked on Continue button.')


def startServing():
    global LAST_GAME_OVER_CHECK
    orders = {}
    backOrders = {}
    LAST_GAME_OVER_CHECK = time.time()

    while True:
        newestOrders = getOrders()
        added, removed = getOrdersDifference(newestOrders, orders)
        if added != {}:
            logging.debug('New orders: %s' % (added))
        if removed != {}:
            logging.debug('Removed orders: %s' % (removed))
        orders = newestOrders

        for pos, order in added.items():
            result = makeOrder(order)
            if result is not None:
                orderIngredient(result)
                backOrders[pos] = order

        if random.randint(1, 10) == 1 or time.time() - PLATE_CLEARING_FREQ > LAST_PLATE_CLEARING:
            clickOnPlates()
        updateInventory()

        # Go through and see if any back orders can be filled.
        backOrdersCopy = copy.copy(backOrders)
        for pos, order in backOrdersCopy.items():
            result = makeOrder(order)
            if result is None:
                del backOrders[pos] # remove from back orders
                logging.debug('Filled back order for %s.' % (order))

        if random.randint(1, 10) == 1:
            checkForGameOver()
        if random.randint(1, 5) == 1:
            orderIngredientsIfNeeded()

        if time.time() - 12 > LAST_GAME_OVER_CHECK:
            checkForGameOver()


def checkForGameOver():
    pass # TODO

def clickOnPlates():
    global LAST_PLATE_CLEARING
    # just blindly click on all the places where a plate should be
    for i in range(6):
        pyautogui.click(83 + GAME_REGION[0] + (i * 101), GAME_REGION[1] + 203)
    LAST_PLATE_CLEARING = time.time()


def getOrders():
    orders = {}
    #startTime = time.time()
    for orderType in (ALL_ORDER_TYPES):
        allOrders = pyautogui.locateAllOnScreen(imPath('%s_order.png' % orderType), region=(GAME_REGION[0] + 32, GAME_REGION[1] + 46, 558, 44))
        for order in allOrders:
            orders[order] = orderType # keys are regions, values are order type
    #logging.debug('Scanning for orders took %s secs.' % (round(time.time() - startTime, 2)))
    return orders


def getOrdersDifference(newOrders, oldOrders):
    added = {}
    removed = {}
    for k in newOrders:
        if k not in oldOrders:
            added[k] = newOrders[k]
    for k in oldOrders:
        if k not in newOrders:
            removed[k] = oldOrders[k]

    return added, removed


def makeOrder(orderType):
    global ROLLING_COMPLETE, INGRED_COORDS, INVENTORY

    while time.time() < ROLLING_COMPLETE:
        time.sleep(0.1)

    for ingredient, amount in RECIPE[orderType].items():
        if INVENTORY[ingredient] < amount:
            logging.debug('More %s is needed to make %s.' % (ingredient, orderType))
            return ingredient

    for ingredient, amount in RECIPE[orderType].items():
        for i in range(amount):
            pyautogui.click(INGRED_COORDS[ingredient], duration=0.25)
            INVENTORY[ingredient] -= 1
    pyautogui.click(MAT_COORDS, duration=0.25)
    logging.debug('Made a %s order.' % (orderType))
    ROLLING_COMPLETE = time.time() + 1.5


def orderIngredientsIfNeeded():
    for ingredient, amount in INVENTORY.items():
        if amount < MIN_INGREDIENTS:
            orderIngredient(ingredient)


def orderIngredient(ingredient):
    logging.debug('Ordering more %s (inventory says %s left)...' % (ingredient, INVENTORY[ingredient]))
    pyautogui.click(PHONE_COORDS, duration=0.25)

    if ingredient == RICE and ORDERING_COMPLETE[RICE] is None:
        pyautogui.click(RICE1_COORDS, duration=0.25)

        # Check if we can't afford the rice
        if pyautogui.locateOnScreen(imPath('cant_afford_rice.png'), region=(GAME_REGION[0] + 498, GAME_REGION[1] + 242, 90, 75)):
            logging.debug("Can't afford rice. Canceling.")
            pyautogui.click(GAME_REGION[0] + 585, GAME_REGION[1] + 335, duration=0.25) # click cancel phone button
            return

        pyautogui.click(RICE2_COORDS, duration=0.25)
        pyautogui.click(NORMAL_DELIVERY_BUTTON_COORDS, duration=0.25)
        ORDERING_COMPLETE[RICE] = time.time() + 6
        logging.debug('Ordered more %s' % (RICE))
        return
    elif ORDERING_COMPLETE[ingredient] is None:
        pyautogui.click(TOPPING_COORDS, duration=0.25)

        # Check if we can't afford the ingredient
        if pyautogui.locateOnScreen(imPath('cant_afford_%s.png' % (ingredient)), region=(GAME_REGION[0] + 446, GAME_REGION[1] + 187, 180, 180)):
            logging.debug("Can't afford %s. Canceling." % (ingredient))
            pyautogui.click(GAME_REGION[0] + 597, GAME_REGION[1] + 337, duration=0.25) # click cancel phone button
            return

        pyautogui.click(ORDER_BUTTON_COORDS[ingredient], duration=0.25)
        pyautogui.click(NORMAL_DELIVERY_BUTTON_COORDS, duration=0.25)
        ORDERING_COMPLETE[ingredient] = time.time() + 6
        logging.debug('Ordered more %s' % (ingredient))
        return

    pyautogui.click(GAME_REGION[0] + 589, GAME_REGION[1] + 341) # click cancel phone button
    logging.debug('Already ordered %s.' % (ingredient))


def updateInventory():
    for ingredient in INVENTORY:
        if ORDERING_COMPLETE[ingredient] is not None and time.time() > ORDERING_COMPLETE[ingredient]:
            ORDERING_COMPLETE[ingredient] = None
            if ingredient in (SHRIMP, UNAGI, SALMON):
                INVENTORY[ingredient] += 5
            elif ingredient in (NORI, ROE, RICE):
                INVENTORY[ingredient] += 10
            logging.debug('Updated inventory with added %s.' % (ingredient))
            pyautogui.screenshot('%s_%sshrimp_%srice_%snori_%sroe_%ssalmon_%sunagi.png' % (int(time.time()), INVENTORY[SHRIMP], INVENTORY[RICE], INVENTORY[NORI], INVENTORY[ROE], INVENTORY[SALMON], INVENTORY[UNAGI]), region=(GAME_REGION[0] + 11, GAME_REGION[1] + 304, 110, 170))
            logging.debug('Assumed inventory: %s' % (pprint.pprint(INVENTORY)))


def checkForGameOver():
    if pyautogui.locateOnScreen(imPath('failed_screen.png'), region=GAME_REGION) is not None:
        logging.debug('Game over detected. Quitting.')
        sys.exit()


if __name__ == '__main__':
    main()