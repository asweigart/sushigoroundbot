#! python3

import pyautogui, time, os, logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

pyautogui.pyscreeze.RAISE_IF_NOT_FOUND = True
pyautogui.pyscreeze.GRAYSCALE_DEFAULT = True


def main():
    logging.debug('Program Started. Press Ctrl-C to abort at any time.')
    startGame()
    startServing()

def startGame():
    global GAME_REGION

    # identify the top-left corner
    logging.debug('Finding game region...')
    region = pyautogui.locateOnScreen(os.path.join('images', 'top_right_corner.png'))
    if region is None:
        raise Exception('Could not find top right corner of the game. Is it visible on the screen?')

    # calculate the region of the entire game
    topRightX = region[0] + region[2] # left + width
    topRightY = region[1] # top
    GAME_REGION = (topRightX - 640, topRightY, 640, 480) # the game screen is always 640 x 480
    logging.debug('Game region found: %s' % (GAME_REGION,))

    # Click on everything needed to get past the menus at the start of the game.

    # click on Play
    logging.debug('Looking for Play button...')
    while True: # loop because it could be the blue or pink Play button displayed at the moment.
        try:
            pos = pyautogui.locateCenterOnScreen(os.path.join('images', 'play_button.png'))
            break
        except:
            pass
    pyautogui.click(pos)
    logging.debug('Clicked on Play button.')

    # click on Continue
    pos = pyautogui.locateCenterOnScreen(os.path.join('images', 'continue_button.png'))
    pyautogui.click(pos)
    logging.debug('Clicked on Continue button.')

    # click on Skip
    logging.debug('Looking for Skip button...')
    while True: # loop because it could be the yellow or red Skip button displayed at the moment.
        try:
            pos = pyautogui.locateCenterOnScreen(os.path.join('images', 'skip_button.png'))
            break
        except:
            pass
    pyautogui.click(pos)
    logging.debug('Clicked on Skip button.')

    # click on Continue
    pos = pyautogui.locateCenterOnScreen(os.path.join('images', 'continue_button.png'))
    pyautogui.click(pos)
    logging.debug('Clicked on Continue button.')


def startServing():
    pass


if __name__ == '__main__':
    main()