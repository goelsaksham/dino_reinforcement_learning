"""
This file defines the Dinosaur class that will help in drawing the dinosaur in the arena.
"""

from arena_object import ArenaObject


class Dinosaur(ArenaObject):
	def __init__(self, init_pos=(0, 0), init_vel=(1, 0), obj_acc=(0.001, -1), walk_dims=(10, 20), duck_dims=(20, 10),
	             walking_figure_path=f'../../data/figs/dino.png',
	             duck_figure_path=f'../../data/figs/dino_ducking.png'):
		super(Dinosaur, self).__init__(init_pos, init_vel, obj_acc, walk_dims)
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

	@staticmethod
	def relu(val):
		return max(0, val)

	def is_jumping(self):
		return self.__jumping

	def is_walking(self):
		return self.__walking

	def is_ducking(self):
		return self.__ducking

	def duck(self):
		self.__walking, self.__jumping, self.__ducking= False, False, True
		self.set_dims(self.__duck_dims)

	def jump(self):
		self.__walking, self.__jumping, self.__ducking = False, True, False
		self.set_dims(self.__walk_dims)

	def assert_state(self):
		assert self.__id == 0
		if self.__walking:
			assert not self.__jumping and not self.__ducking
			assert self.__current_fig == self.__walk_fig
			assert self.get_height(), self.get_width() == self.__walk_dims
		if self.__jumping:
			assert not self.__walking and not self.__ducking
			assert self.__current_fig == self.__walk_fig
			assert self.get_height(), self.get_width() == self.__walk_dims
		if self.__ducking:
			assert not self.__walking and not self.__jumping
			assert self.__current_fig == self.__duck_fig
			assert self.get_height(), self.get_width() == self.__duck_dims

	def update_current_fig(self):
		if self.__walking or self.__jumping:
			self.__current_fig = self.__walk_fig
			self.set_dims(self.__walk_dims)
		else:
			self.__current_fig = self.__duck_fig
			self.set_dims(self.__duck_dims)

	def update_current_state(self):
		if self.get_y_pos() > 0:
			self.__walking = False
			self.__jumping = True
		else:
			self.__walking = True
			self.__jumping = False

	def update(self):
		x_pos, y_pos = 0, Dinosaur.relu(self.get_y_pos() + self.get_y_vel())
		x_vel, y_vel = Dinosaur.relu(self.get_x_vel() + self.get_x_acc()), self.get_y_vel() + self.get_y_acc()
		if y_pos == 0:
			y_vel = 0
		self.set_pos((x_pos, y_pos))
		self.set_vel((x_vel, y_vel))
		self.update_current_state()
		self.assert_state()

