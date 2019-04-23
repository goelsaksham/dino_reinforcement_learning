"""
This file defines the base class for an arena object. All the objects in the arena should be child of this class and
implement all the methods required.
"""


class ArenaObject:
	def __init__(self, object_id, init_pos, initial_velocity, object_acceleration, dimensions):
		"""
		The coordinate system will be defined from the bottom left as (0, 0) and upper right as (inf, inf)
			* +ve value for velocity or acceleration in x-axis is movement towards right
			* -ve value for velocity or acceleration in x-axis is movement towards left
			* +ve value for velocity or acceleration in y-axis is movement upwards
			* -ve value for velocity or acceleration in y-axis is movement downwards

		:param init_pos: The initial position of the object in the arena. This contains the x, y coordinate of the
						lower left corner of the rectangle signifying the object
		:param initial_velocity: The initial velocity of the object
		"""
		self.__id = object_id
		self.__x, self.__y = init_pos
		self.__vx, self.__vy = initial_velocity
		self.__ax, self.__ay = object_acceleration
		self.__width, self.__height = dimensions

	def get_id(self):
		return self.__id

	def get_x_pos(self):
		return self.__x

	def get_y_pos(self):
		return self.__y

	def get_position(self):
		return self.get_x_pos(), self.get_y_pos()

	def get_x_vel(self):
		return self.__vx

	def get_y_vel(self):
		return self.__vy

	def get_velocity(self):
		return self.get_x_vel(), self.get_y_vel()

	def get_x_acc(self):
		return self.__ax

	def get_y_acc(self):
		return self.__ay

	def get_acceleration(self):
		return self.get_x_acc(), self.get_y_acc()

	def get_width(self):
		return self.__width

	def get_height(self):
		return self.__height

	def get_dimensions(self):
		return self.get_width(), self.get_height()

	def set_pos(self, position):
		self.__x, self.__y = position

	def set_vel(self, velocity):
		self.__vx, self.__vy = velocity

	def set_acc(self, acceleration):
		self.__ax, self.__ay = acceleration

	def set_dims(self, dims):
		self.__width, self.__height = dims

	@staticmethod
	def relu(val):
		return max(0, val)

	def update_position(self):
		x_pos = self.get_x_pos() + self.get_x_vel()
		y_pos = ArenaObject.relu(self.get_y_pos() + self.get_y_vel())
		self.set_pos((x_pos, y_pos))

	def update_velocity(self):
		x_vel = self.get_x_vel() + self.get_x_acc()
		y_vel = self.get_y_vel() + self.get_y_acc()
		self.set_vel((x_vel, y_vel))
