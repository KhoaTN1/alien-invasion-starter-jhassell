import pygame
import random
from settings import Settings
from ship import Ship
from aliens import Alien, get_level_sizes

def main():
    pygame.init()
    settings = Settings()
    WIDTH, HEIGHT = settings.screen_width, settings.screen_height
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # create a small fleet placed so the rightmost alien will hit the edge
    ship = Ship(settings, screen)
    alien_sizes = get_level_sizes(settings, ship)
    w, h = alien_sizes[1]
    group = pygame.sprite.Group()

    count = 5
    spacing = 6
    # place fleet so it's close to the right edge and moving right
    start_x = WIDTH - (count * w + (count - 1) * spacing) - 2
    y = 60
    for i in range(count):
        a = Alien(screen, w, h, color=(0,140,0), h_speed=4.0, level=1)
        a.rect.topleft = (start_x + i * (w + spacing), y)
        a.x = float(a.rect.x)
        a.y = float(a.rect.y)
        a.direction = 1
        group.add(a)

    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(settings.bg_color)

    # run for a few seconds to let edge collisions occur
    frames = 240
    for f in range(frames):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        group.update()
        screen.blit(bg, (0, 0))
        group.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    # save a final screenshot
    pygame.image.save(screen, "capture.png")
    pygame.quit()

if __name__ == '__main__':
    main()
