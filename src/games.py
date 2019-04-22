import pygame
from visualizer import GUI


class HumanGame:
	def __init__(self, agent, environment):
		self.__agent = agent
		self.__environment = environment
		self.__env_gui = GUI(self.get_environment().get_environment_height())

	def get_agent(self):
		return self.__agent

	def get_environment(self):
		return self.__environment

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

	def play(self):
		pygame.init()
		pygame.font.init()  # you have to call this at the start,
		# if you want to use this module.
		myfont = pygame.font.SysFont('Comic Sans MS', 20)
		screen = pygame.display.set_mode((self.get_environment_width(), self.get_environment_height()))
		screen.fill((255, 255, 255))
		pygame.display.update()
		clock = pygame.time.Clock()
		counter = 0
		self.draw_environment_objects(screen)
		pygame.display.update()
		pygame.key.set_repeat(100, 1)

		while not self.get_agent().has_crashed():
			screen.fill((255, 255, 255))
			key_down = False
			# Check for any event
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					return
				if event.type == pygame.KEYDOWN:
					key_down = True
					self.update_environment(
						self.get_agent().get_action_from_action_name(self.get_key_action(event.key)))
			if not key_down:
				self.update_environment(0)

			if counter % 60 == 0:
				print('Seconds Elapsed:', counter // 60)
				print(len(self.get_all_cacti()))
				# Add an obstacle
				self.add_obstacle()
				# Increase the Score
				self.increase_score()
				# Increase the level if needed
				self.increase_level()

			counter += 1
			self.draw_environment_objects(screen)
			screen.blit(myfont.render(f'Level: {self.get_current_level()}', False, (0, 0, 0)), (0, 0))
			screen.blit(
				myfont.render(f'Score: {self.get_current_score()}, Reward: {np.round(self.get_total_reward(), 3)}',
				              False, (0, 0, 0)), (self.get_environment_width() - 300, 0))
			pygame.display.update()

			clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return
		pygame.quit()