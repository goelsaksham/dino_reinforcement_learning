import pygame

from arena.environments import ChromeTRexRush
from arena_objects.agent import *
from visualizer import GUI
from utils.directory_utils import *


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
        # Update the Environment
        self.get_environment().update_environment()
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
    def __init__(self, agents, max_iterations, environment):
        super(GeneticAlgorithmGame, self).__init__(environment)
        self.__agents = agents
        self.__population_size = len(self.get_agents())
        self.__max_iterations = max_iterations

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
        mask = np.random.choice([True, False], size=shape_x*shape_y, p=[0.10, 0.9]).reshape(shape_x, shape_y)
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
        mask = np.random.choice([True, False], size=shape_x * shape_y,
                                p=[0.5, 0.5]).reshape(shape_x, shape_y)
        new_weights = np.zeros(weights_1_array.shape)
        new_weights[mask] = weights_1_array[mask]
        new_weights[~mask] = weights_2_array[~mask]
        return new_weights

    @staticmethod
    def should_stop_game(agents):
        return all([agent.has_crashed() for agent in agents])

    def get_all_reproduction_functions(self):
        return [self.row_reproduction, self.column_reproduction, self.element_reproduction]

    def get_child(self, agent_1: GeneticAlgorithmAgent, agent_2: GeneticAlgorithmAgent, mutation_prob=0.05):
        all_reproduction_function = self.get_all_reproduction_functions()
        reproduction_function = np.random.choice(all_reproduction_function, 1)[0]
        new_agent = GeneticAlgorithmAgent(reproduction_function(agent_1.get_weights(), agent_2.get_weights()))
        if np.random.rand(1) < mutation_prob:
            new_agent.set_weights(self.mutate_weights(new_agent.get_weights()))
        return new_agent

    def get_reproduction_population(self, agents, reproduction_population_size):
        reproduced_agents = []
        agents_rewards = np.array([agent.get_total_reward() for agent in agents])
        print(agents_rewards)
        agents_probabilities = GeneticAlgorithmAgent.softmax_activation(agents_rewards)
        print(agents_probabilities)
        for _ in range(reproduction_population_size):
            reproduced_agents.append(self.get_child(*np.random.choice(agents, size=2, p=agents_probabilities,
                                                                      replace=True)))
        return reproduced_agents

    def get_new_population(self, agents, reproduction_factor=0.99):
        sample_agent = agents[0]
        reproduced_population = self.get_reproduction_population(agents, int(reproduction_factor*len(agents)))
        random_population = [GeneticAlgorithmAgent(np.random.randn(*sample_agent.get_weights().shape)) for _ in
                             range(len(agents) - len(reproduced_population))]
        new_population = reproduced_population + random_population
        return new_population

    def get_environment_state(self):
        environment = self.get_environment()
        width, height = environment.get_environment_width(), environment.get_environment_height()

        all_cacti = environment.get_all_cacti()
        closest_cactus_distance = (all_cacti[0].get_x_pos() if len(all_cacti) > 0 else width) / width
        closest_cactus_width = (all_cacti[0].get_width() if len(all_cacti) > 0 else 0) / width

        all_birds = environment.get_all_birds()
        closest_bird_distance = (all_birds[0].get_x_pos() if len(all_birds) > 0 else width) / width
        closest_bird_height = (all_birds[0].get_y_pos() if len(all_birds) > 0 else height) / height

        level = environment.get_current_level()
        num_obstacles = len(all_cacti) + len(all_birds)

        return np.array([num_obstacles, level, closest_cactus_distance, closest_cactus_width,
                         closest_bird_distance, closest_bird_height])

    def get_agent_list(self, agents):
        current_environment_state = self.get_environment_state()
        return [[agent, 'genetic', current_environment_state] for agent in agents]

    def save_top_k_agent_weights(self, agents, weight_save_directory_path, k=10):
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
            # Reset the screen
            screen.fill(white)
            # handle the user action and update the agent/game accordingly
            agent_list = self.get_agent_list(self.get_agents())
            # Updating the game based on what was returned after processing the user action
            self.update_game(agent_list)
            # Print elapsed time
            if counter % 60 == 0:
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
        for iteration_num in range(self.get_maximum_iterations()):
            self.get_environment().reset_environment()
            print(f'Iteration: {iteration_num}')
            self.run_iteration(visualize)
            if self.get_maximum_iterations() > 1:
                try:
                    if iteration_num % 10 == 0:
                        weights_save_directory_path = construct_path(weights_parent_directory, f'iteration_{iteration_num}')
                        check_output_directory(weights_save_directory_path)
                        self.save_top_k_agent_weights(self.get_agents(), weights_save_directory_path)
                except FileNotFoundError:
                    pass
                new_population = self.get_new_population(self.get_agents())
                self.set_agents(new_population)

        try:
            weights_save_directory_path = construct_path(weights_parent_directory, f'iteration_{iteration_num}')
            check_output_directory(weights_save_directory_path)
            self.save_top_k_agent_weights(self.get_agents(), weights_save_directory_path)
        except FileNotFoundError:
            pass

        if visualize:
            pygame.quit()


if __name__ == '__main__':
    ###############################################################
    #                           HUMAN GAME                        #
    ###############################################################
    # agent = Dinosaur()
    # my_game = HumanGame(agent, ChromeTRexRush())

    ###############################################################
    #                       GENETIC ALGORITHM                     #
    ###############################################################
    population_size = 50
    agents = [GeneticAlgorithmAgent(np.random.randn(4, 6)) for _ in range(population_size)]
    my_game = GeneticAlgorithmGame(agents, 10, ChromeTRexRush())
    my_game.play_game(True)
