#! python3
# A simpler version of the Sushi Go Round bot made for the NCSS 2015 Summer Camp

# To use this program, have the Sushi Go Round game at the starting screen.
# At the > prompt, enter the first three letters of an order to make it
# (oni, gun, cal, sal, shr, una, dra, com) or enter a number 1-6 to order new
# ingredients.
#   1-shrimp    2-rice
#   3-nori      4-roe
#   5-salmon    6-unagi

# Entering nothing will clear plates and re-scan for orders.

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
shrimp = (35 + winLeft, 330 + winTop)
nori   = (35 + winLeft, 380 + winTop)
salmon = (35 + winLeft, 430 + winTop)
rice   = (90 + winLeft, 330 + winTop)
roe    = (90 + winLeft, 380 + winTop)
unagi  = (90 + winLeft, 430 + winTop)
mat    = (200 + winLeft, 400 + winTop)

# preprogram phone coordinates
phone            = (550 + winLeft, 350 + winTop)
rice1Button      = (500 + winLeft, 290 + winTop)
rice2Button      = (550 + winLeft, 300 + winTop)
toppingButton    = (500 + winLeft, 270 + winTop)
ingredButtons = {'1': (500 + winLeft, 220 + winTop), # shrimp
                 '3': (500 + winLeft, 270 + winTop), # nori
                 '5': (500 + winLeft, 320 + winTop), # salmon
                 '4': (550 + winLeft, 270 + winTop), # roe
                 '6': (550 + winLeft, 220 + winTop)} # unagi
cancelButton     = (580 + winLeft, 330 + winTop)
deliveryButton   = (500 + winLeft, 300 + winTop)
phoneRegion      = (440 + winLeft, 190 + winTop, 200, 200)


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
command = ''
while True:
    if command == '':
        # read screen for all orders and display them
        print('CURRENT ORDERS: (press Enter to re-scan)')
        for foodImage in ('onigiri_order.png', 'california_roll_order.png',
                          'gunkan_maki_order.png', 'salmon_roll_order.png',
                          'shrimp_sushi_order.png', 'unagi_roll_order.png',
                          'dragon_roll_order.png', 'combo_order.png'):
            numOrders = len(list(pyautogui.locateAllOnScreen(foodImage, region=(20 + winLeft, 40 + winTop, 580, 60))))
            if numOrders > 0:
                # only display amount of orders if there are any
                print(foodImage[:3], numOrders)
        print('==================')

    # get the user's command (One of: oni, cal, gun, shr, sal, dra, com, 1,
    # 2, 3, 4, 5, 6, quit)
    command = input('> ')

    if command == 'quit':
        sys.exit() # exit program

    if command == '':
        clearPlates()
        continue # go back to start of loop


    if not command.isdigit(): # command is to create an order
        if command == 'oni':
            print('Making onigiri...')
            clickIngredients([rice, rice, nori])
        if command == 'cal':
            print('Making california roll...')
            clickIngredients([rice, nori, roe])
        if command == 'gun':
            print('Making gunkan maki...')
            clickIngredients([rice, nori, roe, roe])
        if command == 'sal':
            print('Making salmon roll...')
            clickIngredients([rice, nori, salmon, salmon])
        if command == 'shr':
            print('Making shrimp sushi...')
            clickIngredients([rice, nori, shrimp, shrimp])
        if command == 'una':
            print('Making unagi roll...')
            clickIngredients([rice, nori, unagi, unagi])
        if command == 'dra':
            print('Making dragon roll...')
            clickIngredients([rice, rice, nori, roe, unagi, unagi])
        if command == 'com':
            print('Making combo...')
            clickIngredients([rice, rice, nori, roe, salmon, unagi, shrimp])

        clearPlates()
        time.sleep(1.5) # mat rolling takes 1.5 seconds to complete


    # ordering more ingredients
    if command.isdigit():
        # handle ordering more rice
        if command == '2':
            print('Ordering more rice!')
            pyautogui.click(phone)
            pyautogui.click(rice1Button)
            if pyautogui.locateOnScreen('cant_afford_rice.png', region=phoneRegion) != None:
                print('Cannot afford rice right now.')
                pyautogui.click(cancelButton) # close the phone menu
            else:
                # complete the order
                pyautogui.click(rice2Button)
                pyautogui.click(deliveryButton)

        # handle ordering non-rice toppings
        if command in '13456':
            print('Ordering more toppings!')
            pyautogui.click(phone)
            pyautogui.click(toppingButton)

            if pyautogui.locateOnScreen('cant_afford_' + command + '.png', region=phoneRegion) != None:
                print('Cannot afford that topping right now.')
                pyautogui.click(cancelButton) # close the phone menu
            else:
                # complete the order
                pyautogui.click(ingredButtons[command])
                pyautogui.click(deliveryButton)

        clearPlates()
