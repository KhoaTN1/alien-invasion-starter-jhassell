import pygame


class Ship:
    """A simple ship drawn as a triangle and positioned at screen bottom-center."""

    def __init__(self, settings, screen):
        self.screen = screen
        self.settings = settings

        # Ship dimensions and appearance
        self.width = 60
        self.height = 40
        self.color = (60, 60, 60)

        # Create an image surface with an alpha channel and draw a triangle
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        points = [(0, self.height), (self.width / 2, 0), (self.width, self.height)]
        pygame.draw.polygon(self.image, self.color, points)

        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # Start each new ship at the bottom center of the screen
        self.rect.midbottom = self.screen_rect.midbottom
        self.rect.y -= 10

    def draw(self):
        """Draw the ship to the screen."""
        self.screen.blit(self.image, self.rect)
