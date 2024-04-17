import os, random, math, pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Duck Day 3") #set the 'caption' for the game window 

#defining global variables
BG_COLOR = (255, 255, 255) #equal to white in RGB
WIDTH, HEIGHT = 1000, 800 
FPS = 60
PLAYER_VEL = 5 #Player velocity, speed at which they move around screen (assume pixels per frame)

window = pygame.display.set_mode((WIDTH, HEIGHT)) #create the game window within pygame

def get_background():
    #using the .\ 
    pass

#define the main function that will run the game, pass the pygame window to know WHERE to run
#this will handle the event loop of teh game (collision, drawing, etc.)
def main(window):
    clock = pygame.time.Clock()
    run = True

    #this is the game loop, running at a tick rate of FPS, to regulate the tick rate across devices
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #when the user quits the game, stop the game loop
                run = False
                break

    #if outside of the game loop, quit the pygame "instance"
    pygame.quit()

if __name__=="__main__":
    main(window)