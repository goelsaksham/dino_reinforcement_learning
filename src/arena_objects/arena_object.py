"""
This file defines the base class for an arena object. All the objects in the arena should be child of this class and
implement all the methods required.
"""


class ArenaObject:
	def __init__(self, init_pos, init_vel, obj_acc, dims):
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

	def set_pos(self, pos):
		self.__x, self.__y = pos

	def set_vel(self, vel):
		self.__vx, self.__vy = vel

	def set_acc(self, acc):
		self.__ax, self.__ay = acc

	def set_dims(self, dims):
		self.__width, self.__height = dims
