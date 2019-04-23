import pygame

from arena.environments import ChromeTRexRush
from arena_objects.agent import *
from visualizer import GUI


class HumanGame:
    def __init__(self, agent, environment):
        self.__agent = agent
        self.__environment = environment
        print(self.get_environment())
        self.__env_gui = GUI(self.get_environment().get_environment_height())

    def get_agent(self):
        return self.__agent

    def get_environment(self):
        return self.__environment

    def get_environment_gui(self):
        return self.__env_gui

    def update_agent(self, action_name):
        self.get_agent().update(action_name)

    @staticmethod
    def get_key_map():
        return {pygame.K_UP: 'high_jump', pygame.K_SPACE: 'high_jump', pygame.K_DOWN: 'duck',
                pygame.K_d: 'duck', pygame.K_l: 'low_jump', pygame.K_s: 'low_jump'}

    def get_key_action(self, key_pressed):
        try:
            return self.get_key_map()[key_pressed]
        except KeyError:
            return 'no_op'

    def update_game(self, agent_action):
        # Set the action of the agent
        self.get_agent().set_current_action(agent_action)
        # Update the agents
        self.update_agent(self.get_agent().get_current_action_name())
        # Update the Environment
        self.get_environment().update_environment()
        # Get all the obstacles
        all_obstacles = self.get_environment().get_all_obstacle_list()
        if self.get_agent().has_collided_with_obstacle(all_obstacles):
            self.get_agent().set_crashed(True)
        # Check whether the agent has collided with an obstacle before calculating the reward
        self.get_agent().increase_reward(self.get_agent().get_current_action_reward())

    def draw_game_objects(self, screen):
        # Draw all the environment objects
        self.get_environment_gui().draw_environment_objects(screen, self.get_agent(),
                                                            self.get_environment().get_all_obstacle_list())

    def play(self):
        # initialize the pygame module and font
        pygame.init()
        pygame.font.init()
        # get the font for the score
        myfont = pygame.font.SysFont('Comic Sans MS', 20)

        # Initialize the screen
        screen = pygame.display.set_mode((self.get_environment().get_environment_width(),
                                          self.get_environment().get_environment_height()))
        WHITE = (255, 255, 255)
        screen.fill(WHITE)
        # Initialize the clock for the game
        clock = pygame.time.Clock()
        # Draw all the environment objects
        self.draw_game_objects(screen)
        # Update the pygame screen to reflect the changes
        pygame.display.update()
        # Set the key repeat for the Duck command
        pygame.key.set_repeat(50, 1)
        # Counter to represent the seconds
        counter = 0
        # Have the game run till the agent has not crashed
        while not self.get_agent().has_crashed():
            # Reset the screen
            screen.fill(WHITE)
            key_down = False
            # Check for any event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    key_down = True
                    self.update_game(self.get_agent().get_action_from_action_name(self.get_key_action(event.key)))
            # If not pressed any key, just let the agent be in the simple no_op state
            if not key_down:
                self.update_game(self.get_agent().get_action_from_action_name(self.get_key_action(None)))

            if counter % 60 == 0:
                print('Seconds Elapsed:', counter // 60)
                # Add an obstacle
                self.get_environment().add_obstacle()
                # Increase the Score
                self.get_environment().increase_score()
                # Increase the level if needed
                self.get_environment().increase_level()

            counter += 1

            # Draw all the environment objects
            self.draw_game_objects(screen)
            # Update the scoreboard
            BLACK = [0, 0, 0]
            screen.blit(myfont.render(f'Level: {self.get_environment().get_current_level()}', False, BLACK), (0, 0))
            screen.blit(myfont.render(f'Score: {self.get_environment().get_current_score()}', False, BLACK),
                        (self.get_environment().get_environment_width() - 100, 0))
            # Reward: {np.round(self.get_total_reward(), 3)}
            pygame.display.update()

            clock.tick(60)

        # If the agent has crashed Update the screen
        # Reset the screen
        screen.fill(WHITE)
        # Update the scoreboard
        BLACK = [0, 0, 0]
        screen.blit(myfont.render(f'Level: {self.get_environment().get_current_level()}', False, BLACK), (0, 0))
        screen.blit(myfont.render(f'Score: {self.get_environment().get_current_score()}', False, BLACK),
                    (self.get_environment().get_environment_width() - 100, 0))
        screen.blit(myfont.render(f'Game Over!!!', False, BLACK),
                    (self.get_environment().get_environment_width() / 2 - 50,
                     self.get_environment().get_environment_height() / 2 - 20))
        pygame.display.update()

        while True:
            # Wait for the user to exit the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
        pygame.quit()


class GA_Game():
    def __init__(self, agent, environment):
        self.__agent = agent
        self.__environment = environment
        print(self.get_environment())
        self.__env_gui = GUI(self.get_environment().get_environment_height())

    def get_agent(self):
        return self.__agent

    def get_environment(self):
        return self.__environment

    def get_environment_gui(self):
        return self.__env_gui

    def update_agent(self, environment_state):
        self.get_agent().update(environment_state)

    def get_environment_state(self):
        import numpy as np
        environment = self.get_environment()
        w, h = environment.get_environment_width(), environment.get_environment_height()

        cacti = environment.get_all_cacti()
        closest_cactus_distance = cacti[0].get_x_pos() if len(cacti) > 0 else w
        closest_cactus_distance = closest_cactus_distance / w
        closest_cactus_width = cacti[0].get_width() if len(cacti) > 0 else 0
        closest_cactus_width = closest_cactus_width / w

        birds = environment.get_all_birds()
        closest_bird_distance = birds[0].get_x_pos() if len(birds) > 0 else w
        closest_bird_distance = closest_bird_distance / w
        closest_bird_height = birds[0].get_y_pos() if len(birds) > 0 else h
        closest_bird_height = closest_bird_height / h

        level = environment.get_current_level()

        num_obstacles = len(cacti) + len(birds)

        return np.array([num_obstacles, closest_cactus_distance, closest_cactus_width, closest_bird_distance,
                         closest_bird_height, level])

    def update_game(self, environment_state):
        # Update the agents
        self.update_agent(environment_state)
        # Update the Environment
        self.get_environment().update_environment()
        # Get all the obstacles
        all_obstacles = self.get_environment().get_all_obstacle_list()
        if self.get_agent().has_collided_with_obstacle(all_obstacles):
            self.get_agent().set_crashed(True)
        # Check whether the agent has collided with an obstacle before calculating the reward
        self.get_agent().increase_reward(self.get_agent().get_current_action_reward())

    def draw_game_objects(self, screen):
        # Draw all the environment objects
        self.get_environment_gui().draw_environment_objects(screen, self.get_agent(),
                                                            self.get_environment().get_all_obstacle_list())

    def play(self):
        # initialize the pygame module and font
        pygame.init()
        pygame.font.init()
        # get the font for the score
        myfont = pygame.font.SysFont('Comic Sans MS', 20)

        # Initialize the screen
        screen = pygame.display.set_mode((self.get_environment().get_environment_width(),
                                          self.get_environment().get_environment_height()))
        WHITE = (255, 255, 255)
        screen.fill(WHITE)
        # Initialize the clock for the game
        clock = pygame.time.Clock()
        # Draw all the environment objects
        self.draw_game_objects(screen)
        # Update the pygame screen to reflect the changes
        pygame.display.update()
        # Set the key repeat for the Duck command
        pygame.key.set_repeat(50, 1)
        # Counter to represent the seconds
        counter = 0
        # Have the game run till the agent has not crashed
        while not self.get_agent().has_crashed():
            # Reset the screen
            screen.fill(WHITE)
            # Get the environment state and update the agent
            self.update_game(self.get_environment_state())

            if counter % 60 == 0:
                print('Seconds Elapsed:', counter // 60)
                # Add an obstacle
                self.get_environment().add_obstacle()
                # Increase the Score
                self.get_environment().increase_score()
                # Increase the level if needed
                self.get_environment().increase_level()

            counter += 1

            # Draw all the environment objects
            self.draw_game_objects(screen)
            # Update the scoreboard
            BLACK = [0, 0, 0]
            screen.blit(myfont.render(f'Level: {self.get_environment().get_current_level()}', False, BLACK), (0, 0))
            screen.blit(myfont.render(f'Score: {self.get_environment().get_current_score()}', False, BLACK),
                        (self.get_environment().get_environment_width() - 100, 0))
            # Reward: {np.round(self.get_total_reward(), 3)}
            pygame.display.update()

            clock.tick(60)

        # If the agent has crashed Update the screen
        # Reset the screen
        screen.fill(WHITE)
        # Update the scoreboard
        BLACK = [0, 0, 0]
        screen.blit(myfont.render(f'Level: {self.get_environment().get_current_level()}', False, BLACK), (0, 0))
        screen.blit(myfont.render(f'Score: {self.get_environment().get_current_score()}', False, BLACK),
                    (self.get_environment().get_environment_width() - 100, 0))
        screen.blit(myfont.render(f'Game Over!!!', False, BLACK),
                    (self.get_environment().get_environment_width() / 2 - 50,
                     self.get_environment().get_environment_height() / 2 - 20))
        pygame.display.update()

        while True:
            # Wait for the user to exit the game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
        pygame.quit()


if __name__ == '__main__':
    # my_game = GA_Game(GeneticAlgorithmAgent(np.random.rand(4, 6)), ChromeTRexRush())
    # mat = np.random.randn(4, 6)
    # mat[-1, :] = 1
    # my_game = GA_Game(GeneticAlgorithmAgent(mat), ChromeTRexRush())
    my_game = HumanGame(Dinosaur(), ChromeTRexRush())
    my_game.play()
