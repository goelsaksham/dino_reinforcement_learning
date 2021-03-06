import pygame

from arena.environments import ChromeTRexRush
from arena_objects.agent import *
from visualizer import GUI
from utils.directory_utils import *
import heapq


class Game:
    def __init__(self, environment: ChromeTRexRush):
        self.__environment = environment
        self.__environment_gui = GUI(self.get_environment().get_environment_height())

    def get_environment(self):
        return self.__environment

    def set_environment(self, new_environment):
        self.__environment = new_environment
        self.__environment_gui = GUI(self.get_environment().get_environment_height())

    def get_environment_gui(self):
        return self.__environment_gui

    @staticmethod
    def update_agent_state(agent, agent_type, *args):
        assert len(args) == 1
        if agent_type.lower() == 'human':
            # If the type of the agent is human, *args represent the action of the agent
            agent.set_current_action(*args)
        elif agent_type.lower() == 'genetic':
            # If the type of the agent is genetic, *args represent the environment state
            agent.set_current_environment_state(*args)
        elif agent_type.lower() == 'q':
            agent.set_environment_state(*args)

    def update_game_agents_state(self, agent_list):
        for agent_information in agent_list:
            agent = agent_information[0]
            if not agent.has_crashed():
                self.update_agent_state(*agent_information)
                agent.update()

    def update_game_agents_collision_status(self, agent_list):
        # Get all the obstacles
        all_obstacles = self.get_environment().get_all_obstacle_list()
        # For each agent update its collision status using the obstacles
        for agent_information in agent_list:
            agent = agent_information[0]
            if agent.has_collided_with_obstacle(all_obstacles):
                # Set the crashed status accordingly
                agent.set_crashed(True)

    def update_game_agents_acceleration(self, agent_list):
        current_level = self.get_environment().get_current_level()
        for agent_information in agent_list:
            agent = agent_information[0]
            agent.update_agent_acceleration(current_level)

    @staticmethod
    def update_game_agents_reward(agent_list):
        for agent_information in agent_list:
            agent = agent_information[0]
            if not agent.has_crashed():
                agent.increase_reward(agent.get_current_action_reward())

    def update_game_agents(self, agent_list):
        self.update_game_agents_state(agent_list)
        self.update_game_agents_collision_status(agent_list)
        self.update_game_agents_reward(agent_list)
        self.update_game_agents_acceleration(agent_list)

    def draw_game_agent(self, screen, agent):
        self.get_environment_gui().draw_agent(screen, agent)

    def draw_game_agents(self, screen, agent_list):
        for agent_information in agent_list:
            agent = agent_information[0]
            if not agent.has_crashed():
                self.draw_game_agent(screen, agent)

    def draw_game_obstacles(self, screen):
        # Get all the obstacles in the environment and then draw them
        self.get_environment_gui().draw_obstacles(screen, self.get_environment().get_all_obstacle_list())

    def update_game(self, agent_list):
        sample_agent = agent_list[0][0]
        # Update the Environment
        self.get_environment().update_environment(sample_agent.get_x_vel())
        # Update the agents. It does not matter that we are updating the environment first and then the agent,
        # because the first thing we do in the agent update is update its position and then check for collision and
        # then for rewards so everything works out fine
        self.update_game_agents(agent_list)

    def draw_game(self, screen, agent_list):
        # Draw the agents
        self.draw_game_agents(screen, agent_list)
        # Draw the game obstacles
        self.draw_game_obstacles(screen)

    def init_game(self):
        # initialize the pygame module and font
        pygame.init()

        # Initialize the screen
        screen = pygame.display.set_mode((self.get_environment().get_environment_width(),
                                          self.get_environment().get_environment_height()))
        white = [255, 255, 255]
        screen.fill(white)

        # Initialize the clock for the game
        clock = pygame.time.Clock()

        # initialize the writing mode in pygame
        pygame.font.init()
        # Get the font for the score
        font = pygame.font.SysFont('Comic Sans MS', 20)

        # Set the key repeat for the Duck command
        pygame.key.set_repeat(50, 1)

        return screen, clock, font

    def display_game_statistics(self, screen, font):
        # Update the scoreboard
        black = [0, 0, 0]
        screen.blit(font.render(f'Level: {self.get_environment().get_current_level()}', False, black), (0, 0))
        screen.blit(font.render(f'Score: {self.get_environment().get_current_score()}', False, black),
                    (self.get_environment().get_environment_width() - 100, 0))

    def display_game_over_message(self, screen, font):
        black = [0, 0, 0]
        screen.blit(font.render(f'Game Over!!!', False, black),
                    (self.get_environment().get_environment_width() / 2 - 50,
                     self.get_environment().get_environment_height() / 2 - 20))

    def update_environment_statistics(self):
        # Add an obstacle
        self.get_environment().add_obstacle()
        # Increase the Score
        self.get_environment().increase_score()
        # Increase the level if needed
        self.get_environment().increase_level()

    @staticmethod
    def handle_game_over():
        while True:
            # Wait for the user to exit the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

    @staticmethod
    def update_game_display():
        pygame.display.update()


class HumanGame(Game):
    def __init__(self, agent, environment):
        super(HumanGame, self).__init__(environment)
        self.__agent = agent

    def get_agent(self):
        return self.__agent

    @staticmethod
    def get_key_map():
        return {pygame.K_UP: 'high_jump', pygame.K_SPACE: 'high_jump', pygame.K_DOWN: 'duck',
                pygame.K_d: 'duck', pygame.K_l: 'low_jump', pygame.K_s: 'low_jump'}

    def get_key_action(self, key_pressed):
        try:
            return self.get_key_map()[key_pressed]
        except KeyError:
            return 'no_op'

    def handle_user_action(self):
        # Stores which key is pressed
        key_pressed = ''
        # Check for any event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                # Change the key pressed function
                key_pressed = event.key
        # If not pressed any key, then the key_pressed would be '' (empty string which would return no_op)
        # Get the current action name based on the key pressed by the user
        agent_action_name = self.get_key_action(key_pressed)
        # Get the corresponding action (a number)
        agent_action = self.get_agent().get_action_from_action_name(agent_action_name)
        # Construct the agent list
        agent_list = [[self.get_agent(), 'human', agent_action]]
        return agent_list

    def play_game(self):
        white = [255, 255, 255]
        screen, clock, font = self.init_game()
        # Counter to represent the seconds
        counter = 0
        # Draw all the environment objects
        self.draw_game(screen, [(self.get_agent(), 'human', None)])
        # Update the screen to reflect the changes
        self.update_game_display()

        # Have the game run till the agent has not crashed
        while not self.get_agent().has_crashed():
            # Reset the screen
            screen.fill(white)
            # handle the user action and update the agent/game accordingly
            agent_list = self.handle_user_action()
            # Updating the game based on what was returned after processing the user action
            self.update_game(agent_list)
            # Print elapsed time
            if counter % 60 == 0:
                print('Seconds Elapsed:', counter // 60)
                # Update the environment statistics (add obstacles, increase level, increase score)
                self.update_environment_statistics()
            counter += 1
            # Draw all the environment objects
            self.draw_game(screen, agent_list)
            # Display the updated game statistics
            self.display_game_statistics(screen, font)
            # Update the game display
            self.update_game_display()
            # Tick the clock
            clock.tick(60)

        # If the agent has crashed Update the screen
        # Reset the screen
        screen.fill(white)
        # Display game statistics
        self.display_game_statistics(screen, font)
        # Display game over message
        self.display_game_over_message(screen, font)
        # Update the game display
        self.update_game_display()
        # Handle the game over
        self.handle_game_over()


class GeneticAlgorithmGame(Game):
    def __init__(self, agents, max_iterations, environment, num_best_agents=10):
        super(GeneticAlgorithmGame, self).__init__(environment)
        self.__agents = agents
        self.__population_size = len(self.get_agents())
        self.__max_iterations = max_iterations
        self.__best_agents = list([(-1000, agent) for agent in self.__agents[:num_best_agents]])
        # self.__best_agents = []

    def get_best_agents(self):
        return self.__best_agents

    def set_best_agents(self, new_best_agents):
        self.__best_agents = new_best_agents

    def get_agents(self):
        return self.__agents

    def set_agents(self, agents):
        self.__agents = agents

    def get_population_size(self):
        return self.__population_size

    def get_maximum_iterations(self):
        return self.__max_iterations

    def set_population_size(self, population_size):
        self.__population_size = population_size

    def set_maximum_iterations(self, max_iterations):
        self.__max_iterations = max_iterations

    @staticmethod
    def mutate_weights(weight_array: np.ndarray):
        mutated_weights = np.array(weight_array)
        shape_x, shape_y = mutated_weights.shape
        mask = np.random.choice([True, False], size=shape_x*shape_y, p=[0.3, 0.7]).reshape(shape_x, shape_y)
        mutated_weights[mask] = np.random.randn(np.sum(mask))
        return mutated_weights

    @staticmethod
    def row_reproduction(weights_1_array: np.ndarray, weights_2_array: np.ndarray):
        num_rows = weights_1_array.shape[0]
        row_order = np.random.permutation(range(num_rows))
        weights_1_num_rows = np.random.choice(range(1, num_rows))
        new_weights = np.zeros(weights_1_array.shape)
        new_weights[row_order[:weights_1_num_rows]] = weights_1_array[row_order[:weights_1_num_rows]]
        new_weights[row_order[weights_1_num_rows:]] = weights_2_array[row_order[weights_1_num_rows:]]
        return new_weights

    @staticmethod
    def column_reproduction(weights_1_array: np.ndarray, weights_2_array: np.ndarray):
        num_columns = weights_1_array.shape[1]
        column_order = np.random.permutation(range(num_columns))
        weights_1_num_columns = np.random.choice(range(1, num_columns))
        new_weights = np.zeros(weights_1_array.shape)
        new_weights[:, column_order[:weights_1_num_columns]] = weights_1_array[:, column_order[:weights_1_num_columns]]
        new_weights[:, column_order[weights_1_num_columns:]] = weights_2_array[:, column_order[weights_1_num_columns:]]
        return new_weights

    @staticmethod
    def element_reproduction(weights_1_array: np.ndarray, weights_2_array: np.ndarray):
        shape_x, shape_y = weights_1_array.shape
        mask_prob = np.random.rand(1)[0]
        mask = np.random.choice([True, False], size=shape_x * shape_y,
                                p=[mask_prob, 1-mask_prob]).reshape(shape_x, shape_y)
        new_weights = np.zeros(weights_1_array.shape)
        new_weights[mask] = weights_1_array[mask]
        new_weights[~mask] = weights_2_array[~mask]
        return new_weights

    @staticmethod
    def addition_reproduction(weights_1_array: np.ndarray, weights_2_array: np.ndarray):
        weights_1_coeff, weights_2_coeff = np.random.choice([1, -1], 1), np.random.choice([1, -1], 1)
        return (weights_1_coeff * weights_1_array) + (weights_2_coeff * weights_2_array)

    @staticmethod
    def should_stop_game(agents):
        return all([agent.has_crashed() for agent in agents])

    def get_all_reproduction_functions(self):
        return [self.row_reproduction, self.column_reproduction,
                self.element_reproduction, self.addition_reproduction]

    def get_child(self, agent_1: GeneticAlgorithmAgent, agent_2: GeneticAlgorithmAgent, mutation_prob=0.3):
        all_reproduction_function = self.get_all_reproduction_functions()
        reproduction_function = np.random.choice(all_reproduction_function, 1)[0]
        new_agent = GeneticAlgorithmAgent(reproduction_function(agent_1.get_weights(), agent_2.get_weights()))
        if np.random.rand(1) < mutation_prob:
            new_agent.set_weights(self.mutate_weights(new_agent.get_weights()))
        return new_agent

    def get_top_k_agents(self, agents, k=10):
        agents_rewards = np.array([agent.get_total_reward() for agent in agents])
        top_k_agents = list(np.array(agents)[np.argsort(agents_rewards)[:k]])
        return top_k_agents

    def get_reproduction_population(self, agents, reproduction_population_size):
        k = len(agents)//3
        reproduced_agents = []
        agents_rewards = np.array([agent.get_total_reward() for agent in agents])
        top_k_agents = list(np.array(agents)[np.argsort(agents_rewards)[:k]])
        top_k_agents_rewards = agents_rewards[np.argsort(agents_rewards)[:k]]
        top_k_agents_probabilities = GeneticAlgorithmAgent.softmax_activation(top_k_agents_rewards)
        # print(top_k_agents_rewards)
        for _ in range(reproduction_population_size):
            reproduced_agents.append(self.get_child(*np.random.choice(top_k_agents, size=2,
                                                                      p=top_k_agents_probabilities,
                                                                      replace=False)))
        return reproduced_agents

    def get_new_population(self, agents, reproduction_factor=0.90):
        sample_agent = agents[0]
        best_agents = [agent for _, agent in self.get_best_agents()]
        # best_agents = []
        reproduction_population = len(agents) - len(best_agents)
        reproduced_population = \
            self.get_reproduction_population(agents, int(reproduction_factor*reproduction_population))

        random_population = [GeneticAlgorithmAgent(np.random.randn(*sample_agent.get_weights().shape)) for _ in
                             range(reproduction_population - len(reproduced_population))]

        new_population = best_agents + reproduced_population + random_population
        return new_population

    def get_environment_state(self, agent):
        environment = self.get_environment()
        width, height = environment.get_environment_width(), environment.get_environment_height()

        all_cacti = environment.get_all_cacti()
        closest_cactus_distance = 1 - (all_cacti[0].get_x_pos() if len(all_cacti) > 0 else width) / width
        closest_cactus_width = (all_cacti[0].get_width() if len(all_cacti) > 0 else 0) / width

        all_birds = environment.get_all_birds()
        closest_bird_distance = 1 - (all_birds[0].get_x_pos() if len(all_birds) > 0 else width) / width
        closest_bird_height = 1 - (all_birds[0].get_y_pos() if len(all_birds) > 0 else height) / height

        level = environment.get_current_level()
        # TODO: Add level as part of the environment state

        return np.array([1, agent.get_current_action()/4, 0,
                         closest_cactus_distance, closest_cactus_width,
                         closest_bird_distance, closest_bird_height])

    def get_agent_list(self, agents):
        return [[agent, 'genetic', self.get_environment_state(agent)] for agent in agents]

    def update_best_agents(self, agents):
        k = len(self.get_best_agents())
        agents_rewards = np.array([agent.get_total_reward() for agent in agents])
        top_k_agents = list(np.array(agents)[np.argsort(agents_rewards)[:k]])
        top_k_agents = [(agent.get_total_reward(), agent) for agent in top_k_agents]
        all_top_agents = list(list(self.get_best_agents()) + list(top_k_agents))
        new_best_agents = heapq.nlargest(len(self.get_best_agents()), all_top_agents, key=lambda x: x[0])
        self.set_best_agents(new_best_agents)

    def save_top_k_agent_weights(self, agents, weight_save_directory_path, k=10):
        if check_output_directory(weight_save_directory_path, True):
            agents_rewards = np.array([agent.get_total_reward() for agent in agents])
            top_k_agents = list(np.array(agents)[np.argsort(agents_rewards)[:k]])
            for k, agent in enumerate(top_k_agents):
                file_name = construct_path(weight_save_directory_path,
                                           f'agent_{k}_reward_{agent.get_total_reward()}_weights.npy')
                np.save(file_name, agent.get_weights())

    def run_iteration(self, visualize):
        white = [255, 255, 255]
        screen, clock, font = None, None, None

        if visualize:
            screen, clock, font = self.init_game()
        # Counter to represent the seconds
        counter = 0

        if visualize:
            # Draw all the environment objects
            self.draw_game(screen, self.get_agent_list(self.get_agents()))
            # Update the screen to reflect the changes
            self.update_game_display()

        # Have the game run till all the agents have not crashed
        while not self.should_stop_game(self.get_agents()):
            if visualize:
                # Reset the screen
                screen.fill(white)
            # handle the user action and update the agent/game accordingly
            agent_list = self.get_agent_list(self.get_agents())
            # Updating the game based on what was returned after processing the user action
            self.update_game(agent_list)
            # Print elapsed time
            if counter % 45 == 0:
                # print('Seconds Elapsed:', counter // 60)
                # Update the environment statistics (add obstacles, increase level, increase score)
                self.update_environment_statistics()
            counter += 1
            if visualize:
                # Draw all the environment objects
                self.draw_game(screen, agent_list)
                # Display the updated game statistics
                self.display_game_statistics(screen, font)
                # Update the game display
                self.update_game_display()
                # Tick the clock
                clock.tick(60)

        # If the agent has crashed Update the screen
        if visualize:
            # Reset the screen
            screen.fill(white)
            # Display game statistics
            self.display_game_statistics(screen, font)
            # Display game over message
            self.display_game_over_message(screen, font)
            # Update the game display
            self.update_game_display()
        # # Handle the game over
        # self.handle_game_over()

    def play_game(self, visualize=False, weights_parent_directory=f'../data/genetic_algorithm_weights/'):
        iteration_num = 0
        for iteration_num in range(self.get_maximum_iterations()):
            self.get_environment().reset_environment()
            print(f'Iteration: {iteration_num}')
            self.run_iteration(visualize)
            print(f'Score: {self.get_environment().get_current_score()}')
            self.update_best_agents(self.get_agents())
            print([agent_reward for agent_reward, _ in self.get_best_agents()])
            if self.get_maximum_iterations() > 1:
                if iteration_num % 10 == 0:
                    weights_save_directory_path = construct_path(weights_parent_directory, f'iteration_{iteration_num}')
                    self.save_top_k_agent_weights(self.get_agents(), weights_save_directory_path)
                new_population = self.get_new_population(self.get_agents())
                self.set_agents(new_population)

        weights_save_directory_path = construct_path(weights_parent_directory, f'iteration_{iteration_num}')
        self.save_top_k_agent_weights(self.get_agents(), weights_save_directory_path)

        if visualize:
            pygame.quit()

        best_agents_weights_save_directory_path = construct_path(weights_parent_directory, f'best_agents')
        best_agents = [agent for _, agent in self.get_best_agents()]
        self.save_top_k_agent_weights(best_agents, best_agents_weights_save_directory_path, k=len(best_agents))


class QLearningGame(Game):
    def __init__(self, agent: QLearningAgent, environment, q_function, max_iterations=100, gamma=0.9, alpha=0.2):
        super(QLearningGame, self).__init__(environment)
        self.__agent = agent
        self.__max_iterations = max_iterations
        self.__gamma = gamma
        self.__alpha = alpha
        self.__q_function = q_function

    def get_maximum_iterations(self):
        return self.__max_iterations

    def get_q_function(self):
        return self.__q_function

    def set_q_function(self, new_q_function):
        self.__q_function = new_q_function

    def get_alpha(self):
        return self.__alpha

    def get_agent(self):
        return self.__agent

    def get_gamma(self):
        return self.__gamma

    def get_best_action(self, state):
        return np.argmax(self.get_q_function()[state])

    def update_q_function(self, old_environment_state, new_environment_state):
        agent_action = self.get_agent().get_current_action()
        old_state_current_action_q_value = self.__q_function[(*old_environment_state, agent_action)]
        agent_action_reward = self.get_agent().get_current_action_reward()
        new_state_best_action = self.get_best_action(new_environment_state)
        new_state_best_action_q_value = self.get_q_function()[(*new_environment_state, new_state_best_action)]
        self.__q_function[(*old_environment_state, agent_action)] = old_state_current_action_q_value + \
                self.get_alpha()*(agent_action_reward + self.get_gamma()*new_state_best_action_q_value - old_state_current_action_q_value)

    @staticmethod
    def discretize_agent_speed(speed):
        if speed < 8:
            return 0 # Low speed
        elif speed < 14:
            return 1 # medium speed
        else:
            return 2 # high speed

    @staticmethod
    def discretize_y_coordinate(y_cor):
        if y_cor < 10:
            return 0
        elif y_cor < 90:
            return 1
        elif y_cor < 200:
            return 2
        else:
            return 3

    @staticmethod
    def discretize_x_coordinate_wrt_agent(agent, closest_obstacle):
        agent_end_x_coordinate = agent.get_x_pos() + agent.get_width()
        obstacle_x_coordinate = closest_obstacle.get_x_pos()
        if obstacle_x_coordinate < agent_end_x_coordinate:
            return 0
        elif obstacle_x_coordinate < agent_end_x_coordinate + 100:
            return 0
        elif obstacle_x_coordinate < agent_end_x_coordinate + 200:
            return 1
        else:
            return 2

    @staticmethod
    def discretize_obstacle_width(obstacle_width):
        if obstacle_width <= 50:
            return 0
        elif obstacle_width <= 100:
            return 1
        else:
            return 2

    @staticmethod
    def discretize_agent_state(agent):
        if agent.is_walking():
            return 0
        elif agent.is_jumping():
            return 1
        else:
            return 2

    def get_environment_state(self):
        """
        The environment state is a tuple representing the state of the environment and current value of the agent.
        The state is as follows:
            * Index 0: The discretized speed of the agent (low, medium, high) - 3
            ### NOT Anymore * Index 1: The height of the agent (ground, low, medium, high) - 3 ###
            * Index 1: Current state of the agent (walk, jump, duck)
            * Index 2: The distance to the closest obstacle. (very_near, near, in_sight, very_near, near,
            in_sight, not_in_sight) - 7
                       for both cactus and bird (3 X 2) + 1
            * Index 3: Distance between the two closest obstacles (very near, ok, just not there) - 3
            * Index 4: The length of the obstacle (small, medium, large) - 3
            * Index 5: The y_position of the obstacle (ground, low, medium, high) - 4
        :return:
        """
        agent = self.get_agent()
        agent_speed = self.discretize_agent_speed(agent.get_x_vel())
        # agent_height = self.discretize_y_coordinate(agent.get_y_pos())
        agent_state = self.discretize_agent_state(agent)

        environment = self.get_environment()
        sorted_obstacles = environment.get_objects_sorted_by_distance()
        closest_obstacle_distance = -1      # essentially acting as not in sight
        within_obstacle_distance = -1
        closest_obstacle_width = 0
        closest_obstacle_y_cor = 0
        if len(sorted_obstacles) > 0:
            closest_obstacle_type, closest_obstacle_x_cor, closest_obstacle = sorted_obstacles[0]
            closest_obstacle_distance = self.discretize_x_coordinate_wrt_agent(agent, closest_obstacle)
            if closest_obstacle_type == 'b':
                closest_obstacle_distance += 3
            closest_obstacle_width = self.discretize_obstacle_width(closest_obstacle.get_width())
            closest_obstacle_y_cor = self.discretize_y_coordinate(closest_obstacle.get_y_pos())
            # Check for within distance
            if len(sorted_obstacles) > 1:
                _, second_closest_obstacle_x_cor, _ = sorted_obstacles[1]
                if second_closest_obstacle_x_cor - (closest_obstacle_x_cor + closest_obstacle.get_width()) < 200:
                    within_obstacle_distance = 0
                else:
                    within_obstacle_distance = 1

        return agent_speed, agent_state, closest_obstacle_distance, within_obstacle_distance, \
               closest_obstacle_width, closest_obstacle_y_cor

    def save_q_function(self, weight_save_directory_path, iteration_num):
        if check_output_directory(weight_save_directory_path, False):
            file_name = construct_path(weight_save_directory_path, f'q_func_{iteration_num}.npy')
            np.save(file_name, self.get_q_function())

    def get_agent_list(self):
        return [(self.get_agent(), 'q', self.get_environment_state())]

    def update_game_agents_state(self, agent_list):
        for agent_information in agent_list:
            agent = agent_information[0]
            if not agent.has_crashed():
                self.update_agent_state(*agent_information)
                agent.update(self.get_q_function())

    def run_iteration(self, visualize):
        white = [255, 255, 255]
        screen, clock, font = None, None, None

        if visualize:
            screen, clock, font = self.init_game()
        # Counter to represent the seconds
        counter = 0

        if visualize:
            # Draw all the environment objects
            self.draw_game(screen, self.get_agent_list())
            # Update the screen to reflect the changes
            self.update_game_display()

        # Have the game run till all the agents have not crashed
        while not self.get_agent().has_crashed():
            if visualize:
                # Reset the screen
                screen.fill(white)
            # Get the old environment state before letting the agent do the action
            old_environment_state = self.get_environment_state()
            # handle the user action and update the agent/game accordingly
            agent_list = self.get_agent_list()
            # Updating the game based on what was returned after processing the user action
            self.update_game(agent_list)
            # Get the new environment state after the agent has taken action
            new_environment_state = self.get_environment_state()
            self.update_q_function(old_environment_state, new_environment_state)
            # Print elapsed time
            division = 60 if visualize else 1000
            if counter % division == 0:
                # print('Seconds Elapsed:', counter // 60)
                # Update the environment statistics (add obstacles, increase level, increase score)
                self.update_environment_statistics()
                # print(self.get_agent().get_x_acc(), self.get_agent().get_x_vel())
            counter += 1
            if visualize:
                # Draw all the environment objects
                self.draw_game(screen, agent_list)
                # Display the updated game statistics
                self.display_game_statistics(screen, font)
                # Update the game display
                self.update_game_display()
                # Tick the clock
                clock.tick(60)

        # If the agent has crashed Update the screen
        if visualize:
            # Reset the screen
            screen.fill(white)
            # Display game statistics
            self.display_game_statistics(screen, font)
            # Display game over message
            self.display_game_over_message(screen, font)
            # Update the game display
            self.update_game_display()
        # # Handle the game over
        # self.handle_game_over()

    def play_game(self, visualize=False, weights_parent_directory=f'../data/q_learning/'):
        iteration_num = 0
        for iteration_num in range(self.get_maximum_iterations()):
            self.get_environment().reset_environment()
            self.get_agent().reset_agent()
            self.run_iteration(visualize)
            print(f'Iteration: {iteration_num+1}', f'Score: {self.get_environment().get_current_score()}')
            if iteration_num % 50 == 0:
                self.save_q_function(weights_parent_directory, iteration_num)

        self.save_q_function(weights_parent_directory, iteration_num)

        if visualize:
            pygame.quit()


if __name__ == '__main__':
    ###############################################################
    #                           HUMAN GAME                        #
    ###############################################################
    # init_agent = Dinosaur()
    # my_game = HumanGame(init_agent, ChromeTRexRush())
    # my_game.play_game()

    ###############################################################
    #                       GENETIC ALGORITHM                     #
    ###############################################################
    # population_size = 50
    # init_agents = [GeneticAlgorithmAgent(np.random.randn(4, 7), initial_velocity=(5, 0)) for _ in range(
    #     population_size)]
    # my_game = GeneticAlgorithmGame(init_agents, 31, ChromeTRexRush(bird_add_threshold=1))
    # my_game.play_game(True)

    ###############################################################
    #                           Q LEARNING                        #
    ###############################################################
    init_agent = QLearningAgent()
    my_game = QLearningGame(init_agent, ChromeTRexRush(bird_add_threshold=-1), np.zeros((3, 3, 7, 3, 3, 4, 4)),
                            max_iterations=1000)
    my_game.play_game(True)
    print('End of Main!')
