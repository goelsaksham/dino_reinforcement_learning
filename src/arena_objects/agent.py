"""
This file defines the Dinosaur class that will help in drawing the dinosaur in the arena.
"""

import numpy as np

from arena_object import ArenaObject


class Agent(ArenaObject):
    def __init__(self, object_id, init_pos, initial_velocity, object_acceleration, object_dimension,
                 walking_dimensions=(40, 80), ducking_dimensions=(80, 40), low_jump_acceleration=(0.0, 11.5),
                 high_jump_acceleration=(0.0, 15.0)):
        super(Agent, self).__init__(object_id, init_pos, initial_velocity, object_acceleration, object_dimension)
        self.__walking = True
        self.__jumping = False
        self.__ducking = False
        self.__crashed = False
        self.__walk_dims = walking_dimensions
        self.__duck_dims = ducking_dimensions
        self.__high_jump_acc = high_jump_acceleration
        self.__low_jump_acc = low_jump_acceleration
        self.__current_action = 0
        self.__total_reward = 0

    def is_jumping(self):
        return self.__jumping

    def is_walking(self):
        return self.__walking

    def is_ducking(self):
        return self.__ducking

    def walk(self):
        self.__walking, self.__jumping, self.__ducking = True, False, False
        self.set_dims(self.__walk_dims)

    def duck(self):
        self.__walking, self.__jumping, self.__ducking = False, False, True
        self.set_dims(self.__duck_dims)

    def jump(self):
        self.__walking, self.__jumping, self.__ducking = False, True, False
        self.set_dims(self.__walk_dims)

    def update_dimensions(self):
        if self.__walking or self.__jumping:
            self.set_dims(self.__walk_dims)
        else:
            self.set_dims(self.__duck_dims)

    def get_current_action(self):
        return self.__current_action

    def set_current_action(self, action):
        self.__current_action = action

    def has_crashed(self):
        return self.__crashed

    def set_crashed(self, crash):
        self.__crashed = crash

    def get_total_reward(self):
        return self.__total_reward

    def increase_reward(self, additional_reward):
        self.__total_reward += additional_reward

    @staticmethod
    def get_action_to_action_name_dict():
        return {0: 'no_op', 1: 'low_jump', 2: 'high_jump', 3: 'duck'}

    @staticmethod
    def get_action_name_action_dict():
        return {'no_op': 0, 'low_jump': 1, 'high_jump': 2, 'duck': 3}

    def get_action_from_action_name(self, action_name):
        try:
            return self.get_action_name_action_dict()[action_name]
        except KeyError:
            return 0

    def get_current_action_name(self):
        return self.get_action_to_action_name_dict()[self.get_current_action()]

    @staticmethod
    def check_within_bounds(l_x, l_y, u_x, u_y, x, y):
        return (l_x <= x <= u_x) and (l_y <= y <= u_y)

    @staticmethod
    def get_coordinates(lower_left_coordinate, dimensions, where='ll'):
        if where == 'll':
            return lower_left_coordinate
        elif where == 'ul':
            return lower_left_coordinate[0], lower_left_coordinate[1] + dimensions[1]
        elif where == 'lr':
            return lower_left_coordinate[0] + dimensions[0], lower_left_coordinate[1]
        elif where == 'ur':
            return lower_left_coordinate[0] + dimensions[0], lower_left_coordinate[1] + dimensions[1]
        else:
            return lower_left_coordinate

    def collision_check(self, arena_object_1, arena_object_2):
        ao_1_ll_cors, ao_2_cors = arena_object_1.get_position(), arena_object_2.get_position()
        ao_1_dims, ao_2_dims = arena_object_1.get_dimensions(), arena_object_2.get_dimensions()
        ao_1_ur_cors = self.get_coordinates(ao_1_ll_cors, ao_1_dims, where='ur')
        # Check if lower left in bound
        if self.check_within_bounds(*ao_1_ll_cors, *ao_1_ur_cors, *self.get_coordinates(ao_2_cors, ao_2_dims, 'll')):
            return True
        if self.check_within_bounds(*ao_1_ll_cors, *ao_1_ur_cors, *self.get_coordinates(ao_2_cors, ao_2_dims, 'ul')):
            return True
        if self.check_within_bounds(*ao_1_ll_cors, *ao_1_ur_cors, *self.get_coordinates(ao_2_cors, ao_2_dims, 'lr')):
            return True
        if self.check_within_bounds(*ao_1_ll_cors, *ao_1_ur_cors, *self.get_coordinates(ao_2_cors, ao_2_dims, 'ur')):
            return True
        return False

    def has_collided_with_obstacle(self, obstacles: list):
        # Implement the algorithm that checks whether the object has crashed or not
        for obstacle in obstacles:
            if self.collision_check(self, obstacle) or self.collision_check(obstacle, self):
                return True
        return False

    def get_current_action_reward(self):
        # If the agent has crashed then return negative reward
        if self.has_crashed():
            return -100
        else:
            # Else return reward based on the action
            if self.get_current_action() == 1:
                return -3
            elif self.get_current_action() == 2:
                return -5
            elif self.get_current_action() == 3:
                return -0.001
            else:
                return 1

    def get_jump_acceleration(self, jump_type):
        if jump_type == 'l':
            return self.__low_jump_acc
        elif jump_type == 'h':
            return self.__high_jump_acc
        else:
            raise ValueError(f'Invalid Jump Type')

    def process_jump_action(self, action_name):
        if action_name.lower() == 'low_jump':
            # Set the initial y velocity for the dinosaur based upon the jump type
            self.set_vel((self.get_x_vel() + self.get_jump_acceleration('l')[0],
                          self.get_y_vel() + self.get_jump_acceleration('l')[1]))
        else:
            # Set the initial y velocity for the dinosaur based upon the jump type
            self.set_vel((self.get_x_vel() + self.get_jump_acceleration('h')[0],
                          self.get_y_vel() + self.get_jump_acceleration('h')[1]))
        # Change the jump variables accordingly so we can show in jump state
        self.jump()

    def update_agent(self):
        # get the current action for the agent
        action_name = self.get_current_action_name()
        # Use that to process the actions accordingly
        if action_name.lower() == 'high_jump' or action_name.lower() == 'low_jump':
            # When jumping we immediately change state from the walking or ducking state
            # Check if not already in air (walking or ducking)
            if not self.is_jumping():
                self.process_jump_action(action_name)
            else:
                # Check if in air or at ground (finished the last jump)
                if self.get_y_pos() == 0:
                    # If at ground after previous jump, but have another jump instruction then start another jump
                    # instruction
                    self.process_jump_action(action_name)
                else:
                    # If already in jump then do not let the user do a second jump
                    pass
        elif action_name.lower() == 'duck':
            # When ducking first check that you are not currently in a jumping state
            # Here it is guaranteed that we are in either walking or ducking state
            if not self.is_jumping():
                # Change to the duck position
                self.duck()
            else:
                # If already in the jumping state then you cannot duck
                pass
        else:
            # Make sure not in air or jumping state. If that then start walking or doing no-op
            if not self.is_jumping() or self.get_y_pos() == 0:
                self.walk()

        # Update the position and velocity of the agent after updating the state of the agent
        self.update_position()
        self.update_velocity()

        # Make sure that if jumping was the action but already on the ground means start walking
        if self.is_jumping():
            if self.get_y_pos() == 0:
                self.walk()

        # After changing the state update the dimensions of the dinosaur accordingly
        self.update_dimensions()

    def update(self):
        self.update_agent()


class Dinosaur(Agent):
    def __init__(self, initial_position=(0, 0), initial_velocity=(0, 0), object_acceleration=(0.0, -0.5),
                 walking_dimensions=(40, 80), ducking_dimensions=(80, 40), low_jump_acceleration=(0.0, 11.5),
                 high_jump_acceleration=(0.0, 15.0)):
        super(Dinosaur, self).__init__(0, initial_position, initial_velocity, object_acceleration,
                                       walking_dimensions, walking_dimensions, ducking_dimensions,
                                       low_jump_acceleration, high_jump_acceleration)

    def update_position(self):
        # Dinosaur always stay at the same x coordinate. However The y position should be changed based on whether
        # the dinosaur is jumping or not
        x_pos, y_pos = 0, Dinosaur.relu(self.get_y_pos() + self.get_y_vel())
        self.set_pos((x_pos, y_pos))

    def update_velocity(self):
        # Update the velocity based upon the acceleration
        x_vel, y_vel = Dinosaur.relu(self.get_x_vel() + self.get_x_acc()), self.get_y_vel() + self.get_y_acc()
        # Make sure the y velocity is 0 if the object is on ground (y == 0)
        if self.get_y_pos() == 0:
            y_vel = 0
        self.set_vel((x_vel, y_vel))

    def assert_state(self):
        assert self.__id == 0
        assert self.get_x_pos() >= 0 and self.get_y_pos() >= 0
        if self.__walking:
            assert not self.__jumping and not self.__ducking
            assert self.get_height(), self.get_width() == self.__walk_dims
            assert self.get_y_pos() == 0
        if self.__jumping:
            assert not self.__walking and not self.__ducking
            assert self.get_height(), self.get_width() == self.__walk_dims
            assert self.get_y_pos() > 0
        if self.__ducking:
            assert not self.__walking and not self.__jumping
            assert self.get_height(), self.get_width() == self.__duck_dims
            assert self.get_y_pos() == 0
        assert self.__walking or self.__jumping or self.__ducking


class GeneticAlgorithmAgent(Agent):
    def __init__(self, agent_weights, initial_position=(0, 0), initial_velocity=(0, 0),
                 object_acceleration=(0.0, -0.5), walking_dimensions=(40, 80), ducking_dimensions=(80, 40),
                 low_jump_acceleration=(0.0, 11.5), high_jump_acceleration=(0.0, 15.0)):
        super(GeneticAlgorithmAgent, self).__init__(0, initial_position, initial_velocity, object_acceleration,
                                                    walking_dimensions, walking_dimensions, ducking_dimensions,
                                                    low_jump_acceleration, high_jump_acceleration)
        assert len(agent_weights.shape) == 2
        assert agent_weights.shape[0] == len(self.get_action_to_action_name_dict())
        self.__weights = agent_weights
        self.__environment_state = None

    def get_weights(self):
        return self.__weights

    def set_weights(self, new_weights):
        self.__weights = new_weights

    def get_current_environment_state(self):
        return self.__environment_state

    def set_current_environment_state(self, environment_state):
        self.__environment_state = environment_state

    @staticmethod
    def softmax_activation(vector):
        return np.exp(vector) / np.sum(np.exp(vector))

    def get_best_action(self):
        # Make sure the weight matrix dimensions match the environment state length
        assert self.get_weights().shape[1] == len(self.get_current_environment_state())
        # Get the probabilities for each action using the softmax activation
        action_probabilities = GeneticAlgorithmAgent.softmax_activation(np.matmul(self.get_weights(),
                                                                                  self.get_current_environment_state()))
        # Return the index of the best action: maximum probability
        return np.argmax(action_probabilities)

    def update(self):
        best_action = self.get_best_action()
        self.set_current_action(best_action)
        self.update_agent()

    def get_current_action_reward(self):
        # If the agent has crashed then return negative reward
        if self.has_crashed():
            return -1
        else:
            # Else return reward based on the action
            if self.get_current_action() == 1:
                return -0.01
            elif self.get_current_action() == 2:
                return -0.03
            elif self.get_current_action() == 3:
                return 0.0001
            else:
                return 0.03
