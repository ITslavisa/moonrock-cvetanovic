"""
MoonRock (2D Arcade Prototype)

What this file contains:
- A simple 2D arcade-style prototype built with Pygame.
- Player ship movement with arrow keys.
- Shooting bullets with SPACE (with cooldown).
- Countdown timer + score HUD.
- Parallax scrolling background.
- One enemy sprite (placeholder).
- GAME OVER state when time runs out, with restart on key R.

Controls:
- Arrow keys: move the ship
- SPACE: shoot (only while time_left > 0)
- R: restart after GAME OVER
- Close window: quit
"""
import pygame
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # .../moonrock
ASSETS_DIR = BASE_DIR / 'Assets'                   # .../moonrock/Assets

pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 48)
score = 0
time_left= 350

pygame.display.set_caption("MoonRock")


''' Variables '''

player_x = 400
player_y = 550
vel = 15
last_shot = 0  # timestamp (ms) of the last fired shot
shot_cooldown = 400  # minimum time (ms) between two shots

bullet_group = pygame.sprite.Group()

#setup for Pygame
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

''' Sprites '''
background_image = pygame.image.load(str(ASSETS_DIR/'background_Blue_Nebula_08.png')).convert()
background_y_position = 0
background_image_height = background_image.get_height()

player_img = pygame.image.load(str(ASSETS_DIR/'Player.png')).convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 50))

bullet_img = pygame.image.load(str(ASSETS_DIR/'Laser Bullet.png')).convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (8, 16))
bullet_img = pygame.transform.rotate(bullet_img, 180)

alien_img = pygame.image.load(str(ASSETS_DIR/'alien.png')).convert_alpha()
alien_img = pygame.transform.scale(alien_img, (50, 50))

explosion_img = pygame.image.load(str(ASSETS_DIR/'explosion.png')).convert_alpha()
explosion_img = pygame.transform.scale(explosion_img, (60, 60))

explosions = pygame.sprite.Group()
''' Sound '''
laser_sound = pygame.mixer.Sound(str(ASSETS_DIR/'laser_shot.wav'))
laser_sound.set_volume(0.4)
game_over_sound = pygame.mixer.Sound(str(ASSETS_DIR / 'game_over.wav'))
game_over_sound.set_volume(0.6)

game_over_played = False
game_over = False

running = True

class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, start_pos, speed_y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=start_pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed_y = speed_y

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.y < 0:
            self.kill()
class Explosion(pygame.sprite.Sprite):
    '''Simple explosion effect: shows one image for a short time, than disappears.'''
    def __init__(self, pos):
        super().__init__()
        self.image = explosion_img
        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = pygame.time.get_ticks()
        self.duration_ms = 300   # explosion visible time

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.duration_ms:
            self.kill()


timer_event = pygame.USEREVENT +1 # 50ms timer
pygame.time.set_timer(timer_event, 50)

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = alien_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.direction = 4

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= 800:
            self.direction = -3
            self.rect.y += 20
        elif self.rect.left <= 0:
            self.direction = 3
            self.rect.y += 20

'''Enemies Variables'''
enemy = Alien(100, 100)
enemies = pygame.sprite.Group(enemy)

while running:
    pygame.time.delay(100)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == timer_event and time_left > 0:
            time_left -= 1  # faster or slower Countdown

        # When time runs out, switch the game into "game_over" state.
        # This will be used to disable movement/shooting and allow restarting with R.
        if time_left <= 0 and not game_over_played:
                game_over_sound.play()
                game_over_played = True
                game_over = True  # play is over

        # Restart the game only after GAME OVER:
        # If the player presses R, reset main variables and clear bullets.
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                time_left = 350
                score = 0
                bullet_group.empty()   #remove all bullets from the screen
                player_x, player_y = 400, 550   # reset player position
                last_shot = 0   # reset shooting cooldown timer
                game_over_played = False   # allow game-over sound to play next time
                game_over = False   # Leave game_over state and continue playing

    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    # Disable player movement when the game is over
    if not game_over:
        if keys[pygame.K_LEFT] and player_x >= 0:
            player_x -= vel
        if keys[pygame.K_RIGHT] and player_x <= 750:
            player_x += vel
        if keys[pygame.K_UP] and player_y >= 0:
            player_y -= vel
        if keys[pygame.K_DOWN] and player_y <= 540:
            player_y += vel

    if (keys[pygame.K_SPACE] and not game_over and time_left > 0 \
            and current_time - last_shot > shot_cooldown):
        bullet = Bullet(bullet_img, (player_x + 25, player_y + 30), -20)
        bullet_group.add(bullet)
        laser_sound.play()
        last_shot = current_time

    '''Parallax background moving'''
    background_y_position = background_y_position + 1

    if background_y_position >= background_image_height:
        background_y_position = 0

    '''Background (parallax)'''
    screen.blit(background_image, (0, background_y_position))
    screen.blit(background_image, (0, background_y_position - background_image_height))
    '''Background'''
    #screen.blit(background_image, (0, 0))
    '''Enemies'''
    enemies.update()
    '''Bullet'''
    bullet_group.update()
    '''Explosion'''
    explosions.update()
    '''Hit detection: bullet hits enemy - remove both, add points'''
    hits = pygame.sprite.groupcollide(enemies, bullet_group, True, True)
    for enemy in hits:
        explosions.add(Explosion(enemy.rect.center))
        score += 100
    '''DRAW SECTION'''
    enemies.draw(screen)
    '''Explosion Draw'''
    explosions.draw(screen)
    '''Clock/Timer'''
    time_text = font.render(f"Time = {time_left}", True, (255, 255, 255))
    screen.blit(time_text, (10, 10))
    '''Score'''
    score_text = font.render(f"Score = {score}", True, (255, 255, 255))
    screen.blit(score_text, (600, 10))
    '''Game Over Text'''
    if time_left <= 0:
        game_over_text = font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(game_over_text, (300, 280))
    '''Player'''
    screen.blit(player_img, (player_x, player_y))
    '''Bullet draw'''
    bullet_group.draw(screen)
    '''Display'''
    pygame.display.update()
    pygame.display.flip()
    clock.tick(60)


pygame.quit()
sys.exit()