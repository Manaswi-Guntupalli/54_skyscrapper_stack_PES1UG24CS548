import pygame

class Block:
    def __init__(self, x, y, width, height, color, speed=0):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.color = color
        self.speed = speed
        self.direction = 1

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def update(self, screen_width):
        if self.speed == 0:
            return

        self.x += self.speed * self.direction
        if self.x <= 20:
            self.x = 20
            self.direction = 1
        elif self.x + self.width >= screen_width - 20:
            self.x = screen_width - 20 - self.width
            self.direction = -1

    def render(self, surface):
        draw_rect = self.rect
        pygame.draw.rect(surface, self.color, draw_rect, border_radius=4)
        pygame.draw.rect(surface, (245, 245, 250), draw_rect, width=2, border_radius=4)


class Debris:
    def __init__(self, x, y, width, height, color, velocity_x, velocity_y=-2.0, angular_velocity=0.0):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.color = color
        self.velocity_x = float(velocity_x)
        self.velocity_y = float(velocity_y)
        self.angular_velocity = float(angular_velocity)
        self.angle = 0.0
        self.gravity = 0.35

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        self.angle += self.angular_velocity

    def is_off_screen(self, screen_width, screen_height):
        return (
            self.x + self.width < -50
            or self.x > screen_width + 50
            or self.y > screen_height + 50
        )

    def render(self, surface):
        debris_surface = pygame.Surface(
            (max(1, int(round(self.width))), max(1, int(round(self.height)))),
            pygame.SRCALPHA,
        )
        debris_rect = debris_surface.get_rect()
        pygame.draw.rect(debris_surface, self.color, debris_rect, border_radius=4)
        pygame.draw.rect(debris_surface, (245, 245, 250), debris_rect, width=2, border_radius=4)

        rotated_surface = pygame.transform.rotate(debris_surface, self.angle)
        rotated_rect = rotated_surface.get_rect(
            center=(int(self.x + self.width / 2), int(self.y + self.height / 2))
        )
        surface.blit(rotated_surface, rotated_rect)
