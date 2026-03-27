import math
import os
import random
import sys

import pygame


WIDTH, HEIGHT = 480, 800
FPS = 60
TITLE = "Tap to Breathe"
HIGHSCORE_FILE = "highscore.txt"


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

        self.radius = 22

        self.velocity_y = -2.0
        self.velocity_x = 0.0

        self.gravity = 0.25
        self.auto_lift = -0.05
        self.boost_strength = -6.2
        self.max_fall_speed = 8.0

        self.max_horizontal_speed = 5.2
        self.horizontal_accel = 0.52
        self.horizontal_friction = 0.88

        self.color_main = (255, 90, 110)
        self.color_shadow = (200, 65, 85)
        self.color_highlight = (255, 190, 198)
        self.color_knot = (130, 50, 50)

        self.pulse_timer = 0.0

    def boost(self):
        self.velocity_y = self.boost_strength
        self.pulse_timer = 0.20

    def update(self, dt, move_left=False, move_right=False):
        # Horizontal movement: responsive acceleration + damping for smoother touch/keyboard control.
        if move_left and not move_right:
            self.velocity_x -= self.horizontal_accel
        elif move_right and not move_left:
            self.velocity_x += self.horizontal_accel
        else:
            self.velocity_x *= self.horizontal_friction
            if abs(self.velocity_x) < 0.05:
                self.velocity_x = 0.0

        self.velocity_x = max(-self.max_horizontal_speed, min(self.max_horizontal_speed, self.velocity_x))
        self.x += self.velocity_x

        self.velocity_y += self.gravity
        self.velocity_y += self.auto_lift
        self.velocity_y = min(self.velocity_y, self.max_fall_speed)
        self.y += self.velocity_y

        r = self.get_radius()
        self.x = max(r, min(WIDTH - r, self.x))

        if self.pulse_timer > 0:
            self.pulse_timer -= dt

    def get_radius(self):
        if self.pulse_timer <= 0:
            return self.radius
        t = max(0.0, self.pulse_timer)
        return int(self.radius * (1.0 + 0.20 * math.sin((0.20 - t) * 24)))

    def draw(self, screen):
        r = self.get_radius()
        cx, cy = int(self.x), int(self.y)

        # Soft shadow for depth.
        pygame.draw.ellipse(screen, (100, 120, 140, 80), pygame.Rect(cx - r + 5, cy + r + 12, r * 2 - 8, 12))

        pygame.draw.circle(screen, self.color_shadow, (cx + 2, cy + 3), r)
        pygame.draw.circle(screen, self.color_main, (cx, cy), r)
        pygame.draw.circle(screen, self.color_highlight, (int(cx - r * 0.34), int(cy - r * 0.28)), max(5, r // 4))
        pygame.draw.circle(screen, (255, 220, 225), (int(cx - r * 0.20), int(cy - r * 0.18)), max(2, r // 8))

        knot_w = max(4, r // 3)
        knot_h = max(4, r // 5)
        knot_rect = pygame.Rect(0, 0, knot_w, knot_h)
        knot_rect.center = (cx, cy + r + knot_h // 2 - 1)
        pygame.draw.rect(screen, self.color_knot, knot_rect, border_radius=2)

        wobble = 6 * math.sin(pygame.time.get_ticks() * 0.012)
        string_start = (cx, cy + r + knot_h)
        string_end = (int(cx + wobble), cy + r + 22)
        pygame.draw.line(screen, self.color_knot, string_start, string_end, 2)

    def is_out_of_bounds(self):
        r = self.get_radius()
        return self.y + r < 0 or self.y - r > HEIGHT


class Obstacle:
    TYPES = ("rock", "arrow", "brick")

    def __init__(self, level, target_x):
        self.type = random.choice(self.TYPES)
        self.level = level

        speed_base = 2.5 + level * 0.45
        spawn_side = random.choice(("top", "left", "right"))

        if self.type == "rock":
            self.radius = random.randint(16, 28)
            size = self.radius * 2
            self.rect = pygame.Rect(0, 0, size, size)
        elif self.type == "arrow":
            self.w = random.randint(30, 44)
            self.h = random.randint(16, 24)
            self.rect = pygame.Rect(0, 0, self.w, self.h)
        else:
            self.w = random.randint(32, 56)
            self.h = random.randint(22, 34)
            self.rect = pygame.Rect(0, 0, self.w, self.h)

        if spawn_side == "top":
            self.rect.centerx = random.randint(24, WIDTH - 24)
            self.rect.y = -self.rect.height - random.randint(10, 90)
            self.vx = (target_x - self.rect.centerx) * 0.005 + random.uniform(-0.4, 0.4)
            self.vy = speed_base + random.uniform(0.7, 1.9)
        elif spawn_side == "left":
            self.rect.x = -self.rect.width - random.randint(10, 60)
            self.rect.centery = random.randint(40, HEIGHT - 120)
            self.vx = speed_base + random.uniform(0.6, 1.4)
            self.vy = random.uniform(-0.6, 1.1)
        else:
            self.rect.x = WIDTH + random.randint(10, 60)
            self.rect.centery = random.randint(40, HEIGHT - 120)
            self.vx = -(speed_base + random.uniform(0.6, 1.4))
            self.vy = random.uniform(-0.6, 1.1)

        self.colors = self.pick_colors(level)

    @staticmethod
    def pick_colors(level):
        palettes = [
            ((120, 120, 130), (165, 165, 178)),
            ((152, 92, 76), (196, 136, 102)),
            ((79, 122, 136), (126, 176, 186)),
            ((112, 92, 136), (163, 128, 194)),
            ((94, 136, 94), (150, 196, 145)),
            ((100, 96, 150), (160, 150, 210)),
        ]
        return palettes[level % len(palettes)]

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, screen):
        primary, secondary = self.colors

        if self.type == "rock":
            center = self.rect.center
            pygame.draw.circle(screen, (70, 70, 80), (center[0] + 2, center[1] + 2), self.radius)
            pygame.draw.circle(screen, primary, center, self.radius)
            pygame.draw.circle(screen, secondary, (center[0] - self.radius // 3, center[1] - self.radius // 4), self.radius // 3)

        elif self.type == "brick":
            shadow = self.rect.move(2, 2)
            pygame.draw.rect(screen, (80, 55, 40), shadow, border_radius=4)
            pygame.draw.rect(screen, primary, self.rect, border_radius=4)
            inner = self.rect.inflate(-6, -6)
            pygame.draw.rect(screen, secondary, inner, border_radius=3)
            pygame.draw.line(screen, primary, (inner.left, inner.centery), (inner.right, inner.centery), 2)

        else:
            cx, cy = self.rect.center
            angle = math.atan2(self.vy, self.vx if abs(self.vx) > 0.01 else 0.01)

            tip = (cx + math.cos(angle) * self.w * 0.62, cy + math.sin(angle) * self.w * 0.62)
            back = (cx - math.cos(angle) * self.w * 0.45, cy - math.sin(angle) * self.w * 0.45)
            perp = (-math.sin(angle), math.cos(angle))

            left = (back[0] + perp[0] * self.h * 0.45, back[1] + perp[1] * self.h * 0.45)
            right = (back[0] - perp[0] * self.h * 0.45, back[1] - perp[1] * self.h * 0.45)

            pygame.draw.polygon(screen, (40, 40, 45), [(tip[0] + 2, tip[1] + 2), (left[0] + 2, left[1] + 2), (right[0] + 2, right[1] + 2)])
            pygame.draw.polygon(screen, primary, [tip, left, right])

            tail_left = (back[0] + perp[0] * self.h * 0.18, back[1] + perp[1] * self.h * 0.18)
            tail_right = (back[0] - perp[0] * self.h * 0.18, back[1] - perp[1] * self.h * 0.18)
            tail_end = (back[0] - math.cos(angle) * self.w * 0.25, back[1] - math.sin(angle) * self.w * 0.25)
            pygame.draw.polygon(screen, secondary, [tail_left, tail_right, tail_end])

    def collides_with_player(self, player):
        pr = player.get_radius()
        px, py = player.x, player.y

        if self.type == "rock":
            ox, oy = self.rect.center
            combined = pr + self.radius
            return (px - ox) ** 2 + (py - oy) ** 2 <= combined ** 2

        closest_x = max(self.rect.left, min(px, self.rect.right))
        closest_y = max(self.rect.top, min(py, self.rect.bottom))
        dx = px - closest_x
        dy = py - closest_y
        return dx * dx + dy * dy <= pr * pr

    def is_off_screen(self):
        margin = 120
        return (
            self.rect.right < -margin
            or self.rect.left > WIDTH + margin
            or self.rect.bottom < -margin
            or self.rect.top > HEIGHT + margin
        )


class Coin:
    def __init__(self, level):
        self.radius = 10
        self.x = float(random.randint(30, WIDTH - 30))
        self.y = float(-random.randint(20, 140))

        self.vx = random.uniform(-0.8, 0.8)
        self.vy = 2.1 + level * 0.25 + random.uniform(0.0, 1.2)

        self.pulse = random.uniform(0.0, math.pi * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.pulse += 0.12

    def draw(self, screen):
        r = int(self.radius + math.sin(self.pulse) * 2)
        cx, cy = int(self.x), int(self.y)

        pygame.draw.circle(screen, (185, 130, 30), (cx + 1, cy + 1), r)
        pygame.draw.circle(screen, (245, 210, 60), (cx, cy), r)
        pygame.draw.circle(screen, (255, 238, 134), (cx - 2, cy - 2), max(2, r // 3))

    def collides_with_player(self, player):
        pr = player.get_radius()
        dx = player.x - self.x
        dy = player.y - self.y
        return dx * dx + dy * dy <= (pr + self.radius) ** 2

    def is_off_screen(self):
        margin = 40
        return self.y - self.radius > HEIGHT + margin or self.x < -margin or self.x > WIDTH + margin


class Cloud:
    def __init__(self):
        self.scale = random.uniform(0.7, 1.5)
        self.x = random.uniform(-100, WIDTH + 100)
        self.y = random.uniform(40, HEIGHT - 80)
        # Pixel-per-second speed for natural drift.
        self.speed_y = random.uniform(8.0, 20.0)
        self.speed_x = random.uniform(-4.0, 4.0)
        self.alpha = random.randint(90, 170)

    def update(self, dt, drift):
        self.y += (self.speed_y + drift * 0.10) * dt
        self.x += self.speed_x * dt
        if self.x < -140:
            self.x = WIDTH + 140
        elif self.x > WIDTH + 140:
            self.x = -140
        if self.y - 30 * self.scale > HEIGHT + 30:
            self.y = -40
            self.x = random.uniform(-80, WIDTH + 80)
            self.scale = random.uniform(0.7, 1.5)
            self.speed_y = random.uniform(8.0, 20.0)
            self.speed_x = random.uniform(-4.0, 4.0)
            self.alpha = random.randint(90, 170)

    def draw(self, screen, night_factor):
        surf = pygame.Surface((int(130 * self.scale), int(70 * self.scale)), pygame.SRCALPHA)
        cloud_tint = lerp_color((255, 255, 255), (180, 190, 220), night_factor)
        cloud_alpha = int(lerp(self.alpha, self.alpha * 0.55, night_factor))
        c = (cloud_tint[0], cloud_tint[1], cloud_tint[2], cloud_alpha)
        pygame.draw.ellipse(surf, c, pygame.Rect(8, 20, int(52 * self.scale), int(28 * self.scale)))
        pygame.draw.ellipse(surf, c, pygame.Rect(40, 8, int(56 * self.scale), int(36 * self.scale)))
        pygame.draw.ellipse(surf, c, pygame.Rect(74, 22, int(48 * self.scale), int(26 * self.scale)))
        screen.blit(surf, (self.x - surf.get_width() // 2, self.y - surf.get_height() // 2))


class Game:
    STATE_START = "start"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("georgia", 56, bold=True)
        self.font_ui = pygame.font.SysFont("arial", 28, bold=True)
        self.font_small = pygame.font.SysFont("arial", 22)
        self.font_tiny = pygame.font.SysFont("arial", 18)

        self.high_score = self.load_high_score()

        self.bg_offset = 0.0
        self.clouds = [Cloud() for _ in range(10)]
        self.stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)] for _ in range(50)]

        self.state = self.STATE_START
        self.intro_time = 0.0

        self.touch_active = False
        self.touch_target_x = WIDTH / 2
        self.touch_start_pos = (0.0, 0.0)
        self.touch_start_ms = 0
        self.touch_moved = False

        self.reset_game_data()

    def reset_game_data(self):
        self.player = Player(WIDTH // 2, HEIGHT - 170)
        self.obstacles = []
        self.coins = []

        self.score = 0
        self.level = 1

        self.elapsed = 0.0
        self.level_elapsed = 0.0

        self.obstacle_spawn_timer = 0.0
        self.coin_spawn_timer = 0.0

        self.spawn_obstacle_every = 1.45
        self.spawn_coin_every = 2.2

        self.coin_flash_timer = 0.0

        self.touch_active = False
        self.touch_target_x = self.player.x

    def load_high_score(self):
        if not os.path.exists(HIGHSCORE_FILE):
            return 0
        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip() or 0)
        except (ValueError, OSError):
            return 0

    def save_high_score(self):
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                f.write(str(self.high_score))
        except OSError:
            pass

    def restart(self):
        self.reset_game_data()
        self.state = self.STATE_PLAYING

    def start_game(self):
        self.reset_game_data()
        self.state = self.STATE_PLAYING

    @staticmethod
    def finger_to_screen(fx, fy):
        return fx * WIDTH, fy * HEIGHT

    def on_pointer_down(self, x, y):
        if self.state == self.STATE_START:
            self.start_game()
            return

        if self.state == self.STATE_GAME_OVER:
            self.restart()
            return

        if self.state == self.STATE_PLAYING:
            self.touch_active = True
            self.touch_target_x = x
            self.touch_start_pos = (x, y)
            self.touch_start_ms = pygame.time.get_ticks()
            self.touch_moved = False

    def on_pointer_move(self, x, y):
        if self.state != self.STATE_PLAYING or not self.touch_active:
            return

        self.touch_target_x = x
        sx, sy = self.touch_start_pos
        if abs(x - sx) > 16 or abs(y - sy) > 16:
            self.touch_moved = True

    def on_pointer_up(self, x, y):
        if self.state != self.STATE_PLAYING:
            self.touch_active = False
            return

        self.touch_active = False

        elapsed = pygame.time.get_ticks() - self.touch_start_ms
        sx, sy = self.touch_start_pos
        moved_dist = math.hypot(x - sx, y - sy)

        # Quick tap means "breathe" / boost; dragging is used for steering.
        if elapsed <= 220 and moved_dist <= 18:
            self.player.boost()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.state == self.STATE_START and event.key == pygame.K_SPACE:
                    self.start_game()

                elif self.state == self.STATE_PLAYING and event.key == pygame.K_SPACE:
                    self.player.boost()

                elif self.state == self.STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self.restart()
                    elif event.key == pygame.K_SPACE:
                        self.state = self.STATE_START

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.on_pointer_down(*event.pos)

            if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                self.on_pointer_move(*event.pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.on_pointer_up(*event.pos)

            if event.type == pygame.FINGERDOWN:
                x, y = self.finger_to_screen(event.x, event.y)
                self.on_pointer_down(x, y)

            if event.type == pygame.FINGERMOTION:
                x, y = self.finger_to_screen(event.x, event.y)
                self.on_pointer_move(x, y)

            if event.type == pygame.FINGERUP:
                x, y = self.finger_to_screen(event.x, event.y)
                self.on_pointer_up(x, y)

        return True

    def level_up_if_needed(self):
        level_interval = 18.0
        if self.level_elapsed >= level_interval:
            self.level += 1
            self.level_elapsed = 0.0

            self.spawn_obstacle_every = max(0.42, self.spawn_obstacle_every - 0.10)
            self.spawn_coin_every = max(1.2, self.spawn_coin_every - 0.05)

    def update_playing(self, dt):
        self.elapsed += dt
        self.level_elapsed += dt
        self.score += int(dt * 10)

        keys = pygame.key.get_pressed()
        move_left = bool(keys[pygame.K_LEFT] or keys[pygame.K_a])
        move_right = bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])

        # Touch steering: drag horizontally to guide the balloon.
        if self.touch_active:
            dx = self.touch_target_x - self.player.x
            if dx < -12:
                move_left = True
                move_right = False
            elif dx > 12:
                move_right = True
                move_left = False

        self.player.update(dt, move_left, move_right)

        if self.player.is_out_of_bounds():
            self.end_game()
            return

        self.level_up_if_needed()

        self.obstacle_spawn_timer += dt
        self.coin_spawn_timer += dt

        obstacle_interval = self.spawn_obstacle_every * random.uniform(0.85, 1.15)
        if self.obstacle_spawn_timer >= obstacle_interval:
            self.obstacle_spawn_timer = 0.0
            self.obstacles.append(Obstacle(self.level, self.player.x))

        if self.coin_spawn_timer >= self.spawn_coin_every:
            self.coin_spawn_timer = 0.0
            self.coins.append(Coin(self.level))

        for obstacle in self.obstacles:
            obstacle.update()

        for coin in self.coins:
            coin.update()

        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]
        self.coins = [c for c in self.coins if not c.is_off_screen()]

        for obstacle in self.obstacles:
            if obstacle.collides_with_player(self.player):
                self.end_game()
                return

        collected = []
        for coin in self.coins:
            if coin.collides_with_player(self.player):
                collected.append(coin)

        for coin in collected:
            self.coins.remove(coin)
            self.score += 25
            self.coin_flash_timer = 0.18

        if self.coin_flash_timer > 0:
            self.coin_flash_timer -= dt

        self.bg_offset += (55.0 + self.level * 10.0) * dt
        for cloud in self.clouds:
            cloud.update(dt, 14.0 + self.level * 1.8)

    def update_intro(self, dt):
        self.intro_time += dt
        self.bg_offset += 34.0 * dt
        for cloud in self.clouds:
            cloud.update(dt, 8.0)

    def end_game(self):
        self.state = self.STATE_GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def draw_gradient_background(self):
        # Long-run sky transition: day -> evening -> night.
        if self.state == self.STATE_PLAYING:
            time_progress = max(0.0, min(1.0, self.elapsed / 200.0))
        else:
            time_progress = max(0.0, min(0.35, self.intro_time / 18.0))

        day_top = (82, 172, 223)
        day_mid = (148, 214, 242)
        day_bottom = (240, 248, 255)

        dusk_top = (112, 115, 178)
        dusk_mid = (227, 136, 118)
        dusk_bottom = (255, 206, 170)

        night_top = (16, 26, 58)
        night_mid = (33, 50, 88)
        night_bottom = (66, 83, 116)

        if time_progress < 0.62:
            p = time_progress / 0.62
            top = lerp_color(day_top, dusk_top, p)
            mid = lerp_color(day_mid, dusk_mid, p)
            bottom = lerp_color(day_bottom, dusk_bottom, p)
        else:
            p = (time_progress - 0.62) / 0.38
            top = lerp_color(dusk_top, night_top, p)
            mid = lerp_color(dusk_mid, night_mid, p)
            bottom = lerp_color(dusk_bottom, night_bottom, p)

        for y in range(HEIGHT):
            t = y / HEIGHT
            if t < 0.55:
                tt = t / 0.55
                r = int(top[0] * (1 - tt) + mid[0] * tt)
                g = int(top[1] * (1 - tt) + mid[1] * tt)
                b = int(top[2] * (1 - tt) + mid[2] * tt)
            else:
                tt = (t - 0.55) / 0.45
                r = int(mid[0] * (1 - tt) + bottom[0] * tt)
                g = int(mid[1] * (1 - tt) + bottom[1] * tt)
                b = int(mid[2] * (1 - tt) + bottom[2] * tt)
            self.screen.fill((r, g, b), rect=pygame.Rect(0, y, WIDTH, 1))

        sun_y = 118 + int(math.sin(self.bg_offset * 0.008) * 5)
        sun_alpha = int(lerp(255, 35, time_progress))
        moon_alpha = int(lerp(0, 220, time_progress))

        sun = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(sun, (255, 236, 165, sun_alpha), (62, 60), 42)
        pygame.draw.circle(sun, (255, 248, 215, sun_alpha), (54, 52), 16)
        self.screen.blit(sun, (WIDTH - 130, sun_y - 55))

        moon_y = 122 + int(math.sin(self.bg_offset * 0.006 + 0.9) * 3)
        moon = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(moon, (215, 222, 246, moon_alpha), (56, 60), 28)
        pygame.draw.circle(moon, (145, 160, 198, moon_alpha), (67, 54), 28)
        self.screen.blit(moon, (58, moon_y - 52))

        # Subtle vignette for richer atmosphere at night.
        vignette_strength = int(lerp(0, 85, time_progress))
        if vignette_strength > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((6, 12, 30, vignette_strength))
            self.screen.blit(overlay, (0, 0))

        return time_progress

    def draw_hills(self, time_progress):
        far = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        near = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        far_color = lerp_color((140, 198, 170), (64, 96, 108), time_progress)
        near_color = lerp_color((100, 170, 130), (44, 70, 84), time_progress)
        horizon_glow = lerp_color((255, 212, 165), (90, 108, 146), time_progress)

        glow = pygame.Surface((WIDTH, 170), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (horizon_glow[0], horizon_glow[1], horizon_glow[2], 80), pygame.Rect(-140, 20, WIDTH + 280, 160))
        self.screen.blit(glow, (0, HEIGHT - 210))

        pygame.draw.ellipse(far, (far_color[0], far_color[1], far_color[2], 165), pygame.Rect(-80, HEIGHT - 170, 250, 120))
        pygame.draw.ellipse(far, (far_color[0], far_color[1], far_color[2], 165), pygame.Rect(110, HEIGHT - 190, 270, 145))
        pygame.draw.ellipse(far, (far_color[0], far_color[1], far_color[2], 165), pygame.Rect(300, HEIGHT - 165, 250, 115))

        pygame.draw.ellipse(near, (near_color[0], near_color[1], near_color[2], 215), pygame.Rect(-100, HEIGHT - 120, 260, 110))
        pygame.draw.ellipse(near, (near_color[0], near_color[1], near_color[2], 215), pygame.Rect(90, HEIGHT - 140, 300, 130))
        pygame.draw.ellipse(near, (near_color[0], near_color[1], near_color[2], 215), pygame.Rect(300, HEIGHT - 115, 260, 115))

        self.screen.blit(far, (0, 0))
        self.screen.blit(near, (0, 0))

    def draw_background(self):
        time_progress = self.draw_gradient_background()

        for star in self.stars:
            x, y, size = star
            y2 = (y + self.bg_offset * (0.06 + size * 0.04)) % HEIGHT
            alpha = int(lerp(0, 180, time_progress)) if y2 < HEIGHT * 0.62 else 0
            if alpha > 0:
                s = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 255, alpha), (size + 1, size + 1), size)
                self.screen.blit(s, (int(x), int(y2)))

        for cloud in self.clouds:
            cloud.draw(self.screen, time_progress)

        self.draw_hills(time_progress)

    def draw_ui(self):
        # UI shifts brighter at night for readability.
        ui_dark = (18, 52, 76)
        ui_light = (228, 236, 250)
        t = max(0.0, min(1.0, self.elapsed / 200.0))
        ui_color = lerp_color(ui_dark, ui_light, t)

        score_text = self.font_ui.render(f"Score: {self.score}", True, ui_color)
        level_text = self.font_ui.render(f"Level: {self.level}", True, ui_color)
        high_text = self.font_small.render(f"High: {self.high_score}", True, ui_color)
        controls_text = self.font_tiny.render("Tap: Boost | Drag: Move", True, ui_color)

        self.screen.blit(score_text, (14, 14))
        self.screen.blit(level_text, (14, 48))
        self.screen.blit(high_text, (14, 82))
        self.screen.blit(controls_text, (14, 110))

        if self.coin_flash_timer > 0:
            alpha = int(255 * min(1.0, self.coin_flash_timer / 0.18))
            popup = self.font_small.render("+25", True, (215, 145, 20))
            popup.set_alpha(alpha)
            self.screen.blit(popup, (WIDTH - 88, 24))

    def draw_touch_hint(self):
        if self.state != self.STATE_PLAYING:
            return

        hint_rect = pygame.Rect(WIDTH - 122, HEIGHT - 82, 106, 52)
        box = pygame.Surface((hint_rect.width, hint_rect.height), pygame.SRCALPHA)
        box.fill((255, 255, 255, 115))
        self.screen.blit(box, hint_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), hint_rect, 2, border_radius=10)

        txt = self.font_tiny.render("Tap", True, (25, 66, 92))
        self.screen.blit(txt, txt.get_rect(center=(hint_rect.centerx, hint_rect.centery - 8)))
        txt2 = self.font_tiny.render("Boost", True, (25, 66, 92))
        self.screen.blit(txt2, txt2.get_rect(center=(hint_rect.centerx, hint_rect.centery + 10)))

    def draw_start_screen(self):
        self.draw_background()

        card = pygame.Surface((WIDTH - 46, 300), pygame.SRCALPHA)
        card.fill((245, 252, 255, 210))
        card_rect = card.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 5))
        self.screen.blit(card, card_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), card_rect, 2, border_radius=16)

        t = self.intro_time
        float_y = int(math.sin(t * 2.1) * 8)
        pulse = 1.0 + 0.03 * math.sin(t * 4.2)

        title = self.font_title.render(TITLE, True, (24, 74, 108))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110)))

        # Animated mini balloon in intro.
        intro_r = int(24 * pulse)
        bx, by = WIDTH // 2, HEIGHT // 2 - 50 + float_y
        pygame.draw.circle(self.screen, (255, 88, 108), (bx, by), intro_r)
        pygame.draw.circle(self.screen, (255, 194, 205), (bx - 7, by - 8), 7)
        pygame.draw.rect(self.screen, (130, 50, 50), pygame.Rect(bx - 4, by + intro_r - 1, 8, 6), border_radius=2)
        pygame.draw.line(self.screen, (130, 50, 50), (bx, by + intro_r + 4), (bx, by + intro_r + 20), 2)

        prompt_alpha = int(160 + 95 * (0.5 + 0.5 * math.sin(t * 3.2)))
        prompt = self.font_small.render("Tap Anywhere to Start", True, (28, 84, 118))
        prompt.set_alpha(prompt_alpha)
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 24)))

        c1 = self.font_tiny.render("Tap = Breathe Boost", True, (37, 92, 122))
        c2 = self.font_tiny.render("Drag = Move Left/Right", True, (37, 92, 122))
        c3 = self.font_tiny.render("Keyboard: SPACE + Arrows", True, (37, 92, 122))
        self.screen.blit(c1, c1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 68)))
        self.screen.blit(c2, c2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 92)))
        self.screen.blit(c3, c3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 116)))

        high_text = self.font_small.render(f"High Score: {self.high_score}", True, (30, 68, 98))
        self.screen.blit(high_text, high_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 158)))

    def draw_game_over(self):
        self.draw_background()

        for coin in self.coins:
            coin.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.player.draw(self.screen)

        panel = pygame.Surface((WIDTH - 66, 248), pygame.SRCALPHA)
        panel.fill((240, 248, 255, 225))
        panel_rect = panel.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(panel, panel_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, 2, border_radius=14)

        over = self.font_title.render("Game Over", True, (145, 40, 40))
        score = self.font_ui.render(f"Score: {self.score}", True, (35, 60, 90))
        high = self.font_ui.render(f"High Score: {self.high_score}", True, (35, 60, 90))
        retry = self.font_small.render("Tap to Restart", True, (35, 60, 90))
        menu = self.font_tiny.render("(R to restart, SPACE for start menu)", True, (35, 60, 90))

        self.screen.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))
        self.screen.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 12)))
        self.screen.blit(high, high.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 28)))
        self.screen.blit(retry, retry.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 78)))
        self.screen.blit(menu, menu.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 108)))

    def draw_playing(self):
        self.draw_background()

        for coin in self.coins:
            coin.draw(self.screen)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        self.player.draw(self.screen)
        self.draw_ui()
        self.draw_touch_hint()

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events()

            if self.state == self.STATE_PLAYING:
                self.update_playing(dt)
            else:
                self.update_intro(dt)

            if self.state == self.STATE_START:
                self.draw_start_screen()
            elif self.state == self.STATE_PLAYING:
                self.draw_playing()
            else:
                self.draw_game_over()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
