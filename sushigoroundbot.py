#! python3

import pyautogui, time, os, logging

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

# inventory constant
INVENTORY = {SHRIMP: 5, RICE: 10,
             NORI: 10, ROE: 10,
             SALMON: 5, UNAGI: 5}
RECIPE = {ONIGIRI:         {RICE: 2, NORI: 1},
          GUNKAN_MAKI:     {RICE: 1, NORI: 1, ROE: 1},
          CALIFORNIA_ROLL: {RICE: 1, NORI: 1, ROE: 2},}

def main():
    global INGRED_COORDS, PHONE_COORDS, TOPPING_COORDS, ORDER_BUTTON_COORDS, RICE1_COORDS, RICE2_COORDS, ROLLER_COORDS
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
    RICE2_COORDS = (GAME_REGION[0] + 582, GAME_REGION[1] + 505)

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
    while True:
        newestOrders = getOrders()
        added, removed = getOrdersDifference(newestOrders, orders)
        if added != {}:
            logging.debug('New orders: %s' % (added))
        if removed != {}:
            logging.debug('Removed orders: %s' % (removed))
        orders = newestOrders

        for order in added.values():
            result = makeOrder(order)

        clickOnPlates()



def clickOnPlates():
    # just blindly click on all the places where a plate should be
    for i in range(6):
        pyautogui.click(83 + GAME_REGION[0] + (i * 112), 204) # TODO - buggy, not right coords


def getOrders():
    orders = {}
    for orderType in (ALL_ORDER_TYPES):
        allOrders = pyautogui.locateAllOnScreen(imPath('%s_order.png' % orderType), region=(GAME_REGION[0] + 19, GAME_REGION[1] + 35, 578, 60))
        for order in allOrders:
            orders[order] = orderType # keys are regions, values are order type
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
    for ingredient, amount in RECIPE[orderType].items():
        if INVENTORY[ingredient] < amount:
            return ingredient

    for ingredient, amount in RECIPE[orderType].items():
        for i in range(amount):
            pyautogui.click(INGRED_COORDS[ingredient])
    pyautogui.click(ROLLER_COORDS)
    logging.debug('Made a %s order.' % (orderType))


def orderIngredients():
    pass


if __name__ == '__main__':
    main()