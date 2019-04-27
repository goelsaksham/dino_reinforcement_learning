"""
This file defines the various obstacle classes that will help in drawing the dinosaur in the arena.
"""

import random

from arena_object import ArenaObject


class Obstacle(ArenaObject):
    def __init__(self, object_id, init_pos, initial_velocity, object_acceleration, dimensions):
        super(Obstacle, self).__init__(object_id, init_pos, initial_velocity, object_acceleration, dimensions)

    def update_position(self, agent_x_velocity=0):
        x_pos = self.get_x_pos() - agent_x_velocity
        y_pos = ArenaObject.relu(self.get_y_pos() + self.get_y_vel())
        self.set_pos((x_pos, y_pos))

    def update(self, agent_x_velocity=0):
        self.update_position(agent_x_velocity)
        self.update_velocity()


class Cactus(Obstacle):
    def __init__(self, initial_position, initial_velocity=(-3, 0), object_acceleration=(0.0, 0.0),
                 cactus_dimensions=[(20, 40), (20, 50), (20, 60), (20, 70), (30, 50), (30, 60),
                                    (30, 80), (40, 50), (40, 65), (40, 80), (50, 30), (50, 60),
                                    (60, 30), (60, 60), (70, 30), (70, 50), (70, 60), (80, 60),
                                    (80, 30), (100, 30), (100, 30)]):
        cactus_dimension = random.sample(cactus_dimensions, 1)[0]
        super(Cactus, self).__init__(1, initial_position, initial_velocity, object_acceleration, cactus_dimension)


class Bird(Obstacle):
    def __init__(self, base_position, initial_velocity=(-3, 0), object_acceleration=(0.0, 0.0),
                 bird_dimension=(40, 30), height_addition=20):
        level = random.sample([i*0.2 for i in range(0, 36)], 1)[0]
        initial_position = base_position[0], base_position[1] + level * height_addition
        super(Bird, self).__init__(2, initial_position, initial_velocity, object_acceleration, bird_dimension)

    def update(self, agent_x_velocity=0):
        self.update_position(agent_x_velocity)
        self.update_velocity()
