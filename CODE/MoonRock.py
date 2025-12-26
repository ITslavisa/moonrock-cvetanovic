import pygame
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # .../moonrock
ASSETS_DIR = BASE_DIR / 'Assets'                   # .../moonrock/Assets

pygame.init()
pygame.font.init()
font=pygame.font.Font(None, 48)
score = 0
time_left= 350

pygame.display.set_caption("MoonRock")


''' Variables '''

player_x = 400
player_y = 550
vel = 15
last_shot = 0
shot_cooldown = 400

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

''' Sound '''
laser_sound = pygame.mixer.Sound(str(ASSETS_DIR/'laser_shot.wav'))
laser_sound.set_volume(0.4)
game_over_sound = pygame.mixer.Sound(str(ASSETS_DIR / 'game_over.wav'))
game_over_sound.set_volume(0.6)

game_over_played = False

running = True

class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, start_pos, speed_y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center = start_pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed_y = speed_y

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.y < 0:
            self.kill()

timer_event = pygame.USEREVENT +1 # 1s timer
pygame.time.set_timer(timer_event, 50)

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = alien_img
        self.rect = self.image.get_rect(center = (x, y))
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
            time_left -= 1 # faster or slower Countdown
        if time_left <= 0 and not game_over_played:
                game_over_sound.play()
                game_over_played = True

    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()
    
    if keys[pygame.K_LEFT] and player_x >= 0:
        player_x -= vel
    if keys[pygame.K_RIGHT] and player_x <= 750:
        player_x += vel
    if keys[pygame.K_UP] and player_y >= 0:
        player_y -= vel
    if keys[pygame.K_DOWN] and player_y <= 540:
        player_y += vel

    if keys[pygame.K_SPACE] and time_left > 0 and current_time - last_shot > shot_cooldown:
        bullet = Bullet(bullet_img, (player_x + 25, player_y + 30), -20)
        bullet_group.add(bullet)
        score += 10
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
    enemies.draw(screen)
    enemies.update()
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
    '''Bullet'''
    bullet_group.update()
    bullet_group.draw(screen)
    '''Display'''
    pygame.display.update()
    pygame.display.flip()
    clock.tick(60)


pygame.quit()
sys.exit()