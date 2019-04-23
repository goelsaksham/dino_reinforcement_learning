"""
This file defines the various obstacle classes that will help in drawing the dinosaur in the arena.
"""

import random

from arena_object import ArenaObject


class Obstacle(ArenaObject):
    def __init__(self, object_id, init_pos, initial_velocity, object_acceleration, dimensions, arena_height):
        super(Obstacle, self).__init__(object_id, init_pos, initial_velocity, object_acceleration, dimensions,
                                       arena_height)


class Cactus(Obstacle):
    def __init__(self, initial_position, initial_velocity=(-3, 0), object_acceleration=(0.0, 0.0),
                 cactus_dimensions=[(40, 40), (50, 40), (60, 40), (70, 40), (80, 40), (100, 40), (180, 40)],
                 arena_height=400):
        cactus_dimension = random.sample(cactus_dimensions, 1)[0]
        super(Cactus, self).__init__(1, initial_position, initial_velocity, object_acceleration, cactus_dimension,
                                     arena_height)

    def update(self):
        self.update_position()
        self.update_velocity()


class Bird(Obstacle):
    def __init__(self, base_position, initial_velocity=(-3, 0), object_acceleration=(0.0, 0.0),
                 bird_dimension=(40, 30), height_addition=30, arena_height=400):
        level = random.sample([0, 1, 2, 3, 4, 5], 1)[0]
        initial_position = base_position[0], base_position[1] + level * height_addition
        super(Bird, self).__init__(2, initial_position, initial_velocity, object_acceleration, bird_dimension,
                                   arena_height)

    def update(self):
        self.update_position()
        self.update_velocity()
