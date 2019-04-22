"""
This is the file that contains the main module that runs the whole arena
"""
import os
import glob
from arena_objects.agent import Dinosaur
import time
import matplotlib.pyplot as plt
import random
import pygame
from pygame import RLEACCEL
from pygame import *

####################################################################################################
# Game Initialization
####################################################################################################
pygame.init()
screen_size = (width, height) = (800, 200)
FPS = 60
black = (0, 0, 0)
white = (255, 255, 255)
background_color = (235, 235, 235)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
pygame.display.set_caption("Chrome T-Rex Rush")
jump_sound = pygame.mixer.Sound('../data/sounds/jump.wav')
die_sound = pygame.mixer.Sound('../data/sounds/die.wav')
checkPoint_sound = pygame.mixer.Sound('../data/sounds/checkPoint.wav')
high_score = 0

####################################################################################################
# Directory Utils
####################################################################################################
def exist_directory(directory_path):
	return os.path.isdir(directory_path)


def exist_file(file_path):
	return os.path.isfile(file_path)


def construct_path(directory_path, directory_content):
	return os.path.join(directory_path, directory_content)


def check_output_directory(directory_path):
	if exist_directory(directory_path):
		return True
	else:
		try:
			os.makedirs(directory_path)
			return True
		except FileExistsError:
			return True


def get_directory_contents(directory_path, pattern='*'):
	if exist_directory(directory_path):
		cwd = os.getcwd()
		# change current wording directory
		os.chdir(directory_path)
		# file list
		file_names = glob.glob(pattern)
		# change the cwd back to normal
		os.chdir(cwd)
		return file_names
	return []


def remove_pattern(orig_str, pattern):
	return orig_str.replace(pattern, '')


def get_subdirectory_names(directory_path):
	return get_directory_contents(directory_path, '*//')


def get_subdirectory_nms(directory_path):
	return set([remove_pattern(subdirectory, '//') for subdirectory in get_subdirectory_names(directory_path)])


def get_file_names(directory_path, extension='.*'):
	return get_directory_contents(directory_path, f'*{extension}')


def get_file_nms(directory_path, extension='.*'):
	return set([remove_pattern(file_name, extension) for file_name in get_file_names(directory_path, extension)])


####################################################################################################
# Game Utils
####################################################################################################
def load_image(sprites_path, x_size=-1, y_size=-1, color_key=None):
	sprites_image = pygame.image.load(sprites_path)
	sprites_image = sprites_image.convert()
	if color_key is not None:
		if color_key is -1:
			color_key = sprites_image.get_at((0, 0))
		sprites_image.set_colorkey(color_key, RLEACCEL)

	if x_size != -1 or y_size != -1:
		sprites_image = pygame.transform.scale(sprites_image, (x_size, y_size))

	return sprites_image, sprites_image.get_rect()


def load_sprite_sheet(sprites_path, nx, ny,
					  x_scale=-1, y_scale=-1, color_key=None):
	sprites_sheet = pygame.image.load(sprites_path)
	sprites_sheet = sprites_sheet.convert()

	sheet_rectangle = sprites_sheet.get_rect()

	sprites = []

	x_size = sheet_rectangle.width/nx
	y_size = sheet_rectangle.height/ny

	for i in range(0, ny):
		for j in range(0, nx):
			rect = pygame.Rect((j*x_size,i*y_size,x_size,y_size))
			image = pygame.Surface(rect.size)
			image = image.convert()
			image.blit(sprites_sheet,(0,0),rect)
			if color_key is not None:
				if color_key is -1:
					color_key = image.get_at((0, 0))
				image.set_colorkey(color_key, RLEACCEL)
			if x_scale != -1 or y_scale != -1:
				image = pygame.transform.scale(image, (x_scale, y_scale))
			sprites.append(image)

	sprite_rect = sprites[0].get_rect()
	return sprites, sprite_rect


def display_game_over_message(screen, width, height, return_button_image, game_over_image):
	return_button_rect = return_button_image.get_rect()
	return_button_rect.centerx = width / 2
	return_button_rect.top = height*0.52

	gameover_rect = game_over_image.get_rect()
	gameover_rect.centerx = width / 2
	gameover_rect.centery = height*0.35

	screen.blit(return_button_image, return_button_rect)
	screen.blit(game_over_image, gameover_rect)


def extract_digits(number):
	if number > -1:
		digits = []
		i = 0
		while number / 10 != 0:
			digits.append(number % 10)
			number = int(number / 10)

		digits.append(number % 10)
		for i in range(len(digits), 5):
			digits.append(0)
		digits.reverse()
		return digits


####################################################################################################
# Game Object Classes
####################################################################################################
class ArenaObject:
	def __init__(self, init_pos, init_vel, obj_acc, dims, figure, rect):
		"""
		The coordinate system will be defined from the lower left as (0, 0) and upper right as (inf, inf)
			* +ve value for velocity or acceleration in x-axis is movement towards right
			* -ve value for velocity or acceleration in x-axis is movement towards left
			* +ve value for velocity or acceleration in y-axis is movement upwards
			* -ve value for velocity or acceleration in y-axis is movement downwards

		:param init_pos: The initial position of the object in the arena. This contains the x, y coordinate of the
		lower left corner of the rectangle signifying the object
		:param init_vel:
		:param obj_acc:
		"""
		self.__x, self.__y = init_pos
		self.__vx, self.__vy = init_vel
		self.__ax, self.__ay = obj_acc
		self.__width, self.__height = dims
		self.__figure = figure
		self.__rect = rect

	def get_x_pos(self):
		return self.__x

	def get_y_pos(self):
		return self.__y

	def get_x_vel(self):
		return self.__vx

	def get_y_vel(self):
		return self.__vy

	def get_x_acc(self):
		return self.__ax

	def get_y_acc(self):
		return self.__ay

	def get_width(self):
		return self.__width

	def get_height(self):
		return self.__height

	def get_figure(self):
		return self.__figure

	def get_rectangle(self):
		return self.__rect

	def set_pos(self, pos):
		self.__x, self.__y = pos

	def set_vel(self, vel):
		self.__vx, self.__vy = vel

	def set_acc(self, acc):
		self.__ax, self.__ay = acc

	def set_dims(self, dims):
		self.__width, self.__height = dims

	def set_figure(self, figure):
		self.__figure = figure

	def set_rectangle(self, rect):
		self.__rect = rect

	def draw(self):
		screen.blit(self.__figure, self.__rect)


class Dinosaur(ArenaObject):
	def __init__(self, init_pos=(0, 0), init_vel=(1, 0), obj_acc=(0.1, -.25),
				 walk_dims=(10, 20), duck_dims=(20, 10),
				 jump_velocity_add = 7, max_duck_time = 80,
				 walking_figure_path=f'../data/figs/dino.png',
				 duck_figure_path=f'../data/figs/dino_ducking.png'):
		super(Dinosaur, self).__init__(init_pos, init_vel, obj_acc, walk_dims, None, None)
		self.__id = 0
		self.__walk_fig_path = walking_figure_path
		self.__walk_figs, self.__walk_rect = load_sprite_sheet(self.__walk_fig_path, 5, 1, 44, 47, -1)
		self.__duck_fig_path = duck_figure_path
		self.__duck_figs, self.__duck_rect = load_sprite_sheet(self.__duck_fig_path, 2, 1, 59, 47, -1)
		self.__walking = True
		self.__jumping = False
		self.__ducking = False
		self.__dead = False
		self.__collided = False
		self.__walk_dims = walk_dims
		self.__duck_dims = duck_dims
		self.__jump_vel_add = jump_velocity_add
		self.__duck_timer = 0
		self.__max_duck_timer = max_duck_time
		# Initial figure should be the dinosaur with both feet on ground
		self.set_figure(self.__walk_figs[0])
		self.set_rectangle(self.__walk_rect)
		# Set initial position of the rectangle that needs to be drawn
		self.get_rectangle().bottom = int(0.95 * height)
		self.get_rectangle().left = width // 30
		# Set the width of the rectangle
		self.__walk_rectangle_width = self.__walk_rect.width
		self.__duck_rectangle_width = self.__duck_rect.width
		self.__walk_counter = 0
		self.__duck_counter = 0
		self.__counter = 0

	@staticmethod
	def relu(val):
		return max(0, val)

	def is_jumping(self):
		return self.__jumping

	def is_walking(self):
		return self.__walking

	def is_ducking(self):
		return self.__ducking

	def get_score(self):
		return self.__counter // 10

	def is_dead(self):
		return self.__dead

	def update_pos(self):
		x_pos, y_pos = 0, Dinosaur.relu(self.get_y_pos() + self.get_y_vel())
		self.set_pos((x_pos, y_pos))

	def update_velocity(self):
		x_vel, y_vel = Dinosaur.relu(self.get_x_vel() + self.get_x_acc()), self.get_y_vel() + self.get_y_acc()
		if self.get_y_pos() == 0:
			y_vel = 0
		self.set_vel((x_vel, y_vel))

	def walk(self):
		self.__walking, self.__jumping, self.__ducking = True, False, False
		self.set_dims(self.__walk_dims)
		# Reset the duck timer
		self.__duck_timer = 0

	def duck(self):
		self.__walking, self.__jumping, self.__ducking = False, False, True
		self.set_dims(self.__duck_dims)
		self.__duck_timer += 1

	def jump(self):
		self.__walking, self.__jumping, self.__ducking = False, True, False
		self.set_dims(self.__walk_dims)

	def assert_state(self):
		assert self.__id == 0
		assert self.get_x_pos() >= 0 and self.get_y_pos() >= 0
		if self.__walking:
			assert not self.__jumping and not self.__ducking
			assert self.__current_fig == self.__walk_figs
			assert self.get_height(), self.get_width() == self.__walk_dims
			assert self.get_y_pos() == 0
		if self.__jumping:
			assert not self.__walking and not self.__ducking
			assert self.__current_fig == self.__walk_figs
			assert self.get_height(), self.get_width() == self.__walk_dims
			assert self.get_y_pos() > 0
		if self.__ducking:
			assert not self.__walking and not self.__jumping
			assert self.__current_fig == self.__duck_figs
			assert self.get_height(), self.get_width() == self.__duck_dims
			assert self.get_y_pos() == 0
		assert self.__walking or self.__jumping or self.__ducking

	def update_current_fig(self):
		self.__counter += 1
		if self.__walking:
			# Need this for better and easy transition in states
			if self.__counter % 10 == 0:
				self.__walk_counter += 1
			self.set_figure(self.__walk_figs[2 + self.__walk_counter % 2])
			self.set_rectangle(self.__walk_rect)
			self.set_dims(self.__walk_dims)
		elif self.__jumping:
			self.set_figure(self.__walk_figs[0])
			self.set_rectangle(self.__walk_rect)
			self.set_dims(self.__walk_dims)
		elif self.is_ducking():
			if self.__counter % 10 == 0:
				self.__duck_counter += 1
			self.set_figure(self.__duck_figs[self.__duck_counter % 2])
			self.get_rectangle().width = self.__duck_rectangle_width
			self.set_dims(self.__duck_dims)
		else:
			self.set_figure(self.__walk_figs[-1])
			self.set_rectangle(self.__walk_rect)
			self.set_dims(self.__walk_dims)

	def update(self, action):
		# self.assert_state()
		if action == 'j':
			# When jumping we immediately change state from our walking our ducking state
			# Check if not already in air (walking or ducking)
			if not self.is_jumping():
				# Set the initial y velocity for the dinosaur
				self.set_vel((self.get_x_vel(), self.__jump_vel_add))
			else:
				# If already in jump then do not let the user do a second jump
				pass
			# Change the variables accordingly so that the position is updated and so is the velocity
			self.jump()
			self.update_pos()
			self.update_velocity()
		elif action == 'd':
			# When ducking first check that you are not currently in a jumping state
			# Here it is guaranteed that we are in either walking or ducking state
			if not self.is_jumping():
				# Now we should keep our ducking state restart from the origin if we are already ducking
				# Essentially if we duck again when we were already ducking then we will start a new ducking session
				# from then
				if self.is_ducking():
					self.__duck_timer = 0
				# Then we update the state and increase the duck timer
				self.duck()
			else:
				# If already in the jumping state then you cannot duck
				pass
			self.update_pos()
			self.update_velocity()
		else:
			# First check that if in ducking state then make sure we keep on increasing the duck timer
			if self.is_ducking():
				self.duck()
			# Check if the duck timer has already reached the max threshold then change back to walking
			if self.__duck_timer >= self.__max_duck_timer:
				self.walk()
			# Sanity check. If we just finished our jump and we landed on ground then we should revert back to
			# walking
			if self.is_jumping() and self.get_y_pos() == 0:
				self.walk()
			self.update_pos()
			self.update_velocity()

		# After changing the state update the figure of the dinosaur accordingly
		self.update_current_fig()
		# Moving the figure
		self.set_rectangle(self.get_rectangle().move([self.get_x_pos(), -self.get_y_pos()]))


class Cactus(pygame.sprite.Sprite, ArenaObject):
	def __init__(self, init_pos=(0, 0), init_vel=(-2, 0), obj_acc=(0., 0),
				 dims=(20, 10), cacti_figure_path=f'../data/figs/cacti-small.png',
				 x_size=-1, y_size=-1):
		pygame.sprite.Sprite.__init__(self, self.containers)
		ArenaObject.__init__(self, init_pos, init_vel, obj_acc, dims, None, None)
		self.__cacti_fig_path = cacti_figure_path
		self.__cacti_figs, self.__cacti_rect = load_sprite_sheet(self.__cacti_fig_path, 3, 1, x_size, y_size, -1)
		# Initial figure should be the dinosaur with both feet on ground
		self.set_figure(self.__cacti_figs[random.randrange(0, 3)])
		self.set_rectangle(self.__cacti_rect)
		# Set initial position of the rectangle that needs to be drawn
		self.get_rectangle().bottom = int(0.95 * height)
		self.get_rectangle().left = width + self.get_rectangle().width

	def update_pos(self):
		x_pos, y_pos = self.get_x_pos() + self.get_x_vel(), Dinosaur.relu(self.get_y_pos() + self.get_y_vel())
		self.set_pos((x_pos, y_pos))

	def update_velocity(self):
		x_vel, y_vel = self.get_x_vel() + self.get_x_acc(), self.get_y_vel() + self.get_y_acc()
		if self.get_y_pos() == 0:
			y_vel = 0
		self.set_vel((x_vel, y_vel))

	def update(self):
		self.update_pos()
		self.update_velocity()
		# Moving the figure
		self.set_rectangle(self.get_rectangle().move([self.get_x_vel(), self.get_y_vel()]))
		if self.get_rectangle().right < 0:
			self.kill()


class Bird(pygame.sprite.Sprite, ArenaObject):
	def __init__(self, init_pos=(0, 0), init_vel=(-2, 0), obj_acc=(0, 0),
	             dims=(20, 10), bird_figure_path=f'../data/figs/bird.png',
	             x_size=-1, y_size=-1):
		pygame.sprite.Sprite.__init__(self, self.containers)
		ArenaObject.__init__(self, init_pos, init_vel, obj_acc, dims, None, None)
		self.__bird_figure_path = bird_figure_path
		self.__bird_figure, self.__bird_rectangle = load_sprite_sheet(self.__bird_figure_path, 2, 1, x_size, y_size,-1)

		self.__bird_height = [0.82 * height, 0.75 * height, 0.6 * height]

		# Initial figure should be the dinosaur with both feet on ground
		self.set_figure(self.__bird_figure[0])
		self.set_rectangle(self.__bird_rectangle)
		# Set initial position of the rectangle that needs to be drawn
		self.get_rectangle().centery = self.__bird_height[random.randrange(0, 3)]
		self.get_rectangle().left = width + self.get_rectangle().width

		self.__bird_counter = 0
		self.__counter = 0

	def update_pos(self):
		x_pos, y_pos = self.get_x_pos() + self.get_x_vel(), Dinosaur.relu(self.get_y_pos() + self.get_y_vel())
		self.set_pos((x_pos, y_pos))

	def update_velocity(self):
		x_vel, y_vel = self.get_x_vel() + self.get_x_acc(), self.get_y_vel() + self.get_y_acc()
		if self.get_y_pos() == 0:
			y_vel = 0
		self.set_vel((x_vel, y_vel))

	def update(self):
		self.__counter += 1
		if self.__counter % 10 == 0:
			self.__bird_counter += 1
		self.set_figure(self.__bird_figure[self.__bird_counter%2])

		self.update_pos()
		self.update_velocity()
		# Moving the figure
		self.set_rectangle(self.get_rectangle().move([self.get_x_vel(), self.get_y_vel()]))
		if self.get_rectangle().right < 0:
			self.kill()


class Ground():
	def __init__(self,speed=-2):
		self.image, self.rect = load_image('../data/figs/ground.png',-1,-1,-1)
		self.image1, self.rect1 = load_image('../data/figs/ground.png',-1,-1,-1)
		self.rect.bottom = height
		self.rect1.bottom = height
		self.rect1.left = self.rect.right
		self.speed = speed

	def draw(self):
		screen.blit(self.image, self.rect)
		screen.blit(self.image1, self.rect1)

	def update(self):
		self.rect.left += self.speed
		self.rect1.left += self.speed

		if self.rect.right < 0:
			self.rect.left = self.rect1.right

		if self.rect1.right < 0:
			self.rect1.left = self.rect.right

class Cloud(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image,self.rect = load_image('../data/figs/cloud.png', int(90*30/42), 30, -1)
		self.speed = 1
		self.rect.left = x
		self.rect.top = y
		self.movement = [-1*self.speed,0]

	def draw(self):
		screen.blit(self.image,self.rect)

	def update(self):
		self.rect = self.rect.move(self.movement)
		if self.rect.right < 0:
			self.kill()

class Scoreboard():
	def __init__(self,x=-1,y=-1):
		self.score = 0
		self.tempimages,self.temprect = load_sprite_sheet('../data/figs/numbers.png',12,1,11,int(11*6/5),-1)
		self.image = pygame.Surface((55,int(11*6/5)))
		self.rect = self.image.get_rect()
		if x == -1:
			self.rect.left = width*0.89
		else:
			self.rect.left = x
		if y == -1:
			self.rect.top = height*0.1
		else:
			self.rect.top = y

	def draw(self):
		screen.blit(self.image,self.rect)

	def update(self,score):
		score_digits = extract_digits(score)
		self.image.fill(background_color)
		for s in score_digits:
			self.image.blit(self.tempimages[s],self.temprect)
			self.temprect.left += self.temprect.width
		self.temprect.left = 0



####################################################################################################
# Game Logic
####################################################################################################
def introscreen():
	temp_dino = Dinosaur()
	cacti = pygame.sprite.Group()
	pteras = pygame.sprite.Group()
	clouds = pygame.sprite.Group()
	last_obstacle = pygame.sprite.Group()

	Cactus.containers = cacti
	Bird.containers = pteras
	Cloud.containers = clouds

	temp_cactus = Cactus()
	gameStart = False

	callout, callout_rect = load_image('../data/figs/call_out.png', 196, 45, -1)
	callout_rect.left = width * 0.05
	callout_rect.top = height * 0.4

	temp_ground,temp_ground_rect = load_sprite_sheet('../data/figs/ground.png', 15, 1, -1, -1, -1)
	temp_ground_rect.left = width/20
	temp_ground_rect.bottom = height

	logo,logo_rect = load_image('../data/figs/logo.png', 240, 40, -1)
	logo_rect.centerx = width*0.6
	logo_rect.centery = height*0.6
	while not gameStart:
		if pygame.display.get_surface() == None:
			print("Couldn't load display surface")
			return True
		else:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return True
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
						temp_dino.update('j')
					elif event.key == pygame.K_DOWN:
						temp_dino.update('d')
						temp_cactus.update()


		temp_dino.update('')
		temp_cactus.update()

		if pygame.display.get_surface() != None:
			screen.fill(background_color)
			screen.blit(temp_ground[0], temp_ground_rect)
			if True:
				 screen.blit(logo, logo_rect)
			temp_dino.draw()

			pygame.display.update()

		clock.tick(FPS)
		if temp_dino.is_jumping():
			gameStart = True


def gameplay():
    global high_score
    high_score = 0
    gamespeed = 4
    startMenu = False
    gameOver = False
    gameQuit = False
    playerDino = Dinosaur()
    new_ground = Ground(-1*gamespeed)
    scb = Scoreboard()
    highsc = Scoreboard(width*0.78)
    counter = 0

    cacti = pygame.sprite.Group()
    pteras = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    last_obstacle = pygame.sprite.Group()

    Cactus.containers = cacti
    Bird.containers = pteras
    Cloud.containers = clouds

    retbutton_image,retbutton_rect = load_image('../data/figs/replay_button.png',35,31,-1)
    gameover_image,gameover_rect = load_image('../data/figs/game_over.png',190,11,-1)

    temp_images,temp_rect = load_sprite_sheet('../data/figs/numbers.png',12,1,11,int(11*6/5),-1)
    HI_image = pygame.Surface((22, int(11*6/5)))
    HI_rect = HI_image.get_rect()
    HI_image.fill(background_color)
    HI_image.blit(temp_images[10],temp_rect)
    temp_rect.left += temp_rect.width
    HI_image.blit(temp_images[11],temp_rect)
    HI_rect.top = height*0.1
    HI_rect.left = width*0.73

    while not gameQuit:
        while startMenu:
            pass
        while not gameOver:
            if pygame.display.get_surface() == None:
                print("Couldn't load display surface")
                gameQuit = True
                gameOver = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gameOver = True

                    if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            if not playerDino.is_jumping():
	                            jump_sound.play()
                            playerDino.update('j')

                        if event.key == pygame.K_DOWN:
                            playerDino.update('d')

            for c in cacti:
                #c.movement[0] = -1*gamespeed
                c.update()
                c.draw()
                #if pygame.sprite.collide_mask(playerDino, c):
                    #playerDino.isDead = True
                #    if pygame.mixer.get_init() != None:
                #        die_sound.play()

            for p in pteras:
                #p.movement[0] = -1*gamespeed
                p.update()
                p.draw()
                #if pygame.sprite.collide_mask(playerDino,p):
                #    playerDino.isDead = True
                #    if pygame.mixer.get_init() != None:
                #        die_sound.play()

            if len(cacti) < 2:
                if len(cacti) == 0:
                    last_obstacle.empty()
                    last_obstacle.add(Cactus(init_vel=(-gamespeed/2, 0), x_size=40,y_size=40))
                else:
                    for l in last_obstacle:
                        if l.get_rectangle().right < width*0.7 and random.randrange(0,50) == 10:
                            last_obstacle.empty()
                            last_obstacle.add(Cactus(init_vel=(-gamespeed/2, 0), x_size=40, y_size=40))

            if len(pteras) == 0 and random.randrange(0,200) == 10 and counter > 500:
                for l in last_obstacle:
                    if l.get_rectangle().right < width*0.8:
                        last_obstacle.empty()
                        last_obstacle.add(Bird(init_vel=(-gamespeed, 0), x_size=46, y_size=40))

            if len(clouds) < 5 and random.randrange(0,300) == 10:
                Cloud(width,random.randrange(height/5,height/2))

            playerDino.update('')
            cacti.update()
            pteras.update()
            clouds.update()
            new_ground.update()
            scb.update(playerDino.get_score())
            highsc.update(high_score)

            if pygame.display.get_surface() != None:
	            screen.fill(background_color)
	            new_ground.draw()
	            clouds.draw(screen)
	            scb.draw()
	            if high_score != 0:
		            highsc.draw()
		            screen.blit(HI_image,HI_rect)
	            for c in cacti:
		            c.draw()
	            playerDino.draw()
	            for b in pteras:
		            b.draw()

	            pygame.display.update()
            clock.tick(FPS)

            if playerDino.is_dead():
                gameOver = True
                #if playerDino.score > high_score:
                #    high_score = playerDino.score

            if counter%700 == 699:
                new_ground.speed -= 1
                gamespeed += 1

            counter = (counter + 1)

        if gameQuit:
            break

        while gameOver:
            if pygame.display.get_surface() == None:
                print("Couldn't load display surface")
                gameQuit = True
                gameOver = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gameOver = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            gameQuit = True
                            gameOver = False

                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            gameOver = False
                            gameplay()
            highsc.update(high_score)
            if pygame.display.get_surface() != None:
                display_game_over_message(retbutton_image,gameover_image)
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image,HI_rect)
                pygame.display.update()
            clock.tick(FPS)

    pygame.quit()
    quit()


def main():
	introscreen()
	gameplay()
	# timesteps = 1000
	# x_cors = range(timesteps)
	# y_cors = []
	# for t in range(timesteps):
	# 	if random.random() < 0.08:
	# 		my_dinosaur.update('j')
	# 		print(t, 'Jumping')
	# 	elif random.random() < 0.15:
	# 		my_dinosaur.update('d')
	# 		print(t, 'Ducking')
	# 	else:
	# 		my_dinosaur.update('')
	# 		print(t, 'Doing Nothing')
	# 	y_cors.append(my_dinosaur.get_y_pos() - 1 if my_dinosaur.is_ducking() else my_dinosaur.get_y_pos())
	# plt.plot(x_cors, y_cors)
	# plt.show()


if __name__ == '__main__':
	main()
