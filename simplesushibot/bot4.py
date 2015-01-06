#! python3
import pyautogui, sys, time
print('Program started.')


# Note where the bot's window is.
input('Move mouse over bot window and press Enter.')
botWindow = pyautogui.position()


# locate the game window
window = pyautogui.locateOnScreen('top_left_corner.png')
if window is None:
    sys.exit('Could not find game on screen. Is the game visible?')

winLeft = window[0]
winTop = window[1]

print('Found game window at:', winLeft, winTop)

# preprogram all the ingredient button coordinates
shrimp = [35 + winLeft, 330 + winTop]
nori   = [35 + winLeft, 380 + winTop]
salmon = [35 + winLeft, 430 + winTop]
rice   = [90 + winLeft, 330 + winTop]
roe    = [90 + winLeft, 380 + winTop]
unagi  = [90 + winLeft, 430 + winTop]
mat    = [200 + winLeft, 400 + winTop]

# navigate through start screen
pyautogui.click(320 + winLeft, 200 + winTop) # click on Play button
pyautogui.click(300 + winLeft, 380 + winTop) # click on Continue button
pyautogui.click(550 + winLeft, 450 + winTop) # click on Skip
pyautogui.click(300 + winLeft, 380 + winTop) # click on Continue button
pyautogui.click(botWindow) # click back on bot window

def clickIngredients(coordinates):
    # click on all the coordinates in the coordinates list, then click the mat
    for c in coordinates:
        pyautogui.click(c)
    pyautogui.click(mat)

def clearPlates():
    # clear the plates by clicking on them
    for platex in range(80, 581, 100):
        pyautogui.click(platex + winLeft, 200 + winTop)
    pyautogui.click(botWindow) # put bot window back into focus

# The main program loop will constantly ask the user for a command until
# they enter "quit".
while True:
    # get the user's command
    command = input('> ')

    if command == 'quit':
        sys.exit() # exit program

    elif command == '':
        # read screen for all orders and display them
        print('CURRENT ORDERS: (press Enter to re-scan)')
        for foodImage in ['onigiri_order.png', 'california_roll_order.png',
                          'gunkan_maki_order.png', 'salmon_roll_order.png',
                          'shrimp_sushi_order.png', 'unagi_roll_order.png',
                          'dragon_roll_order.png', 'combo_order.png']:
            numOrders = len(list(pyautogui.locateAllOnScreen(foodImage, region=[20 + winLeft, 40 + winTop, 580, 60])))
            if numOrders > 0:
                # only display amount of orders if there are any
                print(foodImage[:3], numOrders)
        print('==================')

        clearPlates()
        continue # go back to start of loop

    elif not command.isdigit(): # command is to create an order
        if command == 'oni':
            print('Making onigiri...')
            clickIngredients([rice, rice, nori])
        elif command == 'cal':
            print('Making california roll...')
            clickIngredients([rice, nori, roe])
        elif command == 'gun':
            print('Making gunkan maki...')
            clickIngredients([rice, nori, roe, roe])
        elif command == 'sal':
            print('Making salmon roll...')
            clickIngredients([rice, nori, salmon, salmon])
        elif command == 'shr':
            print('Making shrimp sushi...')
            clickIngredients([rice, nori, shrimp, shrimp])
        elif command == 'una':
            print('Making unagi roll...')
            clickIngredients([rice, nori, unagi, unagi])
        elif command == 'dra':
            print('Making dragon roll...')
            clickIngredients([rice, rice, nori, roe, unagi, unagi])
        elif command == 'com':
            print('Making combo...')
            clickIngredients([rice, rice, nori, roe, salmon, unagi, shrimp])
        else:
            continue # invalid sushi order, go back to start of loop

        clearPlates()
        time.sleep(1.5) # mat rolling takes 1.5 seconds to complete

