import pygame
from shared_resources import screen
pygame.mixer.init()


'''  
	    HOW TO USE BUTTONS IN MAIN GAME LOOP - MAKE SURE TO SET ACTION TO FALSE AT END

			if play_button.action:
        print("Play button clicked!")
        # Perform the action, e.g., start the game
        play_button.action = False  # Reset action flag after handling
							^^^^^^^
	'''
	

'''
    # Get mouse position and button states
    mouse_position = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

'''
class SimpleButton:
	def __init__(self, surface: pygame.Surface, coordinates: tuple[int, int], darkness_factor: int | None, shift_amount: int, scale: int, image_path: str, held_image_path: str | None, sound_effect_path: str | None):

		# used for calculations
		self.surface = surface
		self.coordinates = coordinates
		self.shift_amount = shift_amount
		self.darkness_factor = 0.50 if darkness_factor is None else darkness_factor # between 0 and 1

		# sound (SOUND AS A NOTICABLE DELAY FOR SOME REASON)
		self.sound = None if sound_effect_path is None else pygame.mixer.Sound(sound_effect_path)

		# surfaces and rects
		self.image = scale_image(image_path, scale)
		self.held_image = None if held_image_path is None else scale_image(held_image_path, scale)
		self.darked_image = None if self.held_image != None else darken_image(self.image, self.darkness_factor)
		self.rect = self.image.get_rect(center=self.coordinates)

		# button functionality
		self.action = False
		self.held = False
		self.shifted = False
	
	def update_state(self, mouse_position, mouse_buttons):
		if self.rect.collidepoint(mouse_position):
			if mouse_buttons[0]: # left click is held down down
				if self.shifted == False:
					self.rect.y += self.shift_amount # shift button downwards when held
					self.shifted = True
				self.held = True
				

			elif self.held: # left click is releases
				if self.shifted:
					self.rect.y -= self.shift_amount # moves button back to normal place
					self.shifted = False
				self.held = False
				self.action = True

				# if there's a sound effect it will play
				if self.sound:
					self.sound.play()

		else: # resets held state when mouse leaves button !!!!!!!!!!!!is this needed?!!!!!!!!!!!!!!
			self.held = False
	

	def draw(self):
		if self.held: # if the button is held
			if self.held_image == None: # if there's no picture the first image will be darkened
				self.surface.blit(self.darked_image, self.rect.topleft)

			else: # if there's a held down image it will be displayed
				self.surface.blit(self.held_image, self.rect.topleft)

		else: # if the button isn't held, display default image
			self.surface.blit(self.image, self.rect.topleft)


	def update_state_and_draw(self, mouse_position, mouse_buttons):
		self.update_state(mouse_position, mouse_buttons)
		self.draw()


class MultiSpriteImage:
	def __init__(self, surface: pygame.Surface, coordinates: tuple[int, int], scale: int, use_center: True | False, sprite_sheet_rows: int | None, sprite_sheet_columns: int | None, sprite_sheet_path: str | None, image_dictionary: dict | None):

		self.surface = surface
		self.coordinates = coordinates
		self.scale = scale
		self.use_center = use_center
		self.sprite_sheet = None if sprite_sheet_path is None else scale_image(sprite_sheet_path, self.scale) 
		self.sprite_sheet_sprites = []
		self.sprite_sheet_sprite_rects = []
		self.image_dictionary = None if image_dictionary is None else image_dictionary
		self.counter = 0
		self.row_completions = 0

		# to display specific images and flip through them
		self.image_to_display = 0 
		self.flip_to_next_image = False 
		self.change_image = False


		# sprite sheet variables
			# this is used to calculate how many pictures there are and how to cut them out the sheet
		self.sprite_sheet_rows = sprite_sheet_rows
		self.sprite_sheet_columns = sprite_sheet_columns
			# if there's a sprite sheet
		if self.sprite_sheet:
			self.image_amount = self.sprite_sheet_rows * self.sprite_sheet_columns

		if self.sprite_sheet:
			while self.counter < self.image_amount:
				subsurface_rect = pygame.Rect(self.counter%self.sprite_sheet_columns*self.sprite_sheet.get_width()/self.sprite_sheet_columns, self.row_completions*self.sprite_sheet.get_height(), self.sprite_sheet.get_width()/self.sprite_sheet_columns, self.sprite_sheet.get_height()/self.sprite_sheet_rows)
				self.sprite_sheet_sprites.append(self.sprite_sheet.subsurface(subsurface_rect))
				self.sprite_sheet_sprite_rects.append(self.sprite_sheet.subsurface(subsurface_rect).get_rect())
				if self.counter%self.sprite_sheet_columns == self.sprite_sheet_columns - 1:
					self.row_completions += 1
				self.counter += 1 

		
				
		# image to display and when to change it
	def draw_next_image(self):
		self.change_image = True

	def draw_specific_image(self, image_index):
		self.image_to_display = image_index

	def draw(self):
		if self.change_image:
			self.image_to_display += 1
			self.change_image = False
		
		# if it works, it works. Don't you dare look at this long line of math 
		if self.use_center:
			self.surface.blit(self.sprite_sheet_sprites[self.image_to_display % self.image_amount], (self.coordinates[0] - self.sprite_sheet_sprites[self.image_to_display % self.image_amount].get_width()//2, self.coordinates[1] - self.sprite_sheet_sprites[self.image_to_display % self.image_amount].get_height()//2))
		else:
			self.surface.blit(self.sprite_sheet_sprites[self.image_to_display % self.image_amount], self.coordinates)


class RicochetingSprite:
	def __init__(self, surface: pygame.Surface, coordinates: tuple[int, int], speed: int, scale: int, use_center: True | False, image_path: str, boundary_coordinates: tuple[int, int], boundary_width: int, boundary_height: int):

		self.surface = surface
		self.coordinates = coordinates
		self.speed = speed
		self.scale = scale
		self.use_center = use_center

		# load, scale, and get rect of image
		self.image = scale_image(image_path, scale)
		self.rect = self.image.get_rect()
		self.rect.center = coordinates

		# sets initial direction
		self.x_direction = 'right'
		self.y_direction = 'up'

		# checks for perfect corner hit
		self.corner_hit = False

		# creates boundary rect
		self.boundary = pygame.Rect((boundary_coordinates),(boundary_width, boundary_height))

	def draw(self):

		# if both are true a corner hit happened :)
		if self.corner_hit == True:
			self.corner_hit = False
		hit_horizontal = False
		hit_vertical = False
		
		# checks if the next movement will take the sprite out of bounds
		if self.rect.right + self.speed > self.boundary.right:
			self.x_direction = 'left'
			hit_horizontal = True
		elif self.rect.left - self.speed < self.boundary.left:
			self.x_direction = 'right'
			hit_horizontal = True

		if self.rect.top + self.speed < self.boundary.top:
			self.y_direction = 'down'
			hit_vertical = True
		elif self.rect.bottom - self.speed > self.boundary.bottom:
			self.y_direction = 'up'
			hit_vertical = True

		# Check for a corner hit (both horizontal and vertical boundaries are hit)
		if hit_horizontal and hit_vertical:
			self.corner_hit = True
			print("Corner hit detected!")  # You can replace this with your desired action.



		# moves sprite based on current direction [left, right, up, down]
		if self.x_direction == 'right':
			self.rect.x += self.speed
		elif self.x_direction == 'left':
			self.rect.x -= self.speed

		if self.y_direction == 'up':
			self.rect.y -= self.speed
		elif self.y_direction == 'down':
			self.rect.y += self.speed

		# draws the image after the calculations are done :3
		self.surface.blit(self.image, self.rect)





class Text: 
	def __init__(self, surface, font, font_size, text_color, text_content="", coordinates=(0, 0), background_color=None, bold=False, italic=False, antialias=True, use_center=False):
		self.surface = surface
		self.font = pygame.font.Font(font, font_size)
		self.font.set_bold(bold)
		self.font.set_italic(italic)
		self.text_color = text_color
		self.text_content = text_content
		self.coordinates = coordinates
		self.background_color = background_color
		self.antialias = antialias
		self.use_center = use_center

		# gets the rect so text can be position with self.rect.blah
		self.text_surface = self.font.render(self.text_content, self.antialias, self.text_color, self.background_color)
		self.rect = self.text_surface.get_rect()
		if self.use_center:
			self.rect.center = self.coordinates

	
	def draw(self):
		if self.use_center:
			# Render the text to get the surface
			text_surface = self.font.render(self.text_content, self.antialias, self.text_color, self.background_color)
			# Get the rectangle of the text surface
			text_rect = text_surface.get_rect()
			# Set the center of the rectangle to the desired position
			text_rect.center = self.coordinates
			# Blit the text surface to the screen using the rect's topleft as the position
			self.surface.blit(text_surface, text_rect.topleft)
		else:
			text_surface = self.font.render(self.text_content, self.antialias, self.text_color, self.background_color)
			self.surface.blit(text_surface, self.rect.topleft)



# Functions
def darken_image(image, darkness_factor):
	# copies original image so it doesn't get changed
	image = image.copy()
	# creates blank surface the same size as the image sent
	dark_surface = pygame.Surface(image.get_size()).convert_alpha()
	# makes the surface black and makes transparent based on 'darkness_facotr'
	dark_surface.fill((0, 0, 0, int(255 *  darkness_factor)))
	# blend the dark surface with the image sent to make the orignal image darker
	image.blit(dark_surface, (0,0), special_flags=pygame.BLEND_RGBA_SUB)
	return image

def scale_image(image_path, scale):
	return pygame.transform.scale(pygame.image.load(image_path), (pygame.image.load(image_path).get_width() * scale, pygame.image.load(image_path).get_height() * scale))