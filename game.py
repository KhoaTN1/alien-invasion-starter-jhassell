import sys
import pygame
from ship import Ship
from bullet import Bullet, AlienBullet, Laser
import random
import math
from aliens import get_level_sizes, Alien


def run(settings, stars):
    pygame.init()
    WIDTH, HEIGHT = settings.screen_width, settings.screen_height
    FPS = 60

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Alien invasion')
    clock = pygame.time.Clock()

    # Score display
    score = 0
    font = pygame.font.SysFont(None, 36)

    ship = Ship(settings, screen)

    # alien bullets
    alien_bullets = pygame.sprite.Group()

    game_over = False

    # Precompute alien sizes for levels 1-5 using the current ship and screen
    alien_sizes = get_level_sizes(settings, ship)

    # horizontal speed fractions per level (fraction of ship.speed)
    h_fracs = {1: 0.35, 2: 0.65, 3: 0.85, 4: 0.85, 5: 0.0}
    # vertical descent fraction (unused for continuous descent)
    v_frac = 0.15 * 0.35

    # Ability slots (1-4): simple cooldown tracking
    abilities = [
        {"name": "Slot 1", "cooldown": 5000, "last_used": -100000},
        {"name": "Slot 2", "cooldown": 5000, "last_used": -100000},
        {"name": "Slot 3", "cooldown": 5000, "last_used": -100000},
        {"name": "Slot 4", "cooldown": 5000, "last_used": -100000},
    ]

    def spawn_level(level):
        """Return a Group of aliens for the given level according to rules.

        Level 1: 3 level-1 ships
        Level 2: 5 level-1 ships
        Level 3: 2 level-2 (left/right) and 3 level-1 center
        """
        group = pygame.sprite.Group()
        # helper to create and position an alien
        def mk(lvl, x, y, h_speed_override=None):
            w, h = alien_sizes[lvl]
            h_speed = ship.speed * h_fracs.get(lvl, 0.0) if h_speed_override is None else float(h_speed_override)
            v_speed = ship.speed * v_frac
            a = Alien(screen, w, h, h_speed=h_speed, v_speed=v_speed, level=lvl)
            a.rect.topleft = (int(x), int(y))
            a.x = float(a.rect.x)
            a.y = float(a.rect.y)
            group.add(a)

        top_y = 60
        if level == 1:
            count = 3
            w, h = alien_sizes[1]
            spacing = 24
            total_w = count * w + (count - 1) * spacing
            start_x = (WIDTH - total_w) // 2
            for i in range(count):
                mk(1, start_x + i * (w + spacing), top_y)
        elif level == 2:
            count = 5
            w, h = alien_sizes[1]
            spacing = 20
            total_w = count * w + (count - 1) * spacing
            start_x = (WIDTH - total_w) // 2
            for i in range(count):
                mk(1, start_x + i * (w + spacing), top_y)
        elif level == 3:
            # unified fleet: level-2 anchors on sides plus level-1s in center
            # treat entire row as one fleet moving at level-2's speed
            w2, h2 = alien_sizes[2]
            fleet_speed = ship.speed * h_fracs.get(2, 0.0)
            side_y = top_y
            left_x = 40
            right_x = WIDTH - 40 - w2
            mk(2, left_x, side_y, h_speed_override=fleet_speed)
            mk(2, right_x, side_y, h_speed_override=fleet_speed)
            # three level-1 in center row, use same fleet_speed so movement is unified
            count = 3
            w1, h1 = alien_sizes[1]
            spacing = 24
            total_w = count * w1 + (count - 1) * spacing
            start_x = (WIDTH - total_w) // 2
            for i in range(count):
                mk(1, start_x + i * (w1 + spacing), side_y, h_speed_override=fleet_speed)
        else:
            # fallback: one of each level for preview
            y = top_y
            for lvl in sorted(alien_sizes.keys()):
                w, h = alien_sizes[lvl]
                mk(lvl, (WIDTH - w) // 2, y)
                y += h + 24

        return group

    # Start at level 1
    current_level = 1
    aliens = spawn_level(current_level)

    bullets = pygame.sprite.Group()
    firing = False
    last_shot = 0
    shot_delay = 250

    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(settings.bg_color)
    for sx, sy, size in stars:
        if size == 1:
            bg.set_at((sx, sy), (255, 255, 255))
        else:
            pygame.draw.circle(bg, (255, 255, 255), (sx, sy), size // 2)

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
                elif event.key == pygame.K_UP:
                    ship.moving_up = True
                elif event.key == pygame.K_DOWN:
                    ship.moving_down = True
                elif event.key == pygame.K_SPACE:
                    firing = True
                elif event.key == pygame.K_RETURN and game_over:
                    # restart
                    # reset ship position
                    ship.rect.midbottom = ship.screen_rect.midbottom
                    ship.rect.y -= 10
                    ship.x = float(ship.rect.x)
                    ship.moving_left = ship.moving_right = False
                    # reset groups and score
                    bullets.empty()
                    alien_bullets.empty()
                    aliens.empty()
                    # spawn fresh level 1 aliens and reset level counter
                    current_level = 1
                    aliens = spawn_level(current_level)
                    score = 0
                    last_shot = 0
                    firing = False
                    # restore player HP on restart
                    ship.hp = float(getattr(ship, "max_hp", 30.0))
                    game_over = False
                elif event.key == pygame.K_q:
                    running = False
                # Ability slots 1-4
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}[event.key]
                    now = pygame.time.get_ticks()
                    slot = abilities[idx]
                    if now - slot["last_used"] >= slot["cooldown"]:
                        slot["last_used"] = now
                        # placeholder: activating ability logs to console; real effects can be added
                        print(f"Ability {idx+1} used at {now}ms")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    ship.moving_right = False
                elif event.key == pygame.K_LEFT:
                    ship.moving_left = False
                elif event.key == pygame.K_UP:
                    ship.moving_up = False
                elif event.key == pygame.K_DOWN:
                    ship.moving_down = False
                elif event.key == pygame.K_SPACE:
                    firing = False

        if not game_over:
            # If no laser is active, allow held keys to control movement
            laser_active = any(isinstance(b, Laser) for b in alien_bullets)
            if not laser_active:
                keys = pygame.key.get_pressed()
                ship.moving_right = keys[pygame.K_RIGHT]
                ship.moving_left = keys[pygame.K_LEFT]
                ship.moving_up = keys[pygame.K_UP]
                ship.moving_down = keys[pygame.K_DOWN]

            ship.update()

            now = pygame.time.get_ticks()
            if firing and len(bullets) < 3 and now - last_shot >= shot_delay:
                b = Bullet(screen, ship.rect.centerx, ship.rect.top)
                bullets.add(b)
                last_shot = now

            bullets.update()

            # aliens shoot (levels 1-5). level 3 fires bursts; level 4 and 5 fire lasers.
            for a in aliens:
                # small periodic bullets (levels 1-3) — use per-shot randomized interval
                if getattr(a, "shot_interval", None) and getattr(a, "next_shot_time", None) is not None:
                    if now >= a.next_shot_time:
                        if getattr(a, "burst_count", 1) > 1:
                            # spawn vertical stack of bullets at same x (back-to-back)
                            count = a.burst_count
                            spacing = 16  # space between stacked bullets
                            for i in range(count):
                                y0 = a.rect.bottom - i * spacing
                                # damage depends on alien level
                                damage_map = {1: 10.0, 2: 12.5, 3: 20.0}
                                ab = AlienBullet(screen, a.rect.centerx, y0, speed=4)
                                ab.damage = damage_map.get(getattr(a, "level", 1), 10.0)
                                alien_bullets.add(ab)
                        else:
                            ab = AlienBullet(screen, a.rect.centerx, a.rect.bottom, speed=4)
                            damage_map = {1: 10.0, 2: 12.5, 3: 20.0}
                            ab.damage = damage_map.get(getattr(a, "level", 1), 10.0)
                            alien_bullets.add(ab)
                        # schedule next shot with +/-500ms jitter
                        jitter_low = max(100, int(a.shot_interval - 500))
                        jitter_high = int(a.shot_interval + 500)
                        a.next_shot_time = now + random.randint(jitter_low, jitter_high)

                # level 4: deterministic laser straight down every 5000ms
                if getattr(a, "level", None) == 4 and getattr(a, "beam_interval", None):
                    if now - getattr(a, "last_beam_time", 0) >= a.beam_interval:
                        laser = Laser(screen, a.rect.centerx, a.rect.bottom, width=6, duration=800, damage=45.0)
                        alien_bullets.add(laser)
                        a.last_beam_time = now
                        # pause this alien while its laser is active
                        a.pause_until = now + getattr(laser, "duration", 0)

                # level 5: three anchor positions, fire one randomly every 5-7 seconds
                if getattr(a, "level", None) == 5 and getattr(a, "next_beam_time", None) is not None:
                    if now >= a.next_beam_time:
                        left_x = a.rect.left + max(4, a.width // 4)
                        center_x = a.rect.centerx
                        right_x = a.rect.left + max(4, (3 * a.width) // 4)
                        choice_x = random.choice([left_x, center_x, right_x])
                        laser = Laser(screen, choice_x, a.rect.bottom, width=6, duration=800, damage=45.0)
                        alien_bullets.add(laser)
                        a.next_beam_time = now + random.randint(a.beam_min, a.beam_max)
                        # pause this alien while its laser is active
                        a.pause_until = now + getattr(laser, "duration", 0)

            alien_bullets.update()
        else:
            # still update timers for periodic level-5 drops handled inside Alien.update()
            now = pygame.time.get_ticks()

        # Draw background first so preview aliens aren't overwritten
        screen.blit(bg, (0, 0))

        # draw preview aliens (sprite group)
        if not game_over:
            # update aliens
            aliens.update()

            # Collision avoidance: if aliens come into contact, move the
            # colliding alien to a nearby free direction chosen at random.
            sprites = list(aliens)
            screen_rect = screen.get_rect()
            offsets = [(16, 0), (-16, 0), (0, 16), (0, -16), (12, 12), (-12, 12), (12, -12), (-12, -12)]
            # Detect clusters of overlapping sprites and resolve them as groups.
            # This handles cases where 3+ ships overlap and reduces jitter.
            visited = set()
            groups = []
            for s in sprites:
                if s in visited:
                    continue
                # BFS to collect all sprites connected by collisions
                queue = [s]
                group = []
                while queue:
                    cur = queue.pop()
                    if cur in visited:
                        continue
                    visited.add(cur)
                    group.append(cur)
                    for other in sprites:
                        if other in visited:
                            continue
                        if cur.rect.colliderect(other.rect):
                            queue.append(other)
                if len(group) > 1:
                    groups.append(group)

            # Resolve each overlapping group by moving ships away from the group's centroid
            for group in groups:
                now = pygame.time.get_ticks()
                # compute centroid
                cx = sum(a.x + a.rect.width / 2.0 for a in group) / len(group)
                cy = sum(a.y + a.rect.height / 2.0 for a in group) / len(group)
                # spread amount scales with group size
                base_nudge = 14 + len(group) * 4
                for a in group:
                    # vector from centroid to sprite center
                    ax = (a.x + a.rect.width / 2.0) - cx
                    ay = (a.y + a.rect.height / 2.0) - cy
                    dist = math.hypot(ax, ay)
                    if dist < 1e-3:
                        # if almost overlapping exactly, choose a random angle
                        angle = random.random() * 2 * math.pi
                        nx = math.cos(angle)
                        ny = math.sin(angle)
                    else:
                        nx = ax / dist
                        ny = ay / dist

                    # apply nudge outward plus a small random jitter
                    nudge = base_nudge * random.uniform(0.9, 1.2)
                    nudge_x = nx * nudge
                    nudge_y = ny * nudge * 0.7

                    # update position, clamp to screen
                    a.x = float(int(a.x + nudge_x))
                    a.y = float(int(a.y + nudge_y))
                    if a.x < 0:
                        a.x = 0.0
                    if a.x + a.rect.width > screen_rect.width:
                        a.x = float(screen_rect.width - a.rect.width)
                    if a.y < 0:
                        a.y = 0.0
                    if a.y + a.rect.height > screen_rect.height:
                        a.y = float(screen_rect.height - a.rect.height)
                    a.rect.topleft = (int(a.x), int(a.y))

                    # pick new directions and short pause so they resume quickly
                    a.direction = 1 if nx >= 0 else -1
                    a.v_dir = random.choice([-1, 0, 1])
                    a.pause_until = now + max(40, int(a.pause_ms * 0.5))

                    # slightly randomize speeds to break symmetry
                    a.h_speed = a.base_h_speed * random.uniform(0.85, 1.2)
                    a.v_speed = a.base_v_speed * random.uniform(0.85, 1.1)
            # If any alien reaches the player's vertical position, game over
            # Game over only when an alien touches the bottom edge of the screen
            for a in aliens:
                if a.rect.bottom >= screen_rect.bottom:
                    game_over = True
                    break

        # detect bullet->alien collisions and apply damage/flash
        # remove bullets on hit, but do not immediately remove aliens (they handle flash/death)
        collisions = pygame.sprite.groupcollide(bullets, aliens, True, False)
        if collisions:
            for bullet, hit_list in collisions.items():
                for hit_alien in hit_list:
                    # apply one damage per bullet
                    prev_hp = getattr(hit_alien, "hp", 1)
                    hit_alien.hit(damage=1)
                    # if this hit killed the alien, award score immediately
                    if prev_hp > 0 and getattr(hit_alien, "hp", 1) <= 0:
                        score += getattr(hit_alien, "score", 0)

        # level progression: when current wave cleared, advance level and spawn
        if not aliens and not game_over:
            current_level += 1
            aliens = spawn_level(current_level)

        # check alien-bullet -> ship collisions
        if not game_over:
            for ab in list(alien_bullets):
                if ab.rect.colliderect(ship.rect):
                    # Apply damage according to bullet/laser damage attribute.
                    dmg = getattr(ab, "damage", None)
                    if dmg is None:
                        # fallback: instant kill
                        died = ship.take_damage(getattr(ship, "max_hp", 30.0))
                    else:
                        # For lasers, only apply once per beam
                        if getattr(ab, "hit_registered", False):
                            died = False
                        else:
                            died = ship.take_damage(float(dmg))
                            if hasattr(ab, "hit_registered"):
                                ab.hit_registered = True
                    # remove bullets immediately; lasers continue but we mark hit
                    if not hasattr(ab, "hit_registered"):
                        try:
                            ab.kill()
                        except Exception:
                            pass
                    if died:
                        game_over = True
                        break
            # Ship <-> alien collisions: if the player's ship touches an alien,
            # subtract half the ship's maximum HP and remove the alien.
            for a in list(aliens):
                if a.rect.colliderect(ship.rect):
                    # If ship currently invulnerable, ignore contact
                    now = pygame.time.get_ticks()
                    if getattr(ship, "flash_until", 0) and now < ship.flash_until:
                        continue
                    dmg = float(getattr(ship, "max_hp", 30.0)) * 0.5
                    died = ship.take_damage(dmg)
                    # nudge the alien away instead of killing it
                    try:
                        # push alien away in its current horizontal direction
                        nudge_x = (1 if getattr(a, "direction", 1) >= 0 else -1) * 20
                        a.x = float(int(a.x + nudge_x))
                        # clamp
                        if a.x < 0:
                            a.x = 0.0
                        if a.x + a.rect.width > screen_rect.width:
                            a.x = float(screen_rect.width - a.rect.width)
                        a.rect.x = int(a.x)
                        a.pause_until = now + max(40, int(a.pause_ms * 0.5))
                    except Exception:
                        pass
                    if died:
                        game_over = True
                        break

        # propagate reversals: ensure aliens actually touching the screen edge
        # are treated as reversal sources and propagate to same-row neighbors.
        now = pygame.time.get_ticks()
        screen_rect = screen.get_rect()

        # Collect reversal sources first (snapshot) to avoid re-propagation
        def same_row(a, b):
            # use a tolerant y-match so slight integer rounding differences
            # don't exclude neighbors; tolerance is at least 8px or half the
            # taller sprite height.
            tol = max(8, max(a.height, b.height) // 2)
            return abs(a.rect.centery - b.rect.centery) <= tol

        # Row-based edge detection: group aliens by approximate row and
        # if the leftmost or rightmost alien in a row touches the screen
        # edge, reverse and drop the entire row together.
        edge_mark_interval = 300
        # bucket aliens by rounded centery to form rows
        rows = {}
        for a in aliens:
            key = int(round(a.rect.centery / 8.0))
            rows.setdefault(key, []).append(a)

        for key, members in rows.items():
            # find leftmost and rightmost members in this row
            leftmost = min(members, key=lambda s: s.rect.left)
            rightmost = max(members, key=lambda s: s.rect.right)
            # check edges and skip if recently reversed
            if now - getattr(leftmost, "last_reversed", 0) > edge_mark_interval and leftmost.rect.left <= 0:
                # reverse whole row to the right
                for m in members:
                    m.direction = 1
                    m.pause_until = now + getattr(m, "pause_ms", 200)
                    m.last_reversed = now
                    m.start_drop(10)
                # nudge the row inward so the leftmost ship is no longer exactly
                # touching the window border; this prevents repeated edge triggers.
                for m in members:
                    m.x += 2
                    m.rect.x = int(m.x)
            elif now - getattr(rightmost, "last_reversed", 0) > edge_mark_interval and rightmost.rect.right >= screen_rect.right:
                # reverse whole row to the left
                for m in members:
                    m.direction = -1
                    m.pause_until = now + getattr(m, "pause_ms", 200)
                    m.last_reversed = now
                    m.start_drop(10)
                # nudge the row inward (left) so the rightmost ship isn't stuck
                for m in members:
                    m.x -= 2
                    m.rect.x = int(m.x)

        # (collision-to-flip logic removed — keeping propagation below)

        sources = [a for a in aliens if getattr(a, "last_reversed", 0) and now - getattr(a, "last_reversed", 0) <= max(300, getattr(a, "pause_ms", 200))]
        for src in sources:
            src_rev_time = getattr(src, "last_reversed", 0)
            for other in aliens:
                if other is src:
                    continue
                if not same_row(src, other):
                    continue

                # if this 'other' is a level-1 alien, only respond when it's
                # about to collide with a level-2 ship (gap <= 10)
                if getattr(other, "level", None) == 1:
                    close_to_level2 = False
                    for maybe in aliens:
                        if getattr(maybe, "level", None) != 2:
                            continue
                        if not same_row(maybe, other):
                            continue
                        # compute horizontal gaps (positive means separated)
                        gap_right = maybe.rect.left - other.rect.right
                        gap_left = other.rect.left - maybe.rect.right
                        if (0 <= gap_right <= 10) or (0 <= gap_left <= 10):
                            close_to_level2 = True
                            break
                    if not close_to_level2:
                        continue

                # apply reversal/drop once per source snapshot
                other.direction = src.direction
                other.pause_until = now + other.pause_ms
                # set last_reversed to source's reversal time so it won't be reprocessed
                other.last_reversed = src_rev_time
                drop = 10
                if other.level == 5:
                    if now - getattr(other, "last_drop_time", 0) >= 5000:
                        other.start_drop(drop)
                        other.last_drop_time = now
                else:
                    other.start_drop(drop)
                other.x = float(other.rect.x)


        aliens.draw(screen)

        bullets.draw(screen)

        # draw alien bullets
        alien_bullets.draw(screen)

        # render score and current level
        score_surf = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_surf, (12, 12))
        level_surf = font.render(f"Level: {current_level}", True, (200, 200, 100))
        screen.blit(level_surf, (12, 44))

        # draw ability slots (1-4) with simple cooldown indicator
        for i, slot in enumerate(abilities):
            bx = 12 + i * 44
            by = 80
            bw = 36
            bh = 20
            pygame.draw.rect(screen, (40, 40, 40), (bx, by, bw, bh))
            # label
            lbl = font.render(str(i + 1), True, (220, 220, 220))
            screen.blit(lbl, (bx + 4, by + 1))
            # cooldown overlay
            now = pygame.time.get_ticks()
            elapsed = now - slot["last_used"]
            cd = slot["cooldown"]
            if elapsed < cd:
                frac = 1 - (elapsed / cd)
                cover_h = int(bh * frac)
                cover = pygame.Surface((bw, cover_h), pygame.SRCALPHA)
                cover.fill((0, 0, 0, 160))
                screen.blit(cover, (bx, by))
        ship.draw()

        # Game over overlay
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            go_font = pygame.font.SysFont(None, 72)
            go_surf = go_font.render("GAME OVER", True, (255, 40, 40))
            go_rect = go_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            screen.blit(go_surf, go_rect)
            instr = font.render("Press Q to quit or ENTER to restart", True, (255, 255, 255))
            instr_rect = instr.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            screen.blit(instr, instr_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
