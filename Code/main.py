from settings import *
from sprites import *
from custom_timer import Timer
import json

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.running = True
        self.is_game_over = False
        self.timers = []

        self.elapsed_time = None
        
        self.enemies_killed = 0
        self.last_hit_time = 0
        self.is_already_new_highscore = False
        self.new_highscore_time = None
        self.new_highscore_duration = 3500
        
        self.slowed = False
        self.frozen = False
        self.rapid_fire = False
        
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset = (0,0)
        
        self.last_boss_fight_score = 0
        self.is_boss_active = False

        self.double_points = False

        self.muted = True
        self.paused = False
        
        self.flash_heart = False
        self.flash_timer_in_arr = False
        self.life_is_white = False
        
        self.shots_hit = 0
        self.shots_missed = 0
        self.accuracy = 0
        
        self.can_break_shield = False
        self.explosion_frames = [pygame.image.load(join("Images", "Explosions", f"{i}.png")).convert_alpha() for i in range(21)]

        self.all_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_bullet_sprites = pygame.sprite.Group()
        self.heart_sprites = pygame.sprite.Group()
        self.laser_sprites = pygame.sprite.Group()
        self.shield_sprites = pygame.sprite.Group()
        self.speed_boost_sprites = pygame.sprite.Group()
        self.slow_time_sprites = pygame.sprite.Group()
        self.rapid_fire_sprites = pygame.sprite.Group()
        self.powerup_sprites = pygame.sprite.Group()
        self.double_points_sprites = pygame.sprite.Group()
        self.teleport_enemies = pygame.sprite.Group()
        self.star_sprites = pygame.sprite.Group()
        self.freeze_time_sprites = pygame.sprite.Group()
        self.nuke_sprites = pygame.sprite.Group()
        self.break_shield_sprites = pygame.sprite.Group()
        
        self.all_groups = [
            self.all_sprites,
            self.enemy_sprites,
            self.bullet_sprites,
            self.enemy_bullet_sprites,
            self.heart_sprites,
            self.laser_sprites,
            self.shield_sprites,
            self.speed_boost_sprites,
            self.slow_time_sprites,
            self.rapid_fire_sprites,
            self.powerup_sprites,
            self.double_points_sprites,
            self.teleport_enemies,
            self.star_sprites,
            self.freeze_time_sprites,
            self.nuke_sprites,
            self.break_shield_sprites
        ]

        for _ in range(randint(20,30)):
            Star(self.all_sprites, pygame.image.load(join("Images", "star.png")).convert_alpha())

        self.player = Player(self.all_sprites)
        self.lives_remaining = 3
        self.at_one_life = False

        for _ in range(5):
            enemy = Enemy((self.all_sprites, self.enemy_sprites), randint(0, WINDOW_WIDTH))
            if enemy.has_shield:
                PowerupItem((self.all_sprites, self.break_shield_sprites, self.powerup_sprites), enemy, join("Images", "breakshield.png"))

        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, randint(1000,2000))

        self.enemy_bullet_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_bullet_event, randint(300,550))
        
        self.heart_event = pygame.event.custom_type()
        pygame.time.set_timer(self.heart_event, randint(7000,10000))
        
        self.slow_time_event = pygame.event.custom_type()
        pygame.time.set_timer(self.slow_time_event, randint(14000, 15000))
        self.reset_time = pygame.event.custom_type()
        
        self.shield_event = pygame.event.custom_type()
        pygame.time.set_timer(self.shield_event, randint(15000,18000))
        self.end_invincibility = pygame.event.custom_type()
        
        self.rapid_fire_event = pygame.event.custom_type()
        pygame.time.set_timer(self.rapid_fire_event, randint(17000, 18000))
        self.end_rapid_fire = pygame.event.custom_type()
        
        self.warning_event = pygame.event.custom_type()
        pygame.time.set_timer(self.warning_event, randint(9000,12000))
        
        self.speed_boost_event = pygame.event.custom_type()
        pygame.time.set_timer(self.speed_boost_event, randint(11000,13000))
        self.end_speed_boost = pygame.event.custom_type()
        
        self.double_points_event = pygame.event.custom_type()
        pygame.time.set_timer(self.double_points_event, randint(15000,17000))
        self.end_double_points = pygame.event.custom_type()

        self.freeze_time_event = pygame.event.custom_type()

        pygame.time.set_timer(self.freeze_time_event, randint(15000,20000))
        
        self.laser_event = pygame.event.custom_type()
        self.delete_laser_event = pygame.event.custom_type()
        
        self.randomize_boss = pygame.event.custom_type()
        
        self.spawn_teleport_enemy = pygame.event.custom_type()
        pygame.time.set_timer(self.spawn_teleport_enemy, randint(15000, 20000))
        
        self.check_nuke_timer = Timer(5000, self.check_nuke, True, True)
        self.timers.append(self.check_nuke_timer)

        self.music = pygame.mixer.Sound(join("Audio", "music.mp3"))
        self.music.play(loops=-1)
        self.shoot_sound = pygame.mixer.Sound(join("Audio", "bullet.mp3"))
        self.impact_sound = pygame.mixer.Sound(join("Audio", "impact.ogg"))
        self.explosion_sound = pygame.mixer.Sound(join("Audio", "explosion.wav"))
        self.beep_sound = pygame.mixer.Sound(join("Audio", "beep.wav"))
        self.powerup_sound = pygame.mixer.Sound(join("Audio", "powerup.mp3"))
        self.whoosh_sound = pygame.mixer.Sound(join("Audio", "whoosh.wav"))
        self.alarm_sound = pygame.mixer.Sound(join("Audio", "alarm.mp3"))
        self.laser_sound = pygame.mixer.Sound(join("Audio", "laser.wav"))
        
        self.all_sounds = [
            self.music,
            self.shoot_sound,
            self.impact_sound,
            self.explosion_sound,
            self.beep_sound,
            self.powerup_sound,
            self.whoosh_sound,
            self.alarm_sound,
            self.laser_sound,
        ]

    def input(self):
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.player.can_shoot:
            self.bullet = Bullet((self.all_sprites, self.bullet_sprites), self.player)
            self.shoot_sound.play()
            self.player.can_shoot = False
            self.player.shoot_time = pygame.time.get_ticks()

    def collision_logic(self, a, b, func):
        for sprite in b:
            if pygame.sprite.spritecollide(a, b, False, pygame.sprite.collide_mask):
                sprite.kill()
                func()

    def screen_shake(self, dt):
        if self.shake_duration > 0:
            self.shake_intensity = max(self.shake_intensity-(50 * dt), 0)

            offset_x = randint(-int(self.shake_intensity), int(self.shake_intensity))
            offset_y = randint(-int(self.shake_intensity), int(self.shake_intensity))

            self.shake_offset = (offset_x, offset_y)

            self.shake_duration -= dt
        else:
            self.shake_offset = (0, 0)

    def activate_shield(self):
        self.powerup_sound.play()
        self.player.invincible = True
        pygame.time.set_timer(self.end_invincibility, 5000)

    def kill_player(self):
        if not self.player.invincible:
            self.lives_remaining = 0

    def gain_life(self):
        self.powerup_sound.play()
        self.lives_remaining += 1
        if self.lives_remaining == 2:
            self.timers = []
            self.flash_timer_in_arr = False
            self.beep_sound.stop()

    def minus_life(self):
        current_time = pygame.time.get_ticks()
        if not self.player.invincible:
            if current_time - self.last_hit_time > 10:
                self.last_hit_time = pygame.time.get_ticks()
                self.lives_remaining -= 1
                self.impact_sound.play()
                self.shake_duration = 300
                self.shake_intensity = 50

    def activate_speed_boost(self):
        self.powerup_sound.play()
        self.player.speed = 900
        pygame.time.set_timer(self.end_speed_boost, 5000)

    def activate_rapidfire(self):
        self.powerup_sound.play()
        self.rapid_fire = True
        pygame.time.set_timer(self.end_rapid_fire, 5000)

    def slow_time(self):
        self.powerup_sound.play()
        self.slowed = True
        pygame.time.set_timer(self.reset_time, 5000)

    def freeze_time(self):
        self.powerup_sound.play()
        self.frozen = True
        pygame.time.set_timer(self.reset_time, 5000)

    def double_points_func(self):
        self.powerup_sound.play()
        self.double_points = True
        pygame.time.set_timer(self.end_double_points, 5000)

    def BLOW_UP_NUKE(self):
        self.explosion_sound.play()
        self.nuke_sprites.empty()
        for enemy in self.enemy_sprites:
            enemy.kill()
            Explosion(self.all_sprites, self.explosion_frames, enemy.rect.center)
        for bullet in self.enemy_bullet_sprites:
            bullet.kill()
        for powerup in self.powerup_sprites:
            powerup.kill()
        self.enemies_killed += 30
        self.shake_duration = 2000
        self.shake_intensity = 100

    def check_nuke(self):
        random_num = randint(1,100)
        if random_num == 1:
            self.alarm_sound.play(loops=2)
            if self.enemy_sprites:
                PowerupItem((self.all_sprites, self.nuke_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), join("Images", "nuke.png"))

    def turn_on_break_shield(self):
        self.can_break_shield = True
        self.powerup_sound.play()

    def check_collisions(self):
        self.collision_logic(self.player, self.shield_sprites, lambda: self.activate_shield())
        self.collision_logic(self.player, self.heart_sprites, lambda: self.gain_life())
        self.collision_logic(self.player, self.speed_boost_sprites, lambda: self.activate_speed_boost())
        self.collision_logic(self.player, self.rapid_fire_sprites, lambda: self.activate_rapidfire())
        self.collision_logic(self.player, self.slow_time_sprites, lambda: self.slow_time())
        self.collision_logic(self.player, self.laser_sprites, lambda: self.kill_player())
        self.collision_logic(self.player, self.enemy_bullet_sprites, lambda: self.minus_life())
        self.collision_logic(self.player, self.double_points_sprites, lambda: self.double_points_func())
        self.collision_logic(self.player, self.freeze_time_sprites, lambda: self.freeze_time())
        self.collision_logic(self.player, self.nuke_sprites, lambda: self.BLOW_UP_NUKE())
        self.collision_logic(self.player, self.break_shield_sprites, lambda: self.turn_on_break_shield())
        
        for enemy in self.teleport_enemies:
            if enemy.is_over:
                self.kill_player()  

        for bullet in self.bullet_sprites:
            enemies_hit = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask) \
                or pygame.sprite.spritecollide(bullet, self.teleport_enemies, True, pygame.sprite.collide_mask)
            if enemies_hit:
                bullet.kill()
                for enemy in enemies_hit:
                    if not enemy.has_shield or (enemy.has_shield and self.can_break_shield):
                        self.can_break_shield = False
                        enemy.lives -= 1
                        if enemy.lives <= 0:
                            self.explosion_sound.play()
                            enemy.kill()
                            Explosion(self.all_sprites, self.explosion_frames, enemy.rect.center)
            self.enemies_killed += len(enemies_hit) * 2 if self.double_points else len(enemies_hit)
            self.shots_hit += len(enemies_hit)

        for enemy in self.enemy_sprites:
            if enemy.rect.top > 570:
                enemy.kill()
                if not self.player.invincible:
                    self.minus_life()

        if hasattr(self, "boss") and self.boss.alive():
            for bullet in self.bullet_sprites:
                if pygame.sprite.collide_mask(bullet, self.boss):
                    self.shots_hit += 1
                    bullet.kill()
                    self.boss.lives -= 1
                    if self.boss.lives <= 0:
                        self.shake_duration = 2000
                        self.shake_intensity = 100
                        self.boss.kill()
                        self.is_boss_active = False
                        self.enemies_killed += 5
                        self.explosion_sound.play()
                        pygame.time.set_timer(self.enemy_bullet_event, randint(300,550))
            pygame.time.set_timer(self.enemy_event, randint(1000,2000))

    def flash_life(self):
        self.flash_heart = not self.flash_heart

    def game_over(self):
        if self.lives_remaining <= 0 and not self.is_game_over:
            if self.enemies_killed > int(self.highscore):
                self.highscore = self.enemies_killed
            with open(join("Data", "score.txt"), "w") as score_file:
                json.dump(self.highscore, score_file)
            self.is_game_over = True
            self.elapsed_time = pygame.time.get_ticks() / 1000

    def display_game_over(self):
        if self.is_game_over:
            font = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 100)
            small_font = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 30)
            
            text_surf = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text_surf.get_frect(center = (WINDOW_WIDTH/2, (WINDOW_HEIGHT/2) - 40))
            
            restart_text_surf = small_font.render("R to restart, Q to quit", True, (0,0,255))
            restart_text_rect = restart_text_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 250))

            self.display_surface.blit(text_surf, text_rect)
            self.display_surface.blit(restart_text_surf, restart_text_rect)
            
            if self.shots_missed + self.shots_hit > 0:
                self.accuracy = self.shots_hit / (self.shots_missed + self.shots_hit) * 100
            else:
                self.accuracy = 0
            
            for group in self.all_groups:
                group.empty()
            for sound in self.all_sounds:
                sound.stop()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.__init__()
            elif keys[pygame.K_q]:
                self.running = False

    def display_highscore(self):
        try:
            with open(join("Data", "score.txt")) as score_file:
                self.highscore = json.load(score_file)
        except:
            self.highscore = 0

        if self.enemies_killed > int(self.highscore) and not self.is_already_new_highscore:
            self.new_highscore_time = pygame.time.get_ticks()
            self.highscore = self.enemies_killed
            self.is_already_new_highscore = True

        if self.new_highscore_time and pygame.time.get_ticks() - self.new_highscore_time < self.new_highscore_duration:
            font_ = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 50)
            new_highscore_text = font_.render("NEW HIGHSCORE!", True, (255, 255, 0))
            new_highscore_rect = new_highscore_text.get_frect(topright = (WINDOW_WIDTH-20, 20))
            self.display_surface.blit(new_highscore_text, new_highscore_rect)

        if not self.is_game_over:
            font = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 30)
            score_text = font.render(f"HIGHSCORE: {self.highscore}", True, (255,255,255))
            score_rect = score_text.get_frect(topleft = (0,30))
        else:
            font = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 50)
            score_text = font.render(f"HIGHSCORE: {self.highscore}", True, (255,255,255))
            score_rect = score_text.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 100))
        self.display_surface.blit(score_text, score_rect)

    def display_accuracy(self):
        font = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 50)
        accuracy_text_surf = font.render(f"ACCURACY: {self.accuracy:.2f}%", True, (255, 255, 255))
        accuracy_text_rect = accuracy_text_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 150))
        self.display_surface.blit(accuracy_text_surf, accuracy_text_rect)

    def display_time_survived(self):
        font = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 50)
        time_text_surf = font.render(f"TIME SURVIVED: {self.elapsed_time}s", True, (255, 255, 255))
        time_text_rect = time_text_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 200))
        self.display_surface.blit(time_text_surf, time_text_rect)

    def boss_fight(self):
        if self.enemies_killed % 20 == 0 and self.enemies_killed != 0 and self.enemies_killed != self.last_boss_fight_score or \
            (self.enemies_killed % 20) - 1 == 0 and self.double_points and self.enemies_killed != 0 and self.enemies_killed != self.last_boss_fight_score:
            self.last_boss_fight_score = self.enemies_killed
            self.is_boss_active = True
            pygame.time.set_timer(self.enemy_event, 0)
            for sprite in self.enemy_sprites:
                sprite.kill()
            self.boss = Boss(self.all_sprites)
            pygame.time.set_timer(self.randomize_boss, randint(2000,5000))
            pygame.time.set_timer(self.enemy_bullet_event, randint(100,150))

    def gun_timer(self):
        if not self.player.can_shoot:
            self.current_time = pygame.time.get_ticks()
            if self.current_time - self.player.shoot_time >= self.player.cooldown_duration:
                self.player.can_shoot = True

    def display_fps(self):
        font = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 30)
        if self.clock.get_fps() <= 30:
            text_surf = font.render("FPS: " + str(round(self.clock.get_fps(), 2)), True, (255, 0, 0))
        elif self.clock.get_fps() <= 60:
            text_surf = font.render("FPS: " + str(round(self.clock.get_fps(), 2)), True, (255, 255, 0))
        else:
            text_surf = font.render("FPS: " + str(round(self.clock.get_fps(), 2)), True, (0, 255, 0))
        text_rect = text_surf.get_frect(topleft = (0, 60))
        self.display_surface.blit(text_surf, text_rect)

    def display_lives(self):
        lives_img = pygame.image.load(join("Images", "life.png"))
        lives_img_white = pygame.image.load(join("Images", "whitecircle.png"))
        lives_img_width = lives_img.get_width()
        total_width = self.lives_remaining * lives_img_width

        start_x = (WINDOW_WIDTH - total_width) / 2
        x = start_x 
        for _ in range(self.lives_remaining):
            if self.flash_heart:
                self.life_is_white = True
                self.display_surface.blit(lives_img_white, (x,10))
            else:
                self.life_is_white = False
                self.display_surface.blit(lives_img, (x, 10))
            if not self.at_one_life and self.life_is_white:
                self.display_surface.blit(lives_img, (x, 10))
            x += lives_img_width + 10

    def display_score(self):
        if not self.is_game_over:
            font = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 30)
            score_text = font.render(f"SCORE: {self.enemies_killed}", True, (255,255,255))
            score_rect = score_text.get_frect(topleft = (0,0))
        else:
            font = pygame.font.Font(join("Fonts", "Oxanium-Bold.ttf"), 50)
            score_text = font.render(f"SCORE: {self.enemies_killed}", True, (255,255,255))
            score_rect = score_text.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50))
        self.display_surface.blit(score_text, score_rect)

    def display_volume(self):
        surf = pygame.image.load(join("Images", "unmuted.png")) if not self.muted else pygame.image.load(join("Images", "muted.png"))
        rect = surf.get_frect(topleft = (0,80))
        self.display_surface.blit(surf, rect)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused

                if event.type == self.enemy_event:
                    self.enemy = Enemy((self.all_sprites, self.enemy_sprites), randint(0, WINDOW_WIDTH))
                    if self.enemy.has_shield:
                        PowerupItem((self.all_sprites, self.break_shield_sprites, self.powerup_sprites), self.enemy, join("Images", "breakshield.png"))

                if event.type == self.enemy_bullet_event and (self.enemy_sprites or self.is_boss_active):
                    EnemyBullet((self.all_sprites, self.enemy_bullet_sprites), choice(list(self.enemy_sprites)), boss=False) if not self.is_boss_active \
                    else EnemyBullet((self.all_sprites, self.enemy_bullet_sprites), self.boss, boss=True)

                if event.type == self.heart_event and self.enemy_sprites and self.lives_remaining != 5:
                    PowerupItem((self.all_sprites, self.heart_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), join("Images", "heart.png"))

                if event.type == self.shield_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.shield_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), join("Images", "shield.png"))

                if event.type == self.speed_boost_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.speed_boost_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), join("Images", "speedboost.png"))
                
                if event.type == self.slow_time_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.slow_time_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), join("Images", "spiral.png"))

                if event.type == self.rapid_fire_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.rapid_fire_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), join("Images", "lightning.png"))

                if event.type == self.double_points_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.double_points_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), join("Images", "doublepoints.png"))
                
                if event.type == self.freeze_time_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.freeze_time_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), join("Images", "freeze.png"))

                if event.type == self.end_speed_boost:
                    self.player.speed = 550

                if event.type == self.end_invincibility:
                    self.player.invincible = False
                
                if event.type == self.reset_time:
                    self.slowed = False
                    self.frozen = False

                if event.type == self.end_rapid_fire:
                    self.rapid_fire = False

                if event.type == self.end_double_points:
                    self.double_points = False

                if event.type == self.warning_event:
                    self.alarm_sound.play()
                    self.is_second_one = choice([True, False])
                    self.danger_sign = DangerSign(self.all_sprites, (randint(40, WINDOW_WIDTH-40), randint(40, WINDOW_HEIGHT-40)))
                    self.danger_sign2 = DangerSign(self.all_sprites, (randint(40, WINDOW_WIDTH-40), randint(40, WINDOW_HEIGHT-40))) if self.is_second_one else None
                    pygame.time.set_timer(self.laser_event, 1000)

                if event.type == self.laser_event:
                    if self.danger_sign:
                        self.danger_sign.kill()
                    if self.danger_sign2:
                        self.danger_sign2.kill()
                    self.laser_sound.play()
                    Laser((self.all_sprites, self.laser_sprites), self.danger_sign)
                    Laser((self.all_sprites, self.laser_sprites), self.danger_sign2) if self.danger_sign2 else None
                    pygame.time.set_timer(self.delete_laser_event, 2000)
                    pygame.time.set_timer(self.laser_event, 0)

                if event.type == self.delete_laser_event:
                    for laser in self.laser_sprites:
                        laser.kill()
                    pygame.time.set_timer(self.delete_laser_event, 0)
                    pygame.time.set_timer(self.warning_event, randint(10000,15000))

                if event.type == self.spawn_teleport_enemy and len(self.teleport_enemies) < 1:
                    self.telep_enemy = TeleportEnemy((self.all_sprites, self.teleport_enemies), self.whoosh_sound)

                if event.type == self.randomize_boss and self.boss.alive():
                    self.boss.randomize_direction()

            self.display_surface.fill("#000000")

            recent_keys = pygame.key.get_just_pressed()
            if recent_keys[pygame.K_m]:
                self.muted = not self.muted

            if self.muted:
                self.music.set_volume(0)
                self.shoot_sound.set_volume(0)
                self.impact_sound.set_volume(0)
                self.explosion_sound.set_volume(0)
                self.beep_sound.set_volume(0)
                self.powerup_sound.set_volume(0)
                self.whoosh_sound.set_volume(0)
                self.alarm_sound.set_volume(0)
                self.laser_sound.set_volume(0)
            else:
                self.music.set_volume(0.8)
                self.shoot_sound.set_volume(0.5)
                self.impact_sound.set_volume(1)
                self.explosion_sound.set_volume(1)
                self.beep_sound.set_volume(0.85)
                self.powerup_sound.set_volume(1)
                self.whoosh_sound.set_volume(1)
                self.alarm_sound.set_volume(1)
                self.laser_sound.set_volume(1)

            if self.slowed:
                for enemy in self.enemy_sprites:
                    enemy.speed = 250
                for bullet in self.enemy_bullet_sprites:
                    bullet.speed = 225
                for powerup in self.powerup_sprites:
                    powerup.speed = 125
            elif self.frozen:
                for enemy in self.enemy_sprites:
                    enemy.speed = 0
                for bullet in self.enemy_bullet_sprites:
                    bullet.kill()
            else:
                for enemy in self.enemy_sprites:
                    if enemy.has_three_lives:
                        enemy.speed = THREE_LIFE_ENEMY_SPEED
                    else:
                        enemy.speed = ENEMY_SPEED
                for bullet in self.enemy_bullet_sprites:
                    bullet.speed = BULLET_SPEED
                for powerup in self.powerup_sprites:
                    powerup.speed = POWERUP_MOVING_SPEED

            self.player.cooldown_duration = 150 if self.rapid_fire else 500

            if self.lives_remaining == 1 and not self.flash_timer_in_arr:
                self.at_one_life = True
                self.flash_timer_in_arr = True
                self.timers.append(Timer(500, lambda: self.flash_life(), True, True))
                self.beep_sound.play()
            
            if self.lives_remaining > 1:
                self.at_one_life = False
            
            for bullet in self.bullet_sprites:
                if bullet.rect.bottom <= 0:
                    bullet.kill()
                    self.shots_missed += 1

            if not self.is_game_over:
                self.screen_shake(dt)
                offset_x, offset_y = self.shake_offset
                for sprite in self.all_sprites:
                    adjusted_rect = sprite.rect.move(offset_x, offset_y)
                    self.display_surface.blit(sprite.image, adjusted_rect)

                if not self.paused:
                    self.all_sprites.update(dt)
                    for timer in self.timers:
                        timer.update()
                self.display_fps()
                self.input()
                self.check_collisions()
                self.gun_timer()
                self.display_lives()
                self.display_volume()
                self.game_over()
                self.boss_fight()
            else:
                self.display_game_over()
                self.display_accuracy()
                self.display_time_survived()
            self.display_highscore()
            self.display_score()
            if not self.paused:
                pygame.display.update()
        pygame.quit()

if __name__ == "__main__":
    Game().run()
