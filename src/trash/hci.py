"""
This is a human computer interaction script. It takes the action performed by the user in form of the keyboard press
and converts it into the action of the objects
"""

"""import pygame
pygame.init()
pygame.display.set_mode()
from arena_objects.dinosaur import Dinosaur
import time
import matplotlib.pyplot as plt

def main():
	my_dinosaur = Dinosaur(obj_acc=(0.1, -0.25))
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
		        pygame.quit(); #sys.exit() if sys is imported
		    if event.type == pygame.KEYDOWN:
		        if event.key == pygame.K_0:
		            print("Hey, you pressed the key, '0'!")
		        if event.key == pygame.K_1:
		            print("Doing whatever")


if __name__ == '__main__':
    main()
"""
import time

import matplotlib.pyplot as plt
import pygame
from arena_objects.agent import Dinosaur


def main():
    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    clock = pygame.time.Clock()
    counter, text = 20, '200'.rjust(3)
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    font = pygame.font.SysFont('Consolas', 30)
    my_dinosaur = Dinosaur(object_acceleration=(0.1, -0.25))
    # x_cors = range(counter)
    y_cors = []
    keep_alive = True
    while keep_alive:
        for e in pygame.event.get():
            if e.type == pygame.USEREVENT:
                counter -= 1
                text = str(counter).rjust(3) if counter > 0 else 'boom!'
                keep_alive = counter >= 0
                my_dinosaur.update('')
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_j:
                    my_dinosaur.update('j')
                elif e.key == pygame.K_d:
                    my_dinosaur.update('d')
                else:
                    my_dinosaur.update('')
            elif e.type == pygame.QUIT:
                break
            y_cors.append(my_dinosaur.get_y_pos() - 1 if my_dinosaur.is_ducking() else my_dinosaur.get_y_pos())
        else:
            screen.fill((255, 255, 255))
            screen.blit(font.render(text, True, (0, 0, 0)), (32, 48))
            pygame.display.flip()
            clock.tick(60)
            continue
        break
    plt.plot(range(len(y_cors)), y_cors)
    plt.show()


if __name__ == '__main__':
    main()
