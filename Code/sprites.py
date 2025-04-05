from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join("Images", "player.png")).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 100))
        self.direction = pygame.Vector2()
        self.speed = PLAYER_SPEED
        self.can_shoot = True
        self.shoot_time = 0
        self.cooldown_duration = 500
        self.invincible = False

    def boundaries(self):
        if self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]) or int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = 0
        self.rect.center += self.direction * self.speed * dt
        self.boundaries()
        
        if self.invincible:
            self.image = pygame.image.load(join("Images", "playerinvincible.png")).convert_alpha()
        else:
            self.image = pygame.image.load(join("Images", "player.png")).convert_alpha()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, spawnx):
        super().__init__(groups)
        self.image = pygame.image.load(join("Images", "enemy.png")).convert_alpha()
        self.rect = self.image.get_frect(midtop = (WINDOW_WIDTH / 2, 20))
        self.ychange = 100
        self.speed = ENEMY_SPEED
        self.direction = pygame.Vector2(1,0)
        self.rect.centerx = spawnx

    def boundaries(self):
        if self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
            self.rect.y += self.ychange
            self.direction.x *= -1

        if self.rect.left <= 0:
            self.rect.left = 0
            self.rect.y += self.ychange
            self.direction.x *= -1

    def move(self, dt):
        self.rect.center += self.direction * self.speed * dt
    
    def update(self, dt):
        self.boundaries()
        self.move(dt)

class TeleportEnemy(Enemy):
    def __init__(self, groups):
        super().__init__(groups, spawnx=0)
        self.image = pygame.image.load(join("Images", "teleporter.png")).convert_alpha()
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH - 40), randint(0, WINDOW_HEIGHT - 200)))
        self.last_teleport_time = pygame.time.get_ticks()
        self.teleport_interval = 2000
        self.times_teleported = 0
        self.is_over = False

    def move(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_teleport_time  > self.teleport_interval:
            self.rect.center = (randint(0, WINDOW_WIDTH - 40), randint(0, WINDOW_HEIGHT - 200))
            self.last_teleport_time = current_time
            self.times_teleported += 1
        if self.times_teleported > 3:
            self.is_over = True

    def update(self, dt):
        self.move()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, groups, player):
        super().__init__(groups)
        self.image = pygame.image.load(join("Images", "bullet.png")).convert_alpha()
        self.player = player
        self.rect = self.image.get_frect(center = self.player.rect.midtop)
        self.direction = pygame.Vector2(0, -1)

    def move(self, dt):
        self.rect.centery -= BULLET_SPEED * dt
        if self.rect.bottom <= 0:
            self.kill()

    def update(self, dt):
        self.move(dt)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, groups, enemy, boss):
        super().__init__(groups)
        self.original_img = pygame.image.load(join("Images", "bullet.png")).convert_alpha()
        self.image = pygame.transform.rotozoom(self.original_img, 180, 1)
        self.rect = self.image.get_frect(center = enemy.rect.center) if not boss else self.image.get_frect(midtop = (randint(0, WINDOW_WIDTH), 0))
        self.speed = ENEMY_BULLET_MOVING_SPEED

    def move(self, dt):
        self.rect.centery += self.speed * dt
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.kill()

    def update(self, dt):
        self.move(dt)

class PowerupItem(pygame.sprite.Sprite):
    def __init__(self, groups, enemy, surf):
        super().__init__(groups)
        self.image = pygame.image.load(surf).convert_alpha()
        self.rect = self.image.get_frect(center = enemy.rect.center)
        self.speed = POWERUP_MOVING_SPEED

    def move(self, dt):
        self.rect.centery += self.speed * dt
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.kill()

    def update(self, dt):
        self.move(dt)

class DangerSign(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.image = pygame.image.load(join("Images", "danger.png")).convert_alpha()
        self.pos = (pos[0], pos[1])
        self.rect = self.image.get_frect(center = self.pos)

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, danger_sign):
        super().__init__(groups)
        self.danger_sign = danger_sign
        self.image = pygame.Surface((randint(50,150),WINDOW_HEIGHT))
        self.rect = self.image.get_frect(midtop = (self.danger_sign.pos[0], 0))
        pygame.Surface.fill(self.image, (255,0,0))

class Boss(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join("Images", "boss.png")).convert_alpha()
        self.rect = self.image.get_frect(midbottom = (WINDOW_WIDTH/2, -100))
        self.speed = BOSS_MOVING_SPEED
        self.direction = pygame.Vector2(1,0)
        self.lives = 10
        self.anim = True

    def spawn_anim(self):
        if self.rect.midbottom[1] < 475:
            self.direction.x = 0
            self.direction.y = 1
            self.anim = True
        else:
            self.direction.x = choice([-1, 1])
            self.direction.y = 0
            self.anim = False
    
    def randomize_direction(self):
        self.direction.x *= -1
    
    def boundaries(self):
        if self.rect.right >= WINDOW_WIDTH:
            self.direction.x *= -1
        if self.rect.left <= 0:
            self.direction.x *= -1
    
    def move(self, dt):
        self.rect.center += self.direction * self.speed * dt
    
    def update(self, dt):
        self.move(dt)
        self.boundaries()
        if self.anim:
            self.spawn_anim()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.size = randint(10, 50)
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.rotation = randint(-20,20)
        self.image = pygame.transform.rotate(self.image, self.rotation)
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))
