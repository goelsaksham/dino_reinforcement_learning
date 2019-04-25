"""
Define the environment for the game
"""
import numpy as np

from arena_objects.obstacles import Bird, Cactus


class ChromeTRexRush:
    def __init__(self, environment_width=800, environment_height=400,
                 level_threshold=15, high_score_file_path=f'../../data/high_score.txt',
                 bird_add_threshold=1):
        self.__environment_width, self.__environment_height = environment_width, environment_height
        self.__cacti = []
        self.__birds = []
        self.__level = 0
        self.__level_increase_threshold = level_threshold
        self.__velocity_increase = 0
        self.__need_to_increase_velocity = False
        self.__score = 0
        self.__high_score_file_path = high_score_file_path
        self.__high_score = self.load_high_score()
        self.__bird_add_threshold = bird_add_threshold

    def get_bird_add_threshold(self):
        return self.__bird_add_threshold

    def reset_environment(self):
        self.__cacti = []
        self.__birds = []
        self.__level = 0
        self.__velocity_increase = 0
        self.__need_to_increase_velocity = False
        self.__score = 0

    def get_high_score_file_path(self):
        return self.__high_score_file_path

    def load_high_score(self):
        try:
            with open(self.get_high_score_file_path(), 'r') as high_score_file:
                return int(high_score_file.read())
        except FileNotFoundError:
            return 0

    def get_environment_width(self):
        return self.__environment_width

    def get_environment_height(self):
        return self.__environment_height

    def get_current_level(self):
        return self.__level

    def set_current_level(self, new_level):
        self.__level = new_level

    def increase_score(self, increase_by=1):
        self.__score += increase_by

    def get_current_score(self):
        return self.__score

    def get_high_score(self):
        return self.__high_score

    def update_high_score(self):
        try:
            with open(self.get_high_score_file_path(), 'w') as high_score_file:
                high_score_file.write(f'{self.get_high_score()}')
        except FileNotFoundError:
            return

    def get_all_cacti(self):
        return self.__cacti

    def get_all_birds(self):
        return self.__birds

    def get_last_cactus(self):
        if self.get_all_cacti():
            return self.get_all_cacti()[-1]
        else:
            return None

    def get_last_bird(self):
        if self.get_all_birds():
            return self.get_all_birds()[-1]
        else:
            return None

    def should_add(self, x):
        from scipy.stats import expon
        offset = np.random.choice([50, 100, 150, 200, 250, 300], 1)
        if x < self.get_environment_width() - offset:
            return np.random.rand(1) * 2.0 < expon().cdf((self.get_environment_width() - x) * 4 /
                                                       self.get_environment_width())
        else:
            return False

    def get_velocity_increase(self):
        return self.__velocity_increase

    def add_cactus(self):
        if self.get_all_cacti():
            # make sure that the last cactus is at least entirely visible in the environment
            last_cactus = self.get_last_cactus()
            # print(last_cactus.get_x_pos())
            if last_cactus.get_x_pos() + last_cactus.get_width() < self.get_environment_width():
                if self.should_add(last_cactus.get_x_pos() + last_cactus.get_width()):
                    cactus = Cactus((self.get_environment_width(), 0))
                    self.__cacti.append(cactus)
                    return True
        else:
            # 90% chance
            if np.random.rand(1) < 0.95:
                cactus = Cactus((self.get_environment_width(), 0))
                self.__cacti.append(cactus)
                return True

    def add_bird(self):
        if self.get_all_birds():
            # make sure that the last cactus is at least entirely visible in the environment
            last_bird = self.get_last_bird()
            if last_bird.get_x_pos() + last_bird.get_width() < self.get_environment_width():
                if self.should_add(last_bird.get_x_pos()):
                    bird = Bird((self.get_environment_width(), 50))
                    self.__birds.append(bird)
                    return True
        else:
            # 90% chance
            if np.random.rand(1) < 0.95:
                bird = Bird((self.get_environment_width(), 50))
                self.__birds.append(bird)
                return True

    def add_obstacle(self):
        if self.get_current_level() > self.get_bird_add_threshold():
            # try to add either bird or cactus
            if np.random.rand(1) < 0.8:
                self.add_cactus()
            else:
                self.add_bird()
        else:
            self.add_cactus()

    def get_level_increase_threshold(self):
        return self.__level_increase_threshold

    def increase_level(self):
        if self.get_current_score() >= self.get_level_increase_threshold() * (self.get_current_level() + 1):
            self.__level += 1

    def remove_out_of_environment_obstacles(self):
        # Find the first cactus which is still in environment. Remove all cactus before it
        remove_counter = 0
        for cactus in self.get_all_cacti():
            if cactus.get_x_pos() + cactus.get_width() < 0:
                remove_counter += 1
            else:
                break
        self.__cacti = self.__cacti[remove_counter:]
        # Find the first bird which is still in environment. Remove all cactus before it
        remove_counter = 0
        for bird in self.get_all_birds():
            if bird.get_x_pos() + bird.get_width() < 0:
                remove_counter += 1
            else:
                break
        self.__birds = self.__birds[remove_counter:]

    def get_all_obstacle_list(self):
        return self.get_all_cacti() + self.get_all_birds()

    def get_closest_obstacle(self):
        cacti = self.get_all_cacti()
        birds = self.get_all_birds()
        if len(cacti) == 0 and len(birds) == 0:
            return None
        else:
            if len(cacti) == 0:
                return birds[0]
            elif len(birds) == 0:
                return cacti[0]
            else:
                if cacti[0].get_x_pos() < birds[0].get_x_pos():
                    return cacti[0]
                else:
                    return birds[0]

    def update_obstacles(self, agent_x_velocity=0):
        for obstacle in self.get_all_obstacle_list():
            # print(obstacle.get_x_pos())
            obstacle.update(agent_x_velocity)

    def update_environment(self, agent_x_velocity=0):
        # update the obstacles
        self.update_obstacles(agent_x_velocity)
        # Remove the obstacles which are out of the environment
        self.remove_out_of_environment_obstacles()
