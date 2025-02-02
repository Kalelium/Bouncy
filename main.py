# pygame -> engine, os -> helps with closing app, shared_resources -> stores info multiple files need at once, classes -> all classes
import pygame
import sys
from shared_resources import SCREEN_WIDTH, SCREEN_HEIGHT, screen
from classes import SimpleButton, Text, MultiSpriteImage, RicochetingSprite

# pygame setup
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption('DVD Logo')

# colors (R, G, B) | 0 -> 255
white = (255, 255, 255)
dark_blue_gray = (50, 55, 65)

# class definitions
dvd_logo = RicochetingSprite(screen, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 10, 1, False, 'assets/dvd_logo46x22.png', (0, 0), SCREEN_WIDTH, SCREEN_HEIGHT)
#blue_stars = MultiSpriteImage(screen, (SCREEN_WIDTH//2, SCREEN_HEIGHT//3), 12, True, 1, 6, 'assets/blue_stars.png', None)
#upgrade_button = SimpleButton(screen, (SCREEN_WIDTH//2, SCREEN_HEIGHT*0.75), None, 10, 2, 'assets/upgrade_button.png', None, None)

# variables


running = True

# main loop 
while running:

    # player input
    mouse_position = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        # quits game when the topleft x button is pressed
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(dark_blue_gray)

    # RENDER YOUR GAME HERE

    
    dvd_logo.draw()



    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
sys.exit()