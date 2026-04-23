import sys
import random
import pygame
from settings import Settings
from ship import Ship
from settings import Settings
from game import run
import random

settings = Settings()
WIDTH, HEIGHT = settings.screen_width, settings.screen_height
num_stars = 300
stars = [(random.randrange(0, WIDTH), random.randrange(0, HEIGHT), random.randint(1, 3)) for _ in range(num_stars)]

if __name__ == '__main__':
    run(settings, stars)
    sys.exit()


if __name__ == '__main__':
    main()
