"""
This is the file that contains the main module that runs the whole arena
"""
from arena_objects.dinosaur import Dinosaur
import time
import matplotlib.pyplot as plt


def main():
	my_dinosaur = Dinosaur(obj_acc=(0.1, -.25))
	timesteps = 200
	x_cors = range(timesteps)
	y_cors = []
	for t in range(timesteps):
		my_dinosaur.update()
		#time.sleep(0.1)
		if t % 7 == 0:
			print('Jumping')
			if not my_dinosaur.is_jumping():
				my_dinosaur.set_vel((my_dinosaur.get_x_vel(), 3))
		print(my_dinosaur.get_x_pos(), my_dinosaur.get_y_pos())
		y_cors.append(my_dinosaur.get_y_pos())
	plt.plot(x_cors, y_cors)
	plt.show()
	print('Hello World')


if __name__ == '__main__':
    main()
