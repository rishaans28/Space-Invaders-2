from settings import *
from sprites import *
from random import choice
from os.path import join
import json

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.running = True
        self.is_game_over = False
        
        self.enemies_killed = 0
        
        self.slowed = False
        self.rapid_fire = False
        
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset = (0,0)
        
        self.last_boss_fight_score = 0
        self.is_boss_active = False

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

        self.player = Player(self.all_sprites)
        self.lives_remaining = 3

        for _ in range(5):
            Enemy((self.all_sprites, self.enemy_sprites), randint(0, WINDOW_WIDTH))

        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, randint(1000,2000))

        self.enemy_bullet_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_bullet_event, randint(300,550))
        
        self.heart_event = pygame.event.custom_type()
        pygame.time.set_timer(self.heart_event, randint(7000,11000))
        
        self.slow_time_event = pygame.event.custom_type()
        pygame.time.set_timer(self.slow_time_event, randint(11000, 15000))
        self.reset_time = pygame.event.custom_type()
        
        self.shield_event = pygame.event.custom_type()
        pygame.time.set_timer(self.shield_event, randint(11000,15000))
        self.end_invincibility = pygame.event.custom_type()
        
        self.rapid_fire_event = pygame.event.custom_type()
        pygame.time.set_timer(self.rapid_fire_event, randint(11000, 15000))
        self.end_rapid_fire = pygame.event.custom_type()
        
        self.warning_event = pygame.event.custom_type()
        pygame.time.set_timer(self.warning_event, randint(10000,15000))
        
        self.speed_boost_event = pygame.event.custom_type()
        pygame.time.set_timer(self.speed_boost_event, randint(10000,15000))
        self.end_speed_boost = pygame.event.custom_type()

        self.laser_event = pygame.event.custom_type()
        self.delete_laser_event = pygame.event.custom_type()
        
        self.randomize_boss = pygame.event.custom_type()

        self.music = pygame.mixer.Sound("Space Invaders 2/Audio/music.mp3")
        self.music.set_volume(0.5)
        self.music.play(loops=-1)
        self.shoot_sound = pygame.mixer.Sound("Space Invaders 2/Audio/laser.wav")
        self.impact_sound = pygame.mixer.Sound("Space Invaders 2/Audio/impact.ogg")

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

    def screen_shake(self):
        if self.shake_duration > 0:
            self.shake_intensity = max(self.shake_intensity-1, 0)

            offset_x = randint(-self.shake_intensity, self.shake_intensity)
            offset_y = randint(-self.shake_intensity, self.shake_intensity)

            self.shake_offset = (offset_x, offset_y)

            self.shake_duration -= self.clock.get_time()
        else:
            self.shake_offset = (0, 0)

    def activate_shield(self):
        self.player.invincible = True
        pygame.time.set_timer(self.end_invincibility, 5000)

    def kill_player(self):
        if not self.player.invincible:
            self.lives_remaining = 0

    def gain_life(self):
        self.lives_remaining += 1

    def minus_life(self):
        if not self.player.invincible:
            self.lives_remaining -= 1
            self.shake_duration = 300
            self.shake_intensity = 50

    def activate_speed_boost(self):
        self.player.speed = 900
        pygame.time.set_timer(self.end_speed_boost, 5000)

    def activate_rapidfire(self):
        self.rapid_fire = True
        pygame.time.set_timer(self.end_rapid_fire, 5000)

    def slow_time(self):
        self.slowed = True
        pygame.time.set_timer(self.reset_time, 5000)

    def check_collisions(self):
        self.collision_logic(self.player, self.shield_sprites, lambda: self.activate_shield())
        self.collision_logic(self.player, self.heart_sprites, lambda: self.gain_life())
        self.collision_logic(self.player, self.speed_boost_sprites, lambda: self.activate_speed_boost())
        self.collision_logic(self.player, self.rapid_fire_sprites, lambda: self.activate_rapidfire())
        self.collision_logic(self.player, self.slow_time_sprites, lambda: self.slow_time())
        self.collision_logic(self.player, self.laser_sprites, lambda: self.kill_player())
        self.collision_logic(self.player, self.enemy_bullet_sprites, lambda: self.minus_life())

        for bullet in self.bullet_sprites:
            enemies_hit = pygame.sprite.spritecollide(bullet, self.enemy_sprites, True, pygame.sprite.collide_mask)
            if enemies_hit:
                bullet.kill()
            self.enemies_killed += len(enemies_hit)

        for enemy in self.enemy_sprites:
            if enemy.rect.top > 570:
                enemy.kill()
                if not self.player.invincible:
                    self.lives_remaining -= 1
        
        if hasattr(self, "boss") and self.boss.alive():
            for bullet in self.bullet_sprites:
                if pygame.sprite.collide_mask(bullet, self.boss):
                    bullet.kill()
                    self.boss.lives -= 1
                    if self.boss.lives <= 0:
                        self.shake_duration = 2000
                        self.shake_intensity = 100
                        self.boss.kill()
            pygame.time.set_timer(self.enemy_event, randint(1000,2000))

    def game_over(self):
        if self.lives_remaining <= 0 and not self.is_game_over:
            with open(join("Space Invaders 2", "Data", "score.txt"), "w") as score_file:
                json.dump(self.highscore, score_file)
            self.is_game_over = True

    def display_game_over(self):
        if self.is_game_over:
            font = pygame.font.Font("Fonts/Oxanium-Bold.ttf", 100)
            small_font = pygame.font.Font("Fonts/Oxanium-Bold.ttf", 30)
            
            text_surf = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            
            restart_text_surf = small_font.render("R to restart, Q to quit", True, (0,0,255))
            restart_text_rect = restart_text_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 185))
            
            self.display_surface.blit(text_surf, text_rect)
            self.display_surface.blit(restart_text_surf, restart_text_rect)
            
            self.all_sprites.empty()
            self.enemy_sprites.empty()
            self.bullet_sprites.empty()
            self.enemy_bullet_sprites.empty()
            self.heart_sprites.empty()
            self.laser_sprites.empty()
            self.shield_sprites.empty()
            self.speed_boost_sprites.empty()
            self.slow_time_sprites.empty()
            self.rapid_fire_sprites.empty()
            self.powerup_sprites.empty()
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.__init__()
            elif keys[pygame.K_q]:
                self.running = False

    def display_highscore(self):
        try:
            with open(join("Space Invaders 2", "Data", "score.txt")) as score_file:
                self.highscore = json.load(score_file)
        except:
            self.highscore = 0
            
        if self.enemies_killed > int(self.highscore):
            self.highscore = self.enemies_killed

        if not self.is_game_over:
            font = pygame.font.Font("Fonts/Oxanium-Bold.ttf", 30)
            score_text = font.render(f"HIGHSCORE: {self.highscore}", True, (255,255,255))
            score_rect = score_text.get_frect(topleft = (0,30))
        else:
            font = pygame.font.Font("Fonts/Oxanium-Bold.ttf", 50)
            score_text = font.render(f"HIGHSCORE: {self.highscore}", True, (255,255,255))
            score_rect = score_text.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 130))
        self.display_surface.blit(score_text, score_rect)

    def boss_fight(self):
        if self.enemies_killed % 15 == 0 and self.enemies_killed != 0 and self.enemies_killed != self.last_boss_fight_score:
            self.last_boss_fight_score = self.enemies_killed
            self.is_boss_active = True
            pygame.time.set_timer(self.enemy_event, 0)
            for sprite in self.enemy_sprites:
                sprite.kill()
            self.boss = Boss(self.all_sprites)
            pygame.time.set_timer(self.randomize_boss, randint(2000,5000))

    def gun_timer(self):
        if not self.player.can_shoot:
            self.current_time = pygame.time.get_ticks()
            if self.current_time - self.player.shoot_time >= self.player.cooldown_duration:
                self.player.can_shoot = True

    def display_fps(self):
        font = pygame.font.Font("Fonts/Oxanium-Bold.ttf", 30)
        text_surf = font.render("FPS: " + str(round(self.clock.get_fps(), 2)), True, (255, 255, 255))
        text_rect = text_surf.get_frect(topright = (WINDOW_WIDTH, 0))
        self.display_surface.blit(text_surf, text_rect)

    def display_lives(self):
        lives_img = pygame.image.load("Space Invaders 2/Images/life.png")
        lives_img_width = lives_img.get_width()
        total_width = self.lives_remaining * lives_img_width

        start_x = (WINDOW_WIDTH - total_width) / 2
        x = start_x
        for _ in range(self.lives_remaining):
            self.display_surface.blit(lives_img, (x,10))
            x += lives_img_width + 10

    def display_score(self):
        if not self.is_game_over:
            font = pygame.font.Font("Fonts/Oxanium-Bold.ttf", 30)
            score_text = font.render(f"SCORE: {self.enemies_killed}", True, (255,255,255))
            score_rect = score_text.get_frect(topleft = (0,0))
        else:
            font = pygame.font.Font("Fonts/Oxanium-Bold.ttf", 50)
            score_text = font.render(f"SCORE: {self.enemies_killed}", True, (255,255,255))
            score_rect = score_text.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 75))
        self.display_surface.blit(score_text, score_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == self.enemy_event:
                    self.enemy = Enemy((self.all_sprites, self.enemy_sprites), randint(0, WINDOW_WIDTH))

                if event.type == self.enemy_bullet_event and self.enemy_sprites:
                    EnemyBullet((self.all_sprites, self.enemy_bullet_sprites), choice(list(self.enemy_sprites)))

                if event.type == self.heart_event and self.enemy_sprites and self.lives_remaining != 5:
                    PowerupItem((self.all_sprites, self.heart_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), "Space Invaders 2/Images/heart.png")
                
                if event.type == self.shield_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.shield_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), "Space Invaders 2/Images/shield.png")

                if event.type == self.speed_boost_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.speed_boost_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), "Space Invaders 2/Images/speedboost.png")
                
                if event.type == self.slow_time_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.slow_time_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), "Space Invaders 2/Images/spiral.png")

                if event.type == self.rapid_fire_event and self.enemy_sprites:
                    PowerupItem((self.all_sprites, self.rapid_fire_sprites, self.powerup_sprites), choice(list(self.enemy_sprites)), "Space Invaders 2/Images/lightning.png")

                if event.type == self.end_speed_boost:
                    self.player.speed = 550

                if event.type == self.end_invincibility:
                    self.player.invincible = False
                
                if event.type == self.reset_time:
                    self.slowed = False
                
                if event.type == self.end_rapid_fire:
                    self.rapid_fire = False

                if event.type == self.warning_event:
                    self.danger_sign = DangerSign(self.all_sprites, (randint(40, WINDOW_WIDTH-40), randint(40, WINDOW_HEIGHT-40)))
                    pygame.time.set_timer(self.laser_event, 1000)

                if event.type == self.laser_event:
                    if self.danger_sign:
                        self.danger_sign.kill()
                    Laser((self.all_sprites, self.laser_sprites), self.danger_sign)
                    pygame.time.set_timer(self.delete_laser_event, 2000)
                    pygame.time.set_timer(self.laser_event, 0)

                if event.type == self.delete_laser_event:
                    for laser in self.laser_sprites:
                        laser.kill()
                    pygame.time.set_timer(self.delete_laser_event, 0)
                    pygame.time.set_timer(self.warning_event, randint(10000,15000))
                
                if event.type == self.randomize_boss and self.boss.alive():
                    self.boss.randomize_direction()

            self.display_surface.fill("#000000")
            
            if self.slowed:
                for enemy in self.enemy_sprites:
                    enemy.speed = 250
                for bullet in self.enemy_bullet_sprites:
                    bullet.speed = 225
                for powerup in self.powerup_sprites:
                    powerup.speed = 125
            else:
                for enemy in self.enemy_sprites:
                    enemy.speed = 500
                for bullet in self.enemy_bullet_sprites:
                    bullet.speed = 550
                for powerup in self.powerup_sprites:
                    powerup.speed = 350
            
            self.player.cooldown_duration = 150 if self.rapid_fire else 500

            if not self.is_game_over:
                self.screen_shake()
                offset_x, offset_y = self.shake_offset
                for sprite in self.all_sprites:
                    adjusted_rect = sprite.rect.move(offset_x, offset_y)
                    self.display_surface.blit(sprite.image, adjusted_rect)

                self.all_sprites.update(dt)
                self.all_sprites.draw(self.display_surface)
                self.display_fps()
                self.input()
                self.check_collisions()
                self.gun_timer()
                self.display_lives()
                self.game_over()
                self.boss_fight()
            else:
                self.display_game_over()
            self.display_highscore()
            self.display_score()

            pygame.display.update()
        pygame.quit()

if __name__ == "__main__":
    Game().run()
