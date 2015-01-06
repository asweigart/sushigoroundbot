#! python3
# A simpler version of the Sushi Go Round bot made for the NCSS 2015 Summer Camp

# To use this program, have the Sushi Go Round game at the starting screen.
# At the > prompt, enter the first three letters of an order to make it
# (oni, gun, cal, etc.) or enter a number 1-6 to order new ingredients.
#   1-shrimp    2-rice
#   3-nori      4-roe
#   5-salmon    6-unagi

# Entering nothing will clear plates and re-scan for orders.

import pyautogui, sys, time

print('Program started.')

# Note where the bot's window is.
print('Move mouse over bot window and press Enter.')
input()
botWindow = pyautogui.position()

# locate the game window
window = pyautogui.locateOnScreen('top_left_corner.png')
if window is None:
    sys.exit('Could not find game on screen. Is the game visible?')

windowLeft = window[0]
windowTop = window[1]

print('Found game window at:', windowLeft, windowTop)

# preprogram all the ingredient button coordinates
shrimp = (35 + windowLeft, 330 + windowTop)
nori   = (35 + windowLeft, 380 + windowTop)
salmon = (35 + windowLeft, 430 + windowTop)
rice   = (90 + windowLeft, 330 + windowTop)
roe    = (90 + windowLeft, 380 + windowTop)
unagi  = (90 + windowLeft, 430 + windowTop)
mat    = (200 + windowLeft, 400 + windowTop)

# preprogram phone coordinates
phone            = (550 + windowLeft, 350 + windowTop)
rice1Button      = (500 + windowLeft, 290 + windowTop)
rice2Button      = (550 + windowLeft, 300 + windowTop)
toppingButton    = (500 + windowLeft, 270 + windowTop)
ingredButtons = {'shrimp': (500 + windowLeft, 220 + windowTop),
                 'nori':   (500 + windowLeft, 270 + windowTop),
                 'salmon': (500 + windowLeft, 320 + windowTop),
                 'unagi':  (550 + windowLeft, 220 + windowTop),
                 'roe':    (550 + windowLeft, 270 + windowTop)}

cancelButton     = (580 + windowLeft, 330 + windowTop)
deliveryButton   = (500 + windowLeft, 300 + windowTop)
phoneRegion      = (440 + windowLeft, 190 + windowTop, 200, 200)


# navigate through start screen
pyautogui.click(320 + windowLeft, 200 + windowTop) # click on Play button
pyautogui.click(300 + windowLeft, 380 + windowTop) # click on Continue button
pyautogui.click(550 + windowLeft, 450 + windowTop) # click on Skip
pyautogui.click(300 + windowLeft, 380 + windowTop) # click on Continue button
pyautogui.click(botWindow) # click back on bot window

def clickIngredients(coordinates):
    for c in coordinates:
        pyautogui.click(c)
    pyautogui.click(mat)

def clearPlates():
    # clear the plates
    for platex in range(80, 581, 100):
        pyautogui.click(platex + windowLeft, 200 + windowTop)
    pyautogui.click(botWindow) # put bot window back into focus

response = ''
while True:
    if response == '':
        # read screen for all orders and display them
        print('CURRENT ORDERS: (press Enter to re-scan)')
        for foodImage in ('onigiri_order.png', 'california_roll_order.png',
                          'gunkan_maki_order.png', 'salmon_roll_order.png',
                          'shrimp_sushi_order.png', 'unagi_roll_order.png',
                          'dragon_roll_order.png', 'combo_order.png'):
            numOrders = len(list(pyautogui.locateAllOnScreen(foodImage, region=(20 + windowLeft, 40 + windowTop, 580, 60))))
            if numOrders > 0:
                print(foodImage[:3], numOrders)
        print('==================')

    # get the user's action
    response = input('> ')

    if response == 'quit':
        sys.exit() # exit program

    if response == '':
        clearPlates()
        continue # go back to start of loop

    if not response.isdigit(): # command is to create an order
        if response[:3] == 'oni':
            # create an onigiri order
            print('Making onigiri...')
            clickIngredients([rice, rice, nori])
        if response[:3] == 'cal':
            # create a california roll order
            print('Making onigiri...')
            clickIngredients([rice, nori, roe])
        if response[:3] == 'gun':
            # create a gunkan maki order
            print('Making gunkan maki...')
            clickIngredients([rice, nori, roe, roe])
        if response[:3] == 'sal':
            # create a salmon roll order
            print('Making salmon...')
            clickIngredients([rice, nori, salmon, salmon])
        if response[:3] == 'shr':
            # create a shrimp sushi order
            print('Making shrimp...')
            clickIngredients([rice, nori, shrimp, shrimp])
        if response[:3] == 'una':
            # create a unagi roll order
            print('Making unagi roll...')
            clickIngredients([rice, nori, unagi, unagi])
        if response[:3] == 'dra':
            # create a dragon roll order
            print('Making dragon roll...')
            clickIngredients([rice, rice, nori, roe, unagi, unagi])
        if response[:3] == 'com':
            # create a combo order
            print('Making combo...')
            clickIngredients([rice, rice, nori, roe, salmon, unagi, shrimp])

        clearPlates()
        time.sleep(1.5) # mat rolling takes 1.5 seconds to complete


    # ordering more ingredients
    if response.isdigit():
        # handle ordering more rice
        if response == '2':
            print('Ordering more rice!')
            pyautogui.click(phone)
            pyautogui.click(rice1Button)
            if pyautogui.locateOnScreen('cant_afford_rice.png', region=phoneRegion) != None:
                print('Cannot afford rice right now.')
                pyautogui.click(cancelButton)
            else:
                pyautogui.click(rice2Button)
                pyautogui.click(deliveryButton)

        # handle ordering non-rice toppings
        if response in '13456':
            print('Ordering more toppings!')
            pyautogui.click(phone)
            pyautogui.click(toppingButton)
            if response == '1':
                ingred = 'shrimp'
            if response == '3':
                ingred = 'nori'
            if response == '4':
                ingred = 'roe'
            if response == '5':
                ingred = 'salmon'
            if response == '6':
                ingred = 'unagi'

            if pyautogui.locateOnScreen('cant_afford_' + ingred + '.png', region=phoneRegion) != None:
                print('Cannot afford ' + ingred + ' right now.')
                pyautogui.click(cancelButton)
            else:
                pyautogui.click(ingredButtons[ingred])
                pyautogui.click(deliveryButton)

        clearPlates()
