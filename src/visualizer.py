import pygame


class GUI:
	def __init__(self, environment_height=400):
		self.__environment_height = environment_height

	def get_environment_height(self):
		return self.__environment_height

	def get_pygame_coordinates(self, arena_object):
		arena_object_x, arena_object_y = arena_object.get_position()
		arena_object_y = self.get_environment_height() - arena_object_y
		arena_object_w, arena_object_h = arena_object.get_dimensions()
		return arena_object_x, arena_object_y - arena_object_h, arena_object_w, arena_object_h

	def draw_agent(self, screen, agent):
		BLUE = [0, 0, 255]
		pygame.draw.rect(screen, BLUE, self.get_pygame_coordinates(agent))

	def draw_obstacles(self, screen, all_obstacles):
		RED = [255, 0, 0]
		for obstacle in all_obstacles:
			pygame.draw.rect(screen, RED, self.get_pygame_coordinates(obstacle))

	def draw_environment_objects(self, screen, agent, all_obstacles):
		# Drawing the agent
		self.draw_agent(screen, agent)
		# Draw the obstacles
		self.draw_obstacles(screen, all_obstacles)
