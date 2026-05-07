import pygame


def _render_pixel_map(pixel_map, palette):
    """Return a pygame.Surface rendered from a small pixel map and palette.

    - pixel_map: iterable of strings; each character is a key in palette.
    - palette: dict char -> (r,g,b) or (r,g,b,a)
    The returned surface has size (map_w, map_h) where map_* are pixel counts.
    """
    h = len(pixel_map)
    if h == 0:
        return pygame.Surface((0, 0), pygame.SRCALPHA)
    w = len(pixel_map[0])
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(pixel_map):
        for x, ch in enumerate(row):
            col = palette.get(ch)
            if col is None:
                continue
            # If palette color includes alpha use it, otherwise assume opaque
            if len(col) == 4:
                surf.set_at((x, y), col)
            else:
                surf.set_at((x, y), (*col, 255))
    return surf


class Ship:
    """A pixel-art ship positioned at screen bottom-center."""

    def __init__(self, settings, screen):
        self.screen = screen
        self.settings = settings

        # Target ship dimensions (will be used to scale pixel art)
        self.width = 60
        self.height = 40

        # A small pixel map (text rows) representing a silver/gray ship.
        # Characters: 0=transparent, 1=light, 2=dark, 3=mid
        pixel_map = [
            "00000100000",
            "00001110000",
            "00011111000",
            "00111111100",
            "01133333110",
            "11333333311",
            "11122211111",
        ]

        palette = {
            "0": (0, 0, 0, 0),
            "1": (230, 230, 230),  # highlight
            "3": (170, 170, 170),  # mid metal
            "2": (90, 90, 90),     # dark base
        }

        base = _render_pixel_map(pixel_map, palette)
        # Scale to the requested size using nearest-neighbor scaling to keep pixel look
        self.image = pygame.transform.scale(base, (self.width, self.height))

        # keep original image for flash restore
        self._orig_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # Start each new ship at the bottom center of the screen
        self.rect.midbottom = self.screen_rect.midbottom
        self.rect.y -= 10

        # Movement attributes
        self.speed = 5.85
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

        # Store a float x value for precise movement
        self.x = float(self.rect.x)
        # Store a float y value for precise vertical movement
        self.y = float(self.rect.y)

        # Hit points
        self.max_hp = 30.0
        self.hp = float(self.max_hp)

        # Flash / invulnerability after taking damage (ms)
        self.flash_ms = 300
        self.flash_until = 0

    def draw(self):
        """Draw the ship to the screen."""
        # handle flash expiration
        now = pygame.time.get_ticks()
        if getattr(self, "flash_until", 0) and now >= self.flash_until:
            # restore original image
            if hasattr(self, "_orig_image"):
                self.image = self._orig_image
            self.flash_until = 0
        self.screen.blit(self.image, self.rect)

    def take_damage(self, damage):
        """Apply damage to the ship. Returns True if ship is dead."""
        now = pygame.time.get_ticks()
        # if currently invulnerable, ignore
        if getattr(self, "flash_until", 0) and now < self.flash_until:
            return False
        self.hp -= float(damage)
        # start flash/invulnerability
        self.flash_until = now + int(self.flash_ms)
        # set image to white for flash effect
        w, h = self.image.get_size()
        white = pygame.Surface((w, h))
        white.fill((255, 255, 255))
        self.image = white
        return self.hp <= 0

    def update(self):
        """Update ship position based on movement flags and screen boundaries."""
        # Move right
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.speed

        # Move left
        if self.moving_left and self.rect.left > 0:
            self.x -= self.speed

        # Move up
        if self.moving_up and self.rect.top > 0:
            self.y -= self.speed

        # Move down
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.speed

        # Update rect from float position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
