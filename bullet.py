import pygame


class Bullet(pygame.sprite.Sprite):
    """A bullet fired from the ship, moving upward and killing itself off-screen."""

    def __init__(self, screen, x, y, speed=7, color=(60, 60, 60)):
        super().__init__()
        self.screen = screen

        # Simple rectangular bullet
        self.width = 3
        self.height = 15
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        # Position: bottom of the bullet at ship's top
        self.rect.centerx = x
        self.rect.bottom = y

        self.speed = speed

    def update(self):
        # Move the bullet upward
        self.rect.y -= self.speed
        # Remove the bullet when it leaves the top of the screen
        if self.rect.bottom < 0:
            self.kill()
