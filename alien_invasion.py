import sys
import random
import pygame
from settings import Settings


def main():
    pygame.init()
    settings = Settings()
    WIDTH, HEIGHT = settings.screen_width, settings.screen_height
    FPS = 60

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Alien invasion')
    clock = pygame.time.Clock()

    # Create background surface with black and small white 'stars'
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(settings.bg_color)

    # Generate starfield: positions and sizes
    num_stars = 300
    stars = []
    for _ in range(num_stars):
        x = random.randrange(0, WIDTH)
        y = random.randrange(0, HEIGHT)
        size = random.randint(1, 3)
        stars.append((x, y, size))

    for x, y, size in stars:
        if size == 1:
            bg.set_at((x, y), (255, 255, 255))
        else:
            pygame.draw.circle(bg, (255, 255, 255), (x, y), size // 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(bg, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
