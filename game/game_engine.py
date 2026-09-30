import random
import pygame
from game.block import Block, Debris


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.block_height = 28
        self.base_width = 180
        self.background_thresholds = (0, 5, 10, 20)
        self.background_colours = [
            ((70, 120, 190), (18, 35, 75)),
            ((105, 70, 155), (30, 18, 60)),
            ((28, 48, 105), (6, 12, 32)),
            ((12, 18, 30), (0, 0, 5)),
        ]

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 28)
        self.font_big = pygame.font.SysFont(None, 46)

        self.reset()

    def get_color(self, index):
        palette = [
            (230, 75, 75),   # Crimson
            (240, 140, 45),  # Orange
            (245, 210, 50),  # Gold
            (60, 195, 110),  # Green
            (50, 150, 240),  # Blue
            (165, 80, 225),  # Purple
        ]
        return palette[index % len(palette)]

    def generate_stars(self):
        rng = random.Random(1337)
        stars = []
        for _ in range(90):
            stars.append(
                (
                    rng.randrange(self.width),
                    rng.randrange(self.height),
                    rng.choice([1, 1, 1, 2]),
                    rng.randrange(150, 256),
                )
            )
        return stars

    def get_background_colour(self):
        tower_height = max(0, len(self.stack) - 1)
        thresholds = self.background_thresholds

        if tower_height >= thresholds[-1]:
            top_colour, bottom_colour = self.background_colours[-1]
            return top_colour, bottom_colour, 1.0

        for index in range(len(thresholds) - 1):
            start = thresholds[index]
            end = thresholds[index + 1]
            if tower_height < end:
                progress = (tower_height - start) / (end - start)
                start_top, start_bottom = self.background_colours[index]
                end_top, end_bottom = self.background_colours[index + 1]
                top_colour = self._interpolate_colour(start_top, end_top, progress)
                bottom_colour = self._interpolate_colour(start_bottom, end_bottom, progress)
                night_strength = max(0.0, min(1.0, (tower_height - thresholds[1]) / (thresholds[2] - thresholds[1])))
                return top_colour, bottom_colour, night_strength

        return self.background_colours[-1][0], self.background_colours[-1][1], 1.0

    def _interpolate_colour(self, start_colour, end_colour, progress):
        progress = max(0.0, min(1.0, progress))
        return tuple(
            int(start_channel + (end_channel - start_channel) * progress)
            for start_channel, end_channel in zip(start_colour, end_colour)
        )

    def draw_stars(self, screen, night_strength):
        if night_strength <= 0:
            return

        for x, y, radius, brightness in self.stars:
            star_brightness = int(brightness * night_strength)
            colour = (star_brightness, star_brightness, min(255, star_brightness + 20))
            pygame.draw.circle(screen, colour, (x, y), radius)

    def draw_background(self, screen):
        top_colour, bottom_colour, night_strength = self.get_background_colour()
        denominator = max(1, self.height - 1)

        for y in range(self.height):
            progress = y / denominator
            colour = self._interpolate_colour(top_colour, bottom_colour, progress)
            pygame.draw.line(screen, colour, (0, y), (self.width, y))

        self.draw_stars(screen, night_strength)

    def reset(self):
        self.score = 0
        self.game_over = False
        self.perfect_streak = 0
        self.perfect_popup_frames = 0
        self.perfect_tolerance = 3.0
        self.perfect_bonus = 2
        self.perfect_restore_amount = 10.0
        self.perfect_popup_duration = 60
        self.debris = []
        self.stars = self.generate_stars()

        base_x = (self.width - self.base_width) // 2
        base_y = self.height - 60
        base_block = Block(base_x, base_y, self.base_width, self.block_height, self.get_color(0), speed=0)
        self.stack = [base_block]

        self.spawn_active_block()

    def spawn_active_block(self):
        top_block = self.stack[-1]
        next_y = top_block.y - self.block_height - 4
        speed = min(10.0, 4.5 + (len(self.stack) * 0.35))
        color = self.get_color(len(self.stack))

        start_x = 25 if random.choice([True, False]) else self.width - 25 - top_block.width
        self.active_block = Block(start_x, next_y, top_block.width, self.block_height, color, speed=speed)

    def drop_block(self):
        if self.game_over:
            return

        top_block = self.stack[-1]
        act = self.active_block

        left = max(act.x, top_block.x)
        right = min(act.x + act.width, top_block.x + top_block.width)
        overlap = right - left
        
        is_successful_drop = overlap > 0
        
        if is_successful_drop:
            is_perfect = abs(act.x - top_block.x) <= self.perfect_tolerance

            if is_perfect:
                self.perfect_streak += 1
                self.perfect_popup_frames = self.perfect_popup_duration
                new_width = max(10.0, min(self.base_width, act.width))
                new_x = act.x
                self.score += 1 + self.perfect_bonus

                if self.perfect_streak % 3 == 0:
                    new_width = min(self.base_width, new_width + self.perfect_restore_amount)
                    center_x = act.x + act.width / 2
                    new_x = center_x - new_width / 2
                    new_x = max(20.0, min(new_x, self.width - 20.0 - new_width))
            else:
                self.perfect_streak = 0
                new_width = max(10.0, overlap)
                new_x = left
                self.score += 1

                left_overhang = top_block.x - act.x
                if left_overhang > 0:
                    self.debris.append(
                        Debris(
                            act.x,
                            act.y,
                            left_overhang,
                            self.block_height,
                            act.color,
                            velocity_x=-2.5,
                            velocity_y=-2.0,
                            angular_velocity=-7.0,
                        )
                    )

                right_overhang = act.x + act.width - (top_block.x + top_block.width)
                if right_overhang > 0:
                    self.debris.append(
                        Debris(
                            top_block.x + top_block.width,
                            act.y,
                            right_overhang,
                            self.block_height,
                            act.color,
                            velocity_x=2.5,
                            velocity_y=-2.0,
                            angular_velocity=7.0,
                        )
                    )

            new_block = Block(new_x, act.y, new_width, self.block_height, act.color, speed=0)
            self.stack.append(new_block)

            if new_block.y < 180:
                shift_amount = self.block_height + 4
                for b in self.stack:
                    b.y += shift_amount
                for debris in self.debris:
                    debris.y += shift_amount

            self.spawn_active_block()
        else:
            self.game_over = True

    def handle_event(self, event):
        if self.game_over:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_r) or \
               (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.reset()
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.drop_block()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drop_block()

    def update(self):
        if not self.game_over:
            self.active_block.update(self.width)
        if self.perfect_popup_frames > 0:
            self.perfect_popup_frames -= 1
        for debris in self.debris:
            debris.update()
        self.debris = [
            debris
            for debris in self.debris
            if not debris.is_off_screen(self.width, self.height)
        ]

    def render(self, screen):
        self.draw_background(screen)

        title_surf = self.font_title.render("Skyscraper Stack", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 16))

        height = len(self.stack) - 1
        height_surf = self.font_hud.render(f"Height: {height}", True, (255, 220, 80))
        screen.blit(height_surf, (self.width // 2 - height_surf.get_width() // 2, 54))

        score_surf = self.font_hud.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 82))

        if self.perfect_popup_frames > 0:
            perfect_surf = self.font_hud.render("PERFECT!", True, (255, 215, 50))
            screen.blit(perfect_surf, (self.width // 2 - perfect_surf.get_width() // 2, 110))

        for b in self.stack:
            b.render(screen)

        for debris in self.debris:
            debris.render(screen)

        if not self.game_over:
            self.active_block.render(screen)

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 195))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_big.render("TOWER COLLAPSED!", True, (240, 75, 75))
            screen.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 40))

            final_height_surf = self.font_hud.render(f"Final Height: {len(self.stack) - 1}", True, (255, 255, 255))
            screen.blit(final_height_surf, (self.width // 2 - final_height_surf.get_width() // 2, self.height // 2 + 10))

            final_score_surf = self.font_hud.render(f"Final Score: {self.score}", True, (255, 255, 255))
            screen.blit(final_score_surf, (self.width // 2 - final_score_surf.get_width() // 2, self.height // 2 + 42))

            restart_surf = self.font_hud.render("Press [R] or Left-Click to Play Again", True, (200, 200, 200))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 74))
