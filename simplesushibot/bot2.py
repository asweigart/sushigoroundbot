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


# navigate through start screen
pyautogui.click(320 + winLeft, 200 + winTop) # click on Play button
pyautogui.click(300 + winLeft, 380 + winTop) # click on Continue button
pyautogui.click(550 + winLeft, 450 + winTop) # click on Skip
pyautogui.click(300 + winLeft, 380 + winTop) # click on Continue button
pyautogui.click(botWindow) # click back on bot window

# The main program loop will constantly ask the user for a command until
# they enter "quit".
while True:
    # get the user's command
    command = input('> ')

    if command == 'quit':
        sys.exit() # exit program
