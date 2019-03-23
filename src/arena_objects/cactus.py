"""
This file defines the Cactus class that will help in drawing the dinosaur in the arena.
"""

from arena_object import ArenaObject


class Cactus(ArenaObject):
	def __init__(self, init_pos=(0, 0), init_vel=(1, 0), obj_acc=(0.1, -1.25),
	             fugure_dims=(10, 20), catcus_path=f'../../data/figs/dino.png',
	             duck_figure_path=f'../../data/figs/dino_ducking.png'):
		super(Cactus, self).__init__(init_pos, init_vel, obj_acc, walk_dims)
		self.__id = 0
		self.__walk_fig_path = walking_figure_path
		self.__walk_fig = self.__walk_fig_path  # load(self.walk_fig_path)
		self.__duck_fig_path = duck_figure_path
		self.__duck_fig = self.__duck_fig_path  # load(self.jump_fig_path)
		self.__walking = True
		self.__jumping = False
		self.__ducking = False
		self.__collided = False
		self.__current_fig = self.__walk_fig
		self.__walk_dims = walk_dims
		self.__duck_dims = duck_dims
		self.__jump_vel_add = jump_velocity_add
		self.__duck_timer = 0
		self.__max_duck_timer = max_duck_time

	@staticmethod
	def relu(val):
		return max(0, val)

	def is_jumping(self):
		return self.__jumping

	def is_walking(self):
		return self.__walking

	def is_ducking(self):
		return self.__ducking

	def update_pos(self):
		x_pos, y_pos = 0, Cactus.relu(self.get_y_pos() + self.get_y_vel())
		self.set_pos((x_pos, y_pos))

	def update_velocity(self):
		x_vel, y_vel = Cactus.relu(self.get_x_vel() + self.get_x_acc()), self.get_y_vel() + self.get_y_acc()
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
			assert self.__current_fig == self.__walk_fig
			assert self.get_height(), self.get_width() == self.__walk_dims
			assert self.get_y_pos() == 0
		if self.__jumping:
			assert not self.__walking and not self.__ducking
			assert self.__current_fig == self.__walk_fig
			assert self.get_height(), self.get_width() == self.__walk_dims
			assert self.get_y_pos() > 0
		if self.__ducking:
			assert not self.__walking and not self.__jumping
			assert self.__current_fig == self.__duck_fig
			assert self.get_height(), self.get_width() == self.__duck_dims
			assert self.get_y_pos() == 0
		assert self.__walking or self.__jumping or self.__ducking

	def update_current_fig(self):
		if self.__walking or self.__jumping:
			self.__current_fig = self.__walk_fig
			self.set_dims(self.__walk_dims)
		else:
			self.__current_fig = self.__duck_fig
			self.set_dims(self.__duck_dims)

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
