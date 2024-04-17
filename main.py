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

def flip(sprites):
    #sprites is the image used for the player (the asset)
    #first True is to flip in the x dir, and False is to NOT flip in the y dir
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites] 

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    #only flip the image if direction=True 
    #load the sprite sheets for the entire sprite animation
        #we will then later split this sheet into the image we need, OR loop through it to animate it
    path = join("assets", dir1, dir2)

    #we will pull all images for a sprite using this line below
        # only if the file is in the sprites asset path (dir) then load it 
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
        #load an image from the file pulled above, and convert/allow transparent background images
            #all the join(path, <fileName>) does is make sure that it is creating the full directory to the file (ex. fall.png becomes \assets\MainCharacters\MaskDude\fall.png)
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = [] #define the individual sprite images from the sheets
        # now to split the sheet based on the width of a single sprite within the sheet, width is the width of a single sprite image (ex. 32, 64, ... (IN PIXELS))
        for i in range(sprite_sheet.get_width() // width):
            #pygame.SRCALPHA allows loading of transparent images, 32 is a depth, just needed
            surface = pygame.Surface((width,height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height) #define a pygame rect of where the captured sprite image is to be drawn
            
            #@0,0 of the surface (where on the screen we want the sprite to show), we draw the sprite_sheet, but ONLY the frame we want (the rect)
            surface.blit(sprite_sheet, (0,0), rect) #blit is to draw
            sprites.append(pygame.transform.scale2x(surface)) #scale2x to upscale the sprite image (from 32x32 -> 64x64)

        #if there is a direction of the sprite needed, add a key to the sprite dict (all_sprites) to define the L v R facing sprites
            # we take the names of the animations (fall, hit, etc.) and create the keys based on these (fall_right, hit_left, etc.)
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites 
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites) #flip the sprites using the def fn above (flip across y axis to turn direction)
        else:
            #when there is no direction needed, still build the animations dict for the sprites
            all_sprites[image.replace(".png", "")] = sprites 

    return all_sprites
  
def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha() #create image from image file
    surface = pygame.Surface((size,size), pygame.SRCALPHA, 32) #define surface for game based on size
    rect = pygame.Rect(96,0, size, size) #96,0 is the start pixel of what image to use from the Terrain.png file, we then capture a rect of size x size to get the image
    surface.blit(image, (0,0), rect) #draw the surface into the game at the position of the rect
    
    return pygame.transform.scale2x(surface) #return the image in the game but scaled up

class Player(pygame.sprite.Sprite):
    #using the inherited sprite method to handle collisions later
    COLOR=(255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 5 #define a delay for the sprite animation to define how fast the animation runs

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        
        #velocities define how fast the player moves each frame
        self.x_vel = 0
        self.y_vel = 0 
        self.mask = None 
        self.direction = "left" #keep track of the player direction for showing sprite animation facing the correct way
        self.animation_count = 0
        self.fall_count = 0 #for tracking how long gravity has affected the player
        self.jump_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8 #as soon as the jump occurs, the y vel will be opposite to gravity, then gravity will cause the player to fall
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1: 
            #this is the player double jumping
            self.fall_count = 0
        

    #define how to move the player
    #movement in the 'grid' -- (0,0) is the top LEFT of the screen:
        #moving to the right is +x
        #moving to the left is -x
        #moving up is -y
        #moving down is +y
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0 #reset the animation to prevent weird animations when changing directions 

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0 #reset the animation to prevent weird animations when changing directions 

    def loop(self, fps):
        #define the player's loop, called every frame to handle movement, animations, etc.

        #for every tick in the loop, determine number of seconds (divide by FPS) to determine what strength of gravity is needed
            #take the min of at least 1 to not have 'fractional' gravity initially upon falling
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY) 
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1 #increment the fall_count loop 
        self.update_sprite() #update the sprite each frame

    def landed(self):
        #def function and interaction when a player has landed on a surface
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        #def function and interaction when a player hits their head (hits the bottom of a block/object)
        self.count = 0
        self.y_vel *= -1 #set the sign opposite, to cause the player to fall

    def update_sprite(self):
        #define a way to update the sprite (animation) 
        sprite_sheet = "idle" #set default to idle
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            #to prevent glitching of the animation in forever falling, standing on a block is a constantly reoccurring falling onto the block 
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run" #use the run sprite sheet when moving

        sprite_sheet_name = sprite_sheet + "_" + self.direction #based on the above condition, define what spritesheet to use
        sprites = self.SPRITES[sprite_sheet_name] #using the selected key, load the sprites for the given animation
        
        #self.ANIMATION_DELAY is for every x amount of frames we want to show a new animation (frame of the sprite sheet)
            #self. animation_count is used to determine how long the animation has been running for the current sprite
            # modulus divide by the len(sprites) to determine what frame of the sprite should be shown
            # ergo, as time passes, sprite_index goes through each frame of the sprite's animation
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count+=1
        self.update()

    def update(self):
        #define the player mask update, update the bounding rect of the player as it moves/animates/changes sprite
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # a mask is a mapping of the pixels for the player, NOT just the bounding box
            # this helps define that the players arm collides with an enemy, not just their bounding rects
        self.mask = pygame.mask.from_surface(self.sprite)
        pass

    def draw(self, win, offset_x):
        #draw the player within the window (win)
        # pygame.draw.rect(win, self.COLOR, self.rect) #pass the window (win), player color, and the rect where to draw it
        # self.sprite = self.SPRITES["idle_" + self.direction][0] #set the sprite to the first frame of the idle sprite animation
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    #define a parent class that will be the basis for all non-player objects

    def __init__(self, x, y, width, height, name=None):
        #define the constructor with all the required props to build the object
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA) #pygame.SRCALPHA allows transparent having images
        self.width = width
        self.height = height
        self.name = name 

    def draw(self, win, offset_x):
        #draw the image at the location of the object in the game
            #with the constructor, we always have the correct image created/modified before drawing
        win.blit(self.image, (self.rect.x- offset_x, self.rect.y))

class Block(Object):
    #define a block class that inherits the Object class
    def __init__(self, x, y, size): 
        super().__init__(x,y,size, size)
        block = get_block(size) #load the block for writing with blit
        self.image.blit(block, (0,0)) #draw the image to the screen
        self.mask = pygame.mask.from_surface(self.image) #define the mask for collisions


#input of name is the name of the background png to use (must use the full file name ex. "Blue.png" )
def get_background(name):
    #using the .\assets\Background\ directory to populate a grid background image 
    image = pygame.image.load(join("assets","Background", name))
    _, _, width, height = image.get_rect() #get_rect() returns x, y, width, height of the image #use _ to ignore x/y
    tiles = []

    for i in range(WIDTH // width +1 ): #divide the WIDTH of the game screen by the width of the background image to get the number of tiles needed in x
        for j in range(HEIGHT // height +1): #divide the HEIGHT of the game screen by the height of the background image to get the number of tiles needed in y
            #^both for loops contain +1 to ensure no gaps exist
            pos = (i * width, j * height) #define the position of the top left corner of the square for drawing
            tiles.append(pos)

    #return the location of where the tiles should be (tiles) and what image to draw there (image)
    return tiles, image

#define a function to draw the background
def draw(window, background, bg_image, player, objects, offset_x):
    #using get_background we can define the position of the tiles
    for tile in background:
        window.blit(bg_image, tile) #then with window.blit we physically draw the image to the window

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x) #call the Player class's draw here NOT the game draw fn
    
    #we update to clear the screen each frame, and prevent old images on the screen
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj): #within the sprite class (from pygame) there is the collision detection, since we are inheriting, we just need this to be true to determine a collision
            #if a player is moving down, then colliding with TOP of object
            if dy > 0:
                #set the bottom of the player rect (player feet) to be AT the top of the collided with obj
                player.rect.bottom = obj.rect.top 
                player.landed()
            #if a player is moving UP, then colliding with the BOTTOM of object
            elif dy < 0:
                #set the TOP of the player rect (player head) to be AT the BOTTOM of the collided with obj
                player.rect.top = obj.rect.bottom
                player.hit_head()

        collided_objects.append(obj)
    
    #return what objects were collided with to determine effects later, ex collided with a floor tile v a trap v a powerup, etc. 
    return collided_objects

def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    
    player.x_vel=0 #to have 'step' based movement this is needed, set the value to 0 when a new key is pressed (to prevent a flying spaceship movement) (aka only move while there is a key being pressed/held down)
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.move_right(PLAYER_VEL)
    
    handle_vertical_collision(player, objects, player.y_vel )

#define the main function that will run the game, pass the pygame window to know WHERE to run
#this will handle the event loop of teh game (collision, drawing, etc.)
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100,100,50,50)
    
    #create a floor of blocks based on the number of blocks that can fit within the game WIDTH
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    # blocks = [Block(0, HEIGHT- block_size, block_size)]
    
    offset_x = 0
    scroll_area_width = 200 #at 200 pixels near boarder of screen, then this is when we want to start scrolling the game 

    run = True
    #this is the game loop, running at a tick rate of FPS, to regulate the tick rate across devices
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: #when the user quits the game, stop the game loop
                run = False
                break
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        #need to call this player loop to ensure that the inputs/handle_move actually apply to the player
            # we continually call this loop in the game's while loop
        player.loop(FPS) 
        handle_move(player, floor)
        draw(window, background, bg_image, player, floor, offset_x)

        #check if the player is both moving to the right and within the boundary where we want scrolling to start
        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= WIDTH - scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    #if outside of the game loop, quit the pygame "instance"
    pygame.quit()

if __name__=="__main__":
    main(window)