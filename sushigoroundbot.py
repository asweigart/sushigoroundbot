#! python3

import pyautogui, time, os, logging, sys, random

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

pyautogui.pyscreeze.GRAYSCALE_DEFAULT = True

# order constants
ONIGIRI = 'onigiri'
GUNKAN_MAKI = 'gunkan_maki'
CALIFORNIA_ROLL = 'california_roll'
ALL_ORDER_TYPES = (ONIGIRI, GUNKAN_MAKI, CALIFORNIA_ROLL)

# ingredient constants
SHRIMP = 'shrimp'
RICE = 'rice'
NORI = 'nori'
ROE = 'roe'
SALMON = 'salmon'
UNAGI = 'unagi'

MIN_INGREDIENTS = 4 # if an ingredient gets below this value, order more.

# inventory constant
INVENTORY = {SHRIMP: 5, RICE: 10,
             NORI: 10, ROE: 10,
             SALMON: 5, UNAGI: 5}
RECIPE = {ONIGIRI:         {RICE: 2, NORI: 1},
          CALIFORNIA_ROLL: {RICE: 1, NORI: 1, ROE: 1},
          GUNKAN_MAKI:     {RICE: 1, NORI: 1, ROE: 2},}

GAME_REGION = ()
ORDERING_COMPLETE = {SHRIMP: None, RICE: None, NORI: None, ROE: None, SALMON: None, UNAGI: None}
ROLLING_COMPLETE = 0 # the unix time stamp when the current order being made will be done and a new order can start


def main():
    global INGRED_COORDS, PHONE_COORDS, TOPPING_COORDS, ORDER_BUTTON_COORDS, RICE1_COORDS, RICE2_COORDS, ROLLER_COORDS, NORMAL_DELIVERY_BUTTON_COORDS
    logging.debug('Program Started. Press Ctrl-C to abort at any time.')
    startGame()

    INGRED_COORDS = {SHRIMP: (GAME_REGION[0] + 40, GAME_REGION[1] + 335),
                     RICE:   (GAME_REGION[0] + 95, GAME_REGION[1] + 335),
                     NORI:   (GAME_REGION[0] + 40, GAME_REGION[1] + 385),
                     ROE:    (GAME_REGION[0] + 95, GAME_REGION[1] + 385),
                     SALMON: (GAME_REGION[0] + 40, GAME_REGION[1] + 425),
                     UNAGI:  (GAME_REGION[0] + 95, GAME_REGION[1] + 425),}
    PHONE_COORDS = (GAME_REGION[0] + 560, GAME_REGION[1] + 360)
    TOPPING_COORDS = (GAME_REGION[0] + 543, GAME_REGION[1] + 274)
    ORDER_BUTTON_COORDS = {SHRIMP: (GAME_REGION[0] + 496, GAME_REGION[1] + 222),
                           UNAGI:  (GAME_REGION[0] + 578, GAME_REGION[1] + 222),
                           NORI:   (GAME_REGION[0] + 496, GAME_REGION[1] + 281),
                           ROE:    (GAME_REGION[0] + 578, GAME_REGION[1] + 281),
                           SALMON: (GAME_REGION[0] + 496, GAME_REGION[1] + 329),}
    RICE1_COORDS = (GAME_REGION[0] + 543, GAME_REGION[1] + 294)
    RICE2_COORDS = (GAME_REGION[0] + 545, GAME_REGION[1] + 269)

    NORMAL_DELIVERY_BUTTON_COORDS = (GAME_REGION[0] + 495, GAME_REGION[1] + 293)

    ROLLER_COORDS = (GAME_REGION[0] + 190, GAME_REGION[1] + 375)
    startServing()


def imPath(filename):
    return os.path.join('images', filename)


def startGame():
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

    # Click on everything needed to get past the menus at the start of the game.

    # click on Play
    logging.debug('Looking for Play button...')
    while True: # loop because it could be the blue or pink Play button displayed at the moment.
        pos = pyautogui.locateCenterOnScreen(imPath('play_button.png'))
        if pos is not None:
            break
    pyautogui.click(pos)
    logging.debug('Clicked on Play button.')

    # click on Continue
    pos = pyautogui.locateCenterOnScreen(imPath('continue_button.png'))
    pyautogui.click(pos)
    logging.debug('Clicked on Continue button.')

    # click on Skip
    logging.debug('Looking for Skip button...')
    while True: # loop because it could be the yellow or red Skip button displayed at the moment.
        pos = pyautogui.locateCenterOnScreen(imPath('skip_button.png'))
        if pos is not None:
            break
    pyautogui.click(pos)
    logging.debug('Clicked on Skip button.')

    # click on Continue
    pos = pyautogui.locateCenterOnScreen(imPath('continue_button.png'))
    pyautogui.click(pos)
    logging.debug('Clicked on Continue button.')


def startServing():
    orders = {}
    backOrders = {}
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

        clickOnPlates()
        updateInventory()

        # Go through and see if any back orders can be filled.
        for pos, order in backOrders.items():
            result = makeOrder(order)
            if result is None:
                del backOrders[pos] # remove from back orders
                logging.debug('Filled back order for %s.' % (order))

        if random.randint(1, 10) == 1:
            checkForGameOver()
        if random.randint(1, 5) == 1:
            orderIngredientsIfNeeded()


def clickOnPlates():
    # just blindly click on all the places where a plate should be
    for i in range(6):
        pyautogui.click(83 + GAME_REGION[0] + (i * 101), GAME_REGION[1] + 203)


def getOrders():
    orders = {}
    startTime = time.time()
    for orderType in (ALL_ORDER_TYPES):
        allOrders = pyautogui.locateAllOnScreen(imPath('%s_order.png' % orderType), region=(GAME_REGION[0] + 19, GAME_REGION[1] + 35, 578, 60))
        for order in allOrders:
            orders[order] = orderType # keys are regions, values are order type
    logging.debug('Scanning for orders took %s secs.' % (round(time.time() - startTime, 2)))
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
    global ROLLING_COMPLETE

    while time.time() < ROLLING_COMPLETE:
        time.sleep(0.1)

    for ingredient, amount in RECIPE[orderType].items():
        if INVENTORY[ingredient] < amount:
            return ingredient

    for ingredient, amount in RECIPE[orderType].items():
        for i in range(amount):
            pyautogui.click(INGRED_COORDS[ingredient])
            INVENTORY[ingredient] -= 1
    pyautogui.click(ROLLER_COORDS)
    logging.debug('Made a %s order.' % (orderType))
    ROLLING_COMPLETE = time.time() + 1.5


def orderIngredientsIfNeeded():
    for ingredient, amount in INVENTORY.items():
        if amount < MIN_INGREDIENTS:
            orderIngredient(ingredient)


def orderIngredient(ingredient):
    pyautogui.click(PHONE_COORDS)

    if ingredient == RICE and ORDERING_COMPLETE[RICE] is None:
        pyautogui.click(RICE1_COORDS)
        time.sleep(0.25)
        pyautogui.click(RICE2_COORDS)
        time.sleep(0.25)
        pyautogui.click(NORMAL_DELIVERY_BUTTON_COORDS)
        ORDERING_COMPLETE[RICE] = time.time() + 6
        logging.debug('Ordered more %s' % (RICE))
    elif ORDERING_COMPLETE[ingredient] is None:
        pyautogui.click(TOPPING_COORDS)
        time.sleep(0.25)
        pyautogui.click(ORDER_BUTTON_COORDS[ingredient])
        time.sleep(0.25)
        pyautogui.click(NORMAL_DELIVERY_BUTTON_COORDS)
        ORDERING_COMPLETE[ingredient] = time.time() + 6
        logging.debug('Ordered more %s' % (ingredient))


def updateInventory():
    for ingredient in INVENTORY:
        if ORDERING_COMPLETE[ingredient] is not None and time.time() > ORDERING_COMPLETE[ingredient]:
            ORDERING_COMPLETE[ingredient] = None
            if ingredient in (SHRIMP, UNAGI, SALMON):
                INVENTORY[ingredient] += 5
            elif ingredient in (NORI, ROE):
                INVENTORY[ingredient] += 10
            logging.debug('Updated inventory with added %s.' % (ingredient))


def checkForGameOver():
    if pyautogui.locateOnScreen(imPath('failed_screen.png')) is not None:
        logging.debug('Game over detected. Quitting.')
        sys.exit()


if __name__ == '__main__':
    main()