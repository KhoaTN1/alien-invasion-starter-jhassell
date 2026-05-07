import pygame


class Bullet(pygame.sprite.Sprite):
    """A bullet fired from the ship, moving upward and killing itself off-screen."""

    def __init__(self, screen, x, y, speed=7, color=(250, 250, 250)):
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


class AlienBullet(pygame.sprite.Sprite):
    """A bullet fired by an alien, moving downward."""

    def __init__(self, screen, x, y, speed=4, color=(255, 60, 60)):
        super().__init__()
        self.screen = screen

        self.width = 4
        self.height = 12
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

        self.speed = speed

        # damage applied to the player on hit
        self.damage = 10.0

    def update(self):
        # Move the bullet downward
        self.rect.y += self.speed
        # Remove when off the bottom
        if self.rect.top > self.screen.get_height():
            self.kill()


class Laser(pygame.sprite.Sprite):
    """A stationary vertical laser beam that lasts for a short duration.

    Instantly kills the ship on contact (handled by collision detection in game loop).
    """

    def __init__(self, screen, x, y, width=6, color=(255, 30, 30), duration=700, damage=45.0):
        super().__init__()
        self.screen = screen
        self.width = width
        # laser extends from y down to bottom of the screen
        height = max(8, screen.get_height() - y)
        self.image = pygame.Surface((self.width, height), pygame.SRCALPHA)
        self.image.fill(color)

        self.rect = self.image.get_rect()
        # center x provided; place rect so that x is the center of the beam
        self.rect.centerx = int(x)
        self.rect.top = int(y)

        self.start_time = pygame.time.get_ticks()
        self.duration = int(duration)
        # damage applied to the player on first contact
        self.damage = float(damage)
        self.hit_registered = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.start_time >= self.duration:
            self.kill()
