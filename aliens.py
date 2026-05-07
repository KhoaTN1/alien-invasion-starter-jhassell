import math
import random
import pygame


def _alien_size_for_fit(screen_height, fit_count, ship_width, ship_height):
    """Return (width, height) so that `fit_count` aliens fit vertically.

    Keeps the ship's width/height aspect ratio.
    """
    if fit_count <= 0:
        raise ValueError("fit_count must be >= 1")

    # Compute height so that fit_count aliens fit in the available screen height.
    # Use floor division to ensure integer pixel sizes and leave a small margin.
    raw_height = max(8, screen_height // fit_count)

    # Maintain aspect ratio from the ship
    aspect = ship_width / ship_height if ship_height else 1
    raw_width = max(8, int(raw_height * aspect))

    return raw_width, raw_height


def get_level_sizes(settings, ship):
    """Return a dict mapping level -> (width, height) for alien sprites.

    Levels:
      1 - same size as ship
      2 - same size as ship
      3 - sized so that 7 fit on the vertical axis
      4 - sized so that 3 fit on the vertical axis
      5 - sized so that 1 fits on the vertical axis
    """
    ship_w, ship_h = getattr(ship, "width", 60), getattr(ship, "height", 40)
    sh = settings.screen_height

    # Build sizes per requested rules:
    # level1 = 20% bigger than ship, level2 = 40% bigger, level3 = 85% bigger
    # level4 width such that only 7 fit horizontally, level5 width such that only 1 fits
    aspect = ship_w / ship_h if ship_h else 1

    # Base scaled sizes for levels 1-3
    l1_w, l1_h = int(ship_w * 1.2), int(ship_h * 1.2)
    l2_w, l2_h = int(ship_w * 1.4), int(ship_h * 1.4)
    l3_w, l3_h = int(ship_w * 1.85), int(ship_h * 1.85)

    # Level 4: width such that 7 fit across the screen
    lvl4_width = max(8, settings.screen_width // 7)
    lvl4_height = int(lvl4_width / aspect)

    # Level 5: width such that only 1 fits across (leave small margins)
    lvl5_width = max(8, settings.screen_width - 40)
    lvl5_height = int(lvl5_width / aspect)

    # Cap heights so the largest alien is about 10% of screen height
    max_h = max(1, int(settings.screen_height * 0.10))

    def cap(w, h):
        h_c = min(h, max_h)
        w_c = max(8, int(h_c * aspect))
        return w_c, h_c

    sizes = {}
    # For levels 1-3: scale then cap (maintain aspect)
    sizes[1] = cap(l1_w, l1_h)
    sizes[2] = cap(l2_w, l2_h)
    sizes[3] = cap(l3_w, l3_h)

    # For level 4 and 5: enforce horizontal-fit widths, then cap height
    l4_h_c = min(lvl4_height, max_h)
    sizes[4] = (lvl4_width, l4_h_c)

    l5_h_c = min(lvl5_height, max_h)
    # Keep the previous behavior where level 5 spans most of the screen width
    sizes[5] = (lvl5_width, l5_h_c)

    return sizes


__all__ = ["get_level_sizes"]


class Alien(pygame.sprite.Sprite):
    """Simple visual alien sprite used for previews.

    Subclasses `pygame.sprite.Sprite` so it can be added to a `Group` and
    drawn with `Group.draw()`.
    """

    def __init__(self, screen, width, height, color=(0, 140, 0), h_speed=0.0, v_speed=0.0, pause_ms=100, level=None):
        super().__init__()
        self.screen = screen
        self.width = int(width)
        self.height = int(height)
        self.color = color

        # Create pixel-art alien: build a small pixel map and scale it to the
        # requested width/height so we retain a chunky, pixelated look.
        def _shade(col, factor):
            return tuple(max(0, min(255, int(c * factor))) for c in col)

        main = tuple(self.color)
        # Slightly darker and lighter shades for depth
        dark = _shade(main, 0.6)
        light = _shade(main, 1.25)

        # Choose pixel maps per level to make levels 4 and 5 visually unique.
        if level == 4:
            # Level 4: sleeker ship with a central laser barrel
            pixel_map = [
                "00011110000",
                "00111111000",
                "01111111100",
                "11112221110",
                "11112221110",
                "01111111100",
                "00111111000",
                "00011110000",
            ]
            palette = {
                "0": (0, 0, 0, 0),
                "1": main,
                "2": (200, 200, 60),  # a small warm emitter for the barrel
            }
        elif level == 5:
            # Level 5: wide final-boss ship — base map is wide so scaling to full
            # screen width produces a cohesive boss silhouette without pixel
            # stretching artifacts.
            pixel_map = [
                "00000001111111111111000000000",
                "00000011111111111111100000000",
                "00000113333333333333311000000",
                "00001133333333333333333100000",
                "00011333333333333333333310000",
                "00113333333332223333333311000",
                "00113333333333333333333311000",
                "00011333333333333333333310000",
                "00001113333333333333331100000",
                "00000111113333333311111000000",
                "00000001111111111111000000000",
            ]
            palette = {
                "0": (0, 0, 0, 0),
                "1": main,
                "2": dark,
                "3": light,
            }
        else:
            # Levels 1-3: classic small alien form
            pixel_map = [
                "00001110000",
                "00011111000",
                "00111111100",
                "01111111110",
                "11111111111",
                "11011110111",
                "01101111010",
                "00100001000",
            ]
            palette = {
                "0": (0, 0, 0, 0),
                "1": main,
                "2": dark,
                "3": light,
            }

        # Render base surface at 1px-per-tile
        map_h = len(pixel_map)
        map_w = len(pixel_map[0]) if map_h else 0
        base = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
        for y, row in enumerate(pixel_map):
            for x, ch in enumerate(row):
                col = palette.get(ch)
                if col is None:
                    continue
                if len(col) == 4:
                    base.set_at((x, y), col)
                else:
                    base.set_at((x, y), (*col, 255))

        # For level 5 we want the boss to span the full width the code expects
        # (unstretched pixel art that fits). The base pixel map above is wide so
        # scaling it to the target rectangle with nearest-neighbor keeps the
        # silhouette cohesive while filling the screen.
        self.image = pygame.transform.scale(base, (self.width, self.height))

        self.rect = self.image.get_rect()
        # keep original image for restoring after flash
        self._orig_image = self.image.copy()

        # Movement speeds (pixels per frame). Horizontal may be positive/negative.
        # apply a global speed bias (approx +33%) then an extra +20% requested
        # and increase vertical component by ~50% to make vertical/diagonal
        # movement noticeably faster.
        speed_multiplier = 1.33 * 1.20
        # increase vertical multiplier: previous value 1.5, boosted previously to 2.25;
        # boost another 50% so vertical movement is snappier (2.25 * 1.5 = 3.375)
        vertical_multiplier = 3.375
        self.base_h_speed = float(h_speed) * speed_multiplier
        self.base_v_speed = float(v_speed) * speed_multiplier * vertical_multiplier
        # current speeds include a larger random variation so aliens don't all move identically
        self.h_speed = self.base_h_speed * random.uniform(0.8, 1.25)
        self.v_speed = self.base_v_speed * random.uniform(0.85, 1.15)

        # occasional horizontal speed variation timer to desynchronize movement
        self.next_h_change = pygame.time.get_ticks() + random.randint(80, 1000)
        # occasional random horizontal direction change timer so aliens
        # will change left/right even when not hitting edges or other ships
        self.next_dir_change = pygame.time.get_ticks() + random.randint(200, 1400)

        # randomized vertical movement direction (-1,0,1) and timing
        # bias downwards so aliens are more likely to move down than up
        self.v_dir = random.choices([-1, 0, 1], weights=(1, 3, 6), k=1)[0]
        self.next_v_change = pygame.time.get_ticks() + random.randint(300, 900)

        # Direction along x: 1 -> right, -1 -> left
        # start with a completely random horizontal direction per alien
        self.direction = random.choice([-1, 1])

        # Pause behavior when reversing: milliseconds to pause.
        # Keep a small minimum so direction changes feel quick but stable.
        self.pause_ms = max(50, int(pause_ms))
        self.pause_until = 0
        # Timestamp of last reversal (ms); 0 means never
        self.last_reversed = 0
        # Timestamp of last vertical drop (ms); used for level 5 throttling
        self.last_drop_time = 0
        # Level and score
        self.level = level
        level_scores = {1: 1000, 2: 2500, 3: 5000, 4: 7500, 5: 15000}
        self.score = level_scores.get(level, 0)
        # Hit points for testing: default to 1
        # HP by level (customizable): level1=3, level2=5, level3=7, level4=10, level5=15
        hp_map = {1: 3, 2: 5, 3: 7, 4: 10, 5: 15}
        self.hp = hp_map.get(level, 1)

        # Flash state: when hit, we flash white for a short duration
        self.flash_until = 0
        self.pending_kill = False
        self.flash_normal_ms = 220
        self.flash_death_ms = 80

        # Shooting: levels 1-3 shoot periodically (level 3 will fire bursts)
        shot_map = {1: 2000, 2: 1000, 3: 2000}  # milliseconds
        self.shot_interval = shot_map.get(level, None)
        # burst_count: level 3 fires a burst of 5 bullets; others fire single shots
        self.burst_count = 5 if level == 3 else 1
        # schedule first shot with +/-500ms jitter so firing times are not uniform
        if self.shot_interval is not None:
            jitter_low = max(100, int(self.shot_interval - 500))
            jitter_high = int(self.shot_interval + 500)
            self.next_shot_time = pygame.time.get_ticks() + random.randint(jitter_low, jitter_high)
        else:
            self.next_shot_time = None

        # Level 4: single laser beam straight down every 5 seconds
        if level == 4:
            self.beam_interval = 5000
            self.last_beam_time = 0

        # Level 5: three possible beam anchors (left-center, center, right-center)
        # Fires randomly every 5-7 seconds; schedule first shot shortly after spawn
        if level == 5:
            self.beam_min = 5000
            self.beam_max = 7000
            self.next_beam_time = pygame.time.get_ticks() + random.randint(self.beam_min, self.beam_max)
        self.last_shot_time = 0

        # Use float x,y for smoother movement
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        # dropping animation state
        self.dropping = False
        self.drop_start = 0
        self.drop_duration_ms = 80
        self.drop_amount = 0
        self.drop_start_y = float(self.y)

    def update(self, *args):
        """Move horizontally and down. Reverse horizontal direction on screen edges."""
        screen_rect = self.screen.get_rect()

        now = pygame.time.get_ticks()

        # handle flash expiration
        if getattr(self, "flash_until", 0) and now >= self.flash_until:
            # if pending_kill, kill now
            if getattr(self, "pending_kill", False):
                self.kill()
                return
            # restore original image
            if hasattr(self, "_orig_image"):
                self.image = self._orig_image
            self.flash_until = 0

        # horizontal movement (skip if currently paused)
        # handle ongoing drop animation (time-based for smooth/faster drop)
        if getattr(self, "dropping", False):
            elapsed = now - getattr(self, "drop_start", 0)
            if elapsed >= getattr(self, "drop_duration_ms", 1):
                # finish drop
                self.y = self.drop_start_y + self.drop_amount
                # ensure integer alignment to keep fleet rows aligned
                self.y = float(int(round(self.y)))
                self.rect.y = int(self.y)
                self.dropping = False
            else:
                frac = elapsed / float(getattr(self, "drop_duration_ms", 1))
                self.y = self.drop_start_y + self.drop_amount * frac
                self.rect.y = int(self.y)

        # horizontal movement (skip if currently paused)
        if now >= getattr(self, "pause_until", 0):
            self.x += self.h_speed * self.direction
            # update rect.x tentatively and check edges
            self.rect.x = int(self.x)
            if self.rect.right >= screen_rect.right:
                self.rect.right = screen_rect.right
                self.x = float(self.rect.x)
                self.direction = -1
                self.pause_until = now + self.pause_ms
                self.last_reversed = now
                # drop down one level (fixed y-level step)
                # when hitting screen edges, drop a few more pixels for feel
                drop = 4
                if self.level == 5:
                    if now - getattr(self, "last_drop_time", 0) >= 5000:
                        self.start_drop(drop)
                        self.last_drop_time = now
                else:
                    self.start_drop(drop)
            elif self.rect.left <= 0:
                self.rect.left = 0
                self.x = float(self.rect.x)
                self.direction = 1
                self.pause_until = now + self.pause_ms
                self.last_reversed = now
                # when hitting screen edges on left side, drop a few more pixels
                drop = 4
                if self.level == 5:
                    if now - getattr(self, "last_drop_time", 0) >= 5000:
                        self.start_drop(drop)
                        self.last_drop_time = now
                else:
                    self.start_drop(drop)

        # randomized vertical wandering: change vertical direction more often
        # and increase tendency to move (less idle) so movement is more erratic.
        if now >= getattr(self, "next_v_change", 0):
            # pick a new vertical direction with higher likelihood to move
            self.v_dir = random.choices([-1, 0, 1], weights=(4, 1, 4), k=1)[0]
            # more frequent changes to increase erratic motion
            self.next_v_change = now + random.randint(80, 800)
            # slightly vary vertical speed when direction changes
            self.v_speed = self.base_v_speed * random.uniform(0.7, 1.3)

        # occasional horizontal speed tweak to avoid uniform movement
        if now >= getattr(self, "next_h_change", 0):
            self.h_speed = self.base_h_speed * random.uniform(0.8, 1.25)
            self.next_h_change = now + random.randint(200, 1400)

        # occasional random horizontal direction change (independent of edges)
        if now >= getattr(self, "next_dir_change", 0) and now >= getattr(self, "pause_until", 0) and not getattr(self, "dropping", False):
            # higher probability to pick a new direction so movement is less uniform
            if random.random() < 0.75:
                self.direction = random.choice([-1, 1])
            # short pause to avoid immediate flips and desynchronize
            self.pause_until = now + max(30, int(self.pause_ms * 0.4))
            self.next_dir_change = now + random.randint(150, 1200)

        # apply vertical wandering unless currently dropping
        if not getattr(self, "dropping", False) and getattr(self, "v_dir", 0):
            self.y += self.v_speed * self.v_dir
            # clamp to screen bounds
            screen_rect = self.screen.get_rect()
            if self.y < 0:
                self.y = 0
                self.v_dir *= -1
            if self.y + self.rect.height > screen_rect.height:
                self.y = float(screen_rect.height - self.rect.height)
                self.v_dir *= -1
            self.rect.y = int(self.y)

        # automatic periodic drop for level 5 (independent of reversal)
        if self.level == 5:
            drop_interval = 5000
            if now - getattr(self, "last_drop_time", 0) >= drop_interval:
                drop = 3
                self.start_drop(drop)
                self.last_drop_time = now

        # vertical descent is only applied when reversing at screen edges

    def hit(self, damage=1):
        """Apply damage to this alien from a player's bullet.

        Triggers a white flash; if hp <= 0 after damage, schedule death after
        a shorter flash duration.
        """
        now = pygame.time.get_ticks()
        self.hp -= int(damage)
        if self.hp <= 0:
            # set short flash then mark for kill
            self.pending_kill = True
            self.flash_until = now + self.flash_death_ms
            # set image to white fill for flash
            w, h = self.image.get_size()
            white = pygame.Surface((w, h))
            white.fill((255, 255, 255))
            self.image = white
        else:
            # normal hit flash
            self.flash_until = now + self.flash_normal_ms
            w, h = self.image.get_size()
            white = pygame.Surface((w, h))
            white.fill((255, 255, 255))
            self.image = white

    def start_drop(self, drop_amount, duration_ms=None):
        """Begin a time-based drop by drop_amount pixels over a short duration."""
        now = pygame.time.get_ticks()
        # prevent overlapping/rapid repeated drops which can cause multiple
        # unintended descents when sprites are colliding or edge-stuck.
        if getattr(self, "dropping", False):
            return
        # minimum interval between drops (ms)
        min_drop_interval = 150
        if now - getattr(self, "last_drop_time", 0) < min_drop_interval:
            return

        self.drop_amount = float(drop_amount)
        self.drop_start = now
        if duration_ms is not None:
            self.drop_duration_ms = int(duration_ms)
        self.drop_start_y = float(self.y)
        self.dropping = True
        self.last_drop_time = now


__all__.append("Alien")
