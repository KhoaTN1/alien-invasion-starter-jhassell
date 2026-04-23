import sys
import pygame
from ship import Ship
from bullet import Bullet


def run(settings, stars):
    pygame.init()
    WIDTH, HEIGHT = settings.screen_width, settings.screen_height
    FPS = 60

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Alien invasion')
    clock = pygame.time.Clock()

    ship = Ship(settings, screen)

    bullets = pygame.sprite.Group()
    firing = False
    last_shot = 0
    shot_delay = 250

    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(settings.bg_color)
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    ship.moving_right = True
                elif event.key == pygame.K_LEFT:
                    ship.moving_left = True
                elif event.key == pygame.K_SPACE:
                    firing = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    ship.moving_right = False
                elif event.key == pygame.K_LEFT:
                    ship.moving_left = False
                elif event.key == pygame.K_SPACE:
                    firing = False

        ship.update()

        now = pygame.time.get_ticks()
        if firing and len(bullets) < 3 and now - last_shot >= shot_delay:
            b = Bullet(screen, ship.rect.centerx, ship.rect.top)
            bullets.add(b)
            last_shot = now

        bullets.update()

        screen.blit(bg, (0, 0))
        bullets.draw(screen)
        ship.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
